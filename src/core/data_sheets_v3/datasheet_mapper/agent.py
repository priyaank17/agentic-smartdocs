"""Datasheet Mapper Agent"""

import json
import re
import logging
from typing import Dict, Any
from langchain.agents import (
    create_openai_functions_agent,
    AgentExecutor,
)
from langchain.utilities.duckduckgo_search import DuckDuckGoSearchAPIWrapper
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import SystemMessage
from langchain_core.tools import tool
from .aliases import build_aliases
from .canonical_store import CanonicalStore
from .llm_router import LLM, llm_match
from .config import PROMPT_PATH

log = logging.getLogger(__name__)


class DatasheetMapperAgent:
    """Datasheet Mapper Agent"""

    # ───────────────────────────────────────────────────────────────
    #  Constructor
    # ───────────────────────────────────────────────────────────────
    def __init__(self, schema: Dict[str, Any]) -> None:
        """basic setup"""
        self.schema = schema
        self.ent_alias, self.prop_alias = build_aliases(schema)
        self.store = CanonicalStore(schema)

        # build system prompt
        system_msg = SystemMessage(content=self._build_prompt())
        chat_prompt = ChatPromptTemplate.from_messages(
            [
                system_msg,
                MessagesPlaceholder(variable_name="agent_scratchpad"),
                ("user", "{input}"),
            ]
        )

        # ── Tool 1: schema_lookup  (closure, no `self` param) ─────────
        @tool
        def schema_lookup(txt: str) -> str:  # pylint: disable=unused-variable
            """Look up entity or property in the schema."""
            key = re.sub(r"[^A-Z0-9]", "", txt.upper())
            if key in self.prop_alias:
                ent, prop = self.prop_alias[key]
                return json.dumps({"entity": ent, "property": prop})
            if key in self.ent_alias:
                return json.dumps({"entity": self.ent_alias[key]})
            return "NONE"

        # ── Tool 2: write_canonical ──────────────────────────────────
        @tool
        def write_canonical(
            entity: str,
            prop: str | None,  # ← renamed ‟property” → ‟prop”
            value: Any,
        ) -> str:
            """Write a value to the canonical store."""
            self.store.write(entity, prop, value)
            return "OK"

        # ── Tool 3: return_result ────────────────────────────────────
        @tool
        def return_result() -> str:  # pylint: disable=unused-variable
            """Return the current state of the canonical store."""
            return json.dumps(self.store.data, indent=2, ensure_ascii=False)

        # make a LangChain Tool instance
        ddg = DuckDuckGoSearchAPIWrapper()

        @tool
        def web_search(query: str, max_results: int = 3) -> str:
            """DuckDuckGo quick text search."""
            results = ddg.results(query, max_results=max_results)
            return json.dumps({"query": query, "results": results})

        self.web_search = web_search

        tools = [schema_lookup, write_canonical, return_result, web_search]

        # create the function-calling agent
        agent_chain = create_openai_functions_agent(
            llm=LLM,
            tools=tools,
            prompt=chat_prompt,
        )

        # wrap in executor (this is where `verbose` belongs)
        self.agent = AgentExecutor(
            agent=agent_chain,
            tools=tools,
            verbose=False,  # set to True for console traces
        )

    # ------------------------------------------------------------------
    #  Safe property list for any entity (object or array)
    # ------------------------------------------------------------------
    def _entity_props(self, entity: str) -> list[str]:
        """Return the list of canonical property names for an entity."""
        try:
            ent_spec = self.schema["properties"][entity]
        except KeyError:
            return []

        if ent_spec["type"] == "object":
            return list(ent_spec.get("properties", {}).keys())

        if ent_spec["type"] == "array":
            return list(ent_spec["items"].get("properties", {}).keys())

        # unsupported schema type
        return []

    # ──────────────────────────────────────────────────────────────────
    #  LLM mapping constrained by an explicit allow-list
    # ──────────────────────────────────────────────────────────────────
    def _llm_pick(
        self,
        prompt: str,
        allow: list[str],
        kind: str,
    ) -> str | None:
        """
        Ask LLM to choose a value from `allow`.
        Returns the chosen string or None.
        """
        allow_text = ", ".join(f'"{x}"' for x in allow)
        question = (
            f"{prompt}\n\n"
            f"Choose ONE from this list only: [{allow_text}]. "
            'If nothing fits, reply with "NONE". '
            'Respond ONLY with JSON: {"choice": "<value>|NONE"}.'
        )
        resp = llm_match(question) or {}
        choice = resp.get("choice")

        if choice in allow:
            logging.info("LLM %s accepted → %s", kind, choice)
            return choice

        logging.warning("LLM %s '%s' rejected, using fallback", kind, choice)
        return None

    # ── prompt construction ─────────────────────────────────────────── #
    def _build_prompt(self) -> str:
        canon = [
            f"{e}.{p}"
            for e, spec in self.schema["properties"].items()
            for p in spec.get("properties", {})
        ]
        base = PROMPT_PATH.read_text()  # ← now contains the block above
        return base.replace("{{CANON_LIST}}", "\n".join(canon))

    # ── public API ──────────────────────────────────────────────────── #
    def run(self, tables: list[dict]):
        """Run the agent on a list of tables."""
        for tbl in tables:
            self._one_table(tbl)
        self.agent.invoke({"input": "ALL_TABLES_DONE"})

    # ──────────────────────────────────────────────────────────────────
    #  Process one extracted table
    # ──────────────────────────────────────────────────────────────────
    # pylint: disable=too-many-statements, too-many-branches, too complex
    def _one_table(self, tbl: Dict[str, Any]) -> None:
        """Process a single extracted table and write into the canonical store."""
        table_name: str = tbl["table_name"]
        cols: list[str] = tbl["column_names"]
        rows: list[dict] = tbl["data"]

        # ------------------------------------------------------------------ #
        # 1.  Decide which schema entity this table belongs to
        # ------------------------------------------------------------------ #
        norm_name = re.sub(r"[^A-Z0-9]", "", table_name.upper())
        allow = list(self.schema["properties"])

        chosen_ent = next(
            (e for e in allow if norm_name == re.sub(r"[^A-Z0-9]", "", e.upper())), None
        )
        if chosen_ent is None:  # ask LLM only when exact match fails
            prompt = (
                f"Table name: {table_name}\n"
                f"First rows: {json.dumps(rows[:3], indent=2, ensure_ascii=False)}\n\n"
                f'Choose ONE entity from {allow} and respond {{"entity":"<name>"}}'
            )
            llm_resp = llm_match(prompt) or {}
            ent = llm_resp.get("entity", "")
            chosen_ent = ent if ent in allow else "others"

        log.info("TABLE %-30s → entity '%s'", table_name[:30], chosen_ent)

        # helper: list of valid properties for the chosen entity
        def valid_props() -> set[str]:
            spec = self.schema["properties"][chosen_ent]
            if spec["type"] == "object":
                return set(spec.get("properties", {}))
            if spec["type"] == "array":
                return set(spec["items"].get("properties", {}))
            return set()

        # helper: pretty property log
        def log_prop(raw: str, prop_name: str, matched: bool) -> None:
            mark = "✔" if matched else "✖"
            target = (
                f"{chosen_ent}.{prop_name}"
                if matched
                else f"{chosen_ent}.additional_properties[{prop_name}]"
            )
            log.info("    %-26s → %-45s %s", raw[:26], target, mark)

        # ------------------------------------------------------------------ #
        # 2.  KEY / VALUE style table  (has “Standard Property” column)
        # ------------------------------------------------------------------ #
        if {"Standard Property", "Property"} & set(cols):
            pcol = "Standard Property" if "Standard Property" in cols else "Property"
            vcol = "Value" if "Value" in cols else cols[-1]

            for row in rows:
                raw_key = row.get(pcol, "")
                raw_val = row.get(vcol, "")
                if not raw_key:
                    continue

                prop = self._llm_pick(
                    prompt=f"Canonical property for '{raw_key}' in entity '{chosen_ent}'",
                    allow=list(valid_props()),
                    kind="property",
                )

                # retry once with web snippet if still unknown
                if not prop:
                    try:
                        snippet = self.web_search(
                            query=f"{raw_key} pump datasheet meaning", max_results=3
                        )
                        body_txt = " ".join(
                            r["body"] for r in json.loads(snippet)["results"]
                        )
                        prop = self._llm_pick(
                            prompt=(
                                f"Header '{raw_key}' context:\n{body_txt}\n"
                                f"Which property in '{chosen_ent}' fits?"
                            ),
                            allow=list(valid_props()),
                            kind="property",
                        )
                    except Exception:  # network / JSON issues
                        prop = None

                matched = bool(prop)
                prop = prop or self._snake(raw_key)

                self.store.write(chosen_ent, prop, raw_val)
                log_prop(raw_key, prop, matched)

        # ------------------------------------------------------------------ #
        # 3.  COLUMNAR table  (no “Standard Property” column)
        # ------------------------------------------------------------------ #
        else:
            header_map: dict[str, str] = {}

            for col in cols:
                prop = self._llm_pick(
                    prompt=f"Canonical property for header '{col}' in entity '{chosen_ent}'",
                    allow=list(valid_props()),
                    kind="property",
                )

                if not prop:
                    try:
                        snippet = self.web_search(
                            query=f"{col} pump datasheet header", max_results=3
                        )
                        body_txt = " ".join(
                            r["body"] for r in json.loads(snippet)["results"]
                        )
                        prop = self._llm_pick(
                            prompt=(
                                f"Header '{col}' context:\n{body_txt}\n"
                                f"Which property in '{chosen_ent}' fits?"
                            ),
                            allow=list(valid_props()),
                            kind="property",
                        )
                    except Exception:
                        prop = None

                matched = bool(prop)
                prop = prop or self._snake(col)
                header_map[col] = prop
                log_prop(col, prop, matched)

            # write each row dict
            for row in rows:
                mapped = {header_map[c]: v for c, v in row.items()}
                self.store.write(chosen_ent, None, mapped)

    @staticmethod
    def _snake(txt: str) -> str:
        """Convert a string to snake_case."""
        txt = re.sub(r"[^\w\s]", "", txt)
        return re.sub(r"\s+", "_", txt).lower()

"""Landing AI-powered vision extraction agent."""

import asyncio
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

from src.config.settings import get_settings
from src.utils.log import logger

BASE_URL = "https://api.va.landing.ai/v1/tools/agentic-document-analysis"
CONNECT_TIMEOUT = 600
READ_TIMEOUT = 600
POLL_INTERVAL = 15
MAX_RETRIES = 3
SCHEMA_DIR = Path(__file__).resolve().parents[4] / "data" / "schemas"
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)


class VisionExtractionAgent:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.api_key = self.settings.landing_ai_api_key
        self.headers = (
            {"Authorization": f"Basic {self.api_key}"}
            if self.api_key
            else {}
        )
        self._schema_cache: Dict[str, Dict[str, Any]] = {}
        self._session = requests.Session()

    async def run(self, pdf_path: Path, asset_type: str) -> List[Dict[str, Any]]:
        if not self.api_key:
            raise RuntimeError(
                "VA_API_KEY is required for Landing AI extraction; set it in your .env"
            )

        logger.info("LandingAI: loading schema for asset_type=%s", asset_type)
        schema = self._load_schema(asset_type)
        loop = asyncio.get_running_loop()
        extracted = await loop.run_in_executor(None, self._extract_sync, pdf_path, schema)
        return [extracted]

    def _extract_sync(self, pdf_path: Path, schema: Dict[str, Any]) -> Dict[str, Any]:
        files = {"pdf": (pdf_path.name, pdf_path.open("rb"), "application/pdf")}
        payload = {"fields_schema": json.dumps(schema)}

        logger.info("LandingAI: submitting %s", pdf_path.name)
        try:
            resp = self._session.post(
                BASE_URL,
                headers=self.headers,
                files=files,
                data=payload,
                timeout=(CONNECT_TIMEOUT, None),
            )
        except requests.RequestException as exc:
            raise RuntimeError(f"Initial Landing AI request failed: {exc}") from exc

        status_url: Optional[str] = resp.headers.get("Location") if resp.status_code == 202 else None
        if resp.status_code in (200, 206):
            body = resp.json()
        else:
            raise RuntimeError(f"Landing AI error {resp.status_code}: {resp.text[:300]}")

        if resp.status_code == 206 and "data" in body and "status" not in body:
            body["status"] = "partial"

        if "status" not in body and body.get("data", {}).get("extracted_schema") is not None:
            body["status"] = "success"

        if "status" not in body:
            debug_file = OUTPUT_DIR / f"{pdf_path.stem}_error.json"
            debug_file.write_text(json.dumps(body, indent=2, ensure_ascii=False))
            err_msg = body.get("error", {}).get("message", "<no message>")
            raise RuntimeError(
                f"Landing AI unexpected response ({resp.status_code}) – {err_msg}; saved to {debug_file}"
            )

        retries = 0
        while status_url and body.get("status") == "processing":
            time.sleep(POLL_INTERVAL)
            try:
                body = self._session.get(
                    status_url,
                    headers=self.headers,
                    timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
                ).json()
            except requests.RequestException as exc:
                retries += 1
                if retries > MAX_RETRIES:
                    raise RuntimeError(f"Landing AI polling failed: {exc}") from exc
                time.sleep(POLL_INTERVAL * retries)
                continue
            logger.info("LandingAI: status=%s", body.get("status"))

        if body.get("status") not in ("success", "partial"):
            raise RuntimeError(f"Landing AI returned status {body.get('status')}")

        logs = body.get("logs") or body.get("data", {}).get("logs")
        if logs:
            logger.info("— Landing AI run-logs for %s —", pdf_path.name)
            for line in logs:
                logger.info("   %s", line)
            logger.info("— end logs —")

        extracted = body.get("data", {}).get("extracted_schema") or {}
        logger.info("LandingAI: extracted keys=%s", list(extracted.keys()))
        out_file = OUTPUT_DIR / f"{pdf_path.stem}_extracted.json"
        out_file.write_text(json.dumps(extracted, indent=2, ensure_ascii=False))
        logger.info("LandingAI: saved parsed output to %s", out_file)
        return extracted

    def _load_schema(self, asset_type: str) -> Dict[str, Any]:
        if asset_type in self._schema_cache:
            return self._schema_cache[asset_type]
        candidate = SCHEMA_DIR / f"{asset_type}_schema.json"
        if not candidate.exists():
            candidate = SCHEMA_DIR / f"{asset_type}_schema.json"
        schema = json.loads(candidate.read_text(encoding="utf-8"))
        self._schema_cache[asset_type] = schema
        return schema

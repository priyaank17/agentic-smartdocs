"""SmartDocs agentic package initializer with legacy module aliases."""

import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LEGACY_ROOT = ROOT / "core"


def _alias_legacy(name: str, target: str) -> None:
    try:
        module = importlib.import_module(target)
    except ModuleNotFoundError:
        return
    sys.modules[f"src.{name}"] = module


if LEGACY_ROOT.exists():
    for entry in LEGACY_ROOT.iterdir():
        if entry.name.startswith("__"):
            continue
        root_level_candidate = ROOT / entry.name
        if root_level_candidate.exists() and entry.name not in {"core"}:
            # Prefer real modules in src/ over legacy aliases.
            continue
        if entry.is_dir() and (entry / "__init__.py").exists():
            target = f"src.core.{entry.name}"
            _alias_legacy(entry.name, target)
            # ensure nested control_narrative_lambda.* works
            for sub in entry.rglob("*.py"):
                if sub.name == "__init__.py":
                    continue
                rel = sub.relative_to(entry).with_suffix("")
                dotted = ".".join(rel.parts)
                alias = f"{entry.name}.{dotted}"
                _alias_legacy(alias, f"{target}.{dotted}")
        elif entry.is_file() and entry.suffix == ".py":
            module_name = entry.stem
            if (ROOT / f"{module_name}.py").exists():
                continue
            _alias_legacy(module_name, f"src.core.{module_name}")

"""Shared utils package that also exposes legacy modules from src.core.utils."""

from pathlib import Path
from pkgutil import extend_path

__path__ = extend_path(__path__, __name__)
_CORE_UTILS = Path(__file__).resolve().parent.parent / "core" / "utils"
if _CORE_UTILS.exists():
    core_path = str(_CORE_UTILS)
    if core_path not in __path__:
        __path__.append(core_path)

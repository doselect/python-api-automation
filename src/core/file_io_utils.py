"""
Mirrors testutils.core.FileIOUtils (Java): reads key/value pairs from a config.properties-style
file (key=value lines, '#' comments, blank lines ignored).

By default this resolves to the sibling Java `serenity-rest-assured` repo's real config.properties
(the same file that framework reads BaseURL/ResdexServiceURL from), so both frameworks stay
pointed at one source of truth. This module only ever reads that file — it is never modified.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

# python-api-automation/src/core/file_io_utils.py -> parents[2] is python-api-automation's own
# root; its parent is the Documents folder both this repo and serenity-rest-assured live under.
_DEFAULT_CONFIG_PATH = (
    Path(__file__).resolve().parents[3] / "serenity-rest-assured" / "config.properties"
)

_cache: dict[str, str] = {}
_loaded_path: Optional[Path] = None


def _load(config_path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    with config_path.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, _, value = line.partition("=")
            values[key.strip()] = value.strip()
    return values


def get_property_value(key: str, config_path: Path = _DEFAULT_CONFIG_PATH) -> Optional[str]:
    """Mirrors FileIOUtils.getPropertyValue(key): returns the value for key, or None if absent."""
    global _loaded_path
    if _loaded_path != config_path:
        _cache.clear()
        _cache.update(_load(config_path))
        _loaded_path = config_path
    return _cache.get(key)

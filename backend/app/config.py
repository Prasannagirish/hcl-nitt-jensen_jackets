"""Load settings from config/researchiq.yaml."""

import json
import os
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = PROJECT_ROOT / "config" / "researchiq.yaml"


def load_config(path: Path = DEFAULT_CONFIG) -> dict:
    """Read the YAML settings file into a dictionary."""
    with open(path, encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def load_env(path: Path = PROJECT_ROOT / ".env") -> None:
    """Copy KEY=value lines from the .env file into the process environment.

    Values already set in the real environment win. Nothing here prints a value.
    """
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def load_calibration(path: Path = PROJECT_ROOT / "config" / "calibration.json") -> dict:
    """Values chosen by scripts/calibrate_gate.py. Empty when the script has not been run."""
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


PLACEHOLDERS = {
    "",
    "choose-a-password",
    "your-openai-key-here",
    "your-pinecone-key-here",
    "change-me",
}


def require_env(names: list[str]) -> dict[str, str]:
    """Values of required environment variables; refuses to go on if one is unset or a placeholder.

    The error names the missing variables and never prints a value.
    """
    values = {name: os.environ.get(name, "") for name in names}
    missing = [name for name, value in values.items() if value in PLACEHOLDERS]
    if missing:
        raise RuntimeError(f"Set these in .env before starting: {', '.join(missing)}")
    return values

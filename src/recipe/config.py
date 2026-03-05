from __future__ import annotations

import os
import tomllib
from pathlib import Path


_CONFIG_PATH = Path.home() / ".config" / "recipe" / "config.toml"


def load_dotenv() -> None:
    """Load .env file from the current directory if it exists.

    Only sets variables that are not already in the environment.
    """
    env_path = Path(".env")
    if not env_path.exists():
        return
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip("'\"")
            if key and key not in os.environ:
                os.environ[key] = value


def load_config() -> dict:
    """Load optional TOML config file and merge with env vars."""
    config: dict = {}
    if _CONFIG_PATH.exists():
        with open(_CONFIG_PATH, "rb") as f:
            config = tomllib.load(f)
    return config


def get_api_key(name: str) -> str:
    """Get an API key from env vars, falling back to config file."""
    value = os.environ.get(name)
    if value:
        return value
    config = load_config()
    value = config.get("keys", {}).get(name)
    if value:
        return value
    raise RuntimeError(f"Missing API key: set {name} env var or add to {_CONFIG_PATH}")

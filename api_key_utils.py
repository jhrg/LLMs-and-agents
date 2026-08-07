"""Helpers for loading API keys from local files."""

from __future__ import annotations

import os
from pathlib import Path


def load_api_key_from_file(file_path: str, env_var: str = "OPENAI_API_KEY") -> str:
    """Read an API key from ``file_path`` and store it in ``os.environ``.

    The file should contain only the key value, with an optional trailing
    newline. The loaded key is returned so callers can inspect or reuse it.
    """

    key_path = Path(file_path).expanduser()
    if not key_path.is_file():
        raise FileNotFoundError(f"API key file not found: {key_path}")

    api_key = key_path.read_text(encoding="utf-8").strip()
    if not api_key:
        raise ValueError(f"API key file is empty: {key_path}")

    os.environ[env_var] = api_key
    return api_key


def read_api_key_from_file(file_path: str) -> str:
    """Read an API key from ``file_path`` and store it in ``os.environ``.

    The file should contain only the key value, with an optional trailing
    newline. The loaded key is returned so callers can inspect or reuse it.
    """

    key_path = Path(file_path).expanduser()
    if not key_path.is_file():
        raise FileNotFoundError(f"API key file not found: {key_path}")

    api_key = key_path.read_text(encoding="utf-8").strip()
    if not api_key:
        raise ValueError(f"API key file is empty: {key_path}")

    return api_key

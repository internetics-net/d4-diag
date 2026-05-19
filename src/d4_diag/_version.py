"""Read package version from pyproject.toml (single source of truth)."""

from __future__ import annotations

import re
from pathlib import Path


def read_version_from_pyproject() -> str:
    """Return ``[tool.poetry].version`` from the project pyproject.toml."""
    pyproject = Path(__file__).resolve().parents[2] / "pyproject.toml"
    if pyproject.is_file():
        text = pyproject.read_text(encoding="utf-8")
        match = re.search(
            r'\[tool\.poetry\].*?^\s*version\s*=\s*"([^"]+)"',
            text,
            re.MULTILINE | re.DOTALL,
        )
        if match:
            return match.group(1)

    try:
        from importlib.metadata import version

        return version("d4-diag")
    except Exception:
        return "0.0.0"

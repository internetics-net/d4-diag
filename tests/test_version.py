"""Tests for dynamic version loading."""

import re
from pathlib import Path

from d4_diag import __version__
from d4_diag._version import read_version_from_pyproject


def test_version_matches_pyproject():
    pyproject = Path(__file__).resolve().parents[1] / "pyproject.toml"
    text = pyproject.read_text(encoding="utf-8")
    match = re.search(
        r'\[tool\.poetry\].*?^\s*version\s*=\s*"([^"]+)"',
        text,
        re.MULTILINE | re.DOTALL,
    )
    assert match is not None
    assert __version__ == match.group(1)
    assert read_version_from_pyproject() == match.group(1)

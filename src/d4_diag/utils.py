"""Common utility functions for d4-diag."""

import ast
import os
import re
from pathlib import Path
from typing import List, Union


def sanitize_id(name: str) -> str:
    """Sanitize a string for use as a Mermaid node/subgraph ID."""
    if not name:
        return "id_empty"
    s = re.sub(r"[^\w]", "_", name)
    if not s:
        return "id_special"
    if s[0].isdigit():
        s = "n" + s
    return "id_" + s


def qlabel(text: str) -> str:
    """Quote a label for safe Mermaid rendering."""
    if not isinstance(text, str):
        text = str(text)
    return '"' + text.replace('"', "'") + '"'


def get_base_name(base: Union[ast.Name, ast.Attribute, ast.expr]) -> str:
    """Extract base class name from AST node, compatible with Python 3.8+."""
    if isinstance(base, ast.Name):
        return base.id
    elif isinstance(base, ast.Attribute):
        if hasattr(ast, "unparse"):
            return ast.unparse(base)
        # Manual reconstruction for Python 3.8
        parts = []
        node = base
        max_depth = 50
        while isinstance(node, ast.Attribute) and max_depth > 0:
            parts.append(node.attr)
            node = node.value
            max_depth -= 1
        if isinstance(node, ast.Name):
            parts.append(node.id)
        return ".".join(reversed(parts)) if parts else "Unknown"
    return "Unknown"


EXCLUDED_DIRS = {
    ".venv",
    "venv",
    ".env",
    "env",
    "__pycache__",
    ".git",
    ".hg",
    ".svn",
    ".tox",
    ".nox",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "node_modules",
    "site-packages",
    "dist",
    "build",
    ".eggs",
    "*.egg-info",
}


def find_python_files(root_path: str) -> List[str]:
    """Recursively find all Python files in a directory.

    Automatically excludes virtual environments, caches, and other
    non-source directories.
    """
    root = Path(os.path.abspath(root_path))
    if root.is_file():
        return [str(root)] if root.suffix == ".py" else []
    if not root.is_dir():
        return []

    results = []
    for p in root.rglob("*.py"):
        # Check if any parent directory should be excluded
        parts = p.relative_to(root).parts
        if any(part in EXCLUDED_DIRS for part in parts):
            continue
        results.append(str(p))
    return results

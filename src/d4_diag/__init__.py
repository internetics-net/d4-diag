"""d4-diag: Python static analysis and Mermaid diagram generation."""

from ._version import read_version_from_pyproject
from .generate_mermaid import CodeMapAnalyzer
from .utils import find_python_files

__version__ = read_version_from_pyproject()

__all__ = ["CodeMapAnalyzer", "find_python_files", "__version__"]

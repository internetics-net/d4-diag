"""Test configuration and fixtures for d4-diag."""

import tempfile
from pathlib import Path
from typing import Generator

import pytest


@pytest.fixture
def temp_project_dir() -> Generator[Path, None, None]:
    """Create a temporary directory with sample Python files for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir)

        # Create sample Python files
        (project_path / "main.py").write_text(
            """
def main():
    \"\"\"Main entry point.\"\"\"
    return "Hello, World!"

class Application:
    def run(self):
        pass
"""
        )

        (project_path / "utils.py").write_text(
            """
import os
from typing import List

def helper():
    \"\"\"Helper function.\"\"\"
    return os.getcwd()

class Utils:
    def process(self, data: List[str]) -> List[str]:
        return data
"""
        )

        # Create models directory and files
        models_dir = project_path / "models"
        models_dir.mkdir(exist_ok=True)
        (models_dir / "__init__.py").write_text("")
        (models_dir / "user.py").write_text(
            """
from dataclasses import dataclass

@dataclass
class User:
    name: str
    email: str

    def get_display_name(self) -> str:
        return self.name
"""
        )

        # Create services directory and files
        services_dir = project_path / "services"
        services_dir.mkdir(exist_ok=True)
        (services_dir / "auth.py").write_text(
            """
from models.user import User

class AuthService:
    def authenticate(self, user: User) -> bool:
        return True
"""
        )

        # Create a virtual environment directory (should be excluded)
        (project_path / ".venv" / "lib" / "site-packages").mkdir(parents=True, exist_ok=True)
        (project_path / ".venv" / "lib" / "site-packages" / "external.py").write_text(
            "print('external')"
        )

        # Create a cache directory (should be excluded)
        (project_path / "__pycache__").mkdir(exist_ok=True)
        (project_path / "__pycache__" / "main.pyc").write_bytes(b"compiled")

        yield project_path


@pytest.fixture
def empty_project_dir() -> Generator[Path, None, None]:
    """Create an empty temporary directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def complex_project_dir() -> Generator[Path, None, None]:
    """Create a complex project structure with various Python constructs."""
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir)

        # Complex class hierarchy
        (project_path / "base.py").write_text(
            """
from abc import ABC, abstractmethod
from typing import Protocol

class BaseClass(ABC):
    @abstractmethod
    def abstract_method(self):
        pass

class ProtocolClass(Protocol):
    def protocol_method(self) -> str: ...
"""
        )

        (project_path / "derived.py").write_text(
            """
from base import BaseClass

class DerivedClass(BaseClass):
    def abstract_method(self):
        return "implemented"

    @classmethod
    def class_method(cls):
        return cls.__name__

    @staticmethod
    def static_method():
        return "static"
"""
        )

        # File with imports and complex structures
        (project_path / "imports.py").write_text(
            """
import os
import sys
from pathlib import Path
from typing import List, Dict, Optional
from .base import BaseClass
from .derived import DerivedClass

try:
    import external_module
except ImportError:
    external_module = None

def complex_function(param: Optional[str] = None) -> Dict[str, List[str]]:
    return {"items": []}
"""
        )

        # Nested modules
        deep_dir = project_path / "deep" / "nested"
        deep_dir.mkdir(parents=True, exist_ok=True)
        (deep_dir / "module.py").write_text(
            """
def deep_function():
    return "deep"
"""
        )

        yield project_path


@pytest.fixture
def sample_python_file() -> Generator[Path, None, None]:
    """Create a single Python file for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = Path(temp_dir) / "sample.py"
        file_path.write_text(
            """
import os
import sys
from typing import List

class SampleClass:
    def __init__(self):
        self.value = 42

    def method(self) -> int:
        return self.value

    @staticmethod
    def static_method():
        return "static"

def sample_function(param: List[str]) -> str:
    return ",".join(param)

async def async_function():
    return "async"
"""
        )
        yield file_path

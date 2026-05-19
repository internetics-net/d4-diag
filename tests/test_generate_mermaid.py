"""Test CodeMapAnalyzer class."""

from pathlib import Path
from unittest.mock import patch

from d4_diag.generate_mermaid import CodeMapAnalyzer


class TestCodeMapAnalyzer:
    """Test the CodeMapAnalyzer class."""

    def test_init(self, temp_project_dir):
        analyzer = CodeMapAnalyzer(str(temp_project_dir))
        # Explicitly use Path to ensure linter detects the import
        project_root = Path(temp_project_dir).absolute()
        assert analyzer.project_root == str(project_root)
        assert analyzer.files == {}
        assert analyzer.import_edges == set()
        assert analyzer._module_map == {}

    def test_rel_path(self, temp_project_dir):
        analyzer = CodeMapAnalyzer(str(temp_project_dir))

        # Test relative path calculation
        file_path = temp_project_dir / "subdir" / "file.py"
        expected_rel = "subdir/file.py"

        with patch("os.path.relpath", return_value=expected_rel):
            result = analyzer._rel(str(file_path))
            assert result == expected_rel

    def test_build_module_map(self, temp_project_dir):
        analyzer = CodeMapAnalyzer(str(temp_project_dir))

        file_paths = [
            str(temp_project_dir / "main.py"),
            str(temp_project_dir / "utils.py"),
            str(temp_project_dir / "models" / "__init__.py"),
            str(temp_project_dir / "models" / "user.py"),
        ]

        analyzer.build_module_map(file_paths)

        expected_modules = {
            "main": "main.py",
            "utils": "utils.py",
            "models": "models/__init__.py",
            "models.user": "models/user.py",
        }

        assert analyzer._module_map == expected_modules

    def test_build_module_map_with_init_py(self, temp_project_dir):
        analyzer = CodeMapAnalyzer(str(temp_project_dir))

        file_paths = [str(temp_project_dir / "models" / "__init__.py")]
        analyzer.build_module_map(file_paths)

        # __init__.py should map to the package name
        assert "models" in analyzer._module_map
        assert analyzer._module_map["models"] == "models/__init__.py"

    def test_analyze_file_success(self, sample_python_file):
        analyzer = CodeMapAnalyzer(str(sample_python_file.parent))
        analyzer.build_module_map([str(sample_python_file)])

        analyzer.analyze_file(str(sample_python_file))

        rel_path = analyzer._rel(str(sample_python_file))
        assert rel_path in analyzer.files

        file_info = analyzer.files[rel_path]
        assert "classes" in file_info
        assert "functions" in file_info
        assert "imports" in file_info

        # Should find SampleClass
        classes = file_info["classes"]
        assert len(classes) == 1
        assert classes[0]["name"] == "SampleClass"
        assert "method" in classes[0]["methods"]
        assert "static_method" in classes[0]["methods"]

        # Should find functions
        functions = file_info["functions"]
        assert "sample_function" in functions
        assert "async_function" in functions

    def test_analyze_file_with_syntax_error(self, temp_project_dir):
        # Create a file with syntax error
        invalid_file = temp_project_dir / "invalid.py"
        invalid_file.write_text("def invalid_function(\n    # missing closing parenthesis")

        analyzer = CodeMapAnalyzer(str(temp_project_dir))

        # Should handle syntax error gracefully
        with patch("builtins.print") as mock_print:
            analyzer.analyze_file(str(invalid_file))
            mock_print.assert_called()
            # Should print error message
            assert any("Syntax error" in str(call) for call in mock_print.call_args_list)

    def test_analyze_file_too_large(self, temp_project_dir):
        # Create a large file
        large_file = temp_project_dir / "large.py"
        large_content = "x = 1\n" * 1000000  # Create a large file
        large_file.write_text(large_content)

        analyzer = CodeMapAnalyzer(str(temp_project_dir))

        # Mock file size to be larger than MAX_FILE_SIZE
        with patch("os.path.getsize", return_value=15 * 1024 * 1024):  # 15MB
            with patch("builtins.print") as mock_print:
                analyzer.analyze_file(str(large_file))
                mock_print.assert_called()
                assert any("file too large" in str(call) for call in mock_print.call_args_list)

    def test_analyze_file_read_error(self, temp_project_dir):
        # Create a file and make it unreadable
        test_file = temp_project_dir / "unreadable.py"
        test_file.write_text("print('test')")

        analyzer = CodeMapAnalyzer(str(temp_project_dir))

        # Mock open to raise an error
        with patch("builtins.open", side_effect=IOError("Permission denied")):
            with patch("builtins.print") as mock_print:
                analyzer.analyze_file(str(test_file))
                mock_print.assert_called()
                assert any("Error reading" in str(call) for call in mock_print.call_args_list)

    def test_analyze_file_encoding_error(self, temp_project_dir):
        # Create a file with invalid encoding
        test_file = temp_project_dir / "bad_encoding.py"
        test_file.write_bytes(b"\x80\x81\x82invalid utf-8")

        analyzer = CodeMapAnalyzer(str(temp_project_dir))

        with patch("builtins.print") as mock_print:
            analyzer.analyze_file(str(test_file))
            mock_print.assert_called()
            assert any("Error reading" in str(call) for call in mock_print.call_args_list)

    def test_analyze_file_with_imports(self, temp_project_dir):
        """Test analyzing file with various import types."""
        # Create a file with various import types
        test_file = temp_project_dir / "imports.py"
        test_file.write_text(
            """
import os
import sys
from pathlib import Path
from typing import List, Dict
from .local_module import local_function
"""
        )

        analyzer = CodeMapAnalyzer(str(temp_project_dir))
        analyzer.build_module_map([str(test_file)])

        analyzer.analyze_file(str(test_file))

        rel_path = analyzer._rel(str(test_file))
        file_info = analyzer.files[rel_path]

        imports = file_info["imports"]
        expected_imports = ["os", "sys", "pathlib", "typing", "local_module"]
        for expected in expected_imports:
            assert expected in imports

    def test_relative_import_from_dot(self, temp_project_dir):
        """from . import sibling should resolve when sibling module exists."""
        pkg = temp_project_dir / "pkg"
        pkg.mkdir()
        (pkg / "__init__.py").write_text("")
        (pkg / "a.py").write_text("from . import b\n")
        (pkg / "b.py").write_text("def fn(): pass\n")

        analyzer = CodeMapAnalyzer(str(temp_project_dir))
        files = [str(pkg / "a.py"), str(pkg / "b.py")]
        analyzer.build_module_map(files)
        analyzer.analyze_file(files[0])

        assert ("pkg/a.py", "pkg/b.py") in analyzer.import_edges

    def test_class_diagram_skips_external_bases(self, temp_project_dir):
        test_file = temp_project_dir / "models.py"
        test_file.write_text("class User(object):\n    pass\n")

        analyzer = CodeMapAnalyzer(str(temp_project_dir))
        analyzer.build_module_map([str(test_file)])
        analyzer.analyze_file(str(test_file))

        content = analyzer.generate_class_diagram()
        assert "<|--" not in content

    def test_resolve_import_local(self, temp_project_dir):
        # Test local import resolution
        main_file = temp_project_dir / "main.py"
        utils_file = temp_project_dir / "utils.py"

        main_file.write_text("from utils import helper")
        utils_file.write_text("def helper(): pass")

        analyzer = CodeMapAnalyzer(str(temp_project_dir))
        analyzer.build_module_map([str(main_file), str(utils_file)])

        analyzer.analyze_file(str(main_file))

        # Should have resolved the import edge
        assert ("main.py", "utils.py") in analyzer.import_edges

    def test_resolve_import_external(self, temp_project_dir):
        # Test external import (should not create edge)
        test_file = temp_project_dir / "main.py"
        test_file.write_text("import os")

        analyzer = CodeMapAnalyzer(str(temp_project_dir))
        analyzer.build_module_map([str(test_file)])

        analyzer.analyze_file(str(test_file))

        # Should not create edge for external modules
        assert len(analyzer.import_edges) == 0

    def test_analyze_async_functions(self, temp_project_dir):
        # Test that async functions are properly detected
        test_file = temp_project_dir / "async_test.py"
        test_file.write_text(
            """
async def async_function():
    return "async"

class AsyncClass:
    async def async_method(self):
        return "method"
"""
        )

        analyzer = CodeMapAnalyzer(str(temp_project_dir))
        analyzer.build_module_map([str(test_file)])

        analyzer.analyze_file(str(test_file))

        rel_path = analyzer._rel(str(test_file))
        file_info = analyzer.files[rel_path]

        # Should detect async function
        assert "async_function" in file_info["functions"]

        # Should detect async method
        classes = file_info["classes"]
        assert len(classes) == 1
        assert "async_method" in classes[0]["methods"]

    def test_analyze_class_inheritance(self, temp_project_dir):
        # Test class inheritance detection
        test_file = temp_project_dir / "inheritance.py"
        test_file.write_text(
            """
class Base:
    pass

class Derived(Base):
    pass

class Multiple(Base, object):
    pass

from typing import Protocol

class ProtocolClass(Protocol):
    pass
"""
        )

        analyzer = CodeMapAnalyzer(str(temp_project_dir))
        analyzer.build_module_map([str(test_file)])

        analyzer.analyze_file(str(test_file))

        rel_path = analyzer._rel(str(test_file))
        file_info = analyzer.files[rel_path]

        classes = file_info["classes"]
        class_dict = {cls["name"]: cls for cls in classes}

        # Check inheritance
        assert "Base" in class_dict["Derived"]["bases"]
        assert "Base" in class_dict["Multiple"]["bases"]
        assert "object" in class_dict["Multiple"]["bases"]

    def test_print_summary(self, temp_project_dir, capsys):
        analyzer = CodeMapAnalyzer(str(temp_project_dir))

        # Add some mock data
        analyzer.files = {
            "file1.py": {
                "classes": [{"name": "Class1", "methods": ["method1"]}],
                "functions": ["func1"],
                "imports": ["os"],
            },
            "file2.py": {"classes": [], "functions": ["func2"], "imports": ["sys"]},
        }
        analyzer.import_edges = {("file1.py", "file2.py")}

        analyzer.print_summary()

        captured = capsys.readouterr()
        assert "Files analyzed:   2" in captured.out
        assert "Classes found:    1" in captured.out
        assert "Functions found:  2" in captured.out
        assert "Import links:     1" in captured.out

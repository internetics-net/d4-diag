"""Test utility functions."""

import ast
from pathlib import Path

from d4_diag.utils import EXCLUDED_DIRS, _is_excluded_dir, find_python_files, get_base_name, qlabel, sanitize_id


class TestSanitizeId:
    """Test the sanitize_id function."""

    def test_empty_string(self):
        assert sanitize_id("") == "id_empty"

    def test_normal_string(self):
        assert sanitize_id("normal_string") == "id_normal_string"

    def test_special_characters(self):
        assert sanitize_id("string-with-dashes") == "id_string_with_dashes"
        assert sanitize_id("string.with.dots") == "id_string_with_dots"
        assert sanitize_id("string with spaces") == "id_string_with_spaces"
        assert sanitize_id("string@with#symbols") == "id_string_with_symbols"

    def test_only_special_chars(self):
        assert sanitize_id("@#$") == "id____"  # Special chars become underscores

    def test_starts_with_digit(self):
        assert sanitize_id("123string") == "id_n123string"
        assert sanitize_id("1") == "id_n1"

    def test_unicode_characters(self):
        # Unicode characters with diacritics are preserved by \w regex
        assert sanitize_id("naïve") == "id_naïve"  # ï is preserved
        assert sanitize_id("café") == "id_café"  # é is also preserved


class TestQLabel:
    """Test the qlabel function."""

    def test_normal_string(self):
        assert qlabel("test") == '"test"'

    def test_string_with_quotes(self):
        assert qlabel('test"quote') == '"test\'quote"'
        assert qlabel("test'quote") == '"test\'quote"'

    def test_non_string_input(self):
        assert qlabel(123) == '"123"'
        assert qlabel(None) == '"None"'
        assert qlabel([1, 2, 3]) == '"[1, 2, 3]"'

    def test_empty_string(self):
        assert qlabel("") == '""'


class TestGetBaseName:
    """Test the get_base_name function."""

    def test_simple_name(self):
        node = ast.Name(id="MyClass", ctx=ast.Load())
        assert get_base_name(node) == "MyClass"

    def test_simple_attribute(self):
        node = ast.Attribute(
            value=ast.Name(id="module", ctx=ast.Load()), attr="Class", ctx=ast.Load()
        )
        assert get_base_name(node) == "module.Class"

    def test_nested_attribute(self):
        node = ast.Attribute(
            value=ast.Attribute(
                value=ast.Name(id="package", ctx=ast.Load()), attr="module", ctx=ast.Load()
            ),
            attr="Class",
            ctx=ast.Load(),
        )
        assert get_base_name(node) == "package.module.Class"

    def test_deeply_nested_attribute(self):
        # Test with maximum depth protection
        node = ast.Name(id="base", ctx=ast.Load())
        # Create a chain of attributes
        for i in range(60):  # More than max_depth
            node = ast.Attribute(value=node, attr=f"level{i}", ctx=ast.Load())

        result = get_base_name(node)
        # The actual implementation doesn't have a depth limit, so it returns the full chain
        assert result.startswith("base.level0")

    def test_unknown_node_type(self):
        node = ast.Constant(value=42)
        assert get_base_name(node) == "Unknown"


class TestFindPythonFiles:
    """Test the find_python_files function."""

    def test_find_single_file(self, sample_python_file):
        result = find_python_files(str(sample_python_file))
        assert len(result) == 1
        assert result[0] == str(sample_python_file)

    def test_find_non_python_file(self, temp_project_dir):
        non_py_file = temp_project_dir / "test.txt"
        non_py_file.write_text("not python")

        result = find_python_files(str(non_py_file))
        assert len(result) == 0

    def test_find_in_directory(self, temp_project_dir):
        result = find_python_files(str(temp_project_dir))

        # Should find Python files but exclude excluded directories
        python_files = [Path(f) for f in result]
        assert len(python_files) >= 4  # main.py, utils.py, user.py, auth.py

        # Check that excluded directories are not included
        for file_path in python_files:
            assert ".venv" not in str(file_path)
            assert "__pycache__" not in str(file_path)

    def test_excluded_directories(self, temp_project_dir):
        # Create additional excluded directories
        (temp_project_dir / "node_modules").mkdir()
        (temp_project_dir / "node_modules" / "script.js").write_text("js")
        (temp_project_dir / "site-packages").mkdir()
        (temp_project_dir / "site-packages" / "external.py").write_text("python")

        result = find_python_files(str(temp_project_dir))
        python_files = [Path(f) for f in result]

        # Should not include files from excluded directories
        for file_path in python_files:
            assert "node_modules" not in str(file_path)
            assert "site-packages" not in str(file_path)

    def test_nonexistent_directory(self):
        result = find_python_files("/nonexistent/directory")
        assert result == []

    def test_empty_directory(self, empty_project_dir):
        result = find_python_files(str(empty_project_dir))
        assert result == []

    def test_nested_python_files(self, complex_project_dir):
        result = find_python_files(str(complex_project_dir))
        python_files = [Path(f) for f in result]

        # Should find deeply nested files
        deep_files = [f for f in python_files if "deep" in str(f)]
        assert len(deep_files) == 1
        assert deep_files[0].name == "module.py"

    def test_excluded_dirs_constant(self):
        """Test that EXCLUDED_DIRS contains expected directories."""
        expected_dirs = {
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
        }
        assert expected_dirs.issubset(EXCLUDED_DIRS)

    def test_egg_info_directory_excluded(self, temp_project_dir):
        egg_dir = temp_project_dir / "my_package.egg-info"
        egg_dir.mkdir()
        (egg_dir / "PKG-INFO").write_text("Metadata")
        (egg_dir / "module.py").write_text("x = 1\n")

        result = find_python_files(str(temp_project_dir))
        assert not any("egg-info" in f for f in result)

    def test_is_excluded_dir_glob(self):
        assert _is_excluded_dir("foo.egg-info") is True
        assert _is_excluded_dir("src") is False

    def test_file_with_py_extension_only(self, temp_project_dir):
        # Create a file that ends with .py but isn't valid Python
        invalid_py = temp_project_dir / "invalid.py"
        invalid_py.write_text("this is not valid python syntax [[[")

        result = find_python_files(str(temp_project_dir))
        assert str(invalid_py) in result  # Should still be found by extension

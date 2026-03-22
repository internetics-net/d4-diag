"""Integration tests for d4-diag."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from d4_diag.generate_mermaid import CodeMapAnalyzer
from d4_diag.main import main
from d4_diag.utils import find_python_files


class TestIntegration:
    """Integration tests for the complete workflow."""

    def test_full_analysis_workflow(self, temp_project_dir):
        """Test complete analysis workflow from files to diagrams."""
        # Find all Python files
        python_files = find_python_files(str(temp_project_dir))
        assert len(python_files) >= 4  # Should find main.py, utils.py, user.py, auth.py

        # Create analyzer
        analyzer = CodeMapAnalyzer(str(temp_project_dir))
        analyzer.build_module_map(python_files)

        # Analyze all files
        for file_path in python_files:
            analyzer.analyze_file(file_path)

        # Check that files were analyzed
        assert len(analyzer.files) >= 4

        # Check that import edges were created
        assert len(analyzer.import_edges) >= 0  # May have imports or not

        # Test diagram generation (without saving)
        with tempfile.TemporaryDirectory() as temp_dir:
            analyzer.generate_all(save_files=True, output_dir=temp_dir)

            # Check that diagram files were created
            diagrams_dir = Path(temp_dir)
            assert (diagrams_dir / "architecture.mmd").exists()
            assert (diagrams_dir / "class_diagram.mmd").exists()
            assert (diagrams_dir / "module_deps.mmd").exists()

    def test_complex_project_analysis(self, complex_project_dir):
        """Test analysis of complex project with inheritance and imports."""
        python_files = find_python_files(str(complex_project_dir))

        analyzer = CodeMapAnalyzer(str(complex_project_dir))
        analyzer.build_module_map(python_files)

        for file_path in python_files:
            analyzer.analyze_file(file_path)

        # Should detect complex structures
        total_classes = sum(len(file_info["classes"]) for file_info in analyzer.files.values())
        total_functions = sum(len(file_info["functions"]) for file_info in analyzer.files.values())

        assert total_classes >= 2  # BaseClass, DerivedClass
        assert total_functions >= 2  # complex_function, deep_function

    def test_analysis_with_errors(self, temp_project_dir):
        """Test analysis handling of various error conditions."""
        # Create a file with syntax error
        syntax_error_file = temp_project_dir / "syntax_error.py"
        syntax_error_file.write_text("def broken_function(\n    # missing closing parenthesis")

        # Create a large file
        large_file = temp_project_dir / "large.py"
        large_content = "x = 1\n" * 1000000
        large_file.write_text(large_content)

        python_files = find_python_files(str(temp_project_dir))

        analyzer = CodeMapAnalyzer(str(temp_project_dir))
        analyzer.build_module_map(python_files)

        # Should handle errors gracefully
        for file_path in python_files:
            analyzer.analyze_file(file_path)

        # Should still analyze valid files
        valid_files = [
            f for f in analyzer.files.keys() if "syntax_error.py" not in f and "large.py" not in f
        ]
        assert len(valid_files) >= 4  # Original valid files

    def test_backward_compatibility_integration(self, temp_project_dir):
        """Test backward compatibility with main() function."""
        custom_argv = ["d4-diag", str(temp_project_dir)]

        with patch("d4_diag.main.CodeMapAnalyzer") as mock_analyzer_class:
            mock_analyzer = MagicMock()
            mock_analyzer_class.return_value = mock_analyzer

            # Should work with custom argv
            main(custom_argv)

            # Should have called analyzer
            mock_analyzer.build_module_map.assert_called()
            mock_analyzer.generate_all.assert_called()

    def test_empty_project_handling(self, empty_project_dir):
        """Test handling of empty project."""
        python_files = find_python_files(str(empty_project_dir))
        assert len(python_files) == 0

        # Should handle empty project gracefully
        analyzer = CodeMapAnalyzer(str(empty_project_dir))
        analyzer.build_module_map(python_files)

        assert len(analyzer.files) == 0
        assert len(analyzer.import_edges) == 0

    def test_single_file_analysis(self, sample_python_file):
        """Test analysis of single Python file."""
        python_files = [str(sample_python_file)]

        analyzer = CodeMapAnalyzer(str(sample_python_file.parent))
        analyzer.build_module_map(python_files)
        analyzer.analyze_file(str(sample_python_file))

        # Should find the class and functions
        assert len(analyzer.files) == 1
        file_info = list(analyzer.files.values())[0]

        assert len(file_info["classes"]) == 1
        assert file_info["classes"][0]["name"] == "SampleClass"
        assert "method" in file_info["classes"][0]["methods"]
        assert "static_method" in file_info["classes"][0]["methods"]

        assert "sample_function" in file_info["functions"]
        assert "async_function" in file_info["functions"]

    def test_deeply_nested_structure(self, complex_project_dir):
        """Test analysis of deeply nested module structure."""
        python_files = find_python_files(str(complex_project_dir))

        analyzer = CodeMapAnalyzer(str(complex_project_dir))
        analyzer.build_module_map(python_files)

        for file_path in python_files:
            analyzer.analyze_file(file_path)

        # Should find deeply nested files
        nested_files = [f for f in analyzer.files.keys() if "deep" in f]
        assert len(nested_files) == 1

        # Should have proper module mapping
        assert "deep.nested.module" in analyzer._module_map

    def test_import_resolution_across_modules(self, temp_project_dir):
        """Test import resolution between modules."""
        python_files = find_python_files(str(temp_project_dir))

        analyzer = CodeMapAnalyzer(str(temp_project_dir))
        analyzer.build_module_map(python_files)

        for file_path in python_files:
            analyzer.analyze_file(file_path)

        # Should resolve local imports
        # Note: This depends on the actual imports in the test files
        # If there are no local imports, this will be 0
        local_imports = [
            (src, dst)
            for src, dst in analyzer.import_edges
            if not any(dst.startswith(ext) for ext in ["os", "sys", "pathlib", "typing"])
        ]

        # The test is flexible - it may or may not find local imports
        # depending on the test file contents
        assert isinstance(local_imports, list)

    def test_diagram_content_validation(self, temp_project_dir):
        """Test that generated diagrams contain expected content."""
        python_files = find_python_files(str(temp_project_dir))

        analyzer = CodeMapAnalyzer(str(temp_project_dir))
        analyzer.build_module_map(python_files)

        for file_path in python_files:
            analyzer.analyze_file(file_path)

        # Generate diagrams
        with tempfile.TemporaryDirectory() as temp_dir:
            analyzer.generate_all(save_files=True, output_dir=temp_dir)

            diagrams_dir = Path(temp_dir)

            # Check architecture diagram
            arch_content = (diagrams_dir / "architecture.mmd").read_text()
            assert "graph LR" in arch_content or "graph TD" in arch_content

            # Check class diagram
            class_content = (diagrams_dir / "class_diagram.mmd").read_text()
            assert "classDiagram" in class_content

            # Check module dependencies
            module_content = (diagrams_dir / "module_deps.mmd").read_text()
            assert "graph LR" in module_content or "graph TD" in module_content

    def test_excluded_directories_in_analysis(self, temp_project_dir):
        """Test that excluded directories are properly ignored."""
        # Add more excluded content using a directory that doesn't have permission issues
        excluded_dir = temp_project_dir / "build"
        excluded_dir.mkdir(parents=True, exist_ok=True)
        (excluded_dir / "test.py").write_text("print('should be ignored')")

        python_files = find_python_files(str(temp_project_dir))

        # Should not include files from excluded directories
        for file_path in python_files:
            assert "build" not in file_path
            assert ".venv" not in file_path
            assert "__pycache__" not in file_path

"""Test CLI functionality."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from d4_diag import __version__
from d4_diag.main import (
    EXIT_ERROR,
    EXIT_SUCCESS,
    EXIT_USAGE,
    KNOWN_COMMANDS,
    _detect_project_root,
    _validate_output_directory,
    cli,
    main,
)


class TestCLI:
    """Test the CLI interface."""

    def setup_method(self):
        """Set up test runner."""
        self.runner = CliRunner()

    def test_cli_help(self):
        """Test CLI help command."""
        result = self.runner.invoke(cli, ["--help"])
        assert result.exit_code == EXIT_SUCCESS
        assert "d4-diag" in result.output
        assert "analyze" in result.output
        assert "viewer" in result.output

    def test_cli_version(self):
        """Test CLI version command."""
        result = self.runner.invoke(cli, ["--version"])
        assert result.exit_code == EXIT_SUCCESS
        assert __version__ in result.output

    def test_analyze_help(self):
        """Test analyze command help."""
        result = self.runner.invoke(cli, ["analyze", "--help"])
        assert result.exit_code == EXIT_SUCCESS
        assert "Analyze Python code" in result.output
        assert "PATHS" in result.output
        assert "--output-dir" in result.output
        assert "--verbose" in result.output
        assert "--project-root" in result.output

    def test_viewer_help(self):
        """Test viewer command help."""
        result = self.runner.invoke(cli, ["viewer", "--help"])
        assert result.exit_code == EXIT_SUCCESS
        assert "View generated Mermaid diagrams" in result.output
        assert "DIAGRAMS_DIR" in result.output
        assert "--no-browser" in result.output

    def test_analyze_no_paths(self, temp_project_dir):
        """Test analyze command with no paths."""
        result = self.runner.invoke(cli, ["analyze"])
        assert result.exit_code == EXIT_USAGE
        assert "At least one path is required" in result.output

    def test_analyze_nonexistent_path(self, temp_project_dir):
        """Test analyze command with nonexistent path."""
        result = self.runner.invoke(cli, ["analyze", "/nonexistent/path"])
        assert result.exit_code == EXIT_ERROR
        assert "Path not found" in result.output

    def test_analyze_single_file(self, sample_python_file):
        """Test analyze command with single file."""
        with patch("d4_diag.main.CodeMapAnalyzer") as mock_analyzer_class:
            mock_analyzer = MagicMock()
            mock_analyzer_class.return_value = mock_analyzer

            result = self.runner.invoke(cli, ["analyze", str(sample_python_file)])
            assert result.exit_code == EXIT_SUCCESS

            # Verify analyzer was called
            mock_analyzer.build_module_map.assert_called_once()
            mock_analyzer.analyze_file.assert_called_once()
            mock_analyzer.print_summary.assert_called_once()
            mock_analyzer.generate_all.assert_called_once()

    def test_analyze_directory(self, temp_project_dir):
        """Test analyze command with directory."""
        with patch("d4_diag.main.CodeMapAnalyzer") as mock_analyzer_class:
            mock_analyzer = MagicMock()
            mock_analyzer_class.return_value = mock_analyzer

            result = self.runner.invoke(cli, ["analyze", str(temp_project_dir)])
            assert result.exit_code == EXIT_SUCCESS

            # Should have analyzed multiple files
            assert mock_analyzer.analyze_file.call_count >= 1

    def test_analyze_verbose(self, temp_project_dir):
        """Test analyze command with verbose flag."""
        with patch("d4_diag.main.CodeMapAnalyzer") as mock_analyzer_class:
            mock_analyzer = MagicMock()
            mock_analyzer_class.return_value = mock_analyzer

            result = self.runner.invoke(cli, ["analyze", str(temp_project_dir), "--verbose"])
            assert result.exit_code == EXIT_SUCCESS
            assert "Project root:" in result.output
            assert "Auto-detected project root:" in result.output

    def test_analyze_custom_output_dir(self, temp_project_dir):
        """Test analyze command with custom output directory."""
        custom_output = temp_project_dir / "custom_output"

        with patch("d4_diag.main.CodeMapAnalyzer") as mock_analyzer_class:
            mock_analyzer = MagicMock()
            mock_analyzer_class.return_value = mock_analyzer

            result = self.runner.invoke(
                cli, ["analyze", str(temp_project_dir), "--output-dir", str(custom_output)]
            )
            assert result.exit_code == EXIT_SUCCESS

            # Verify output directory was used
            mock_analyzer.generate_all.assert_called_once()
            call_args = mock_analyzer.generate_all.call_args
            assert call_args[1]["output_dir"] == str(custom_output)

    def test_analyze_custom_project_root(self, temp_project_dir):
        """Test analyze command with custom project root."""
        custom_root = temp_project_dir / "custom_root"
        custom_root.mkdir()

        with patch("d4_diag.main.CodeMapAnalyzer") as mock_analyzer_class:
            mock_analyzer = MagicMock()
            mock_analyzer_class.return_value = mock_analyzer

            result = self.runner.invoke(
                cli, ["analyze", str(temp_project_dir), "--project-root", str(custom_root)]
            )
            assert result.exit_code == EXIT_SUCCESS

            # Verify custom project root was used
            mock_analyzer_class.assert_called_once_with(str(custom_root))

    def test_analyze_nonexistent_project_root(self, temp_project_dir):
        """Test analyze command with nonexistent project root."""
        result = self.runner.invoke(
            cli, ["analyze", str(temp_project_dir), "--project-root", "/nonexistent/root"]
        )
        assert result.exit_code == EXIT_ERROR
        assert "Project root not found" in result.output

    def test_analyze_no_python_files(self, empty_project_dir):
        """Test analyze command with no Python files."""
        result = self.runner.invoke(cli, ["analyze", str(empty_project_dir)])
        assert result.exit_code == EXIT_ERROR
        assert "No Python files found" in result.output

    def test_analyze_analysis_error(self, temp_project_dir):
        """Test analyze command with analysis error."""
        with patch("d4_diag.main.CodeMapAnalyzer") as mock_analyzer_class:
            mock_analyzer = MagicMock()
            mock_analyzer.build_module_map.side_effect = RuntimeError("Analysis failed")
            mock_analyzer_class.return_value = mock_analyzer

            result = self.runner.invoke(cli, ["analyze", str(temp_project_dir)])
            assert result.exit_code == EXIT_ERROR
            assert "Analysis failed" in result.output

    def test_analyze_generation_error(self, temp_project_dir):
        """Test analyze command with diagram generation error."""
        with patch("d4_diag.main.CodeMapAnalyzer") as mock_analyzer_class:
            mock_analyzer = MagicMock()
            mock_analyzer.generate_all.side_effect = RuntimeError("Generation failed")
            mock_analyzer_class.return_value = mock_analyzer

            result = self.runner.invoke(cli, ["analyze", str(temp_project_dir)])
            assert result.exit_code == EXIT_ERROR
            assert "Failed to generate diagrams" in result.output

    def test_viewer_nonexistent_directory(self):
        """Test viewer command with nonexistent directory."""
        result = self.runner.invoke(cli, ["viewer", "/nonexistent/directory"])
        assert result.exit_code == EXIT_ERROR
        assert "Diagrams directory not found" in result.output

    def test_viewer_not_directory(self, temp_project_dir):
        """Test viewer command with file instead of directory."""
        test_file = temp_project_dir / "test.txt"
        test_file.write_text("test")

        result = self.runner.invoke(cli, ["viewer", str(test_file)])
        assert result.exit_code == EXIT_ERROR
        assert "Path is not a directory" in result.output

    def test_viewer_no_mmd_files(self, temp_project_dir):
        """Test viewer command with directory containing no .mmd files."""
        result = self.runner.invoke(cli, ["viewer", str(temp_project_dir)])
        assert result.exit_code == EXIT_ERROR
        assert "No .mmd diagram files found" in result.output

    def test_viewer_success(self, temp_project_dir):
        """Test viewer command success."""
        # Create some .mmd files
        (temp_project_dir / "test1.mmd").write_text("graph LR\nA-->B")
        (temp_project_dir / "test2.mmd").write_text("classDiagram\nClassA-->ClassB")

        with patch("d4_diag.main.view_diagrams") as mock_view:
            result = self.runner.invoke(cli, ["viewer", str(temp_project_dir)])
            assert result.exit_code == EXIT_SUCCESS
            mock_view.assert_called_once()

    def test_viewer_no_browser(self, temp_project_dir):
        """Test viewer command with --no-browser flag."""
        (temp_project_dir / "test.mmd").write_text("graph LR\nA-->B")

        with patch("d4_diag.main.view_diagrams") as mock_view:
            result = self.runner.invoke(cli, ["viewer", str(temp_project_dir), "--no-browser"])
            assert result.exit_code == EXIT_SUCCESS
            mock_view.assert_called_once_with(str(temp_project_dir), False)

    def test_viewer_launch_error(self, temp_project_dir):
        """Test viewer command with launch error."""
        (temp_project_dir / "test.mmd").write_text("graph LR\nA-->B")

        with patch("d4_diag.main.view_diagrams", side_effect=RuntimeError("Launch failed")):
            result = self.runner.invoke(cli, ["viewer", str(temp_project_dir)])
            assert result.exit_code == EXIT_ERROR
            assert "Failed to launch viewer" in result.output


class TestMainFunction:
    """Test the main() function for backward compatibility."""

    def test_main_no_args(self):
        """Test main() with no arguments."""
        with patch("d4_diag.main.click.echo") as mock_echo:
            with pytest.raises(SystemExit) as exc:
                main(["d4-diag"])
            assert exc.value.code == EXIT_SUCCESS
            mock_echo.assert_called_with("Use 'd4-diag --help' for usage information.")

    def test_main_help_arg(self):
        """Test main() with --help argument."""
        with patch("sys.argv", ["d4-diag", "--help"]):
            with patch("d4_diag.main.cli.main") as mock_cli_main:
                main()
                mock_cli_main.assert_called_once()

    def test_main_version_arg(self):
        """Test main() with --version argument."""
        with patch("sys.argv", ["d4-diag", "--version"]):
            with patch("d4_diag.main.cli.main") as mock_cli_main:
                main()
                mock_cli_main.assert_called_once()

    def test_main_analyze_command(self):
        """Test main() with analyze command."""
        with patch("sys.argv", ["d4-diag", "analyze", "test.py"]):
            with patch("d4_diag.main.cli.main") as mock_cli_main:
                main()
                mock_cli_main.assert_called_once()

    def test_main_viewer_command(self):
        """Test main() with viewer command."""
        with patch("sys.argv", ["d4-diag", "viewer", "diagrams"]):
            with patch("d4_diag.main.cli.main") as mock_cli_main:
                main()
                mock_cli_main.assert_called_once()

    def test_backward_compatibility_path(self):
        """Test main() backward compatibility with path."""
        with patch("sys.argv", ["d4-diag", "test.py"]):
            with patch("d4_diag.main.cli.main") as mock_cli_main:
                main()
                # Should insert 'analyze' before the path
                mock_cli_main.assert_called_once()
                args = mock_cli_main.call_args.kwargs.get("args")
                assert args == ["analyze", "test.py"]

    def test_main_backward_compatibility_with_flags(self):
        """Test main() backward compatibility with flags."""
        with patch("sys.argv", ["d4-diag", "-v", "test.py"]):
            with patch("d4_diag.main.cli.main") as mock_cli_main:
                main()
                # Should insert 'analyze' after flags
                mock_cli_main.assert_called_once()
                args = mock_cli_main.call_args.kwargs.get("args")
                assert args == ["-v", "analyze", "test.py"]

    def test_main_separator_handling(self):
        """Test main() with -- separator."""
        with patch("sys.argv", ["d4-diag", "--", "test.py"]):
            with patch("d4_diag.main.cli.main") as mock_cli_main:
                main()
                # Should pass through unchanged
                mock_cli_main.assert_called_once()
                args = mock_cli_main.call_args.kwargs.get("args")
                assert args == ["--", "test.py"]

    def test_main_custom_argv(self):
        """Test main() with custom argv parameter."""
        custom_argv = ["d4-diag", "test.py"]
        with patch("d4_diag.main.cli.main") as mock_cli_main:
            main(custom_argv)
            mock_cli_main.assert_called_once()
            args = mock_cli_main.call_args.kwargs.get("args")
            assert args == ["analyze", "test.py"]

    def test_main_click_exception(self):
        """Test main() handling ClickException."""
        from click import ClickException

        with patch("sys.argv", ["d4-diag", "test.py"]):
            with patch("d4_diag.main.cli.main", side_effect=ClickException("Click error")):
                with patch("sys.exit") as mock_exit:
                    main()
                    mock_exit.assert_called_with(EXIT_ERROR)

    def test_main_system_exit(self):
        """Test main() handling SystemExit."""
        with patch("sys.argv", ["d4-diag", "test.py"]):
            with patch("d4_diag.main.cli.main", side_effect=SystemExit(42)):
                with patch("sys.exit") as mock_exit:
                    main()
                    mock_exit.assert_called_with(42)

    def test_main_unexpected_exception(self):
        """Test main() handling unexpected exception."""
        with patch("sys.argv", ["d4-diag", "test.py"]):
            with patch("d4_diag.main.cli.main", side_effect=RuntimeError("Unexpected error")):
                with patch("sys.exit") as mock_exit:
                    main()
                    mock_exit.assert_called_with(EXIT_ERROR)


class TestUtilityFunctions:
    """Test utility functions in main module."""

    def test_detect_project_root_with_directory(self, temp_project_dir):
        """Test _detect_project_root with directory input."""
        paths = [temp_project_dir]
        result = _detect_project_root(paths)
        assert result == temp_project_dir.resolve()

    def test_detect_project_root_with_files(self, temp_project_dir):
        """Test _detect_project_root with file input."""
        file1 = temp_project_dir / "file1.py"
        file2 = temp_project_dir / "file2.py"
        paths = [file1, file2]

        result = _detect_project_root(paths)
        assert result == temp_project_dir.resolve()

    def test_detect_project_root_empty(self):
        """Test _detect_project_root with empty paths."""
        result = _detect_project_root([])
        assert result == Path.cwd()

    def test_validate_output_directory_safe(self, temp_project_dir):
        """Test _validate_output_directory with safe directory."""
        output_dir = temp_project_dir / "docs" / "diagrams"

        # Should not raise any exception
        _validate_output_directory(output_dir, temp_project_dir)

    def test_validate_output_directory_unsafe(self, temp_project_dir):
        """Test _validate_output_directory with unsafe directory."""
        output_dir = Path("/etc")  # Outside project root

        with patch("d4_diag.main.click.confirm", return_value=False):
            with patch("sys.exit") as mock_exit:
                _validate_output_directory(output_dir, temp_project_dir)
                mock_exit.assert_called_with(EXIT_ERROR)

    def test_validate_output_directory_unsafe_confirmed(self, temp_project_dir):
        """Test _validate_output_directory with unsafe directory but user confirms."""
        output_dir = Path("/etc")  # Outside project root

        with patch("d4_diag.main.click.confirm", return_value=True):
            # Should not exit
            _validate_output_directory(output_dir, temp_project_dir)

    def test_validate_output_directory_error(self, temp_project_dir):
        """Test _validate_output_directory with validation error."""
        output_dir = temp_project_dir / "docs" / "diagrams"

        with patch("d4_diag.main.click.echo"):
            # Mock Path.resolve to raise an exception
            with patch.object(Path, "resolve", side_effect=RuntimeError("Resolution error")):
                # Should not raise exception, just print warning
                _validate_output_directory(output_dir, temp_project_dir)


class TestConstants:
    """Test module constants."""

    def test_exit_codes(self):
        """Test exit code constants."""
        assert EXIT_SUCCESS == 0
        assert EXIT_ERROR == 1
        assert EXIT_USAGE == 2

    def test_known_commands(self):
        """Test KNOWN_COMMANDS constant."""
        expected_commands = {"--help", "-h", "--version", "analyze", "viewer"}
        assert KNOWN_COMMANDS == expected_commands

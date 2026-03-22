"""Test basic CLI functionality."""

from click.testing import CliRunner

from d4_diag.main import cli


def test_cli_import():
    """Test that CLI can be imported."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "d4-diag" in result.output

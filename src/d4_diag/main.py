"""Main entry point for d4-diag - coordinates code analysis and diagram generation."""

import sys
from pathlib import Path
from typing import List, Optional, Sequence

import click

from . import __version__
from .generate_mermaid import CodeMapAnalyzer
from .utils import find_python_files
from .viewer_mermaid import view_diagrams

__all__ = ["cli", "main"]

# Exit code constants
EXIT_SUCCESS = 0
EXIT_ERROR = 1
EXIT_USAGE = 2

# Known commands for backward compatibility
KNOWN_COMMANDS = {"--help", "-h", "--version", "analyze", "viewer"}


@click.group(context_settings=dict(help_option_names=["-h", "--help"]))
@click.version_option(version=__version__, prog_name="d4-diag")
def cli():
    """Analyze Python code and generate dependency diagrams.

    d4-diag analyzes Python files and directories to create Mermaid diagrams
    showing module dependencies, class relationships, and code structure.

    Available commands:
        analyze    Analyze Python code and generate diagrams
        viewer     View generated Mermaid diagrams
    """


def _validate_input_paths(paths: List[Path]) -> None:
    """Validate that input paths exist."""
    for path in paths:
        if not path.exists():
            click.echo(f"Error: Path not found: {path}", err=True)
            sys.exit(EXIT_ERROR)

    if not paths:
        click.echo("Error: At least one path is required.", err=True)
        click.echo("Use 'd4-diag analyze --help' for usage information.")
        sys.exit(EXIT_USAGE)


def _resolve_project_root(project_root: Optional[Path], paths: List[Path], verbose: bool) -> Path:
    """Resolve and validate project root directory."""
    if project_root:
        if not project_root.exists():
            click.echo(f"Error: Project root not found: {project_root}", err=True)
            sys.exit(EXIT_ERROR)
        project_root = project_root.resolve()
    else:
        # Auto-detect project root
        project_root = _detect_project_root(paths)
        if verbose:
            click.echo(f"Auto-detected project root: {project_root}")

    if verbose:
        click.echo(f"Project root: {project_root}")

    return project_root


def _collect_python_files(paths: List[Path], verbose: bool) -> List[str]:
    """Collect all Python files from input paths."""
    all_files = []

    for path in paths:
        if path.is_dir():
            if verbose:
                click.echo(f"Scanning directory: {path}")
            found = find_python_files(str(path))
            if verbose:
                click.echo(f"  Found {len(found)} Python files")
            # Ensure all paths are strings for consistency with analyzer
            all_files.extend([str(f) for f in found])
        elif path.suffix == ".py":
            if verbose:
                click.echo(f"Adding file: {path}")
            all_files.append(str(path))
        else:
            click.echo(f"Warning: Skipping non-Python file: {path}", err=True)

    if not all_files:
        click.echo("Error: No Python files found!", err=True)
        sys.exit(EXIT_ERROR)

    return all_files


def _setup_output_directory(output_dir: Optional[Path], project_root: Path) -> Path:
    """Setup and validate output directory."""
    if output_dir is None:
        output_dir = project_root / "docs" / "diagrams"

    # Validate output directory is safe
    _validate_output_directory(output_dir, project_root)

    return output_dir


def _run_analysis(project_root: Path, all_files: List[str], verbose: bool) -> CodeMapAnalyzer:
    """Run code analysis on all files."""
    try:
        analyzer = CodeMapAnalyzer(str(project_root))
        analyzer.build_module_map(all_files)

        click.echo(f"\nAnalyzing {len(all_files)} file(s)...")
        for fp in all_files:
            if verbose:
                click.echo(f"  Processing: {fp}")
            try:
                analyzer.analyze_file(fp)
            except (OSError, ValueError, SyntaxError) as e:
                click.echo(f"Warning: Failed to analyze {fp}: {e}", err=True)
                continue

        analyzer.print_summary()
        return analyzer
    except (OSError, RuntimeError, ValueError) as e:
        click.echo(f"Error: Analysis failed: {e}", err=True)
        sys.exit(EXIT_ERROR)


def _generate_diagrams(analyzer: CodeMapAnalyzer, output_dir: Path) -> None:
    """Generate Mermaid diagrams."""
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        click.echo(f"\nGenerating diagrams in: {output_dir}")
        analyzer.generate_all(save_files=True, output_dir=str(output_dir))
    except OSError as e:
        click.echo(f"Error: Failed to create output directory: {e}", err=True)
        sys.exit(EXIT_ERROR)
    except RuntimeError as e:
        click.echo(f"Error: Failed to generate diagrams: {e}", err=True)
        sys.exit(EXIT_ERROR)


@cli.command()
@click.argument("paths", nargs=-1, type=click.Path(exists=False, path_type=Path))
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(path_type=Path),
    help="Output directory for diagrams (default: docs/diagrams)",
    default=None,
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option(
    "--project-root",
    "-r",
    type=click.Path(exists=False, path_type=Path),
    help="Project root directory (auto-detected if not specified)",
)
def analyze(paths, output_dir, verbose, project_root):
    """Analyze Python code and generate dependency diagrams.

    PATHS: Python files or directories to analyze

    Examples:
        d4-diag analyze ./src
        d4-diag analyze file1.py file2.py
        d4-diag analyze /path/to/project --output-dir ./docs
        d4-diag analyze . --verbose
    """
    # Validate input paths
    _validate_input_paths(paths)

    # Resolve project root
    project_root = _resolve_project_root(project_root, paths, verbose)

    # Collect Python files
    all_files = _collect_python_files(paths, verbose)

    # Setup output directory
    output_dir = _setup_output_directory(output_dir, project_root)

    # Run analysis
    analyzer = _run_analysis(project_root, all_files, verbose)

    # Generate diagrams
    _generate_diagrams(analyzer, output_dir)

    click.echo(f"\nDone! View diagrams with: d4-diag viewer {output_dir}")
    click.echo(f"Or use: poetry run viewer {output_dir}")


@cli.command()
@click.argument(
    "diagrams_dir", type=click.Path(path_type=Path), default="docs/diagrams", required=False
)
@click.option(
    "--no-browser", is_flag=True, help="Generate HTML viewer but don't open browser automatically"
)
def viewer(diagrams_dir, no_browser):
    """View generated Mermaid diagrams in an interactive HTML viewer.

    DIAGRAMS_DIR: Directory containing .mmd diagram files (default: docs/diagrams)

    Examples:
        d4-diag viewer              # Uses default docs/diagrams
        d4-diag viewer ./docs/diagrams
        d4-diag viewer /path/to/diagrams --no-browser
    """
    # Validate that diagrams directory exists
    if not diagrams_dir.exists():
        click.echo(f"Error: Diagrams directory not found: {diagrams_dir}", err=True)
        click.echo("Hint: Run 'd4-diag analyze' first to generate diagrams.", err=True)
        sys.exit(EXIT_ERROR)

    if not diagrams_dir.is_dir():
        click.echo(f"Error: Path is not a directory: {diagrams_dir}", err=True)
        sys.exit(EXIT_ERROR)

    # Check if directory contains .mmd files
    mmd_files = list(diagrams_dir.glob("*.mmd"))
    if not mmd_files:
        click.echo(f"Warning: No .mmd diagram files found in: {diagrams_dir}", err=True)
        click.echo("Hint: Run 'd4-diag analyze' first to generate diagrams.", err=True)
        sys.exit(EXIT_ERROR)

    click.echo(f"Opening viewer for diagrams in: {diagrams_dir}")
    open_browser = not no_browser

    try:
        view_diagrams(str(diagrams_dir), open_browser)
    except (OSError, RuntimeError, ValueError) as e:
        click.echo(f"Error: Failed to launch viewer: {e}", err=True)
        sys.exit(EXIT_ERROR)


def _detect_project_root(paths: Sequence[Path]) -> Path:
    """Auto-detect project root from given paths."""
    # Use the first directory or parent of first file as project root
    for path in paths:
        if path.is_dir():
            return path.resolve()

    # All paths are files, use their common parent
    if paths:
        return paths[0].parent.resolve()

    # Fallback to current directory
    return Path.cwd()


def _validate_output_directory(output_dir: Path, project_root: Path) -> None:
    """Validate that output directory is safe to use."""
    try:
        # Resolve the path to check if it's outside project root
        output_abs = output_dir.resolve()
        project_abs = project_root.resolve()

        # Check if output directory would be outside project root
        try:
            if not output_abs.is_relative_to(project_abs):
                click.echo(
                    f"Warning: Output directory '{output_dir}' is outside project root. "
                    f"This may write to unexpected locations.",
                    err=True,
                )
                if not click.confirm("Continue anyway?", default=False):
                    sys.exit(EXIT_ERROR)
        except AttributeError:
            # Python < 3.9 fallback
            try:
                output_abs.relative_to(project_abs)
            except ValueError:
                click.echo(
                    f"Warning: Output directory '{output_dir}' is outside project root. "
                    f"This may write to unexpected locations.",
                    err=True,
                )
                if not click.confirm("Continue anyway?", default=False):
                    sys.exit(EXIT_ERROR)
    except (OSError, RuntimeError, ValueError) as e:
        click.echo(f"Warning: Could not validate output directory: {e}", err=True)


# Maintain backward compatibility - default command is analyze
def main(argv: Optional[List[str]] = None) -> None:
    """Main entry point for backward compatibility.

    Args:
        argv: Command line arguments (defaults to sys.argv if None)
    """
    if argv is None:
        argv = list(sys.argv)  # Create a copy to avoid mutating sys.argv

    # If no arguments provided, show help
    if len(argv) == 1:
        click.echo("Use 'd4-diag --help' for usage information.")
        sys.exit(EXIT_SUCCESS)

    # Handle -- separator
    if len(argv) > 1 and argv[1] == "--":
        cli.main(args=argv[1:], standalone_mode=False)
        return

    # If first argument is not a known command, treat as analyze for backward compatibility
    if len(argv) > 1 and argv[1] not in KNOWN_COMMANDS:
        # Find the right position to insert 'analyze' (before first non-flag)
        insert_pos = 1
        for i, arg in enumerate(argv[1:], 1):
            if arg.startswith("-") and arg not in ["--help", "-h", "--version"]:
                insert_pos = i + 1
            else:
                break
        argv.insert(insert_pos, "analyze")

    try:
        cli.main(args=argv[1:], standalone_mode=False)
    except click.ClickException as e:
        e.show()
        sys.exit(EXIT_ERROR)
    except SystemExit as e:
        sys.exit(e.code)
    except (OSError, RuntimeError, ValueError) as e:
        click.echo(f"Unexpected error: {e}", err=True)
        sys.exit(EXIT_ERROR)


if __name__ == "__main__":
    main()

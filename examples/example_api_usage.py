#!/usr/bin/env python3
"""
Example demonstrating the enhanced d4-diag API.

The new API returns diagrams as a dictionary by default,
with optional file saving.
"""

from pathlib import Path

from d4_diag import CodeMapAnalyzer, find_python_files


def example_1_return_dictionary():
    """Example 1: Generate diagrams and get them as a dictionary (no files saved)"""
    print("=" * 60)
    print("Example 1: Return diagrams as dictionary (default behavior)")
    print("=" * 60)

    project_root = Path(__file__).resolve().parents[1] / "src" / "d4_diag"
    files = find_python_files(str(project_root))

    analyzer = CodeMapAnalyzer(str(project_root))
    analyzer.build_module_map(files)

    for fp in files:
        analyzer.analyze_file(fp)

    diagrams = analyzer.generate_all()

    print(f"\nReturned {len(diagrams)} diagrams:")
    for filename, content in diagrams.items():
        lines = content.count("\n") + 1
        chars = len(content)
        print(f"  {filename}: {lines} lines, {chars} characters")

    print("\nFirst 200 chars of architecture diagram:")
    print(diagrams["architecture.mmd"][:200])
    print("...")

    return diagrams


def example_2_save_to_default_location():
    """Example 2: Save diagrams to default location (project_root/docs/diagrams)"""
    print("\n" + "=" * 60)
    print("Example 2: Save to default location")
    print("=" * 60)

    project_root = Path(__file__).resolve().parents[1] / "src" / "d4_diag"
    files = find_python_files(str(project_root))

    analyzer = CodeMapAnalyzer(str(project_root))
    analyzer.build_module_map(files)

    for fp in files:
        analyzer.analyze_file(fp)

    diagrams = analyzer.generate_all(save_files=True)

    print(f"\nFiles saved to: {project_root}/docs/diagrams")
    print(f"Also returned dictionary with {len(diagrams)} diagrams")

    return diagrams


def example_3_save_to_custom_location(tmp_dir: Path):
    """Example 3: Save diagrams to custom location"""
    print("\n" + "=" * 60)
    print("Example 3: Save to custom location")
    print("=" * 60)

    project_root = Path(__file__).resolve().parents[1] / "src" / "d4_diag"
    files = find_python_files(str(project_root))

    analyzer = CodeMapAnalyzer(str(project_root))
    analyzer.build_module_map(files)

    for fp in files:
        analyzer.analyze_file(fp)

    custom_output = tmp_dir / "custom_diagrams"
    diagrams = analyzer.generate_all(save_files=True, output_dir=str(custom_output))

    print(f"\nFiles saved to: {custom_output}")
    print(f"Also returned dictionary with {len(diagrams)} diagrams")

    return diagrams


def example_4_process_diagrams():
    """Example 4: Process diagrams programmatically"""
    print("\n" + "=" * 60)
    print("Example 4: Process diagrams programmatically")
    print("=" * 60)

    project_root = Path(__file__).resolve().parents[1] / "src" / "d4_diag"
    files = find_python_files(str(project_root))

    analyzer = CodeMapAnalyzer(str(project_root))
    analyzer.build_module_map(files)

    for fp in files:
        analyzer.analyze_file(fp)

    diagrams = analyzer.generate_all()

    for filename, content in diagrams.items():
        print(f"\n{filename}:")
        node_count = content.count("[")
        print(f"  Approximate nodes: {node_count}")
        edge_count = content.count("-->")
        print("  Edges: " + str(edge_count))
        if "classDiagram" in content:
            print("  Type: Class Diagram")
        elif "graph LR" in content:
            print("  Type: Graph (Left-to-Right)")
        elif "graph TD" in content:
            print("  Type: Graph (Top-to-Down)")

    return diagrams


if __name__ == "__main__":
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        example_1_return_dictionary()
        example_2_save_to_default_location()
        example_3_save_to_custom_location(Path(tmp))
        example_4_process_diagrams()

    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)

# Programmatic Usage

Use **d4-diag** as a library for diagram generation in scripts, CI, or services.

## Basic flow

```python
from d4_diag import CodeMapAnalyzer, find_python_files

project_root = "/path/to/project"
files = find_python_files(project_root)

analyzer = CodeMapAnalyzer(project_root)
analyzer.build_module_map(files)

for file_path in files:
    analyzer.analyze_file(file_path)

# Return dict — does not write files by default
diagrams = analyzer.generate_all()
print(diagrams["architecture.mmd"][:200])

# Save to default location
analyzer.generate_all(save_files=True)

# Save to custom directory
analyzer.generate_all(save_files=True, output_dir="/custom/output")
```

## `generate_all` API

```python
diagrams: dict[str, str] = analyzer.generate_all(
    save_files=False,       # True to write .mmd files
    output_dir=None,        # default: {project_root}/docs/diagrams
)
```

Keys: `architecture.mmd`, `class_diagram.mmd`, `module_deps.mmd`.

Individual generators also return strings:

```python
arch = analyzer.generate_architecture()
analyzer.generate_class_diagram(output_file="out/class.mmd")
```

## Open the viewer from Python

```python
from d4_diag.viewer_mermaid import view_diagrams

view_diagrams("docs/diagrams", open_browser=False)
```

## Use cases

### CI / documentation pipeline

```python
import os
from d4_diag import CodeMapAnalyzer, find_python_files

def generate_docs_diagrams():
    root = os.environ.get("CI_PROJECT_DIR", ".")
    files = find_python_files(root)
    analyzer = CodeMapAnalyzer(root)
    analyzer.build_module_map(files)
    for fp in files:
        analyzer.analyze_file(fp)
    analyzer.generate_all(
        save_files=True,
        output_dir=os.path.join(root, "docs", "diagrams"),
    )
```

### Custom metrics report

```python
from d4_diag import CodeMapAnalyzer, find_python_files

def analyze_and_report(project_path: str) -> dict:
    files = find_python_files(project_path)
    analyzer = CodeMapAnalyzer(project_path)
    analyzer.build_module_map(files)
    for fp in files:
        analyzer.analyze_file(fp)

    diagrams = analyzer.generate_all()
    return {
        "files": len(analyzer.files),
        "classes": sum(len(f["classes"]) for f in analyzer.files.values()),
        "functions": sum(len(f["functions"]) for f in analyzer.files.values()),
        "imports": len(analyzer.import_edges),
        "diagram_sizes": {k: len(v) for k, v in diagrams.items()},
    }
```

### Batch projects

```python
from d4_diag import CodeMapAnalyzer, find_python_files

def analyze_projects(paths: dict[str, str]) -> None:
    for name, root in paths.items():
        files = find_python_files(root)
        analyzer = CodeMapAnalyzer(root)
        analyzer.build_module_map(files)
        for fp in files:
            analyzer.analyze_file(fp)
        out = f"analysis_results/{name}"
        analyzer.generate_all(save_files=True, output_dir=out)
        print(f"{name}: {len(files)} files → {out}")
```

## Migration note

Older examples called `generate_all(output_dir)` with a positional output path. Current API:

```python
# Before (legacy)
analyzer.generate_all("docs/diagrams")

# Now
analyzer.generate_all(save_files=True, output_dir="docs/diagrams")
```

Calling `generate_all()` with no arguments returns content only (no files written).

## Error handling

- `analyze_file` logs syntax errors and continues
- `find_python_files` returns `[]` for missing/non-directory paths
- Empty file list should be handled before analysis

```python
files = find_python_files(project_path)
if not files:
    raise SystemExit("No Python files found")
```

## Related

- [API Reference](../reference/api.md)
- [CLI Reference](../reference/cli.md)
- [Examples](../examples.md)

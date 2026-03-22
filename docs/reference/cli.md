# CLI Reference

Complete command-line interface reference for D4-Diag.

## Main Command

Analyze Python code and generate diagrams.

### Syntax

```bash
poetry run main <path> [path2 ...]
```

### Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `<path>` | string | Yes | Python file or directory to analyze |
| `[path2 ...]` | string | No | Additional paths to analyze |

### Examples

```bash
# Single file
poetry run main app.py

# Single directory
poetry run main src/

# Multiple paths
poetry run main src/ tests/ scripts/

# Current directory
poetry run main .
```

### Output

Generates three Mermaid diagram files in `<project_root>/docs/diagrams/`:
- `architecture.mmd` - Architecture overview
- `class_diagram.mmd` - Class diagram
- `module_deps.mmd` - Module dependencies

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | No arguments provided |
| 1 | No Python files found |

## Viewer Command

Launch interactive diagram viewer.

### Syntax

```bash
poetry run viewer <diagrams_directory>
```

### Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `<diagrams_directory>` | string | Yes | Directory containing `.mmd` files |

### Examples

```bash
# View diagrams from analyzed project
poetry run viewer /path/to/project/docs/diagrams

# View diagrams from current directory
poetry run viewer docs/diagrams
```

### Behavior

1. Scans directory for `.mmd` files
2. Generates temporary HTML file
3. Opens HTML in default browser
4. Displays interactive diagram viewer

### Output

```
Scanning for diagrams in: /path/to/diagrams

Found 3 diagram file(s):
  - architecture.mmd
  - class_diagram.mmd
  - module_deps.mmd

Generated viewer: /tmp/tmpXXXXXX.html
Opening in browser...
```

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | No arguments provided |
| 1 | Directory not found |
| 1 | No `.mmd` files found |

## Environment

### Python Version

Requires Python 3.8 or higher.

### Dependencies

Runtime dependencies:
- Python standard library only

Development dependencies:
- pytest (testing)
- mkdocs (documentation)
- mkdocs-material (documentation theme)

## Configuration

D4-Diag has no configuration files. All behavior is controlled via command-line arguments.

## Programmatic Usage

You can also use D4-Diag as a Python module:

```python
from d4_diag.main import CodeMapAnalyzer

# Create analyzer
analyzer = CodeMapAnalyzer(project_root="/path/to/project")

# Build module map
analyzer.build_module_map(file_paths)

# Analyze files
for file_path in file_paths:
    analyzer.analyze_file(file_path)

# Generate diagrams
analyzer.generate_all(output_dir="docs/diagrams")
```

See [API Reference](api.md) for details.

## Next Steps

- [API Reference](api.md) - Programmatic usage
- [Examples](../examples.md) - Real-world usage examples

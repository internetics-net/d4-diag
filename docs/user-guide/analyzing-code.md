# Analyzing Code

Learn how to use D4-Diag's analysis capabilities effectively.

## Command Line Interface

### Basic Syntax

```bash
d4-diag analyze <path> [path2 ...]
```

Or as a Python module:

```bash
python -m d4_diag analyze <path> [path2 ...]
```

### Arguments

- `<path>` - Python file or directory to analyze
- Multiple paths can be provided

### Examples

```bash
# Single file
d4-diag analyze app.py

# Single directory
d4-diag analyze src/

# Multiple paths
d4-diag analyze src/ tests/ scripts/

# Current directory
d4-diag analyze .

# With verbose output
d4-diag analyze src/ --verbose

# Custom output directory
d4-diag analyze src/ --output-dir ./docs/diagrams
```

## What Gets Analyzed

D4-Diag performs static analysis using Python's AST (Abstract Syntax Tree):

### Detected Elements

- **Classes** - All class definitions with their methods
- **Functions** - Top-level function definitions
- **Imports** - Import statements (`import` and `from ... import`)
- **Inheritance** - Base classes for each class

### Not Analyzed

- Runtime behavior
- Dynamic imports
- Decorators (shown but not analyzed)
- Type hints (shown but not analyzed)

## Output Location

Diagrams are generated in:
```
<project_root>/docs/diagrams/
├── architecture.mmd
├── class_diagram.mmd
└── module_deps.mmd
```

The project root is determined by:
1. First directory in arguments → use as root
2. Only files provided → use parent directory of first file
3. Fallback → current working directory

## Analysis Summary

After analysis, you'll see a summary:

```
=== Code Map Summary ===
Files analyzed:   32
Classes found:    59
Functions found:  56
Import links:     37

Project structure:
  src/models.py  (16 classes)
  src/server.py  (3 classes)
  src/main.py  (5 functions)
  ...
```

## Large Projects

D4-Diag is optimized for large codebases:

- **Fast AST parsing** - No code execution required
- **Deduplication** - Import edges are deduplicated
- **Lazy rendering** - Viewer only renders visible diagrams
- **Scrollable output** - Large diagrams are scrollable

### Performance Tips

For very large projects (100+ files):

1. **Analyze specific subdirectories** instead of entire repo
2. **Exclude test files** if not needed
3. **Use module dependencies** to understand high-level structure first

## Troubleshooting

### Syntax Errors

Files with syntax errors are skipped:
```
Syntax error in src/broken.py: invalid syntax
```

The analysis continues with remaining files.

### No Python Files Found

```
No Python files found!
```

Check that:
- Path exists and is correct
- Directory contains `.py` files
- You have read permissions

### Import Resolution

D4-Diag resolves imports by:
1. Building a module map from analyzed files
2. Matching import statements to project files
3. External imports (e.g., `numpy`) are ignored

Only **project-local** imports create edges in the module dependency diagram.

## Next Steps

- [Diagram Types](diagram-types.md) - Understand each diagram
- [Viewing Diagrams](viewing-diagrams.md) - Interactive viewer features
- [CLI Reference](../reference/cli.md) - Complete command reference

# Analyzing Code

How to run **d4-diag** analysis effectively.

## CLI syntax

```bash
d4-diag analyze <path> [path ...] [options]
```

Legacy (implicit `analyze`):

```bash
d4-diag ./src
```

Module form:

```bash
python -m d4_diag analyze ./src
```

## Options

| Option | Description |
|--------|-------------|
| `-v`, `--verbose` | Show directories scanned and each file processed |
| `-o`, `--output-dir` | Output directory (default: `{project_root}/docs/diagrams`) |
| `-r`, `--project-root` | Override auto-detected project root |

## Examples

```bash
d4-diag analyze app.py
d4-diag analyze src/
d4-diag analyze src/ tests/ scripts/
d4-diag analyze . --verbose
d4-diag analyze src/ --output-dir ./docs/diagrams
d4-diag analyze ./packages/foo --project-root ./packages/foo
```

## What gets analyzed

Static analysis via Python **AST**:

| Detected | Notes |
|----------|-------|
| Classes | Name, methods, base classes |
| Functions | Top-level definitions |
| Imports | `import` and `from … import` |
| Inheritance | Base class names |

Not analyzed: runtime behavior, dynamic imports, decorator bodies, type hints (shown in source only).

## File discovery

`find_python_files` walks directories with:

- **Excluded dirs:** `.venv`, `venv`, `__pycache__`, `.git`, `.pytest_cache`, `.mypy_cache`, `.ruff_cache`, `node_modules`, `dist`, `build`, `site-packages`, `*.egg-info`, …
- **No symlink following** — symlinked directories are not descended; symlinked `.py` files are skipped
- **Size limit:** files **> 10 MB** are skipped during analysis

## Project root detection

1. First **directory** argument → used as root
2. Only **files** → parent of the first file
3. Fallback → current working directory

Use `--project-root` when auto-detection is wrong (monorepos, nested packages).

## Output

```
<output-dir>/
├── architecture.mmd
├── class_diagram.mmd
└── module_deps.mmd
```

## Summary output

```
=== Code Map Summary ===
Files analyzed:   32
Classes found:    59
Functions found:  56
Import links:     37
```

## Output directory safety

If `--output-dir` resolves outside the project root, d4-diag warns and asks for confirmation before writing.

## Large projects

Tips for 100+ files:

1. Analyze subdirectories (`src/`, `lib/`) instead of the whole monorepo
2. Start with **module dependencies** for high-level structure
3. Use `--verbose` to see which paths are included

## Troubleshooting

**No Python files found**

- Path exists and contains `.py` files
- Files are not only under excluded dirs or symlinks
- Read permissions are OK

**Syntax error in file**

Analysis continues; the file may be omitted or partial:

```
Warning: Failed to analyze src/broken.py: ...
```

**Import edges missing**

Only **project-local** imports become edges. Third-party packages are ignored.

## Next steps

- [Diagram Types](diagram-types.md)
- [Viewing Diagrams](viewing-diagrams.md)
- [CLI Reference](../reference/cli.md)
- [Security](../SECURITY.md)

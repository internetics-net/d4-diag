# CLI Reference

Complete command-line reference for **d4-diag** v0.1.5.

## Global

```bash
d4-diag --help
d4-diag --version
d4-diag -h
```

| Exit code | Meaning |
|-----------|---------|
| `0` | Success |
| `1` | Runtime error (missing paths, analysis failure, viewer error) |
| `2` | Usage error (e.g. no paths for `analyze`) |

## `analyze`

Analyze Python files and generate Mermaid diagrams.

### Syntax

```bash
d4-diag analyze <path> [path ...] [options]
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `path` | Yes (one or more) | `.py` file or directory to scan |

### Options

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--output-dir` | `-o` | `{project_root}/docs/diagrams` | Where to write `.mmd` files |
| `--project-root` | `-r` | Auto-detected | Root for relative paths and module resolution |
| `--verbose` | `-v` | off | Print discovery and per-file progress |

### Examples

```bash
d4-diag analyze ./src
d4-diag analyze app.py lib/
d4-diag analyze . --verbose
d4-diag analyze src/ tests/ --output-dir ./docs/diagrams
d4-diag analyze ./packages/foo --project-root ./packages/foo
```

### Backward compatibility

If the first argument is not a known subcommand (`analyze`, `viewer`, `--help`, `--version`), **`analyze` is inserted automatically**:

```bash
d4-diag ./src              # same as d4-diag analyze ./src
d4-diag ./src --verbose
```

### Output

Creates (or overwrites) three files in the output directory:

- `architecture.mmd`
- `class_diagram.mmd`
- `module_deps.mmd`

Prints a summary (files, classes, functions, import links) to stdout.

### Output directory safety

If `-o` resolves **outside** the project root, the CLI warns and prompts `Continue anyway? [y/N]`. In CI, keep the output path inside the project or use a TTY-aware wrapper.

---

## `viewer`

Open an interactive HTML viewer for generated diagrams.

### Syntax

```bash
d4-diag viewer [diagrams_dir] [options]
```

### Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `diagrams_dir` | `docs/diagrams` | Directory containing `*.mmd` files |

### Options

| Option | Description |
|--------|-------------|
| `--no-browser` | Write `_d4_diag_viewer.html` but do not open the browser |

### Examples

```bash
d4-diag viewer
d4-diag viewer ./docs/diagrams
d4-diag viewer /path/to/diagrams --no-browser
```

### Behavior

1. Finds all `*.mmd` files in the directory (max **10 MB** each).
2. Writes `<diagrams_dir>/_d4_diag_viewer.html`.
3. Opens the HTML file in the default browser (unless `--no-browser`).

### Sample output

```
Scanning for diagrams in: docs/diagrams

Found 3 diagram file(s):
  - architecture.mmd
  - class_diagram.mmd
  - module_deps.mmd

Generated viewer: .../docs/diagrams/_d4_diag_viewer.html
Opening browser...
```

---

## Run as a module

```bash
python -m d4_diag analyze ./src
python -m d4_diag viewer ./docs/diagrams
python -m d4_diag --help
```

---

## Poetry script aliases

From a dev checkout (`poetry install`):

| Script | Equivalent |
|--------|------------|
| `poetry run d4-diag …` | Full CLI |
| `poetry run main …` | Same entry point as `d4-diag` |
| `poetry run view <dir>` | Standalone viewer (`viewer_mermaid.main`) |
| `poetry run test` | Test runner (`tests.run_tests`) |

---

## Environment

- **Python:** 3.8.1+
- **Runtime dependency:** [Click](https://click.palletsprojects.com/) 8.x
- **No config file** — behavior is controlled only by CLI flags

---

## Related

- [Analyzing Code](../user-guide/analyzing-code.md)
- [Viewing Diagrams](../user-guide/viewing-diagrams.md)
- [API Reference](api.md)
- [Security](../SECURITY.md)

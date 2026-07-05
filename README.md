# d4-diag

Python static analysis tool that generates **Mermaid** diagrams for project structure, class relationships, and module dependencies — with an interactive HTML viewer.

**Version:** `0.1.6` · **Python:** 3.8.1+

## Links

- [Documentation](https://internetics-net.github.io/d4-diag/)
- [Repository](https://github.com/internetics-net/d4-diag)
- [Issues](https://github.com/internetics-net/d4-diag/issues)

## Quick start

```bash
pip install d4-diag

d4-diag analyze ./src
d4-diag viewer ./docs/diagrams
```

From a dev checkout:

```bash
git clone https://github.com/internetics-net/d4-diag.git
cd d4-diag
poetry install
poetry run d4-diag analyze src/
poetry run d4-diag viewer docs/diagrams
```

## Features

- **AST-based analysis** — classes, functions, imports, inheritance (no code execution)
- **Three diagram types** — architecture, class diagram, module dependencies
- **Smart discovery** — skips venvs, caches, build dirs, and **symlinks**
- **Interactive viewer** — tabbed HTML UI with lazy Mermaid rendering
- **Click CLI** — `analyze` and `viewer` subcommands; legacy `d4-diag ./src` still works
- **Programmatic API** — `CodeMapAnalyzer` returns diagrams as a dict or saves `.mmd` files
- **Safety** — HTML escaping in the viewer, Mermaid `securityLevel: 'strict'`, SRI on CDN script, 10 MB file/diagram limits, output-dir validation

## CLI

| Command | Description |
|---------|-------------|
| `d4-diag analyze PATH [PATH …]` | Analyze files/directories, write diagrams |
| `d4-diag viewer [DIR]` | Open interactive viewer (default: `docs/diagrams`) |
| `d4-diag --version` | Print version |

Common options:

```bash
d4-diag analyze ./src --verbose
d4-diag analyze ./src --output-dir ./docs/diagrams
d4-diag analyze ./src --project-root .
d4-diag viewer ./docs/diagrams --no-browser
```

Backward-compatible (implicit `analyze`):

```bash
d4-diag ./src
d4-diag ./src ./tests --verbose
```

Poetry script aliases: `poetry run main …`, `poetry run view …` (viewer only).

## Output

Default directory: `<project_root>/docs/diagrams/`

| File | Content |
|------|---------|
| `architecture.mmd` | Files as subgraphs with classes/functions and import edges |
| `class_diagram.mmd` | UML-style classes, methods, inheritance |
| `module_deps.mmd` | Project-local import graph |

The viewer writes `_d4_diag_viewer.html` next to the `.mmd` files.

## Programmatic usage

```python
from d4_diag import CodeMapAnalyzer, find_python_files

project_root = "/path/to/project"
files = find_python_files(project_root)

analyzer = CodeMapAnalyzer(project_root)
analyzer.build_module_map(files)
for fp in files:
    analyzer.analyze_file(fp)

diagrams = analyzer.generate_all()  # dict of filename → content
analyzer.generate_all(save_files=True, output_dir="docs/diagrams")
```

See [docs/reference/api.md](docs/reference/api.md).

## Excluded paths

Discovery skips: `.venv`, `venv`, `__pycache__`, `.git`, `.pytest_cache`, `.mypy_cache`, `.ruff_cache`, `node_modules`, `dist`, `build`, `site-packages`, `*.egg-info`, and **symlinked** files/directories.

## Tests

```bash
poetry install
poetry run pytest tests -v
# or
poetry run test
```

## Documentation

| Document | Topic |
|----------|-------|
| [docs/index.md](docs/index.md) | MkDocs home |
| [docs/getting-started/quick-start.md](docs/getting-started/quick-start.md) | 5-minute guide |
| [docs/reference/cli.md](docs/reference/cli.md) | Full CLI reference |
| [docs/reference/api.md](docs/reference/api.md) | Python API |
| [docs/user-guide/viewing-diagrams.md](docs/user-guide/viewing-diagrams.md) | Viewer |
| [docs/SECURITY.md](docs/SECURITY.md) | Security notes |

Build docs locally: `poetry run mkdocs serve`

## License

MIT — see [LICENSE](LICENSE).

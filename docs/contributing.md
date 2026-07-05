# Contributing

Thank you for contributing to **d4-diag**.

## Setup

```bash
git clone https://github.com/internetics-net/d4-diag.git
cd d4-diag
poetry install
poetry run pre-commit install   # optional but recommended
```

## Workflow

```bash
git checkout -b feature/my-change

# format & lint
poetry run black src tests
poetry run flake8 src tests

# test
poetry run pytest tests -v

# dogfood
poetry run d4-diag analyze src/
poetry run d4-diag viewer docs/diagrams --no-browser
```

Submit a pull request from your fork.

## Tests

```bash
poetry run pytest                  # all tests
poetry run pytest tests/test_viewer_mermaid.py -v
poetry run pytest --cov=d4_diag    # with coverage
poetry run test                    # alternate entry point
```

Test modules:

| File | Focus |
|------|--------|
| `test_cli_basic.py`, `test_main.py` | CLI and analyze flow |
| `test_generate_mermaid.py` | Analyzer and diagrams |
| `test_viewer_mermaid.py` | HTML viewer, escaping |
| `test_utils.py` | File discovery, symlinks |
| `test_integration.py` | End-to-end |

## Documentation

```bash
poetry run mkdocs serve    # http://127.0.0.1:8000
poetry run mkdocs build --strict
```

Update `mkdocs.yml` nav when adding pages. Keep `README.md` and `docs/` in sync.

## Code style

- PEP 8, Black (line length 100)
- Flake8 via `.flake8` and pre-commit
- Type hints where helpful
- Docstrings on public APIs

See [Code Quality](contributing/code-quality.md).

## Security changes

If you touch file discovery, diagram parsing, or the HTML viewer:

- Add or extend tests in `tests/test_utils.py` / `tests/test_viewer_mermaid.py`
- Document behavior in [SECURITY.md](SECURITY.md)

## Reporting issues

Include Python version, d4-diag version (`d4-diag --version`), minimal repro steps, and expected vs actual behavior.

## Release (maintainers)

1. Bump `version` in `pyproject.toml`
2. Update changelog if maintained
3. Tag `vX.Y.Z` and push
4. Publish to PyPI when configured

## License

Contributions are licensed under the project MIT license.

# Installation

## Prerequisites

- Python **3.8.1** or higher
- `pip` (included with Python)

## Install from PyPI

```bash
pip install d4-diag
```

Verify:

```bash
d4-diag --version   # 0.1.5
d4-diag --help
```

## Upgrade

```bash
pip install --upgrade d4-diag
```

## Uninstall

```bash
pip uninstall d4-diag
```

## Isolated install (recommended)

Use [pipx](https://pypa.github.io/pipx/) so d4-diag does not mix with project dependencies:

```bash
pip install pipx
pipx install d4-diag
```

## Development install

Clone and use Poetry:

```bash
git clone https://github.com/internetics-net/d4-diag.git
cd d4-diag
poetry install
poetry run d4-diag --version
poetry run pytest tests -v
```

Poetry registers console scripts: `d4-diag`, `main`, `view`, `test`.

## Virtual environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

pip install d4-diag
```

## Troubleshooting

**`d4-diag: command not found`**

Run as a module:

```bash
python -m d4_diag --help
python -m d4_diag analyze ./src
```

Or add the scripts directory to `PATH`:

- **Windows:** `%APPDATA%\Python\PythonXX\Scripts`
- **macOS/Linux:** `~/.local/bin`

## Next steps

- [Quick Start](quick-start.md)
- [CLI Reference](../reference/cli.md)

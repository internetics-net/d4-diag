# Installation

## Prerequisites

- Python 3.8 or higher
- pip (comes with Python)

## Install

```bash
pip install d4-diag
```

## Verify

```bash
d4-diag --version
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

## Isolated Install (recommended)

Use `pipx` to install d4-diag in an isolated environment so it doesn't interfere with other packages:

```bash
pip install pipx
pipx install d4-diag
```

## Virtual Environment

If you prefer a project-level virtual environment:

```bash
# Create and activate
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# Install
pip install d4-diag
```

## Troubleshooting

**`d4-diag: command not found` after install**

Your Python scripts directory may not be on your PATH. Try running as a module instead:

```bash
python -m d4_diag --help
```

Or add the scripts directory to PATH:

- **Windows**: Add `%APPDATA%\Python\PythonXX\Scripts` to your PATH
- **macOS/Linux**: Add `~/.local/bin` to your PATH

## Next Steps

- [Quick Start Guide](quick-start.md) - Run your first analysis
- [Analyzing Code](../user-guide/analyzing-code.md) - Detailed analysis options

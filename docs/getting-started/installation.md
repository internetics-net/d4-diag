# Installation

## Prerequisites

- Python 3.8 or higher
- Poetry (recommended) or pip

## Using Poetry (Recommended)

Poetry manages dependencies and virtual environments automatically.

### Install Poetry

If you don't have Poetry installed:

```bash
# On Windows (PowerShell)
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -

# On macOS/Linux
curl -sSL https://install.python-poetry.org | python3 -
```

### Install D4-Diag

```bash
# Clone the repository
git clone https://github.com/internetics-net/d4-diag.git
cd d4-diag

# Install dependencies
poetry install

# Verify installation
poetry run main --help
```

## Using pip

If you prefer pip:

```bash
# Clone the repository
git clone https://github.com/internetics-net/d4-diag.git
cd d4-diag

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate

# Install in development mode
pip install -e .

# Verify installation
python -m d4_diag.main --help
```

## Verify Installation

Test that everything works:

```bash
# Analyze the d4-diag project itself
poetry run main .

# View the generated diagrams
poetry run viewer docs/diagrams
```

Your browser should open showing three interactive diagrams.

## Next Steps

- [Quick Start Guide](quick-start.md) - Learn basic usage
- [Analyzing Code](../user-guide/analyzing-code.md) - Detailed analysis options

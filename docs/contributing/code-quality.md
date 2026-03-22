# Code Quality

D4-Diag uses several tools to maintain code quality and consistency.

## Tools

### Black - Code Formatter

[Black](https://black.readthedocs.io/) is an opinionated Python code formatter that ensures consistent code style.

**Configuration:** `pyproject.toml`
```toml
[tool.black]
line-length = 100
target-version = ['py38', 'py39', 'py310', 'py311']
```

**Usage:**
```bash
# Format all files
poetry run black .

# Check without modifying
poetry run black --check .

# Format specific files
poetry run black src/d4_diag/main.py
```

### Flake8 - Linter

[Flake8](https://flake8.pycqa.org/) is a linting tool that checks for code style issues, potential bugs, and complexity.

**Configuration:** `.flake8`
```ini
[flake8]
max-line-length = 100
extend-ignore = E203, E266, E501, W503, F541
max-complexity = 20
```

**Usage:**
```bash
# Check all source files
poetry run flake8 src/

# Check specific files
poetry run flake8 src/d4_diag/main.py

# Check with specific rules
poetry run flake8 --select=E,W src/
```

**Common Error Codes:**
- `E`: PEP 8 errors
- `W`: PEP 8 warnings
- `F`: PyFlakes errors (undefined names, unused imports)
- `C`: McCabe complexity
- `N`: PEP 8 naming conventions

### Pre-commit - Git Hooks

[Pre-commit](https://pre-commit.com/) runs checks automatically before each commit.

**Configuration:** `.pre-commit-config.yaml`

**Setup:**
```bash
# Install hooks
poetry run pre-commit install

# Run manually on all files
poetry run pre-commit run --all-files

# Run on specific files
poetry run pre-commit run --files src/d4_diag/main.py
```

**Hooks configured:**
1. **trailing-whitespace** - Remove trailing whitespace
2. **end-of-file-fixer** - Ensure files end with newline
3. **check-yaml** - Validate YAML files
4. **check-json** - Validate JSON files
5. **check-toml** - Validate TOML files
6. **black** - Auto-format Python code
7. **flake8** - Lint Python code
8. **isort** - Sort imports

## Workflow

### Before Committing

```bash
# 1. Format code with black
poetry run black .

# 2. Check with flake8
poetry run flake8 src/

# 3. Run all pre-commit hooks
poetry run pre-commit run --all-files
```

### During Development

```bash
# Format on save (configure your IDE)
# Or run black periodically
poetry run black src/d4_diag/

# Check specific file
poetry run flake8 src/d4_diag/main.py
```

### CI/CD Integration

Add to your CI pipeline:

```yaml
# .github/workflows/quality.yml
name: Code Quality

on: [push, pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.8'

      - name: Install dependencies
        run: |
          pip install poetry
          poetry install

      - name: Run black
        run: poetry run black --check .

      - name: Run flake8
        run: poetry run flake8 src/

      - name: Run pre-commit
        run: poetry run pre-commit run --all-files
```

## IDE Integration

### VS Code

Install extensions:
- **Black Formatter** - Format on save
- **Flake8** - Real-time linting

**Settings (.vscode/settings.json):**
```json
{
  "[python]": {
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "ms-python.black-formatter"
  },
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.linting.flake8Args": ["--config=.flake8"]
}
```

### PyCharm

1. **Black:**
   - Settings → Tools → External Tools → Add Black
   - Configure as file watcher for auto-format

2. **Flake8:**
   - Settings → Tools → External Tools → Add Flake8
   - Or use built-in inspections

## Ignoring Rules

### Black

Black is opinionated and doesn't support ignoring specific lines. To exclude files:

```toml
[tool.black]
exclude = '''
/(
    \.git
  | \.venv
  | migrations
)/
'''
```

### Flake8

**Inline ignore:**
```python
# Ignore specific error on this line
result = some_long_function_call()  # noqa: E501

# Ignore multiple errors
import unused_module  # noqa: F401,E402
```

**File-level ignore:**
```python
# flake8: noqa
# At top of file to ignore all errors
```

**Config-level ignore:**
```ini
# .flake8
per-file-ignores =
    __init__.py:F401
    tests/*:E501
```

## Best Practices

1. **Run black before committing** - Ensures consistent formatting
2. **Fix flake8 issues** - Address linting errors before pushing
3. **Use pre-commit hooks** - Automate quality checks
4. **Configure IDE** - Get real-time feedback
5. **Don't ignore warnings** - Fix issues rather than suppressing them
6. **Keep complexity low** - Refactor complex functions (C901 warnings)

## Troubleshooting

### Black and Flake8 Conflicts

Some flake8 rules conflict with black's formatting. These are already ignored in `.flake8`:
- `E203` - Whitespace before ':'
- `E501` - Line too long (black handles this)
- `W503` - Line break before binary operator

### Pre-commit Fails

```bash
# Update hooks
poetry run pre-commit autoupdate

# Clear cache
poetry run pre-commit clean

# Reinstall
poetry run pre-commit uninstall
poetry run pre-commit install
```

### Flake8 Too Strict

Adjust `.flake8` configuration:
```ini
# Increase complexity threshold
max-complexity = 20

# Ignore additional rules
extend-ignore = E203, E266, E501, W503, F541
```

## Resources

- [Black Documentation](https://black.readthedocs.io/)
- [Flake8 Documentation](https://flake8.pycqa.org/)
- [Pre-commit Documentation](https://pre-commit.com/)
- [PEP 8 Style Guide](https://pep8.org/)

# Contributing

Thank you for considering contributing to D4-Diag!

## Getting Started

### Fork and Clone

```bash
# Fork on GitHub, then clone your fork
git clone https://github.com/internetics-net/d4-diag.git
cd d4-diag

# Add upstream remote
git remote add upstream https://github.com/internetics-net/d4-diag.git
```

### Development Setup

```bash
# Install dependencies
poetry install

# Run tests
poetry run pytest

# Analyze d4-diag itself
poetry run main .
poetry run viewer docs/diagrams
```

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes

Follow these guidelines:
- Write clear, descriptive commit messages
- Add tests for new features
- Update documentation
- Follow existing code style

### 3. Test Your Changes

```bash
# Run tests
poetry run pytest

# Test on real projects
poetry run main /path/to/test/project
poetry run viewer /path/to/test/project/docs/diagrams
```

### 4. Submit Pull Request

```bash
# Push to your fork
git push origin feature/your-feature-name

# Create PR on GitHub
```

## Code Style

### Python

- Follow PEP 8
- Use type hints where helpful
- Keep functions focused and small
- Add docstrings for public APIs

### Example

```python
def sanitize_id(name: str) -> str:
    """Sanitize a string for use as a Mermaid node ID.

    Args:
        name: Raw string to sanitize

    Returns:
        Sanitized ID safe for Mermaid
    """
    s = re.sub(r'[^\w]', '_', name)
    if s and s[0].isdigit():
        s = 'n' + s
    return 'id_' + s
```

## Testing

### Running Tests

```bash
# All tests
poetry run pytest

# Specific test file
poetry run pytest tests/test_analyzer.py

# With coverage
poetry run pytest --cov=d4_diag
```

### Writing Tests

Add tests in `tests/` directory:

```python
def test_sanitize_id():
    assert sanitize_id("models.py") == "id_models_py"
    assert sanitize_id("123test") == "id_n123test"
```

## Documentation

### Building Docs Locally

```bash
# Install docs dependencies
poetry install

# Serve docs locally
poetry run mkdocs serve

# Build docs
poetry run mkdocs build
```

### Writing Docs

- Use clear, concise language
- Include code examples
- Add screenshots where helpful
- Update navigation in `mkdocs.yml`

## Areas for Contribution

### High Priority

- [ ] Add support for more diagram types
- [ ] Improve import resolution for complex projects
- [ ] Add filtering options (exclude patterns, etc.)
- [ ] Performance optimization for very large projects

### Medium Priority

- [ ] Add configuration file support
- [ ] Export diagrams to PNG/SVG
- [ ] Interactive diagram editing
- [ ] Plugin system for custom analyzers

### Low Priority

- [ ] Support for other languages (JavaScript, TypeScript)
- [ ] Integration with IDEs
- [ ] Diagram diff tool
- [ ] Web-based diagram editor

## Reporting Issues

### Bug Reports

Include:
- Python version
- D4-Diag version
- Steps to reproduce
- Expected vs actual behavior
- Sample code if possible

### Feature Requests

Include:
- Use case description
- Proposed solution
- Alternative approaches considered
- Willingness to implement

## Code Review Process

1. Maintainer reviews PR
2. Feedback provided via comments
3. Author addresses feedback
4. Maintainer approves and merges

## Release Process

Maintainers handle releases:

1. Update version in `pyproject.toml`
2. Update CHANGELOG.md
3. Create GitHub release
4. Publish to PyPI (future)

## Community

- **GitHub Discussions** - Ask questions, share ideas
- **Issues** - Bug reports and feature requests
- **Pull Requests** - Code contributions

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

## Questions?

Open a GitHub Discussion or reach out to maintainers.

Thank you for contributing! 🎉

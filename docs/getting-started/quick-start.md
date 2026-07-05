# Quick Start

Get up and running with **d4-diag** in a few minutes.

## 1. Install

```bash
pip install d4-diag
d4-diag --version
```

Or from source:

```bash
git clone https://github.com/internetics-net/d4-diag.git
cd d4-diag && poetry install
```

## 2. Analyze a project

```bash
d4-diag analyze /path/to/project
d4-diag analyze /path/to/project/src
d4-diag analyze . --verbose
```

Legacy shorthand: `d4-diag ./src` (same as `analyze ./src`).

## 3. View diagrams

```bash
d4-diag viewer /path/to/project/docs/diagrams
```

Opens `_d4_diag_viewer.html` in your browser with three tabs:

- **Architecture** — files, classes, functions, imports
- **Class diagram** — UML-style classes
- **Module dependencies** — import graph

Use `--no-browser` to only generate the HTML file.

## Minimal walkthrough

```bash
mkdir my-project && cd my-project

cat > models.py << 'EOF'
class User:
    def __init__(self, name):
        self.name = name
    def greet(self):
        return f"Hello, {self.name}"
class Admin(User):
    pass
EOF

cat > main.py << 'EOF'
from models import User
def main():
    print(User("Alice").greet())
if __name__ == "__main__":
    main()
EOF

d4-diag analyze .
d4-diag viewer docs/diagrams
```

## Common patterns

```bash
d4-diag analyze src/ tests/
d4-diag analyze ./src --output-dir ./docs/diagrams
python -m d4_diag analyze .
```

## Next steps

- [Analyzing Code](../user-guide/analyzing-code.md)
- [Diagram Types](../user-guide/diagram-types.md)
- [Viewing Diagrams](../user-guide/viewing-diagrams.md)
- [CLI Reference](../reference/cli.md)

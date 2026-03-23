# Quick Start

Get up and running with d4-diag in 5 minutes.

## 1. Install

```bash
pip install d4-diag
```

## 2. Analyze a Project

Point d4-diag at any Python project directory:

```bash
# Analyze entire project
d4-diag analyze /path/to/project

# Analyze specific directory
d4-diag analyze /path/to/project/src

# Analyze current directory
d4-diag analyze .

# Analyze with verbose output
d4-diag analyze . --verbose
```

## 3. View the Diagrams

Open the interactive viewer in your browser:

```bash
d4-diag viewer /path/to/project/docs/diagrams
```

Your browser opens showing three tabs:

- **Architecture** - File structure with classes and functions
- **Class Diagram** - UML-style class relationships
- **Module Dependencies** - Import graph

## Example Walkthrough

```bash
# Create a sample project
mkdir my-project
cd my-project

cat > models.py << 'EOF'
class User:
    def __init__(self, name):
        self.name = name

    def greet(self):
        return f"Hello, {self.name}"

class Admin(User):
    def __init__(self, name, level):
        super().__init__(name)
        self.level = level
EOF

cat > main.py << 'EOF'
from models import User, Admin

def create_user(name):
    return User(name)

def main():
    user = create_user("Alice")
    print(user.greet())

if __name__ == "__main__":
    main()
EOF

# Analyze
d4-diag analyze .

# View diagrams
d4-diag viewer docs/diagrams
```

## What You'll See

### Architecture Diagram
```
┌─ main.py ─────────┐       ┌─ models.py ────────┐
│ create_user()     │──────>│ User (2 methods)   │
│ main()            │       │ Admin (0 methods)  │
└───────────────────┘       └────────────────────┘
```

### Class Diagram
```
    User
    ├─ __init__()
    └─ greet()
        ▲
        │
      Admin
      └─ __init__()
```

### Module Dependencies
```
main.py ──> models.py
```

## Common Patterns

```bash
# Analyze multiple paths
d4-diag analyze src/ tests/ scripts/

# Custom output directory
d4-diag analyze ./src --output-dir ./docs/diagrams

# Run as Python module (alternative)
python -m d4_diag analyze .
```

## Next Steps

- [Analyzing Code](../user-guide/analyzing-code.md) - Advanced analysis options
- [Diagram Types](../user-guide/diagram-types.md) - Understand each diagram
- [Viewing Diagrams](../user-guide/viewing-diagrams.md) - Viewer features

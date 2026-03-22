# Quick Start

Get up and running with D4-Diag in 5 minutes.

## Basic Usage

### 1. Analyze a Project

Point D4-Diag at any Python project or file:

```bash
# Analyze entire project
poetry run main /path/to/project

# Analyze specific directory
poetry run main /path/to/project/src

# Analyze single file
poetry run main script.py
```

### 2. View the Diagrams

D4-Diag generates diagrams in `<project>/docs/diagrams/`:

```bash
poetry run viewer /path/to/project/docs/diagrams
```

Your browser opens showing three tabs:
- **Architecture** - File structure with classes/functions
- **Class Diagram** - UML-style class relationships
- **Module Dependencies** - Import graph

## Example Walkthrough

Let's analyze a sample project:

```bash
# Create a simple Python project
mkdir my-project
cd my-project

# Create some Python files
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

# Analyze it
poetry run main .

# View diagrams
poetry run viewer docs/diagrams
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

### Analyze Multiple Paths

```bash
poetry run main src/ tests/ scripts/
```

### Analyze Current Directory

```bash
cd /path/to/project
poetry run main .
```

### Custom Output Location

Diagrams are always saved to `<project_root>/docs/diagrams/`. The project root is determined by:
1. First directory argument (if analyzing a directory)
2. Parent directory of first file (if analyzing files)
3. Current working directory (as fallback)

## Next Steps

- [Analyzing Code](../user-guide/analyzing-code.md) - Advanced analysis options
- [Diagram Types](../user-guide/diagram-types.md) - Understand each diagram
- [Viewing Diagrams](../user-guide/viewing-diagrams.md) - Viewer features

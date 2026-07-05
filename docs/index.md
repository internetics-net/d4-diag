# D4-Diag

**D4-Diag** analyzes Python codebases and generates interactive **Mermaid** diagrams for architecture, classes, and module dependencies.

**Version:** `0.1.5`

## Features

- **Architecture overview** — files as containers with classes, functions, and cross-file imports
- **Class diagram** — UML-style classes, methods, and inheritance
- **Module dependencies** — project-local import graph
- **Interactive viewer** — tabbed HTML UI with lazy rendering and hardened Mermaid config
- **Fast static analysis** — AST parsing only; no code execution

## Quick example

```bash
# PyPI install
pip install d4-diag
d4-diag analyze /path/to/your/project
d4-diag viewer /path/to/your/project/docs/diagrams

# Dev checkout
poetry install
poetry run d4-diag analyze src/
poetry run d4-diag viewer docs/diagrams
```

Legacy form (implicit `analyze`):

```bash
d4-diag ./src
```

## What you get

### Architecture diagram

Each Python file is a subgraph containing its classes and top-level functions. Arrows show imports between project files.

### Class diagram

Mermaid `classDiagram` with methods and inheritance (`User <|-- Admin`).

### Module dependencies

Minimal graph of which modules import which (external packages like `numpy` are excluded).

## Installation

See the [Installation Guide](getting-started/installation.md).

## Why D4-Diag?

- **One command** to visualize structure
- **Clear diagrams** focused on navigation and onboarding
- **Safe defaults** — symlink skipping, size limits, escaped HTML viewer, strict Mermaid security level
- **Library-friendly** — use `CodeMapAnalyzer` from Python or the CLI

## Next steps

- [Quick Start](getting-started/quick-start.md) — first analysis in 5 minutes
- [Analyzing Code](user-guide/analyzing-code.md) — CLI options and behavior
- [Diagram Types](user-guide/diagram-types.md) — when to use each diagram
- [Viewing Diagrams](user-guide/viewing-diagrams.md) — viewer features
- [Security](SECURITY.md) — hardening details
- [Examples](examples.md) — real-world patterns

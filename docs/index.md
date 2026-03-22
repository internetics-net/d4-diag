# D4-Diag

**D4-Diag** is a Python code analysis and visualization tool that generates interactive Mermaid diagrams to help you understand your codebase structure.

## Features

- 🏗️ **Architecture Overview** - Visualize your project structure with files as containers showing classes and functions
- 📊 **Class Diagrams** - See all classes with their methods and inheritance relationships
- 🔗 **Module Dependencies** - Understand import relationships between your Python modules
- 🎨 **Interactive Viewer** - Browse all diagrams in a beautiful web interface
- ⚡ **Fast Analysis** - Quickly analyze entire projects or individual files

## Quick Example

```bash
# Analyze a project
poetry run main /path/to/your/project

# View the generated diagrams
poetry run viewer /path/to/your/project/docs/diagrams
```

## What You Get

### Architecture Diagram
Shows your project's file structure with each file as a subgraph containing its classes and functions. Import relationships are shown as arrows between files.

### Class Diagram
A proper UML-style class diagram showing all classes, their methods, and inheritance relationships using Mermaid's `classDiagram` syntax.

### Module Dependencies
A clean dependency graph showing which modules import from which, helping you understand coupling and module organization.

## Installation

Get started with D4-Diag in seconds:

```bash
# Clone the repository
git clone https://github.com/internetics-net/d4-diag.git
cd d4-diag

# Install with Poetry
poetry install

# Run analysis
poetry run main .
```

See the [Installation Guide](getting-started/installation.md) for more details.

## Why D4-Diag?

Traditional code analysis tools often produce overwhelming output or require complex setup. D4-Diag focuses on:

- **Simplicity** - Single command to analyze and visualize
- **Clarity** - Clean, focused diagrams that show what matters
- **Speed** - Fast AST-based analysis
- **Interactivity** - Beautiful web viewer with lazy rendering for large projects

## Next Steps

- [Quick Start Guide](getting-started/quick-start.md) - Get up and running in 5 minutes
- [Analyzing Code](user-guide/analyzing-code.md) - Learn all analysis options
- [Diagram Types](user-guide/diagram-types.md) - Understand each diagram type
- [Examples](examples.md) - See real-world usage examples

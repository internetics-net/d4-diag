# API Reference

Use D4-Diag programmatically in your Python code.

## CodeMapAnalyzer

Main class for code analysis and diagram generation.

### Constructor

```python
from d4_diag.main import CodeMapAnalyzer

analyzer = CodeMapAnalyzer(project_root: str)
```

**Parameters:**
- `project_root` (str): Absolute path to project root directory

**Attributes:**
- `files` (Dict[str, dict]): Per-file analysis data
- `import_edges` (Set[tuple]): Import relationships between files
- `project_root` (str): Project root path

### Methods

#### build_module_map

Build mapping from module names to file paths.

```python
analyzer.build_module_map(file_paths: List[str])
```

**Parameters:**
- `file_paths` (List[str]): List of absolute file paths to analyze

**Returns:** None

**Side effects:** Populates internal `_module_map` for import resolution

#### analyze_file

Analyze a single Python file.

```python
analyzer.analyze_file(file_path: str)
```

**Parameters:**
- `file_path` (str): Absolute path to Python file

**Returns:** None

**Side effects:** Updates `files` dict with analysis results

**Raises:**
- Prints syntax error message if file has invalid Python syntax

#### generate_architecture

Generate architecture overview diagram.

```python
analyzer.generate_architecture(output_file: str)
```

**Parameters:**
- `output_file` (str): Path where diagram will be saved

**Returns:** None

**Side effects:** Writes Mermaid diagram to file

#### generate_class_diagram

Generate UML class diagram.

```python
analyzer.generate_class_diagram(output_file: str)
```

**Parameters:**
- `output_file` (str): Path where diagram will be saved

**Returns:** None

**Side effects:** Writes Mermaid diagram to file

#### generate_module_deps

Generate module dependency diagram.

```python
analyzer.generate_module_deps(output_file: str)
```

**Parameters:**
- `output_file` (str): Path where diagram will be saved

**Returns:** None

**Side effects:** Writes Mermaid diagram to file

#### generate_all

Generate all three diagram types.

```python
analyzer.generate_all(output_dir: str)
```

**Parameters:**
- `output_dir` (str): Directory where diagrams will be saved

**Returns:** None

**Side effects:**
- Creates output directory if it doesn't exist
- Writes three `.mmd` files to output directory

#### print_summary

Print analysis summary to stdout.

```python
analyzer.print_summary()
```

**Returns:** None

**Side effects:** Prints formatted summary to stdout

## Utility Functions

### sanitize_id

Sanitize a string for use as a Mermaid node ID.

```python
from d4_diag.main import sanitize_id

node_id = sanitize_id(name: str) -> str
```

**Parameters:**
- `name` (str): Raw string to sanitize

**Returns:** str - Sanitized ID safe for Mermaid

**Example:**
```python
sanitize_id("models.py")  # Returns: "id_models_py"
sanitize_id("User")       # Returns: "id_User"
```

### qlabel

Quote a label for safe Mermaid rendering.

```python
from d4_diag.main import qlabel

label = qlabel(text: str) -> str
```

**Parameters:**
- `text` (str): Text to quote

**Returns:** str - Quoted text safe for Mermaid labels

**Example:**
```python
qlabel("User (3 methods)")  # Returns: '"User (3 methods)"'
```

## Complete Example

```python
import os
from pathlib import Path
from d4_diag.main import CodeMapAnalyzer, find_python_files

# Setup
project_root = "/path/to/project"
output_dir = os.path.join(project_root, "docs", "diagrams")

# Find all Python files
file_paths = find_python_files(project_root)
print(f"Found {len(file_paths)} Python files")

# Create analyzer
analyzer = CodeMapAnalyzer(project_root)

# Build module map for import resolution
analyzer.build_module_map(file_paths)

# Analyze all files
for file_path in file_paths:
    analyzer.analyze_file(file_path)

# Print summary
analyzer.print_summary()

# Generate diagrams
analyzer.generate_all(output_dir)

print(f"Diagrams saved to {output_dir}")
```

## Data Structures

### File Info

Each entry in `analyzer.files` has this structure:

```python
{
    'classes': [
        {
            'name': str,           # Class name
            'methods': [str],      # List of method names
            'bases': [str]         # List of base class names
        }
    ],
    'functions': [str],            # List of function names
    'imports': [str]               # List of imported modules
}
```

### Import Edge

Each entry in `analyzer.import_edges` is a tuple:

```python
(source_rel: str, target_rel: str)
```

Where paths are relative to `project_root`.

## Next Steps

- [CLI Reference](cli.md) - Command-line usage
- [Examples](../examples.md) - Real-world examples

# Programmatic Usage

D4-Diag can be used as a Python library for programmatic diagram generation.

## New API (v0.2.0+)

The enhanced API returns diagrams as a dictionary by default, with optional file saving.

### Basic Usage - Return Dictionary

```python
from d4_diag.main import CodeMapAnalyzer, find_python_files

# Setup
project_root = "/path/to/project"
files = find_python_files(project_root)

# Analyze
analyzer = CodeMapAnalyzer(project_root)
analyzer.build_module_map(files)

for file_path in files:
    analyzer.analyze_file(file_path)

# Generate diagrams - returns dictionary, doesn't save files
diagrams = analyzer.generate_all()

# Access diagram content
print(diagrams['architecture.mmd'])
print(diagrams['class_diagram.mmd'])
print(diagrams['module_deps.mmd'])
```

### Save to Default Location

```python
# Save to {project_root}/docs/diagrams
diagrams = analyzer.generate_all(save_files=True)
```

### Save to Custom Location

```python
# Save to custom directory
diagrams = analyzer.generate_all(
    save_files=True,
    output_dir="/custom/output/path"
)
```

## API Reference

### `CodeMapAnalyzer`

Main class for code analysis and diagram generation.

#### Constructor

```python
analyzer = CodeMapAnalyzer(project_root: str)
```

**Parameters:**
- `project_root` (str): Absolute path to project root directory

#### Methods

##### `build_module_map(file_paths: List[str])`

Build mapping from module names to file paths for import resolution.

```python
analyzer.build_module_map(file_paths)
```

##### `analyze_file(file_path: str)`

Analyze a single Python file and extract classes, functions, and imports.

```python
analyzer.analyze_file("/path/to/file.py")
```

##### `generate_all(save_files: bool = False, output_dir: Optional[str] = None) -> Dict[str, str]`

Generate all three diagram types and return as dictionary.

```python
diagrams = analyzer.generate_all(
    save_files=False,      # Set to True to save files
    output_dir=None        # Custom output directory (optional)
)
```

**Parameters:**
- `save_files` (bool): If True, save diagrams to files (default: False)
- `output_dir` (str, optional): Directory to save files. If None and save_files=True, defaults to `{project_root}/docs/diagrams`

**Returns:**
- `Dict[str, str]`: Dictionary mapping filenames to mmd content
  - `'architecture.mmd'`: Architecture overview diagram
  - `'class_diagram.mmd'`: UML class diagram
  - `'module_deps.mmd'`: Module dependency graph

##### Individual Diagram Methods

Generate specific diagrams:

```python
# Generate individual diagrams
arch_content = analyzer.generate_architecture()
class_content = analyzer.generate_class_diagram()
deps_content = analyzer.generate_module_deps()

# Or save to file
analyzer.generate_architecture(output_file="/path/to/arch.mmd")
```

##### `print_summary()`

Print analysis summary to stdout.

```python
analyzer.print_summary()
```

### Utility Functions

#### `find_python_files(root_path: str) -> List[str]`

Recursively find all Python files in a directory.

```python
from d4_diag.main import find_python_files

files = find_python_files("/path/to/project")
```

## Use Cases

### 1. Web Service Integration

```python
from flask import Flask, jsonify
from d4_diag.main import CodeMapAnalyzer, find_python_files

app = Flask(__name__)

@app.route('/analyze', methods=['POST'])
def analyze_project():
    project_path = request.json['path']

    files = find_python_files(project_path)
    analyzer = CodeMapAnalyzer(project_path)
    analyzer.build_module_map(files)

    for fp in files:
        analyzer.analyze_file(fp)

    # Return diagrams as JSON
    diagrams = analyzer.generate_all()
    return jsonify(diagrams)
```

### 2. CI/CD Pipeline

```python
import os
from d4_diag.main import CodeMapAnalyzer, find_python_files

def generate_docs_for_ci():
    """Generate diagrams in CI pipeline"""
    project_root = os.getenv('CI_PROJECT_DIR', '.')

    files = find_python_files(project_root)
    analyzer = CodeMapAnalyzer(project_root)
    analyzer.build_module_map(files)

    for fp in files:
        analyzer.analyze_file(fp)

    # Save to docs directory for deployment
    analyzer.generate_all(
        save_files=True,
        output_dir=os.path.join(project_root, 'docs', 'diagrams')
    )

    print("Diagrams generated for documentation site")
```

### 3. Custom Processing

```python
from d4_diag.main import CodeMapAnalyzer, find_python_files

def analyze_and_report(project_path):
    """Analyze project and generate custom report"""
    files = find_python_files(project_path)
    analyzer = CodeMapAnalyzer(project_path)
    analyzer.build_module_map(files)

    for fp in files:
        analyzer.analyze_file(fp)

    # Get diagrams
    diagrams = analyzer.generate_all()

    # Custom processing
    report = {
        'file_count': len(analyzer.files),
        'class_count': sum(len(f['classes']) for f in analyzer.files.values()),
        'function_count': sum(len(f['functions']) for f in analyzer.files.values()),
        'import_count': len(analyzer.import_edges),
        'diagrams': {
            name: {
                'size': len(content),
                'lines': content.count('\n') + 1,
                'nodes': content.count('['),
                'edges': content.count('-->')
            }
            for name, content in diagrams.items()
        }
    }

    return report
```

### 4. Batch Processing

```python
from d4_diag.main import CodeMapAnalyzer, find_python_files
import os

def analyze_multiple_projects(projects):
    """Analyze multiple projects and save diagrams"""
    results = {}

    for project_name, project_path in projects.items():
        print(f"Analyzing {project_name}...")

        files = find_python_files(project_path)
        analyzer = CodeMapAnalyzer(project_path)
        analyzer.build_module_map(files)

        for fp in files:
            analyzer.analyze_file(fp)

        # Save each project's diagrams
        output_dir = f"analysis_results/{project_name}"
        diagrams = analyzer.generate_all(save_files=True, output_dir=output_dir)

        results[project_name] = {
            'files': len(files),
            'diagrams': list(diagrams.keys()),
            'output': output_dir
        }

    return results

# Usage
projects = {
    'project-a': '/path/to/project-a',
    'project-b': '/path/to/project-b',
    'project-c': '/path/to/project-c'
}

results = analyze_multiple_projects(projects)
```

## Migration from Old API

### Before (v0.1.0)

```python
# Old API - always saved files
analyzer.generate_all(output_dir)
```

### After (v0.2.0+)

```python
# New API - return dictionary by default
diagrams = analyzer.generate_all()

# Or save files (backward compatible)
diagrams = analyzer.generate_all(save_files=True, output_dir=output_dir)
```

## Error Handling

```python
from d4_diag.main import CodeMapAnalyzer, find_python_files

try:
    files = find_python_files(project_path)

    if not files:
        print("No Python files found")
        return

    analyzer = CodeMapAnalyzer(project_path)
    analyzer.build_module_map(files)

    for fp in files:
        analyzer.analyze_file(fp)  # Errors are logged, not raised

    diagrams = analyzer.generate_all()

except Exception as e:
    print(f"Error during analysis: {e}")
```

## Next Steps

- [CLI Reference](../reference/cli.md) - Command-line usage
- [API Reference](../reference/api.md) - Complete API documentation
- [Examples](../examples.md) - More usage examples

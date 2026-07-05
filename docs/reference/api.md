# API Reference

Use **d4-diag** programmatically in Python.

## Package exports

```python
from d4_diag import CodeMapAnalyzer, find_python_files, __version__
```

Lower-level utilities:

```python
from d4_diag.utils import sanitize_id, qlabel, get_base_name
from d4_diag.generate_mermaid import CodeMapAnalyzer
from d4_diag.viewer_mermaid import view_diagrams, generate_html_viewer
```

## CodeMapAnalyzer

Main class for AST analysis and diagram generation (`d4_diag.generate_mermaid`).

### Constructor

```python
analyzer = CodeMapAnalyzer(project_root: str)
```

**Parameters:**

- `project_root` — project root used for relative paths and import resolution

**Attributes (after analysis):**

- `files` — per-file analysis data
- `import_edges` — set of `(source_rel, target_rel)` tuples
- `project_root` — root path string

### Methods

#### `build_module_map(file_paths: List[str]) -> None`

Build module name → file path mapping for resolving imports.

#### `analyze_file(file_path: str) -> None`

Parse one Python file (skips files **> 10 MB**). Updates `files`. Syntax errors are printed; not raised.

#### `generate_architecture(output_file: Optional[str] = None) -> str`

Return architecture diagram content; optionally write to `output_file`.

#### `generate_class_diagram(output_file: Optional[str] = None) -> str`

Return class diagram content; optionally write to file.

#### `generate_module_deps(output_file: Optional[str] = None) -> str`

Return module dependency diagram; optionally write to file.

#### `generate_all(save_files: bool = False, output_dir: Optional[str] = None) -> Dict[str, str]`

Generate all three diagrams.

| Parameter | Default | Behavior |
|-----------|---------|----------|
| `save_files` | `False` | When `True`, write `.mmd` files |
| `output_dir` | `{project_root}/docs/diagrams` | Target directory when saving |

**Returns:** `{'architecture.mmd': str, 'class_diagram.mmd': str, 'module_deps.mmd': str}`

#### `print_summary() -> None`

Print file/class/function/import counts to stdout.

---

## Utility functions

### `find_python_files(root_path: str) -> List[str]`

Recursively collect `.py` files; excludes venvs, caches, build dirs, and **symlinks**.

```python
files = find_python_files("/path/to/project")
```

### `sanitize_id(name: str) -> str`

Sanitize a string for Mermaid node/subgraph IDs.

### `qlabel(text: str) -> str`

Quote a label for safe Mermaid rendering.

### `view_diagrams(diagrams_dir: str, open_browser: bool = True) -> None`

Load `.mmd` files, emit `_d4_diag_viewer.html`, optionally open the browser.

---

## Complete example

```python
from pathlib import Path
from d4_diag import CodeMapAnalyzer, find_python_files

project_root = "/path/to/project"
output_dir = Path(project_root) / "docs" / "diagrams"

files = find_python_files(project_root)
print(f"Found {len(files)} Python files")

analyzer = CodeMapAnalyzer(project_root)
analyzer.build_module_map(files)

for file_path in files:
    analyzer.analyze_file(file_path)

analyzer.print_summary()

diagrams = analyzer.generate_all(save_files=True, output_dir=str(output_dir))
print(f"Wrote {len(diagrams)} diagrams to {output_dir}")
```

## Data structures

### Per-file entry (`analyzer.files[rel_path]`)

```python
{
    "classes": [
        {"name": str, "methods": [str], "bases": [str]}
    ],
    "functions": [str],
    "imports": [str],
}
```

### Import edge

```python
(source_rel: str, target_rel: str)  # paths relative to project_root
```

## Related

- [Programmatic Usage](../user-guide/programmatic-usage.md) — CI, Flask, batch examples
- [CLI Reference](cli.md)
- [Examples](../examples.md)

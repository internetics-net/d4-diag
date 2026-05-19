"""Mermaid diagram generation for Python code analysis."""

import ast
import os
import re
from typing import Dict, List, Optional, Set

from .utils import get_base_name, qlabel, sanitize_id


class CodeMapAnalyzer:
    """Analyzes Python code and generates Mermaid diagrams."""

    def __init__(self, project_root: str):
        """Initialize the analyzer with a project root directory.

        Args:
            project_root: Absolute path to the project root directory.
        """
        self.project_root = os.path.abspath(project_root)
        # per-file data: { rel_path: FileInfo }
        self.files: Dict[str, dict] = {}
        # import edges: (source_rel, target_rel)
        self.import_edges: Set[tuple] = set()
        # all project module names for resolving local imports
        self._module_map: Dict[str, str] = {}

    def _rel(self, path: str) -> str:
        """Get path relative to project root."""
        return os.path.relpath(path, self.project_root).replace("\\", "/")

    def build_module_map(self, file_paths: List[str]):
        """Build mapping from dotted module names to relative file paths."""
        for fp in file_paths:
            rel = self._rel(fp)
            # models/server.py  ->  models.server
            mod = rel.replace("/", ".")
            if mod.endswith(".py"):
                mod = mod[:-3]
            if mod.endswith(".__init__"):
                mod = mod[:-9]
            self._module_map[mod] = rel

    def analyze_file(self, file_path: str):
        """Analyze a single Python file."""
        rel = self._rel(file_path)

        # Check file size to prevent memory issues
        MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
        try:
            file_size = os.path.getsize(file_path)
            if file_size > MAX_FILE_SIZE:
                print(f"  Skipping {rel}: file too large ({file_size} bytes)")
                return
        except OSError as e:
            print(f"  Error accessing {rel}: {e}")
            return

        # Read file with error handling
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                source = f.read()
        except (IOError, UnicodeDecodeError) as e:
            print(f"  Error reading {rel}: {e}")
            return

        try:
            tree = ast.parse(source)
        except SyntaxError as e:
            print(f"  Syntax error in {rel}: {e}")
            return

        info = {
            "classes": [],  # [ {name, methods, bases} ]
            "functions": [],  # [ name ]  (top-level only)
            "imports": [],  # [ module_str ]
        }

        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.ClassDef):
                cls = {
                    "name": node.name,
                    "methods": [],
                    "bases": [],
                }
                for base in node.bases:
                    cls["bases"].append(get_base_name(base))
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) or isinstance(item, ast.AsyncFunctionDef):
                        cls["methods"].append(item.name)
                info["classes"].append(cls)

            elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                info["functions"].append(node.name)

            elif isinstance(node, ast.Import):
                for alias in node.names:
                    info["imports"].append(alias.name)
                    self._resolve_import(rel, alias.name)

            elif isinstance(node, ast.ImportFrom):
                self._record_import_from(rel, info, node)

        self.files[rel] = info

    def _package_parts_for_file(self, source_rel: str) -> List[str]:
        """Dotted package components for a source file (no trailing .py)."""
        source_mod = source_rel.replace("/", ".").replace(".py", "")
        if source_mod.endswith(".__init__"):
            source_mod = source_mod[:-9]
        return source_mod.split(".") if source_mod else []

    def _record_import_from(self, source_rel: str, info: dict, node: ast.ImportFrom) -> None:
        """Record ImportFrom nodes, including relative ``from . import`` forms."""
        if node.level > 0:
            pkg_parts = self._package_parts_for_file(source_rel)
            pkg_parts = pkg_parts[: max(0, len(pkg_parts) - node.level)]
            if node.module:
                full_mod = (
                    ".".join(pkg_parts + node.module.split(".")) if pkg_parts else node.module
                )
                info["imports"].append(full_mod)
                self._resolve_import(source_rel, module_str=full_mod, level=0)
                for alias in node.names:
                    if alias.name != "*":
                        member = f"{full_mod}.{alias.name}"
                        info["imports"].append(member)
                        self._resolve_import(source_rel, module_str=member, level=0)
            else:
                for alias in node.names:
                    if alias.name == "*":
                        continue
                    full_mod = ".".join(pkg_parts + [alias.name]) if pkg_parts else alias.name
                    info["imports"].append(full_mod)
                    self._resolve_import(source_rel, module_str=full_mod, level=0)
        elif node.module:
            info["imports"].append(node.module)
            self._resolve_import(source_rel, module_str=node.module, level=0)

    def _resolve_import(self, source_rel: str, module_str: str, level: int = 0):
        """Try to resolve an import to a project-local file."""
        if not module_str:
            return

        # try full match, then progressively shorter prefixes
        parts = module_str.split(".")
        for i in range(len(parts), 0, -1):
            candidate = ".".join(parts[:i])
            if candidate in self._module_map:
                target_rel = self._module_map[candidate]
                if target_rel != source_rel:
                    self.import_edges.add((source_rel, target_rel))
                return

    def generate_architecture(self, output_file: Optional[str] = None) -> str:
        """Generate architecture diagram. Returns mmd content as string."""
        lines = ["```mermaid", "graph LR"]
        lines.append(
            "    classDef fileStyle fill:#37474F,stroke:#263238,color:#ECEFF1,font-weight:bold;"
        )
        lines.append("    classDef classNodeStyle fill:#1565C0,stroke:#0D47A1,color:white;")
        lines.append("    classDef funcStyle fill:#2E7D32,stroke:#1B5E20,color:white;")
        lines.append("")

        file_ids = {}
        for rel, info in sorted(self.files.items()):
            fid = sanitize_id(rel)
            file_ids[rel] = fid
            short = os.path.basename(rel)

            has_content = info["classes"] or info["functions"]
            if has_content:
                lines.append(f"    subgraph {fid}[{qlabel(short)}]")
                lines.append("        direction TB")
                for cls in info["classes"]:
                    cid = sanitize_id(rel + "_" + cls["name"])
                    method_count = len(cls["methods"])
                    label = "{name}  ({count} methods)".format(name=cls["name"], count=method_count)
                    lines.append(f"        {cid}[{qlabel(label)}]:::classNodeStyle")
                for fn in info["functions"]:
                    fnid = sanitize_id(rel + "_" + fn)
                    lines.append(
                        "        {id}[{label}]:::funcStyle".format(id=fnid, label=qlabel(fn))
                    )
                lines.append("    end")
            else:
                lines.append(f"    {fid}[{qlabel(short)}]:::fileStyle")
            lines.append("")

        # import edges between files
        added = set()
        for src, tgt in sorted(self.import_edges):
            if src in file_ids and tgt in file_ids:
                key = (file_ids[src], file_ids[tgt])
                if key not in added:
                    lines.append(f"    {file_ids[src]} --> {file_ids[tgt]}")
                    added.add(key)

        lines.append("```")
        content = "\n".join(lines)
        if output_file:
            self._write(output_file, lines)
            print(f"  Architecture diagram -> {output_file}")
        return content

    def generate_class_diagram(self, output_file: Optional[str] = None) -> str:
        """Generate class diagram. Returns mmd content as string."""
        lines = ["```mermaid", "classDiagram"]

        # collect all classes with file origin tracking
        all_classes: Dict[str, tuple] = {}  # qualified_name -> (cls, rel_path)
        class_name_counts: Dict[str, int] = {}  # track duplicate class names

        # First pass: count duplicates
        for rel, info in self.files.items():
            for cls in info["classes"]:
                class_name_counts[cls["name"]] = class_name_counts.get(cls["name"], 0) + 1

        # Second pass: build qualified names
        for rel, info in self.files.items():
            for cls in info["classes"]:
                if class_name_counts[cls["name"]] > 1:
                    # Use qualified name for duplicates
                    module = rel.replace("/", ".").replace(".py", "")
                    qualified = f"{module}.{cls['name']}"
                else:
                    qualified = cls["name"]
                all_classes[qualified] = (cls, rel)

        if not all_classes:
            lines.append("    class NoClassesFound")
            lines.append("```")
            content = "\n".join(lines)
            if output_file:
                self._write(output_file, lines)
                print(f"  Class diagram -> {output_file}  (no classes found)")
            return content

        for qualified_name, (cls, rel) in sorted(all_classes.items()):
            safe_name = re.sub(r"[^\w]", "_", qualified_name)
            lines.append(f"    class {safe_name}" + " {")
            for method in cls["methods"]:
                lines.append(f"        +{method}()")
            lines.append("    }")

        # inheritance — only link bases that exist in the analyzed project
        name_to_qualified: Dict[str, str] = {}
        for qname, (cls, _) in all_classes.items():
            name_to_qualified.setdefault(cls["name"], qname)
        for qualified_name, (cls, _) in all_classes.items():
            safe_name = re.sub(r"[^\w]", "_", qualified_name)
            for base in cls["bases"]:
                base_qualified = name_to_qualified.get(base)
                if base_qualified and base_qualified in all_classes:
                    safe_base = re.sub(r"[^\w]", "_", base_qualified)
                    lines.append(f"    {safe_base} <|-- {safe_name}")

        lines.append("```")
        content = "\n".join(lines)
        if output_file:
            self._write(output_file, lines)
            print(f"  Class diagram -> {output_file}")
        return content

    def generate_module_deps(self, output_file: Optional[str] = None) -> str:
        """Generate module dependencies diagram. Returns mmd content as string."""
        lines = ["```mermaid", "graph LR"]
        lines.append(
            "    classDef modStyle fill:#FF8F00,stroke:#E65100,color:white,font-weight:bold;"
        )
        lines.append("")

        # only show files that participate in at least one import edge
        mentioned = set()
        for src, tgt in self.import_edges:
            mentioned.add(src)
            mentioned.add(tgt)

        # also add all analyzed files so isolated modules appear too
        for rel in self.files:
            mentioned.add(rel)

        ids = {}
        for rel in sorted(mentioned):
            ids[rel] = sanitize_id(rel)
            short = os.path.basename(rel)
            lines.append("    {id}[{label}]:::modStyle".format(id=ids[rel], label=qlabel(short)))

        lines.append("")
        added = set()
        for src, tgt in sorted(self.import_edges):
            if src in ids and tgt in ids:
                key = (ids[src], ids[tgt])
                if key not in added:
                    lines.append(f"    {ids[src]} --> {ids[tgt]}")
                    added.add(key)

        lines.append("```")
        content = "\n".join(lines)
        if output_file:
            self._write(output_file, lines)
            print(f"  Module dependencies -> {output_file}")
        return content

    def generate_all(
        self, save_files: bool = False, output_dir: Optional[str] = None
    ) -> Dict[str, str]:
        """Generate all diagrams and return as dictionary.

        Args:
            save_files: If True, save diagrams to files (default: False)
            output_dir: Directory to save files (default: {project_root}/docs/diagrams)

        Returns:
            Dictionary mapping filenames to mmd content
        """
        print("Generating diagrams...")

        diagrams = {
            "architecture.mmd": self.generate_architecture(),
            "class_diagram.mmd": self.generate_class_diagram(),
            "module_deps.mmd": self.generate_module_deps(),
        }

        if save_files:
            if output_dir is None:
                output_dir = os.path.join(self.project_root, "docs", "diagrams")
            os.makedirs(output_dir, exist_ok=True)

            for filename, content in diagrams.items():
                filepath = os.path.join(output_dir, filename)
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"  {filename} -> {filepath}")

            print(f"All diagrams saved to {output_dir}")
        else:
            print("Diagrams generated (not saved to files)")

        return diagrams

    @staticmethod
    def _write(path: str, lines: List[str]):
        """Write lines to a file."""
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    def print_summary(self):
        """Print analysis summary."""
        total_classes = sum(len(i["classes"]) for i in self.files.values())
        total_functions = sum(len(i["functions"]) for i in self.files.values())
        print("\n=== Code Map Summary ===")
        print(f"Files analyzed:   {len(self.files)}")
        print(f"Classes found:    {total_classes}")
        print(f"Functions found:  {total_functions}")
        print(f"Import links:     {len(self.import_edges)}")

        if self.files:
            print("\nProject structure:")
            for rel in sorted(self.files):
                info = self.files[rel]
                parts = []
                if info["classes"]:
                    parts.append(f"{len(info['classes'])} classes")
                if info["functions"]:
                    parts.append(f"{len(info['functions'])} functions")
                detail = ", ".join(parts) if parts else "empty"
                print(f"  {rel}  ({detail})")

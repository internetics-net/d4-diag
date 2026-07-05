# Security

Security-relevant behavior in **d4-diag** (file discovery, diagram generation, HTML viewer). The tool is intended for **trusted local codebases** on a developer machine.

## Threat model (summary)

| Surface | Risk | Mitigation |
|---------|------|------------|
| Directory walk | Follow symlinks outside intended tree | `followlinks=False`; skip symlinked dirs and `.py` files |
| Large files | DoS via huge reads | Skip source files and diagram files **> 10 MB** |
| HTML viewer | XSS from diagram or project names | `html.escape()` on text; diagram source in `type="text/plain"` blocks with `</script>` neutralized |
| Symlink `.mmd` in viewer dir | Read arbitrary files via symlink | Skip symlink entries in `find_diagram_files`; refuse in `read_diagram_content` |
| Diagram output paths | Path traversal via `output_dir` | `safe_join_directory()` when saving `.mmd` files |
| Browser open (Windows) | Malformed `file://` URLs | `Path.as_uri()` for viewer launch |
| Mermaid rendering | Script injection via diagram syntax | `securityLevel: 'strict'`, `htmlLabels: false` |
| CDN script | Supply-chain tampering | jsDelivr URL with **SRI** (`integrity` + `crossorigin`) |
| Output directory | Writes outside project | Warn and prompt if `--output-dir` resolves outside `--project-root` |

## File discovery (`find_python_files`)

- Walks with `os.walk(..., followlinks=False)`.
- Skips excluded directory names (venv, `.git`, caches, etc.).
- Does not descend into symlinked subdirectories.
- Ignores symlinked `.py` files.
- Single-file arguments that are symlinks are skipped with a warning in the CLI.

## Analysis (`CodeMapAnalyzer`)

- Reads Python source with a **10 MB** size cap per file.
- Parses with `ast.parse` only — **does not execute** analyzed code.
- Syntax errors on individual files are logged; analysis continues.

## HTML viewer (`viewer_mermaid.py`)

Generated file: `<diagrams_dir>/_d4_diag_viewer.html` (alongside `.mmd` files, not a world-writable temp path).

Protections:

```python
# Text inserted into HTML attributes / titles
html.escape(text, quote=True)

# Diagram source embedded for lazy client-side copy into Mermaid
text.replace("</script>", r"<\/script>")
```

Mermaid initialization:

```javascript
mermaid.initialize({
  securityLevel: 'strict',
  htmlLabels: false,
  // ...
});
```

External script: Mermaid **10.9.0** from jsDelivr with Subresource Integrity hash.

## CLI output path

When `--output-dir` resolves outside the project root, the CLI prints a warning and asks for confirmation before continuing (non-interactive CI may need to keep output inside the project tree).

## Recommendations

1. **Analyze trusted code only** — diagrams reflect source structure; do not run the viewer on `.mmd` files from untrusted third parties without review.
2. **Commit `.mmd`, review HTML** — the viewer HTML is regenerated locally; treat `_d4_diag_viewer.html` as build output if you prefer not to commit it.
3. **Keep d4-diag updated** — `pip install --upgrade d4-diag` or pin a known version in CI.
4. **CI** — use `d4-diag analyze … --no-browser` / `viewer --no-browser` when automating; avoid piping untrusted paths.

## Related tests

| Module | Focus |
|--------|--------|
| `tests/test_utils.py` | Symlink-safe discovery |
| `tests/test_viewer_mermaid.py` | HTML escaping, viewer generation |
| `tests/test_generate_mermaid.py` | Size limits, diagram output |
| `tests/test_main.py` | CLI validation |

## Reporting

Open security issues at [GitHub Issues](https://github.com/internetics-net/d4-diag/issues).

## Related documentation

- [Viewing Diagrams](user-guide/viewing-diagrams.md)
- [Analyzing Code](user-guide/analyzing-code.md)
- [CLI Reference](reference/cli.md)

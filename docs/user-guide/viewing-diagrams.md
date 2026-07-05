# Viewing Diagrams

The **d4-diag** viewer renders `.mmd` diagrams in a local HTML page with tabs and lazy Mermaid rendering.

## Start the viewer

```bash
d4-diag viewer [diagrams_directory] [--no-browser]
```

Defaults to `docs/diagrams` when the directory argument is omitted.

```bash
d4-diag analyze ./src
d4-diag viewer ./docs/diagrams
d4-diag viewer ./docs/diagrams --no-browser
```

Standalone script (Poetry dev checkout):

```bash
poetry run view ./docs/diagrams
```

## Generated HTML

The viewer writes:

```
<diagrams_dir>/_d4_diag_viewer.html
```

Open that file directly in a browser if you used `--no-browser`.

## Interface

- **Tabs** — one per `.mmd` file (Architecture, Class Diagram, Module Dependencies)
- **Lazy rendering** — diagram parsed when its tab is selected (`startOnLoad: false`)
- **Scrollable canvas** — pan large graphs with scrollbars
- **Project title** — read from nearest `pyproject.toml` `name` field

## Security-related behavior

The viewer is designed for **local, trusted** diagram folders:

| Control | Detail |
|---------|--------|
| HTML escaping | Project name and tab labels escaped with `html.escape` |
| Diagram embedding | Source stored in `type="text/plain"` blocks; `</script>` sequences neutralized |
| Mermaid | `securityLevel: 'strict'`, `htmlLabels: false` |
| CDN | Mermaid 10.9.0 from jsDelivr with **SRI** integrity attribute |
| File size | Diagram files **> 10 MB** are rejected |

See [Security](../SECURITY.md) for full notes.

## Mermaid configuration

```javascript
mermaid.initialize({
  startOnLoad: false,
  securityLevel: 'strict',
  maxTextSize: 5000000,
  maxEdges: 5000,
  flowchart: { useMaxWidth: false, htmlLabels: false },
  deterministicIDs: true,
  deterministicIDSeed: 'd4-diag',
});
```

## Browser support

Tested: Chrome, Edge, Firefox, Safari.

Zoom: browser shortcuts (`Ctrl/Cmd +`, `-`, `0`).

## Tips

**Large diagrams**

- Zoom out for overview, scroll to focus areas
- Analyze subdirectories separately if needed

**Save as image**

- Right-click rendered diagram → Save image (browser-dependent)
- Or use [Mermaid CLI](https://github.com/mermaid-js/mermaid-cli) on `.mmd` files

**Share**

- Commit `.mmd` files to the repo
- Embed Mermaid blocks in GitHub Markdown READMEs
- Regenerate `_d4_diag_viewer.html` locally (optional to commit)

## Errors

If rendering fails, the tab shows a Mermaid error message. Common causes:

- Invalid Mermaid syntax in generated output (file a bug)
- Extremely large graphs (browser memory)

## Next steps

- [Diagram Types](diagram-types.md)
- [Examples](../examples.md)
- [CLI Reference](../reference/cli.md)

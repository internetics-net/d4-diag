# Viewing Diagrams

The D4-Diag viewer provides an interactive web interface for browsing generated diagrams.

## Starting the Viewer

```bash
poetry run viewer <diagrams_directory>
```

### Example

```bash
# After analyzing a project
poetry run main /path/to/project

# View the diagrams
poetry run viewer /path/to/project/docs/diagrams
```

## Viewer Interface

The viewer opens in your default browser with:

- **Tab navigation** - Switch between diagram types
- **Scrollable canvas** - Pan around large diagrams
- **Full-size rendering** - Diagrams render at actual size
- **Lazy loading** - Diagrams render only when their tab is clicked

## Features

### Tab Switching

Click any tab to view that diagram:
- Architecture
- Class Diagram
- Module Dependencies

### Scrolling

Large diagrams are scrollable:
- **Horizontal scroll** - Pan left/right
- **Vertical scroll** - Pan up/down
- **Mouse wheel** - Scroll vertically

### Zoom

Use browser zoom controls:
- `Ctrl +` / `Cmd +` - Zoom in
- `Ctrl -` / `Cmd -` - Zoom out
- `Ctrl 0` / `Cmd 0` - Reset zoom

## Diagram Rendering

### Lazy Rendering

Diagrams are rendered on-demand when you click their tab. This prevents:
- Slow initial page load
- Rendering hidden elements (which causes tiny boxes)
- Memory issues with many large diagrams

### Error Handling

If a diagram fails to render, you'll see:
```
Diagram render error: <error message>
```

Common causes:
- Invalid Mermaid syntax (report as bug)
- Diagram too large (increase browser memory)

## Technical Details

### Mermaid Version

The viewer uses **Mermaid v10.9.0** for compatibility.

### Configuration

Mermaid is configured with:
```javascript
{
  startOnLoad: false,      // Lazy rendering
  maxTextSize: 500000,     // Support large diagrams
  maxEdges: 5000,          // Support complex graphs
  useMaxWidth: false       // Full-size rendering
}
```

### Browser Compatibility

Tested on:
- Chrome/Edge (recommended)
- Firefox
- Safari

## Tips

### Large Diagrams

For projects with many files:
1. Use browser zoom to get an overview
2. Scroll to focus on specific areas
3. Consider analyzing subdirectories separately

### Saving Diagrams

To save a diagram:
1. Right-click the diagram
2. Select "Save image as..."
3. Save as PNG or SVG

Alternatively, the `.mmd` files can be:
- Opened in any Mermaid editor
- Embedded in Markdown documentation
- Converted to images with Mermaid CLI

### Sharing

Share diagrams by:
1. Committing `.mmd` files to your repo
2. Using GitHub's Mermaid rendering in README
3. Hosting the viewer HTML (it's self-contained)

## Next Steps

- [Diagram Types](diagram-types.md) - Understand what each diagram shows
- [Examples](../examples.md) - See real-world usage

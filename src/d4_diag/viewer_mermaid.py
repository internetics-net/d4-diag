import html
import re
import sys
import tempfile
import webbrowser
from pathlib import Path
from typing import Dict, List


def find_diagram_files(diagrams_dir: str) -> List[Path]:
    """Find all .mmd diagram files in the specified directory"""
    diagram_files = []
    diagrams_path = Path(diagrams_dir)

    if not diagrams_path.exists():
        raise FileNotFoundError(f"Directory '{diagrams_dir}' does not exist")

    if not diagrams_path.is_dir():
        raise NotADirectoryError(f"'{diagrams_dir}' is not a directory")

    for mmd_file in diagrams_path.glob("*.mmd"):
        diagram_files.append(mmd_file)

    return sorted(diagram_files)


def read_diagram_content(file_path: Path) -> str:
    """Read the content of a diagram file"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return content
    except (IOError, OSError, UnicodeDecodeError) as e:
        raise FileNotFoundError(f"Error reading {file_path}: {e}") from e


def extract_mermaid_code(content: str) -> str:
    """Extract Mermaid code from markdown code blocks"""
    content = content.strip()

    # Pattern to match ```mermaid ... ``` with optional indentation
    pattern = r"^\s*```mermaid\n(.*?)\n\s*```"
    match = re.search(pattern, content, re.MULTILINE | re.DOTALL)

    if match:
        return match.group(1).strip()
    else:
        # No mermaid code found
        return ""


def _escape_html(text: str) -> str:
    return html.escape(text, quote=True)


def read_project_name(start_dir: Path) -> str:
    """Resolve a display name from pyproject.toml or directory name."""
    current = start_dir.resolve()
    while True:
        pyproject = current / "pyproject.toml"
        if pyproject.is_file():
            try:
                raw = pyproject.read_text(encoding="utf-8")
            except OSError:
                return current.name
            match = re.search(
                r'^\s*name\s*=\s*"([^"]+)"',
                raw,
                re.MULTILINE,
            )
            if match:
                return match.group(1)
            return current.name
        if current.parent == current:
            break
        current = current.parent
    return start_dir.name


def generate_html_viewer(
    diagrams: Dict[str, str], output_path: str, project_name: str = "Project"
) -> str:
    """Generate an HTML file with all diagrams"""
    html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{project_name} Viewer</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10.9.0/dist/mermaid.min.js"></script>
    <script>
        mermaid.initialize({
            startOnLoad: false,
            theme: 'default',
            securityLevel: 'strict',
            maxTextSize: 5000000,
            maxEdges: 5000,
            flowchart: {
                useMaxWidth: false,
                htmlLabels: true,
                curve: 'basis'
            },
            // Performance optimizations
            deterministicIDs: true,
            deterministicIDSeed: 'd4-diag',
            cloneCssStyles: false,
            suppressErrorRendering: false,
            logLevel: 1  // Only show errors
        });
    </script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
        }

        h1 {
            color: white;
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }

        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            flex-wrap: wrap;
            justify-content: center;
        }

        .tab {
            padding: 12px 24px;
            background: rgba(255, 255, 255, 0.2);
            border: 2px solid rgba(255, 255, 255, 0.3);
            border-radius: 8px;
            color: white;
            cursor: pointer;
            font-size: 16px;
            font-weight: 600;
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
        }

        .tab:hover {
            background: rgba(255, 255, 255, 0.3);
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }

        .tab.active {
            background: white;
            color: #667eea;
            border-color: white;
        }

        .diagram-container {
            display: none;
            background: white;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            margin-bottom: 20px;
        }

        .diagram-container.active {
            display: block;
            animation: fadeIn 0.3s ease;
        }

        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .diagram-title {
            color: #333;
            margin-bottom: 20px;
            font-size: 1.8em;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }

        .diagram {
            overflow: auto;
            min-height: 400px;
            max-height: 80vh;
            padding: 10px;
        }

        .diagram svg {
            max-width: none !important;
            height: auto !important;
        }

        .no-diagrams {
            text-align: center;
            color: white;
            font-size: 1.5em;
            padding: 60px 20px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 12px;
            backdrop-filter: blur(10px);
        }

        .footer {
            text-align: center;
            color: white;
            margin-top: 40px;
            padding: 20px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            backdrop-filter: blur(10px);
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 {project_name} Viewer</h1>

        {tabs_html}

        {diagrams_html}

        {no_diagrams_html}

        <div class="footer">
            <p>Generated by d4-diag | Mermaid Diagram Viewer</p>
        </div>
    </div>

    <script>
        const rendered = {};

        async function renderMermaid(container) {
            const mermaidDiv = container.querySelector('.mermaid');
            if (!mermaidDiv || rendered[container.id]) return;

            try {
                const code = mermaidDiv.textContent.trim();
                console.log(`Rendering diagram ${container.id}, code length:`, code.length);

                // Show loading indicator
                mermaidDiv.innerHTML = '<div style="text-align:center;padding:20px;color:#666;">🔄 Rendering diagram...</div>';

                // Check if diagram is too large
                if (code.length > 50000) {
                    mermaidDiv.innerHTML = '<p style="color:orange;">⚠️ Diagram too large to render (' + code.length + ' characters). Maximum recommended size is 50,000 characters.</p><details><summary>Click to view raw diagram code</summary><pre style="font-size:12px;max-height:300px;overflow:auto;">' + code + '</pre></details>';
                    rendered[container.id] = true;
                    return;
                }

                // Add timeout for large diagrams
                const timeoutPromise = new Promise((_, reject) =>
                    setTimeout(() => reject(new Error('Rendering timeout - diagram too complex')), 10000)
                );

                const renderPromise = mermaid.render('svg-' + container.id, code);
                const { svg } = await Promise.race([renderPromise, timeoutPromise]);

                mermaidDiv.innerHTML = svg;
                rendered[container.id] = true;
                console.log(`Successfully rendered diagram ${container.id}`);
            } catch (e) {
                console.error(`Error rendering diagram ${container.id}:`, e);
                const isTimeout = e.message.includes('timeout');
                const errorMsg = isTimeout ?
                    '⏰ Diagram rendering timed out (too complex). Try simplifying the diagram or breaking it into smaller parts.' :
                    '❌ Diagram render error: ' + e.message;

                mermaidDiv.innerHTML = '<p style="color:red;">' + errorMsg + '</p><details><summary>Click to view raw diagram code</summary><pre style="font-size:12px;max-height:300px;overflow:auto;">' + mermaidDiv.textContent + '</pre></details>';
            }
        }

        function showDiagram(diagramId, btn) {
            document.querySelectorAll('.diagram-container').forEach(c => {
                c.classList.remove('active');
            });
            document.querySelectorAll('.tab').forEach(t => {
                t.classList.remove('active');
            });
            const container = document.getElementById(diagramId);
            if (!container) return;
            container.classList.add('active');
            if (btn) btn.classList.add('active');
            renderMermaid(container);
        }

        window.addEventListener('load', function() {
            document.querySelectorAll('.tab').forEach(btn => {
                btn.addEventListener('click', function() {
                    showDiagram(btn.dataset.diagramId, btn);
                });
            });
            const firstTab = document.querySelector('.tab');
            if (firstTab) firstTab.click();
        });
    </script>
</body>
</html>"""

    if not diagrams:
        tabs_html = ""
        diagrams_html = ""
        no_diagrams_html = (
            '<div class="no-diagrams">No diagrams found in the specified directory.</div>'
        )
    else:
        tabs = []
        diagram_sections = []

        for i, (name, content) in enumerate(diagrams.items()):
            diagram_id = f"diagram-{i}"

            # Create tab
            safe_name = _escape_html(name)
            tabs.append(
                f'<button type="button" class="tab" data-diagram-id="{diagram_id}">'
                f"{safe_name}</button>"
            )

            mermaid_code = _escape_html(extract_mermaid_code(content))
            diagram_sections.append(
                f"""
        <div id="{diagram_id}" class="diagram-container">
            <h2 class="diagram-title">{safe_name}</h2>
            <div class="diagram">
                <div class="mermaid">{mermaid_code}</div>
            </div>
        </div>"""
            )

        tabs_html = f'<div class="tabs">\n            {chr(10).join(tabs)}\n        </div>'
        diagrams_html = "\n".join(diagram_sections)
        no_diagrams_html = ""

    html_content = html_template.replace("{tabs_html}", tabs_html)
    html_content = html_content.replace("{diagrams_html}", diagrams_html)
    html_content = html_content.replace("{no_diagrams_html}", no_diagrams_html)
    html_content = html_content.replace("{project_name}", _escape_html(project_name))

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    return output_path


def view_diagrams(diagrams_dir: str, open_browser: bool = True):
    """View all diagrams in the specified directory"""
    print(f"Scanning for diagrams in: {diagrams_dir}")

    diagram_files = find_diagram_files(diagrams_dir)

    if not diagram_files:
        raise ValueError("No diagram files found")

    print(f"\nFound {len(diagram_files)} diagram file(s):")
    for file in diagram_files:
        print(f"  - {file.name}")

    # Read all diagrams
    diagrams = {}
    for file_path in diagram_files:
        content = read_diagram_content(file_path)
        if content:
            diagrams[file_path.stem] = content

    diagrams_path = Path(diagrams_dir)
    project_name = read_project_name(diagrams_path)

    # Generate HTML viewer
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".html", delete=False, encoding="utf-8"
    ) as tmp:
        html_path = tmp.name

    try:
        html_file = generate_html_viewer(diagrams, html_path, project_name)
    except Exception as e:
        raise IOError(f"Failed to generate HTML viewer: {e}") from e

    print("\nGenerated viewer: " + html_file)

    if open_browser:
        print("Opening browser...")
        webbrowser.open(f"file://{html_file}")
    else:
        print("\nTo view diagrams, open this file in your browser:")
        print("  " + html_file)


def main():
    if len(sys.argv) < 2:
        print("Usage: python viewer.py <diagrams_directory>")
        print("\nExamples:")
        print("  python viewer.py ./diagrams")
        print("  python viewer.py /path/to/diagrams")
        print("\nThis will open an interactive HTML viewer in your browser")
        print("showing all .mmd diagram files from the specified directory.")
        return

    diagrams_dir = sys.argv[1]

    # Check if user wants to skip browser opening
    open_browser = "--no-browser" not in sys.argv

    view_diagrams(diagrams_dir, open_browser)


if __name__ == "__main__":
    main()

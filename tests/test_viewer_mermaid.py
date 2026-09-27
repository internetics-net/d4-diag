"""Test viewer functionality."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from d4_diag.viewer_mermaid import (
    extract_mermaid_code,
    find_diagram_files,
    generate_html_viewer,
    read_diagram_content,
    view_diagrams,
)


class TestViewerFunctions:
    """Test viewer module functions."""

    def test_find_diagram_files(self, temp_project_dir):
        """Test finding diagram files."""
        # Create some test files
        (temp_project_dir / "test1.mmd").write_text("graph LR\nA-->B")
        (temp_project_dir / "test2.mmd").write_text("classDiagram\nA-->B")
        (temp_project_dir / "other.txt").write_text("not a diagram")

        result = find_diagram_files(str(temp_project_dir))

        assert len(result) == 2
        assert any("test1.mmd" in str(f) for f in result)
        assert any("test2.mmd" in str(f) for f in result)
        assert not any("other.txt" in str(f) for f in result)

    def test_find_diagram_files_nonexistent(self):
        """Test finding diagram files in nonexistent directory."""
        with pytest.raises(FileNotFoundError):
            find_diagram_files("/nonexistent")

    def test_read_diagram_content(self, temp_project_dir):
        """Test reading diagram content."""
        diagram_file = temp_project_dir / "sample.mmd"
        diagram_file.write_text("```mermaid\ngraph LR\nA-->B\n```", encoding="utf-8")
        content = read_diagram_content(diagram_file)
        assert "graph LR" in content
        assert "A-->B" in content

    def test_read_diagram_content_nonexistent(self):
        """Test reading nonexistent diagram file."""
        with pytest.raises(FileNotFoundError):
            read_diagram_content(Path("/nonexistent/file.mmd"))

    def test_read_diagram_content_too_large(self, temp_project_dir):
        """Test rejecting oversized diagram files."""
        huge = temp_project_dir / "huge.mmd"
        huge.write_bytes(b"x" * (10 * 1024 * 1024 + 1))
        with pytest.raises(FileNotFoundError, match="too large"):
            read_diagram_content(huge)

    def test_extract_mermaid_code(self):
        """Test extracting Mermaid code from content."""
        content = """
Some text before
```mermaid
graph LR
    A --> B
    B --> C
```
Some text after
"""
        result = extract_mermaid_code(content)
        assert result == "graph LR\n    A --> B\n    B --> C"

    def test_extract_mermaid_code_no_mermaid(self):
        """Test extracting Mermaid code when none exists."""
        content = "Just regular text without any mermaid diagrams"
        result = extract_mermaid_code(content)
        assert result == ""

    def test_extract_mermaid_code_multiple_blocks(self):
        """Test extracting first Mermaid code block when multiple exist."""
        content = """
First block:
```mermaid
graph LR
    A --> B
```
Second block:
```mermaid
classDiagram
    ClassA --> ClassB
```
"""
        result = extract_mermaid_code(content)
        assert result == "graph LR\n    A --> B"

    def test_generate_html_viewer(self):
        """Test generating HTML viewer."""
        mermaid_code = "```mermaid\ngraph LR\nA-->B\n```"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
            html_path = f.name

        try:
            diagrams = {"test": mermaid_code}
            generate_html_viewer(diagrams, html_path)

            with open(html_path, "r", encoding="utf-8") as f:
                html_content = f.read()

            assert "<!DOCTYPE html>" in html_content
            assert "mermaid" in html_content.lower()
            assert "graph LR" in html_content
            assert "securityLevel: 'strict'" in html_content
            assert 'class="mermaid-source"' in html_content
            assert 'integrity="sha384-' in html_content
            assert 'crossorigin="anonymous"' in html_content
            assert "htmlLabels: false" in html_content
            assert "mermaidDiv.innerHTML = '<p" not in html_content
            assert "mermaidDiv.innerHTML = '<div" not in html_content
        finally:
            Path(html_path).unlink(missing_ok=True)

    def test_generate_html_viewer_escapes_unsafe_names(self):
        """Diagram titles must not inject HTML or script."""
        mermaid_code = "```mermaid\ngraph LR\nA-->B\n```"
        unsafe = '<script>alert("x")</script>'

        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
            html_path = f.name

        try:
            generate_html_viewer({unsafe: mermaid_code}, html_path, project_name=unsafe)
            html_content = Path(html_path).read_text(encoding="utf-8")
            assert "<script>alert" not in html_content
            assert "data-diagram-id=" in html_content
            assert 'onclick="showDiagram' not in html_content
        finally:
            Path(html_path).unlink(missing_ok=True)

    def test_view_diagrams_success(self, temp_project_dir):
        """Test view_diagrams function success."""
        # Create test diagram files
        (temp_project_dir / "test1.mmd").write_text("graph LR\nA-->B")
        (temp_project_dir / "test2.mmd").write_text("classDiagram\nA-->B")

        with patch("d4_diag.viewer_mermaid.generate_html_viewer") as mock_generate:
            with patch("webbrowser.open") as mock_browser:
                view_diagrams(str(temp_project_dir), open_browser=True)

                # Should have generated HTML once for all diagrams
                assert mock_generate.call_count == 1
                # Should have opened browser
                mock_browser.assert_called_once()

    def test_view_diagrams_no_browser(self, temp_project_dir):
        """Test view_diagrams function without opening browser."""
        (temp_project_dir / "test.mmd").write_text("graph LR\nA-->B")

        with patch("d4_diag.viewer_mermaid.generate_html_viewer") as mock_generate:
            with patch("webbrowser.open") as mock_browser:
                view_diagrams(str(temp_project_dir), open_browser=False)

                # Should have generated HTML but not opened browser
                mock_generate.assert_called_once()
                mock_browser.assert_not_called()

    def test_view_diagrams_no_diagrams(self, temp_project_dir):
        """Test view_diagrams function with no diagram files."""
        with pytest.raises(ValueError, match="No.*diagram files found"):
            view_diagrams(str(temp_project_dir))

    def test_view_diagrams_nonexistent_directory(self):
        """Test view_diagrams function with nonexistent directory."""
        with pytest.raises(FileNotFoundError):
            view_diagrams("/nonexistent/directory")

    def test_view_diagrams_generation_error(self, temp_project_dir):
        """Test view_diagrams function with HTML generation error."""
        (temp_project_dir / "test.mmd").write_text("graph LR\nA-->B")

        with patch("d4_diag.viewer_mermaid.generate_html_viewer", side_effect=IOError("Generation failed")):
            with pytest.raises(IOError, match="Failed to generate HTML viewer"):
                view_diagrams(str(temp_project_dir))

    def test_extract_mermaid_code_with_indented_fence(self):
        """Test extracting Mermaid code with indented code fence."""
        content = """
    ```mermaid
    graph LR
        A --> B
    ```
"""
        result = extract_mermaid_code(content)
        assert result == "graph LR\n        A --> B"

    def test_extract_mermaid_code_with_language_specifier(self):
        """Test extracting Mermaid code with different language specifiers."""
        content = """
```mermaid
flowchart TD
    A --> B
```
"""
        result = extract_mermaid_code(content)
        assert result == "flowchart TD\n    A --> B"

    def test_extract_mermaid_code_same_line_opening(self):
        """Test extracting Mermaid code when opening fence has no newline."""
        content = "```mermaid\ngraph LR\n    A --> B\n```"
        result = extract_mermaid_code(content)
        assert result == "graph LR\n    A --> B"

    def test_generate_html_viewer_escapes_script_closing_tag(self):
        """Diagram source must not break out of the script container."""
        malicious = "```mermaid\ngraph LR\nA-->B\n</script><img onerror=alert(1)>\n```"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
            html_path = f.name

        try:
            generate_html_viewer({"evil": malicious}, html_path)
            html_content = Path(html_path).read_text(encoding="utf-8")
            assert "</script><img" not in html_content
            assert r"<\/script>" in html_content
        finally:
            Path(html_path).unlink(missing_ok=True)

    def test_view_diagrams_writes_viewer_beside_diagrams(self, temp_project_dir):
        """Viewer HTML is written next to diagrams, not in system temp."""
        (temp_project_dir / "test.mmd").write_text("graph LR\nA-->B")

        with patch("webbrowser.open") as mock_browser:
            view_diagrams(str(temp_project_dir), open_browser=True)

        viewer_path = temp_project_dir / "_d4_diag_viewer.html"
        assert viewer_path.is_file()
        mock_browser.assert_called_once()
        uri_arg = mock_browser.call_args[0][0]
        assert uri_arg.startswith("file:")

    def test_find_diagram_files_skips_symlinks(self, temp_project_dir):
        """Symlinked .mmd files must not be loaded into the viewer."""
        real = temp_project_dir / "real.mmd"
        real.write_text("graph LR\nA-->B", encoding="utf-8")
        link = temp_project_dir / "linked.mmd"
        link.symlink_to(real)

        try:
            found = find_diagram_files(str(temp_project_dir))
            assert len(found) == 1
            assert found[0].name == "real.mmd"
        finally:
            link.unlink(missing_ok=True)

    def test_read_diagram_content_rejects_symlink(self, temp_project_dir):
        target = temp_project_dir / "target.mmd"
        target.write_text("graph LR\nA-->B", encoding="utf-8")
        link = temp_project_dir / "link.mmd"
        link.symlink_to(target)

        try:
            with pytest.raises(FileNotFoundError, match="symlink"):
                read_diagram_content(link)
        finally:
            link.unlink(missing_ok=True)

    def test_view_diagrams_opens_file_uri(self, temp_project_dir):
        (temp_project_dir / "test.mmd").write_text("graph LR\nA-->B")

        with patch("webbrowser.open") as mock_browser:
            view_diagrams(str(temp_project_dir), open_browser=True)

        uri = mock_browser.call_args[0][0]
        assert (
            Path(uri.replace("file:///", "").replace("file://", "")).name.endswith("_d4_diag_viewer.html")
            or "_d4_diag_viewer.html" in uri
        )

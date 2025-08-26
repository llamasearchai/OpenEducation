import json

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import DirectoryTree, Markdown, Static


class SyllabusViewer(Static):
    """A widget to view syllabi."""

    def compose(self) -> ComposeResult:
        """Render the widget."""
        with Horizontal():
            yield DirectoryTree("data/syllabi", id="syllabus_tree")
            with Vertical():
                yield Markdown(id="syllabus_content_viewer")

    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        """Called when a file is selected in the directory tree."""
        try:
            with open(event.path, 'r', encoding='utf-8') as f:
                # Assuming the syllabus files are JSON, pretty-print them in a Markdown block
                content = json.load(f)
                md_content = f"```json\n{json.dumps(content, indent=2)}\n```"
                self.query_one("#syllabus_content_viewer", Markdown).update(md_content)
        except Exception as e:
            self.query_one("#syllabus_content_viewer", Markdown).update(f"Error loading file: {e}")

import os
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Tabs, Tab, ContentSwitcher
from textual.containers import Container
from .widgets.dashboard import Dashboard
from .widgets.syllabus_viewer import SyllabusViewer
from .widgets.performance_viewer import PerformanceViewer

class OpenEducationTUI(App):
    """A Textual user interface for the OpenEducation platform."""

    CSS_PATH = "styles.css"
    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("q", "quit", "Quit"),
    ]

    def fetch_summary_data(self) -> dict:
        """Fetch summary data from the filesystem."""
        syllabi_path = "data/syllabi"
        coaching_path = "data/coaching"
        progress_path = "data/progress"
        
        syllabi_count = len([f for f in os.listdir(syllabi_path) if f.endswith('.json')]) if os.path.exists(syllabi_path) else 0
        coaching_cycles_count = len([f for f in os.listdir(coaching_path) if f.startswith('cycle_')]) if os.path.exists(coaching_path) else 0
        performance_reports_count = len([f for f in os.listdir(progress_path) if f.endswith('_progress.json')]) if os.path.exists(progress_path) else 0

        return {
            "syllabi_count": syllabi_count,
            "coaching_cycles_count": coaching_cycles_count,
            "performance_reports_count": performance_reports_count,
        }

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        summary_data = self.fetch_summary_data()

        yield Header()
        yield Footer()
        with Container():
            yield Tabs(
                Tab("Dashboard", id="dashboard"),
                Tab("Syllabus", id="syllabus"),
                Tab("Performance", id="performance"),
                Tab("Settings", id="settings"),
            )
            with ContentSwitcher(initial="dashboard"):
                yield Dashboard(summary_data=summary_data, id="dashboard_content")
                yield SyllabusViewer(id="syllabus_content")
                yield PerformanceViewer(id="performance_content")
                yield Container(id="settings_content")

    def on_tabs_tab_activated(self, event: Tabs.TabActivated) -> None:
        """Handle tab activation."""
        self.query_one(ContentSwitcher).current = f"{event.tab.id}_content"

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark

if __name__ == "__main__":
    app = OpenEducationTUI()
    app.run()

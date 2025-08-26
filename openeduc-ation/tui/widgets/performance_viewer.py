from textual.widgets import Static


class PerformanceViewer(Static):
    """A widget to display a performance report."""

    def compose(self):
        """Render the widget."""
        yield Static("Performance Report", id="performance_title")
        yield Static("\n--- Overview ---")
        yield Static("Student ID: student_001")
        yield Static("Syllabus ID: syllabus_science_9-12")
        yield Static("Overall Completion: 75.0%")

        yield Static("\n--- Weak Topics ---")
        yield Static("- Quantum Physics (Score: 0.55)")
        
        yield Static("\n--- Strong Topics ---")
        yield Static("- Classical Mechanics (Score: 0.95)")

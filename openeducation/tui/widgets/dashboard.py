from textual.widgets import Static

class Dashboard(Static):
    """A dashboard widget to display summary information."""

    def __init__(self, summary_data: dict, **kwargs):
        super().__init__(**kwargs)
        self.summary_data = summary_data

    def compose(self):
        """Render the widget."""
        yield Static("Welcome to OpenEducation!", id="welcome_title")
        yield Static("Your adaptive learning companion.", id="welcome_subtitle")
        yield Static("\n--- Summary ---")
        yield Static(f"Syllabi Generated: {self.summary_data.get('syllabi_count', 0)}")
        yield Static(f"Coaching Cycles: {self.summary_data.get('coaching_cycles_count', 0)}")
        yield Static(f"Performance Reports: {self.summary_data.get('performance_reports_count', 0)}")

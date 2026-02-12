
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Input
from textual.containers import VerticalScroll
from caspoon.core.runner import ReconRunner


class ReportView(Static):
    def update_report(self, report):
        from rich.pretty import Pretty
        self.update(Pretty(report.pretty(), expand_all=True))


class CaspoonApp(App):
    CSS_PATH = None
    TITLE = "Caspoon Reverse Engineering Toolkit"
    SUB_TITLE = "Executable Recon Viewer"

    def compose(self) -> ComposeResult:
        yield Header()
        yield Input(placeholder="Enter path to binary and press Enter...", id="path_input")
        yield VerticalScroll(ReportView(id="report_view"), id="scroll")
        yield Footer()

    def on_input_submitted(self, message: Input.Submitted) -> None:
        path = message.value.strip()
        if not path:
            return

        runner = ReconRunner()
        report = runner.run(path)

        report_view = self.query_one("#report_view", ReportView)
        report_view.update_report(report)

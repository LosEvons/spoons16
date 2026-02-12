# caspoon/ui/app.py

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, TabbedContent, TabPane
from textual.containers import ScrollableContainer
from caspoon.core.runner import ReconRunner

from .views.overview import OverviewView
from .views.protections import ProtectionsView
from .views.strings_view import StringsView
from .views.imports_exports import ImportsExportsView
from .views.r2_view import R2View

class CaspoonApp(App):
    TITLE = "Caspoon Reverse Engineering Toolkit"
    SUB_TITLE = "Executable Recon Viewer"

    def compose(self) -> ComposeResult:
        yield Header()

        yield Input(
            placeholder="Enter path to binary and press Enter...",
            id="path_input"
        )

        with TabbedContent():
            with TabPane("Overview"):
                with ScrollableContainer():
                    yield OverviewView(id="overview")
            with TabPane("Protections"):
                with ScrollableContainer():
                    yield ProtectionsView(id="protections")
            with TabPane("Strings"):
                with ScrollableContainer():
                    yield StringsView(id="strings_view")
            with TabPane("Imports / Exports"):
                with ScrollableContainer():
                    yield ImportsExportsView(id="imp_exp")
            with TabPane("R2 Analysis"):
                with ScrollableContainer():
                    yield R2View(id="r2_view")

        yield Footer()

    def on_input_submitted(self, message: Input.Submitted) -> None:
        path = message.value.strip()
        if not path:
            return

        runner = ReconRunner()
        report = runner.run(path)
        self.display_report(report)
        self.set_status(f"Loaded: {path}")

    def display_report(self, report):
        self.query_one("#overview", OverviewView).update_data(report)
        self.query_one("#protections", ProtectionsView).update_data(report)
        self.query_one("#strings_view", StringsView).update_data(report)
        self.query_one("#imp_exp", ImportsExportsView).update_data(report)
        self.query_one("#r2_view", R2View).update_data(report)
        
    def set_status(self, text: str):
        footer = self.query_one(Footer)
        footer.renderable = text  # Update the Footer's content by setting its renderable attribute
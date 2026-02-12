# caspoon/ui/app.py

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, TabbedContent, TabPane
from caspoon.core.runner import ReconRunner

from .views.overview import OverviewView
from .views.protections import ProtectionsView
from .views.strings_view import StringsView
from .views.imports_exports import ImportsExportsView
from .views.r2_view import R2View
from .widgets.file_picker import FilePicker


class CaspoonApp(App):
    TITLE = "Caspoon Reverse Engineering Toolkit"
    SUB_TITLE = "Executable Recon Viewer"
    BINDINGS = [
        ("o", "open_file_picker", "Open File"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()

        yield Input(
            placeholder="Enter path to binary and press Enter...",
            id="path_input"
        )

        with TabbedContent():
            with TabPane("Overview"):
                yield OverviewView(id="overview")
            with TabPane("Protections"):
                yield ProtectionsView(id="protections")
            with TabPane("Strings"):
                yield StringsView(id="strings_view")
            with TabPane("Imports / Exports"):
                yield ImportsExportsView(id="imp_exp")
            with TabPane("R2 Analysis"):
                yield R2View(id="r2_view")

        yield Footer()
        
    def action_open_file_picker(self):
        def on_select(path):
            runner = ReconRunner()
            report = runner.run(path)
            self.display_report(report)
        picker = FilePicker(start_path=".", on_select=on_select)
        self.mount(picker)

    def on_input_submitted(self, message: Input.Submitted) -> None:
        path = message.value.strip()
        if not path:
            return

        runner = ReconRunner()
        report = runner.run(path)
        self.display_report(report)

        message.input.blur()
        self.query_one(TabbedContent).focus()

    def display_report(self, report):
        self.query_one("#overview", OverviewView).update_data(report)
        self.query_one("#protections", ProtectionsView).update_data(report)
        self.query_one("#strings_view", StringsView).update_data(report)
        self.query_one("#imp_exp", ImportsExportsView).update_data(report)
        self.query_one("#r2_view", R2View).update_data(report)
        
    def on_mouse_down(self, event):
        if not isinstance(event.sender, Input):
            self.set_focus(None)
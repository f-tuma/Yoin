from dashboard import DashboardScreen

from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Label
from textual.containers import VerticalGroup


class WelcomeScreen(Screen):
    BINDINGS = [
        ("enter", "start_yoin", "Starts the application..."),
    ]

    def compose(self) -> ComposeResult:
        yield VerticalGroup(
            Label("Welcome to Yoin!", id="h1"),
            Label("Press ENTER to start...", id="p"),
            classes="info-screen",
        )

    def action_start_yoin(self) -> None:
        self.app.push_screen(DashboardScreen())


class Yoin(App):
    CSS_PATH = "style.tcss"

    def on_mount(self) -> None:
        self.push_screen(WelcomeScreen())

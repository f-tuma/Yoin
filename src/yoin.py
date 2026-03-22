from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Label
from textual.containers import Vertical


class WelcomeScreen(Screen):
    BINDINGS = [
        ("enter", "start_yoin", "Starts the application..."),
    ]

    def compose(self) -> ComposeResult:
        yield Vertical(
            Label("Welcome to Yoin!", id="h1"),
            Label("Press ENTER to start...", id="p"),
            classes="info-screen",
        )

    def action_start_yoin(self) -> None:
        self.app.push_screen(DashboardScreen())


class DashboardScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Label("DASHBOARD", id="h1")


class Yoin(App):
    CSS_PATH = "style.tcss"

    def on_mount(self) -> None:
        self.push_screen(WelcomeScreen())

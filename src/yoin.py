from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Label
from textual.containers import Horizontal, Vertical, VerticalGroup, VerticalScroll


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


class AudioVisualizer(Vertical):
    pass


class ChannelContainer(VerticalScroll):
    pass


class DashboardScreen(Screen):
    def compose(self) -> ComposeResult:
        yield VerticalGroup(
            Horizontal(
                AudioVisualizer(),
                Vertical(),
            ),
            ChannelContainer(),
        )


class Yoin(App):
    CSS_PATH = "style.tcss"

    def on_mount(self) -> None:
        self.push_screen(WelcomeScreen())

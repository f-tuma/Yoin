from dashboard import DashboardScreen
from textual.app import App


class Yoin(App):
    CSS_PATH = "style.tcss"

    def on_mount(self) -> None:
        self.push_screen(DashboardScreen())

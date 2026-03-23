from sound.sound_generator import (
    BrownNoiseLayer,
    SoundLayer,
    ToneLayer,
    WhiteNoiseLayer,
)
from values import DEF_FREQUENCY, DEF_VOLUME, sound_layers, samplerate

from textual import on
from textual.app import App, ComposeResult
from textual.screen import ModalScreen, Screen
from textual.widgets import Button, Label, Select
from textual_slider import Slider
from textual.containers import HorizontalGroup, Vertical, VerticalGroup, VerticalScroll


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


class ChannelSelector(ModalScreen):
    def compose(self) -> ComposeResult:
        options = [
            ("Tone", "tone"),
            ("Brown Noise", "brown"),
            ("White Noise", "white"),
        ]

        with Vertical(id="channel-selector"):
            yield Select(
                options, prompt="Choose sound channel to add...", id="sound-select"
            )
            yield Button("Cancel", variant="error", id="cancel")

    @on(Select.Changed)
    def select_sound(self, event: Select.Changed):
        if event.value:
            self.dismiss(event.value)

    @on(Button.Pressed, "#cancel")
    def cancel(self):
        self.dismiss(None)


class ChannelContainer(HorizontalGroup):
    def __init__(
        self,
        *children,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        markup: bool = True,
        c_name: str,
        sound_layer: SoundLayer,
    ) -> None:
        super().__init__(
            *children,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
            markup=markup,
        )
        self.c_name = c_name
        self.sound_layer = sound_layer
        sound_layers.add(self.sound_layer)

    def compose(self) -> ComposeResult:
        yield Label(f"{self.c_name}")
        yield Slider(
            min=0, max=100, step=1, value=int(DEF_VOLUME * 100), id="volume-slider"
        )

    @on(Slider.Changed, "#volume-slider")
    def on_slider_changed_volume(self, event: Slider.Changed) -> None:
        self.volume = event.value / 100
        self.sound_layer.volume = self.volume


class DashboardScreen(Screen):
    BINDINGS = [
        ("a", "add_channel", "Add channel"),
        # ("s", "save_preset", "Save current layout as preset"),
    ]

    def compose(self) -> ComposeResult:
        yield VerticalScroll(id="channels")

    def create_channel(self, choice: str):
        s_layer: SoundLayer | None
        c_name = ""
        match choice:
            case "tone":
                c_name = "Tone"
                s_layer = ToneLayer(
                    samplerate=samplerate, volume=DEF_VOLUME, frequency=DEF_FREQUENCY
                )
            case "brown":
                c_name = "Brown Noise"
                s_layer = BrownNoiseLayer(samplerate=samplerate, volume=DEF_VOLUME)
            case "white":
                c_name = "White Noise"
                s_layer = WhiteNoiseLayer(samplerate=samplerate, volume=DEF_VOLUME)
            case _:
                s_layer = None

        if s_layer:
            new_channel = ChannelContainer(c_name=c_name, sound_layer=s_layer)
            self.query_one("#channels").mount(new_channel)

    def action_add_channel(self):
        def check_choice(choice: str | None):
            if choice:
                self.create_channel(choice)

        self.app.push_screen(ChannelSelector(), check_choice)


class Yoin(App):
    CSS_PATH = "style.tcss"

    def on_mount(self) -> None:
        self.push_screen(WelcomeScreen())

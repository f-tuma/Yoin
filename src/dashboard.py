from sound.sound_generator import (
    BrownNoiseLayer,
    SoundLayer,
    ToneLayer,
    WhiteNoiseLayer,
)
from values import DEF_FREQUENCY, DEF_VOLUME, sound_layers, samplerate

from textual import on
from textual.app import ComposeResult
from textual.screen import ModalScreen, Screen
from textual.widgets import Button, Label, OptionList
from textual.widgets.option_list import Option
from textual_slider import Slider
from textual.containers import HorizontalGroup, VerticalScroll


class DashboardScreen(Screen):
    BINDINGS = [
        ("a", "add_channel", "Add channel"),
        # ("s", "save_preset", "Save current layout as preset"),
    ]

    def compose(self) -> ComposeResult:
        yield VerticalScroll(id="channels", classes="screen")

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
            new_channel = ChannelContainer(
                c_name=c_name, sound_layer=s_layer, classes="sound-channel"
            )
            self.query_one("#channels").mount(new_channel)

    def action_add_channel(self):
        def check_choice(choice: str | None):
            if choice:
                self.create_channel(choice)

        self.app.push_screen(ChannelSelector(), check_choice)


class ChannelSelector(ModalScreen):
    BINDINGS = [
        ("escape", "cancel", "Cancel selection"),
    ]

    def compose(self) -> ComposeResult:

        yield OptionList(
            Option("Tone", id="tone"),
            Option("Brown Noise", id="brown"),
            Option("White Noise", id="white"),
            id="sound-select",
        )

    @on(OptionList.OptionSelected)
    def select_sound(self, event: OptionList.OptionSelected):
        if event.option_id:
            self.dismiss(event.option_id)

    def action_cancel(self):
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
        with HorizontalGroup(classes="channel-row"):
            yield Label(f"{self.c_name}", id="channel-name")
            yield Slider(
                min=0,
                max=100,
                value=int(DEF_VOLUME * 100),
                id="volume-slider",
            )
            yield Button("Mute", variant="default", flat=True, id="mute_btn")
            yield Button(
                "Remove",
                variant="error",
                flat=True,
                id="remove-channel",
                classes="channel-item",
            )

    @on(Button.Pressed, "#mute_btn")
    def on_mute_pressed(self):
        self.sound_layer.muted = False if self.sound_layer.muted else True

    @on(Button.Pressed, "#remove-channel")
    def on_remove_pressed(self):
        sound_layers.discard(self.sound_layer)
        self.remove()

    @on(Slider.Changed, "#volume-slider")
    def on_slider_changed_volume(self, event: Slider.Changed) -> None:
        self.volume = event.value / 100
        self.sound_layer.volume = self.volume

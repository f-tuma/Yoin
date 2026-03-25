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
from textual.widgets import Button, Input, Label, OptionList
from textual.widgets.option_list import Option
from textual_slider import Slider
from textual.containers import HorizontalGroup, Vertical, VerticalScroll


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


class ChannelContainer(Vertical):
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
        with HorizontalGroup(classes="channel-row primary-controls"):
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

        if self.sound_layer.settings:
            with HorizontalGroup(classes="channel-row secondary-controls"):
                for setting in self.sound_layer.settings:
                    yield setting

    @on(Button.Pressed, "#mute_btn")
    def on_mute_pressed(self, event: Button.Pressed):
        self.sound_layer.muted = not self.sound_layer.muted

        if self.sound_layer.muted:
            event.button.label = "Unmute"
            event.button.variant = "warning"
            self.add_class("muted-channel")
        else:
            event.button.label = "Mute"
            event.button.variant = "default"
            self.remove_class("muted-channel")

    @on(Button.Pressed, "#remove-channel")
    def on_remove_pressed(self):
        sound_layers.discard(self.sound_layer)
        self.remove()

    @on(Slider.Changed, "#volume-slider")
    def on_slider_changed_volume(self, event: Slider.Changed) -> None:
        self.volume = event.value / 100
        self.sound_layer.volume = self.volume

    @on(Input.Changed, "#frq_s")
    def on_frq_changed(self, event: Input.Changed) -> None:
        if isinstance(self.sound_layer, ToneLayer) and event.value:
            try:
                self.sound_layer.frequency = int(event.value)
            except ValueError:
                pass

    @on(Input.Changed, "#lfo_s")
    def on_lfo_changed(self, event: Input.Changed) -> None:
        if isinstance(self.sound_layer, SoundLayer) and event.value:
            try:
                self.sound_layer.lfo = float(int(event.value) / 100)
            except ValueError:
                pass

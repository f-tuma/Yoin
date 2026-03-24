import numpy as np
import sounddevice as sd
from textual.containers import HorizontalGroup
from textual.widgets import Input, Label

from values import sound_layers


class SoundLayer:
    def __init__(self, samplerate, volume) -> None:
        self.samplerate = samplerate
        self.volume = volume
        self.start_idx = 0
        self.muted = False
        self.settings = []


class ToneLayer(SoundLayer):
    def __init__(self, samplerate, volume, frequency=123, lfo=0.0) -> None:
        super().__init__(samplerate, volume)
        self.frequency = frequency
        self.lfo = lfo
        frequency_setting = HorizontalGroup(
            Label("FRQ:"),
            Input(type="integer", value=f"{self.frequency}"),
            classes="setting-group",
        )
        lfo_setting = HorizontalGroup(
            Label("LFO:"),
            Input(type="integer", value=f"{int(self.lfo * 100)}"),
            classes="setting-group",
        )
        self.settings = [frequency_setting, lfo_setting]

    def get_next_chunk(self, frames: int) -> np.ndarray:
        timeline = np.arange(self.start_idx, self.start_idx + frames) / self.samplerate
        wave = np.sin(2 * np.pi * self.frequency * timeline)
        lfo_wave = (np.sin(2 * np.pi * self.lfo * timeline) + 1.0) / 2.0
        wave = wave * lfo_wave * self.volume
        self.start_idx += frames
        return wave


class WhiteNoiseLayer(SoundLayer):
    def __init__(self, samplerate, volume) -> None:
        super().__init__(samplerate, volume)

    def get_next_chunk(self, frames: int):
        wave = np.random.uniform(-self.volume, self.volume, frames)
        return wave


class BrownNoiseLayer(SoundLayer):
    def __init__(self, samplerate, volume) -> None:
        super().__init__(samplerate, volume)
        self.last_val = 0.0

    def get_next_chunk(self, frames: int):
        wave = np.zeros(frames)
        white_noise = np.random.uniform(-1.0, 1.0, frames)
        for i in range(frames):
            self.last_val = white_noise[i] + (self.last_val * 0.99)
            wave[i] = self.last_val
        wave = (wave / 10.0) * self.volume
        return wave


def mixer_callback(outdata, frames: int, time, status):
    wave = np.zeros(frames)
    for layer in sound_layers:
        if not layer.muted:
            wave = wave + layer.get_next_chunk(frames)
    outdata[:] = wave.reshape(-1, 1)


stream = sd.OutputStream(samplerate=44100, channels=2, callback=mixer_callback)

stream.start()

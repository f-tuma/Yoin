import numpy as np
import sounddevice as sd


class SoundLayer:
    def __init__(self, samplerate, volume) -> None:
        self.samplerate = samplerate
        self.volume = volume
        self.start_idx = 0


class ToneLayer(SoundLayer):
    def __init__(self, samplerate, volume, frequency) -> None:
        super().__init__(samplerate, volume)
        self.frequency = frequency

    def get_next_chunk(self, frames: int) -> np.ndarray:
        timeline = np.arange(self.start_idx, self.start_idx + frames) / self.samplerate
        wave = np.sin(2 * np.pi * self.frequency * timeline) * self.volume
        self.start_idx += frames
        return wave


class BreathingLayer(SoundLayer):
    def __init__(self, samplerate, volume, frequency, lfo) -> None:
        super().__init__(samplerate, volume)
        self.frequency = frequency
        self.lfo = lfo

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


my_tone = BreathingLayer(samplerate=44100, volume=0.01, frequency=152.0, lfo=0.1)

my_noise = BrownNoiseLayer(samplerate=44100, volume=0.01)


def mixer_callback(outdata, frames: int, time, status):
    wave = my_tone.get_next_chunk(frames) + my_noise.get_next_chunk(frames)
    outdata[:] = wave.reshape(-1, 1)


with sd.OutputStream(samplerate=44100, channels=1, callback=mixer_callback):
    print("Hraje nekonečný tón... Zastavíš stisknutím Enter.")
    input()

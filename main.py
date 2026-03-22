import sounddevice as sd
import numpy as np

sample_rate = 44100
volume = 0.05

def audio_callback(outdata, frames, time, status):
    if status:
        print(status)
    noise = np.random.uniform(-1, 1, size=(frames, 2))
    outdata[:] = (noise * volume).astype('float32')

def main():
    stream = sd.OutputStream(channels=2, callback=audio_callback, samplerate=sample_rate)
    with stream:
        print("Streaming noise... Press Enter to stop.")
        input()

if __name__ == "__main__":
    main()

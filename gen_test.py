import numpy as np
import soundfile as sf

sr = 44100
duration = 3.0
t = np.linspace(0, duration, int(sr * duration), False)
audio = np.sin(2 * np.pi * 440 * t) * 0.5
sf.write("test_audio.wav", audio, sr)
print("Saved test_audio.wav")

import numpy as np
from scipy.io.wavfile import write

sample_rate = 44100
t = np.linspace(0, 0.5, int(sample_rate * 0.5), False) # 0.5 seconds

# Beep for distracted
note = np.sin(2 * np.pi * 880 * t)
audio = np.int16(note * 32767)
write('distracted.wav', sample_rate, audio)

# Different beep for yawn
note = np.sin(2 * np.pi * 440 * t)
audio = np.int16(note * 32767)
write('yawn.wav', sample_rate, audio)

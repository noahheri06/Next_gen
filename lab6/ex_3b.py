import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fftshift, fftfreq
from scipy.signal import find_peaks

fc = 12e6
Fs = 50e6
pulses = 40
PRI = 1e-3
T_pulse = 10e-6

# method 1, a sine is windowed.
t = np.arange(0, pulses * PRI, 1 / Fs)
signal1 = np.exp(2j * np.pi * fc * t)
for index in range(len(signal1)):
    if index % (PRI * Fs) >= T_pulse * Fs:
        signal1[index] = 0

# method 2, a sine pulse concatenated (difference in phases per pulse)
pulse = signal1[: int(PRI * Fs)].tolist()
signal2 = []
for i in range(pulses):
    signal2.append(pulse)
signal2 = np.array(signal2).flatten()

# do FFT and add zero padding to a power of 2
N_fft = 2 ** (3 + int(np.ceil(np.log2(len(t)))))
bin_hz = Fs / N_fft
signal1_fft = np.abs(fftshift(fft(signal1, n=N_fft)))
signal2_fft = np.abs(fftshift(fft(signal2, n=N_fft)))

# normalize and convert to dB for better peak detection
signal1_db = 20 * np.log10(signal1_fft / np.max(signal1_fft))
signal2_db = 20 * np.log10(signal2_fft / np.max(signal2_fft))

freq_axis = fftshift(fftfreq(N_fft, d=1 / Fs))

# plot results
plt.subplot(2, 1, 1)
plt.plot(freq_axis, signal1_fft)
plt.axvline(x=12e6, color='red')
plt.grid()
plt.xlim(11.88e6, 12.12e6)

plt.subplot(2, 1, 2)
plt.plot(freq_axis, signal2_fft)
plt.axvline(x=12e6, color='red')
plt.grid()
plt.xlim(11.88e6, 12.12e6)

plt.tight_layout()
plt.show()

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt
import scipy.io
import os

def lowpass_filter(signal, fs, cutoff=1e6): 
    nyq = fs / 2
    normal_cutoff = cutoff / nyq
    b, a = butter(N=4, Wn=normal_cutoff, btype='low')
    signal_filtered = filtfilt(b, a, signal)
    return signal_filtered

PlutoSamprate = 40e6

B = 25e6
T = 100e-6
f0 = 2.5e9
fs = PlutoSamprate
c = 3e8
N = int(round(T * fs))
t = np.arange(N) / fs

#chirp generation
k = B / T
sig_A = np.exp(1j * 2 * np.pi * 0.5 * k * t**2) 

capture_range = 100

FILE_NAME = "saved_25MHz"
stored_results = mat = scipy.io.loadmat(f'pluto_data/{FILE_NAME}.mat')['received_data']
added_result = np.sum(stored_results, axis=0) / capture_range


plt.figure()
plt.plot(np.real(added_result))
plt.title("Real part of the averaged received signal")
plt.xlabel("Sample index")
plt.ylabel("Amplitude")
plt.grid()
plt.xlim(0, 800)
plt.show()


beat_signal = np.conj(added_result) * sig_A
beat_signal = lowpass_filter(beat_signal, fs, cutoff=400e3)
beat_fft = np.fft.fftshift(np.fft.fft(beat_signal))
freq_axis = np.fft.fftshift(np.fft.fftfreq(len(beat_signal), d=1/fs)) / 1e3
range_axis = (freq_axis * c) / (2 * k) * 1e3
plt.figure()
plt.subplot(2, 1, 1)
plt.plot(freq_axis, np.abs(beat_fft))
plt.title("FFT of the beat signal")
plt.xlabel("Frequency (kHz)")
plt.ylabel("Magnitude")
plt.xlim(0, 0.06*B/1e3)
plt.grid()
plt.subplot(2, 1, 2)
plt.plot(range_axis, np.abs(beat_fft))
plt.title("Range profile")
plt.xlabel("Range (m)")
plt.ylabel("Magnitude")
plt.xlim(0, 800)
plt.grid()
plt.tight_layout()
#plt.savefig(os.path.join(save_path, f"range_profile_{B/1e6:.1f}MHz.png"))
plt.show()
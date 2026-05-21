import numpy as np
import adi
import time
import os
import scipy.io
from setupPlutoSDR_TDD import initialize_Pluto_TDD
from TDD_Transreceiver import pluto_transmit_receive
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt

def lowpass_filter(signal, fs, cutoff=1e6): 
    nyq = fs / 2
    normal_cutoff = cutoff / nyq
    b, a = butter(N=4, Wn=normal_cutoff, btype='low')
    signal_filtered = filtfilt(b, a, signal)
    return signal_filtered

#plputo constants
Pluto_IP = '192.168.2.1'
PlutoSamprate = 40e6
Tx_CenterFrequency = 2.5e9
Rx_CenterFrequency = 2.5e9
tx_gain = -10
rx_gain = 10

# Radar waveform parameters
B = 5e6
T = 100e-6
f0 = 2.5e9
fs = PlutoSamprate
c = 3e8

# Time vector
N = int(round(T * fs))
t = np.arange(N) / fs
rx_time_ms = 1000.0 * N / PlutoSamprate
my_sdr, tddn = initialize_Pluto_TDD(Pluto_IP, PlutoSamprate, f0, rx_gain, tx_gain, rx_time_ms)

#chirp generation
k = B / T
sig_A = np.exp(1j * 2 * np.pi * 0.5 * k * t**2) 
save_path = "pluto_data"

tx_waveform = ((2**14) * sig_A).astype(np.complex64)
frame_length_samples = tx_waveform.shape[0]
capture_range = 100

results = np.array(pluto_transmit_receive(my_sdr, tddn, tx_waveform, capture_range, frame_length_samples, save_path))
my_sdr.close()

added_result = np.sum(results, axis=0) / capture_range
plt.figure()
plt.plot(np.real(added_result))
plt.title("Real part of the averaged received signal")
plt.xlabel("Sample index")
plt.ylabel("Amplitude")
plt.grid()
plt.show()

beat_signal = added_result * np.conj(sig_A)
beat_signal = lowpass_filter(beat_signal, fs, cutoff=1e6)
beat_fft = np.fft.fftshift(np.fft.fft(beat_signal))
freq_axis = np.fft.fftshift(np.fft.fftfreq(len(beat_signal), d=1/fs))
range_axis = (freq_axis * c) / (2 * k)
plt.figure()
plt.plot(freq_axis, np.abs(beat_fft))
plt.title("FFT of the beat signal")
plt.xlabel("Frequency (Hz)")
plt.ylabel("Magnitude")
# plt.xlim(-1, 1)
plt.grid()
plt.show()
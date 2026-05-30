import numpy as np
import adi
import time
import os
import scipy.io
from setupPlutoSDR_TDD import initialize_Pluto_TDD
from TDD_Transreceiver import pluto_transmit_receive
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt
from numpy.fft import fftshift, fftfreq, fft

def lowpass_filter(signal, fs, cutoff=1e6): 
    nyq = fs / 2
    normal_cutoff = cutoff / nyq
    b, a = butter(N=4, Wn=normal_cutoff, btype='low')
    signal_filtered = filtfilt(b, a, signal)
    return signal_filtered

#pluto constants
Pluto_IP = '192.168.2.1'
PlutoSamprate = 50e6
Tx_CenterFrequency = 2.4e9
Rx_CenterFrequency = 2.4e9
tx_gain = 0
rx_gain = 10

# Radar waveform parameters
B = 5e6
T = 100e-6
f0 = 2.4e9
fs = PlutoSamprate
c = 3e8

# Time vector
N = int(round(T * fs))
t = np.arange(N) / fs
rx_time_ms = 1000.0 * N / PlutoSamprate
my_sdr, tddn = initialize_Pluto_TDD(Pluto_IP, PlutoSamprate, f0, rx_gain, tx_gain, rx_time_ms, rx_samples=N)

#chirp generation
k = B / T
sig_A = np.exp(1j * 2 * np.pi * 0.5 * k * t**2) 
save_path = "pluto_data"

tx_waveform = ((2**14) * sig_A).astype(np.complex64)
frame_length_samples = tx_waveform.shape[0]
capture_range = 1_000_000

plt.plot(fftshift(np.fft.fftfreq(len(tx_waveform), d=1/fs)), np.abs(fftshift(np.fft.fft(tx_waveform))))
plt.show()

results = np.array(pluto_transmit_receive(my_sdr, tddn, tx_waveform, capture_range, frame_length_samples, save_path))
my_sdr.close()

# stored_results = mat = scipy.io.loadmat('pluto_data/received_data.mat')['received_data']
# added_result = np.sum(stored_results, axis=0) / capture_range

added_result = np.sum(results, axis=0) / capture_range
plt.figure()
plt.plot(np.real(added_result))
plt.title("Real part of the averaged received signal")
plt.xlabel("Sample index")
plt.ylabel("Amplitude")
plt.grid()
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
plt.savefig(os.path.join(save_path, f"range_profile_{B/1e6:.1f}MHz.png"))
plt.show()


##adding zero padding to improve range resolution

beat_signal = np.conj(added_result) * sig_A
beat_signal = lowpass_filter(beat_signal, fs, cutoff=400e3)
zero_pad_factor = 5
nfft = len(beat_signal) * zero_pad_factor
beat_fft = np.fft.fftshift(np.fft.fft(beat_signal, n=nfft))
freq_axis = np.fft.fftshift(np.fft.fftfreq(nfft, d=1/fs))/1e3
range_axis = (freq_axis * c) / (2 * k) * 1e3
plt.figure()
plt.subplot(2, 1, 1)
plt.plot(freq_axis, np.abs(beat_fft))
plt.title("FFT of the zero-padded beat signal")
plt.xlabel("Frequency (kHz)")
plt.ylabel("Magnitude")
plt.xlim(0, 0.06*B/1e3)
plt.grid()
plt.subplot(2, 1, 2)
plt.plot(range_axis, np.abs(beat_fft))
plt.title("Range profile (zero padded)")
plt.xlabel("Range (m)")
plt.ylabel("Magnitude")
plt.xlim(0, 800)
plt.grid()
plt.tight_layout()
plt.savefig(os.path.join(save_path, f"range_profile_padded_{B/1e6:.1f}MHz.png"))
plt.show()
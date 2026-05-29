import numpy as np
import matplotlib.pyplot as plt
from scipy.io import loadmat
from scipy.fft import fft, fftshift, fftfreq
from scipy.signal import butter, filtfilt
import os
os.makedirs("plots", exist_ok=True)
def lowpass_filter(signal, fs, cutoff=1e6): 
    nyq = fs / 2
    normal_cutoff = cutoff / nyq
    b, a = butter(N=4, Wn=normal_cutoff, btype='low')
    signal_filtered = filtfilt(b, a, signal)
    return signal_filtered

#====================
# task A
#====================
B, R, T, c = 5e6, 200, 1e-3, 3e8

fb = 2*B*R/(T*c)
print("The beat frequency is: ", round(fb, 1), "Hz")

#====================
# task B
#====================
fs = 200e6
data1 = loadmat("data_ex3/Data_file_1.mat")
data2 = loadmat("data_ex3/Data_file_2.mat")
data3 = loadmat("data_ex3/Data_file_3.mat")
data4 = loadmat("data_ex3/Data_file_4.mat")
data5 = loadmat("data_ex3/Data_file_5.mat")
data6 = loadmat("data_ex3/Data_file_6.mat")
data7 = loadmat("data_ex3/freq_axis.mat")
data8 = loadmat("data_ex3/time_axis.mat")
data9 = loadmat("data_ex3/freq_axis_beat.mat")

print(data1.keys())
print(data2.keys())
print(data3.keys())
print(data4.keys())
print(data5.keys())
print(data6.keys())
print(data7.keys())
print(data8.keys())
print(data9.keys())

signalA = data1['sig_A'].flatten()
signalA_fft = data2['sig_A_fft'].flatten()
signalB = data3['sig_B'].flatten()
signalB_fft = data4['sig_B_fft'].flatten()
signalC = data5['sig_C'].flatten()
signalC_fft = data6['sig_C_fft'].flatten()
freq_axis_beat = data9['freqaxis_beat'].flatten()
freq = data7['freqaxis'].flatten()
time = data8['t'].flatten()

print("Signal A shape: ", np.real(signalA).shape)
print("Signal B shape: ", np.real(signalB).shape)
print("Signal C shape: ", np.real(signalC).shape)
print("FFT of Signal A shape: ", signalA_fft.shape)
print("FFT of Signal B shape: ", signalB_fft.shape)
print("FFT of Signal C shape: ", signalC_fft.shape)

# Plotting
fig, axes = plt.subplots(3, 2, figsize=(12, 10))
axes[0, 0].plot(time/1e-3, np.real(signalA))
axes[0, 0].set_title("Signal A")
axes[0, 0].set_xlabel("Time (ms)")
axes[0, 0].set_ylabel("Amplitude")
axes[0, 0].set_xlim(0, 0.05)
axes[0, 1].plot(freq/1e6, np.abs(signalA_fft))
axes[0, 1].set_title("FFT of Signal A")
axes[0, 1].set_xlabel("Frequency (MHz)")
axes[0, 1].set_ylabel("Magnitude")
axes[1, 0].plot(time/1e-3, np.real(signalB))
axes[1, 0].set_title("Signal B")
axes[1, 0].set_xlabel("Time (ms)")
axes[1, 0].set_ylabel("Amplitude")
axes[1, 0].set_xlim(0, 0.05)
axes[1, 1].plot(freq/1e6, np.abs(signalB_fft))
axes[1, 1].set_title("FFT of Signal B")
axes[1, 1].set_xlabel("Frequency (MHz)")
axes[1, 1].set_ylabel("Magnitude")
axes[2, 0].plot(time/1e-3, np.real(signalC))
axes[2, 0].set_title("Signal C")
axes[2, 0].set_xlabel("Time (ms)")
axes[2, 0].set_ylabel("Amplitude")
axes[2, 1].plot(freq_axis_beat/1e3, signalC_fft)
axes[2, 1].set_title("FFT of Signal C")
axes[2, 1].set_xlabel("Frequency (kHz)")
axes[2, 1].set_ylabel("Magnitude")
axes[2, 1].set_xlim(0, 25)
plt.tight_layout()
plt.savefig("plots/3b.pdf")
plt.show()


#====================
# task C
#====================

#radar parameters
B, T, f0, fs, c = 20e6, 0.8e-3, 50e6, 200e6, 3e8

#target parameters
R_targets = np.array([100])

#time vectors
t = np.arange(0, T, 1/fs)
N = len(t)

#signal generator - chirpgeneration base band
k = B / T
sig_A = np.exp(1j * 2 * np.pi * 0.5 * k * t**2)
plt.figure(figsize=(10, 6))
plt.subplot(2, 1, 1)
plt.plot(t/1e-3, np.real(sig_A))
plt.title("Generated Chirp Signal")
plt.xlabel("Time (ms)")
plt.ylabel("Amplitude")

plt.subplot(2, 1, 2)
freqax = np.linspace(-fs/2, fs/2, N )
plt.plot(freqax/1e6, np.abs(fftshift(fft(sig_A))))
plt.xlim(0, fs/2/1e6)
plt.title("FFT of Generated Chirp Signal")
plt.xlabel("Frequency (MHz)")
plt.ylabel("Magnitude")
plt.tight_layout()
plt.show()

#generate FMCW signal
lo = np.exp(1j * 2 * np.pi * f0 * t)
sig_B = sig_A * lo
plt.figure(figsize=(10, 6))
plt.subplot(2, 1, 1)
plt.plot(t/1e-3, np.real(sig_B))
plt.title("FMCW Signal")
plt.xlabel("Time (ms)")
plt.ylabel("Amplitude")
plt.subplot(2, 1, 2)
plt.plot(freqax/1e6, np.abs(fftshift(fft(sig_B))))
plt.xlim(0, fs/2/1e6)
plt.title("FFT of FMCW Signal")
plt.xlabel("Frequency (MHz)")
plt.ylabel("Magnitude")
plt.tight_layout()
plt.show()

#generated received signal
s_rx = 0
for range in R_targets:
    tau = 2 * range / c
    s_rx += np.exp(1j * 2 * np.pi * (f0 * (t - tau) + 0.5 * k * (t - tau)**2))

#mix signbals for beat frequency
s_beat = s_rx * np.conj(sig_B)
s_beat = lowpass_filter(s_beat, fs)
plt.figure(figsize=(10, 10))
plt.subplot(3, 1, 1)
plt.plot(t/1e-3, np.real(s_beat))
plt.title("Beat Signal")
plt.xlabel("Time (ms)")
plt.ylabel("Amplitude")
plt.grid()


#FFT analysis for range estimation
N_fft = 2**(3+int(np.ceil(np.log2(N))))
sig_C_fft = np.abs(fftshift(fft(np.real(s_beat), n=N_fft)))
freq_axis = fftshift(fftfreq(N_fft, d=1/fs))
range_axis = (freq_axis * c) / (2 * k)
plt.subplot(3, 1, 2)
plt.plot(freq_axis/1e3, sig_C_fft)
plt.xlim(-fs/2/1e3, fs/2/1e3)
plt.title("FFT of Beat Signal")
plt.xlabel("Frequency (kHz)")
plt.ylabel("Magnitude")
plt.xlim(0, 50)
plt.grid()
plt.subplot(3, 1, 3)
plt.plot(range_axis, sig_C_fft)
plt.xlim(0, 500)
plt.title("Range Profile")
plt.xlabel("Range (m)")
plt.ylabel("Magnitude")
plt.grid()
plt.tight_layout()
plt.savefig("plots/3c_1.pdf")
plt.show()

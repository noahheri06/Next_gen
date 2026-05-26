import numpy as np
import adi
import time
import os
import scipy.io

# =====================================================================
# Pluto Parameters
# =====================================================================
PLUTO_IP          = 'ip:192.168.2.1'
PLUTO_SAMPRATE    = int(40e6)
TX_CENTER_FREQ    = int(2.5e9)
RX_CENTER_FREQ    = int(2.5e9)
TX_GAIN           = -10
RX_GAIN           = 0

# =====================================================================
# Radar Waveform Parameters
# =====================================================================
B   = 5e6
T   = 100e-6
f0  = 2.5e9
fs  = PLUTO_SAMPRATE
c   = 3e8

# =====================================================================
# Time vector & chirp generation
# =====================================================================
samples_per_chirp    = int(40e6)
t = np.linspace(0, T, samples_per_chirp, endpoint=False)
N   = len(t)
k   = B / T

sig_A       = np.exp(1j * 2 * np.pi * (0.5 * k * t**2))
tx_waveform = (2**14) * sig_A

   # 4000 samples — one chirp only
capture_range        = 100
save_path            = os.path.dirname(os.path.abspath(__file__))
os.makedirs(save_path, exist_ok=True)

# =====================================================================
# Initialise PlutoSDR — buffer size MUST be set before tx()
# =====================================================================
print("Initialising PlutoSDR...")
sdr = adi.Pluto(PLUTO_IP)

sdr.sample_rate              = PLUTO_SAMPRATE
sdr.rx_rf_bandwidth          = int(10e6)
sdr.tx_rf_bandwidth          = int(10e6)
sdr.tx_lo                    = TX_CENTER_FREQ
sdr.rx_lo                    = RX_CENTER_FREQ
sdr.tx_hardwaregain_chan0    = TX_GAIN
sdr.gain_control_mode_chan0  = "manual"
sdr.rx_hardwaregain_chan0    = RX_GAIN
sdr.rx_buffer_size           = samples_per_chirp   # 4000 instead of 40000000
sdr.tx_cyclic_buffer         = True

sdr.tx(tx_waveform.astype(np.complex64))
print(f"TX waveform loaded — buffer size: {sdr.rx_buffer_size} samples")

# =====================================================================
# Transmit & Receive
# =====================================================================
t_start = time.time()

received_frames = np.zeros(samples_per_chirp, dtype=complex)  # complex array
for i in range(capture_range):
    rx_frame = sdr.rx()
    received_frames += rx_frame
    if i % 10 == 0:
        print(f"  Frame {i+1}/{capture_range} received")

received_data = received_frames  # already summed — no concatenate needed
print(f"Shape: {received_data.shape}")  # should be (4000,)
# =====================================================================
# Save results
# ========================================================# =====================================================================
# Dechirping
# =====================================================================
from scipy.signal import butter, filtfilt

def lowpass_filter(signal, cutoff_hz, fs, order=5):
    nyq    = fs / 2
    normal_cutoff = cutoff_hz / nyq      # normalize to Nyquist
    b, a   = butter(order, normal_cutoff, btype='low')
    return filtfilt(b, a, signal)        # zero-phase filtering

# Example — filter dechirped signal to keep only beat frequencies up to 1 MHz

# 1. Multiply received signal by conjugate of transmitted chirp
#    sig_A is your transmitted baseband chirp (already defined above)
sig_A = sig_A[:samples_per_chirp]   # trim to exactly 4000 samples
dechirped = received_data * np.conj(sig_A)

# Max range you care about (e.g. 100 m)
R_max      = 100                        # meters
f_beat_max = (2 * k * R_max) / c       # max beat frequency for that range
print(f"Max beat frequency for {R_max}m: {f_beat_max/1e3:.1f} kHz")

filtered = lowpass_filter(dechirped, cutoff_hz=f_beat_max, fs=fs)

# 2. FFT of dechirped signal
fft_dechirped = np.fft.fft(filtered, n=samples_per_chirp)
fft_dechirped = np.fft.fftshift(fft_dechirped)

# 3. Frequency axis → convert to range
freq_axis  = np.fft.fftshift(np.fft.fftfreq(samples_per_chirp, 1/fs))  # Hz
range_axis = (freq_axis * c) / (2 * k)                                   # meters

# 4. Plot range profile
import matplotlib.pyplot as plt

plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
plt.plot(freq_axis / 1e3, 20*np.log10(np.abs(fft_dechirped) + 1e-12))
plt.xlabel('Beat frequency (kHz)')
plt.ylabel('Power (dB)')
plt.title('Dechirped spectrum')
plt.grid()

plt.subplot(1, 2, 2)
# Only show positive ranges (0 to max)
pos_mask = range_axis >= 0
plt.plot(range_axis[pos_mask], 20*np.log10(np.abs(fft_dechirped[pos_mask]) + 1e-12))
plt.xlabel('Range (m)')
plt.ylabel('Power (dB)')
plt.title('Range profile')
plt.grid()

plt.suptitle('Dechirped signal')
plt.tight_layout()
plt.show()

# 5. Print range resolution and max unambiguous range
range_resolution   = c / (2 * B)
max_range          = (fs * c) / (2 * k)
print(f"Range resolution   : {range_resolution:.2f} m")
print(f"Max unambiguous range: {max_range/1e3:.2f} km")
#!/usr/bin/env python3

import adi
import numpy as np
import matplotlib.pyplot as plt
import time

# ============================================================
# Configuration
# ============================================================

SAMPLE_RATE = int(61.44e6)
CENTER_FREQ = int(2.4e9)

CHIRP_DURATION = 1e-3       # 1 ms
TX_GAIN = -10               # dB

# Use slightly less than full Nyquist to avoid filter rolloff
F_START = -5e6
F_STOP = 5e6

RX_BUFFER_SIZE = 65536

# ============================================================
# Generate complex chirp
# ============================================================

N = int(SAMPLE_RATE * CHIRP_DURATION)

t = np.arange(N) / SAMPLE_RATE

k = (F_STOP - F_START) / CHIRP_DURATION

phase = 2 * np.pi * (
    F_START * t +
    0.5 * k * t**2
)

chirp = np.exp(1j * phase)

# Scale to Pluto range
tx_data = (0.8 * chirp).astype(np.complex64)

print(f"Generated chirp:")
print(f"  Duration      : {CHIRP_DURATION*1e3:.2f} ms")
print(f"  Samples       : {N}")
print(f"  Start freq    : {F_START/1e6:.2f} MHz")
print(f"  Stop freq     : {F_STOP/1e6:.2f} MHz")
print(f"  Sweep BW      : {(F_STOP-F_START)/1e6:.2f} MHz")

# ============================================================
# Connect Pluto
# ============================================================

print("\nConnecting to Pluto...")

sdr = adi.Pluto()

sdr.sample_rate = SAMPLE_RATE

sdr.tx_lo = CENTER_FREQ
sdr.rx_lo = CENTER_FREQ

sdr.tx_rf_bandwidth = int(56e6)
sdr.rx_rf_bandwidth = int(56e6)

sdr.tx_hardwaregain_chan0 = TX_GAIN

sdr.rx_buffer_size = RX_BUFFER_SIZE

print("Connected.")

# ============================================================
# Start cyclic transmission
# ============================================================

print("Starting cyclic transmission...")

sdr.tx_destroy_buffer()
sdr.tx_cyclic_buffer = True
sdr.tx(tx_data)

time.sleep(0.5)

# ============================================================
# Receive samples
# ============================================================

print("Receiving samples...")

for i in range(10):
    rx = sdr.rx() #clear buffer and get latest samples

rx = sdr.rx()

print(f"Received {len(rx)} samples")

# ============================================================
# FFT
# ============================================================

window = np.hanning(len(rx))

spectrum = np.fft.fftshift(
    np.fft.fft(rx * window)
)

freq = np.fft.fftshift(
    np.fft.fftfreq(len(rx), d=1/SAMPLE_RATE)
)

psd = 20 * np.log10(np.abs(spectrum) + 1e-12)

# ============================================================
# Estimate occupied bandwidth
# ============================================================

threshold = np.max(psd) - 20

mask = psd > threshold

if np.any(mask):
    bw = freq[mask].max() - freq[mask].min()
else:
    bw = 0

print(f"Estimated occupied BW: {bw/1e6:.2f} MHz")

# ============================================================
# Plot
# ============================================================

plt.figure(figsize=(12, 6))

plt.plot(freq / 1e6, psd)

plt.xlabel("Baseband Frequency (MHz)")
plt.ylabel("Magnitude (dB)")
plt.title("Received Chirp Spectrum")

plt.grid(True)

plt.axvline(F_START/1e6, linestyle="--")
plt.axvline(F_STOP/1e6, linestyle="--")

plt.tight_layout()
plt.show()

# ============================================================
# Cleanup
# ============================================================

input("\nPress ENTER to stop transmission...")

sdr.tx_destroy_buffer()

print("Done.")
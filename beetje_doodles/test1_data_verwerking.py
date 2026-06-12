import numpy as np
import matplotlib.pyplot as plt
import re
from scipy.fft import rfft, rfftfreq, next_fast_len

filename = r"measurements\Horn against T = 5ms, D = 90.txt"

# Read file
with open(filename, "r") as f:
    lines = f.readlines()

total_time_s = None

# 1. Extract the total time and dynamically check the unit
for line in lines:
    if "Period" in line:
        # Regex captures group 1 (the number) and group 2 (the unit: us, ms, or s)
        match = re.search(r'([\d.]+)\s*([uµ]s|ms|s)', line, re.IGNORECASE)
        if match:
            value = float(match.group(1))
            unit = match.group(2).lower()
            
            # Convert the value to a standard seconds baseline
            if unit in ['us', 'µs']:
                total_time_s = value * 1e-6
            elif unit == 'ms':
                total_time_s = value * 1e-3
            elif unit == 's':
                total_time_s = value
        break

# 2. Extract signal values first (so we know exactly how many samples we have)
signal = []
for line in lines:
    parts = line.split()
    if len(parts) == 2 and parts[0].isdigit():
        signal.append(float(parts[1]))

signal = np.asarray(signal)

# 3. Calculate dt using the converted total time and the exact sample count
if total_time_s is not None and len(signal) > 0:
    dt = total_time_s / len(signal)
    fs = 1 / dt
else:
    raise ValueError("Could not extract Period or signal data from the file.")

# Create the time array now that dt is securely calculated
t = np.arange(0, len(signal) * dt, dt)

# Remove DC
signal = signal - np.mean(signal)

# ---> FIX: Create a separate variable for the windowed signal <---
signal_windowed = signal * np.hanning(len(signal))

# --------------------------
# Zero padding
# --------------------------
N = len(signal_windowed)

# Pad to 8× length
N_fft = next_fast_len(8 * N)

# ---> FIX: Pass 'signal_windowed' into the FFT <---
fft_vals = rfft(signal_windowed, n=N_fft)
freqs = rfftfreq(N_fft, d=dt)

# FMCW range axis
B = 10e6
T = 0.9e-3

range_axis = freqs * 3e8 * T / (2 * B)

# Magnitude
magnitude = np.abs(fft_vals)

# Normalize
magnitude /= np.max(magnitude)

# Convert to dB
magnitude_db = 20 * np.log10(magnitude + 1e-12)

# Plot
plt.figure(figsize=(10, 5))
plt.subplot(2, 1, 1)
plt.plot(range_axis, magnitude_db)
plt.xlabel("Range (m)")
plt.ylabel("Magnitude (dB)")
plt.title("Radar Range Profile")
plt.grid(True)

plt.subplot(2, 1, 2)
# ---> FIX: Plot the original, un-tapered 'signal' here <---
plt.plot(t[:N]/1e-3, signal)
plt.xlabel("Time (ms)")
plt.ylabel("Amplitude")
plt.title("Time-Domain Signal")
plt.grid(True)

plt.tight_layout()
plt.show()
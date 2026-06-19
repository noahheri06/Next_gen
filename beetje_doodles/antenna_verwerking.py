import numpy as np
import matplotlib.pyplot as plt
from scipy.signal.windows import blackman

# ==========================================
# 1. RADAR & MEASUREMENT PARAMETERS
# ==========================================
FILENAME = r"cables connected.txt"
FILE_PATH = f'measurements/{FILENAME}'
SAMPLING_RATE = 5000/(4e-3)           # Hz
CHIRP_BANDWIDTH = 80e6       # Hz
CHIRP_DURATION = 1e-3         # Seconds
TRIGGER_THRESHOLD = 1700      # mV
SPEED_OF_LIGHT = 3e8          # m/s

# ==========================================
# 2. FILE PARSING
# ==========================================
def load_oscilloscope_data(filepath):
    data_lines = []
    with open(filepath, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if parts and parts[0].isdigit():
                data_lines.append(line)
                
    data = np.loadtxt(data_lines)
    ch1 = data[:, 1]
    ch2 = data[:, 2]
    
    return ch1-np.mean(ch1), ch2

# ==========================================
# 3. PULSE EXTRACTION & COHERENT ADDITION
# ==========================================
def process_radar_data():
    # Load data
    ch1, ch2 = load_oscilloscope_data(FILE_PATH)
    
    # Create a boolean mask where the trigger is active
    is_pulse = np.abs(ch2) > TRIGGER_THRESHOLD
    
    # Find transitions (Rising edges = 1)
    diff = np.diff(np.concatenate(([0], is_pulse.astype(int))))
    trigger_indices = np.where(diff == 1)[0]
    
    if len(trigger_indices) < 2:
        print("Not enough trigger pulses found to establish an interval. Check your TRIGGER_THRESHOLD.")
        return

    # NEW LOGIC: A pulse starts at a trigger and ends at the NEXT trigger.
    # We discard the very last trigger because we don't know when that final pulse ends.
    starts = trigger_indices[:-1]
    ends = trigger_indices[1:]
        
    print(f"Found {len(starts)} complete pulse intervals.")

    # We find the minimum length of all extracted pulses to ensure matrix alignment
    pulse_lengths = ends - starts
    min_len = np.min(pulse_lengths)
    
    pulses = np.zeros((len(starts), min_len))
    for i, (s, e) in enumerate(zip(starts, ends)):
        # We only take 'min_len' samples from each interval so they stack perfectly
        pulses[i, :] = ch1[s : s + min_len]
        
    # Coherent addition (Averaging over all pulses)
    coherent_signal = np.mean(pulses, axis=0)
    
    # ==========================================
    # 4. SIGNAL PROCESSING (FFT)
    # ==========================================
    t = np.arange(min_len) / SAMPLING_RATE
    
    # Apply a window function (e.g., Blackman)
    window = blackman(min_len)
    windowed_signal = coherent_signal * window
    
    # Compute FFT with zero padding to nearest power of 2
    nfft = int(2**(3+np.ceil(np.log2(len(windowed_signal)))))
    fft_result = np.fft.fft(windowed_signal, n=nfft)
    fft_mag = np.abs(fft_result)
    
    # Generate Frequency Axis
    freqs = np.fft.fftfreq(nfft, 1 / SAMPLING_RATE)
    
    # Keep only the positive half of the spectrum
    pos_mask = freqs >= 0
    freqs = freqs[pos_mask]
    fft_mag = fft_mag[pos_mask]
    
    # Convert Magnitude to decibels (dB)
    # Adding a tiny offset to avoid log10(0) warnings just in case
    fft_mag_db = 20 * np.log10((fft_mag + 1e-12) / np.max(fft_mag)) 
    
    # Generate Range Axis
    range_axis = (SPEED_OF_LIGHT * CHIRP_DURATION * freqs) / (2 * CHIRP_BANDWIDTH)
    
    # ==========================================
    # 5. PLOTTING
    # ==========================================
    plt.figure(figsize=(12, 10))
    
    # Plot 1: Coherently Added Time Domain Signal
    plt.subplot(4, 1, 1)
    plt.plot(t * 1e3, coherent_signal, color='blue')
    plt.title("1. Coherently Added Beat Tone (Time Domain)")
    plt.xlabel("Time (ms)")
    plt.ylabel("Amplitude (mV)")
    plt.grid(True)
    
    # Plot 2: FFT (Frequency Domain)
    plt.subplot(4, 1, 2)
    plt.plot(freqs / 1e3, fft_mag_db, color='green')
    plt.title("2. Frequency Spectrum (Beat Frequencies)")
    plt.xlabel("Frequency (kHz)")
    plt.ylabel("Magnitude (dB)")
    plt.ylim(-30, 0)  # Focus on the main lobe and suppress noise floor
    plt.grid(True)
    
    # Plot 3: Range Profile
    plt.subplot(4, 1, 3)
    plt.plot(range_axis, fft_mag_db, color='red')
    plt.title("3. Radar Range Profile")
    plt.xlabel("Range (Meters)")
    plt.ylabel("Magnitude (dB)")
    plt.ylim(-30, 0)  # Focus on the main lobe and suppress noise floor
    plt.xlim(0, 20)
    plt.grid(True)
    
    # Plot 4: Trigger Events (Fixed)
    # Create a time axis for the entire raw dataset to plot the trigger properly
    t_full = np.arange(len(ch2)) / SAMPLING_RATE
    plt.subplot(4, 1, 4)
    plt.plot(t_full * 1e3, ch2, color='orange', label='CH2 (Raw)')
    plt.plot(t_full[starts] * 1e3, ch2[starts], 'ro', markersize=6, label='Detected Sweep Starts')
    plt.title("4. Raw Trigger Signal and Detected Intervals")
    plt.xlabel("Full Measurement Time (ms)")
    plt.ylabel("Amplitude (mV)")
    plt.legend(loc='upper right')
    plt.grid(True)

    plt.tight_layout()
    plt.savefig(rf"plots/{FILENAME}_radar_plots.png")
    plt.show()

if __name__ == "__main__":
    process_radar_data()
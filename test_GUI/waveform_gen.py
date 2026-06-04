import numpy as np

def generate_chirp(sample_rate, num_samples, bandwidth, mid_freq):
    """
    Generates a Linear Frequency Modulated (LFM) Chirp signal.
    """
    t = np.arange(num_samples) / sample_rate
    T = num_samples / sample_rate
    
    # Calculate starting and ending frequencies based on center freq and bandwidth
    f_start = mid_freq - (bandwidth / 2)
    f_slope = bandwidth / T
    
    # Phase calculation for linear chirp: 2*pi*(f_start*t + 0.5*slope*t^2)
    phase = 2 * np.pi * (f_start * t + 0.5 * f_slope * (t ** 2))
    chirp = np.exp(1j * phase)
    
    # Scale to 14-bit full range for Pluto DAC optimization
    return chirp * 16384

def generate_complex_exp(sample_rate, num_samples, freq):
    """
    Generates a simple complex exponential (CW tone).
    """
    t = np.arange(num_samples) / sample_rate
    signal = np.exp(1j * 2 * np.pi * freq * t)
    return signal * 16384

def load_waveform(filepath):
    """
    Loads I/Q data from a file. Supports .npy (numpy binary) or comma-separated text files.
    """
    if filepath.endswith('.npy'):
        data = np.load(filepath)
    else:
        # Assumes a 2-column text file: Real, Imag
        raw = np.loadtxt(filepath, delimiter=',')
        data = raw[:, 0] + 1j * raw[:, 1]
    return data

def coherent_alignment(rx_pulses, tx_template):
    """
    Aligns multiple received captures using cross-correlation against the 
    transmitted template, then adds them together coherently.
    rx_pulses: List of 1D complex numpy arrays.
    tx_template: The original transmitted complex waveform.
    """
    if not rx_pulses:
        return np.array([])
        
    aligned_pulses = []
    # Use the first pulse or the template to establish a baseline reference index
    for pulse in rx_pulses:
        # Cross-correlate to find the timing delay offset
        correlation = np.correlate(pulse, tx_template, mode='same')
        peak_idx = np.argmax(np.abs(correlation))
        
        # Shift the signal to align the peaks
        shift_amount = len(pulse) // 2 - peak_idx
        aligned_pulse = np.roll(pulse, shift_amount)
        aligned_pulses.append(aligned_pulse)
        
    # Coherent addition (Summing up the complex matrix across rows)
    coherent_sum = np.sum(aligned_pulses, axis=0)
    return coherent_sum
import time
import numpy as np
import matplotlib.pyplot as plt

# Import your custom TDD backend
import pluto_tdd 

def plot_fft_signal(signal, sample_rate):
    N_fft = int(2**(2+ np.ceil(np.log2(len(signal)))))
    fft_signal = np.fft.fft(signal, n=N_fft)
    freq = np.fft.fftfreq(N_fft, 1/sample_rate)
    plt.plot(freq/1e6, np.abs(fft_signal))
    plt.xlabel("Frequency (MHz)")
    plt.ylabel("Magnitude")
    plt.title("FFT of Signal")
    plt.show()

def main():
    # Pluto constants
    Pluto_IP = '192.168.2.1'
    PlutoSamprate = 59e6
    Tx_CenterFrequency = 2.1e9
    tx_gain = 0  # 0 is max power; consider -10 if testing on the bench
    print(f"tx_gain = {tx_gain} dB")
    # Radar waveform parameters
    B = 40e6 
    f_start = -B/2
    f_stop = B/2
    print(f"bandwidth is {B/1e6} MHz")
    print(f"start frequency is {f_start/1e6} MHz")
    print(f"stop frequency is {f_stop/1e6} MHz")
    
    T_chirp = 1e-3
    T_rest = 0
    fs = PlutoSamprate

    # Time vector
    N = int(round((T_chirp + T_rest) * fs))
    t = np.arange(N) / fs

    # Chirp generation
    chirp_window = np.concatenate((np.ones(int(T_chirp*fs)), np.zeros(int(T_rest*fs))))
    sig_A = np.exp(1j * 2 * np.pi * (f_start * t + 0.5 * B / T_chirp * t**2)) * chirp_window

    # --- DATA PACKING FOR pluto_tdd.py ---
    # The pluto_tdd module expects interleaved int16 data scaled to the DAC (4096)
    # just like the MATLAB script provided it.
    tx_scaled = sig_A * 4096
    
    # Create an empty int16 array double the size to hold I and Q sequentially
    tx_iq = np.empty(sig_A.size * 2, dtype=np.int16)
    tx_iq[0::2] = np.real(tx_scaled).astype(np.int16) # Evens are I
    tx_iq[1::2] = np.imag(tx_scaled).astype(np.int16) # Odds are Q

    # --- TDD TRIGGER PARAMETERS ---
    # frame_ms calculates total chirp length in ms plus a 0.1ms gap
    frame_ms = (len(sig_A) / fs) * 1000.0
    pulse_us = 10.0  # Pulse width in microseconds for the L10P scope trigger

    print("\nStarting TDD stream. Wire L10P -> scope trigger (CH2).")
    
    # Start the continuous cyclic transmission + L10P trigger
    stream_handle = pluto_tdd.start_tdd_stream(
        pluto_ip=Pluto_IP, 
        sample_rate=fs, 
        center_freq=Tx_CenterFrequency, 
        tx_gain=tx_gain, 
        tx_iq=tx_iq, 
        frame_ms=frame_ms, 
        pulse_us=pulse_us
    )

    try:
        print("Transmitting... Press Ctrl+C to stop.")
        # Let the hardware run continuously for 80 seconds
        time.sleep(3600)
    except KeyboardInterrupt:
        print("\nStopping transmission early...")

    # Safely spin down the TDD engine and clear hardware buffers
    pluto_tdd.stop_tdd_stream(stream_handle)

    # Plot the FFT of the original complex chirp
    plot_fft_signal(sig_A, fs)

if __name__ == "__main__":
    main()
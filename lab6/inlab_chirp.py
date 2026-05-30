import os
import time
import adi
import numpy as np

def continuous_transmit(my_sdr, iq):
    print("sending IQ data")
    iq = np.squeeze(iq)  # Removes dimensions of length 1   
    my_sdr.tx_cyclic_buffer = True  # must be true to use the continuos transmission
    my_sdr.tx(iq)
   
    # Print configuration information
    print("TX Transmission Mode: Continuous")
    print(f"TX Sampling_rate: {my_sdr.sample_rate}")
    print(f"TX buffer length: {len(iq)}")

def clear_buffer(my_sdr):
   
    # Clear the transmission buffer
    my_sdr.tx_destroy_buffer()
    print("Pluto Buffer Cleared!")

def receive_data(my_sdr, frame_length_samples, save_path = None):
   
    my_sdr._rx_init_channels()
   
    # Print configuration information
    print(f"RX Sampling_rate: {my_sdr.sample_rate}")
    print(f"Number of samples in a frame: {frame_length_samples}")
    print(f"RX buffer length: {frame_length_samples}")
   
    # receive the data
    received_array = my_sdr.rx()

    # Save the received data if needed
    if save_path is not None:
        np.save(save_path, received_array)
        print(f"Data saved to {save_path}")
   
    # Return the received np.array
    return received_array

def print_sdr_info(my_sdr):
    print(f"Sample Rate: {my_sdr.sample_rate}")
    print(f"TX LO: {my_sdr.tx_lo}")
    print(f"RX LO: {my_sdr.rx_lo}")

def initialize_pluto(PlutoIP,tx_buffer_size,sample_rate,tx_center_freq,rx_center_freq,rx_gain,tx_gain,rx_SamplePerFrame):
    PlutoIP = 'ip:'+PlutoIP
    my_sdr = adi.Pluto(uri=PlutoIP)
   
   
    my_sdr.sample_rate = int(sample_rate)
   
    my_sdr.tx_rf_bandwidth = int(sample_rate)
    my_sdr.rx_rf_bandwidth = int(sample_rate)
    my_sdr.rx_lo = int(rx_center_freq)
    my_sdr.tx_lo = int(tx_center_freq)
       
    print("I've set the sample rate and LOs!")
       
    # Configure Rx
    my_sdr.rx_enabled_channels = [0]
    sample_rate = int(my_sdr.sample_rate)
    # manual or slow_attack
    my_sdr.gain_control_mode_chan0 = "manual"
    my_sdr.rx_hardwaregain_chan0 = int(rx_gain)
    # Default is 4 Rx buffers are stored, but to immediately see the result, set buffers=1
    my_sdr._rxadc.set_kernel_buffers_count(1)

    # Configure Tx
    my_sdr.tx_enabled_channels = [0]
    my_sdr.tx_hardwaregain_chan0 = int(tx_gain)
   
    frame_length_samples = rx_SamplePerFrame
   
    if (
        frame_length_samples != tx_buffer_size
    ):
        frame_length_samples = int(tx_buffer_size)
   
    N_rx = int(1 * frame_length_samples)
    my_sdr.rx_buffer_size = N_rx

    print("SDR Configuration Completed")

    # Return the my_sdr and tddn objects
    return (my_sdr)

def main():
    #pluto constants
    Pluto_IP = '192.168.2.1'
    PlutoSamprate = 59e6
    Tx_CenterFrequency = 3e9
    Rx_CenterFrequency = 3e9
    tx_gain = -30
    rx_gain = 10

    # Radar waveform parameters
    B = 15e6
    f_start = 1.1*B
    f_stop = 2.1*B
    print("bandwidth is ", B/1e6, "MHz")
    print("start frequency is ", f_start/1e6, "MHz")
    print("stop frequency is ", f_stop/1e6, "MHz")
    T_chirp = 1e-3
    # T_rest = 1e-4
    T_rest = 0
    fs = PlutoSamprate
    amp = 1
    sine_freq = 0

    # Time vector
    N = int(round((T_chirp + T_rest) * fs))
    t = np.arange(N) / fs
    my_sdr = initialize_pluto(Pluto_IP, N, PlutoSamprate, Tx_CenterFrequency, Rx_CenterFrequency, rx_gain, tx_gain, N)

    #chirp generation
    chirp_window = np.concatenate((np.ones(int(T_chirp*fs)), np.zeros(int(T_rest*fs))))
    sig_A = np.exp(1j * 2 * np.pi * (f_start * t + 0.5 * B / T_chirp * t**2)) * chirp_window
    sig_B = np.exp(1j * 2 * np.pi * sine_freq * t) * chirp_window

    tx_waveform = (amp*(2**14) * sig_B).astype(np.complex64)

    clear_buffer(my_sdr)
    continuous_transmit(my_sdr, tx_waveform)
    
    time.sleep(15*60)

    my_sdr.tx_destroy_buffer()
    my_sdr.close()

if __name__ == "__main__":
    main()
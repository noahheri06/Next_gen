import numpy as np
import scipy.io
import os
import adi


def continuous_transmit(my_sdr, iq):
    
    # Invia il segnale IQ
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


def receive_data(my_sdr, frame_length_samples, path):
    
    my_sdr._rx_init_channels()
    
    # Print configuration information
    print(f"RX Sampling_rate: {my_sdr.sample_rate}")
    print(f"Number of samples in a frame: {frame_length_samples}")
    print(f"RX buffer length: {frame_length_samples}")
    
    # Initialize the array used to store the received data
    received_array = np.zeros((1, frame_length_samples), dtype=complex)

    
    received_array = my_sdr.rx()

    # Save the received data
    npy_file_path = os.path.join(path, 'received_data.npy')
    np.save(npy_file_path, received_array)

    print(f"Data saved to {npy_file_path}")
    
    # Return the received_array list
    return received_array.tolist()


def initialize_Pluto(PlutoIP,tx_buffer_size,sample_rate,tx_center_freq,rx_center_freq,rx_gain,tx_gain,rx_SamplePerFrame):
    PlutoIP = 'ip:'+PlutoIP
    my_sdr = adi.Pluto(uri=PlutoIP)
    
   
    my_sdr.sample_rate = int(sample_rate)
    
    my_sdr.tx_rf_bandwidth = int(sample_rate)
    my_sdr.rx_rf_bandwidth = int(sample_rate)
    my_sdr.rx_lo = int(tx_center_freq)
    my_sdr.tx_lo = int(rx_center_freq)
        
    print("I've set the sample rate and LOs!")
        
    my_sdr.rx_output_type    
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
    pluto_ip = '192.168.2.1'
    PlutoSamprate = 3e6
    TXcenterFreq = 1.5e9
    RXcenterFreq = 1.5e9
    TXgain = -20
    RXgain = 0
    tx_buffer_size = 1024
    rx_SamplePerFrame = 1024
    path = 'C:/Users/Noahh/Documents/python/next_gen/lab4/data'
    my_sdr = initialize_Pluto(pluto_ip,tx_buffer_size,PlutoSamprate,TXcenterFreq,RXcenterFreq,RXgain,TXgain,rx_SamplePerFrame)

    # Example IQ data (replace with your actual IQ data)
    iq_data = np.random.randn(1024) + 1j * np.random.randn(1024)  # Replace with your actual IQ data
    continuous_transmit(my_sdr, iq_data)
    received_data = receive_data(my_sdr, rx_SamplePerFrame, path)
    clear_buffer(my_sdr)

if __name__ == "__main__":
    main()
    
# -*- coding: utf-8 -*-
"""
Created on Sun May 11 15:04:54 2025

@author: Gaetano
"""

import adi

def initialize_Pluto(PlutoIP,tx_buffer_size,sample_rate,tx_center_freq,rx_center_freq,rx_gain,tx_gain,rx_SamplePerFrame):
    
    # %% Setup SDR
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
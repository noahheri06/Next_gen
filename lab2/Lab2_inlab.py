#afstand is 1.30 + 0.08

import skrf as rf
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
import sympy as sp

def readout_s2p(your_file):

  ntwk = rf.Network(f'lab2/measurements/{your_file}.s2p')

  # Frequency (Hz)
  freq = ntwk.f

  # S-parameters (complex!)
  S = ntwk.s   # shape: (Nfreq, 2, 2)

  # Individual parameters
  S11 = S[:, 0, 0]
  S21 = S[:, 1, 0]
  S12 = S[:, 0, 1]
  S22 = S[:, 1, 1]
  return(freq, S11, S21, S12, S22)

def calculate_minus10dB_bandwidth(freq, s11_db):
    valid_indices = np.where(s11_db <= -10)[0]

    if len(valid_indices) == 0:
        return 0.0

    min_freq = freq[valid_indices[0]]
    max_freq = freq[valid_indices[-1]]

    return max_freq - min_freq

def task1():
    freq, S11, S21, S12, S22 = readout_s2p('0')
    #S11 = S11/np.max(np.abs(S11))
    p_transmitted = 1-np.abs(S11)**2
    p_transmitted  = p_transmitted/np.max(p_transmitted)
    return_loss = 20 * np.log10(np.abs(S11))

    bandwidth = calculate_minus10dB_bandwidth(freq, return_loss)
    
    print(f"-10 dB Bandwidth: {bandwidth / 1e9:.2f} GHz")

    plt.plot(freq/1e9, return_loss, label='S11 (dB)')

    plt.axhline(y=-10, color='r', linestyle='--', label='-10 dB Threshold')
    plt.title('S-Parameter vs Frequency')
    plt.xlabel('Frequency (GHz)')
    plt.ylabel('Magnitude (dB)')
    plt.ylim(-40, 0)
    plt.legend()
    plt.grid()
    plt.show()

def task2():
    p_1 =[]
    p_2 = []
    p_3 = []
    for i in range(45):
        freq, S11, S21, S12, S22 = readout_s2p(f'{i*2}')
        #find correct indexis
        index1 = 1
        index2 = freq.index(15e9)
        index3 = freq.index(16e9)
 
        

        p_1.append(np.abs(S21[index1])**2)
        p_2.append(np.abs(S21[index2])**2)
        p_3.append(np.abs(S21[index3])**2)

    angles = np.linspace(0, 90, 45)
    plt.plot(p_1, angles)
    plt.show()


def task3():
    pass

if __name__ == "__main__":
    #task1()
    task2()
    #task3()
    pass
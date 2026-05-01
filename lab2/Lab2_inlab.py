#afstand is 1.30 + 0.08

import skrf as rf
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
import sympy as sp

def readout_s2p(your_file):

  ntwk = rf.Network(f'lab2/measurements/Practicum2-1.38m/{your_file}.s2p')

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

def calculate_minusdB_bandwidth(freq, s11_db, threshold=-10):
    valid_indices = np.where(s11_db <= threshold)[0]

    if len(valid_indices) == 0:
        return 0.0

    min_freq = freq[valid_indices[0]]
    max_freq = freq[valid_indices[-1]]

    return max_freq - min_freq

def task1():
    freq, S11, S21, S12, S22 = readout_s2p('0')

    return_loss = 20 * np.log10(np.abs(S11))

    bandwidth = calculate_minusdB_bandwidth(freq, return_loss, threshold=-10)
    
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
    for i in range(46):
        # print(i)
        freq, S11, S21, S12, S22 = readout_s2p(f'{i*2}')
        #find correct indexis
        index1 = np.where(freq == 13e9)
        index2 = np.where(freq == 15e9)
        index3 = np.where(freq == 16e9)

        db = 10*np.log10(np.abs(S21)**2)

        if(i==0):
            p_1.append(db[index1])
            p_2.append(db[index2])
            p_3.append(db[index3])
        else:
            p_1.append(db[index1])
            p_1.insert(0, db[index1])
            p_2.append(db[index2])
            p_2.insert(0, db[index2])
            p_3.append(db[index3])
            p_3.insert(0, db[index3])

    angles = np.linspace(-90, 90, 91)
    #print(angles)

    max = np.max(p_1)
    p_1 = p_1 - max
    plt.plot(angles, p_1)


    # if(plot_with_overlay):
    plt.grid()


    plt.xlabel("angle in degrees")
    plt.ylabel("S21 in dB")
    plt.show()


def task3():
    angles_deg = np.arange(0, 92, 2)
    angles_rad = np.deg2rad(angles_deg)

    S21_all = []
    for angle in angles_deg:
        freq, _, S21, _, _ = readout_s2p(str(angle))
        S21_all.append(S21)

    S21_all = np.array(S21_all) 

    D = []
    for f_idx in range(len(freq)):
        P = np.abs(S21_all[:, f_idx])**2
        P_max = np.max(P)
        integral = np.trapezoid(P * np.sin(angles_rad), angles_rad)

        D_f = 2 * P_max / integral 
        D.append(D_f)

    D = np.array(D)
    D_dBi = 10 * np.log10(D)

    plt.figure()
    plt.plot(freq / 1e9, D_dBi)
    plt.xlabel("Frequency (GHz)")
    plt.ylabel("Directivity (dBi)")
    plt.title("Directivity vs Frequency")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    #task1()
    #task2()
    task3()
    pass
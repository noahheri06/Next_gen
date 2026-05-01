import skrf as rf
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
import sympy as sp


def readout_s2p(your_file):
    ntwk = rf.Network(f'measurements/Practicum2-1.38m/{your_file}.s2p')
    freq = ntwk.f
    S = ntwk.s  # shape: (Nfreq, 2, 2)
    S11 = S[:, 0, 0]
    S21 = S[:, 1, 0]
    S12 = S[:, 0, 1]
    S22 = S[:, 1, 1]
    return freq, S11, S21, S12, S22


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
    task3()
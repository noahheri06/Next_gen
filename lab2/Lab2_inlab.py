#afstand is 1.30 + 0.08

import skrf as rf
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
import sympy as sp

def f_function(theta, phi, f):
    C = 3e8
    lx = 8.86e-2
    ly = 6.5e-2
    lambd = C / f
    gammax = (lx / lambd) * np.sin(theta) * np.cos(phi)
    gammay = (ly / lambd) * np.sin(theta) * np.sin(phi)
    f_val = np.sinc(gammax) * np.sinc(gammay)
    return f_val, lambd, gammax, gammay

def readout_s2p(your_file):

  ntwk = rf.Network(f'measurements/Practicum2-1.38m/{your_file}.s2p')

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
    plt.plot(freq/1e9, return_loss, label=r'$|S_{11}|$ (dB)')

    plt.axhline(y=-10, color='r', linestyle='--', label='-10 dB Threshold')
    plt.title('S-Parameter vs Frequency')
    plt.xlabel('Frequency (GHz)')
    plt.ylabel('Magnitude (dB)')
    plt.ylim(-40, 0)
    plt.legend()
    plt.grid()
    plt.savefig('task1.png')
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

    p_1 = p_1 - np.max(p_1)
    p_2 = p_2 - np.max(p_2)
    p_3 = p_3 - np.max(p_3)

    plt.plot(angles, p_1, label='13 GHz')
    plt.plot(angles, p_2, label='15 GHz')
    plt.plot(angles, p_3, label='16 GHz')
    plt.title("S21 parameter vs angle")
    plt.grid()
    plt.xlabel("angle (degrees)")
    plt.ylabel("Magnitude (dB)")
    plt.legend()
    plt.savefig("plots/task2.png")
    plt.show()

    theta = np.linspace(-np.pi, np.pi, 2000)
    phi = 0
    f_val, lambd, gammax, gammay = f_function(theta, phi, f=13e9)
    s1 = f_val**2
    normalized = 10 * np.log10(s1 / np.max(s1))
    plt.plot(np.rad2deg(theta), normalized, label='Theoretical 13 GHz')
    plt.plot(angles, p_1, label='Measured 13 GHz')
    plt.grid()
    plt.xlabel("angle (degrees)")
    plt.ylabel("Magnitude (dB)")
    plt.xlim(-90, 90)
    plt.ylim(-40, 0)
    plt.legend()
    plt.title("Comparison of Measured and Theoretical Radiation Pattern")
    plt.savefig("plots/task2_comparison.png")
    plt.show()


    # --- Polar plot ---
    # Convert to numpy arrays (needed for math operations)
    p_1 = np.array(p_1)
    p_2 = np.array(p_2)
    p_3 = np.array(p_3)

    # Take only 0 to 90 degrees (second half of your data)
    half_idx = len(angles)//2
    angles_half = angles[half_idx:]
    p1_half = p_1[half_idx:]
    p2_half = p_2[half_idx:]
    p3_half = p_3[half_idx:]

    # Mirror to -90 to 0 (symmetry)
    angles_full = np.concatenate((-angles_half[::-1], angles_half))
    p1_full = np.concatenate((p1_half[::-1], p1_half))
    p2_full = np.concatenate((p2_half[::-1], p2_half))
    p3_full = np.concatenate((p3_half[::-1], p3_half))

    # Convert to radians
    angles_rad = np.deg2rad(angles_full)

    # Polar plot
    plt.figure(figsize=(6,6))
    ax = plt.subplot(111, projection='polar')

    ax.plot(angles_rad, p1_full, label='13 GHz')
    ax.plot(angles_rad, p2_full, label='15 GHz')
    ax.plot(angles_rad, p3_full, label='16 GHz')

    # Title with padding so it doesn't overlap
    ax.set_title("Polar plot S21 vs angle", pad=20)

    # Orientation
    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)

    # Move legend outside
    ax.legend(loc='upper left', bbox_to_anchor=(1.1, 1.1))

    # Adjust layout so nothing gets cut off
    plt.tight_layout()
    plt.subplots_adjust(top=0.85, right=0.75)

    plt.savefig("plots/task2_polar.png", bbox_inches='tight')
    plt.show()

def directivity(S21_all, angles_rad):
    S = np.abs(S21_all)
    S_norm = S / np.max(S, axis=0, keepdims=True)

    N_freq = S_norm.shape[1]
    D = np.zeros(N_freq)

    threshold = 1 / np.sqrt(2)  

    for i in range(N_freq):
        pattern = S_norm[:, i]
        above = pattern >= threshold

        if not np.any(above):
            D[i] = np.nan
            continue

        idx = np.where(above)[0]
        i_min = idx[0]
        i_max = idx[-1]
        if i_min == 0:
            theta_min = angles_rad[0]
        else:
            x0, x1 = angles_rad[i_min - 1], angles_rad[i_min]
            y0, y1 = pattern[i_min - 1], pattern[i_min]

            theta_min = x0 + (threshold - y0) * (x1 - x0) / (y1 - y0 + 1e-12)
        if i_max == len(pattern) - 1:
            theta_max = angles_rad[-1]
        else:
            x0, x1 = angles_rad[i_max], angles_rad[i_max + 1]
            y0, y1 = pattern[i_max], pattern[i_max + 1]

            theta_max = x0 + (threshold - y0) * (x1 - x0) / (y1 - y0 + 1e-12)

        beta_half = theta_max - theta_min
        beta = 2 * beta_half
        D[i] = 4 * np.pi / (beta ** 2)

    return D.reshape(1, -1)

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

    D_method2 = directivity(S21_all, angles_rad)
    D_method2_dBi = 10 * np.log10(D_method2)
    print("Average difference in directivity (dB):", np.mean(D_method2_dBi.flatten() - D_dBi))

    efficiencies = [1, 0.67, 0.55]
    Ap = 8.86e-2 * 6.5e-2

    plt.subplot(1, 1, 1)
    c = 3e8
    for eff in efficiencies:
        Ae = eff * Ap
        d = (4 * np.pi * Ae * freq ** 2) / (c**2)
        plt.plot(freq / 1e9, 10 * np.log10(d), label=f'Directivity {int(eff*100)}% Efficiency')
    plt.plot(freq / 1e9, D_dBi, label='Directivity (Method 1)')
    plt.plot(freq / 1e9, D_method2_dBi.flatten(), label='Directivity (Method 2)')
    plt.xlabel("Frequency (GHz)")
    plt.ylabel("Directivity (dBi)")
    plt.title("Directivity vs Frequency")
    plt.grid(True)
    plt.legend(loc="upper left")
    plt.savefig("plots/task3_directivity.png")
    plt.show()

    # plt.subplot(2, 1, 2)
    # plt.plot(freq / 1e9, D_method2_dBi.flatten() - D_dBi, label='Difference')
    # plt.axhline(y=np.mean(D_method2_dBi.flatten() - D_dBi), color='r', linestyle='--', label='Average Difference')
    # plt.xlabel("Frequency (GHz)")
    # plt.ylabel("Difference in Directivity (dB)")
    # plt.title("Difference in Directivity vs Frequency")
    # plt.grid(True)
    # plt.legend()
    # plt.tight_layout()
    # plt.show()

if __name__ == "__main__":
    #task1()
    #task2()
    task3()
    pass
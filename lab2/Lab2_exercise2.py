import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import interp1d

data = np.loadtxt("Impedance_Antenna.txt", comments="#")
freq = data[:, 0]*1e9
Z_real = data[:, 1]
Z_imag = data[:, 2]
Z_ant = Z_real + 1j * Z_imag
Z_real_interp = interp1d(freq, Z_real, kind='cubic', fill_value="extrapolate")
Z_imag_interp = interp1d(freq, Z_imag, kind='cubic', fill_value="extrapolate")

def ZA(f):
    return Z_real_interp(f) + 1j * Z_imag_interp(f)

def P_r(f):
    Zg = 50
    G = 10**2
    R = 2
    c = 3e8
    gamma = (ZA(f) - Zg) / (ZA(f) + Zg)
    mismatch_efficiency = 1 - np.abs(gamma)**2
    Pt = 0.1 * mismatch_efficiency
    Pr_available = Pt * (G ** 2) * (c / (4 * np.pi * f * R))**2
    Pr_delivered = Pr_available * mismatch_efficiency
    return Pr_delivered

Pr = P_r(freq)
plt.plot(freq*1e-9, 10*np.log10(Pr)+30)
plt.xlabel("Frequency (GHz)")
plt.ylabel("Received Power (dBm)")
plt.title("Received Power vs Frequency")
plt.grid()
plt.savefig("plots/2d.png", dpi=500)
plt.show()




    
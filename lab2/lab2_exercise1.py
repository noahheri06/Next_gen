import numpy as np
import matplotlib.pyplot as plt

data = np.loadtxt("Impedance_Antenna.txt", comments="#")

freq = data[:, 0]
Z_real = data[:, 1]
Z_imag = data[:, 2]

Z_ant = Z_real + 1j * Z_imag

Z0 = 50
gamma_ant = (Z_ant - Z0) / (Z_ant + Z0)

plt.plot(freq, np.abs(gamma_ant)**2, label="Reflection Coefficient Magnitude")
plt.xlabel("Frequency (GHz)")
plt.ylabel("Reflection Coefficient Magnitude")
plt.title("Antenna Reflection Coefficient vs Frequency")
plt.grid()
plt.savefig("plots/1e.png", dpi=500)
plt.show()

Z0 = 50
Zg = 50
beta = 0.85 * 2 * np.pi * freq * 1e9 / (3e8)
l = 30e-2
Z_in = Z0 * (Z_ant + 1j*Z0 * np.tan(beta*l))/(Z0 + 1j*Z_ant * np.tan(beta*l))
gamma_in = (Z_in - Zg) / (Z_in + Zg)
P_rad = 0.1 * (1 - np.abs(gamma_in)**2)

plt.plot(freq, 10*np.log10(P_rad)+30, label="Radiated Power")
plt.xlabel("Frequency (GHz)")
plt.ylabel("Radiated Power (dBm)")
plt.title("Radiated Power vs Frequency")
plt.grid()
plt.savefig("plots/1f.png", dpi=500)
plt.show()
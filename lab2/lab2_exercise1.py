import numpy as np
import matplotlib.pyplot as plt


Z0 = 50
Zg = 50

# =============================================================================
# a
# =============================================================================

Z_A = 50+100j

Gamma = (Z_A-Z0)/(Z_A+Z0)
print(f"1a: The refelction coefficient is: {np.abs(Gamma)**2}")

# =============================================================================
# b
# =============================================================================
c0 = 299_792_458
f = 15e9

lambd = c0/f
k0 = 2*np.pi/lambd
beta = 0.8*k0
l = 5e-2

Zin = Z0 * (Z_A+1j*Z0*np.tan(beta*l))/(Z0+1j*Z_A*np.tan(beta*l))

print(f"1b: The input impedane Z_in is = {Zin}")

# =============================================================================
# c
# =============================================================================

Pi = 0.1

Ztot = Zg+Zin
Itot = np.sqrt(Pi/Ztot)
Pinc = np.abs(Itot)**2 / 2 * np.real(Zin)
Pl = Pinc * (1-np.abs(Gamma)**2)
Pr = Pinc * np.abs(Gamma)**2

print(f"1c: Pl = {Pl}, Pr = {Pr}")

# =============================================================================
# d
# =============================================================================

beta = 0.85 * k0

lambd = 2*np.pi / beta

l = lambd/4

Z_A = 100

# Zin = Z0**2/Z_A
# Zin must be matched to Zg, so Zin = 50
Zin = 50
Z_0 = np.sqrt(Zin*Z_A)

print(f"1d: The length l={l}, and the intrinsic impedance Z_0={Z_0}")


# =============================================================================
# e
# =============================================================================


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

# =============================================================================
# f
# =============================================================================

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










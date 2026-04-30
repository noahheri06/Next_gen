import numpy as np
import matplotlib.pyplot as plt

Z0 = 50
C = 3e8

# Frequencies
frequencies = [12e9, 15e9, 16e9]

# Angles
theta = np.linspace(-np.pi, np.pi, 2000)

# Dimensions
lx = 8.86e-2
ly = 6.6e-2

# Planes (phi values)
planes = [0, np.pi/2]
plane_labels = [r'$\phi = 0$', r'$\phi = 90\degree$']

def f_function(theta, phi, f):
    lambd = C / f
    gammax = (lx / lambd) * np.sin(theta) * np.cos(phi)
    gammay = (ly / lambd) * np.sin(theta) * np.sin(phi)
    f_val = np.sinc(gammax) * np.sinc(gammay)
    return f_val, lambd, gammax, gammay

# Create subplots (rows = planes, cols = frequencies)
fig, axes = plt.subplots(len(planes), len(frequencies), figsize=(15, 8), sharex=True, sharey=True)

for row, phi in enumerate(planes):
    for col, f in enumerate(frequencies):
        ax = axes[row, col]

        f_val, lambd, gammax, gammay = f_function(theta, phi, f)

        s1 = f_val**2
        normalized = 10 * np.log10(s1 / np.max(s1))

        ax.plot(np.rad2deg(theta), normalized)
        ax.set_title(f"f = {f/1e9:.0f} GHz")

        if col == 0:
            ax.set_ylabel(f"{plane_labels[row]}\nNormalized Power (dB)")
        if row == len(planes) - 1:
            ax.set_xlabel(r'$\theta$ (deg)')
        plt.ylim(-40, 0)
        plt.xlim(-180, 180)
        ax.grid(True)

plt.suptitle("Radiation Pattern for Different Frequencies and Planes", fontsize=16)
plt.tight_layout()
plt.show()


#B
freq_range = np.linspace(12e9, 16e9, 100000)
lambda_range = C/freq_range


#Directivity
k = 0.88 # slides for uniform ilumniation 
betaxz = k*lambda_range/lx
betayz = k*lambda_range/ly
D = 4*np.pi/(betaxz*betayz)
plt.plot(freq_range, D)
plt.title("directivity vs freq")
plt.show()


#C
R = 2 * lx**2 / lambd
print(R)


#D


efficiencies = [1, 0.8, 0.5]
Ap = [8.86e-2, 6.5e-2]

for i in range(2):
    for j in range(3):
        Ae = efficiencies[j]*Ap[i]
        d = (4*np.pi*Ae)/(lambda_range**2)
        plt.plot(lambda_range, d)
        plt.title(f"directitty at area = {Ae}")
        plt.show()


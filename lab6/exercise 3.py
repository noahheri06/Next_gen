import numpy as np
from matplotlib import pyplot as plt
from scipy.fft import fft,fftshift
from math import ceil
# =============================================================================
# PART A
# =============================================================================
print("Part A")

n_pulses = 40
tau_pulse = 10e-6
PRI = 1e-3


CPI = n_pulses * PRI



print(f"The CPI is {CPI*1e3} ms")

doppler_res_freq = 1/CPI
print(f"The Doppler resolution is {doppler_res_freq} Hz")



# =============================================================================
# PART B
# =============================================================================
print("Part B")

f_c = 12e6 # arbitrary
F_s = 50e6 # sampling freq


signal = np.zeros(int(CPI * F_s), dtype=complex)


samples_in_one_pulse = int(F_s * tau_pulse)
t = np.arange(samples_in_one_pulse) / F_s
one_pulse = np.exp(2j*np.pi*f_c*t)


PRI_samples = int(round(F_s * PRI))

for i in range(40):
    signal[i*PRI_samples:i*PRI_samples + samples_in_one_pulse] = one_pulse
    
    
    
# take fft
Signal = np.abs(fftshift(fft(signal, n = int(2**(np.ceil(np.log2(len(signal)))+3)))))

#normalize
Signal = Signal/np.max(Signal)


freqax = np.linspace(-F_s/2,F_s/2,num=len(Signal))

fig, (ax3,ax2,ax) = plt.subplots(3,1)
ax.plot(freqax,Signal)
ax2.plot(freqax,Signal)
ax3.plot(freqax,Signal)


ax.set_xlim(11.88,12.12)
ax.set_xlim(11.9999,12.0001)

ax.set_xlim(11_999_900,12_000_100)
ax2.set_xlim(11_995_000,12_005_000)
ax3.set_xlim(11_880_000,12_120_000)

ax.axhline(0.05,xmin=0.5+0.01, xmax=0.625+0.01, color = "red",label="Rayleigh width = 25Hz")
ax.axvline(12_000_002)
ax2.axhline(0.4,xmin=0.5,xmax=0.6,color="red", label="Spacing of line segments = 1 kHz")


ax.set_xlabel("Frequency (Hz)")
ax2.set_xlabel("Frequency (Hz)")
ax3.set_xlabel("Frequency (Hz)")


ax.set_ylabel("Normalized amplitude")
ax2.set_ylabel("Normalized amplitude")
ax3.set_ylabel("Normalized amplitude")

ax.legend(loc=1)
ax2.legend(loc=1)
plt.show()




# =============================================================================
# PART C
# =============================================================================
print("Part C")

f_c = 9.4e9
dv = 1 # m/s
PRF = 1500

doppler_res_freq = dv * 2 * f_c / 3e8
T_d = 1/doppler_res_freq

M = PRF * T_d
print(f"{ceil(M)} pulses must be processed")




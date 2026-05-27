import numpy as np
from matplotlib import pyplot as plt
from scipy.fft import fft,fftshift
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
F_s = 100e6 # sampling freq


signal = np.zeros(int(CPI * F_s))


samples_in_one_pulse = int(F_s * tau_pulse)
t = np.linspace(0, tau_pulse, num=samples_in_one_pulse)
one_pulse = np.sin(2*np.pi*f_c*t)


PRI_samples = F_s * PRI

for i in range(40):
    signal[int(i*PRI_samples):int(i*PRI_samples + samples_in_one_pulse)] = one_pulse
    
    
    
# take fft
Signal = np.abs(fftshift(fft(signal)))

#normalize
Signal = Signal/np.max(Signal)


freqax = np.linspace(-F_s/2,F_s/2,num=len(Signal))


fig, ax = plt.subplots(1,1)
ax.plot(freqax,Signal)
# ax.set_xlim(11e6,13e6)

plt.show()









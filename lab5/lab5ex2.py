import matplotlib.pyplot as plt
import numpy as np

Pt = 160e3
dB_pt = 10*np.log10(Pt)
f = 9.1e9
c = 3e8
k = 1.381e-23
lambd = c/f
tau = 1.2e-6
T_0 = 290 #K
PRF = 2e3
G_a = 45 #dB
lin_Ga = 10**(G_a/10)
T_d = 18.3e-3
F = 2.5 #dB
lin_F = 10**(F/10)
L = 11.2 #dB
lin_L = 10**(L/10)
atmos_L = 0.16 #dB/km 
lin_atmosL = 10**(atmos_L/10)
RCS = -20 #dBsm
lin_RCS = 10**(RCS/10) 
R = np.linspace(5e3, 105e3, 100)
SNR1 = (Pt * tau*T_d *(lin_Ga**2)*lin_RCS *(lambd**2)*PRF*lin_atmosL)/(lin_L*k*T_0*lin_F*(R**5)*(4*np.pi)**3)
SNR1log = 10*np.log10(SNR1)
SNR2 = dB_pt + 10*np.log10(tau) + 10*np.log10(T_d) + 10*np.log10(PRF) + 2*G_a + RCS + 2*10*np.log10(lambd) - L -F +atmos_L -10*np.log10(T_0) -50*np.log10(R) -30*np.log10(4*np.pi) -10*np.log10(k)
SNR15 = np.ones(100)*15
plt.plot(R,SNR1log)
plt.plot(R, SNR15)
plt.show()

plt.plot(R, SNR2)
plt.plot(R, SNR15)
plt.show()

diff = SNR1log - SNR15   # e.g. SNR_threshold = 0 or 13 dB
idx = np.where(np.diff(np.sign(diff)))[0]
x_cross = R[idx] + (R[idx+1] - R[idx]) * (-diff[idx] / (diff[idx+1] - diff[idx]))
print(f"Maximum range: {x_cross[0]/1e3:.2f} km")

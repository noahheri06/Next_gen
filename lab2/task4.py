import numpy as np
import skrf as rf
import matplotlib.pyplot as plt

def readout_s2p(your_file):

  ntwk = rf.Network(your_file)

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



phi = 0

freq, S11, S21, S12, S22 = readout_s2p("measurements/Practicum2-1.38m/0.s2p")

c0 = 3e8


r = 1.38 # 1, 0.5
lambd = c0/freq

gain = np.abs(S21)*4*np.pi*r/lambd

plt.plot(freq/1e9,10*np.log10(gain))
plt.xlabel("Freq (GHz)")
plt.ylabel("Gain (dB)")
plt.title("Gain per frequency")
plt.grid()

plt.show()
plt.savefig("plots/task4.png", dpi=500)
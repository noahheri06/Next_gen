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



def get_gain(dist,file):
    freq, S11, S21, S12, S22 = readout_s2p(file)

    c0 = 3e8


    lambd = c0/freq
    
    # Friis equation
    gain = np.abs(S21)*4*np.pi*dist/lambd
    
    return(freq,gain)




# voor elke afstand
freq_138,gain_138 = get_gain(1.38,"measurements/Practicum2-1.38m/0.s2p")

freq_100, gain_100 = get_gain(1.00,"measurements/Practicum2-1m/0.s2p")

freq_050, gain_050 = get_gain(0.5,"measurements/Practicum2-0.5m/0.s2p")


# far field distance

lx = 8.86e-2
ly = 6.5e-2
D = lx # (lx**2+ly**2)**0.5

lambd = 3e8/freq_138
R = 2*D**2/lambd



fig, ax1 = plt.subplots()




ax1.plot(freq_138/1e9,10*np.log10(gain_138),label="1.38m")
ax1.plot(freq_100/1e9,10*np.log10(gain_100),label="1m")
ax1.plot(freq_050/1e9,10*np.log10(gain_050),label="0.5m")


ax2 = ax1.twinx()
ax2.plot(freq_138/1e9,R,"--",label="Far field distance")
ax2.set_ylabel("Distance (m)")

ax1.set_xlabel("Freq (GHz)")
ax1.set_ylabel("Gain (dB)")
ax1.set_title("Gain per frequency")
ax1.grid()
ax1.legend()
ax2.legend(loc=4)


plt.show()
plt.savefig("plots/task5.png", dpi=500)
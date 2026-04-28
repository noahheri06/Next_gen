import skrf as rf
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
import sympy as sp

Z0 = 50

def readout_s2p(your_file):

  ntwk = rf.Network(f'{your_file}.s2p')
  # Frequency (Hz)
  freq = ntwk.f

  # S-parameters (complex!)
  S = ntwk.s   # shape: (Nfreq, 2, 2)

  # Individual parameters
  S11 = S[:, 0, 0]
  S21 = S[:, 1, 0]
  S12 = S[:, 0, 1]
  S22 = S[:, 1, 1]

  return(freq, S, S11, S21, S12, S22)




def plot_smith_charts(measured_file, given_file, m=0, n=0):
   # Create Network objects (needed for smith plotting)
  ntwk_measured = rf.Network(f'{measured_file}.s2p')
  ntwk_given = rf.Network(f'{given_file}.s2p')

  ntwk_measured.crop(0, 6, unit='ghz')
  ntwk_given.crop(0, 6, unit='ghz')

  # Plot Smith chart
  plt.figure()
  ntwk_measured.plot_s_smith(m=m, n=n, label="Measured")
  ntwk_given.plot_s_smith(m=m, n=n, label="Given (interpolated)")

  plt.title(f"Smith Chart (S{m+1}{n+1})")
  plt.legend()
  plt.show()
  
#for recalibrate measurement l=1.84cm

def method1():
  frequency, _, S11, S21, _, _ = readout_s2p("recalibrate")
  frequency = frequency[:-3*len(frequency)//10]
  S11 = S11[:len(frequency)]
  S21 = S21[:len(frequency)]
  phase = np.angle(S11, deg=False)
  magnitude = 20*np.log10(np.abs(S11))



  plt.subplot(2, 1, 1)
  plt.plot(frequency, magnitude)
  plt.title("Magnitude of S11")
  plt.xlabel("Frequency (Hz)")
  plt.ylabel("Magnitude (dB)")
  plt.grid()

  plt.subplot(2, 1, 2)
  plt.plot(frequency, phase)
  plt.title("Phase of S11")
  plt.xlabel("Frequency (Hz)")
  plt.ylabel("phase (rad)")
  plt.grid()

  time_delay = -np.gradient(phase, frequency*(2*np.pi))
  plt.subplot(2, 1, 3)
  plt.plot(frequency, time_delay)
  plt.ylim(0, 1e-10)
  plt.title("Time Delay")
  plt.xlabel("Frequency (Hz)")
  plt.ylabel("Time Delay (s)")
  plt.grid()
  plt.show()

  average_delay = np.mean(time_delay[0:len(time_delay)])
  print(average_delay)
  length = average_delay * 3e8*100
  print(f"Estimated length of the cable: {length:.2f} centimeters")


def interpolate_complex(x_old, y_old, x_new):
    real_interp = np.interp(x_new, x_old, np.real(y_old))
    imag_interp = np.interp(x_new, x_old, np.imag(y_old))
    return real_interp + 1j * imag_interp

def interpolate_sparameters(x_old, y_old, x_new): #freq tot, abcdtot, freq_probe


    y_new = np.zeros((len(x_new), 2, 2), dtype=complex)

    for i in range(2):
        for j in range(2):
            real_interp = np.interp(x_new, x_old, np.real(y_old[:, i, j]))
            imag_interp = np.interp(x_new, x_old, np.imag(y_old[:, i, j]))
            y_new[:, i, j] = real_interp + 1j * imag_interp

    return y_new


def method2():
    frequency_measured, _, S11_measured, S21_measured, _, _ = readout_s2p("recalibrate")
    S21_measured = S21_measured[:len(frequency_measured)]
    S11_measured = S11_measured[:len(frequency_measured)]

    frequency_given, _, S11_given, S21_given, _, _ = readout_s2p("thru_calibrated")
    S21_given = S21_given[:len(frequency_given)]
    S11_given = S11_given[:len(frequency_given)]

    S21_given_interp = interpolate_complex(frequency_given, S21_given, frequency_measured)
    S11_given_interp = interpolate_complex(frequency_given, S11_given, frequency_measured)
    frequency = frequency_measured

    WCEB11 = np.abs(S11_measured - S11_given_interp)
    WCEB21 = np.abs(S21_measured - S21_given_interp)
    WCEB = np.maximum(WCEB11, WCEB21)
    plt.plot(frequency, WCEB)
    plt.title("Worst Case Error Bound (WCEB)")
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("WCEB")
    plt.grid()
    plt.show()

    plot_smith_charts("measured_thru", "thru_calibrated", m=0, n=0)


def excersice2(measuered_transmission, given_probe):
  frequency_TOT, smat_TOT, S11_TOT, S21_TOT, S12_TOT, S22_TOT =readout_s2p(measuered_transmission)
  frequency_probe, smat_probe, S11_probe, S21_probe, S12_probe, S22_probe =readout_s2p(given_probe)

  ABCD_probe = rf.network.s2a(smat_probe, Z0)
  ABCD_TOT = rf.network.s2a(smat_TOT, Z0)
  ABCD_TOT = interpolate_sparameters(frequency_TOT, ABCD_TOT, frequency_probe)


  ABCD_LINE = []

  for i in range(len(frequency_probe)):
    ABCD_probe_i = ABCD_probe[i]
    ABCD_TOT_i = ABCD_TOT[i]
    ABCD_probe_i_inv = np.linalg.inv(ABCD_probe_i)


    result = np.matmul(ABCD_probe_i_inv, ABCD_TOT_i)
    result = np.matmul(result, ABCD_probe_i_inv)
    ABCD_LINE.append(result)

  #print(ABCD_LINE)
  ABCD_LINE = np.array(ABCD_LINE)

  S_LINE = rf.network.a2s(ABCD_LINE, Z0)
  plt.subplot(2, 1, 1)
  plt.title("Frequency vs Magnitude")
  plt.xlabel("Frequency (GHz)")
  plt.ylabel("Magnitude (dB)")
  plt.ylim(-40,0)
  plt.plot(frequency_TOT/1e9, 20*np.log10(np.abs(S11_TOT)), label="TOT")
  plt.plot(frequency_probe/1e9, 20*np.log10(np.abs(S_LINE[:, 0, 0])), label="LINE")
  plt.grid()
  plt.legend(loc="upper right")

  plt.subplot(2, 1, 2)
  plt.title("Frequency vs Phase")
  plt.xlabel("Frequency (GHz)")
  plt.ylabel("Phase (Rad)")
  plt.plot(frequency_TOT/1e9, np.angle(S11_TOT), label="TOT")
  plt.plot(frequency_probe/1e9, np.angle(S_LINE[:, 0, 0]), label="LINE")
  plt.grid()
  plt.legend(loc="upper right")


  plt.tight_layout()
  #plt.savefig("magnitude and freq exc2.png", dpi=600)
  plt.show()

def exercise3(impedance):
  freq, matrixs, S11, _, _, _ = readout_s2p(impedance)
  p_reflected = np.abs(S11)**2


  a = 138 # 26 = 1.4 GHz. 138 = 7 GHz
  freq = freq/1e9

  
  print(f"power reflected at {freq[a]} Ghz  = { 100*p_reflected[a]} %)")

  p_reflected = 10*np.log10(p_reflected)

  print(f" which equals {p_reflected[a]} dB)")

  plt.plot()
  plt.title("Frequency vs Magnitude")
  plt.xlabel("Frequency (GHz)")
  plt.ylabel("Magnitude (dB)")
  plt.ylim(-40,0)
  plt.plot(freq, p_reflected)
  plt.grid()
  plt.show()

  matrixz = rf.network.s2z(matrixs)
  Z11 = matrixz[:,0,0]

  # plt.plot(freq, np.real(Z11) > 50)
  # plt.show()

  Rl = np.real(Z11[a])
  Xl = np.imag(Z11[a])
  if(Rl > Z0):
    print("Step down needed")
    B = Xl + ((Rl/Z0)**(1/2) * (Rl**2 + Xl**2 - Rl*Z0)**(1/2))/(Rl**2 + Xl**2) #+ or - choice
    X = 1/B + Xl*Z0/Rl - Z0/(B*Rl)
    print(f"B = {B}, X = {X}")

  else:
    print("Step up needed")
    X = (Rl(Z0 - Rl))**(1/2) - Xl
    B = (((Z0-Rl)/Rl)**(1/2))/(Z0)
    print(f"B = {B}, X = {X}")
    #+ or - choice twice, both should have same sign
  return

if __name__ == "__main__":
  #method1()
  #method2()
  #excersice2("exerciswe2beter", "XMW_probe")
  exercise3("week1excercise3")
  pass
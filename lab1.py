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
  return(freq, S11, S21, S12, S22)


def getABCD(S11, S12, S21, S22):
  A  = ((1+S11)*(1-S22) + S12*S21)/(2*S21)
  B  = Z0*((1+S11)*(1+S22) - S12*S21)/(2*S21)
  C  = ((1-S11)*(1-S22) - S12*S21)/((2*S21)*Z0)
  D  = ((1-S11)*(1+S22) + S12*S21)/(2*S21)
  matrixABCD = np.array([[A, B], [C, D]])
  return (matrixABCD)

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
  frequency, S11, S21, _, _ = readout_s2p("recalibrate")
  frequency = frequency[:-3*len(frequency)//7]
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

  time_delay = -np.gradient(phase, frequency*(2*np.pi))
  plt.subplot(2, 1, 2)
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

def interpolate_sparameters(x_old, y_old, x_new):
    # y_old: shape (2, 2, N)

    y_new = np.zeros((2, 2, len(x_new)), dtype=complex)

    for i in range(2):
        for j in range(2):
            real_interp = np.interp(x_new, x_old, np.real(y_old[i, j, :]))
            imag_interp = np.interp(x_new, x_old, np.imag(y_old[i, j, :]))
            y_new[i, j, :] = real_interp + 1j * imag_interp

    return y_new


def method2():
    frequency_measured, S11_measured, S21_measured, _, _ = readout_s2p("recalibrate")
    S21_measured = S21_measured[:len(frequency_measured)]
    S11_measured = S11_measured[:len(frequency_measured)]

    frequency_given, S11_given, S21_given, _, _ = readout_s2p("thru_calibrated")
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
  frequency_TOT, S11_TOT, S12_TOT, S21_TOT, S22_TOT =readout_s2p(measuered_transmission)
  frequency_probe, S11_probe, S12_probe, S21_probe, S22_probe =readout_s2p(given_probe)

  ABCD_probe = getABCD(S11_probe, S12_probe, S21_probe, S22_probe)
  ABCD_TOT = getABCD(S11_TOT, S12_TOT, S21_TOT, S22_TOT)
  ABCD_TOT = interpolate_sparameters(frequency_TOT, ABCD_TOT, frequency_probe)

  ABCD_probe_inv = np.linalg.inv(np.moveaxis(ABCD_probe, 2, 0)).transpose(1, 2, 0)
  result = np.matmul(ABCD_probe_inv.transpose(2,0,1), ABCD_TOT.transpose(2,0,1))
  result = np.matmul(result, ABCD_probe_inv.transpose(2,0,1))
  ABCD_LINE = result.transpose(1,2,0)

  S_LINE = rf.a2s(np.moveaxis(ABCD_LINE, 2, 0), z0=Z0)
  plt.subplot(2, 1, 1)
  plt.plot(frequency_TOT, 20*np.log10(np.abs(S11_TOT)), label="TOT")
  plt.plot(frequency_probe, 20*np.log10(np.abs(S_LINE[:, 0, 0])), label="LINE")
  plt.grid()
  plt.legend()

  plt.subplot(2, 1, 2)
  plt.plot(frequency_TOT, np.angle(S11_TOT), label="TOT")
  plt.plot(frequency_probe, np.angle(S_LINE[:, 0, 0]), label="LINE")
  plt.grid()
  plt.legend()
  plt.show()


if __name__ == "__main__":
  #method1()
  method2()
  #excersice2("exerciswe2beter", "XMW_probe")
  pass
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import loadmat

#====================
# task A
#====================
B, R, T, c = 5e6, 200, 1e-3, 3e8

fb = 2*B*R/(T*c)
print("The beat frequency is: ", round(fb, 1), "Hz")

#====================
# task B
#====================
fs = 200e6
data1 = loadmat("data_ex3/Data_file_1.mat")
data2 = loadmat("data_ex3/Data_file_2.mat")
data3 = loadmat("data_ex3/Data_file_3.mat")
data4 = loadmat("data_ex3/Data_file_4.mat")
data5 = loadmat("data_ex3/Data_file_5.mat")
data6 = loadmat("data_ex3/Data_file_6.mat")
data7 = loadmat("data_ex3/freq_axis.mat")
data8 = loadmat("data_ex3/time_axis.mat")

print(data1.keys())
print(data2.keys())
print(data3.keys())
print(data4.keys())
print(data5.keys())
print(data6.keys())
print(data7.keys())
print(data8.keys())

signalA = data1['sig_A'].flatten()
signalA_fft = data2['sig_A_fft'].flatten()
signalB = data3['sig_B'].flatten()
signalB_fft = data4['sig_B_fft'].flatten()
signalC = data5['sig_C'].flatten()
signalC_fft = data6['sig_C_fft'].flatten()
freq = data7['freqaxis'].flatten()
time = data8['t'].flatten()

print("Signal A shape: ", np.real(signalA).shape)
print("Signal B shape: ", np.real(signalB).shape)
print("Signal C shape: ", np.real(signalC).shape)
print("FFT of Signal A shape: ", signalA_fft.shape)
print("FFT of Signal B shape: ", signalB_fft.shape)
print("FFT of Signal C shape: ", signalC_fft.shape)

# Plotting
fig, axes = plt.subplots(3, 2, figsize=(12, 10))
axes[0, 0].plot(time/1e-3, np.real(signalA))
axes[0, 0].set_title("Signal A")
axes[0, 0].set_xlabel("Time (ms)")
axes[0, 0].set_ylabel("Amplitude")
axes[0, 1].plot(freq/1e6, np.abs(signalA_fft))
axes[0, 1].set_title("FFT of Signal A")
axes[0, 1].set_xlabel("Frequency (MHz)")
axes[0, 1].set_ylabel("Magnitude")
axes[1, 0].plot(time/1e-3, np.real(signalB))
axes[1, 0].set_title("Signal B")
axes[1, 0].set_xlabel("Time (ms)")
axes[1, 0].set_ylabel("Amplitude")
axes[1, 1].plot(freq/1e6, np.abs(signalB_fft))
axes[1, 1].set_title("FFT of Signal B")
axes[1, 1].set_xlabel("Frequency (MHz)")
axes[1, 1].set_ylabel("Magnitude")
axes[2, 0].plot(time/1e-3, np.real(signalC))
axes[2, 0].set_title("Signal C")
axes[2, 0].set_xlabel("Time (ms)")
axes[2, 0].set_ylabel("Amplitude")
# axes[2, 1].plot(freq/1e6, np.abs(signalC_fft[0:200000]))
axes[2, 1].plot(freq/1e6, np.abs(np.fft.fft(signalC)[0:200000])) ##can replace this later with the correct file on bs
axes[2, 1].set_title("FFT of Signal C")
axes[2, 1].set_xlabel("Frequency (MHz)")
axes[2, 1].set_ylabel("Magnitude")
plt.tight_layout()
plt.savefig("plots/3b.png")
plt.show()


#====================
# task C
#====================
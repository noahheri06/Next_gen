import scipy.io

from scipy import fft, signal

import numpy as np
from matplotlib import pyplot as plt

import h5py
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# then your original line works as-is
scipy.io.loadmat('Data file week6 highSNR.mat')

C = 3e8

B = 200e6
T = 0.1e-3
F_CARRIER = 2e9
F_SAMPLE = 500e6

FRAME_LENGTH = 25.6e-3

def zero_append(signal, amount = 1000):
    signal_padded = np.concatenate((signal, np.zeros(amount)))
    return signal_padded

def recalc_dists_from_signal(power_db, sampling_rate, B, T):

    peaks_index = signal.find_peaks(power_db, threshold=2, height=-30)

    freqs = np.zeros(len(peaks_index[0]))
    freq_axis = fft.fftfreq(len(power_db), d=1/sampling_rate)
    for i, index in enumerate(peaks_index[0]):
        
        freqs[i] = freq_axis[index]


    print(f"The found frequencies are {freqs}")

    dists = np.zeros_like(freqs)
    for i, freq in enumerate(freqs):
         dists[i] = (C*T*freq)/(2*B)
    print(f"Number of found distances are {len(dists)}")
    print(f"The found distances are {dists}")
    return dists


def plot_power_spectra(power_db, sampling_rate = F_SAMPLE, calc_dists = True, dists = [], Bandwidth =B, Chirp_Time =T):


    freq_axis = fft.fftfreq(len(power_db), d=1/sampling_rate)
    range_axis = freq_axis * C * Chirp_Time / (2 * Bandwidth)

    fig, ax1 = plt.subplots(figsize=(10,5))

    half = len(freq_axis)//2


    ax1.plot(range_axis[:half], power_db[:half])
    ax1.set_ylabel("Power (dB)")
    ax1.set_ylim(-80, 1)
    

    if (calc_dists == True):
        found_dists = recalc_dists_from_signal(power_db, sampling_rate, Bandwidth, Chirp_Time)


    # ax1.set_xlim(0, 30)
    range_ticks = np.arange(0, 31, 5)
    ax1.set_xticks(range_ticks)
    ax1.set_xlabel("Range (m)")
    ax1.grid()

    ax2 = ax1.twiny()
    ax2.set_xlim(ax1.get_xlim())
    freq_ticks = 2 * Bandwidth * range_ticks / (C * Chirp_Time)
    ax2.set_xticks(range_ticks)
    ax2.set_xticklabels([f"{f/1000:.0f}" for f in freq_ticks])
    ax2.set_xlabel("Frequency (kHz)")

    plt.title("FFT of Situation A")
    plt.show()



def task1():
    SamplesPerChirp = T*F_SAMPLE
    print(f"The amount of samples per chirp is {SamplesPerChirp}")

    TBetweenSamples = 1/F_SAMPLE
    print(f"The time between each sample is {TBetweenSamples}")

    ChirpsInFrame = FRAME_LENGTH/T
    print(f"The amount of chirps in one frame is {ChirpsInFrame}")


    Totalsamples = SamplesPerChirp * ChirpsInFrame
    print(f"The amount of total samples in is {Totalsamples}")

    RadarData = scipy.io.loadmat('Data file week6 highSNR.mat', mat_dtype = False)['s_beat_vector']
    RadarData = RadarData[:,0]

    RadarData = np.reshape(RadarData, (int(ChirpsInFrame), int(SamplesPerChirp)))
    #print(len(RadarData[0]))
    return RadarData


def task2(RadarData):
    fig, ax = plt.subplots(1,1)
    FFT_RadarData = np.fft.fft(RadarData)
    
    FFT_RadarData = np.abs(FFT_RadarData)
    
    FFT_RadarData = FFT_RadarData/np.max(FFT_RadarData)
    
    print(FFT_RadarData)
    print(np.max(FFT_RadarData), np.argmax(FFT_RadarData))
    
    FFT_RadarData = 20*np.log10(FFT_RadarData)
    
    R_MAX = C * T / (2 * B) * F_SAMPLE
    ax.imshow(FFT_RadarData,vmin = -100, vmax=0, extent = (-R_MAX/2, R_MAX/2, 0,250), aspect="auto", cmap='magma')
    ax.set_xlim(18500,R_MAX/2)
    plt.xlabel("Range [m]")
    plt.ylabel("Chirp")
    plt.show()
    return

    for i in range(len(RadarData[:,0])):
        RadarData_AlongRow = zero_append(RadarData[i], 15536) #DFT zooi maar totale machten van 2 werken beste ## nu 2^16
        FFT_RadarData_AlongRow = np.fft.fft(RadarData_AlongRow)
        FFT_RadarData_AlongRow = np.fft.fftshift(FFT_RadarData_AlongRow)

        


        freq_axis = fft.fftfreq(len(FFT_RadarData_AlongRow), d=1/F_SAMPLE)
        
        power_spectrum = np.abs(FFT_RadarData_AlongRow)**2
        freq_axis = fft.fftfreq(len(power_spectrum), d=1/F_SAMPLE)
        power_db = 10*np.log10(power_spectrum / np.max(power_spectrum) + 1e-12)
        
        # peaks_index = signal.find_peaks(power_db, threshold=22)
        # freqs = np.zeros(len(peaks_index[0]))
        # for i, index in enumerate(peaks_index[0]):
        #     freqs[i] = freq_axis[index]

        
        # print(f"The found frequencies are {len(freqs)}")
        # Ranges = freqs*(C*T)/(2*B)
        # print(f"The found ranges are {Ranges}")
        if (i ==10 or i ==250):
            plot_power_spectra(power_db, calc_dists=False)


def task3(RadarData):
    fig, ax = plt.subplots(1,1)
    FFT_RadarData = np.fft.fft2(RadarData)

    FFT_RadarData = np.abs(FFT_RadarData)
    
    FFT_RadarData = FFT_RadarData/np.max(FFT_RadarData)
    
    print(FFT_RadarData)
    print(np.max(FFT_RadarData), np.argmax(FFT_RadarData))
    
    FFT_RadarData = 20*np.log10(FFT_RadarData)
    
    R_MAX = C * T / (2 * B) * F_SAMPLE
    Fd_MAX = 1/(2*T)
    ax.imshow(FFT_RadarData,vmin = -100, vmax=0, extent = (-R_MAX/2, R_MAX/2, -Fd_MAX,Fd_MAX), aspect="auto", cmap='magma')
    ax.set_xlim(18500,R_MAX/2)
    plt.xlabel("Range [m]")
    plt.ylabel("Frequency [Hz]")
    plt.show()
    return

def task4(RadarData):
    fig, ax = plt.subplots(1,1)
    FFT_RadarData = np.fft.fft2(RadarData)

    FFT_RadarData = np.abs(FFT_RadarData)
    
    FFT_RadarData = FFT_RadarData/np.max(FFT_RadarData)
    
    print(FFT_RadarData)
    print(np.max(FFT_RadarData), np.argmax(FFT_RadarData))
    
    FFT_RadarData = 20*np.log10(FFT_RadarData)
    
    R_MAX = C * T / (2 * B) * F_SAMPLE
    V_MAX = C / (F_CARRIER * T * 4)
    ax.imshow(FFT_RadarData,vmin = -100, vmax=0, extent = (-R_MAX/2, R_MAX/2, -V_MAX,V_MAX), aspect="auto", cmap='magma')
    ax.set_xlim(18500,R_MAX/2)
    plt.xlabel("Range [m]")
    plt.ylabel("Velocity [m/s]")
    plt.show()
    return


if __name__ == "__main__":
    RadarData = task1()
    # task2(RadarData)
    # task3(RadarData)
    task4(RadarData)


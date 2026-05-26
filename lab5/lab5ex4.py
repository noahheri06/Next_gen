import numpy as np
from scipy import fft, signal
import matplotlib.pyplot as plt


DISTS = [5, 8, 12] ## assumed to be sorted
C = 3e8

def create_tones(dists, t, B = 200e6, T = 0.1e-3, amplitudes = np.ones_like(DISTS)):
    all_S_beats = []

    for j in range(len(t)): ## for every time moment
        #print(t[j])
        S_beats = []
        for i, dist in enumerate(dists):
            tau_n = 2*dist/C
            exponent = 1j*2*np.pi*(B/T)*t[j]*tau_n
            S_beat = np.exp(exponent)*amplitudes[i]
            S_beats.append(S_beat)
        
        all_S_beats.append(S_beats)
    
    all_S_beats = np.sum(all_S_beats, axis=1)
    received_signal = np.real(all_S_beats)

    return all_S_beats, received_signal

def calc_amplitudes(dists, rcses = False, reference_0 = True):
    amplitudes = np.ones_like(dists)

    if (reference_0 == False):
        at_zero = (4*np.pi*(dists[0]**2))**2
        #print(at_zero)
        amplitudes = amplitudes * at_zero
        
    # print(amplitudes)

    for i, dist in enumerate(dists):
        correction_factor = 1/((4*np.pi*(dist**2))**2)
        amplitudes[i] = amplitudes[i] * correction_factor
    
    # print(amplitudes)

    if (rcses != False):
        for i, rcs, in enumerate(rcses):
            amplitudes[i] = amplitudes[i]*rcs

    return amplitudes

def calc_expected_freqs(dists, B, T):
    freqs = np.zeros_like(dists)
    for i, dist in enumerate(dists):
        freqs[i] = 2*B*dist/(C*T)
    print(f"The expected frequencies are {freqs}")
    return freqs

def recalc_dists_from_signal(received_signal, sampling_rate, B, T):
    received_fft = fft.fft(received_signal)
    power_spectrum = np.abs(received_fft)**2
    freq_axis = fft.fftfreq(len(power_spectrum), d=1/sampling_rate)
    
    peaks_index = signal.find_peaks(power_spectrum)

    freqs = np.zeros_like(peaks_index[0])
    for i, index in enumerate(peaks_index[0]):
        freqs[i] = freq_axis[index]


    print(f"The found frequencies are {freqs}")

    dists = np.zeros_like(freqs)
    for i, freq in enumerate(freqs):
        dists[i] = (C*T*freq)/(2*B)
    
    print(f"The found distances are {dists}")
    return dists


def plot_power_spectra(received_signal, sampling_rate, dB = False, calc_freqs = False, calc_dists = False, dists = [], B =0, T =0):
    received_fft = fft.fft(received_signal)
    power_spectrum = np.abs(received_fft)**2

    power_db = 10*np.log10(power_spectrum)

    freq_axis = fft.fftfreq(len(power_spectrum), d=1/sampling_rate)

    plt.figure(figsize=(10,5))
    if (dB == True):
        plt.plot(freq_axis[:len(freq_axis)//2], power_db[:len(power_db)//2])
        plt.ylabel("Power (dB)")
    else:
        plt.plot(freq_axis[:len(freq_axis)//2], power_spectrum[:len(power_spectrum)//2])
        plt.ylabel("Power (W)")
    
    if (calc_freqs == True):
        freqs = calc_expected_freqs(dists, B, T)    
        for i, freq in enumerate(freqs):
            plt.axvline(freq)

    if (calc_dists == True):
        found_dists = recalc_dists_from_signal(received_signal, sampling_rate, B, T)

    plt.xlim(0, 400e3)
    plt.xlabel("Frequency (Hz)")
    plt.title("FFT of measured powers")
    plt.grid()
    plt.show()

def calc_signal_power(received_signal, time):
    abs_square = np.abs(received_signal)**2
    power = abs_square/time
    return power

def create_noise_signal(received_signal, measuring_time, snr_db):
    signal_power = calc_signal_power(received_signal, measuring_time)
    snr_factor = 10**(snr_db/10)
    noise_power = signal_power/snr_factor

    samples = len(received_signal)
    noise = np.random.normal(size = samples) + 1j*np.random.normal(size= samples)
    noise = noise*(noise_power**(1/2))/2
    return noise

def task1():
    sampling_rate = 500e6
    measuring_time = 0.1e-3  ##start taking really long if larger than 0.001
    samples = measuring_time * sampling_rate
    t_axis = np.linspace(0, measuring_time, int(samples))
    s_beats, received_signal = create_tones(DISTS, t_axis)

    plot_power_spectra(s_beats, sampling_rate, 
                       calc_freqs=True, calc_dists=True, dB = True,
                       dists=DISTS, B =200e6, T = 0.1e-3)
    



    #print(s_beats)

def task2():
    sampling_rate = 500e6
    measuring_time = 0.1e-3  ##start taking really long if larger than 0.001
    samples = measuring_time*sampling_rate
    t_axis = np.linspace(0, measuring_time, int(samples))

    amplitudes = calc_amplitudes(DISTS, reference_0 = False)
    
    s_beats, received_signal = create_tones(DISTS, t_axis, amplitudes= amplitudes)

    plot_power_spectra(s_beats, sampling_rate, 
                       calc_freqs=True, calc_dists=True, dB = True,
                       dists=DISTS, B =200e6, T = 0.1e-3)



def task3():
    sampling_rate = 500e6
    measuring_time = 0.1e-3 ##start taking really long if larger than 0.001
    snr_db = 3 #-30 #(dB)

    samples = measuring_time*sampling_rate
    t_axis = np.linspace(0, measuring_time, int(samples))

    amplitudes = calc_amplitudes(DISTS, reference_0 = False)

    s_beats, received_signal = create_tones(DISTS, t_axis, amplitudes= amplitudes)
    print(s_beats)


    noise_signal = create_noise_signal(s_beats, measuring_time, snr_db)

    s_with_noise = s_beats + noise_signal


    plot_power_spectra(s_with_noise, sampling_rate, 
                       calc_freqs=True, calc_dists=True, dB = True,
                       dists=DISTS, B =200e6, T = 0.1e-3)
    return "Fuck you"

def task4():
    sampling_rate = 500e6
    measuring_time = 0.1e-3 ##start taking really long if larger than 0.001
    snr_db = -30 #(dB)
    k = 50

    samples = measuring_time*sampling_rate
    t_axis = np.linspace(0, measuring_time, int(samples))

    amplitudes = calc_amplitudes(DISTS, reference_0 = False)

    s_beats, received_signal = create_tones(DISTS, t_axis, amplitudes= amplitudes)
    print(s_beats)

    s_average = np.zeros_like(s_beats)
    for i in range(k):
        noise_signal = create_noise_signal(s_beats, measuring_time, snr_db)
        s_with_noise = s_beats + noise_signal
        s_average = s_average + s_with_noise
    s_average = s_average # klopt

    

    plot_power_spectra(s_average, sampling_rate, 
                       calc_freqs=True, calc_dists=True, dB = True,
                       dists=DISTS, B =200e6, T = 0.1e-3)
    return "Fuck you"

if __name__ == "__main__":
    #task1()
    #task2()
    #task3()
    task4()
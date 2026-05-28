import numpy as np
from scipy import fft, signal
import matplotlib.pyplot as plt


DISTS = [5, 8, 12] ## assumed to be sorted
C = 3e8

def create_tones(dists, t, B = 200e6, T = 0.1e-3, amplitudes = np.ones_like(DISTS)):
    all_S_beats = []

    for k in range(len(t)): ## for every time moment
        #print(t[j])
        S_beats = []
        for i, dist in enumerate(dists):
            tau_n = 2*dist/C
            exponent = 1j*2*np.pi*(B/T)*t[k]*tau_n
            S_beat = np.exp(exponent)*amplitudes[i]
            S_beats.append(S_beat)
        
        all_S_beats.append(S_beats)
    
    all_S_beats = np.sum(all_S_beats, axis=1)
    received_signal = np.real(all_S_beats)

    return all_S_beats, received_signal

def zero_append(signal, amount = 1000):
    signal_padded = np.concatenate((signal, np.zeros(amount)))
    return signal_padded

def calc_amplitudes(dists, rcses = False, reference_0 = True):
    amplitudes = np.ones_like(dists)

    if (reference_0 == False):
        at_zero = (4*np.pi*(dists[0]**2))**2
        #print(at_zero)
        amplitudes = amplitudes * at_zero
        
    #print(amplitudes)

    for i, dist in enumerate(dists):
        correction_factor = 1/((4*np.pi*(dist**2))**2)
        amplitudes[i] = amplitudes[i] * correction_factor
    
    print(amplitudes)

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
    power_db = 10*np.log10(power_spectrum / np.max(power_spectrum) + 1e-12)

    peaks_index = signal.find_peaks(power_db, threshold=2, height=-30)

    freqs = np.zeros(len(peaks_index[0]))
    for i, index in enumerate(peaks_index[0]):
        freqs[i] = freq_axis[index]


    print(f"The found frequencies are {freqs}")

    dists = np.zeros_like(freqs)
    for i, freq in enumerate(freqs):
         dists[i] = (C*T*freq)/(2*B)
    print(f"Number of found distances are {len(dists)}")
    print(f"The found distances are {dists}")
    return dists


def plot_power_spectra(received_signal, sampling_rate, dB = False, calc_freqs = False, calc_dists = False, dists = [], B =0, T =0):
    padded_zero = zero_append(received_signal, 15536) ## padded to the next power of two cuz apperently that works best (does appear so)
    received_fft = fft.fft(padded_zero)
    power_spectrum = np.abs(received_fft)**2
    power_db = 10*np.log10(power_spectrum / np.max(power_spectrum) + 1e-12)

    freq_axis = fft.fftfreq(len(power_spectrum), d=1/sampling_rate)
    range_axis = freq_axis * C * T / (2 * B)

    fig, ax1 = plt.subplots(figsize=(10,5))

    half = len(freq_axis)//2


    if dB:
        ax1.plot(range_axis[:half], power_db[:half])
        ax1.set_ylabel("Power (dB)")
        ax1.set_ylim(-80, 1)

    else:
        ax1.plot(range_axis[:half], power_spectrum[:half])
        ax1.set_ylabel("Power (W)")


    if (calc_freqs == True):
        freqs = calc_expected_freqs(dists, B, T)
        for distance in dists:
            ax1.axvline(distance, ls="--", c="red")

    if (calc_dists == True):
        found_dists = recalc_dists_from_signal(padded_zero, sampling_rate, B, T)


    ax1.set_xlim(0, 30)
    range_ticks = np.arange(0, 31, 5)
    ax1.set_xticks(range_ticks)
    ax1.set_xlabel("Range (m)")
    ax1.grid()

    ax2 = ax1.twiny()
    ax2.set_xlim(ax1.get_xlim())
    freq_ticks = 2 * B * range_ticks / (C * T)
    ax2.set_xticks(range_ticks)
    ax2.set_xticklabels([f"{f/1000:.0f}" for f in freq_ticks])
    ax2.set_xlabel("Frequency (kHz)")

    plt.title("FFT of Situation A")
    plt.show()

def plot_time_domain(received_signal, time_axis):

    time_us = time_axis * 1e6
    plt.plot(time_us ,received_signal )
    plt.xlim(0,0.1e3)
    plt.xlabel("Time (µs)")
    plt.ylim(-3,3)
    plt.ylabel("Amplitude")
    plt.grid()
    plt.title("Time Domain Signal of Situation A")
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

def plot_power_spectra_with_noise (s_beats, measuring_time, received_signal, sampling_rate, noise_dB, t_axis, dB = False, calc_freqs = False, calc_dists = False, dists = [], B =0, T =0):
    
    noise_signal = create_noise_signal(s_beats, measuring_time, noise_dB)
    s_with_noise = s_beats + noise_signal
    received_signal_with_noise = np.real(s_with_noise)

    padded_zero = zero_append(received_signal, 15536) ## padded to the next power of two cuz apperently that works best (does appear so)
    received_fft = fft.fft(padded_zero)
    power_spectrum = np.abs(received_fft)**2


    noise_padded_zero = zero_append(received_signal_with_noise, 15536) ## padded to the next power of two cuz apperently that works best (does appear so)
    noise_received_fft = fft.fft(noise_padded_zero)
    noise_power_spectrum = np.abs(noise_received_fft)**2

    max_db = max(np.max(power_spectrum), np.max(noise_power_spectrum))
    power_db = 10*np.log10(power_spectrum / max_db + 1e-12)
    noise_power_db = 10*np.log10(noise_power_spectrum / max_db + 1e-12)

    #plt.plot(t_axis, noise_signal )
    plt.plot(t_axis,received_signal)
    plt.plot(t_axis,received_signal_with_noise, alpha=0.3)
    plt.show()




    freq_axis = fft.fftfreq(len(power_spectrum), d=1/sampling_rate)
    range_axis = freq_axis * C * T / (2 * B)

    fig, ax1 = plt.subplots(figsize=(10,5))

    half = len(freq_axis)//2


    if dB:
        ax1.plot(range_axis[:half], power_db[:half])
        ax1.plot(range_axis[:half], noise_power_db[:half])
        ax1.set_ylabel("Power (dB)")
        ax1.set_ylim(-80, 1)

    else:
        ax1.plot(range_axis[:half], power_spectrum[:half])
        ax1.set_ylabel("Power (W)")


    if (calc_freqs == True):
        freqs = calc_expected_freqs(dists, B, T)
        for distance in dists:
            ax1.axvline(distance, ls="--", c="red")

    if (calc_dists == True):
        found_dists = recalc_dists_from_signal(noise_padded_zero, sampling_rate, B, T)


    ax1.set_xlim(0, 30)
    range_ticks = np.arange(0, 31, 5)
    ax1.set_xticks(range_ticks)
    ax1.set_xlabel("Range (m)")
    ax1.grid()

    ax2 = ax1.twiny()
    ax2.set_xlim(ax1.get_xlim())
    freq_ticks = 2 * B * range_ticks / (C * T)
    ax2.set_xticks(range_ticks)
    ax2.set_xticklabels([f"{f/1000:.0f}" for f in freq_ticks])
    ax2.set_xlabel("Frequency (kHz)")

    plt.title("FFT of Situation A")
    plt.show()


def task1():
    sampling_rate = 500e6
    measuring_time = 0.1e-3  ##start taking really long if larger than 0.001
    samples = measuring_time * sampling_rate
    t_axis = np.linspace(0, measuring_time, int(samples))
    s_beats, received_signal = create_tones(DISTS, t_axis)
    plot_time_domain(received_signal, t_axis)

    plot_power_spectra(received_signal, sampling_rate, 
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
    plot_time_domain(received_signal, t_axis)

    plot_power_spectra(received_signal, sampling_rate, 
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
    # print(s_beats)


    plot_power_spectra_with_noise (s_beats, measuring_time, received_signal, sampling_rate, snr_db, t_axis,
                       calc_freqs=True, calc_dists=True, dB = True,
                       dists=DISTS, B =200e6, T = 0.1e-3)
    return "Fuck you"

def task4():
    sampling_rate = 500e6
    measuring_time = 0.1e-2 ##start taking really long if larger than 0.001
    snr_db = 3 #(dB)
    k = 200

    samples = measuring_time*sampling_rate
    t_axis = np.linspace(0, measuring_time, int(samples))

    amplitudes = calc_amplitudes(DISTS, reference_0 = False)

    s_beats, received_signal = create_tones(DISTS, t_axis, amplitudes= amplitudes)
    #print(s_beats)

    s_average = np.zeros_like(s_beats)
    for i in range(k):
        print(i)
        noise_signal = create_noise_signal(s_beats, measuring_time, snr_db)
        s_with_noise = s_beats + noise_signal
        s_average = s_average + s_with_noise
    s_average = s_average # klopt
    received_signal_average = np.real(s_average)
    received_signal_average = zero_append(received_signal_average)

    plot_power_spectra(received_signal_average, sampling_rate, 
                       calc_freqs=True, calc_dists=True, dB = True,
                       dists=DISTS, B =200e6, T = 0.1e-3)
    return "Fuck you"

if __name__ == "__main__":
    #task1()
    #task2()
    task3()
    #task4()
    calc_expected_freqs([6.3], 200e6, 0.1e-3)

    print("Done")
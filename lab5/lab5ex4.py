import numpy as np
from scipy import fft
import matplotlib.pyplot as plt


DISTS = [5,8,12]
C = 3e8

def create_tones(dists, t, B = 200e6, T = 0.1e-3, amplitudes = []):
    all_S_beats = []

    for j in range(len(t)): ## for every time moment
        #print(t[j])
        S_beats = []
        if (amplitudes == []):
            for i, dist in enumerate(dists): ## calc the beats expected
                tau_n = 2*dist/C
                exponent = 1j*2*np.pi*(B/T)*t[j]*tau_n
                S_beat = np.real(np.exp(exponent))
                S_beats.append(S_beat)
        else:
            for i, dist in enumerate(dists):
                tau_n = 2*dist/C
                exponent = 1j*2*np.pi*(B/T)*t[j]*tau_n
                S_beat = np.real(np.exp(exponent))*amplitudes[i]
                S_beats.append(S_beat)
        all_S_beats.append(S_beats)
    

    received_signal = np.sum(all_S_beats, axis=1)

    return all_S_beats, received_signal

def calc_amplitudes(dists, reference_1 = 0):
    


def task1():
    sampling_rate = 500e6
    measuring_time = 0.01 ##start taking really long if larger than 0.001
    samples = measuring_time*sampling_rate
    t_axis = np.linspace(0, measuring_time, int(samples))
    s_beats, received_signal = create_tones(DISTS, t_axis)


    received_fft = fft.fft(received_signal)
    power_spectrum = np.abs(received_fft)**2
    power_db = 10*np.log10(power_spectrum)

    freq_axis = fft.fftfreq(len(power_spectrum), d=1/sampling_rate)

    plt.figure(figsize=(10,5))
    plt.plot(freq_axis[:len(freq_axis)//2],
            power_db[:len(power_db)//2])
    plt.xlim(0, 300e3)
    plt.xlabel("Frequency [Hz]")
    plt.ylabel("Power")
    plt.title("FFT of measured powers")
    plt.grid()
    plt.show()


    #print(s_beats)

def task2():
    sampling_rate = 500e6
    measuring_time = 0.001 ##start taking really long if larger than 0.001
    samples = measuring_time*sampling_rate
    t_axis = np.linspace(0, measuring_time, int(samples))

    amplitudes = calc_amplitudes()


    __, received_signal = create_tones(DISTS, t_axis)


    received_fft = fft.fft(received_signal)
    power_spectrum = np.abs(received_fft)**2
    power_db = 10*np.log10(power_spectrum)

    freq_axis = fft.fftfreq(len(power_spectrum), d=1/sampling_rate)

    plt.figure(figsize=(10,5))
    plt.plot(freq_axis[:len(freq_axis)//2],
            power_db[:len(power_db)//2])
    plt.xlim(0, 300e3)
    plt.xlabel("Frequency [Hz]")
    plt.ylabel("Power")
    plt.title("FFT of measured powers")
    plt.grid()
    plt.show()



if __name__ == "__main__":
    #task1()

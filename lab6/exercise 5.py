import scipy.io

from scipy import fft, signal

import numpy as np
from matplotlib import pyplot as plt

# import h5py
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


def find_peak_in_region(matrix, x_axis, y_axis, x_min, x_max, y_min, y_max):
    x_mask = (x_axis >= x_min) & (x_axis <= x_max)
    y_mask = (y_axis >= y_min) & (y_axis <= y_max)
    if not np.any(x_mask) or not np.any(y_mask):
        return None
    sub = matrix[np.ix_(y_mask, x_mask)]
    idx = np.argmax(sub)
    y_idx, x_idx = np.unravel_index(idx, sub.shape)
    value = sub[y_idx, x_idx]
    x_val = x_axis[x_mask][x_idx]
    y_val = y_axis[y_mask][y_idx]
    return value, x_val, y_val


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



def task1(do_task = True):
    SamplesPerChirp = T*F_SAMPLE
    TBetweenSamples = 1/F_SAMPLE
    ChirpsInFrame = FRAME_LENGTH/T
    Totalsamples = SamplesPerChirp * ChirpsInFrame
    
    if (do_task == True):
        print(f"The amount of samples per chirp is {int(SamplesPerChirp)}")
        print(f"The time between each sample is {TBetweenSamples*1e9} ns")
        print(f"The amount of chirps in one frame is {int(ChirpsInFrame)}")
        print(f"The amount of total samples in is {int(Totalsamples)}")

    RadarData = scipy.io.loadmat('Data file week6 highSNR.mat', mat_dtype = False)['s_beat_vector']
    RadarData = RadarData[:,0]

    RadarData = np.reshape(RadarData, (int(ChirpsInFrame), int(SamplesPerChirp)))
    #print(len(RadarData[0]))
    return RadarData


def task2(RadarData):
    t = np.arange(len(RadarData[0])) / F_SAMPLE
    f1, f2 = 4e4*20/3, 4e4*100/3
    delay_guess = 1.56e-6 # 1.56 micro seconds
    predicted_signal = np.exp(-2j*np.pi*f1*(t - delay_guess)) + np.exp(-2j*np.pi*f2*(t - delay_guess))
    plt.subplot(2,1,1)
    plt.plot(t, np.real(RadarData[0]), label="Real part")
    plt.plot(t, np.real(predicted_signal), label="Predicted signal (real part)", linestyle='dashed')
    plt.title("Real and Imaginary part of the first chirp")
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    plt.legend()
    plt.grid()

    plt.subplot(2,1,2)
    plt.plot(t, np.imag(RadarData[0]), label="Imaginary part")
    plt.plot(t, np.imag(predicted_signal), label="Predicted signal (imaginary part)", linestyle='dashed')
    plt.title("Real and Imaginary part of the first chirp")
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    plt.legend()
    plt.grid()
    plt.tight_layout()
    plt.show()

    N_fft = 2**(3 + int(np.ceil(np.log2(len(RadarData[0])))))
    FFT_RadarData = np.fft.fft(RadarData[0], n=N_fft)
    FFT_RadarData = np.abs(FFT_RadarData)
    FFT_RadarData = FFT_RadarData/np.max(FFT_RadarData)
    FFT_RadarData_dB = 20*np.log10(FFT_RadarData)
    
    freq_axis = fft.fftfreq(N_fft, d=1/F_SAMPLE)
    freq_axis_shifted = np.fft.fftshift(freq_axis)
    FFT_shifted = np.fft.fftshift(FFT_RadarData_dB)
    
    range_axis = -freq_axis_shifted * C * T / (2 * B)
    plt.plot(range_axis, FFT_shifted)
    plt.xlabel("Range (m)")
    plt.ylabel("Power (dB)")
    plt.title("FFT of the first chirp")
    plt.xlim(0, 150)
    plt.ylim(-50, 0)
    plt.grid()
    plt.show()

    # 2D range-time plot: one vertical column per chirp
    N_fft_2d = 2**(3 + int(np.ceil(np.log2(RadarData.shape[1]))))
    spectra = np.fft.fft(RadarData, n=N_fft_2d, axis=1)
    spectra = np.abs(spectra)
    spectra = spectra / np.max(spectra, axis=1, keepdims=True)
    spectra_db = 20 * np.log10(spectra + 1e-12)

    spectra_shifted = np.fft.fftshift(spectra_db, axes=1)
    half = N_fft_2d // 2
    spectra_half = spectra_shifted[:, :half]
    spectra_half = spectra_half[:, ::-1] #flip so that the negative range is resolved

    freq_axis_2d = np.fft.fftfreq(N_fft_2d, d=1/F_SAMPLE)
    freq_axis_shifted = np.fft.fftshift(freq_axis_2d)
    range_axis_2d = -freq_axis_shifted[:half][::-1] * C * T / (2 * B)
    time_axis = np.arange(RadarData.shape[0]) * T

    fig, ax = plt.subplots(figsize=(10, 6))
    im = ax.imshow(
        spectra_half.T,
        origin='lower',
        aspect='auto',
        extent=[time_axis[0], time_axis[-1], range_axis_2d[0], range_axis_2d[-1]],
        cmap='magma',
        vmin=-80,
        vmax=0
    )
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Range (m)')
    ax.set_title('Range-time intensity from per-chirp FFT')
    fig.colorbar(im, label='Power (dB)')
    plt.ylim(0, 150)
    plt.savefig("plots/exercise5_range_time.png", dpi=600)
    plt.show()





def task3(RadarData):
    # Range-Doppler processing: FFT across fast time for range, then FFT across slow time for Doppler.
    n_chirps, n_samples = RadarData.shape
    n_range = 2**(3 + int(np.ceil(np.log2(n_samples))))
    n_doppler = 2**(int(np.ceil(np.log2(n_chirps))))

    # Fast-time FFT per chirp -> range bins
    range_fft = np.fft.fft(RadarData, n=n_range, axis=1)
    
    # Use negative frequency half (like task2 does)
    range_fft_shifted = np.fft.fftshift(range_fft, axes=1)
    half = n_range // 2
    range_fft_half = range_fft_shifted[:, :half]
    range_fft_half = range_fft_half[:, ::-1]  # Flip to get correct range order

    # Slow-time FFT per range bin -> Doppler bins
    rd_matrix = np.fft.fft(range_fft_half, n=n_doppler, axis=0)
    rd_matrix = np.fft.fftshift(rd_matrix, axes=0)

    rd_mag = np.abs(rd_matrix)
    rd_mag /= np.max(rd_mag + 1e-12)
    rd_db = 20 * np.log10(rd_mag + 1e-12)

    # Range axis: use negative frequency half mapped to positive range
    freq_range = np.fft.fftfreq(n_range, d=1 / F_SAMPLE)
    freq_range_shifted = np.fft.fftshift(freq_range)
    range_axis = -freq_range_shifted[:half][::-1] * C * T / (2 * B)

    # Doppler axis across slow time (chirp-to-chirp), centered at 0
    doppler_freq = np.fft.fftfreq(n_doppler, d=T)
    doppler_freq = np.fft.fftshift(doppler_freq)

    rd_db_plot = rd_db.T
    peak1 = find_peak_in_region(rd_db_plot, doppler_freq, range_axis, 70, 220, 90, 110)
    peak2 = find_peak_in_region(rd_db_plot, doppler_freq, range_axis, -620, -460, 10, 30)
    if peak1 is not None:
        print(f"Task3 peak 1: value={peak1[0]:.2f} dB at range={peak1[2]:.2f} m, doppler={peak1[1]:.2f} Hz")
    else:
        print("Task3 peak 1: no bins found in the specified region")
    if peak2 is not None:
        print(f"Task3 peak 2: value={peak2[0]:.2f} dB at range={peak2[2]:.2f} m, doppler={peak2[1]:.2f} Hz")
    else:
        print("Task3 peak 2: no bins found in the specified region")

    fig, ax = plt.subplots(figsize=(12, 6))
    im = ax.imshow(
        rd_db.T,
        origin='lower',
        aspect='auto',
        extent=[doppler_freq[0], doppler_freq[-1], range_axis[0], range_axis[-1]],
        cmap='magma',
        vmin=-80,
        vmax=0,
    )
    ax.set_xlabel('Doppler Frequency (Hz)')
    ax.set_ylabel('Range (m)')
    ax.set_title('Range-Doppler matrix')
    fig.colorbar(im, label='Power (dB)')
    plt.tight_layout()
    plt.ylim(0, 150)
    plt.xlim(-800, 800)
    plt.savefig("plots/exercise5_range_doppler.png", dpi=600)
    plt.show()
    return


def task4(RadarData):
    # Range-Doppler processing: FFT across fast time for range, then FFT across slow time for Doppler.
    n_chirps, n_samples = RadarData.shape
    n_range = 2**(3 + int(np.ceil(np.log2(n_samples))))
    n_doppler = 2**(int(np.ceil(np.log2(n_chirps))))

    # Fast-time FFT per chirp -> range bins
    range_fft = np.fft.fft(RadarData, n=n_range, axis=1)
    
    # Use negative frequency half (like task2 does)
    range_fft_shifted = np.fft.fftshift(range_fft, axes=1)
    half = n_range // 2
    range_fft_half = range_fft_shifted[:, :half]
    range_fft_half = range_fft_half[:, ::-1]  # Flip to get correct range order

    # Slow-time FFT per range bin -> Doppler bins
    rd_matrix = np.fft.fft(range_fft_half, n=n_doppler, axis=0)
    rd_matrix = np.fft.fftshift(rd_matrix, axes=0)

    rd_mag = np.abs(rd_matrix)
    rd_mag /= np.max(rd_mag + 1e-12)
    rd_db = 20 * np.log10(rd_mag + 1e-12)

    # Range axis: use negative frequency half mapped to positive range
    freq_range = np.fft.fftfreq(n_range, d=1 / F_SAMPLE)
    freq_range_shifted = np.fft.fftshift(freq_range)
    range_axis = -freq_range_shifted[:half][::-1] * C * T / (2 * B)

    # Doppler axis across slow time (chirp-to-chirp), centered at 0
    doppler_freq = np.fft.fftfreq(n_doppler, d=T)
    doppler_freq = np.fft.fftshift(doppler_freq)
    velocity_axis = C * doppler_freq / (2 * F_CARRIER)

    rd_db_plot = rd_db.T
    peak1 = find_peak_in_region(rd_db_plot, velocity_axis, range_axis, 5, 15, 90, 110)
    peak2 = find_peak_in_region(rd_db_plot, velocity_axis, range_axis, -50, -30, 10, 30)
    if peak1 is not None:
        print(f"Task4 peak 1: value={peak1[0]:.2f} dB at range={peak1[2]:.2f} m, velocity={peak1[1]:.2f} m/s")
    else:
        print("Task4 peak 1: no bins found in the specified region")
    if peak2 is not None:
        print(f"Task4 peak 2: value={peak2[0]:.2f} dB at range={peak2[2]:.2f} m, velocity={peak2[1]:.2f} m/s")
    else:
        print("Task4 peak 2: no bins found in the specified region")

    fig, ax = plt.subplots(figsize=(12, 6))
    im = ax.imshow(
        rd_db.T,
        origin='lower',
        aspect='auto',
        extent=[velocity_axis[0], velocity_axis[-1], range_axis[0], range_axis[-1]],
        cmap='magma',
        vmin=-80,
        vmax=0,
    )
    ax.set_xlabel('Velocity (m/s)')
    ax.set_ylabel('Range (m)')
    ax.set_title('Range-Velocity matrix')
    fig.colorbar(im, label='Power (dB)')
    plt.tight_layout()
    plt.ylim(0, 150)
    plt.savefig("plots/exercise5_range_velocity.png", dpi=600)
    plt.show()
    return


if __name__ == "__main__":
    RadarData = task1(do_task=False)
    #task2(RadarData)
    #task3(RadarData)
    task4(RadarData)
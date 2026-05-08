#afstand is 1.43
#distance between patches (middle to middle):
# a = 6.8 cm
# 
# c = 10.4 cm
#
import numpy as np
import skrf as rf
import matplotlib.pyplot as plt
Z0 = 50
C = 3e8
R = 1,43
#task1



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


def calc_impedance(S_param): ##patch was aangesloten aan aansluiting 2
  z = Z0*(1+S_param)/(1-S_param)
  return z

def calculate_minusdB_bandwidth(freq, s11_db, threshold=-10):
    valid_indices = np.where(s11_db <= threshold)[0]

    if len(valid_indices) == 0:
        return 0.0

    min_freq = freq[valid_indices[0]]
    max_freq = freq[valid_indices[-1]]

    return max_freq - min_freq

def calc_bandwith(Z_ant, freq):
  gamma_ant = (Z_ant - Z0) / (Z_ant + Z0)
  db_gamma = 10*np.log10(gamma_ant)
  bandwith = calculate_minusdB_bandwidth(freq, db_gamma, -10)
  return bandwith

def get_horn_gain():
    freq, S11, S21, S12, S22 = readout_s2p("measurements/Practicum2-1.38m/0.s2p")

    c0 = 3e8


    r = 1.38 # 1, 0.5
    lambd = c0/freq

    gain = np.abs(S21)*4*np.pi*r/lambd

    return freq, gain

def patch_gain_from_S21(freq, S21):
    abssquare = np.abs(S21)**2

    freq_horn, gain_horn = get_horn_gain()
    if (freq == freq_horn): print("freqs_match")
    else: print('freqs dont match so fix that code')
    lambda0 = C/freq
    gain_patch = abssquare*(4*np.pi*R)**2/(gain_horn*lambda0**2)

    plt.plot(freq/1e9,10*np.log10(gain_patch))
    plt.xlabel("Freq (GHz)")
    plt.ylabel("Gain (dB)")
    plt.title("Gain per frequency")
    plt.grid()

    plt.show()
    plt.savefig("lab3/plots/patchgain.png", dpi=500)
    return gain_patch


def get_beamwidth(pattern,theta):
    power = pattern**2
    ind_above_halfpower = np.where(power>0.5)[0]
    splits = np.where(np.diff(ind_above_halfpower) !=1)[0] + 1
    groups = np.split(ind_above_halfpower,splits)

    middlebeam = groups[floor(len(groups)/2)]

    bw = theta[middlebeam[-1]]-theta[middlebeam[0]]
    bw = np.rad2deg(bw)
    
    return(bw)

def patch_antenna(L,W,THETA,PHI):
    vx = (L/lambd) * np.sin(THETA) * np.cos(PHI)
    vy = (W/lambd) * np.sin(THETA) * np.sin(PHI)

    f = np.cos(vx*np.pi) * np.sinc(vy)

    pattern = (np.cos(THETA)**2 * np.sin(PHI)**2 + np.cos(PHI)**2) * np.abs(f)**2

    pattern_norm = pattern/np.max(pattern)
    
    
    return(pattern_norm)

def get_theo_directivity(pattern_norm):
    total_norm = pattern_norm * AF_norm

    theta = np.linspace(0, np.pi, 1000)
    phi = np.linspace(-np.pi, np.pi, 1000)

    total_zerophi = AF_zerophi[::10] * pattern_zerophi
    total_90phi = AF_90phi[::10] * pattern_90phi



    bwzero = get_beamwidth(total_zerophi,theta)
    bw90 = get_beamwidth(total_90phi,theta)

    #calc directivity
    D = 4*np.pi*(180/np.pi)**2 / (bwzero*bw90)

    return D ##### moet nog af

def compare(gain, D):
   efficiency = gain/D
   print(f"The efficiency is equal to {efficiency}")
   return efficiency

def array_plotter(op_frequencie, symtrec = True):

    p =[]

    if(symtrec):
        for i in range(46):
            # print(i)
            freq, S11, S21, S12, S22 = readout_s2p(f'{i*2}') #get correct name
            index = np.where(freq == op_frequencie) ##operating frequency
            #find correct indexis


            db = 10*np.log10(np.abs(S21)**2)

            if(i==0):
                p.append(db[index])
            else:
                p.append(db[index])
                p.insert(0, db[index])
    else: 
        for i in range(91):

            # print(i)
            freq, S11, S21, S12, S22 = readout_s2p(f'{(i-45)*2}') #get correct name
            index = np.where(freq == op_frequencie) ##operating frequency
            #find correct indexis

            db = 10*np.log10(np.abs(S21)**2)
            p.append(db[index])
    
    angles = np.linspace(-90, 90, 91)
    plt.plot(angles, p, label='15 GHz')
    plt.title("S21 parameter vs angle")
    plt.grid()
    plt.xlabel("angle (degrees)")
    plt.ylabel("Magnitude (dB)")
    plt.legend()
    plt.savefig("lab3/plots/powerplot.png")
    plt.show()

    indexmax = np.where(p == np.max(p))
    anglemax = angles[indexmax]
    print(f"the max angle is {anglemax}")




#S11**2 = p_ref/p_in
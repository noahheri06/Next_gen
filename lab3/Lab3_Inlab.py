#afstand is 1.43
#distance between patches (middle to middle):
# a = 6.8 cm
# 
# c = 10.4 cm
# d = 21.7 cm
import numpy as np
import skrf as rf
import matplotlib.pyplot as plt


Z0 = 50
C = 3e8
R = 1,43
#task1



def readout_s2p(your_file):

  ntwk = rf.Network(f'measurements/{your_file}.s2p')

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


def calc_op_bandwidth(freq,s11_db,threshold=-10):
    ind_above_10 = np.where(s11_db >= threshold)[0]

    lower_max = len(freq)/4
    upper_min = len(freq)/2
    # lower bound
    lower_ind = np.max(ind_above_10[np.where(ind_above_10 < lower_max)[0]])
    upper_ind = np.min(ind_above_10[np.where(ind_above_10 > upper_min)[0]])
    
    
    min_freq = freq[lower_ind]
    max_freq = freq[upper_ind]
    
    
    return(max_freq - min_freq)


def calc_bandwith(Z_ant, freq):
  gamma_ant = (Z_ant - Z0) / (Z_ant + Z0)
  db_gamma = 10*np.log10(gamma_ant)
  bandwith = calculate_minusdB_bandwidth(freq, db_gamma, -10)
  return bandwith

def get_horn_gain():
    freq, S11, S21, S12, S22 = readout_s2p("Practicum2-1.38m/0")

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


# def get_beamwidth(pattern,theta):
#     power = pattern**2
#     ind_above_halfpower = np.where(power>0.5)[0]
#     splits = np.where(np.diff(ind_above_halfpower) !=1)[0] + 1
#     groups = np.split(ind_above_halfpower,splits)

#     middlebeam = groups[floor(len(groups)/2)]

#     bw = theta[middlebeam[-1]]-theta[middlebeam[0]]
#     bw = np.rad2deg(bw)
    
#     return(bw)

# def patch_antenna(L,W,THETA,PHI):
#     vx = (L/lambd) * np.sin(THETA) * np.cos(PHI)
#     vy = (W/lambd) * np.sin(THETA) * np.sin(PHI)

#     f = np.cos(vx*np.pi) * np.sinc(vy)

#     pattern = (np.cos(THETA)**2 * np.sin(PHI)**2 + np.cos(PHI)**2) * np.abs(f)**2

#     pattern_norm = pattern/np.max(pattern)
    
    
#     return(pattern_norm)

# def get_theo_directivity(pattern_norm):
#     total_norm = pattern_norm * AF_norm

#     theta = np.linspace(0, np.pi, 1000)
#     phi = np.linspace(-np.pi, np.pi, 1000)

#     total_zerophi = AF_zerophi[::10] * pattern_zerophi
#     total_90phi = AF_90phi[::10] * pattern_90phi



#     bwzero = get_beamwidth(total_zerophi,theta)
#     bw90 = get_beamwidth(total_90phi,theta)

#     #calc directivity
#     D = 4*np.pi*(180/np.pi)**2 / (bwzero*bw90)

#     return D ##### moet nog af

def compare(gain, D):
   efficiency = gain/D
   print(f"The efficiency is equal to {efficiency}")
   return efficiency

def array_plotter(op_frequencie, array_name, symtrec = True):
    fig, ax = plt.subplots(1, 1)
    p =[]

    if(symtrec):
        for i in range(36):
            # print(i)
            freq, S11, S21, S12, S22 = readout_s2p(f'{array_name}{i*2}') #get correct name
            index = np.where(freq == op_frequencie) ##operating frequency
            #find correct indexis


            db = 10*np.log10(np.abs(S21)**2)

            if(i==0):
                p.append(db[index])
            else:
                p.append(db[index])
                p.insert(0, db[index])
    else: 
        for i in range(71):

            # print(i)
            freq, S11, S21, S12, S22 = readout_s2p(f'1x8ap{(i-35)*2}') #get correct name
            index = np.where(freq == op_frequencie) ##operating frequency
            #find correct indexis

            db = 10*np.log10(np.abs(S21)**2)
            p.append(db[index])
    
    angles = np.linspace(-70, 70, 71)
    ax.plot(angles, p, label='15 GHz')
    ax.set_title(f"{array_name} radiation pattern")
    ax.grid()
    ax.set_xlabel("angle (degrees)")
    ax.set_ylabel("Magnitude (dB)")
    plt.legend()
    #plt.savefig("lab3/plots/powerplot.png")
    plt.show()

    indexmax = np.where(p == np.max(p))[0]
    anglemax = angles[indexmax]
    print(f"the max angle is {anglemax}")


#array_plotter(15e9, False)

#S11**2 = p_ref/p_in





# =============================================================================
# TASK 1,2,3
# =============================================================================

# only antenna facing directly to horn antenna

antarrays = ["1x1patch","1x2patch","1x4patch","1x8patcha"]

fig, axs = plt.subplots(2, 2)
#fig.tight_layout()
plt.subplots_adjust(top=0.95,bottom=0.1,wspace=0.4,hspace=0.4)
for i, antenna in zip(list(range(len(antarrays))),antarrays):
    x = i//2
    y= i % 2
    ax = axs[x,y]
    
    freq, S11, S21, S12, S22 = readout_s2p(antenna)
    
    S11 = np.abs(S11)
    
    imp = calc_impedance(S11)
    
    
    S11_dB = 10*np.log10(S11)
    

    ax2 = ax.twinx()
    ax.set_title(f"{antenna[:3]} array reflection and impedance")
    ax.plot(freq/1e9,S11_dB,label="Reflection coefficient",color="orange")
    ax2.plot(freq/1e9,imp,label="Impedance",color="blue")
    
    ax.set_xlabel("Frequency (GHz)")
    ax.set_ylabel("Gain (dB)")
    ax2.set_ylabel("Impedance ($\Omega$)")
    ax.grid()
    ax.legend(loc=2, prop={'size': 15})
    ax2.legend(loc=1, prop={'size': 15})
    plt.show()
    
    op_bandwidth = calc_op_bandwidth(freq,S11_dB)/1e9
    print(f"The operational bandwidth of the {antenna} array is {op_bandwidth} GHz")
    
    
    
    #%%
# =============================================================================
# TASK 4,5,6
# =============================================================================

# again only one direction is needed

antarrays = ["1x1patch","1x2patch","1x4patch","1x8patcha"]


# plot received power (based on S21)

fig, axs = plt.subplots(2, 2)
#fig.tight_layout()
plt.subplots_adjust(top=0.95,bottom=0.1,wspace=0.4,hspace=0.4)
for i, antenna in zip(list(range(len(antarrays))),antarrays):
    x = i//2
    y= i % 2
    ax = axs[x,y]
    
    freq, S11, S21, S12, S22 = readout_s2p(antenna)
    
    S21 = np.abs(S21)
    
    power = S21**2

    
    power_dB = 10*np.log10(power)
    
    
    ax.set_title(f"{antenna[:3]} array received power")
    ax.plot(freq/1e9,power_dB,label="Received power")
    
    
    
    ax.set_xlabel("Frequency (GHz)")
    ax.set_ylabel("Gain (dB)")
    ax.grid()
    #ax.legend(loc=2, prop={'size': 15})
    plt.show()



fig, axs = plt.subplots(2, 2)
#fig.tight_layout()
plt.subplots_adjust(top=0.95,bottom=0.1,wspace=0.4,hspace=0.4)
for i, antenna in zip(list(range(len(antarrays))),antarrays):
    x = i//2
    y= i % 2
    ax = axs[x,y]
    
    freq, S11, S21, S12, S22 = readout_s2p(antenna)
    
   
    
    c0 = 3e8

    r = 1.38 # 1, 0.5
    lambd = c0/freq
    
    total_gain = np.abs(S21)**2 * (4*np.pi*r/lambd)**2
    _, horn_gain = get_horn_gain()
    array_gain = total_gain/horn_gain
    
    array_gain_dB = 10*np.log10(array_gain)
    
    #ax2 = ax.twinx()

    ax.set_title(f"{antenna[:3]} array and horn antenna")
    ax.plot(freq/1e9,array_gain_dB,label="Array gain")
    # ax.plot(freq/1e9,10*np.log10(horn_gain),label="Horn",color="orange")
    # ax.plot(freq/1e9,10*np.log10(total_gain),label="Total", color="red")
    
    ax.set_xlabel("Frequency (GHz)")
    ax.set_ylabel("Gain (dB)")
    ax.grid()
    ax.legend(loc=2, prop={'size': 15})
    plt.show()
    
    
    
    # efficiency calc at 15 GHz

    ind_15GHz = np.where(freq==15e9)[0][0]
    
    array_gain_15GHz = array_gain[ind_15GHz]
    
    print(f"Gain at 15 GHz: {10*np.log10(array_gain_15GHz)} dB")
    
    

    






#%%

# =============================================================================
# task 7
# =============================================================================










antennas = ["1x8a","1x8ap","1x8b","1x8c","1x8d"]


for antenna in antennas:
    
    if antenna=="1x8ap":
        array_plotter(15e9,antenna,symtrec=False)
    else:
        array_plotter(15e9,antenna,symtrec=True)
    
















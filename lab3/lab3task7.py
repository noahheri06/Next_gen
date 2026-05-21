antennas = ["1x8a","1x8ap","1x8b","1x8c","1x8d"]

import numpy as np
import skrf as rf
import matplotlib.pyplot as plt


Z0 = 50
C = 3e8
R = 1.43

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


def gain(l, w, freq, phi, theta):
    lambda0 = C/freq
    theta = [theta]
    phi = [phi]
    for i in range(len(theta)):
        for j in range(len(phi)):
            v_y = (w/lambda0)*np.sin(theta[i])*np.sin(phi[j])
            if v_y == 0:
                v_y = 1e-10
            v_x = (l/lambda0)*np.sin(theta[i])*np.cos(phi[j])
            F_theta_phi = np.cos(np.pi*v_x)*np.sin(np.pi*v_y)/(np.pi*v_y)
            g_theta_phi = ((np.cos(theta[i])*np.sin(phi[j]))**2 + (np.cos(phi[j])**2))*F_theta_phi**2
            g = g_theta_phi
            print(g)
    return (g)

def array_plotter_correct_for_theo(fig, ax,op_frequencie, array_name, symtrec = True):
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

    gain_at_angles = []
    
    for i in range(71):
        gain_at_angle = gain(5e-3, 6.5e-3, 15e9, np.deg2rad(angles[i]), np.pi/2)
        print(gain_at_angle)
        gain_angle_db = 10*np.log10(gain_at_angle)
        gain_at_angles.append(gain_angle_db)
        p[i] = p[i] - gain_angle_db



    ax.plot(angles, p, label='15 GHz')
    ax.set_title(f"{array_name} radiation pattern")
    ax.grid()
    ax.set_xlabel("angle (degrees)")
    ax.set_ylabel("Magnitude (dB)")
    #plt.legend()
    #plt.savefig("lab3/plots/powerplot.png")
    plt.show()

    indexmax = np.where(p == np.max(p))[0]
    anglemax = angles[indexmax]
    print(f"the max angle is {anglemax}")


        
        
antennas = ["1x8a","1x8ap","1x8b","1x8c","1x8d"]
antennas = ["1x8a","1x8b","1x8c","1x8d"]
antennas = ["1x8ap"]
fig, axs = plt.subplots(1, 1)
#fig.tight_layout()
plt.subplots_adjust(top=0.95,bottom=0.1,wspace=0.4,hspace=0.4)

for i, antenna in zip(list(range(len(antennas))),antennas):
    x = i//2
    y= i % 2
    ax = axs
    
    
    
    if antenna=="1x8ap":
        array_plotter_correct_for_theo(fig,ax,15e9,antenna,symtrec=False)
    else:
        array_plotter_correct_for_theo(fig,ax,15e9,antenna,symtrec=True)
    
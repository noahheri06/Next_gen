import numpy as np
import matplotlib.pyplot as plt
from math import floor

C = 2.99e8
resonant_freq = 15e9
substrate_thickness = 0.5e-3
epsilon_r = 3.66
def find_L_W(fr, er, h):
    w = C/(2*fr*np.sqrt((er+1)/2))
    epsilon_eff = (er+1)/2 + (er-1)/(2*np.sqrt(1+12*h/w))
    L_eff = C/(2*fr*np.sqrt(epsilon_eff))
    print(epsilon_eff, L_eff)
    delta_L = (0.412*h*(epsilon_eff+0.3)*(w/h+0.264))/((epsilon_eff-0.258)*(w/h+0.8))
    l = L_eff - 2*delta_L
    print(f"Found W and L are: W = {w*1000} mm, L = {l*1000} mm")
    return (l, w)


test_frequencies = [14e9, 15e9, 16e9]

def gain(l, w, freq, phi, theta):
    lambda0 = C/freq


    g = np.zeros((len(theta), len(phi)))
    for i in range(len(theta)):
        for j in range(len(phi)):
            v_y = (w/lambda0)*np.sin(theta[i])*np.sin(phi[j])
            if v_y == 0:
                v_y = 1e-10
            v_x = (l/lambda0)*np.sin(theta[i])*np.cos(phi[j])
            F_theta_phi = np.cos(np.pi*v_x)*np.sin(np.pi*v_y)/(np.pi*v_y)
            g_theta_phi = ((np.cos(theta[i])*np.sin(phi[j]))**2 + (np.cos(phi[j])**2))*F_theta_phi**2
            g[i][j] = g_theta_phi
    return (g)

def interp_array(N1):  # add interpolated rows and columns to array
    N2 = np.empty([int(N1.shape[0]), int(2*N1.shape[1] - 1)])  # insert interpolated columns
    N2[:, 0] = N1[:, 0]  # original column
    for k in range(N1.shape[1] - 1):  # loop through columns
        N2[:, 2*k+1] = np.mean(N1[:, [k, k + 1]], axis=1)  # interpolated column
        N2[:, 2*k+2] = N1[:, k+1]  # original column
    N3 = np.empty([int(2*N2.shape[0]-1), int(N2.shape[1])])  # insert interpolated columns
    N3[0] = N2[0]  # original row
    for k in range(N2.shape[0] - 1):  # loop through rows
        N3[2*k+1] = np.mean(N2[[k, k + 1]], axis=0)  # interpolated row
        N3[2*k+2] = N2[k+1]  # original row
    return N3

def plot_gain(phi, theta, gain):

    c_sens = 15 ## colour sensitivty, lower has higher contrast
    len_t = len(theta)
    len_p = len(phi)

    X = np.zeros((len(theta), len(phi)))
    Y = np.zeros((len(theta), len(phi)))
    Z = np.zeros((len(theta), len(phi)))
    for i in range(len_t):
        for j in range(len_p):
            X[i][j] = gain[i][j] * np.sin(theta[i]) * np.cos(phi[j])
            Y[i][j] = gain[i][j] * np.sin(theta[i]) * np.sin(phi[j])
            Z[i][j] = gain[i][j] * np.cos(theta[i])



    gain_dB = 10*np.log10(gain)
    gain_dB = np.clip(gain_dB, -c_sens, 0)


    fig = plt.figure(figsize=(8,8))
    ax = fig.add_subplot(111, projection='3d')

    surf = ax.plot_surface(
        X, Y, Z,
        facecolors=plt.cm.jet((gain_dB + c_sens)/c_sens))

    # ax.axes.set_xlim3d(left=-1, right=1) 
    # ax.axes.set_ylim3d(bottom=-1, top=1) 
    # ax.axes.set_zlim3d(bottom=-1, top=1)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

    plt.show()

def plot_gain_slice(phi, phi_angle, theta, gain):
    index = np.where(phi >= phi_angle)
    gains = gain[:, index[0][0]]
    # print(f"gains {gains}")
    plt.plot(theta, gains)
    plt.show()


    return

def directivity_plot(phi, theta, gain):

    dtheta = theta[1] - theta[0]
    dphi = phi[1] - phi[0]

    total_power = 0

    for i in range(len(theta)):
        for j in range(len(phi)):
            total_power += gain[i,j] * np.sin(theta[i]) * dtheta * dphi

    D = 4*np.pi * gain / total_power
    plot_gain(phi, theta, D)


def plot_2d_cuts(pat_zerophi,pat_90phi,theta):
  
    pat_zerophi_dB = 20*np.log10(pat_zerophi)
    pat_90phi_dB = 20*np.log10(pat_90phi)

    fig = plt.figure()
    ax = fig.add_subplot()

    ax.plot(np.rad2deg(theta),pat_zerophi_dB,label="$\phi$ = 0$\degree$")
    ax.plot(np.rad2deg(theta),pat_90phi_dB,label="$\phi$ = 90$\degree$")

    ax.set_ylim(-70,5)
    ax.set_xlabel("$\\theta$ (deg)")
    ax.set_ylabel("normalized AF (dB)")
        

    ax.legend()
    plt.grid()
    plt.show()
    
    return(fig,ax)



def plot_2d_cuts_side_by_side(l, w, frequencies, phi, theta):

    fig, axs = plt.subplots(1, 3, figsize=(15, 4), sharey=True)

    for k, freq in enumerate(frequencies):

        g = gain(l, w, freq, phi, theta)

        index_phi0 = np.argmin(np.abs(phi - 0))
        index_phi90 = np.argmin(np.abs(phi - np.pi/2))

        pat_zerophi = g[:, index_phi0]
        pat_90phi = g[:, index_phi90]

        # Normalize
        pat_zerophi = pat_zerophi / np.max(pat_zerophi)
        pat_90phi = pat_90phi / np.max(pat_90phi)

        # Convert to dB
        pat_zerophi_dB = 10 * np.log10(pat_zerophi)
        pat_90phi_dB = 10 * np.log10(pat_90phi)

        axs[k].plot(np.rad2deg(theta), pat_zerophi_dB, label=r"$\phi = 0^\circ$")
        axs[k].plot(np.rad2deg(theta), pat_90phi_dB, label=r"$\phi = 90^\circ$")

        axs[k].set_title(f"Radiation pattern at {freq/1e9:.0f} GHz")
        axs[k].set_xlabel(r"$\theta$ (deg)")
        axs[k].set_ylim(-40, 5)
        axs[k].grid(True)
        axs[k].legend()

    axs[0].set_ylabel("Normalized gain (dB)")

    plt.tight_layout()
    plt.show()

def get_beamwidth(pattern,theta):
    power = pattern**2
    ind_above_halfpower = np.where(power>0.5)[0]
    splits = np.where(np.diff(ind_above_halfpower) !=1)[0] + 1
    groups = np.split(ind_above_halfpower,splits)
    
    if len(groups)==0:
        print("NO GROUPS FOUND, BEAMWIDTH IMPOSSIBLE")
        return(360)
    
    middlebeam = groups[floor(len(groups)/2)]
    if len(middlebeam)<=1:
        print("NO MIDDLEBEAM FOUND, BEAMWIDTH IMPOSSIBLE")
        return(360)

    bw = theta[middlebeam[-1]]-theta[middlebeam[0]]
    bw = np.rad2deg(bw)
    
    return(bw)


# if __name__ == "__main__":
#     l, w = find_L_W(resonant_freq, epsilon_r, substrate_thickness)
#     phi = np.linspace(0,2*np.pi, 300)
#     theta = np.linspace(0, 0.5*np.pi, 300)
#     g_theta_phi = gain(l, w, 15e9, phi, theta)
#     # print(g_theta_phi)
#     plot_gain(phi, theta, g_theta_phi)
#     # plot_gain_slice(phi, 0, theta, g_theta_phi)
#     # plot_gain_slice(phi, np.pi/4, theta, g_theta_phi)
#     directivity_plot(phi, theta, g_theta_phi)

if __name__ == "__main__":

    l, w = find_L_W(resonant_freq, epsilon_r, substrate_thickness)
    R_Rad = 90*((epsilon_r**2)/(epsilon_r-1))*((l/w)**2)
    print(f'R_rad = {R_Rad}')
    BW = 3.77*((epsilon_r-1)/epsilon_r**2)*(w/l)*((substrate_thickness*15e9)/C)
    print(f'BW = {BW}')
    phi = np.linspace(0, 2*np.pi, 300)
    theta = np.linspace(-0.5*np.pi, 0.5*np.pi, 300)

    plot_2d_cuts_side_by_side(l, w, test_frequencies, phi, theta)

    g = gain(l, w, 15e9, phi, theta)

    index_phi0 = np.argmin(np.abs(phi - 0))
    index_phi90 = np.argmin(np.abs(phi - np.pi/2))

    pattern_phi0 = g[:, index_phi0]
    pattern_phi90 = g[:, index_phi90]

    bw_phi0 = get_beamwidth(pattern_phi0, theta)
    bw_phi90 = get_beamwidth(pattern_phi90, theta)

    d = 4*np.pi/(np.deg2rad(bw_phi0)*np.deg2rad(bw_phi90))
    d_db = 10*np.log10(d)
    print(f"Beamwidth at phi = 0°  : {bw_phi0:.2f} degrees")
    print(f"Beamwidth at phi = 90° : {bw_phi90:.2f} degrees")
    print(f'D = {d} or {d_db} dBi')
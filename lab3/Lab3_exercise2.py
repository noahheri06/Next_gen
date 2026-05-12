import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from math import floor
from scipy.signal import find_peaks

c=3e8
f = 15e9
lambd = c/f
k0 = 2*np.pi/lambd

dy = lambd/2


LOW_RES = 2000
HIGH_RES = 10000


# =============================================================================
# 3D Plot
# =============================================================================

def plot_pattern3D(pattern,THETA,PHI,title=""):
    
    R = pattern

    X = R * np.sin(THETA)*np.cos(PHI)
    Y = R * np.sin(THETA)*np.sin(PHI)
    Z = R * np.cos(THETA)

    
    
    c_sens = 15
    pat_dB = 10*np.log10(pattern)
    colors = cm.jet((pat_dB + c_sens)/c_sens)
    
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')

    ax.plot_surface(X,Y,Z, facecolors = colors, edgecolor="none", antialiased=True)

    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")
    ax.set_xlim(-1.01,1.01)
    ax.set_ylim(-1.01,1.01)
    ax.set_zlim(0,2.02)
    
    ax.set_title(title)

    plt.grid()
    plt.show()




def array_factor(dy,dx,PHI,THETA,N,M=1,resolution=LOW_RES):
    
    AF = np.zeros(np.shape(THETA))

    # ARRAY
    for m in range(M):
        for n in range(N):
        
            kvect = k0*np.array([np.sin(THETA)*np.cos(PHI), np.sin(THETA)*np.sin(PHI), np.cos(THETA)])
            
            rvect = np.array([dx*m,dy*n,0])
            
            kdotr = kvect[0]*rvect[0]+kvect[1]*rvect[1]+kvect[2]*rvect[2]
            
            AF = AF + np.e**(1j*kdotr)

    AF_mag = np.abs(AF)
    AF_norm = AF_mag/np.max(AF_mag)
    
    return(AF_norm)

def array_factor_single_phi(phi,dy,dx,PHI,THETA,N,M=1):

    AF = np.zeros(np.shape(THETA))

    # ARRAY
    for m in range(M):
        for n in range(N):
        
            kvect = k0*np.array([np.sin(THETA)*np.cos(PHI), np.sin(THETA)*np.sin(PHI), np.cos(THETA)])
            
            rvect = np.array([dx*m,dy*n,0])
            
            kdotr = kvect[0]*rvect[0]+kvect[1]*rvect[1]+kvect[2]*rvect[2]
            
            AF = AF + np.e**(1j*kdotr)

    AF_mag = np.abs(AF)
    AF_norm = AF_mag/np.max(AF_mag)
    
    return(AF_norm[0])

# returns normalized patch antenna radiation pattern
def patch_antenna(L,W,THETA,PHI):
    vx = (L/lambd) * np.sin(THETA) * np.cos(PHI)
    vy = (W/lambd) * np.sin(THETA) * np.sin(PHI)

    f = np.cos(vx*np.pi) * np.sinc(vy)

    pattern = (np.cos(THETA)**2 * np.sin(PHI)**2 + np.cos(PHI)**2) * np.abs(f)**2

    pattern_norm = pattern/np.max(pattern)
    
    
    return(pattern_norm)


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
    
def calc_sidelobelevel(pattern):
    peaks,prop = find_peaks(pattern,height=-100)
    heights = prop["peak_heights"]
    max_sidelobe = np.max(np.delete(heights,np.argmax(heights)))
    return(max_sidelobe)



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



def lab3_ex2a():
    print("A")
    
    theta = np.linspace(0, np.pi, LOW_RES)
    phi = np.linspace(-np.pi, np.pi, LOW_RES)

    THETA, PHI = np.meshgrid(theta, phi)
    
    # 3D plot
    AF_norm = array_factor(dy,0,THETA,PHI,8)
    #AF_norm = AF_norm # 20*np.log10(np.where(AF_norm>1e-6,AF_norm,1e-6))+121
    
    plot_pattern3D(AF_norm, THETA, PHI,title="Array factor") 
    
     
    # 2D cuts
    theta = np.linspace(-np.pi/2, np.pi/2, HIGH_RES)
    phi = [0,np.pi/2]
    THETA, PHI = np.meshgrid(theta, phi)
    
    
    AF_zerophi, AF_90phi = array_factor(dy,0,THETA,PHI,8)
    


    #AF_zerophi_dB = 20*np.log10(AF_zerophi)
    AF_90phi_dB = 20*np.log10(AF_90phi)

    # calc parameters
    max_sidelobe = calc_sidelobelevel(AF_90phi_dB)
    print(f"The maximum sidelobe level is {round(max_sidelobe,4)} dB")


    beamwidth90 = get_beamwidth(AF_90phi,theta)

    beamwidthzero = get_beamwidth(AF_zerophi,theta)

    print(f"The beamwidth in the phi=90 plane is {beamwidth90} deg")
    print(f"The beamwidth in the phi=0 plane is {beamwidthzero} deg")

    D = 4*np.pi*(180/np.pi)**2 / (beamwidthzero*beamwidth90)

    print(f"The directivity of the antenna is {round(D,3)}, which is {round(20*np.log10(D),4)} dB")

    # actual plotting
    fig,ax = plot_2d_cuts(AF_zerophi, AF_90phi, theta)
    
    ax.set_title("Array Factor")

    
    
    
def lab3_ex2b():
    print(10*"-")
    print("B")
    
    
    L = 5e-3
    W = 6.5e-3
    
    
    theta = np.linspace(0, np.pi/2, LOW_RES)
    phi = np.linspace(-np.pi, np.pi, LOW_RES)
    THETA, PHI = np.meshgrid(theta, phi)
    
    # calc pattern
    pattern_norm = patch_antenna(L,W,THETA,PHI)
    
    # plotting
    # 3D
    plot_pattern3D(pattern_norm,THETA,PHI,title="Patch antenna radiation pattern")
    
    
    
    # 2D
    phi = np.array([0,np.pi/2])
    theta = np.linspace(-np.pi/2,np.pi/2,HIGH_RES)
    THETA,PHI = np.meshgrid(theta,phi)
    pattern = patch_antenna(L,W,THETA,PHI)
    pattern_zerophi,pattern_90phi = pattern
    
    fig,ax = plot_2d_cuts(pattern_zerophi, pattern_90phi, theta)
    
    ax.set_ylabel("normalized gain (dB)")
    ax.set_title("Patch antenna radiation pattern")

    
    
    # 2D
    #fig,ax,pattern_zerophi,pattern_90phi = plot_2d_cuts(patch_antenna,L,W,title="Patch antenna radiation pattern")
    #ax.set_ylabel("normalized gain (dB)")
    
    theta = np.linspace(-np.pi/2, np.pi/2, HIGH_RES)
    # calc bandwidth
    bwzero = get_beamwidth(pattern_zerophi,theta)
    bw90 = get_beamwidth(pattern_90phi,theta)
    
    #calc directivity
    D = 4*np.pi*(180/np.pi)**2 / (bwzero*bw90)
    
    
    print("Patch antenna")
    print(f"The beamwidth in the phi=90 plane is {bw90} deg")
    print(f"The beamwidth in the phi=0 plane is {bwzero} deg")
    print(f"The directivity of the antenna is {round(D,3)}, which is {round(20*np.log10(D),4)} dB")
    
    
def lab3_ex2c():
    print(10*"-")
    print("C")
    L,W = 5e-3,6.5e-3
    N = 8
    
    theta = np.linspace(-np.pi/2, np.pi/2, LOW_RES)
    phi = np.linspace(-np.pi, np.pi, LOW_RES)
    THETA, PHI = np.meshgrid(theta, phi)
    
    # calc pattern of element
    element_pattern_norm = patch_antenna(L,W,THETA,PHI)
    
    # calc AF
    AF_norm = array_factor(dy,0,THETA,PHI,8)
    
    total_norm = element_pattern_norm * AF_norm

    # plot 3D
    plot_pattern3D(total_norm, THETA, PHI)


    # 2D cuts
    theta = np.linspace(-np.pi/2, np.pi/2, HIGH_RES)
    phi = [0,np.pi/2]
    THETA, PHI = np.meshgrid(theta, phi)
    
    
    # element factor
    ef_zerophi,ef_90phi = patch_antenna(L, W, THETA, PHI)
   
    fig,ax = plot_2d_cuts(ef_zerophi, ef_90phi, theta)
    ax.set_ylabel("normalized gain (dB)")
    # array factor
    
    af_zerophi, af_90phi = array_factor(dy, 0, PHI, THETA, N)
    
    fig,ax = plot_2d_cuts(af_zerophi, af_90phi,theta)
    ax.set_ylabel("normalized AF (dB)")
    
    
    total_zerophi = ef_zerophi * af_zerophi
    total_90phi = ef_90phi * af_90phi
    
    # calc beamwidth
    bwzero = get_beamwidth(total_zerophi,theta)
    bw90 = get_beamwidth(total_90phi,theta)

    #calc directivity
    D = 4*np.pi*(180/np.pi)**2 / (bwzero*bw90)


    print("Total pattern")
    print(f"The beamwidth in the phi=90 plane is {bw90} deg")
    print(f"The beamwidth in the phi=0 plane is {bwzero} deg")
    print(f"The directivity of the antenna is {round(D,3)}, which is {round(20*np.log10(D),4)} dB")
    
def lab3_ex2d():
    print(10*"-")
    print("D")

    # 3D PLOT
    N,M = 8,8
    L,W = 5e-3,6.5e-3
    dx=dy

    phi = np.linspace(-np.pi,np.pi,LOW_RES)
    theta = np.linspace(-np.pi/2,np.pi/2,LOW_RES)

    THETA,PHI = np.meshgrid(theta,phi)


    # calc pattern of element
    element_pattern_norm = patch_antenna(L,W,THETA,PHI)
    # calc array factor of 8x8 array
    AF_norm = array_factor(dy, dx, PHI, THETA, N, M=M)
        
    total_pattern = AF_norm * element_pattern_norm
    # PLOTTING
    plot_pattern3D(total_pattern, THETA, PHI,title="Antenna factor (8x8)")


    # CALCULATING DIRECTIVITY
    # only use two phi's
    phi = np.array([0,np.pi/2])
    theta = np.linspace(-np.pi/2,np.pi/2,HIGH_RES)
    THETA,PHI = np.meshgrid(theta,phi)
    
    # array factor
    AF_norm = array_factor(dy, dx, PHI, THETA, N, M=M)
    # split in zero and 90  
    AF_zerophi,AF_90phi = AF_norm


    # element pattern
    element_pattern_norm = patch_antenna(L,W,THETA,PHI)
    
    # split in zero and 90
    pattern_zerophi, pattern_90phi = element_pattern_norm
    
    total_zerophi = AF_zerophi * pattern_zerophi
    total_90phi = AF_90phi * pattern_90phi
    
    
    
    # calc beamwidth
    beamwidth90 = get_beamwidth(total_90phi, theta)
    beamwidthzero = get_beamwidth(total_zerophi, theta)


    print(10*"-")
    print("8x8 matrix")
    print(f"The beamwidth in the phi=90 plane is {beamwidth90} deg")
    print(f"The beamwidth in the phi=0 plane is {beamwidthzero} deg")

    D = 4*np.pi*(180/np.pi)**2 / (beamwidthzero*beamwidth90)

    print(f"The directivity of the antenna is {round(D,3)}, which is {round(20*np.log10(D),4)} dB")




if __name__=="__main__":
    
    
    lab3_ex2a()
    
    




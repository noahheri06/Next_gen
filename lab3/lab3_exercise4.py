from scipy.signal.windows import chebwin
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

def plot_pattern3D(pattern,THETA,PHI,title=""):
    
    R = pattern

    X = R * np.sin(THETA)*np.cos(PHI)
    Y = R * np.sin(THETA)*np.sin(PHI)
    Z = R * np.cos(THETA)

    colors = cm.jet(pattern)


    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')

    ax.plot_surface(X,Y,Z, facecolors = colors)

    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")
    ax.set_title(title)

    plt.grid()
    plt.show()
    
def get_beamwidth(pattern,theta):
    power = pattern**2
    ind_above_halfpower = np.where(power>0.5)[0]
    splits = np.where(np.diff(ind_above_halfpower) !=1)[0] + 1
    groups = np.split(ind_above_halfpower,splits)

    middlebeam = groups[floor(len(groups)/2)]

    bw = theta[middlebeam[-1]]-theta[middlebeam[0]]
    bw = np.rad2deg(bw)
    
    return(bw)
    

# =============================================================================
# A
# =============================================================================

N = 8
att = 45

# taper coefficients
taper_coef = chebwin(N, att)
#taper_coef = 8*[1]
print("Amplitude weights:",taper_coef)

phi = np.linspace(0,np.pi,1000)
theta = np.linspace(-np.pi,np.pi,1000)

THETA,PHI = np.meshgrid(theta,phi)


AF = np.zeros(np.shape(THETA))

for n in range(8):
    
    kvect = k0*np.array([np.sin(THETA)*np.cos(PHI), np.sin(THETA)*np.sin(PHI), np.cos(THETA)])
    
    rvect = np.array([0,dy*n,0])
    
    kdotr = kvect[0]*rvect[0]+kvect[1]*rvect[1]+kvect[2]*rvect[2]
    
    AF = AF + taper_coef[n] * np.e**(1j*kdotr)
    

AF_mag = np.abs(AF)

AF_norm = AF_mag/np.max(AF_mag)

plot_pattern3D(AF_norm, THETA, PHI, title="8x1 array")





# 2D PLOTS
phi = [0,np.pi/2]
theta = np.linspace(-np.pi,np.pi,10000)

THETA,PHI = np.meshgrid(theta,phi)


AF = np.zeros(np.shape(THETA))

for n in range(8):
    
    kvect = k0*np.array([np.sin(THETA)*np.cos(PHI), np.sin(THETA)*np.sin(PHI), np.cos(THETA)])
    
    rvect = np.array([0,dy*n,0])
    
    kdotr = kvect[0]*rvect[0]+kvect[1]*rvect[1]+kvect[2]*rvect[2]
    
    AF = AF + taper_coef[n] * np.e**(1j*kdotr)

AF_mag = np.abs(AF)

AF_normcuts = AF_mag/np.max(AF_mag)
    
AF_zerophi = AF_normcuts[0]
AF_90phi = AF_normcuts[1]

AF_zerophi_dB = 20*np.log10(AF_zerophi)
AF_90phi_dB = 20*np.log10(AF_90phi)


peaks,prop = find_peaks(AF_90phi_dB,height=-100)
heights = prop["peak_heights"]
max_sidelobe = np.max(np.delete(heights,np.argmax(heights)))
print(f"The maximum sidelobe level is {round(max_sidelobe,4)} dB")

fig = plt.figure()
ax = fig.add_subplot()

ax.plot(np.rad2deg(theta),AF_zerophi_dB,label="$\phi$ = 0$\degree$")
ax.plot(np.rad2deg(theta),AF_90phi_dB,label="$\phi$ = 90$\degree$")

ax.set_xlabel("$\theta$ (rad)")
ax.set_ylabel("normalized AF (dB)")

ax.set_title("Array Factor")
ax.legend()
plt.grid()
plt.show()


beamwidth90 = get_beamwidth(AF_90phi,theta)

beamwidthzero = get_beamwidth(AF_zerophi,theta)

print("8 in a line")
print(f"The beamwidth in the phi=90 plane is {beamwidth90} deg")
print(f"The beamwidth in the phi=0 plane is {beamwidthzero} deg")

D = 4*np.pi*(180/np.pi)**2 / (beamwidthzero*beamwidth90)

print(f"The directivity of the antenna is {round(D,3)}, which is {round(20*np.log10(D),4)} dB")


#%%

# =============================================================================
# B
# =============================================================================

dx=dy

N = 8
M = 8
att = 45

# taper coefficients
taper_coef_N = chebwin(N, att)
taper_coef_M = chebwin(M, att)
a,b = np.meshgrid(taper_coef_N,taper_coef_M)

taper_coef = a*b

# uncomment to the see case with constant coefficients
#taper_coef = 8*[8*[1]]

print("Amplitude weights:",taper_coef)

phi = np.linspace(0,np.pi,1000)
theta = np.linspace(-np.pi,np.pi,1000)

THETA,PHI = np.meshgrid(theta,phi)


AF = np.zeros(np.shape(THETA))

for n in range(N):
    for m in range(M):
    
        kvect = k0*np.array([np.sin(THETA)*np.cos(PHI), np.sin(THETA)*np.sin(PHI), np.cos(THETA)])
        
        rvect = np.array([dx*m,dy*n,0])
        
        kdotr = kvect[0]*rvect[0]+kvect[1]*rvect[1]+kvect[2]*rvect[2]
        
        AF = AF + taper_coef[n][m] * np.e**(1j*kdotr)
        

AF_mag = np.abs(AF)

AF_norm = AF_mag/np.max(AF_mag)

plot_pattern3D(AF_norm, THETA, PHI, title="8x8 array")








# 2D PLOTS
phi = [0,np.pi/2]
theta = np.linspace(-np.pi,np.pi,10000)

THETA,PHI = np.meshgrid(theta,phi)


AF = np.zeros(np.shape(THETA))

for n in range(N):
    for m in range(M):
    
        kvect = k0*np.array([np.sin(THETA)*np.cos(PHI), np.sin(THETA)*np.sin(PHI), np.cos(THETA)])
        
        rvect = np.array([dx*m,dy*n,0])
        
        kdotr = kvect[0]*rvect[0]+kvect[1]*rvect[1]+kvect[2]*rvect[2]
        
        AF = AF + taper_coef[n][m] * np.e**(1j*kdotr)
        
        
AF_mag = np.abs(AF)

AF_normcuts = AF_mag/np.max(AF_mag)
    
AF_zerophi = AF_normcuts[0]
AF_90phi = AF_normcuts[1]

AF_zerophi_dB = 20*np.log10(AF_zerophi)
AF_90phi_dB = 20*np.log10(AF_90phi)


peaks,prop = find_peaks(AF_90phi_dB,height=-100)
heights = prop["peak_heights"]
max_sidelobe = np.max(np.delete(heights,np.argmax(heights)))
print(f"The maximum sidelobe level is {round(max_sidelobe,4)} dB")

fig = plt.figure()
ax = fig.add_subplot()

ax.plot(np.rad2deg(theta),AF_zerophi_dB,label="$\phi$ = 0$\degree$")
ax.plot(np.rad2deg(theta),AF_90phi_dB,label="$\phi$ = 90$\degree$")

ax.set_xlabel("$\theta$ (rad)")
ax.set_ylabel("normalized AF (dB)")

ax.set_title("Array Factor")
ax.legend()
plt.grid()
plt.show()


beamwidth90 = get_beamwidth(AF_90phi,theta)

beamwidthzero = get_beamwidth(AF_zerophi,theta)

print("8 in a line")
print(f"The beamwidth in the phi=90 plane is {beamwidth90} deg")
print(f"The beamwidth in the phi=0 plane is {beamwidthzero} deg")

D = 4*np.pi*(180/np.pi)**2 / (beamwidthzero*beamwidth90)

print(f"The directivity of the antenna is {round(D,3)}, which is {round(20*np.log10(D),4)} dB")




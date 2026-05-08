from scipy.signal.windows import chebwin
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from math import floor
from scipy.signal import find_peaks
from Lab3_exercise2 import *

    

c=3e8
f = 15e9
lambd = c/f
k0 = 2*np.pi/lambd
dy = lambd/2
LOW_RES = 1000
HIGH_RES = 10000
    
def array_factor_taper(dy,dx,PHI,THETA,taper,N,M=1,resolution=LOW_RES):
    
    AF = np.zeros(np.shape(THETA))
    
    
    # ARRAY
    for m in range(M):
        for n in range(N):
        
            kvect = k0*np.array([np.sin(THETA)*np.cos(PHI), np.sin(THETA)*np.sin(PHI), np.cos(THETA)])
            
            rvect = np.array([dx*m,dy*n,0])
            
            kdotr = kvect[0]*rvect[0]+kvect[1]*rvect[1]+kvect[2]*rvect[2]
            
            
            # niet heel goed maar t werkt
            if M==1:
                AF = AF + taper_coef[n] * np.e**(1j*kdotr)
            else:
                AF = AF + taper_coef[n][m] * np.e**(1j*kdotr)

    AF_mag = np.abs(AF)
    AF_norm = AF_mag/np.max(AF_mag)
    
    return(AF_norm)



# =============================================================================
# A
# =============================================================================

N = 8
att = 45

# taper coefficients
taper_coef = chebwin(N, att)
#taper_coef = 8*[1]

print("Amplitude weights:",taper_coef)

phi = np.linspace(-np.pi,np.pi,1000)
theta = np.linspace(0,np.pi,1000)

THETA,PHI = np.meshgrid(theta,phi)



AF_norm = array_factor_taper(dy,0,PHI,THETA,taper_coef,N)

plot_pattern3D(AF_norm, THETA, PHI, title="8x1 array")





# 2D PLOTS

theta = np.linspace(-np.pi/2,np.pi/2,HIGH_RES)

fig,ax,AF_zerophi,AF_90phi = plot_2d_cuts(array_factor_taper, dy,0,taper_coef,N)


AF_zerophi_dB = 20*np.log10(AF_zerophi)
AF_90phi_dB = 20*np.log10(AF_90phi)


peaks,prop = find_peaks(AF_90phi_dB,height=-100)
heights = prop["peak_heights"]
max_sidelobe = np.max(np.delete(heights,np.argmax(heights)))
print(f"The maximum sidelobe level is {round(max_sidelobe,4)} dB")

ax.set_title("Array Factor (8x1 tapered)")


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


AF_norm = array_factor_taper(dy, dx, PHI, THETA, taper_coef, N,M=M)

plot_pattern3D(AF_norm, THETA, PHI, title="8x8 array")



# 2D PLOTS

theta = np.linspace(-np.pi/2,np.pi/2,HIGH_RES)

fig,ax,AF_zerophi,AF_90phi = plot_2d_cuts(array_factor_taper, dy,dx,taper_coef,N,M=M)


AF_zerophi_dB = 20*np.log10(AF_zerophi)
AF_90phi_dB = 20*np.log10(AF_90phi)


peaks,prop = find_peaks(AF_90phi_dB,height=-100)
heights = prop["peak_heights"]
max_sidelobe = np.max(np.delete(heights,np.argmax(heights)))
print(f"The maximum sidelobe level is {round(max_sidelobe,4)} dB")


ax.set_title("Array Factor (8x8 tapered)")


beamwidth90 = get_beamwidth(AF_90phi,theta)

beamwidthzero = get_beamwidth(AF_zerophi,theta)

print("8 in a line")
print(f"The beamwidth in the phi=90 plane is {beamwidth90} deg")
print(f"The beamwidth in the phi=0 plane is {beamwidthzero} deg")

D = 4*np.pi*(180/np.pi)**2 / (beamwidthzero*beamwidth90)

print(f"The directivity of the antenna is {round(D,3)}, which is {round(20*np.log10(D),4)} dB")




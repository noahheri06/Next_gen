import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from math import floor


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

    colors = cm.jet(AF_norm)


    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')

    ax.plot_surface(X,Y,Z, facecolors = colors)

    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")
    ax.set_title(title)

    plt.grid()
    plt.show()



# =============================================================================
# A
# =============================================================================


# =============================================================================
# 3D PLOT
# =============================================================================

phi = np.linspace(0,np.pi,1000)
theta = np.linspace(-np.pi,np.pi,1000)

THETA,PHI = np.meshgrid(theta,phi)


AF = np.zeros(np.shape(THETA))

for n in range(8):
    
    kvect = k0*np.array([np.sin(THETA)*np.cos(PHI), np.sin(THETA)*np.sin(PHI), np.cos(THETA)])
    
    rvect = np.array([0,dy*n,0])
    
    kdotr = kvect[0]*rvect[0]+kvect[1]*rvect[1]+kvect[2]*rvect[2]
    
    AF = AF + np.e**(1j*kdotr)
    
    
    #AF += np.e**(1j*n*dy*k0*np.sin(theta)*np.sin(phi))

AF_mag = np.abs(AF)

AF_norm = AF_mag/np.max(AF_mag)
    

R = AF_norm

X = R * np.sin(THETA)*np.cos(PHI)
Y = R * np.sin(THETA)*np.sin(PHI)
Z = R * np.cos(THETA)

colors = cm.jet(AF_norm)


fig = plt.figure()
ax = fig.add_subplot(projection='3d')

ax.plot_surface(X,Y,Z, facecolors = colors)

ax.set_xlabel("x")
ax.set_ylabel("y")
ax.set_zlabel("z")
ax.set_title("Array Factor")

plt.grid()
plt.show()


# =============================================================================
# 2D CUTS
# =============================================================================



phi = np.array([0,np.pi/2])
theta = np.linspace(-np.pi,np.pi,10000)

THETA,PHI = np.meshgrid(theta,phi)
AF = np.zeros(np.shape(THETA))

for n in range(8):
    
    kvect = k0*np.array([np.sin(THETA)*np.cos(PHI), np.sin(THETA)*np.sin(PHI), np.cos(THETA)])
    
    rvect = np.array([0,dy*n,0])
    
    kdotr = kvect[0]*rvect[0]+kvect[1]*rvect[1]+kvect[2]*rvect[2]
    
    AF = AF + np.e**(1j*kdotr)
    
    
    #AF += np.e**(1j*n*dy*k0*np.sin(theta)*np.sin(phi))

AF_mag = np.abs(AF)

AF_normcuts = AF_mag/np.max(AF_mag)
    
AF_zerophi = AF_normcuts[0]
AF_90phi = AF_normcuts[1]


colors = cm.jet(AF_norm)


fig = plt.figure()
ax = fig.add_subplot()

ax.plot(np.rad2deg(theta),20*np.log10(AF_zerophi),label="$\phi$ = 0*")
ax.plot(np.rad2deg(theta),20*np.log10(AF_90phi),label="$\phi$ = 90*")


ax.set_xlabel("$\theta$ (rad)")
ax.set_ylabel("normalized AF (dB)")

ax.set_title("Array Factor")
ax.legend()
plt.grid()
plt.show()



# =============================================================================
# HALF POWER BANDWIDTH
# =============================================================================

def get_beamwidth(pattern,theta):
    power = pattern**2
    ind_above_halfpower = np.where(power>0.5)[0]
    splits = np.where(np.diff(ind_above_halfpower) !=1)[0] + 1
    groups = np.split(ind_above_halfpower,splits)

    middlebeam = groups[floor(len(groups)/2)]

    bw = theta[middlebeam[-1]]-theta[middlebeam[0]]
    bw = np.rad2deg(bw)
    
    return(bw)
    
    


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

# returns normalized patch antenna radiation pattern
def patch_antenna(L,W,THETA,PHI):
    vx = (L/lambd) * np.sin(THETA) * np.cos(PHI)
    vy = (W/lambd) * np.sin(THETA) * np.sin(PHI)

    f = np.cos(vx*np.pi) * np.sinc(vy)

    pattern = (np.cos(THETA)**2 * np.sin(PHI)**2 + np.cos(PHI)**2) * np.abs(f)**2

    pattern_norm = pattern/np.max(pattern)
    
    
    return(pattern_norm)




L = 0.02
W = 0.03

er = 3.44
tan_delta = 0.01
h = 0.5e-3


theta = np.linspace(0, np.pi, 1000)
phi = np.linspace(-np.pi, np.pi, 1000)

THETA, PHI = np.meshgrid(theta, phi)
    
pattern_norm = patch_antenna(L,W,THETA,PHI)


# plotting
plot_pattern3D(pattern_norm,THETA,PHI)


# calculate beamwidth
# calc for phi=0
phi = 0
THETA, PHI = np.meshgrid(theta, phi)
pattern_zerophi = patch_antenna(L,W,THETA,PHI)[0]

# calc for phi=90
phi = 90
THETA, PHI = np.meshgrid(theta, phi)
pattern_90phi = patch_antenna(L,W,THETA,np.pi/2)[0]


bwzero = get_beamwidth(pattern_zerophi,theta)
bw90 = get_beamwidth(pattern_90phi,theta)

#calc directivity
D = 4*np.pi*(180/np.pi)**2 / (bwzero*bw90)

print(10*"-")
print("Patch antenna")
print(f"The beamwidth in the phi=90 plane is {bw90} deg")
print(f"The beamwidth in the phi=0 plane is {bwzero} deg")
print(f"The directivity of the antenna is {round(D,3)}, which is {round(20*np.log10(D),4)} dB")





#%%

# =============================================================================
# C
# =============================================================================

total_norm = pattern_norm * AF_norm

theta = np.linspace(0, np.pi, 1000)
phi = np.linspace(-np.pi, np.pi, 1000)

THETA, PHI = np.meshgrid(theta, phi)

plot_pattern3D(total_norm, THETA, PHI)


total_zerophi = AF_zerophi[::10] * pattern_zerophi
total_90phi = AF_90phi[::10] * pattern_90phi



bwzero = get_beamwidth(total_zerophi,theta)
bw90 = get_beamwidth(total_90phi,theta)

#calc directivity
D = 4*np.pi*(180/np.pi)**2 / (bwzero*bw90)

print(10*"-")
print("Total pattern")
print(f"The beamwidth in the phi=90 plane is {bw90} deg")
print(f"The beamwidth in the phi=0 plane is {bwzero} deg")
print(f"The directivity of the antenna is {round(D,3)}, which is {round(20*np.log10(D),4)} dB")


#%%

# =============================================================================
# D
# =============================================================================


# 3D PLOT

dx=dy

phi = np.linspace(0,np.pi,1000)
theta = np.linspace(-np.pi,np.pi,1000)

THETA,PHI = np.meshgrid(theta,phi)


AF = np.zeros(np.shape(THETA))

# 8x8 ARRAY
for n in range(8):
    for m in range(8):
    
        kvect = k0*np.array([np.sin(THETA)*np.cos(PHI), np.sin(THETA)*np.sin(PHI), np.cos(THETA)])
        
        rvect = np.array([dx*m,dy*n,0])
        
        kdotr = kvect[0]*rvect[0]+kvect[1]*rvect[1]+kvect[2]*rvect[2]
        
        AF = AF + np.e**(1j*kdotr)

AF_mag = np.abs(AF)
AF_norm = AF_mag/np.max(AF_mag)
    
total_pattern = AF_norm * pattern_norm
# PLOTTING
plot_pattern3D(total_pattern, THETA, PHI)


# CALCULATING DIRECTIVITY

phi = np.array([0,np.pi/2])
theta = np.linspace(-np.pi,np.pi,10000)

THETA,PHI = np.meshgrid(theta,phi)
AF = np.zeros(np.shape(THETA))

for n in range(8):
    for m in range(8):
    
        kvect = k0*np.array([np.sin(THETA)*np.cos(PHI), np.sin(THETA)*np.sin(PHI), np.cos(THETA)])
        
        rvect = np.array([dx*m,dy*n,0])
        
        kdotr = kvect[0]*rvect[0]+kvect[1]*rvect[1]+kvect[2]*rvect[2]
        
        AF = AF + np.e**(1j*kdotr)

AF_mag = np.abs(AF)

AF_norm = AF_mag/np.max(AF_mag)
    
AF_zerophi = AF_norm[0]
AF_90phi = AF_norm[1]


total_zerophi = AF_zerophi[::10] * pattern_zerophi
total_90phi = AF_90phi[::10] * pattern_90phi

beamwidth90 = get_beamwidth(total_90phi, theta)
beamwidthzero = get_beamwidth(total_zerophi, theta)


print(10*"-")
print("8x8 matrix")
print(f"The beamwidth in the phi=90 plane is {beamwidth90} deg")
print(f"The beamwidth in the phi=0 plane is {beamwidthzero} deg")

D = 4*np.pi*(180/np.pi)**2 / (beamwidthzero*beamwidth90)

print(f"The directivity of the antenna is {round(D,3)}, which is {round(20*np.log10(D),4)} dB")


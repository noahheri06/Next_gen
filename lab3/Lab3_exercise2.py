import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm


c=3e8
f = 15e9
lambd = c/f
k0 = 2*np.pi/lambd

dy = lambd/2





phi = np.linspace(0,np.pi,300)
theta = np.linspace(-np.pi,np.pi,300)

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
# ax.set_xlim(-1.01, 1.01)
# ax.set_ylim(-1.01, 1.01)
ax.set_xlabel("x")
ax.set_ylabel("y")
ax.set_zlabel("z")
ax.set_title("Array Factor")
plt.grid()
plt.show()


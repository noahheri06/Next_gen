import numpy as np
import matplotlib.pyplot as plt

Z0  =50
C = 3e8
# =============================================================================
# a
# =============================================================================

f = [12e9, 15e9, 16e9]
thetha = np.linspace(-np.pi, np.pi, 1000000)

lx = 8.86e-2
ly = 6.6e-2



def f_function(thetha, phi,f):
    lambd = C/f
    gammax = (lx/lambd)*np.sin(thetha)*np.cos(phi)
    gammay = (lx/lambd)*np.sin(thetha)*np.sin(phi)
    f_function = np.sinc(gammax)*np.sinc(gammay)
    return f_function, lambd, gammax, gammay

for i in range(3):
    phi = np.pi()
    f_function1, lambd, gammax, gammay = f_function(thetha, phi, f[i])
    s1 = f_function1**2/(2*(120*np.pi)*lambd**2)
    normalized = 10*np.log10(s1/np.max(s1))

    plt.plot(thetha, normalized) # from first principle
    plt.plot(thetha, 10*np.log10(np.sinc(gammax)**2)) # from simplified formula case phi = 0
    plt.show()




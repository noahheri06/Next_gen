import numpy as np
from matplotlib import pyplot as plt

c = 3e8

# =============================================================================
# Point A
# =============================================================================
print("Point A")

X = 6 # laatste cijfer van sudentnummer Casper
M = 30
tau_pulse = 10e-6
PRI = X * 100e-6

dR = c * tau_pulse/2
doppler_res_freq = 1/(PRI * M)
Rmax = c * PRI / 2
f_d_max = 1 / (2 * PRI)

print(f"The range resolution is {round(dR,2)} m")
print(f"The doppler resolution is {round(doppler_res_freq,2)} Hz")
print(f"The unambiguous range is {round(Rmax,2)} m")
print(f"The unambiguous doppler shift is {round(f_d_max,2)} Hz")


# =============================================================================
# Point B
# =============================================================================

print("Point B")


def doppler_shift(v,f_carrier):
    f_d = 2*v*f_carrier/3e8
    return(f_d)



radars = {1: 2.4e9, 2: 15e9, 3: 77e9}
possible_PRF = [1e3,2e3,4e3,6e3,8e3,10e3]

targets = [1.4, 2.9, 18/3.6, 36/3.6, 108/3.6]

for radar in radars:
    print(f"Radar {radar} at {radars[radar]/1e9} GHz")
    
    for PRF in possible_PRF:
        print(f"Using a PRF of {PRF/1e3} kHz")
        doppler_res_freq = PRF / M
        print(f"So the doppler resolution is {round(doppler_res_freq,2)} Hz")
        for v_target in targets:
            freq_shift = doppler_shift(v_target,radars[radar])
            detectable = freq_shift > doppler_res_freq
            print_text = {True: 'Detectable!',False: 'Not detectable...'}[detectable]
            print(f"The doppler shift for the target moving at {v_target} m/s is {round(freq_shift,2)} Hz")
            print(f"{print_text}")
            
            
            
    print(20*"#"+"\n")














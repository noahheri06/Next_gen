import numpy as np
from matplotlib import pyplot as plt


# =============================================================================
# PART A
# =============================================================================
print("Part A")

X = np.random.randint(1,10)
f_c = 12e9
# X = 1 # laatste cijfer van mijn studentennummer
print(f"X used is {X}")

tau_pulse = X * 1e-6

# one pulse, so T_d = tau_pulse

doppler_res_freq = 1/tau_pulse

print(f"The Rayleigh resolution in Doppler frequency is {round(doppler_res_freq,3)} Hz")


dv = doppler_res_freq * 3e8/2 / f_c

print(f"The associated velocity resolution is {round(dv,3)} m/s")




# =============================================================================
# PART B
# =============================================================================
print("Part B")

f_c_a = 5.8e9
f_c_b = 5.81e9

df = f_c_b - f_c_a

# Rayleigh resolution
tau_pulse = 1/df

tau_pulse *=1e6

print(f"The minimum pulse length should be {round(tau_pulse,3)} us")


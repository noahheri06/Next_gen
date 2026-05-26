import numpy as np



# =============================================================================
# A
# =============================================================================
def to_linear(x):
    return(10**(x/10))

models = {"A":{"Tx power":25000,"Gain":36, "Carrier Frequency":9.4},
          "B":{"Tx power":250000,"Gain":31, "Carrier Frequency":9.4},
          "C":{"Tx power":250000,"Gain":31, "Carrier Frequency":2.8},
          "D":{"Tx power":250000,"Gain":36, "Carrier Frequency":9.4}}

SNR_results = {}


noise_bandwidth = 15e6
sigma = 1
R = 35e3

# NF_9_4GHz_dB = 3.2
# NF_2_8GHz_dB = 2.7

NF_dB = {9.4:3.2,2.8:2.7}
NF = {a:to_linear(NF_dB[a]) for a in NF_dB}

k = 1.38065e-23
T0 = 290
c = 3e8



print("PART A")
for model in models:
    
    P_t, gain_dB,carrier_freq = models[model]["Tx power"],models[model]["Gain"],models[model]["Carrier Frequency"]
    gain = to_linear(gain_dB)
    #print(P_t, gain_dB,carrier_freq)
    
    
    P_n = k * T0 * NF[carrier_freq] * noise_bandwidth
    
    lambd = c/(carrier_freq*1e9)
    
    SNR = P_t * gain * gain * sigma * lambd**2 / ((4*np.pi)**3 * R**4 * P_n )
    print(model,SNR)
    
    SNR_dB = 10*np.log10(SNR)
    SNR_results[model] = SNR_dB
    
    print(f"The SNR for model {model} is {SNR_dB} dB")
    
    
# =============================================================================
# B
# =============================================================================

print("PART B")

max_SNR_model = list(SNR_results.keys())[list(SNR_results.values()).index(max(SNR_results.values()))]

print(f"The model with the highest SNR is model {max_SNR_model}")


alpha = 0.05 # dB/km attenuation

total_att_dB = alpha * R/1e3

L_s = to_linear(total_att_dB)
print(f"L_s = {L_s}")

n_p = int(np.ceil(L_s))

print(f"The amount of pulses needed to compensate for the atmospheric propagation losses is: {n_p}")

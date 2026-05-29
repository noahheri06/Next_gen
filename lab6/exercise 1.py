import numpy as np
from matplotlib import pyplot as plt


def doppler_shift(v,theta,f_carrier):
    v_radial = np.cos(np.deg2rad(theta)) * v
    
    f_d = 2*v_radial*f_carrier/3e8
    
    return(f_d)



targets = {1:{"v":3,"theta":0,"f_c":12},
           2:{"v":6,"theta":45,"f_c":12},
           3:{"v":12,"theta":30,"f_c":3}}

for target in targets:
    v,theta,f_c = targets[target]["v"]/3.6 , targets[target]["theta"], targets[target]["f_c"]*1e9
    
    print(f"The doppershift of target {target} is {doppler_shift(v,theta,f_c)} Hz")
    
    
    
    
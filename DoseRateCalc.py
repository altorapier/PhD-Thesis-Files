# -*- coding: utf-8 -*-
"""
Created on Thu May 26 13:48:38 2022

@author: Yunpeng Jia, modified by Kieran Ramaswami

This script is designed to calcualt teh dose rate from an X-ray system using a DIY Air chamber.
"""

####################### imports ################################
import numpy as np
import os
import matplotlib.pyplot as plt
import numpy.polynomial.polynomial as poly
import scipy
from scipy.interpolate import lagrange
from numpy.polynomial.polynomial import Polynomial
import math
##################################################################
# some inputs of one kVp and mA point
# this script is running once for a kVp and a mA with experimental data I_Se and I_ch
kVp = 40#25 #kV
mA = 55#50 #mA

I_ch = 3.57E-10#1.21122*10**-9 #A
I_ch_err = 7.9395*10**-12 #A error

##################################################################
# some constants
# density of Air
p_air=1.225e-6 #kg/cm^3

t_x = 10 #seconds # X-ray exposure time

d = 0.64442 #diameter of xray spot cm
d_err = 0.01407

t_ch = 0.6#0.51# cm # ion chamber thickness
t_ch_err = 0.01
e_c = 1.602176634e-19 # Charge
# W constant
W_air = 34 # eV

##################################################################

D_dot = (4*W_air*I_ch)/(math.pi*t_ch*p_air*(d**2))#dose rate
a_ch = 0.407#math.pi*(d/2)**2
v_air = t_ch*a_ch
m_air = p_air*v_air
D = W_air*I_ch/(m_air)*1000

D_dot_err = (4*W_air/(math.pi*t_ch*p_air*(d**2)))*math.sqrt(I_ch_err**2+(2*I_ch*d_err/d)**2+(I_ch*t_ch_err/t_ch)**2)

##################################################################
print("Average Dose Rate: "+str(round(D_dot*1000,2))+"mGy/s")
print("Average Dose Rate Std: "+str(round(D_dot_err*1000,2))+"mGy/s")

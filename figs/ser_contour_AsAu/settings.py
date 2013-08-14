# settings for the data generation of the contour plot
import numpy as np
from numpy import pi

T = 1.
As = 1.0
Au = 100.0

dx = 1./250

# pre-300 
#tau_range = np.arange(-1.5*T, 1.51*T, 3*T*dx)
#tau_range_wide = np.arange(-4.0*T, 4.001*T, 8*T*dx)
tau_range = np.arange(-1.5*T, 1.5001*T, 3*T*dx)
tau_range_wide = np.arange(-4.0*T, 4.0001*T, 8*T*dx)

phi_range = np.random.uniform(-pi, pi, size=200)

Au_range_dB = np.arange(-10, 51, 60*dx) # v2
#Au_range_dB = np.arange(-10, 50.1, 60*dx) # v3
Au_range  = np.sqrt(10.0**(Au_range_dB / 10.0))

Au_range_wide_dB = np.arange(-3, 16.001, 21*dx)
Au_range_wide    = np.sqrt(10.0**(Au_range_wide_dB / 10.0))

nbits = 1000
nsyms = 100
pktlen = 16

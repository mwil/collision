# settings for the data generation of the contour plot

import numpy as np

T = 1.
As = 1.0
Au = 100.0
#Au = 2.0

dx = 1./150  # 200 for 2.0
nbits = 1000
nsyms = 250

tau_range = np.arange(-1.5*T, 1.51*T, dx)
phi_range = np.arange(-np.pi, np.pi+0.01, dx)
#tau_range = np.arange(-1.5*T, 1.5001*T, dx)
#phi_range = np.arange(-np.pi, np.pi+0.0001, dx)
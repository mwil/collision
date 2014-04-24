# settings for the data generation of the contour plot

import numpy as np

T = 1.
As = 1.0
Au = 100.0
#Au = 2.0

#dx = 1./250
dx = 1./200
nbits = 3000

tau_range = np.arange(-1.5*T, 1.5*T, 3*T*dx)
phi_range = np.arange(-np.pi, np.pi, 2*np.pi*dx)

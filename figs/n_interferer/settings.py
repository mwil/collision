# settings for the data generation of the contour plot

import numpy as np

T = 1.
As = 1.0
Au  = 1/np.sqrt(2)
Au_ = 1/np.sqrt(2)

nsyms = 250
nphi  = 2500
pktlen = 16

num_interferer = 8

phi_range = np.random.uniform(-np.pi, np.pi, size=nphi)

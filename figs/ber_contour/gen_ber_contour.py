# Copyright 2013 Matthias Wilhelm

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys
import time

sys.path.append('../src')

import numpy as np
from numpy import pi
from pylab import *
from phitau import *
from settings import *

#tau_range = np.arange(-1.5*T, 1.51*T, 8*T*dx)
#phi_range = np.arange(-pi, pi+0.01, 2*pi*dx)

BER_U, BER_S = None, None

content = ('same', 'unif')[1]

# Query user to enter parameter settings, useful to run scripts in parallel
input_params = (('content', ('same', 'unif'), 'Data content'),)

for var, choices, prompt in input_params:
    resp = None
    while resp not in choices:
        resp = raw_input(prompt+' '+repr(choices) +'? ').lower()
    globals()[var] = resp

if os.path.exists('data/ber_u_Au%.2f_%s.npy'%(Au, content)):
    print("The file already exists!")    
    resp = None
        
    while resp not in ('yes', 'no', 'y', 'n'):
        resp = raw_input('Do you want to continue (y/n)? ').lower()
                    
    if resp not in ('yes', 'y'):
        exit(0)

start_time = time.time()

for tau in tau_range:
    print 'Step time for tau = %.3f: %.3fs'% (tau, time.time() - start_time)
    start_time = time.time()

    ber_u = np.array([])
    ber_s = np.array([])
    
    if content in ('same', ):
        send_chips = np.array([2*np.random.randint(2, size=2*nbits)-1]).reshape((2, nbits))
        send_chips = np.vstack((send_chips, send_chips)) 
    else:    
        send_chips = np.array([2*np.random.randint(2, size=4*nbits)-1]).reshape((4, nbits))
    
    RECV_CHIPS_I = detect_i(send_chips[:2], send_chips[2:], phi_range, tau, As, Au)
    RECV_CHIPS_Q = detect_q(send_chips[:2], send_chips[2:], phi_range, tau, As, Au)
    
    for i in xrange(len(phi_range)):
        recv_chips  = sign(np.ravel(zip(RECV_CHIPS_I[:,i], RECV_CHIPS_Q[:,i])))
        sync_chips  = np.ravel(zip(send_chips[0], send_chips[1]))
        usync_chips = np.ravel(zip(send_chips[2], send_chips[3]))
    
        # ignore chips that are only partially affected here
        ber_u = np.append(ber_u, np.sum(recv_chips[2:-2] != usync_chips[2:-2]) / (1.0*len(recv_chips[2:-2])))
        ber_s = np.append(ber_s, np.sum(recv_chips[2:-2] != sync_chips[2:-2])  / (1.0*len(recv_chips[2:-2])))
    
    if BER_U is None:
        BER_U = ber_u
        BER_S = ber_s
    else:
        BER_U = np.vstack((BER_U, ber_u))
        BER_S = np.vstack((BER_S, ber_s))
    
np.save('data/ber_u_Au%.2f_%s.npy'%(Au, content), BER_U)
np.save('data/ber_s_Au%.2f_%s.npy'%(Au, content), BER_S)

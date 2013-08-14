import os
import sys
import time

sys.path.append('../src')

import numpy as np
from numpy import pi
from phitau import *
from settings import *

BER_U, BER_S = None, None


content = ('same', 'unif')[0]
wide = ('', '_wide')[0]

# Query user to enter parameter settings, useful to run scripts in parallel
input_params = (('content', ('same', 'unif'), 'Data content'), ('wide', ('', '_wide'), 'Time offset interval'))

for var, choices, prompt in input_params:
    resp = None
    while resp not in choices:
        resp = raw_input(prompt+' '+repr(choices) +'? ').lower()
    globals()[var] = resp


if os.path.exists('data/prr_s_AsAu_%s%s-300.npy'%(content, wide)):
    print("The file already exists!")    
    resp = None
        
    while resp not in ('yes', 'no', 'y', 'n'):
        resp = raw_input('Do you want to continue (y/n)? ').lower()
                    
    if resp not in ('yes', 'y'):
        exit(0)

start_time = time.time()

tau_range   = (tau_range_wide   if wide else tau_range)
Au_range    = (Au_range_wide    if wide else Au_range)
Au_range_dB = (Au_range_wide_dB if wide else Au_range_dB)

for tau in tau_range:
    ber_u, ber_s = np.array([]), np.array([])

    if content in ('same', ):
        send_chips = np.array([2*np.random.randint(2, size=2*nbits)-1]).reshape((2, nbits))
        send_chips = np.vstack((send_chips, send_chips))
    else:
        send_chips = np.array([2*np.random.randint(2, size=4*nbits)-1]).reshape((4, nbits))
    
    for Au in Au_range:
        ber_u_phi, ber_s_phi = np.array([]), np.array([])

        print "ber_contour_AsAu: tau=%.4f, Au=%.4f, runtime: %.2f secs" % (tau, Au, time.time() - start_time)
        start_time = time.time()
        
        RECV_CHIPS_I = detect_i(send_chips[:2], send_chips[2:], phi_range, tau, As, Au)
        RECV_CHIPS_Q = detect_q(send_chips[:2], send_chips[2:], phi_range, tau, As, Au)
        
        for i in xrange(len(phi_range)):
            recv_chips = sign(np.ravel(zip(RECV_CHIPS_I[:,i], RECV_CHIPS_Q[:,i])))
            usync_chips  = np.ravel(zip(send_chips[2], send_chips[3]))
            sync_chips = np.ravel(zip(send_chips[0], send_chips[1]))
        
            # ignore chips that are only partially affected here
            ber_u_phi = np.append(ber_u_phi, np.sum(recv_chips[2:-2] != usync_chips[2:-2])  / (1.0*len(recv_chips[2:-2])))
            ber_s_phi = np.append(ber_s_phi, np.sum(recv_chips[2:-2] != sync_chips[2:-2]) / (1.0*len(recv_chips[2:-2])))
    
        ber_s = np.append(ber_s, np.mean((1-ber_s_phi)**pktlen))
        ber_u = np.append(ber_u, np.mean((1-ber_u_phi)**pktlen))
    
    if BER_U is None:
        BER_U = ber_u
        BER_S = ber_s
    else:
        BER_U = np.vstack((BER_U, ber_u))
        BER_S = np.vstack((BER_S, ber_s))
    
np.save('data/prr_u_AsAu_%s%s-300.npy'%(content, wide), BER_U)
np.save('data/prr_s_AsAu_%s%s-300.npy'%(content, wide), BER_S)


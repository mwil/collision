import os
import sys
import time

sys.path.append('../src')

import numpy as np
from numpy import pi
from phitau_jit import *
from settings import *

start_time = time.time()

SER_S, SER_U = None, None

content = ('same', 'unif')[1]
decision = ('hard', 'soft')[0]
wide = ('', '_wide')[0]

# Query user to enter parameter settings, useful to run scripts in parallel
input_params = (('content', ('same', 'unif'), 'Data content'), ('decision', ('hard', 'soft'), 'Bit decision'), ('wide', ('', '_wide'), 'Time offset interval'))

for var, choices, prompt in input_params:
    resp = None
    while resp not in choices:
        resp = raw_input(prompt+' '+repr(choices) +'? ').lower()
    globals()[var] = resp

# Since the computations are quite long, make sure that existing results should really be deleted!
if os.path.exists('data/prr_s_AsAu_%s_%s%s.npy'%(content, decision, wide)):
    print("The file already exists!")
    resp = None
        
    while resp not in ('yes', 'no', 'y', 'n'):
        resp = raw_input('Do you want to continue (y/n)? ').lower()
                    
    if resp not in ('yes', 'y'):
        exit(0)

if wide: 
    tau_range = tau_range_wide
    Au_range  = Au_range_wide

for tau in tau_range:
    ser_s, ser_u = np.array([]), np.array([])
    
          
    # symbols of (synch'ed, unsynch'ed) sender
    if content in ('same',):
        tmp_syms = np.random.randint(15, size=nsyms+2)
        send_syms = [tmp_syms, tmp_syms]
    else:
        send_syms = [np.random.randint(15, size=nsyms+2), np.random.randint(15, size=nsyms+2)]
    
    send_syms_s, send_syms_u = send_syms[0][1:-1], send_syms[1][1:-1]
    send_chips = map_chips(*send_syms)
    
    for Au in Au_range:
        ser_s_phi, ser_u_phi = np.array([]), np.array([])

        print "ser_contour_AsAu: tau=%.4f, Au=%.4f, runtime: %.2f secs" % (tau, Au, time.time() - start_time)
        start_time = time.time()
        
        RECV_CHIPS_I = detect_i(send_chips[:2], send_chips[2:], phi_range, tau, As, Au)
        RECV_CHIPS_Q = detect_q(send_chips[:2], send_chips[2:], phi_range, tau, As, Au)
        
        for i in xrange(len(phi_range)):
            recv_chips = np.ravel(zip(RECV_CHIPS_I[:,i], RECV_CHIPS_Q[:,i]))

            if decision in ('hard',):
                recv_chips = np.sign(recv_chips)

            recv_syms = detect_syms_corr(recv_chips)[1:-1]
            
            ser_s_phi = np.append(ser_s_phi, sum(recv_syms != send_syms_s) / (1.0*len(recv_syms)))
            ser_u_phi = np.append(ser_u_phi, sum(recv_syms != send_syms_u) / (1.0*len(recv_syms)))
            
        ser_s = np.append(ser_s, np.mean((1-ser_s_phi)**pktlen))
        ser_u = np.append(ser_u, np.mean((1-ser_u_phi)**pktlen))
        
    if SER_S is None:
        SER_S = ser_s
        SER_U = ser_u
    else:
        SER_S = np.vstack((SER_S, ser_s))
        SER_U = np.vstack((SER_U, ser_u))
    
np.save('data/prr_s_AsAu_%s_%s%s.npy'%(content, decision, wide), SER_S)
np.save('data/prr_u_AsAu_%s_%s%s.npy'%(content, decision, wide), SER_U)

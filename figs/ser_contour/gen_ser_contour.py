import os
import sys

sys.path.append('../src')

import numpy as np
from numpy import pi
from phitau import *
from settings import *

SER_S, SER_U = None, None

content = ('same', 'unif')[1]
decision = ('hard', 'soft')[0]

# Query user to enter parameter settings, useful to run scripts in parallel
input_params = (('content', ('same', 'unif'), 'Data content'), ('decision', ('hard', 'soft'), 'Bit decision'))

for var, choices, prompt in input_params:
    resp = None
    while resp not in choices:
        resp = raw_input(prompt+' '+repr(choices) +'? ').lower()
    globals()[var] = resp

if os.path.exists('data/ser_u_Au%.2f_%s_%s.npy'%(Au, content, decision)):
    print("The file already exists!")
    resp = None
        
    while resp not in ('yes', 'no', 'y', 'n'):
        resp = raw_input('Do you want to continue (y/n)? ').lower()
                    
    if resp not in ('yes', 'y'):
        exit(0)

for tau in tau_range:
    print 'tau = %.2f' % (tau)
    ser_s, ser_u = np.array([]), np.array([])
          
    # symbols of (synch'ed, unsynch'ed) sender
    if content in ('same',):
        tmp_syms = np.random.randint(15, size=nsyms+2)
        send_syms = [tmp_syms, tmp_syms]
    else:
        send_syms = [np.random.randint(15, size=nsyms+2), np.random.randint(15, size=nsyms+2)]

    send_syms_s, send_syms_u = send_syms[0][1:-1], send_syms[1][1:-1]  
    send_chips = map_chips(*send_syms)
    
    RECV_CHIPS_I = detect_i(send_chips[:2], send_chips[2:], phi_range, tau, As, Au)
    RECV_CHIPS_Q = detect_q(send_chips[:2], send_chips[2:], phi_range, tau, As, Au)
    
    for i in xrange(len(phi_range)):
        recv_chips = np.ravel(zip(RECV_CHIPS_I[:,i], RECV_CHIPS_Q[:,i])) 

        # slice bits to simulate hard decision decoder
        if decision in ('hard',):
            recv_chips = np.sign(recv_chips)

        recv_syms = detect_syms_corr(recv_chips)[1:-1]
        
        ser_s = np.append(ser_s, sum(recv_syms != send_syms_s) / (1.0*len(recv_syms)))
        ser_u = np.append(ser_u, sum(recv_syms != send_syms_u) / (1.0*len(recv_syms)))
    
    if SER_S is None:
        SER_S = ser_s
        SER_U = ser_u
    else:
        SER_S = np.vstack((SER_S, ser_s))
        SER_U = np.vstack((SER_U, ser_u))
    
np.save('data/ser_s_Au%.2f_%s_%s.npy'%(Au, content, decision), SER_S)
np.save('data/ser_u_Au%.2f_%s_%s.npy'%(Au, content, decision), SER_U)

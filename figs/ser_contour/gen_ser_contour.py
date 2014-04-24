import os
import sys

sys.path.append('../src')

import numpy as np
import phitau_opt as pt
import tools

######################################################
#################      SETTINGS      #################
######################################################
T = 1.0
As = 1.0
Au = np.sqrt(1e4)
nsyms = 1000
nsteps = 750

tau_range = np.linspace(-1.5*T, 1.5*T, num=nsteps)   
phi_range = np.linspace(-np.pi, np.pi, num=nsteps)
######################################################
######################################################

def do_gen(content, decision):
    SER_S, SER_U = None, None

    for tau in tau_range:
        print 'tau = %.2f' % (tau)
        ser_s, ser_u = np.array([]), np.array([])
              
        # symbols of (synch'ed, unsynch'ed) sender
        if content in ('same',):
            tmp_syms = np.random.randint(16, size=nsyms+2)
            send_syms = [tmp_syms, tmp_syms]
        else:
            send_syms = np.random.randint(16, size=2*(nsyms+2)).reshape(2, nsyms+2)

        send_syms_s, send_syms_u = send_syms[0][1:-1], send_syms[1][1:-1]  
        send_chips = pt.map_chips(*send_syms)
        
        RECV_CHIPS_I = pt.detect_i(send_chips[:2], send_chips[2:], phi_range, tau, As, Au)
        RECV_CHIPS_Q = pt.detect_q(send_chips[:2], send_chips[2:], phi_range, tau, As, Au)
        
        for i in xrange(len(phi_range)):
            recv_chips = np.ravel(zip(RECV_CHIPS_I[:,i], RECV_CHIPS_Q[:,i])) 

            # slice bits to simulate hard decision decoder
            if decision in ('hard',):
                recv_chips = np.sign(recv_chips)

            recv_syms = pt.detect_syms_corr(recv_chips)[1:-1]
            
            ser_s = np.append(ser_s, sum(recv_syms != send_syms_s) / (1.0*len(recv_syms)))
            ser_u = np.append(ser_u, sum(recv_syms != send_syms_u) / (1.0*len(recv_syms)))
        
        if SER_S is None:
            SER_S = ser_s
            SER_U = ser_u
        else:
            SER_S = np.vstack((SER_S, ser_s))
            SER_U = np.vstack((SER_U, ser_u))
        
    np.savez_compressed('data/ser_Au%.2f_%s_%s_v2.npz'%(Au, content, decision), 
        tau_range=tau_range, phi_range=phi_range, As=As, Au=Au, SER_S=SER_S, SER_U=SER_U, nsyms=nsyms, nsteps=nsteps)

if __name__ == '__main__':
    input_params = (('content', ('same', 'unif'), 'Data content'), ('decision', ('hard', 'soft'), 'Bit decision'))
    content, decision = tools.get_params(input_params)

    if not tools.overwrite_ok('data/ser_u_Au%.2f_%s_%s.npy'%(Au, content, decision)):
        sys.exit(0)

    do_gen(content, decision)

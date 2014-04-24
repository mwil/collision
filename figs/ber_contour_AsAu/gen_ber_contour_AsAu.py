import sys
import time

sys.path.append('../src')

import numpy as np
import phitau_opt as pt
import tools

######################################################
#################      SETTINGS      #################
######################################################
T       = 1.0
As      = 1.0
nbits   = 125*16
nsteps  = 500
pktlen  = 64 # bits

tau_range_g      = np.linspace(-1.5*T, 1.5*T, num=nsteps)
tau_range_wide   = np.linspace(-4*T, 4*T, num=nsteps)

Au_range_dB      = np.linspace(-10, 51, num=nsteps)
Au_range_g       = np.sqrt(10.0**(Au_range_dB / 10.0))

Au_range_wide_dB = np.linspace(-3, 16, num=nsteps)
Au_range_wide    = np.sqrt(10.0**(Au_range_wide_dB / 10.0))

phi_range        = np.linspace(-np.pi, np.pi, num=nsteps)
######################################################
######################################################

def do_gen(content, wide):
    start_time = time.time()

    tau_range  = (tau_range_wide if wide else tau_range_g)
    Au_range   = (Au_range_wide  if wide else Au_range_g)

    BER_U, BER_S = np.zeros((tau_range.shape[0], Au_range.shape[0]), dtype=np.float), np.zeros((tau_range.shape[0], Au_range.shape[0]), dtype=np.float)

    for tau_idx in xrange(tau_range.shape[0]):
        tau = tau_range[tau_idx]

        if content in ('same',):
            send_chips = np.array([2*np.random.randint(2, size=2*nbits)-1]).reshape((2, nbits))
            send_chips = np.vstack((send_chips, send_chips))
        else:
            send_chips = np.array([2*np.random.randint(2, size=4*nbits)-1]).reshape((4, nbits))
        
        for Au_idx in xrange(Au_range.shape[0]):
            Au = Au_range[Au_idx]
            ber_u_phi, ber_s_phi = np.array([]), np.array([])

            print "ber_contour_AsAu: tau=%8.4f, Au=%9.4f, progress: %5.2f%% runtime: %.2f secs" %\
                (tau, Au, 100*(tau_idx*Au_range.shape[0]+Au_idx)/(1.0*Au_range.shape[0]*tau_range.shape[0]), time.time() - start_time)
            start_time = time.time()
            
            RECV_CHIPS_I = pt.detect_i(send_chips[:2], send_chips[2:], phi_range, tau, As, Au)
            RECV_CHIPS_Q = pt.detect_q(send_chips[:2], send_chips[2:], phi_range, tau, As, Au)
            
            for phi_idx in xrange(len(phi_range)):
                recv_chips       = np.zeros(2*RECV_CHIPS_I.shape[0], dtype=np.float)
                recv_chips[::2]  = np.sign(RECV_CHIPS_I[:,phi_idx])
                recv_chips[1::2] = np.sign(RECV_CHIPS_Q[:,phi_idx])

                usync_chips       = np.zeros(2*send_chips.shape[1], dtype=np.float)
                usync_chips[::2]  = send_chips[2]
                usync_chips[1::2] = send_chips[3]

                sync_chips       = np.zeros(2*send_chips.shape[1], dtype=np.float)
                sync_chips[::2]  = send_chips[0]
                sync_chips[1::2] = send_chips[1]
            
                # ignore chips that are only partially affected here
                ber_u_phi = np.append(ber_u_phi, np.sum(recv_chips[2:-2] != usync_chips[2:-2]) / (1.0*len(recv_chips[2:-2])))
                ber_s_phi = np.append(ber_s_phi, np.sum(recv_chips[2:-2] != sync_chips[2:-2])  / (1.0*len(recv_chips[2:-2])))
        
            BER_S[tau_idx, Au_idx] = np.mean((1-ber_s_phi)**pktlen)
            BER_U[tau_idx, Au_idx] = np.mean((1-ber_u_phi)**pktlen)
        
    np.savez_compressed('data/prr_AsAu_%s%s.npz'%(content, wide), BER_S=BER_S, BER_U=BER_U,
        tau_range=tau_range, nsteps=nsteps, nbits=nbits, As=As, Au_range=Au_range, phi_range=phi_range, pktlen=pktlen)


if __name__ == '__main__':
    input_params = (('content', ('same', 'unif'), 'Data content'), ('wide', ('', '_wide'), 'Time offset interval'))
    content, wide = tools.get_params(input_params)

    if not tools.overwrite_ok('data/prr_AsAu_%s%s.npz'%(content, wide)):
        exit(0)

    do_gen(content, wide)

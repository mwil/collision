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

import sys
import time

sys.path.append('../src')

import numpy as np
import phitau_opt as pt
import tools

######################################################
#################      SETTINGS      #################
######################################################
T = 1.0
nsteps = 250

Au_range_dB      = np.linspace(-10, 51, num=nsteps)
Au_range_wide_dB = np.linspace( -3, 16, num=nsteps)

settings = {
    'T':      T,
    'As':     1.0,
    'nsyms':  128,
    'nsteps': nsteps,
    'pktlen': 16,

    'tau_range_g':    np.linspace(-1.5*T, 1.5*T, num=nsteps),
    'tau_range_wide': np.linspace(-4*T, 4*T, num=nsteps),

    'Au_range_g':     np.sqrt(10.0**(Au_range_dB / 10.0)),
    'Au_range_wide':  np.sqrt(10.0**(Au_range_wide_dB / 10.0)),

    'phi_range':      np.linspace(-np.pi, np.pi, num=nsteps)
}

globals().update(settings)
######################################################
######################################################

def do_gen(content, decision, wide):
    tau_range = (tau_range_wide if wide else tau_range_g)
    Au_range  = (Au_range_wide  if wide else Au_range_g)

    SER_S, SER_U = np.zeros((tau_range.shape[0], Au_range.shape[0]), dtype=np.float), np.zeros((tau_range.shape[0], Au_range.shape[0]), dtype=np.float)

    start_time = time.time()

    for tau_idx in xrange(tau_range.shape[0]):
        tau = tau_range[tau_idx]
              
        # symbols of (synch'ed, unsynch'ed) sender
        if content in ('same',):
            tmp_syms = np.random.randint(16, size=nsyms+2)
            send_syms = np.vstack((tmp_syms, tmp_syms))
        else:
            send_syms = np.random.randint(16, size=2*(nsyms+2)).reshape(2, nsyms+2)
        
        send_syms_s, send_syms_u = send_syms[0][1:-1], send_syms[1][1:-1]
        send_chips = pt.map_chips(*send_syms)
        
        for Au_idx in xrange(Au_range.shape[0]):
            Au = Au_range[Au_idx]
            ser_s_phi, ser_u_phi = np.zeros(len(phi_range)), np.zeros(len(phi_range))

            print "ser_contour_AsAu: tau=%.4f, Au=%.4f, step=%i/%i, runtime: %.2f secs" % (tau, Au, Au_idx, Au_range.shape[0], time.time() - start_time)
            start_time = time.time()
            
            RECV_CHIPS_I = pt.detect_i(send_chips[:2], send_chips[2:], phi_range, tau, As, Au)
            RECV_CHIPS_Q = pt.detect_q(send_chips[:2], send_chips[2:], phi_range, tau, As, Au)
            
            for phi_idx in xrange(phi_range.shape[0]):
                # Interleave the I and Q phase (this is faster than np.ravel)
                recv_chips = np.zeros(2*RECV_CHIPS_I.shape[0], dtype=np.float)
                recv_chips[::2]  = RECV_CHIPS_I[:,phi_idx]
                recv_chips[1::2] = RECV_CHIPS_Q[:,phi_idx]

                if decision in ('hard',):
                    recv_chips = np.sign(recv_chips)

                recv_syms = pt.detect_syms_corrcoef(recv_chips)[1:-1]
                
                ser_s_phi[phi_idx] = np.sum(recv_syms != send_syms_s) / (1.0*len(recv_syms))
                ser_u_phi[phi_idx] = np.sum(recv_syms != send_syms_u) / (1.0*len(recv_syms))
                
            SER_S[tau_idx, Au_idx] = np.mean((1-ser_s_phi)**pktlen)
            SER_U[tau_idx, Au_idx] = np.mean((1-ser_u_phi)**pktlen)          
        
    np.savez_compressed('data/prr_AsAu_%s_%s%s.npz'%(content, decision, wide), SER_S=SER_S, SER_U=SER_U, 
        tau_range=tau_range, nsteps=nsteps, nsyms=nsyms, As=As, Au_range=Au_range, phi_range=phi_range)


if __name__ == '__main__':
    input_params = (('content', ('same', 'unif'), 'Data content'), ('decision', ('hard', 'soft'), 'Bit decision'), ('wide', ('', '_wide'), 'Time offset interval'))
    content, decision, wide = tools.get_params(input_params)

    if not tools.overwrite_ok('data/prr_AsAu_%s_%s%s.npz'%(content, decision, wide)):
        sys.exit(0)

    do_gen(content, decision, wide)

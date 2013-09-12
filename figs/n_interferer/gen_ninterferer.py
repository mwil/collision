import sys
sys.path.append('../src')

import numpy as np
import phitau_n as ptn
import phitau_opt as pt

import tools

######################################################
#################      SETTINGS      #################
######################################################
nphi           = 1500
num_interferer = 8

settings = {
    'T':      1.0,
    'tau':    0.0,
    'As':     1.0,
    'Au':	  1./np.sqrt(2),
    'Au_':	  1./np.sqrt(2),
    'nsyms':  500,
    'pktlen': 16,

    'phi_range': np.random.uniform(-np.pi, np.pi, size=nphi)
}

globals().update(settings)
######################################################
######################################################

def gen_n_interf(mode='n'):
	'''@param mode: [n] refers to the n interferer mode, we use n low-power interferers with half the power of the sync signal
	                [1] refers to one strong interferer that has the sum of n interferers as its power level.
	'''
	SER_S = None

	for ninterf in np.arange(0, num_interferer+1):
		print 'Starting to generate for %i interferers, mode is %s' % (ninterf, mode)
		ser_s = np.array([])

		if mode in ('1',):
			# we use a single interferer with the same power as n interferers
			Au = Au_ * np.sqrt(ninterf)
			if ninterf:
				ninterf = 1
		else:
			# we use n low-power interferers with default power setting
			Au = Au_

		if ninterf == 0:
			phi_range = np.zeros((1,nphi), dtype=np.float)
		else:
			#phi_range = np.repeat(-pi, nphi*ninterf).reshape(ninterf, nphi)
			phi_range = np.random.uniform(-np.pi, np.pi, size=nphi*ninterf).reshape(ninterf, nphi)
		
		if content in ('unif',):
			send_syms = np.random.randint(16, size=(ninterf+1)*(nsyms+2)).reshape(ninterf+1, nsyms+2)
		else:
			# everyone gets the same symbols to send
			sync_syms = np.random.randint(16, size=nsyms+2)
			send_syms = np.vstack([sync_syms]*(ninterf+1))

		send_syms_s = send_syms[0][1:-1]
		send_chips = ptn.map_chips_n(*send_syms)
	    
		RECV_CHIPS_I = ptn.detect_i_n(ninterf, send_chips[:2], send_chips[2:], phi_range, tau, As, Au)
		RECV_CHIPS_Q = ptn.detect_q_n(ninterf, send_chips[:2], send_chips[2:], phi_range, tau, As, Au)

		for phi_idx in xrange(nphi):
			#recv_chips = np.ravel(zip(RECV_CHIPS_I[:,i], RECV_CHIPS_Q[:,i])) 
			recv_chips = np.zeros(2*RECV_CHIPS_I.shape[0], dtype=np.float)
			recv_chips[::2]  = RECV_CHIPS_I[:,phi_idx]
			recv_chips[1::2] = RECV_CHIPS_Q[:,phi_idx]

			# slice bits to simulate hard decision decoder
			if decision in ('hard',):
				recv_chips = np.sign(recv_chips)

			recv_syms = pt.detect_syms_corrcoef(recv_chips)[1:-1]
	        
			ser_s = np.append(ser_s, np.sum(recv_syms != send_syms_s) / (1.0*len(recv_syms)))
	    
		if SER_S is None:
			SER_S = ser_s
		else:
			SER_S = np.vstack((SER_S, ser_s))

		print 'PRR = ', np.mean((1-ser_s)**pktlen)

	np.save('data/ser_s_%s_%s_%s.npy'%(content, decision, mode), SER_S)

if __name__ == '__main__':
	input_params = (('content', ('same', 'unif'), 'Data content'), ('decision', ('hard', 'soft'), 'Bit decision'))
	content, decision = tools.get_params(input_params)

	if not tools.overwrite_ok('data/ser_s_%s_%s_n.npy'%(content, decision)):
		sys.exit()

	gen_n_interf(mode='n')
	gen_n_interf(mode='1')

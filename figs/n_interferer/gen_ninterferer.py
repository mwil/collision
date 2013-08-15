import os
import sys

sys.path.append('../src')

import numpy as np
from numpy import pi
from phitau_n import *
from settings import *

tau = 0.0

content = ('same', 'unif')[1]
decision = ('hard', 'soft')[1]

#### Query user to enter parameter settings, useful to run scripts in parallel ####
input_params = (('content', ('same', 'unif'), 'Data content'), ('decision', ('hard', 'soft'), 'Bit decision'))

for var, choices, prompt in input_params:
	resp = None
	while resp not in choices:
		resp = raw_input(prompt+' '+repr(choices) +'? ').lower()
	globals()[var] = resp

if os.path.exists('data/ser_s_%s_%s_n.npy'%(content, decision)):
	print("The file already exists!")
	resp = None

	while resp not in ('yes', 'no', 'y', 'n'):
		resp = raw_input('Do you want to continue (y/n)? ').lower()

	if resp not in ('yes', 'y'):
		exit(0)
####################################################################################

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
			phi_range = np.repeat(0, nphi).reshape(1, nphi)
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
		send_chips = map_chips(*send_syms)
	    
		RECV_CHIPS_I = detect_i(ninterf, send_chips[:2], send_chips[2:], phi_range, tau, As, Au)
		RECV_CHIPS_Q = detect_q(ninterf, send_chips[:2], send_chips[2:], phi_range, tau, As, Au)

		for i in xrange(nphi):
			recv_chips = np.ravel(zip(RECV_CHIPS_I[:,i], RECV_CHIPS_Q[:,i])) 

			# slice bits to simulate hard decision decoder
			if decision in ('hard',):
				recv_chips = np.sign(recv_chips)

			recv_syms = detect_syms_corr(recv_chips)[1:-1]
	        
			ser_s = np.append(ser_s, sum(recv_syms != send_syms_s) / (1.0*len(recv_syms)))
	    
		if SER_S is None:
			SER_S = ser_s
		else:
			SER_S = np.vstack((SER_S, ser_s))

		print 'PRR = ', np.mean((1-ser_s)**pktlen)

	np.save('data/ser_s_%s_%s_%s.npy'%(content, decision, mode), SER_S)

if __name__ == '__main__':
	gen_n_interf(mode='n')
	gen_n_interf(mode='1')

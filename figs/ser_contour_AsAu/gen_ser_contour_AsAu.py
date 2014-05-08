from __future__ import print_function

import argparse
import os
import sys
import time

sys.path.append('../src')

import numpy as np
import phitau_opt as pt
import tools

# multiprocessing stuff
import multiprocessing as mp
from functools import partial

######################################################
#################      SETTINGS      #################
######################################################
T = 1.0
nsteps = 32

Au_range_norm_dB = np.linspace(-10, 51, num=nsteps)
Au_range_wide_dB = np.linspace(-3., 16, num=nsteps)

settings = {
	'T':      T,
	'As':     1.0,
	'nsyms':  128,
	'nsteps': nsteps,
	'pktlen': 8,

	'Au_range_norm':  np.sqrt(10.0**(Au_range_norm_dB / 10.0)),
	'Au_range_wide':  np.sqrt(10.0**(Au_range_wide_dB / 10.0)),
	'tau_range_norm': np.linspace(-1.5*T, 1.5*T, num=nsteps),
	'tau_range_wide': np.linspace(-4.0*T, 4.0*T, num=nsteps),
	'phi_range':      np.linspace(-np.pi, np.pi, num=nsteps)
}

globals().update(settings)
######################################################
######################################################

def do_gen(part, content, decision, wide, numthreads):
	tau_range   = (tau_range_wide   if wide else tau_range_norm)
	Au_range    = (Au_range_wide    if wide else Au_range_norm)
	Au_range_dB = (Au_range_wide_dB if wide else Au_range_norm_dB)

	start_time = time.time()

	tau_range = np.split(tau_range, numthreads)[part]

	PRR_S = np.zeros((tau_range.shape[0], Au_range.shape[0]))
	PRR_U = np.zeros((tau_range.shape[0], Au_range.shape[0]))

	SER_S_PHI = np.zeros((tau_range.shape[0], phi_range.shape[0]))
	SER_U_PHI = np.zeros((tau_range.shape[0], phi_range.shape[0]))

	for tau_idx, tau in enumerate(tau_range):
		# symbols of (synch'ed, unsynch'ed) sender
		if content in ('same',):
			tmp_syms= np.random.randint(16, size=nsyms+2)
			send_syms = np.vstack((tmp_syms, tmp_syms))
		else:
			send_syms = np.random.randint(16, size=2*(nsyms+2)).reshape(2, nsyms+2)
		
		send_syms_s, send_syms_u = send_syms[0][1:-1], send_syms[1][1:-1]
		send_chips = pt.map_chips(*send_syms)

		#RECV_CHIPS_I_A = pt.detect_i(send_chips[:2], send_chips[2:], phi_range, tau, As, Au_range)
		#RECV_CHIPS_Q_A = pt.detect_q(send_chips[:2], send_chips[2:], phi_range, tau, As, Au_range)
		
		for Au_idx, Au in enumerate(Au_range):
			print('%s: tau=%7.3f, tau_step=(%3i/%3i), Au=%7.3f, Au_step=(%3i/%3i), runtime: %5.2f secs' %\
				(sys.argv[0], tau, tau_idx+1, tau_range.shape[0], Au, Au_idx+1, Au_range.shape[0], time.time() - start_time))
			start_time = time.time()

			RECV_CHIPS_I = pt.detect_i(send_chips[:2], send_chips[2:], phi_range, tau, As, Au)
			RECV_CHIPS_Q = pt.detect_q(send_chips[:2], send_chips[2:], phi_range, tau, As, Au)
			
			for phi_idx, phi in enumerate(phi_range):
				# Interleave the I and Q phase (this is faster than np.ravel)
				recv_chips       = np.zeros(2*RECV_CHIPS_I.shape[0])
				recv_chips[ ::2] = RECV_CHIPS_I[:,phi_idx]
				recv_chips[1::2] = RECV_CHIPS_Q[:,phi_idx]

				if decision in ('hard',):
					recv_chips = np.sign(recv_chips)

				recv_syms = pt.detect_syms_corr(recv_chips)[1:-1]
				
				SER_S_PHI[tau_idx, phi_idx] = np.sum(recv_syms != send_syms_s) / (1.0*len(recv_syms))
				SER_U_PHI[tau_idx, phi_idx] = np.sum(recv_syms != send_syms_u) / (1.0*len(recv_syms))
				
			PRR_S[tau_idx, Au_idx] = np.mean((1.0-SER_S_PHI[tau_idx,:])**pktlen)
			PRR_U[tau_idx, Au_idx] = np.mean((1.0-SER_U_PHI[tau_idx,:])**pktlen)

	np.savez_compressed('data/prr_AsAu_%s_%s%s_part%i.npz'%(content, decision, wide, part), 
		PRR_S=PRR_S, PRR_U=PRR_U, SER_S_PHI=SER_S_PHI, SER_U_PHI=SER_U_PHI,
		tau_range=tau_range, nsteps=nsteps, nsyms=nsyms, As=As, Au_range=Au_range, phi_range=phi_range, Au_range_dB=Au_range_dB)



if __name__ == '__main__':
	# Query user to enter parameter settings, useful to run scripts in parallel
	argp = argparse.ArgumentParser()
	argp.add_argument('content',  choices=('same', 'unif'), help='Relation between data content in the two transmitted packets')
	argp.add_argument('decision', choices=('soft', 'hard'), help='Bit decision for DSSS decoding (SDD, HDD)')
	argp.add_argument('-w', '--wide', action='store_true', help='Wide interval of time offsets used (-4T to 4T instead of -1.5T to 1.5T)')
	argp.add_argument('-n', '--numthreads', type=int, default=1, help="Number of threads to start in the worker pool (default:1)")

	args = argp.parse_args()

	wide = ('_wide' if args.wide else '')

	if not tools.overwrite_ok('data/prr_AsAu_%s_%s%s.npz'%(args.content, args.decision, wide)):
		exit()

	pool = mp.Pool(args.numthreads)
	pool.map(partial(do_gen, content=args.content, decision=args.decision, wide=wide, numthreads=args.numthreads), list(range(args.numthreads)))

	PRR_S, PRR_U = None, None
	SER_S_PHI, SER_U_PHI = None, None

	tau_range   = (tau_range_wide   if wide else tau_range_norm)
	Au_range    = (Au_range_wide    if wide else Au_range_norm)
	Au_range_dB = (Au_range_wide_dB if wide else Au_range_norm_dB)

	# combine stuff again and cleanup
	for part in range(args.numthreads):
		data = np.load('data/prr_AsAu_%s_%s%s_part%i.npz'%(args.content, args.decision, wide, part))

		for vname in ('PRR_S', 'PRR_U', 'SER_S_PHI', 'SER_U_PHI'):
			if locals()[vname] is None:
				locals()[vname] = data[vname]
			else:
				locals()[vname] = np.vstack((locals()[vname], data[vname]))

		os.remove('data/prr_AsAu_%s_%s%s_part%i.npz'%(args.content, args.decision, wide, part))

	np.savez_compressed('data/prr_AsAu_%s_%s%s.npz'%(args.content, args.decision, wide), 
		PRR_S=PRR_S, PRR_U=PRR_U, SER_S_PHI=SER_S_PHI, SER_U_PHI=SER_U_PHI,
		tau_range=tau_range, As=As, Au_range=Au_range, phi_range=phi_range, Au_range_dB=Au_range_dB,
		nsteps=nsteps, nsyms=nsyms, T=T, pktlen=pktlen)

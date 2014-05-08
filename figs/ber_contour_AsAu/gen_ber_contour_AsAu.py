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
T       = 1.0
As      = 1.0
nbits   = 125*16
nsteps  = 256
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

def do_gen(part, content, wide, numthreads):
	start_time = time.time()

	tau_range  = (tau_range_wide if wide else tau_range_g)
	Au_range   = (Au_range_wide  if wide else Au_range_g)

	tau_range = np.split(tau_range, numthreads)[part]

	PRR_S = np.zeros((tau_range.shape[0], Au_range.shape[0]))
	PRR_U = np.zeros((tau_range.shape[0], Au_range.shape[0]))

	for tau_idx, tau in enumerate(tau_range):
		if content in ('same',):
			send_chips = np.array([2*np.random.randint(2, size=2*nbits)-1]).reshape((2, nbits))
			send_chips = np.vstack((send_chips, send_chips))
		else:
			send_chips = np.array([2*np.random.randint(2, size=4*nbits)-1]).reshape((4, nbits))
		
		for Au_idx, Au in enumerate(Au_range):
			ber_u_phi = np.zeros(phi_range.shape[0])
			ber_s_phi = np.zeros(phi_range.shape[0])

			print('%s: tau=%7.3f, tau_step=(%3i/%3i), Au=%7.3f, Au_step=(%3i/%3i), runtime: %5.2f secs' %\
				(sys.argv[0], tau, tau_idx+1, tau_range.shape[0], Au, Au_idx+1, Au_range.shape[0], time.time() - start_time))

			start_time = time.time()
			
			RECV_CHIPS_I = pt.detect_i(send_chips[:2], send_chips[2:], phi_range, tau, As, Au)
			RECV_CHIPS_Q = pt.detect_q(send_chips[:2], send_chips[2:], phi_range, tau, As, Au)
			
			for phi_idx, phi in enumerate(phi_range):
				recv_chips       = np.zeros(2*RECV_CHIPS_I.shape[0])
				recv_chips[::2]  = np.sign(RECV_CHIPS_I[:,phi_idx])
				recv_chips[1::2] = np.sign(RECV_CHIPS_Q[:,phi_idx])

				usync_chips       = np.zeros(2*send_chips.shape[1])
				usync_chips[::2]  = send_chips[2]
				usync_chips[1::2] = send_chips[3]

				sync_chips       = np.zeros(2*send_chips.shape[1])
				sync_chips[::2]  = send_chips[0]
				sync_chips[1::2] = send_chips[1]
			
				# ignore chips that are only partially affected here
				ber_s_phi[phi_idx] = np.sum(recv_chips[2:-2] != sync_chips[2:-2])  / (1.0*len(recv_chips[2:-2]))
				ber_u_phi[phi_idx] = np.sum(recv_chips[2:-2] != usync_chips[2:-2]) / (1.0*len(recv_chips[2:-2]))
		
			PRR_S[tau_idx, Au_idx] = np.mean((1-ber_s_phi)**pktlen)
			PRR_U[tau_idx, Au_idx] = np.mean((1-ber_u_phi)**pktlen)
		
	np.savez_compressed('data/prr_AsAu_%s%s_part%i.npz'%(content, wide, part), PRR_S=PRR_S, PRR_U=PRR_U,
		tau_range=tau_range, As=As, Au_range=Au_range, phi_range=phi_range, 
		pktlen=pktlen, nsteps=nsteps, nbits=nbits)


if __name__ == '__main__':
	# Query user to enter parameter settings, useful to run scripts in parallel
	argp = argparse.ArgumentParser()
	argp.add_argument('content',  choices=('same', 'unif'), help='Relation between data content in the two transmitted packets')
	argp.add_argument('-w', '--wide', action='store_true', help='Wide interval of time offsets used (-4T to 4T instead of -1.5T to 1.5T)')
	argp.add_argument('-n', '--numthreads', type=int, default=1, help="Number of threads to start in the worker pool (default:1)")

	args = argp.parse_args()

	wide = ('_wide' if args.wide else '')

	if not tools.overwrite_ok('data/prr_AsAu_%s%s.npz'%(args.content, wide)):
		exit()

	pool = mp.Pool(args.numthreads)
	pool.map(partial(do_gen, content=args.content, wide=wide, numthreads=args.numthreads), list(range(args.numthreads)))

	PRR_S, PRR_U = None, None

	tau_range   = (tau_range_wide   if wide else tau_range_g)
	Au_range    = (Au_range_wide    if wide else Au_range_g)
	Au_range_dB = (Au_range_wide_dB if wide else Au_range_dB)

	# combine stuff again and cleanup
	for part in range(args.numthreads):
		data = np.load('data/prr_AsAu_%s%s_part%i.npz'%(args.content, wide, part))

		for vname in ('PRR_S', 'PRR_U'):
			if locals()[vname] is None:
				locals()[vname] = data[vname]
			else:
				locals()[vname] = np.vstack((locals()[vname], data[vname]))

		os.remove('data/prr_AsAu_%s%s_part%i.npz'%(args.content, wide, part))

	np.savez_compressed('data/prr_AsAu_%s%s.npz'%(args.content, wide), 
		PRR_S=PRR_S, PRR_U=PRR_U,
		tau_range=tau_range, As=As, Au_range=Au_range, phi_range=phi_range, Au_range_dB=Au_range_dB,
		nsteps=nsteps, nbits=nbits, T=T, pktlen=pktlen)

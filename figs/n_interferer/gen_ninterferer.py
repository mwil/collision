# Copyright 2013-2014 Matthias Wilhelm

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

from __future__ import print_function

import argparse
import sys
sys.path.append("../../src")

import numpy as np
import phitau_opt as pt
import phitau_n as ptn   # modified code for n concurrent signals

import tools

######################################################
#################      SETTINGS      #################
######################################################
nsteps         = 256
num_interferer = 8

settings = {
    "T":      1.0,
    "tau":    0.0,
    "As":     1.0,
    "Au":     1./np.sqrt(2),
    "Au_":    1./np.sqrt(2),
    "nsyms":  256,
	"nsteps": nsteps,
    "pktlen": 16,
	"num_interferer": num_interferer,

    "phi_range": None
}

globals().update(settings)
######################################################
######################################################

def gen_n_interf(content, decision, mode="n"):
	"""@param mode: [n] refers to the n interferer mode, we use n low-power interferers with half the power of the sync signal
	                [1] refers to one strong interferer that has the sum of n interferers as its power level.
	"""
	SER_S = np.empty((num_interferer+1, nsteps))

	for ninterf in np.arange(0, num_interferer+1):
		print("Starting to generate for %i interferers, mode is %s" % (ninterf, mode))

		if mode in ("1",):
			# we use a single interferer with the same power as n interferers
			Au = Au_ * np.sqrt(ninterf)
			if ninterf:
				ninterf = 1
		else:
			# we use n low-power interferers with default power setting
			Au = Au_

		if ninterf == 0:
			phi_range = np.zeros((1,nsteps))
		else:
			phi_range = np.random.uniform(-np.pi, np.pi, size=nsteps*ninterf).reshape(ninterf, nsteps)

		if content in ("unif",):
			send_syms = np.random.randint(16, size=(ninterf+1)*(nsyms+2)).reshape(ninterf+1, nsyms+2)
		else:
			# everyone gets the same symbols to send
			sync_syms = np.random.randint(16, size=nsyms+2)
			send_syms = np.vstack([sync_syms]*(ninterf+1))

		send_syms_s = send_syms[0][1:-1]
		send_chips = ptn.map_chips_n(*send_syms)

		RECV_CHIPS_I = ptn.detect_i_n(ninterf, send_chips[:2], send_chips[2:], phi_range, tau, As, Au)
		RECV_CHIPS_Q = ptn.detect_q_n(ninterf, send_chips[:2], send_chips[2:], phi_range, tau, As, Au)

		for phi_idx in range(nsteps):
			recv_chips = np.zeros(2*RECV_CHIPS_I.shape[0])
			recv_chips[ ::2] = RECV_CHIPS_I[:,phi_idx]
			recv_chips[1::2] = RECV_CHIPS_Q[:,phi_idx]

			# slice bits to simulate hard decision decoder
			if decision in ("hard",):
				recv_chips = np.sign(recv_chips)

			recv_syms = pt.detect_syms_corrcoef(recv_chips)[1:-1]

			SER_S[ninterf, phi_idx] = np.sum(recv_syms != send_syms_s) / (1.0*len(recv_syms))

		print("PRR = ", np.mean((1.0-SER_S[ninterf,:])**pktlen))

	np.savez_compressed("data/ser_s_%s_%s_%s.npz"%(content, decision, mode), SER_S=SER_S, **settings)

if __name__ == "__main__":
	argp = argparse.ArgumentParser()
	argp.add_argument("content",  choices=("same", "unif"), help="Relation between data content in the two transmitted packets")
	argp.add_argument("decision", choices=("soft", "hard"), help="Bit decision for DSSS decoding (SDD, HDD)")

	args = argp.parse_args()

	if not tools.overwrite_ok("data/ser_s_%s_%s_n.npy"%(args.content, args.decision)):
		sys.exit()

	gen_n_interf(args.content, args.decision, mode="n")
	gen_n_interf(args.content, args.decision, mode="1")

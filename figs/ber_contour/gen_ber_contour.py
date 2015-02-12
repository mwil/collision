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
import time

sys.path.append("../../src")

import numpy as np
import phitau_opt as pt

import tools

######################################################
#################      SETTINGS      #################
######################################################
T = 1.0
nsteps = 250

settings = {
	"T":      T,
	"As":     1.0,
	"Au":     100.0,
	"nbits":  1024,
	"nsteps": nsteps,

	"tau_range": np.linspace(-1.5*T, 1.5*T, num=nsteps),
	"phi_range": np.linspace(-np.pi, np.pi, num=nsteps)
}

globals().update(settings)
######################################################
######################################################

def do_gen(content):
	start_time = time.time()

	BER_U = np.zeros((tau_range.shape[0], phi_range.shape[0]))
	BER_S = np.zeros((tau_range.shape[0], phi_range.shape[0]))

	for tau_idx in range(len(tau_range)):
		tau = tau_range[tau_idx]

		print("Step time for tau = %.3f: %.3fs"% (tau, time.time() - start_time))
		start_time = time.time()

		if content in ("same", ):
			send_chips = np.array([2*np.random.randint(2, size=2*nbits)-1]).reshape((2, nbits))
			send_chips = np.vstack((send_chips, send_chips))
		else:
			send_chips = np.array([2*np.random.randint(2, size=4*nbits)-1]).reshape((4, nbits))

		RECV_CHIPS_I = pt.detect_i(send_chips[:2], send_chips[2:], phi_range, tau, As, Au)
		RECV_CHIPS_Q = pt.detect_q(send_chips[:2], send_chips[2:], phi_range, tau, As, Au)

		for phi_idx in range(len(phi_range)):
			recv_chips       = np.empty(2*RECV_CHIPS_I.shape[0])
			recv_chips[ ::2] = np.sign(RECV_CHIPS_I[:,phi_idx])
			recv_chips[1::2] = np.sign(RECV_CHIPS_Q[:,phi_idx])

			sync_chips       = np.empty(2*send_chips.shape[1])
			sync_chips[ ::2] = send_chips[0]
			sync_chips[1::2] = send_chips[1]

			usync_chips       = np.empty(2*send_chips.shape[1])
			usync_chips[ ::2] = send_chips[2]
			usync_chips[1::2] = send_chips[3]

			# ignore chips that are only partially affected here (the outermost two chips)
			BER_U[tau_idx, phi_idx] = np.sum(recv_chips[2:-2] != usync_chips[2:-2]) / (1.0*len(recv_chips[2:-2]))
			BER_S[tau_idx, phi_idx] = np.sum(recv_chips[2:-2] != sync_chips[2:-2])  / (1.0*len(recv_chips[2:-2]))

	np.savez_compressed("data/ber_Au%.2f_%s.npz"%(Au, content), BER_S=BER_S, BER_U=BER_U, **settings)


if __name__ == "__main__":
	argp = argparse.ArgumentParser()
	argp.add_argument("content",  choices=("same", "unif"), help="Relation between data content in the two transmitted packets")

	args = argp.parse_args()

	if not tools.overwrite_ok("data/ber_Au%.2f_%s.npz"%(Au, args.content)):
		exit()

	do_gen(args.content)

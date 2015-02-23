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
import os
import sys

sys.path.append("../../src")

import numpy as np
import phitau_opt as pt
import tools

######################################################
#################      SETTINGS      #################
######################################################
T = 1.0
nsteps = 256

settings = {
	"As":     1.0,
	"Au":     np.sqrt(1e4),
	"nsyms":  256,
	"nsteps": nsteps,

	"tau_range": np.linspace(-1.5*T, 1.5*T, num=nsteps),
	"phi_range": np.linspace(-np.pi, np.pi, num=nsteps)
}

globals().update(settings)
######################################################
######################################################

def do_gen(content, decision):
	SER_S = np.empty((tau_range.shape[0], phi_range.shape[0]))
	SER_U = np.empty((tau_range.shape[0], phi_range.shape[0]))

	for tau_idx, tau in enumerate(tau_range):
		print("tau = %.2f" % (tau))

		# symbols of (synch"ed, unsynch"ed) sender
		if content in ("same",):
			tmp_syms = np.random.randint(16, size=nsyms+2)
			send_syms = [tmp_syms, tmp_syms]
		else:
			send_syms = np.random.randint(16, size=2*(nsyms+2)).reshape(2, nsyms+2)

		send_syms_s, send_syms_u = send_syms[0][1:-1], send_syms[1][1:-1]
		send_chips = pt.map_chips(*send_syms)

		RECV_CHIPS_I = pt.detect_i(send_chips[:2], send_chips[2:], phi_range, tau, As, Au)
		RECV_CHIPS_Q = pt.detect_q(send_chips[:2], send_chips[2:], phi_range, tau, As, Au)

		for phi_idx in range(len(phi_range)):
			recv_chips       = np.empty(2*RECV_CHIPS_I.shape[0])
			recv_chips[ ::2] = RECV_CHIPS_I[:,phi_idx]
			recv_chips[1::2] = RECV_CHIPS_Q[:,phi_idx]

			# slice bits to simulate hard decision decoder
			if decision in ("hard",):
				recv_chips = np.sign(recv_chips)

			recv_syms = pt.detect_syms_corr(recv_chips)[1:-1]

			SER_S[tau_idx, phi_idx] = sum(recv_syms != send_syms_s) / (1.0*len(recv_syms))
			SER_U[tau_idx, phi_idx] = sum(recv_syms != send_syms_u) / (1.0*len(recv_syms))

	np.savez_compressed("data/ser_Au%.2f_%s_%s_v2.npz"%(Au, content, decision),
                        SER_S=SER_S, SER_U=SER_U, **settings)

if __name__ == "__main__":
	argp = argparse.ArgumentParser()
	argp.add_argument("content",  choices=("same", "unif"), help="Relation between data content in the two transmitted packets")
	argp.add_argument("decision", choices=("soft", "hard"), help="Bit decision for DSSS decoding (SDD, HDD)")

	args = argp.parse_args()

	if not tools.overwrite_ok("data/ser_Au%.2f_%s_%s_v2.npz"%(Au, args.content, args.decision)):
		sys.exit(0)

	do_gen(args.content, args.decision)

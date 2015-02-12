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

import numpy as np

T = 1.0

chips = {0:np.array([1,1,0,1,1,0,0,1,1,1,0,0,0,0,1,1,0,1,0,1,0,0,1,0,0,0,1,0,1,1,1,0]),
         8:np.array([1,0,0,0,1,1,0,0,1,0,0,1,0,1,1,0,0,0,0,0,0,1,1,1,0,1,1,1,1,0,1,1])}

# building the chipping sequences by shifting ...
for sym in range(1, 8):
    chips[sym]   = np.concatenate((chips[sym-1][-4:], chips[sym-1][:-4]))
    chips[sym+8] = np.concatenate((chips[sym+7][-4:], chips[sym+7][:-4]))

# change chips to constellation {0,1} -> {-1,1}
for sym in chips.keys():
    chips[sym] = 2*chips[sym] - 1

# Remain silent during this symbol (if symbol is given as 'None')
chips[None] = np.array([0]*32)

chips_a = np.vstack([chips[i] for i in range(16)])

def detect_i_n(ninterf, alpha, beta_n, phi_range_n, tau, As, Au):
	_tau_   = np.remainder(tau, 2*T)
	_tau_n_ = np.remainder(tau+T, 2*T)
	omega_p = np.pi/(2*T)
	phi_p   = omega_p * tau

	k_tau   = np.int(np.floor(tau / (2*T)))
	k_tau_n = np.int(np.floor((tau+T) / (2*T)))

	_, ALPHA = np.meshgrid(phi_range_n[0], alpha[0])

	result = (T/2) * ALPHA * As

	for interf in range(ninterf):
		phi_range = phi_range_n[interf]
		PHI_C, _  = np.meshgrid(phi_range, alpha[0])

		beta = beta_n[2*interf:(2*interf)+2]
		beta_i = np.concatenate((beta[0], np.zeros(max(1, 2*abs(k_tau)))))
		beta_q = np.concatenate((beta[1], np.zeros(max(1, 2*abs(k_tau_n)))))

		bkn_i = np.roll(beta_i, k_tau + 1)  [:len(alpha[0])]
		bk_i  = np.roll(beta_i, k_tau)      [:len(alpha[0])]
		bkn_q = np.roll(beta_q, k_tau_n + 1)[:len(alpha[1])]
		bk_q  = np.roll(beta_q, k_tau_n)    [:len(alpha[1])]

		arg1 = np.cos(phi_p) * (_tau_ * bkn_i + (2*T - _tau_) * bk_i)
		arg2 = ((2*T) / np.pi) * np.sin(phi_p) * (bkn_i - bk_i)
		arg3 = np.sin(phi_p) * (_tau_n_ * bkn_q + (2*T - _tau_n_) * bk_q)
		arg4 = ((2*T) / np.pi) * np.cos(phi_p) * (bkn_q - bk_q)

		_, ARG12 = np.meshgrid(phi_range, (arg1 - arg2))
		_, ARG34 = np.meshgrid(phi_range, (arg3 + arg4))

		result += (Au/4.0) * (np.cos(PHI_C) * ARG12 - np.sin(PHI_C) * ARG34)

	if Au > 0 and ninterf != 0:
		return result / ((T/2) * As * Au)
	else:
		return result / ((T/2) * As)

def detect_q_n(ninterf, alpha, beta_n, phi_range_n, tau, As, Au):
	_tau_   = np.remainder(tau, 2*T)
	_tau_p_ = np.remainder(tau-T, 2*T)
	omega_p = np.pi/(2*T)
	phi_p   = omega_p * tau

	k_tau   = np.int(np.floor(tau / (2*T)))
	k_tau_p = np.int(np.floor((tau-T) / (2*T)))

	_, ALPHA = np.meshgrid(phi_range_n[0], alpha[1])

	result = (T/2) * ALPHA * As

	for interf in range(ninterf):
		phi_range = phi_range_n[interf]
		PHI_C, _  = np.meshgrid(phi_range, alpha[1])

		beta = beta_n[2*interf:(2*interf)+2]
		# fill negative indices with zeros
		beta_i = np.concatenate((beta[0], np.zeros(max(1, 2*abs(k_tau_p)))))
		beta_q = np.concatenate((beta[1], np.zeros(max(1, 2*abs(k_tau)))))

		bkn_i = np.roll(beta_i, k_tau_p + 1)[:len(alpha[0])]
		bk_i  = np.roll(beta_i, k_tau_p)    [:len(alpha[0])]
		bkn_q = np.roll(beta_q, k_tau + 1)  [:len(alpha[1])]
		bk_q  = np.roll(beta_q, k_tau)      [:len(alpha[1])]

		arg1 = np.cos(phi_p) * (_tau_ * bkn_q + (2*T - _tau_) * bk_q)
		arg2 = ((2*T) / np.pi) * np.sin(phi_p) * (bkn_q - bk_q)
		arg3 = np.sin(phi_p) * (_tau_p_ * bkn_i + (2*T - _tau_p_) * bk_i)
		arg4 = ((2*T) / np.pi) * np.cos(phi_p) * (bkn_i - bk_i)

		_, ARG12 = np.meshgrid(phi_range, (arg1 - arg2))
		_, ARG34 = np.meshgrid(phi_range, (arg3 + arg4))

		result += (Au/4.0) * (np.cos(PHI_C) * ARG12 - np.sin(PHI_C) * ARG34)

	if Au > 0 and ninterf != 0:
		return result / ((T/2) * As * Au * ninterf)
	else:
		return result / ((T/2) * As)

def map_chips_n(vsyms, *args):
	chips_i, chips_q = {}, {}

	# Split chipping sequences in I and Q
	for sym in chips.iterkeys():
		chips_i[sym] = chips[sym][ ::2]
		chips_q[sym] = chips[sym][1::2]

	alpha_i, alpha_q = np.array([], dtype=np.int), np.array([], dtype=np.int)

	for vsym in vsyms:
		alpha_i = np.concatenate((alpha_i, chips_i[vsym]))
		alpha_q = np.concatenate((alpha_q, chips_q[vsym]))

	result = np.array([alpha_i, alpha_q])

	for asyms in args:
		beta_i, beta_q = np.array([], dtype=np.int), np.array([], dtype=np.int)

		for asym in asyms:
			beta_i = np.concatenate((beta_i, chips_i[asym]))
			beta_q = np.concatenate((beta_q, chips_q[asym]))

		result = np.vstack([result, np.array([beta_i, beta_q])])

	return result

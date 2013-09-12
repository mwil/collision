from numpy import *
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
    _tau_ = remainder(tau, 2*T)
    _tau_n_ = remainder(tau+T, 2*T)
    omega_p = pi/(2*T)
    phi_p = omega_p * tau
    
    k_tau = int(floor(tau / (2*T)))
    k_tau_n = int(floor((tau+T) / (2*T)))

    _, ALPHA = meshgrid(phi_range_n[0], alpha[0])

    result = (T/2) * ALPHA * As

    for interf in range(ninterf):
        phi_range = phi_range_n[interf]
        PHI_C, _ = meshgrid(phi_range, alpha[0])

        beta = beta_n[2*interf:(2*interf)+2]
        beta_i, beta_q = concatenate((beta[0], zeros(max(1, 2*abs(k_tau))))), concatenate((beta[1], zeros(max(1, 2*abs(k_tau_n)))))
        
        bkn_i = roll(beta_i, k_tau + 1)[:len(alpha[0])]
        bk_i = roll(beta_i, k_tau)[:len(alpha[0])]
        bkn_q = roll(beta_q, k_tau_n + 1)[:len(alpha[1])]
        bk_q = roll(beta_q, k_tau_n)[:len(alpha[1])]
        
        arg1 = cos(phi_p) * (_tau_ * bkn_i + (2*T - _tau_) * bk_i)
        arg2 = ((2*T) / pi) * sin(phi_p) * (bkn_i - bk_i)
        arg3 = sin(phi_p) * (_tau_n_ * bkn_q + (2*T - _tau_n_) * bk_q)
        arg4 = ((2*T) / pi) * cos(phi_p) * (bkn_q - bk_q)
        
        _, ARG12 = meshgrid(phi_range, (arg1 - arg2))
        _, ARG34 = meshgrid(phi_range, (arg3 + arg4))    
        
        result += (Au/4.0) * (cos(PHI_C) * ARG12 - sin(PHI_C) * ARG34)
    
    if Au > 0 and ninterf != 0:
        return result / ((T/2) * As * Au)
    else:
        return result / ((T/2) * As)

def detect_q_n(ninterf, alpha, beta_n, phi_range_n, tau, As, Au):
    _tau_ = remainder(tau, 2*T)
    _tau_p_ = remainder(tau-T, 2*T)
    omega_p = pi/(2*T)
    phi_p = omega_p * tau

    k_tau = int(floor(tau / (2*T)))
    k_tau_p = int(floor((tau-T) / (2*T)))

    _, ALPHA = meshgrid(phi_range_n[0], alpha[1])
    
    result = (T/2) * ALPHA * As
    
    for interf in range(ninterf):
        phi_range = phi_range_n[interf]
        PHI_C, _ = meshgrid(phi_range, alpha[1])

        beta = beta_n[2*interf:(2*interf)+2]
        # fill negative indices with zeros
        beta_i, beta_q = concatenate((beta[0], zeros(max(1, 2*abs(k_tau_p))))), concatenate((beta[1], zeros(max(1, 2 * abs(k_tau)))))
        
        bkn_i = roll(beta_i, k_tau_p + 1)[:len(alpha[0])]
        bk_i = roll(beta_i, k_tau_p)[:len(alpha[0])]
        bkn_q = roll(beta_q, k_tau + 1)[:len(alpha[1])]
        bk_q = roll(beta_q, k_tau)[:len(alpha[1])]
        
        arg1 = cos(phi_p) * (_tau_ * bkn_q + (2*T - _tau_) * bk_q)
        arg2 = ((2*T) / pi) * sin(phi_p) * (bkn_q - bk_q)
        arg3 = sin(phi_p) * (_tau_p_ * bkn_i + (2*T - _tau_p_) * bk_i)
        arg4 = ((2*T) / pi) * cos(phi_p) * (bkn_i - bk_i)
        
        _, ARG12 = meshgrid(phi_range, (arg1 - arg2))
        _, ARG34 = meshgrid(phi_range, (arg3 + arg4))
        
        result += (Au/4.0) * (cos(PHI_C) * ARG12 - sin(PHI_C) * ARG34)
    
    if Au > 0 and ninterf != 0:
        return result / ((T/2) * As * Au * ninterf)
    else:
        return result / ((T/2) * As)

def map_chips_n(vsyms, *args):
    chips_i, chips_q = {}, {}
    
    # Split chipping sequences in I and Q
    for sym in chips.iterkeys():
        chips_i[sym] = chips[sym][::2]
        chips_q[sym] = chips[sym][1::2]
    
    alpha_i, alpha_q = array([], dtype=int32), array([], dtype=int32)
    for vsym in vsyms:
        alpha_i = concatenate((alpha_i, chips_i[vsym]))
        alpha_q = concatenate((alpha_q, chips_q[vsym]))

    result = array([alpha_i, alpha_q])
    
    for asyms in args:
        beta_i, beta_q = array([], dtype=int32), array([], dtype=int32)
    
        for asym in asyms:
            beta_i = concatenate((beta_i, chips_i[asym]))
            beta_q = concatenate((beta_q, chips_q[asym]))

        result = vstack([result, array([beta_i, beta_q])])
        
    return result
 
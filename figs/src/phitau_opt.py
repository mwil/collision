import numpy as np

T = 1.0

# IEEE 802.15.4 chipping sequences (I/Q as bits, interleaved)
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

def detect_i(alpha, beta, phi_range, tau, As, Au):
    _tau_   = np.remainder(tau, 2*T)
    _tau_n_ = np.remainder(tau+T, 2*T)
    omega_p = np.pi/(2*T)
    phi_p   = omega_p * tau
    
    k_tau   = int(np.floor(tau / (2*T)))
    k_tau_n = int(np.floor((tau+T) / (2*T)))
        
    # fill negative indices with np.zeros (FIXED: k=0 also needs one zero at position -1!)
    beta_i = np.concatenate((beta[0], np.zeros(max(1, 2*abs(k_tau)))))
    beta_q = np.concatenate((beta[1], np.zeros(max(1, 2*abs(k_tau_n)))))

    bkn_i = np.roll(beta_i, k_tau + 1)[:len(alpha[0])]
    bk_i  = np.roll(beta_i, k_tau)[:len(alpha[0])]
    bkn_q = np.roll(beta_q, k_tau_n + 1)[:len(alpha[0])]
    bk_q  = np.roll(beta_q, k_tau_n)[:len(alpha[0])]
    
    arg1 = np.cos(phi_p) * (_tau_ * bkn_i + (2*T - _tau_) * bk_i)
    arg2 = ((2*T) / np.pi) * np.sin(phi_p) * (bkn_i - bk_i)
    arg3 = np.sin(phi_p) * (_tau_n_ * bkn_q + (2*T - _tau_n_) * bk_q)
    arg4 = ((2*T) / np.pi) * np.cos(phi_p) * (bkn_q - bk_q)
    
    PHI_C, ALPHA = np.meshgrid(phi_range, alpha[0])
    ARG12 = np.meshgrid(phi_range, (arg1 - arg2))[1]
    ARG34 = np.meshgrid(phi_range, (arg3 + arg4))[1]
    
    # TODO: fix Au in partial overlap! One strong chip can dominate the complete correlation of a symbol ...
    
    result = (T/2) * ALPHA * As + (Au/4) * (np.cos(PHI_C) * ARG12 - np.sin(PHI_C) * ARG34)
    
    # modified for Au only transmissions
    if As != 0:
        return result / ((T/2) * As * Au)
    else:
        return result / ((T/2) * Au)

def detect_q(alpha, beta, phi_range, tau, As, Au):
    _tau_   = np.remainder(tau, 2*T)
    _tau_p_ = np.remainder(tau-T, 2*T)
    omega_p = np.pi/(2*T)
    phi_p   = omega_p * tau

    k_tau   = int(np.floor(tau / (2*T)))
    k_tau_p = int(np.floor((tau-T) / (2*T)))
    
    # fill negative indices with np.zeros
    beta_i = np.concatenate((beta[0], np.zeros(max(1, 2*abs(k_tau_p)))))
    beta_q = np.concatenate((beta[1], np.zeros(max(1, 2 * abs(k_tau)))))
    
    bkn_i = np.roll(beta_i, k_tau_p + 1)[:len(alpha[0])]
    bk_i  = np.roll(beta_i, k_tau_p)[:len(alpha[0])]
    bkn_q = np.roll(beta_q, k_tau + 1)[:len(alpha[0])]
    bk_q  = np.roll(beta_q, k_tau)[:len(alpha[0])]
    
    arg1 = np.cos(phi_p) * (_tau_ * bkn_q + (2*T - _tau_) * bk_q)
    arg2 = ((2*T) / np.pi) * np.sin(phi_p) * (bkn_q - bk_q)
    arg3 = np.sin(phi_p) * (_tau_p_ * bkn_i + (2*T - _tau_p_) * bk_i)
    arg4 = ((2*T) / np.pi) * np.cos(phi_p) * (bkn_i - bk_i)
    
    PHI_C, ALPHA = np.meshgrid(phi_range, alpha[1])
    ARG12 = np.meshgrid(phi_range, (arg1 - arg2))[1]
    ARG34 = np.meshgrid(phi_range, (arg3 + arg4))[1]
    
    # TODO: fix Au in partial overlap! One strong chip can dominate the complete correlation of a symbol ...
    result = (T/2) * ALPHA * As + (Au/4) * (np.cos(PHI_C) * ARG12 - np.sin(PHI_C) * ARG34)
    
    # modified for Au only transmissions
    if As != 0:
        return result / ((T/2) * As * Au)
    else:
        return result / ((T/2) * Au)


def map_chips(vsyms, asyms):
    chips_i, chips_q = {}, {}
    
    # Split chipping sequences in I and Q
    for sym in chips.iterkeys():
        chips_i[sym] = chips[sym][::2]
        chips_q[sym] = chips[sym][1::2]
    
    alpha_i, alpha_q = np.array([], dtype=np.int), np.array([], dtype=np.int)
    beta_i, beta_q   = np.array([], dtype=np.int), np.array([], dtype=np.int)
    
    # map symbols to chips
    for vsym in vsyms:
        alpha_i = np.concatenate((alpha_i, chips_i[vsym]))
        alpha_q = np.concatenate((alpha_q, chips_q[vsym]))
    for asym in asyms:
        beta_i = np.concatenate((beta_i, chips_i[asym]))
        beta_q = np.concatenate((beta_q, chips_q[asym]))
        
    return np.array([alpha_i, alpha_q, beta_i, beta_q])
    
def channel(alpha, beta, phi_range, tau, As, Au):
    RECV_CHIPS_I = detect_i(alpha, beta, phi_range, tau, As, Au)
    RECV_CHIPS_Q = detect_q(alpha, beta, phi_range, tau, As, Au)

    # return received chipping sequence with alternating I/Q chips for correlation ([i0, q0, i1, q1, ...])
    i = 0 # choose a phi_c value from the matrix
    #recv_chips = sign(ravel(zip(RECV_CHIPS_I[:,i], RECV_CHIPS_Q[:,i])))
    recv_chips = np.ravel(zip(RECV_CHIPS_I[:,i], RECV_CHIPS_Q[:,i]))
    
    return recv_chips

def detect_syms_corr(recv_chips, **args):
    recv_syms = np.array([], dtype=np.int)
    
    # Choose the symbol with the highest correlation value
    for i in xrange(len(recv_chips)/32):
        curr_chips = recv_chips[i*32:(i+1)*32]
        best_syms  = []
        best_corr  = 0
        
        for sym in chips.iterkeys():
            curr_corr, = np.abs(np.correlate(chips[sym], curr_chips))
            
            if curr_corr > best_corr:
                best_syms  = [sym]
                best_corr  = curr_corr
            elif curr_corr == best_corr:
                best_syms.append(sym)
                
        # all values with the same correlation could be detected, just choose one ...
        recv_syms = np.append(recv_syms, np.random.choice(best_syms))
    
    return recv_syms

def detect_syms_corrcoef(recv_chips, **args):
    recv_syms = np.array([], dtype=np.int)
    
    # Choose the symbol with the highest correlation value
    for i in xrange(len(recv_chips)/32):
        curr_chips = recv_chips[i*32:(i+1)*32]

        corr_matrix = np.abs(np.corrcoef(curr_chips, chips_a))[0,1:]
        best_syms,  = np.where(corr_matrix >= np.max(corr_matrix))
                
        # all values with the same correlation could be detected, just choose one ...
        recv_syms = np.append(recv_syms, np.random.choice(best_syms))
    
    return recv_syms

#detect_syms_corr = detect_syms_corrcoef
    
def detect_syms_cerr(recv_chips, **args):
    recv_syms = array([], dtype=np.int)
    
    # Choose the symbol with the lowest number of chip errors
    while len(recv_chips) > 0:
        curr_chips = recv_chips[:32]
        best_sym   = 0
        best_cerr  = 33
        
        for sym in chips:
            if not sym: continue
            curr_cerr = sum(chips[sym][1:] != curr_chips[1:])
            
            if curr_cerr < best_cerr:
                best_sym  = sym
                best_cerr  = curr_cerr
        
        recv_syms = append(recv_syms, best_sym)
        recv_chips = recv_chips[32:]
        
    return recv_syms

if __name__ == "__main__":
    alpha = np.array([[-1, 1, -1, 1, -1, -1], [ 1,  1, -1, -1, -1, 1]])  # (I,Q)
    beta  = np.array([[-1, 1, -1, 1,  1, -1], [-1, -1, -1,  1, -1, 1]])  # (I,Q)
    phi_range = np.arange(-np.pi, np.pi, np.pi / 2)

    res = detect_i(alpha, beta, phi_range, -6.0, 1.0, 10.0)
    #res = detect_q(alpha, beta, phi_range, -6.0, 1.0, 10.0)
    
    np.set_printoptions(threshold=np.NaN, precision=2, suppress=True, linewidth=180)
    print res[:,-1]

    asyms = [1,2,3]
    vsyms = [4,5,6]

    send_chips = map_chips(asyms, vsyms)
    recv_chips = channel(send_chips[:2], send_chips[2:], phi_range=[np.pi/2], tau=0.0, As=1.0, Au=100.0)

    for i in xrange(1000):
        recv_syms = detect_syms_corrcoef(recv_chips)

    print recv_syms

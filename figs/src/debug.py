# Copyright 2013 Matthias Wilhelm

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
import matplotlib.pyplot as plt
from collections import defaultdict

from phitau import *

T = 1.0

As, Am = 1.0, 100.0

tau = 0.0
phi_range = array([0.0, 0.6015625*pi])
#tau_range = np.arange(-1.5*T, 1.51*T, 0.1)
#phi_range = np.arange(-pi, pi, pi/128)

send_syms = np.vstack((array([0x0]*18),        
    array([None, 0xD, 0xE, 0xA, 0xD, 0xB, 0xE, 0xE, 0xF, 0x1, 0x2, 0x3, 0x4, 0x5, 0x6, 0x7, 0x8, None])))
send_syms_s, send_syms_u = send_syms[0][1:-1], send_syms[1][1:-1]

send_chips = map_chips(*send_syms)
set_printoptions(threshold=NaN, precision=3, suppress=True)

RECV_CHIPS_I = detect_i(send_chips[:2], send_chips[2:], phi_range, tau, As, Am)
RECV_CHIPS_Q = detect_q(send_chips[:2], send_chips[2:], phi_range, tau, As, Am)

recv_chips = np.ravel(zip(RECV_CHIPS_I[:,1], RECV_CHIPS_Q[:,1]))
print recv_chips       
recv_syms = detect_syms_corr(recv_chips)[1:-1]
    
print ''.join(['%x'%(sym) for sym in recv_syms])
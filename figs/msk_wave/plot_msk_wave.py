#! /usr/bin/env python2.7

import numpy as np
from numpy import pi, cos, sin
import matplotlib as mpl
import matplotlib.pyplot as plt

mpl.rc_file('../2fig-rc.txt')

mpl.rc('figure', figsize=(7, 4))

I, Q = 0, 1

T = 1.
dt = 0.01
mark_skip = 25
t = np.arange(-2*T, 11*T, dt)

fc = 1
omega_c = 2 * pi * fc
omega_p = pi / (2*T)

tau = 0 * T/dt

fig = plt.figure()

axes = []

axes.append(fig.add_subplot('311'))
axes.append(fig.add_subplot('312'))
axes.append(fig.add_subplot('313'))

alpha = np.array([[ 1, 1, -1, -1, 1], [ 1, -1, 1, -1, 1]])

a_i = np.concatenate([np.repeat(a, (2*T)/dt) for a in alpha[I]])
a_i = np.concatenate([np.repeat(0., T/dt), a_i, np.repeat(0., 10*T/dt)])[:len(t)]

a_q = np.concatenate([np.repeat(a, (2*T)/dt) for a in alpha[Q]])
a_q = np.concatenate([np.repeat(0., 2*T/dt), a_q, np.repeat(0., 10*T/dt)])[:len(t)]

for ax in axes:
    ax.set_xlim(-2, 11)
    ax.set_ylim(-1.2, 1.2)
    ax.set_yticklabels([])
    ax.grid(axis='x')
    ax.set_yticks((-1, 0, 1))


axes[0].set_title('In-phase component', size=12)
axes[0].set_xticks(range(-1, 12, 2))
axes[0].set_xticks(range(0, 12, 2), minor=True)
axes[0].set_xticklabels([])

axes[1].set_title('Quadrature component', size=12)

axes[1].set_xticks(range(0, 12, 2))
axes[1].set_xticks(range(-1, 12, 2), minor=True)
axes[1].set_xticklabels([])
axes[1].set_ylabel('Transmitted signal amplitude')

axes[2].set_title('Passband signal $s(t)$', size=12)
axes[2].set_xlabel('Time $t$ ($/T$)')
axes[2].set_xticks(range(-1, 11))

s_i = a_i*cos(t*omega_c)*cos(t*omega_p)
s_q = a_q*sin(t*omega_c)*sin(t*omega_p)


axes[0].plot(t, a_i, c='0.0')
axes[0].plot(t, s_i, c='0.4')
axes[0].plot(t[::mark_skip], s_i[::mark_skip], '^', ms=4, c='0.4')
axes[0].plot(t, a_i*cos(t*omega_p), c='0.7')
axes[0].plot(t[::mark_skip], (a_i*cos(t*omega_p))[::mark_skip], 'o', ms=4, c='0.7')

axes[1].plot(t, a_q, c='0.0')
axes[1].plot(t, s_q, c='0.4')
axes[1].plot(t[::mark_skip], s_q[::mark_skip], '^', ms=4, c='0.4')
axes[1].plot(t, a_q*sin(t*omega_p), c='0.7')
axes[1].plot(t[::mark_skip], (a_q*sin(t*omega_p))[::mark_skip], 'o', ms=4, c='0.7')

axes[2].plot(t, s_i + s_q, c='0.1')

plt.savefig('pdf/msk_wave.pdf')

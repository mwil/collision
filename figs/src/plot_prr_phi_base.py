import os

import itertools as it

import numpy as np
from numpy import pi
import matplotlib as mpl
import matplotlib.pyplot as plt

mpl.rc_file('../4fig-rc.txt')
#mpl.rc('figure', figsize=(3.33, 2.25))

def plot(sync_file, unsync_file, outfile, y_label, **args):
    for mode in ('unif', 'same'):
    #for mode in ('same',):
        plt.clf()
        fig = plt.figure()
        
        axes = []
        axes.append(fig.add_subplot('311'))
        axes.append(fig.add_subplot('312'))
        axes.append(fig.add_subplot('313'))
        
        tau_range = (args['tau_range_unif'] if mode == 'unif' else args['tau_range_same'])
        phi_range = args['phi_range']
        
        if mode in ('unif',):    
            lstyle = it.cycle([a+b for a, b in it.product('rgkc', '--')])
            markers = it.cycle('ssoovv^^')
        elif mode in ('same',):
            lstyle = it.cycle(['r-', 'g-', 'k-', 'c-', 'b-'])
            markers = it.cycle('sov^x')
        
        lines = []
        for i in range(len(tau_range)):
            tau = tau_range[i]
            prr_s = np.load(sync_file%(mode, tau, mode))
            prr_u = np.load(unsync_file%(mode, tau, mode))
            
            if mode in ('same'):
                line_tmp, = axes[i].plot(phi_range/pi, prr_s, next(lstyle), lw=1)
                lines.append(axes[i].plot(phi_range[25::50]/pi, prr_s[25::50], ' ', color=line_tmp.get_color(), marker=next(markers), markersize=4)[0])
            
            if mode in ('unif',):
                line_tmp, = axes[i].plot(phi_range/pi, prr_u, next(lstyle), lw=1)
                axes[i].plot(phi_range[25::50]/pi, prr_u[25::50], ' ', color=line_tmp.get_color(), marker=next(markers), markersize=6, fillstyle='none')
            
        #lgd = plt.legend(lines, [r'$\tau=%1.1fT$'%(t) for t in tau_range], loc='center right', fontsize=6, numpoints=1)
        #for l in lgd.get_lines():
        #    l.set_linestyle('-')
        
        #plt.axis([min(phi_range)/pi, max(phi_range)/pi, 1e-2, 1])
        axes[-1].set_xlabel(r'Carrier phase offset $\varphi_c$ ($/\pi$)', labelpad=2)
        #axes[1].set_ylabel(r'Packet reception ratio ($\mathrm{PRR}_u$)')
        axes[1].set_ylabel(y_label, labelpad=2)
        
        for ax in axes:
            ax.set_xlim(-1, 1)
            ax.set_ylim(0, 1.1)
            ax.set_yticklabels([0, 1])
            ax.set_yticks((0.0, 1.0))
            ax.grid(axis='x')
        
        axes[0].set_xticklabels([])
        axes[1].set_xticklabels([])
        
        lgd = axes[0].legend(lines, (r'$\tau=0$',), loc='upper center', borderaxespad=0.25)
        for l in lgd.get_lines(): l.set_linestyle('-')
        lgd = axes[1].legend(lines[1:], (r'$\tau=0.5T$',), loc='upper center', borderaxespad=0.25)
        for l in lgd.get_lines(): l.set_linestyle('-')
        lgd = axes[2].legend(lines[2:], (r'$\tau=1.0T$',), loc='upper center', borderaxespad=0.25)
        for l in lgd.get_lines(): l.set_linestyle('-')
        
        #plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
        #plt.tight_layout()
        plt.savefig(outfile%(mode))
    
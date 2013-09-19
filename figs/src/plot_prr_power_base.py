import os

import itertools as it

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

mpl.rc_file('../3fig-rc.txt')

tau_range = np.array([0.0, 0.5, 1.0, 1.5])

def plot(data_file, outfile, loc='', kind='', **args):
    '''loc is the location of the plot legend (e.g., "upper right")'''
    
    for content, decision in it.product(('unif', 'same'), ('soft',)):
        fig = plt.figure()
        ax  = fig.add_subplot(111)
        
        if content in ('unif',): 
            lstyle = it.cycle([a+b for a, b in it.product('rgkc', ('-', '-'))])
            markers = it.cycle('ssoovv^^')
        elif content in ('same',):
            lstyle = it.cycle(['r-', 'g-', 'k-', 'c-', 'b-'])
            markers = it.cycle('sov^x')
        
        lines = []
        
        for tau in tau_range:
            data = np.load(data_file%(content, tau, content, ('_'+decision if kind == 'dsss' else '')))
            As_range  = data['As_range']

            prr_s = data['prr_s']
            prr_u = data['prr_u']
            
            line_tmp, = ax.plot(As_range, prr_s, next(lstyle), lw=1)
            lines.append(ax.plot(As_range[::10], prr_s[::10], ' ', color=line_tmp.get_color(), marker=next(markers))[0])
            
            if content in ('unif',):
                ax.plot(As_range, prr_u, next(lstyle), lw=1)
                ax.plot(As_range[::10], prr_u[::10], ' ', color=line_tmp.get_color(), marker=next(markers), fillstyle='none')
            
        lgd = ax.legend(lines, [r'$%.1fT$'%(t) for t in tau_range], loc=loc)
        lgd.set_title(r'$\tau=$', prop=FontProperties(size=12))
        for l in lgd.get_lines():
            l.set_linestyle('-')
        
        ax.set_xlim(min(As_range), max(As_range)+0.1)
        ax.set_ylim(0, 1)
        ax.set_xlabel('Signal power ratio SIR (/dB)', labelpad=2)
        ax.set_ylabel('Packet reception ratio', labelpad=2)
        ax.grid(axis='y')
        ax.set_xscale('log')
        
        ax.set_xticklabels(['', '$-30$', '$-20$', '$-10$', '$0$', '$10$'])
        
        if kind == 'dsss':
            plt.savefig(outfile%(content, decision))
        else:
            plt.savefig(outfile%(content,))
    
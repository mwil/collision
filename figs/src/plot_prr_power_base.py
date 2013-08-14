import os

import itertools as it

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

mpl.rc_file('../3fig-rc.txt')

def plot(sync_file, unsync_file, outfile, loc='', **args):
    '''loc is the location of the plot legend (e.g., "upper right")'''
    
    for content, decision, zoom in it.product(('unif', 'same'), ('soft', ), (False,)):#(False, True)):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        
        As_range = (args['As_range_zoom'] if zoom else args['As_range_norm'])
        tau_range = (args['tau_range_unif'] if content == 'unif' else args['tau_range_same'])
        
        if content in ('unif',):    
            lstyle = it.cycle([a+b for a, b in it.product('rgkc', ('-', '-'))])
            markers = it.cycle('ssoovv^^')
        elif content in ('same',):
            lstyle = it.cycle(['r-', 'g-', 'k-', 'c-', 'b-'])
            markers = it.cycle('sov^x')
        
        lines = []
        for tau in tau_range:
            prr_o = np.load(sync_file%(content, tau, '_zoom' if zoom else '', content, '_'+decision))
            prr_m = np.load(unsync_file%(content, tau, '_zoom' if zoom else '', content, '_'+decision))
            
            line_tmp, = ax.plot(As_range, prr_o, next(lstyle), lw=1)
            lines.append(ax.plot(As_range[::10], prr_o[::10], ' ', color=line_tmp.get_color(), marker=next(markers))[0])
            
            if content in ('unif',):
                ax.plot(As_range, prr_m, next(lstyle), lw=1)
                ax.plot(As_range[::10], prr_m[::10], ' ', color=line_tmp.get_color(), marker=next(markers), fillstyle='none')
            
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
        
        if not zoom:
            ax.set_xticklabels(['$-30$', '$-20$', '$-10$', '$0$', '$10$'])
        else:
            ax.set_xticklabels(['', 0, 10])
            ax.set_xticklabels(8*['']+[3, '', 6], minor=True)
        #plt.yscale('log')
        
        plt.savefig(outfile%('_zoom' if zoom else '', content, decision))
    
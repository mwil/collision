import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.cm as cm

import itertools as it

from matplotlib.font_manager import FontProperties

from settings import *

mpl.rc_file('../3fig-contour-rc.txt')

wide = '_wide'

tau_range = (tau_range_wide   if wide else tau_range)
Au_range  = (Au_range_wide    if wide else Au_range)
Au_range  = (Au_range_wide_dB if wide else Au_range_dB)

AU, TAU = np.meshgrid(Au_range, tau_range)

np.set_printoptions(precision=3, suppress=True, threshold=np.NaN)
#print AU[:,::-1]

#for mode, content in it.product(('sync', 'usync'), ('same', 'unif')):
for mode, content in it.product(('sync',), ('unif',)):
    Zu = np.load('data/prr_u_AsAu_%s%s.npy'%(content, wide))
    Zs = np.load('data/prr_s_AsAu_%s%s.npy'%(content, wide))

    #mpl.rc_file('../2fig-contour-rc.txt')

    print 'DEBUG: If "Inputs x and y must be 1D or 2D." -> Shape mismatch TAU, AU, Zu: ', TAU.shape, AU.shape, Zu.shape
    
    plt.clf()
    
    if mode in ('sync',):
        # Plot the inverse power ratio, sync signal is stronger for positive ratios
        CSf = plt.contourf(TAU, -AU, Zs, levels=(0.0, 0.2, 0.4, 0.6, 0.8, 0.9, 1.0), colors=('1.0', '0.75', '0.5', '0.25', '0.15', '0.0'), origin='lower')
        CS2 = plt.contour(CSf, colors = ('r',)*5+('w',), linewidths=(0.75,)*5+(1.0,), origin='lower', hold='on')
    else:
        #CSf  = plt.contourf(TAU, -AU, Zs, levels=(0.0, 0.2, 0.4, 0.6, 0.8, 0.9, 1.0), colors=('1.0', '0.75', '0.5', '0.25', '0.15', '0.0'), origin='lower')
        #CS2f = plt.contour(CSf, levels=(0.0, 0.2, 0.4, 0.6, 0.8, 1.0), colors=4*('r',)+('w',), linewidths=(0.75,)*4+(1.0,), origin='lower', hold='on')
        CS2f = plt.contour(TAU, -AU, Zs, levels=(0.9, 1.0), colors=('0.0',), linewidths=(1.0,), origin='lower', hold='on')
        if content in ('unif',):
            CSu  = plt.contourf(TAU, -AU, Zu, levels=(0.2, 1.0), hatches=('////',), colors=('0.75',), origin='lower')
            CS2  = plt.contour(CSu, levels=(0.2,), colors = ('r',), linewidths=(1.0,), origin='lower', hold='on')

    if mode in ('sync',):
        plt.annotate(r'$\delta_{\mathrm{SIR}}$', xy=(-0.25, 1), xytext=(-3.25, 1.75), color='1.0', fontsize=10,
            arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=-0.2', color='1.0'))
    else:
        plt.annotate(r'$\delta_{\mathrm{SIR}}$', xy=(-0.25, 1), xytext=(-3.25, 1.75), color='0.0', fontsize=10,
            arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=-0.2', color='0.0'))

    #cb  = plt.colorbar(CSf)
    
    if mode in ('sync'):
        if wide:
            plt.axis([-4.0, 4.0, -10, 3])
        else:
            plt.axis([-1.5, 1.5, -10, 3])
    else:
        plt.axis([-1.5, 1.5, -50, 10])

    plt.ylabel(r'Signal power ratio ($\mathrm{SIR}$)', labelpad=0) 
    #cb.set_label(r'Packet reception ratio ($\mathrm{PRR}$)')
    plt.xlabel(r'Time offset $\tau$ ($/T$)', labelpad=2)
    
    plt.savefig('pdf/prrc2_%s_%s%s.pdf'%(mode, content, wide))

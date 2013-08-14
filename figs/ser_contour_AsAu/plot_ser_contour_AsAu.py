import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import itertools as it

from settings import *

mpl.rc_file('../3fig-contour-rc.txt')


def plot(mode, content, decision, wide):
    if mode in ('usync',):
        _plot_usync(content, decision, wide)
    else:
        _plot_sync(content, decision, wide)

def _plot_sync(content, decision, wide):
    global tau_range, Au_range, Au_range_dB

    Zs = np.load('data/prr_s_AsAu_%s_%s%s-300.npy'%(content, decision, wide))
    Zu = np.load('data/prr_u_AsAu_%s_%s%s-300.npy'%(content, decision, wide))

    #Zs_bc = np.load('../ber_contour_AsAu/data/prr_s_AsAu_%s%s.npy'%(content, wide))
    #Zu_bc = np.load('../ber_contour_AsAu/data/prr_u_AsAu_%s%s.npy'%(content, wide))

    tau_range    = (tau_range_wide   if wide else tau_range)
    Au_range     = (Au_range_wide    if wide else Au_range)
    Au_range_dB  = (Au_range_wide_dB if wide else Au_range_dB)

    AU, TAU = np.meshgrid(Au_range_dB, tau_range)

    plt.clf()

    print 'DEBUG: If "Inputs x and y must be 1D or 2D." -> Shape mismatch TAU, AU, Zu: ', TAU.shape, AU.shape, Zs.shape#, Zs_bc.shape

    # version for sync, same, hard
    #CSf = plt.contourf(TAU[::2,::2], -AU[::2,::2], Zs, levels=(0.0, 0.2, 0.4, 0.6, 0.8, 0.9, 1.0), colors=('1.0', '0.75', '0.5', '0.25', '0.15', '0.0'), origin="lower")
    CSf = plt.contourf(TAU, -AU, Zs, levels=(0.0, 0.2, 0.4, 0.6, 0.8, 0.9, 1.0), colors=('1.0', '0.75', '0.5', '0.25', '0.15', '0.0'), origin="lower")
    CS2 = plt.contour(CSf,  colors = ('r',)*5+('w',), linewidths=(0.75,)*5+(1.0,), origin="lower", hold='on')
    #[::2,::2]
    #CS_bc = plt.contour(TAU, -AU, Zs_bc, levels=(0.9,), colors='w', origin='lower', hold='on')

    #cb  = plt.colorbar(CSf)
    
    if content in ('same'):
        if wide:
            plt.annotate(r'$\delta_\mathrm{SIR}$', xy=(-0.25, 1), xytext=(-3.25, 1.75), color='w', fontsize=10,
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=-0.2', color='w'))
        else:
            plt.annotate(r'$\delta_\mathrm{SIR}$', xy=(-0.25, 1), xytext=(-1.25, 3.75), color='w', fontsize=10,
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=-0.2', color='w'))

        if wide:
           plt.axis([-4.0, 4.0, -50, 10])
        else:
            plt.axis([-1.5, 1.5, -50, 10])
    else:
        if wide:
            plt.annotate(r'$\delta_\mathrm{SIR}$', xy=(-0.25, 1), xytext=(-3.25, 1.75), color='w', fontsize=10, # xtext=2.5, 1.25
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=-0.2', color='w'))
        else:
            plt.annotate(r'$\delta_\mathrm{SIR}$', xy=(-0.25, 1), xytext=(-1.25, 3.75), color='w', fontsize=10, # xtext=2.5, 1.25
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=-0.2', color='w'))

        if wide:
            plt.axis([-4.0, 4.0, -10, 3])
        else:
            plt.axis([-1.5, 1.5, -10, 3])
    
    plt.xlabel(r'Time offset $\tau$ ($/T$)', labelpad=2)
    plt.ylabel(r'Signal power ratio ($\mathrm{SIR}$)', labelpad=0)
    #cb.set_label(r'Packet reception ratio ($\mathrm{PRR}$)')
    
    plt.savefig('pdf/prrc_sync2_%s_%s%s.pdf'%(content, decision, wide))

def _plot_usync(content, decision, wide):
    global tau_range, Au_range, Au_range_dB
    #if decision in ('soft',):
    #    mpl.rc_file('../1fig-contour-rc.txt')
    #else:
    #    mpl.rc_file('../2fig-contour-rc.txt')

    Zs = np.load('data/prr_s_AsAu_%s_%s%s.npy'%(content, decision, wide))
    Zu = np.load('data/prr_u_AsAu_%s_%s%s.npy'%(content, decision, wide))

    Zs_bc = np.load('../ber_contour_AsAu/data/prr_s_AsAu_%s%s.npy'%(content, wide))
    #Zu_bc = np.load('../ber_contour_AsAu/data/prr_u_AsAu_%s%s.npy'%(content, wide))

    tau_range    = (tau_range_wide   if wide else tau_range)
    Au_range     = (Au_range_wide    if wide else Au_range)
    Au_range_dB  = (Au_range_wide_dB if wide else Au_range_dB)

    AU, TAU = np.meshgrid(Au_range_dB, tau_range)

    plt.clf()

    print 'Matrix shapes (should match): ', TAU.shape, AU.shape, Zu.shape
    CSf = plt.contourf(TAU, -AU, Zu, hatches=(None,)+('////',)*3, levels=(0.0, 0.2, 0.4, 0.6, 0.8, 0.9, 1.0), colors=('1.0', '0.75', '0.5', '0.25', '0.15', '0.0'), origin="lower")
    CS2 = plt.contour(CSf, colors = 4*('r',)+('w',), linewidths=(1, 0.75, 0.75, 0.75, 0.75), origin="lower", hold='on')

    #plt.annotate(r'$\delta_\mathrm{NEU}$', xy=(-0.9, -3), xytext=(-1.45, -25), fontsize=8, arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=.2'))

    if content in ('unif',):
        #pass
        #CSf_bc = plt.contourf(TAU, -AU, Zs, levels=(0.6, 0.8, 0.9, 1.0), colors=('0.25', '0.15', '0.0'), origin="lower")
        CS_bc  = plt.contour(TAU,  -AU, Zs_bc, linewidths=1.0, levels=(0.9, 1.0), colors='0.0', origin='lower', hold='on')

        plt.annotate(r'$\delta_\mathrm{SIR}$', xy=(-0.25, 0.75), xytext=(-1.25, 3.25), color='0.0', fontsize=10, # xtext=2.5, 1.25
            arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=-0.2', color='0.0'))
    else:
        pass
        #CS_bc = plt.contour(TAU, -AU, Zs, levels=(0.8,), colors='w', origin='lower', hold='on')

    #cb  = plt.colorbar(CSf)

    if wide:
        plt.axis([-4.0, 4.0, -16, 3])
    else:
        plt.axis([-1.5, 1.5, -50, 10])
    
    #plt.gca().axes.get_yaxis().set_ticklabels([])
    plt.xlabel(r'Time offset $\tau$ ($/T$)', labelpad=2)
    plt.ylabel(r'Signal power ratio ($\mathrm{SIR}$)', labelpad=0)
    #cb.set_label(r'Packet reception ratio ($\mathrm{PRR}$)')
    
    plt.savefig('pdf/prrc_usync2_%s_%s%s.pdf'%(content, decision, wide))

def colorbar_only():
    #fig = plt.figure(figsize=(0.375, 1.44))
    fig = plt.figure(figsize=(0.375, 1.92))
    ax1 = fig.add_axes([0, 0.05, 0.25, 1])
    
    cmap = mpl.colors.ListedColormap(['1.0', '0.75', '0.5', '0.25', '0.15', '0.0'])

    bounds = [0.0, 0.2, 0.4, 0.6, 0.8, 0.9, 1.0]
    norm = mpl.colors.BoundaryNorm(bounds, cmap.N)
    cb2 = mpl.colorbar.ColorbarBase(ax1, cmap=cmap,
                                         boundaries=bounds,
                                         ticks=bounds, # optional
                                         orientation='vertical')
    cb2.set_label(r'Packet reception ratio ($\mathrm{PRR}$)', fontsize=12)

    plt.savefig('pdf/cb.pdf')


if __name__ == '__main__':
    #for mode, content in it.product(('sync', 'usync'), ('unif', 'same')):
    mode = ('sync', 'usync')[0]
    content = ('unif', 'same')[1]
    decision = 'soft'
    wide = ''

    for decision in ('hard', 'soft'):
        plot(mode, content, decision, wide)
    #plot ('sync', 'same', 'soft', '')

    #colorbar_only()

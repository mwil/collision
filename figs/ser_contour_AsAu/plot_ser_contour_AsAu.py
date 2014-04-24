import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import itertools as it

mpl.rc_file('../3fig-contour-rc.txt')


def plot(mode, content, decision, wide):
    dat_sc = np.load('data/prr_AsAu_%s_%s%s.npz'%(content, decision, wide))
    Zs, Zu = dat_sc['SER_S'], dat_sc['SER_U']

    dat_bc = np.load('../ber_contour_AsAu/data/prr_AsAu_%s%s.npz'%(content, wide))
    Zs_bc, Zu_bc = dat_bc['BER_S'][::2,::2], dat_bc['BER_U'][::2,::2]

    Z    = (Zs    if mode in ('sync',) else Zu)
    Z_bc = (Zs_bc if mode in ('sync',) else Zu_bc)

    tau_range = dat_sc['tau_range']
    Au_range_dB  = 20*np.log10(dat_sc['Au_range'])

    AU, TAU = np.meshgrid(Au_range_dB, tau_range)

    # make adjustments for unif/sync/_wide
    if AU.shape == (251, 227):
        Zs_bc = np.vstack((Zs_bc, np.zeros((1,250))))
        Zs_bc = Zs_bc[:,:227]

    plt.clf()

    print 'DEBUG: If "Inputs x and y must be 1D or 2D." -> Shape mismatch TAU, AU, Zu: ', TAU.shape, AU.shape, Zs.shape#, Zs_bc.shape

    # version for sync, same, hard
    CSf = plt.contourf(TAU, -AU, Z, levels=(0.0, 0.1, 0.2, 0.4, 0.6, 0.8, 0.9, 1.0), colors=('1.0', '0.85', '0.75', '0.65', '0.5', '0.35', '0.0'), origin="lower")
    CS2 = plt.contour(CSf,  colors = ('r',)*6+('w',), linewidths=(0.75,)*6+(1.0,), origin="lower", hold='on')
    #CS_bc = plt.contour(TAU, -AU, Z_bc, levels=(0.9,), colors='w', origin='lower', hold='on')
    
    # adjust color for sync/usync figures
    CS_bc  = plt.contour(TAU, -AU, Zs_bc, linewidths=1.0, levels=(0.9, 1.0), colors='1.0', origin='lower', hold='on')

    #cb  = plt.colorbar(CSf)

    if mode in ('usync',):
        _plot_usync(content, decision, wide)
    else:
        _plot_sync(content, decision, wide)

    if wide:
        plt.axis([-4.0, 4.0, -13, 3])
    else:
        plt.axis([-1.5, 1.5, -50, 10])

    plt.xlabel(r'Time offset $\tau$ ($/T$)', labelpad=2)
    plt.ylabel(r'Signal power ratio ($\mathrm{SIR}$)', labelpad=0)
    #cb.set_label(r'Packet reception ratio ($\mathrm{PRR}$)')
    
    plt.savefig('pdf/prrc_%s2_%s_%s%s.pdf'%(mode, content, decision, wide))

def _plot_sync(content, decision, wide):    
    if content in ('same'):
        if wide:
            plt.annotate(r'$\delta_\mathrm{SIR}$', xy=(-0.25, 1), xytext=(-3.25, 1.75), color='w', fontsize=10,
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=-0.2', color='w'))
        else:
            plt.annotate(r'$\delta_\mathrm{SIR}$', xy=(-0.25, 1), xytext=(-1.25, 3.75), color='w', fontsize=10,
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=-0.2', color='w'))

    else:
        if wide:
            plt.annotate(r'$\delta_\mathrm{SIR}$', xy=(-0.25, 1), xytext=(-3.25, 1.75), color='w', fontsize=10, # xtext=2.5, 1.25
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=-0.2', color='w'))
        else:
            plt.annotate(r'$\delta_\mathrm{SIR}$', xy=(-0.25, 1), xytext=(-1.25, 3.75), color='w', fontsize=10, # xtext=2.5, 1.25
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=-0.2', color='w'))
    


def _plot_usync(content, decision, wide):
    #CSf = plt.contourf(TAU, -AU, Zu, hatches=(None,)+('////',)*3, levels=(0.0, 0.2, 0.4, 0.6, 0.8, 0.9, 1.0), colors=('1.0', '0.75', '0.5', '0.25', '0.15', '0.0'), origin="lower")
    #CS2 = plt.contour(CSf, colors = 4*('r',)+('w',), linewidths=(1, 0.75, 0.75, 0.75, 0.75), origin="lower", hold='on')

    #plt.annotate(r'$\delta_\mathrm{NEU}$', xy=(-0.9, -3), xytext=(-1.45, -25), fontsize=8, arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=.2'))

    if content in ('unif',):
        #pass
        #CSf_bc = plt.contourf(TAU, -AU, Zs, levels=(0.6, 0.8, 0.9, 1.0), colors=('0.25', '0.15', '0.0'), origin="lower")
        #CS_bc  = plt.contour(TAU,  -AU, Zs_bc, linewidths=1.0, levels=(0.9, 1.0), colors='0.0', origin='lower', hold='on')

        # switch colors for both text and arrow here (0<->1) for sync/usync figures!
        plt.annotate(r'$\delta_\mathrm{SIR}$', xy=(-0.25, 0.75), xytext=(-1.25, 3.25), color='0.0', fontsize=10, # xtext=2.5, 1.25
            arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=-0.2', color='0.0'))
    else:
        plt.annotate(r'$\delta_\mathrm{SIR}$', xy=(-0.25, 0.75), xytext=(-1.25, 3.25), color='1.0', fontsize=10, # xtext=2.5, 1.25
            arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=-0.2', color='1.0'))
        #CS_bc = plt.contour(TAU, -AU, Zs, levels=(0.8,), colors='w', origin='lower', hold='on')
   

def colorbar_only():
    fig = plt.figure(figsize=(0.375, 1.44))
    #fig = plt.figure(figsize=(0.375, 1.92))
    ax1 = fig.add_axes([0, 0.05, 0.25, 1])
    
    cmap = mpl.colors.ListedColormap(['1.0', '0.85', '0.75', '0.65', '0.5', '0.35', '0.0'])

    bounds = [0.0, 0.2, 0.4, 0.6, 0.8, 0.9, 1.0]
    norm = mpl.colors.BoundaryNorm(bounds, cmap.N)
    cb2 = mpl.colorbar.ColorbarBase(ax1, cmap=cmap, boundaries=bounds,ticks=bounds, orientation='vertical')
    cb2.set_label(r'Packet reception ratio ($\mathrm{PRR}$)', fontsize=12)

    plt.savefig('pdf/cb-1fig.pdf')


if __name__ == '__main__':
    #for mode, content in it.product(('sync', 'usync'), ('unif', 'same')):
    mode = ('sync', 'usync')[0]
    content = ('unif', 'same')[1]
    decision = 'soft'
    wide = ''

    #for decision in ('hard', 'soft'):
    #    plot(mode, content, decision, wide)
    
    # for unif
    plot ('sync', 'unif', 'hard', '_wide')

    # for same
    #plot ('usync', 'unif', 'soft', '')

    #colorbar_only()

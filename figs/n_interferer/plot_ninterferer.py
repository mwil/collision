import sys

sys.path.append('../src')

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

from matplotlib.patches import Ellipse

from settings import *

mpl.rc_file('../1fig-rc.txt')

decision = 'soft'

def plot():
    ser_s_n_same = np.load('data/ser_s_%s_%s_n.npy'%('same', decision))
    ser_s_1_same = np.load('data/ser_s_%s_%s_1.npy'%('same', decision))
    ser_s_n_unif = np.load('data/ser_s_%s_%s_n.npy'%('unif', decision))
    ser_s_1_unif = np.load('data/ser_s_%s_%s_1.npy'%('unif', decision))


    prr_s_n_same = np.mean((1-ser_s_n_same)**pktlen, axis=1)
    prr_s_1_same = np.mean((1-ser_s_1_same)**pktlen, axis=1)
    prr_s_n_unif = np.mean((1-ser_s_n_unif)**pktlen, axis=1)
    prr_s_1_unif = np.mean((1-ser_s_1_unif)**pktlen, axis=1)

    ninterferers = np.arange(num_interferer+1)

    fig = plt.figure()
    ax = fig.add_subplot(111)

    ax.set_xlabel(r'Number of interferers $n$', labelpad=2)
    ax.set_ylabel(r'Packet reception ratio (PRR)', labelpad=2)
    
    ax.set_xlim(0, num_interferer)
    ax.set_ylim(0, 1)
    
    ax.grid()

    ax.plot(ninterferers, prr_s_n_same, 'b^-')
    ax.plot(ninterferers, prr_s_1_same, 'bo-')
    ax.plot(ninterferers, prr_s_n_unif, 'r^-')
    ax.plot(ninterferers, prr_s_1_unif, 'ro-')

    # proxy artists to get black markers http://www.mail-archive.com/matplotlib-users@lists.sourceforge.net/msg25195.html
    l1, = ax.plot(ninterferers, prr_s_1_unif, 'k^')
    l2, = ax.plot(ninterferers, prr_s_1_unif, 'ko')
    l1.remove()
    l2.remove()

    plt.annotate('Identical payload', xy=(3.5, 0.775), xytext=(4, 0.675), color='k', fontsize=12, # xtext=2.5, 1.25
                arrowprops=dict(arrowstyle='->', color='k')) #connectionstyle='arc3,rad=-0.2',

    e1 = Ellipse(xy=(3.55, 0.875), width=0.15, height=0.2, angle=0, fill=False)
    ax.add_artist(e1)

    plt.annotate('Independent payload', xy=(2.42, 0.4), xytext=(0.2, 0.25), color='k', fontsize=12, # xtext=2.5, 1.25
                arrowprops=dict(arrowstyle='->', color='k')) #connectionstyle='arc3,rad=-0.2',

    e2 = Ellipse(xy=(2.5, 0.55), width=0.15, height=0.4, angle=-45, fill=False)
    ax.add_artist(e2)

    lgd = plt.legend((l2, l1), (r'One interferer', r'$n$ interferers'), loc='center right', handlelength=0.5)
    
    plt.savefig('pdf/ninterf_%s.pdf' % (decision))
    #plt.show()


if __name__ == '__main__':
    plot()

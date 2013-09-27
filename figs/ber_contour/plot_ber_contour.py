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
from numpy import pi
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.cm as cm

from settings import *

#tau_range = np.arange(-1.5*T, 1.501*T, dx*2)
#phi_range = np.arange(-pi, pi+0.01, dx*2)

mpl.rc_file('../3x2-contour-rc.txt')

def plot():
	PHI, TAU = np.meshgrid(phi_range, tau_range)

	mode = ('sync', 'usync')[0]
	content = ('unif', 'same')[0]

	Zu = np.load('data/ber_u_Au%.2f_%s.npy'%(Au, content))
	Zs = np.load('data/ber_s_Au%.2f_%s.npy'%(Au, content))

	Z = (Zu if mode in ('usync',) else Zs)

	print 'Shapes: TAU %s, PHI %s, Zu %s' %(TAU.shape, PHI.shape, Zu.shape)

	CS  = plt.contourf(TAU, PHI/pi, Z,  levels=(0, 1e-6, 0.45, 0.55, 1-1e-6, 1), colors=('0.0', '0.25', '0.5', '0.75', '1.0'), origin="lower")
	CS2 = plt.contour(CS, levels=(1e-6, 0.45, 0.55, 1-1e-6), colors=('w',)+3*('r',), linewidths=(1.0, 0.75,0.75,0.75,0.75), origin="lower", hold='on')
	#cb  = plt.colorbar(CS)
	#cb.set_ticklabels(['0', '$10^{-6}$', '0.45', '0.55', '$1-10^{-6}$', '1'])

	#plt.annotate(r'$\nabla^u$', xy=(0.5, 0.25), xytext=(-0.25, 0), fontsize=8, color='w', arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.2', color='w'))

	plt.axis([-1.5, 1.5, -1, 1])
	plt.xlabel(r'Time offset $\tau$ ($/T$)', labelpad=2)
	plt.ylabel(r'Carrier phase offset $\varphi_c$ ($/\pi$)', labelpad=0)

	#cb.set_label(r'Bit error rate ($\mathrm{BER}$)', labelpad=-7, y=0.35)

	plt.savefig('pdf/berc2_Au%.2f_%s_%s.pdf'%(Au, mode, content))

def colorbar_only():
    fig = plt.figure(figsize=(0.375, 1.92))
    ax1 = fig.add_axes([0, 0.05, 0.25, 1])
    
    cmap = mpl.colors.ListedColormap(['0.0', '0.25', '0.5', '0.75', '1.0'])

    bounds = [0.0, 1e-6, 0.45, 0.55, 1-1e-6, 1.0]
    norm = mpl.colors.BoundaryNorm(bounds, cmap.N)
    cb2 = mpl.colorbar.ColorbarBase(ax1, cmap=cmap,
                                         boundaries=bounds,
                                         ticks=bounds, # optional
                                         orientation='vertical')

    cb2.set_ticklabels(['0', '$10^{-6}$', '0.45', '0.55', '$1-10^{-6}$', '1'])
    cb2.set_label(r'Bit error rate ($\mathrm{BER}$)', fontsize=12, labelpad=-7, y=0.4)

    plt.savefig('pdf/cb.pdf')

if __name__ == '__main__':
	plot()
	#colorbar_only()

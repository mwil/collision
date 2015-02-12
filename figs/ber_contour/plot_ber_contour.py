# Copyright 2013-2014 Matthias Wilhelm

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

from __future__ import print_function

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.cm as cm

mpl.rc_file("../rc/3fig-contour-rc.txt")

def plot(mode, Au, content):
	data = np.load("data/ber_Au%.2f_%s.npz"%(Au, content))
	Zu = data["BER_U"]
	Zs = data["BER_S"]
	Z = (Zu if mode in ("usync",) else Zs)

	PHI, TAU = np.meshgrid(data["phi_range"], data["tau_range"])

	print("Shapes: TAU %s, PHI %s, Zu %s" %(TAU.shape, PHI.shape, Z.shape))

	CS  = plt.contourf(TAU, PHI/np.pi, Z,  levels=(0, 1e-6, 0.45, 0.55, 1-1e-6, 1), colors=("0.0", "0.5", "0.75", "0.85", "1.0"), origin="lower")
	CS2 = plt.contour(CS, levels=(1e-6, 0.45, 0.55, 1-1e-6), colors=("w",)+3*("r",), linewidths=(1.0, 0.75,0.75,0.75,0.75), origin="lower", hold="on")

	plt.annotate(r"capture zone", xy=(-0.35, 0.125), xytext=(-1.425, 0.475), fontsize=10, color="1.0",
		arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=-0.2", color="1.0"))

	plt.axis([-1.5, 1.5, -1, 1])
	plt.xlabel(r"Time offset $\tau$ ($/T$)", labelpad=2)
	plt.ylabel(r"Carrier phase offset $\varphi_c$ ($/\pi$)", labelpad=0)

	#cb.set_label(r"Bit error rate ($\mathrm{BER}$)", labelpad=-7, y=0.35)

	plt.savefig("pdf/berc2_Au%.2f_%s_%s.pdf"%(Au, mode, content))

def colorbar_only():
	fig = plt.figure(figsize=(0.375, 1.92))
	ax1 = fig.add_axes([0, 0.05, 0.25, 1])

	cmap = mpl.colors.ListedColormap(["0.0", "0.5", "0.75", "0.85", "1.0"])

	bounds = [0.0, 1e-6, 0.45, 0.55, 1-1e-6, 1.0]
	norm = mpl.colors.BoundaryNorm(bounds, cmap.N)
	cb2 = mpl.colorbar.ColorbarBase(ax1, cmap=cmap,
                                         norm=norm,
                                         boundaries=bounds,
                                         ticks=bounds, # optional
                                         orientation="vertical")

	cb2.set_ticklabels(["0", "$10^{-6}$", "0.45", "0.55", "$1-10^{-6}$", "1"])
	cb2.set_label(r"Bit error rate ($\mathrm{BER}$)", fontsize=12, labelpad=-7, y=0.4)

	plt.savefig("pdf/cb.pdf")

if __name__ == "__main__":
	mode = ("sync", "usync")[1] # choose if you want the BER performance of the sync"ed sender at the receiver or the other

	plot(mode, Au=100.0, content="unif")
	#colorbar_only()

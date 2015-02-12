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
import itertools as it

from style_ser_contour_AsAu import Style1col


def do_plot(mode, content, decision, wide):
	if mode in ("usync",):
		_plot_usync(content, decision, wide)
	else:
		_plot_sync(content, decision, wide)


def _plot_sync(content, decision, wide):
	global style
	style.apply("sync", content, decision, wide)

	data    = np.load("data/prr_AsAu_%s_%s%s.npz"%(content, decision, wide))
	data_bc = np.load("../ber_contour_AsAu/data/prr_AsAu_%s%s.npz"%(content, wide))

	AU, TAU = np.meshgrid(-data["Au_range_dB"], data["tau_range"])

	plt.clf()
	plt.axis([data["tau_range"][0], data["tau_range"][-1], -data["Au_range_dB"][-1], -data["Au_range_dB"][0]])

	assert TAU.shape == AU.shape == data["PRR_S"].shape, "The inputs TAU, AU, PRR_S must have the same shape for plotting!"

	CSf = plt.contourf(TAU, AU, data["PRR_S"], levels=(0.0, 0.2, 0.4, 0.6, 0.8, 0.9, 1.0), colors=("1.0", "0.5", "0.25", "0.15", "0.05", "0.0"), origin="lower")
	CS2 = plt.contour(CSf,  colors = ("r",)*5+("w",), linewidths=(0.75,)*5+(1.0,), origin="lower", hold="on")

	CS_bc = plt.contour(TAU, AU, data_bc["PRR_S"], levels=(0.9,), colors="w", origin="lower", hold="on")

	style.annotate("sync", content, decision, wide)

	plt.xlabel(r"Time offset $\tau$ ($/T$)", labelpad=2)
	plt.ylabel(r"Signal power ratio ($\mathrm{SIR}$)", labelpad=2)

	plt.savefig("pdf/prr_sync_%s_%s%s_z.pdf"%(content, decision, wide))



def _plot_usync(content, decision, wide):
	global style
	style.apply("usync", content, decision, wide)

	data = np.load("data/prr_AsAu_%s_%s%s.npz"%(content, decision, wide))

	#Zs_bc = np.load("../ber_contour_AsAu/data/prr_s_AsAu_%s%s.npy"%(content, wide))
	#Zu_bc = np.load("../ber_contour_AsAu/data/prr_u_AsAu_%s%s.npy"%(content, wide))

	AU, TAU = np.meshgrid(-data["Au_range_dB"], data["tau_range"])

	plt.clf()
	plt.axis([data["tau_range"][0], data["tau_range"][-1], -data["Au_range_dB"][-1]], -data["Au_range_dB"][0])

	assert TAU.shape == AU.shape == data["PRR_U"].shape, "The inputs TAU, AU, PRR_S must have the same shape for plotting!"

	CSf = plt.contourf(TAU, AU, data["PRR_U"], hatches=(None,)+("////",)*3, levels=(0.0, 0.2, 0.4, 0.6, 0.8, 0.9, 1.0), colors=("1.0", "0.75", "0.5", "0.25", "0.15", "0.0"), origin="lower")
	CS2 = plt.contour(CSf, colors = 4*("r",)+("w",), linewidths=(1, 0.75, 0.75, 0.75, 0.75), origin="lower", hold="on")

	style.annotate("usync", content, decision, wide)

	plt.xlabel(r"Time offset $\tau$ ($/T$)", labelpad=2)
	plt.ylabel(r"Signal power ratio ($\mathrm{SIR}$)", labelpad=2)

	plt.savefig("pdf/prr_usync_%s_%s%s_z.pdf"%(content, decision, wide))



def colorbar_only():
	fig = plt.figure(figsize=(0.375, 1.3))
	ax1 = fig.add_axes([0, 0.05, 0.25, 1])

	cmap = mpl.colors.ListedColormap(["1.0", "0.75", "0.5", "0.25", "0.15", "0.0"])

	bounds = [0.0, 0.2, 0.4, 0.6, 0.8, 0.9, 1.0]
	norm = mpl.colors.BoundaryNorm(bounds, cmap.N)
	cb2 = mpl.colorbar.ColorbarBase(ax1, cmap=cmap, boundaries=bounds, ticks=bounds, orientation="vertical")

	cb2.set_label(r"Packet reception ratio ($\mathrm{PRR}$)", fontsize=8)

	plt.savefig("pdf/cb-1fig.pdf")



if __name__ == "__main__":
	#for mode, content in it.product(("sync", "usync"), ("unif", "same")):
	mode =		("sync", "usync")[0]
	content =	("unif", "same")[1]
	decision =	("soft", "hard")[0]
	wide =		("", "_wide")[1]

	style = Style1col()

	#for decision in ("hard", "soft"):
		#plot(mode, content, decision, wide)

	#plot ("sync", "unif", "soft", "")
	do_plot(mode, content, decision, wide)

	#colorbar_only()

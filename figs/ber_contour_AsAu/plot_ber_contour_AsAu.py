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

import argparse

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.cm as cm

mpl.rc_file("../rc/1fig-contour-rc.txt")

from style_ber_contour_AsAu import Style1col

def do_plot(mode, content, wide):
	global style
	style.apply(mode, content, wide)

	data = np.load("data/prr_AsAu_%s%s.npz"%(content, wide))

	AU, TAU = np.meshgrid(-data["Au_range_dB"], data["tau_range"])
	Zu = data["PRR_U"]
	Zs = data["PRR_S"]

	assert TAU.shape == AU.shape == Zu.shape, "The inputs TAU, AU, PRR_U must have the same shape for plotting!"

	plt.clf()

	if mode in ("sync",):
		# Plot the inverse power ratio, sync signal is stronger for positive ratios
		CSf = plt.contourf(TAU, AU, Zs, levels=(0.0, 0.2, 0.4, 0.6, 0.8, 0.9, 1.0), colors=("1.0", "0.75", "0.5", "0.25", "0.15", "0.0"), origin="lower")
		CS2 = plt.contour(CSf, colors = ("r",)*5+("w",), linewidths=(0.75,)*5+(1.0,), origin="lower", hold="on")
	else:
		CSf  = plt.contourf(TAU, AU, Zs, levels=(0.0, 0.2, 0.4, 0.6, 0.8, 0.9, 1.0), colors=("1.0", "0.75", "0.5", "0.25", "0.15", "0.0"), origin="lower")
		CS2f = plt.contour(CSf, levels=(0.0, 0.2, 0.4, 0.6, 0.8, 1.0), colors=4*("r",)+("w",), linewidths=(0.75,)*4+(1.0,), origin="lower", hold="on")
		#CS2f = plt.contour(TAU, -AU, Zu, levels=(0.9, 1.0), colors=("0.0",), linewidths=(1.0,), origin="lower", hold="on")
		if content in ("unif",):
			CSu  = plt.contourf(TAU, AU, Zu, levels=(0.2, 1.0), hatches=("////",), colors=("0.75",), origin="lower")
			CS2  = plt.contour(CSu, levels=(0.2,), colors = ("r",), linewidths=(1.0,), origin="lower", hold="on")

	style.annotate(mode, content, wide)

	plt.axis([data["tau_range"][0], data["tau_range"][-1], -data["Au_range_dB"][-1], -data["Au_range_dB"][0]])

	plt.ylabel(r"Signal power ratio ($\mathrm{SIR}$)", labelpad=2)
	plt.xlabel(r"Time offset $\tau$ ($/T$)", labelpad=2)

	plt.savefig("pdf/prrc2_%s_%s%s_z.pdf"%(mode, content, wide))



if __name__ == "__main__":
	argp = argparse.ArgumentParser()
	argp.add_argument("mode",  choices=("sync", "usync"), help="Plot from the view of the synchronized or unsynchronized sender")
	argp.add_argument("content",  choices=("same", "unif"), help="Relation between data content in the two transmitted packets")
	argp.add_argument("-w", "--wide", action="store_true", help="Wide interval of time offsets used (-4T to 4T instead of -1.5T to 1.5T)")

	args = argp.parse_args()

	wide = ("_wide" if args.wide else "")

	style = Style1col()

	do_plot(args.mode, args.content, wide)

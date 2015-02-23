# Copyright 2015 Matthias Wilhelm

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

import NPZ
import PyPlot
const plt = PyPlot
using LaTeXStrings

# -----------------------------------------------------------------------------

function main()
	if length(ARGS) == 0
		# use the newest .npz file in the data directory for plotting
		do_plot(joinpath("data", sort(readdir("data"), by=(x)->splitext(x)[end]==".npz"?mtime(joinpath("data", x)):0.0)[end]))
	else
		for filename in ARGS
			if splitext(filename)[end] == ".npz"
				do_plot(filename)
			end
		end
	end
end
# -----------------------------------------------------------------------------

function do_plot(filename::String)
	println("Starting to plot data file: ", filename)

	data    = NPZ.npzread(filename)
	SER_U   = data["SER_U"]
	τ_range = data["tau_range"]
	𝜑_range = data["phi_range"]

	plt.clf()
	Cf = plt.contourf(τ_range, 𝜑_range/π, SER_U, levels=(0.0, 1e-3, 0.25, 0.9, 1.0), colors=("0.0", "0.5", "0.75", "1."), origin="lower")
	#plt.contour(Cf, colors=("r","r","w"), linewidths=(0., 0.75, 1.0), origin="lower", hold="on")

	plt.xlabel(L"Time offset $\tau$ ($/T$)", labelpad=2)
	plt.ylabel(L"Carrier phase offset $\varphi_c$ ($/\pi$)", labelpad=0)

	plt.savefig("pdf/$(splitext(splitdir(filename)[end])[1]).pdf", bbox_inches="tight")
end
# -----------------------------------------------------------------------------



main()

# Copyright 2015-2017 Matthias Wilhelm

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
	if length(ARGS) == 0 # use the newest .npz file in the data directory for plotting
		do_plot(joinpath("data",
		                 sort(readdir("data"),
		                      by=(x)->splitext(x)[end]==".npz"?mtime(joinpath("data", x)):0.0)[end]))
	else
		for filename in ARGS
			if splitext(filename)[end] == ".npz"
				do_plot(filename)
			else
				println("Ignoring file $(filename), a npz archive is required!")
			end
		end
	end
end
# -----------------------------------------------------------------------------


function do_plot(filename::String)
	println("Starting to plot data file: ", filename)

	data = NPZ.npzread(filename)

	plt.clf()
	plt.grid()

	plt.plot(0:data["ninterf"], prepend!(data["PRR_S_same_n"], [1.0]), "b^-")
	plt.plot(0:data["ninterf"], prepend!(data["PRR_S_same_1"], [1.0]), "bo-")
	plt.plot(0:data["ninterf"], prepend!(data["PRR_S_unif_n"], [1.0]), "r^-")
	plt.plot(0:data["ninterf"], prepend!(data["PRR_S_unif_1"], [1.0]), "ro-")

	# proxy artists to get black markers
   # http://www.mail-archive.com/matplotlib-users@lists.sourceforge.net/msg25195.html
	#l1, = ax.plot(1:data["ninterf"], data["PRR_S_unif_1"], "k^")
	#l2, = ax.plot(1:data["ninterf"], data["PRR_S_unif_1"], "ko")
	#l1.remove()
	#l2.remove()

	plt.xlabel(L"Number of interferers $n$", labelpad=2)
	plt.ylabel(L"Packet reception ratio (PRR)", labelpad=2)

	plt.savefig(joinpath("pdf", "$(splitext(splitdir(filename)[end])[1]).pdf"), bbox_inches="tight")
end
# -----------------------------------------------------------------------------


main()


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

push!(LOAD_PATH, "../../src")

import PhiTau
@everywhere const pt = PhiTau

@everywhere const T = 1.0
@everywhere const τ = 0.0
@everywhere const As = 1.0
@everywhere const Au = sqrt(100)
@everywhere const nsyms = 256
@everywhere const ninterf = 8

@everywhere function calcPRR!(dPRR_S::DArray, dPRR_U::DArray, content::String, decision::String; mode="1")
	if !(content in ("same", "unif"))
		throw(ArgumentError("Content must be in {same, unif}"))
	end
	if !(decision in ("hard", "soft"))
		throw(ArgumentError("Decision must be in {hard, soft}"))
	end

	PRR_S = localpart(dPRR_S)
	PRR_U = localpart(dPRR_U)

	lidx = localindexes(dPRR_U)

	for n in 1:ninterf
		if mode == "1"
			Au = As * sqrt(n)
		end
	end
end

function do_gen()
	PRR_S = dzeros(length(Au_range), length(τ_range))
	PRR_U = dzeros(length(Au_range), length(τ_range))

	@sync @parallel for i=1:length(workers())
		calcPRR!(PRR_S, PRR_U, content, decision)
	end

	NPZ.npzwrite("data/ninf_$(content)_$(decision).npz",
				 Dict("PRR_S"=>convert(Array, PRR_S), "PRR_U"=>convert(Array, PRR_U),
					  "tau"=>τ, "phi_range"=>𝜑_range,
					  "As"=>As, "nsyms"=>nsyms, "nsteps"=>nsteps))
end

function main()
	if length(ARGS) == 2
		do_gen(ARGS...)
	else
		println("Two required arguments: content={same,unif}, decision={hard,soft}")
	end
end

main()
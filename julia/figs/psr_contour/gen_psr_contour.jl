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

@everywhere using DistributedArrays

# -----------------------------------------------------------------------------

function main()
	do_gen()
end

# -----------------------------------------------------------------------------

function do_gen()
	const T  = 1.0
	const nsyms  = 2^10
	const nsteps = 2^8

	const τ_range = linspace(-2.5T, 2.5T, nsteps)
	const 𝜑_range = linspace( -π,  π, nsteps)

	PSR_U = dzeros(length(𝜑_range), length(τ_range))

	@sync @parallel for i=1:length(workers())
		calcPSR!(PSR_U, τ_range, 𝜑_range; nsyms=nsyms)
	end

	NPZ.npzwrite("data/psr.npz", Dict("PSR_U"=>convert(Array, PSR_U),
				 "tau_range"=>τ_range, "phi_range"=>𝜑_range, "nsyms"=>nsyms, "nsteps"=>nsteps))
end

# -----------------------------------------------------------------------------

@everywhere function calcPSR!(dPSR_U::DArray, τ_range::Vector{Float64}, 𝜑_range::Vector{Float64}; nsyms=2^10)
	PSR_U = localpart(dPSR_U)
	lidx = localindexes(dPSR_U)

	β_send_syms = zeros(Int, nsyms)
	β_send_chips = zeros(Complex128, 16*nsyms)

	for (τ_idx, τ) in enumerate(τ_range[lidx[2]])
		println("τ = ", @sprintf("% .3f", τ), ". Worker progress: ", @sprintf("%6.2f", 100.τ_idx/length(lidx[2])), "%")

		rand!(β_send_syms, 1:16)
		pt.map_chips!(β_send_chips, β_send_syms)

		RECV_CHIPS = pt.Λu(β_send_chips, 𝜑_range[lidx[1]], τ)

		for 𝜑_idx in 1:length(lidx[1])
			PSR_U[𝜑_idx,τ_idx] = 20*log10(mean(abs(real(RECV_CHIPS[:,𝜑_idx]))))
		end
	end
	println(minimum(PSR_U))
end

# -----------------------------------------------------------------------------

main()

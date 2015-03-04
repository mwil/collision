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
	if length(ARGS) == 2
		do_gen(ARGS...)
	else
		println("Two required arguments: content={same,unif}, decision={hard,soft}")
	end
end

function main_vid()
	if length(ARGS) == 2
		for SIR in -30:10
			do_gen(ARGS...; SIR=SIR)
		end
	else
		println("Two required arguments: content={same,unif}, decision={hard,soft}")
	end
end

# -----------------------------------------------------------------------------

function do_gen(content::String, decision::String; SIR=-20.0)
	const T  = 1.0
	const Au = √(10^(-SIR/10))
	const nsyms  = 2^12
	const nsteps = 2^9

	const τ_range = linspace(-2.5T, 2.5T, nsteps)
	const 𝜑_range = linspace( -π,  π, nsteps)

	SER_S = dzeros(length(𝜑_range), length(τ_range))
	SER_U = dzeros(length(𝜑_range), length(τ_range))

	@sync @parallel for i=1:length(workers())
		calcSER!(SER_S, SER_U, content, decision, τ_range, 𝜑_range, As=1.0, Au=Au, nsyms=nsyms)
	end

	NPZ.npzwrite("data/serc_$(content)_$(decision)_SIR_$(round(Int, SIR)).npz",
				 Dict("SER_S"=>convert(Array, SER_S), "SER_U"=>convert(Array, SER_U),
					  "tau_range"=>τ_range, "phi_range"=>𝜑_range,
					  "As"=>1.0, "Au"=>Au, "nsyms"=>nsyms, "nsteps"=>nsteps))
end

# -----------------------------------------------------------------------------

@everywhere function calcSER!(dSER_S::DArray, dSER_U::DArray, content::String, decision::String,
		τ_range::Vector{Float64}, 𝜑_range::Vector{Float64}; As=1.0, Au=√100, nsyms=2^10, nsteps=2^8)

	if !(content in ("same", "unif"))
		throw(ArgumentError("Content must be in {same, unif}"))
	end
	if !(decision in ("hard", "soft"))
		throw(ArgumentError("Decision must be in {hard, soft}"))
	end

	SER_S = localpart(dSER_S)
	SER_U = localpart(dSER_U)

	lidx = localindexes(dSER_U)

	α_send_syms = zeros(Int, nsyms)
	β_send_syms = zeros(Int, nsyms)
	α_send_chips = zeros(Complex128, 16*nsyms)
	β_send_chips = zeros(Complex128, 16*nsyms)

	recv_syms = zeros(Int, nsyms)


	for (τ_idx, τ) in enumerate(τ_range[lidx[2]])
		println("τ = ", @sprintf("% .3f", τ), ". Worker progress: ", @sprintf("%6.2f", 100.τ_idx/length(lidx[2])), "%")

		if content == "same"
			rand!(α_send_syms, 1:16)
			β_send_syms  = α_send_syms
			pt.map_chips!(α_send_chips, α_send_syms)
			β_send_chips = α_send_chips
		else
			rand!(α_send_syms, 1:16)
			rand!(β_send_syms, 1:16)
			pt.map_chips!(α_send_chips, α_send_syms)
			pt.map_chips!(β_send_chips, β_send_syms)
		end

		RECV_CHIPS = As*α_send_chips .+ Au*pt.Λu(β_send_chips, 𝜑_range[lidx[1]], τ)

		if decision == "hard"
			RECV_CHIPS = complex(sign(real(RECV_CHIPS)), sign(imag(RECV_CHIPS)))
		end

		tic()
		for 𝜑_idx in 1:length(lidx[1])
			pt.detect_syms_corr!(recv_syms, RECV_CHIPS[:,𝜑_idx])

			SER_S[𝜑_idx,τ_idx] = countnz(recv_syms .≠ α_send_syms)/nsyms
			SER_U[𝜑_idx,τ_idx] = countnz(recv_syms .≠ β_send_syms)/nsyms
		end
		toc()
	end
end

# -----------------------------------------------------------------------------

main_vid()

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

# -----------------------------------------------------------------------------

function do_gen(content::String, decision::String)
	const T = 1.0
	const nsyms = 2^8
	const nsteps = 2^8
	const pktlen = 8

	const τ_range  = linspace(-1.5T, 1.5T, nsteps)
	const Au_range = √logspace(-1, 5, nsteps)
	const 𝜑_range  = linspace(-π, π, nsteps)

	PRR_S = dzeros(length(Au_range), length(τ_range))
	PRR_U = dzeros(length(Au_range), length(τ_range))

	@sync @parallel for i=1:length(workers())
		calcPRR!(PRR_S, PRR_U,
		   content, decision, τ_range, Au_range, 𝜑_range,
			As=1.0, nsyms=nsyms, nsteps=nsteps, pktlen=pktlen)
	end

	NPZ.npzwrite(
	   joinpath("data", "scAu_$(content)_$(decision).npz"),
		Dict(
		   "PRR_S"=>convert(Array, PRR_S),
		   "PRR_U"=>convert(Array, PRR_U),
			"tau_range"=>convert(Array, τ_range),
			"phi_range"=>convert(Array, 𝜑_range),
			"Au_range"=>convert(Array, Au_range),
			"As"=>1.0,
			"nsyms"=>nsyms,
			"nsteps"=>nsteps,
			"pktlen"=>pktlen))
end

# -----------------------------------------------------------------------------

@everywhere function calcPRR!(
      dPRR_S::DArray,
      dPRR_U::DArray,
      content::String,
      decision::String,
      τ_range::AbstractVector{Float64},
      Au_range::AbstractVector{Float64},
      𝜑_range::AbstractVector{Float64}
      ; As=1.0, nsyms=2^8, nsteps=2^7, pktlen=8)

	if !(content in ("same", "unif"))
		throw(ArgumentError("Content must be in {same, unif}"))
	end
	if !(decision in ("hard", "soft"))
		throw(ArgumentError("Decision must be in {hard, soft}"))
	end

	PRR_S = localpart(dPRR_S)
	PRR_U = localpart(dPRR_U)

	lidx = localindexes(dPRR_U)

   α_send_syms = zeros(Int, nsyms)
	β_send_syms = zeros(Int, nsyms)
	α_send_chips = zeros(Complex128, 16*nsyms)
	β_send_chips = zeros(Complex128, 16*nsyms)

	ser_s = zeros(Float64, nsteps)
	ser_u = zeros(Float64, nsteps)

	recv_syms = zeros(Int, nsyms)

	for (τ_idx, τ) in enumerate(τ_range[lidx[2]])
		tic()

		rand!(α_send_syms, 1:16)
		pt.map_chips!(α_send_chips, α_send_syms)

		if content == "same"
			β_send_syms  = α_send_syms
			β_send_chips = α_send_chips
		else
			rand!(β_send_syms, 1:16)
			pt.map_chips!(β_send_chips, β_send_syms)
		end

		recv_chips = pt.Λu(β_send_chips, 𝜑_range, τ)

		for (Au_idx, Au) in enumerate(Au_range[lidx[1]])
			RECV_CHIPS = As*α_send_chips .+ Au*recv_chips

			if decision == "hard"
				RECV_CHIPS = complex(sign(real(RECV_CHIPS)), sign(imag(RECV_CHIPS)))
			end

			for 𝜑_idx in 1:nsteps
				pt.detect_syms_corr!(recv_syms, RECV_CHIPS[:,𝜑_idx])

				ser_s[𝜑_idx] = countnz(recv_syms .≠ α_send_syms)/nsyms
				ser_u[𝜑_idx] = countnz(recv_syms .≠ β_send_syms)/nsyms
			end

			PRR_S[Au_idx, τ_idx] = mean((1.0-ser_s).^pktlen)
			PRR_U[Au_idx, τ_idx] = mean((1.0-ser_u).^pktlen)
		end

		toc()
		println("τ = ", @sprintf("% .3f", τ), ". Worker progress: ", @sprintf("%6.2f", 100.0τ_idx/length(lidx[2])), "%")
	end
end

# -----------------------------------------------------------------------------

main()

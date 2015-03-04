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
	if length(ARGS) == 1
		do_gen(ARGS...)
	else
		println("One required argument: decision={hard,soft}")
	end
end

# -----------------------------------------------------------------------------

function do_gen(decision::String)
	const T = 1.0
	const nsyms = 2^10
	const nsteps = 2^10
	const pktlen = 16
	const ninterf = 20

	results = Dict("As"=>1.0, "nsyms"=>nsyms, "nsteps"=>nsteps, "pktlen"=>pktlen, "ninterf"=>ninterf)

	for content in ("same", "unif"), mode in ("1", "n")
		PRR_S = dzeros(ninterf)

		@sync @parallel for i=1:length(workers())
			calcPRR!(PRR_S, content=content, decision=decision, mode=mode, τ=0.0,
					 As=1.0, nsyms=nsyms, nsteps=nsteps, pktlen=pktlen)
		end

		results["PRR_S_$(content)_$(mode)"] = convert(Array, PRR_S)
	end

	NPZ.npzwrite(joinpath("data", "ninf_$(decision).npz"), results)
end

# -----------------------------------------------------------------------------

@everywhere function calcPRR!(dPRR_S::DArray; content="unif", decision="soft", mode="1",
							  As=1.0, τ=0.0, nsyms=2^8, nsteps=2^7, pktlen=8)

	if !(content in ("same", "unif"))
		throw(ArgumentError("Content must be in {same, unif}"))
	end
	if !(decision in ("hard", "soft"))
		throw(ArgumentError("Decision must be in {hard, soft}"))
	end

	PRR_S = localpart(dPRR_S)
	lidx = localindexes(dPRR_S)

	ser_s = zeros(Float64, nsteps)
	recv_syms = zeros(Int, nsyms)

	α_send_syms = zeros(Int, nsyms)
	β_send_syms = zeros(Int, nsyms)
	α_send_chips = zeros(Complex128, 16*nsyms)
	β_send_chips = zeros(Complex128, 16*nsyms)

	for (nidx, ninterf) in enumerate(lidx[1])
		println("Simulating $(ninterf) concurrent interferers in mode='$(mode)' ...")

		if mode == "1"
			Au = (As/√2) * √ninterf
			ninterf  = (ninterf > 0)? 1: 0
		else
			Au = As/√2
		end

		rand!(α_send_syms, 1:16)
		pt.map_chips!(α_send_chips, α_send_syms)

		if content == "same"
			β_send_syms  = α_send_syms
			β_send_chips = α_send_chips
		end

		RECV_CHIPS = As*α_send_chips

		for inf in 1:ninterf
			if content == "unif"
				rand!(β_send_syms, 1:16)
				pt.map_chips!(β_send_chips, β_send_syms)
			end

			RECV_CHIPS .+= Au*pt.Λu(β_send_chips, 2π*rand(nsteps), τ)
		end

		if decision == "hard"
			RECV_CHIPS = complex(sign(real(RECV_CHIPS)), sign(imag(RECV_CHIPS)))
		end

		for 𝜑_idx in 1:nsteps
			pt.detect_syms_corr!(recv_syms, RECV_CHIPS[:,𝜑_idx])

			ser_s[𝜑_idx] = countnz(recv_syms .≠ α_send_syms)/nsyms
		end


		PRR_S[nidx] = mean((1.0-ser_s).^pktlen)
	end
end

# -----------------------------------------------------------------------------

main()

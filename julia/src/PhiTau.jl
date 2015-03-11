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

module PhiTau

export Λu, map_chips!, detect_syms_corr!

const T = 1.0

# -----------------------------------------------------------------------------

tmp_chips = zeros(Complex128, 16, 16)

# Initialize the chips according to the IEEE 802.15.4-2006 Standard (§6.5.2.3)
# instead of bits, use constellation points (0,1) -> (-1,1), i->real, q->imag
tmp_chips[:,1] = complex(2.0*[1,0,1,0,1,0,0,1,0,0,0,1,0,1,1,1].-1, 2.0*[1,1,0,1,1,0,0,1,1,1,0,0,0,0,1,0].-1)
tmp_chips[:,9] = conj(tmp_chips[:,1])

# the other chipping sequences are shifted versions of the two sequences above
for sym_idx in 1:7
	tmp_chips[:,sym_idx+1] = [tmp_chips[end-1:end, sym_idx]; tmp_chips[1:end-2, sym_idx]]
	tmp_chips[:,sym_idx+9] = conj(tmp_chips[:,sym_idx+1])
end

const CHIPSEQ_MAPPING = tmp_chips

# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------

function Λu(β::Vector{Complex128}, 𝜑_range::Vector{Float64}, τ::Float64)
	complex(Λu_i(β, 𝜑_range, τ), Λu_q(β, 𝜑_range, τ))
end
# -----------------------------------------------------------------------------

function Λu_i(β::Vector{Complex128}, 𝜑_range::Vector{Float64}, τ::Float64)
	𝜑_p = (π/2T)τ
	τ_i_, τ_q_ = mod(τ, 2T),       mod((τ+T), 2T)
	k_i,  k_q  = floor(Int, τ/2T), floor(Int, (τ+T)/2T)

	βk_i, βkn_i = shift_indices(real(β), k_i)
	βk_q, βkn_q = shift_indices(imag(β), k_q)

	1/2T * (cos(𝜑_range').*(cos(𝜑_p)*(τ_i_*βkn_i .+ (2T-τ_i_)*βk_i).-sin(𝜑_p)*(2T/π) * (βkn_i.-βk_i))
		  .-sin(𝜑_range').*(sin(𝜑_p)*(τ_q_*βkn_q .+ (2T-τ_q_)*βk_q).+cos(𝜑_p)*(2T/π) * (βkn_q.-βk_q)))
end
# -----------------------------------------------------------------------------

function Λu_q(β::Vector{Complex128}, 𝜑_range::Vector{Float64}, τ::Float64)
	𝜑_p = (π/2T)τ
	τ_q_, τ_i_ = mod(τ, 2T),       mod((τ-T), 2T)
	k_q,  k_i  = floor(Int, τ/2T), floor(Int, (τ-T)/2T)

	βk_i, βkn_i = shift_indices(real(β), k_i)
	βk_q, βkn_q = shift_indices(imag(β), k_q)

	1/2T * (cos(𝜑_range').*(cos(𝜑_p)*(τ_q_*βkn_q .+ (2T-τ_q_)*βk_q).-sin(𝜑_p)*(2T/π) * (βkn_q.-βk_q))
		  .-sin(𝜑_range').*(sin(𝜑_p)*(τ_i_*βkn_i .+ (2T-τ_i_)*βk_i).+cos(𝜑_p)*(2T/π) * (βkn_i.-βk_i)))
end
# -----------------------------------------------------------------------------

function shift_indices(X::Vector{Float64}, k::Int)
	if k > 0
		Xk  = [zeros(k);   X[1:end-k]]
		Xkn = [zeros(k+1); X[1:end-k-1]]
	elseif k < 0
		k = abs(k)
		Xk  = [X[(k+1):end]; zeros(k)]
		Xkn = [X[k:end];     zeros(k-1)]
	else # k == 0
		Xk  = X
		Xkn = [0.0; X[1:end-1]]
	end

	return Xk, Xkn
end

# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------

function map_chips!(chipseq::Vector{Complex128}, syms::Vector{Int})
	for (idx, sym) in enumerate(syms)
		chipseq[1+16(idx-1):16idx] = CHIPSEQ_MAPPING[:,sym]
	end

	return chipseq
end

# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------

function detect_syms_corr!(recv_syms::Vector{Int}, recv_chips::Vector{Complex128})
	if length(recv_chips) % 16 ≠ 0
		throw(DimensionMismatch("Input recv_chips contains an incomplete chipping sequence (<16 chips)!"))
	end

	sym_corrs = zeros(Complex128, 16)

	for idx in 1:length(recv_syms)
		curr_chips = recv_chips[1+16(idx-1):16idx]

		sym_correlate!(sym_corrs, curr_chips/maxabs(curr_chips))
		recv_syms[idx] = sym_bestmatch(abs(real(sym_corrs)))
	end

	return recv_syms
end
# -----------------------------------------------------------------------------

## Implements the correlate function from numpy for the "valid" setting
## (http://docs.scipy.org/doc/numpy/reference/generated/numpy.correlate.html)
#function sym_correlate{T<:Number}(a::Matrix{T}, v::Vector{T})
#	real(sum(a.*conj(v), 1))'
#end

@inline function sym_correlate!(result::Vector{Complex128}, chipseq::Vector{Complex128})
	for sym in 1:16
		@inbounds result[sym] = 0

		@inbounds @simd for idx in 1:16 # index in chip sequence
			result[sym] += CHIPSEQ_MAPPING[idx, sym] * conj(chipseq[idx])
		end
	end

	return result
end
# -----------------------------------------------------------------------------

#function sym_bestmatch(sym_corrs::Vector{Float64})
#	best_syms = [1:16;][sym_corrs .> (maximum(sym_corrs) - 1e-9)]  # alternative version

#	return rand(best_syms)
#end

@inline function sym_bestmatch(sym_corrs::Vector{Float64})
	best_syms = Int[]
	best_corr = 0.0

	for sym in 1:16
		if sym_corrs[sym] > best_corr
			best_syms = Int[sym]
			best_corr = sym_corrs[sym]
		elseif isapprox(best_corr, sym_corrs[sym])
			push!(best_syms, sym)
		end
	end

	return rand(best_syms)
end
# -----------------------------------------------------------------------------


end

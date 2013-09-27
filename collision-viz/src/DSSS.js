/* Copyright 2013 Matthias Wilhelm

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
*/

/***
 * Generate DSSS chipping sequences of IEEE 802.15.4
 */

var DSSS = {
	"chips" : {0: [1,1,0,1,1,0,0,1,1,1,0,0,0,0,1,1,0,1,0,1,0,0,1,0,0,0,1,0,1,1,1,0],
		       8: [1,0,0,0,1,1,0,0,1,0,0,1,0,1,1,0,0,0,0,0,0,1,1,1,0,1,1,1,1,0,1,1]}
};

// building the rest of the chipping sequences by shifting ...
for (var sym=1; sym<8; sym++) {
	DSSS.chips[sym]   = DSSS.chips[sym-1].slice(-4).concat(DSSS.chips[sym-1].slice(0, -4));
    DSSS.chips[sym+8] = DSSS.chips[sym+7].slice(-4).concat(DSSS.chips[sym+7].slice(0, -4));
}

// change chips to constellation {0,1} -> {-1,1}
for (var sym=0; sym<16; sym++) {
	for (var chip=0; chip<32; chip++) {
		DSSS.chips[sym][chip] = 2*DSSS.chips[sym][chip] - 1;
	}
}

// Remain silent during this symbol (if symbol is given as None)
DSSS.chips['None'] = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0];

DSSS.map_syms = function (syms) {
    var sequence = [];
    
    // map symbols to chips
    for (var i=0; i<syms.length; i++) {
        sequence = sequence.concat(DSSS.chips[syms[i]]);
    }
        
    return sequence;
};

DSSS.correlate = function (a, v) {
	// z[k] = sum_n a[n] * conj(v[n+k])
	var z = [];
	var k = 0;
	
	var sum = 0;
	
	for (var n=0; n<Math.min(a.length, v.length); n++) {
		sum += a[n] * v[k+n];
	}
	
	return sum;
}

DSSS.detect_corr = function (recv_chips) {
    var recv_syms = [];
    
    // Choose the symbol with the highest correlation value
    while (recv_chips.length > 0) {
        var curr_chips = recv_chips.slice(0, 32);
        var best_syms  = [];
        var best_corr  = 0;
        epsilon = 0.02;
        
        for (var i=0; i<16; i++) {
            var curr_corr = Math.abs(DSSS.correlate(DSSS.chips[i], curr_chips))/32;
            
            if (curr_corr > best_corr) {
                best_syms  = [i];
                best_corr  = curr_corr;
            /* Float rounding needed, use all symbols that are below the best symbol but in a threshold of epsilon */
            } else if (curr_corr > best_corr - epsilon) {
                best_syms.push(i);
            }
        }
        
        // all values with the same correlation could be detected, just choose one ...
        var rand_idx = Math.floor(Math.random() * best_syms.length);
        recv_syms.push(best_syms[rand_idx]);
        recv_chips = recv_chips.slice(32);
    }
    
    return recv_syms
};

DSSS.sym_dist = function (sym, chips) {
	var cerrs = 0;
	
	for (var i=0; i<chips.length; i++) {
		cerrs += (DSSS.chips[sym][i] == chips[i] ? 0 : 1);
	}
	
	return cerrs;
};

/**************************************************
 * Debugging Code
 */

DSSS.qa_map_syms = function () {
	alpha = DSSS.map_syms([0, 0]);
	beta  = DSSS.map_syms([1, 1]);
};

DSSS.chips_to_str = function (chips) {
	str = "";
		
	for (var i=0; i<chips.length; i++) {
		if (i!=0 && !(i%32)) {
			str += " ";
		}
		
		str += (chips[i] >= 0) ? 1 : 0;
	}
	
	return str;
};

DSSS.qa_chips = function () {
	alert(DSSS.chips_to_str(DSSS.chips[1]));
};

DSSS.qa_detect_corr = function () {
	alpha = DSSS.map_syms([13, 14]);
	beta  = DSSS.map_syms([2]);
	
	$("#dbg1")[0].innerHTML = DSSS.chips_to_str(alpha);
	$("#dbg2")[0].innerHTML = DSSS.chips_to_str(beta);
	
	recv_chips = Model.demod(alpha, beta, phi=0.0, tau=32.0, 1.0, 100.0);
	
	$("#dbg3")[0].innerHTML = DSSS.chips_to_str(recv_chips);
	
	result = DSSS.detect_corr(recv_chips);
	alert(result);
	
	return result;
};

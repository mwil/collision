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

var Model = {};

// Bit duration of the MSK modulation
var T = 1.0;

Model.detect_i = function (k, alpha_i, beta_i, beta_q, phi_c, tau, As, Au) {
	var _tau_   = tau % (2*T);
	var _tau_n_ = (tau+T) % (2*T);
	var omega_p = Math.PI / (2*T);
    var phi_p   = omega_p * tau;
	
    var k_tau   = Math.floor(tau/(2*T));
    var k_tau_n = Math.floor((tau+T)/(2*T));
    
    // use 0 if symbol is out of bounds
    var bkn_i = (0 <= k-1-k_tau   && k-1-k_tau   < beta_i.length) ? beta_i[k-1-k_tau]   : 0;
    var bk_i  = (0 <= k-k_tau     && k-k_tau     < beta_i.length) ? beta_i[k-k_tau]     : 0;
    var bkn_q = (0 <= k-1-k_tau_n && k-1-k_tau_n < beta_q.length) ? beta_q[k-1-k_tau_n] : 0;
    var bk_q  = (0 <= k-k_tau_n   && k-k_tau_n   < beta_q.length) ? beta_q[k-k_tau_n]   : 0;
    
    if (bkn_i == 0 && bk_i == 0 && bkn_q == 0 && bk_q == 0) {
    	// the unsynchronized signal has no contribution at all!
    	Au = 1.0;
    }
    
    var arg1 = Math.cos(phi_p) * (_tau_*bkn_i + (2*T-_tau_) * bk_i);
    var arg2 = ((2*T)/Math.PI) * Math.sin(phi_p) * (bkn_i - bk_i);
    var arg3 = Math.sin(phi_p) * (_tau_n_*bkn_q + (2*T-_tau_n_)*bk_q);
    var arg4 = ((2*T)/Math.PI) * Math.cos(phi_p) * (bkn_q - bk_q);
    
    var result = (T/2)*alpha_i[k]*As + (Au/4) * (Math.cos(phi_c) * (arg1 - arg2) - Math.sin(phi_c) * (arg3 + arg4));

	return result / ((T/2)*As*Au);
};

Model.detect_q = function (k, alpha_q, beta_i, beta_q, phi_c, tau, As, Au) {
    var _tau_   = tau % (2*T);
    var _tau_p_ = (tau-T) % (2*T);
    var omega_p = Math.PI / (2*T);
    var phi_p   = omega_p * tau;

    var k_tau   = Math.floor(tau/(2*T));
    var k_tau_p = Math.floor((tau-T)/(2*T));
    
    var bkn_i = (0 <= k-1-k_tau_p && k-1-k_tau_p < beta_i.length) ? beta_i[k-1-k_tau_p] : 0;
    var bk_i  = (0 <= k-k_tau_p   && k-k_tau_p   < beta_i.length) ? beta_i[k-k_tau_p]   : 0;
    var bkn_q = (0 <= k-1-k_tau   && k-1-k_tau   < beta_q.length) ? beta_q[k-1-k_tau]   : 0;
    var bk_q  = (0 <= k-k_tau     && k-k_tau     < beta_q.length) ? beta_q[k-k_tau]     : 0;
    
    if (bkn_i == 0 && bk_i == 0 && bkn_q == 0 && bk_q == 0) {
    	// the unsynchronized signal has no contribution at all! FIXED: don't let the attacker affect the correlation of chips that are not involved!
    	Au = 1.0;
    }
    
    var arg1 = Math.cos(phi_p) * (_tau_*bkn_q + (2*T-_tau_) * bk_q);
    var arg2 = ((2*T)/Math.PI) * Math.sin(phi_p) * (bkn_q - bk_q);
    var arg3 = Math.sin(phi_p) * (_tau_p_*bkn_i + (2*T-_tau_p_)*bk_i);
    var arg4 = ((2*T)/Math.PI) * Math.cos(phi_p) * (bkn_i - bk_i);
    
    var result = (T/2)*alpha_q[k]*As + (Au/4) * (Math.cos(phi_c) * (arg1 - arg2) - Math.sin(phi_c) * (arg3 + arg4));
    
    return result / ((T/2)*As*Au);
}; 

Model.interlace = function (chips_i, chips_q) {
	result = [];
	
	for (var i=0; i<chips_i.length; i++) {
		result = result.concat(chips_i[i]);
		result = result.concat(chips_q[i]);
	}
	
	return result;
}

Model.deinterlace = function (chips, even) {
    result = [];
	
	for (var i=0; i<chips.length; i++) {
    	if (!even && i%2) {
    		result = result.concat(chips[i]);
    	} else if (even && !(i%2)) {
    		result = result.concat(chips[i]);	
    	}
    }
	
	return result;
}

Model.demod = function (alpha, beta, phi_c, tau, As, Au) {
    var recv_chips_i = [];
    var recv_chips_q = [];
    
    // Split chipping sequences into I/Q
    var alpha_i = Model.deinterlace(alpha, true);
    var alpha_q = Model.deinterlace(alpha, false);
    var beta_i  = Model.deinterlace(beta, true);
    var beta_q  = Model.deinterlace(beta, false);

    for (var k=0; k < alpha.length/2; k++) {
        recv_chips_i = recv_chips_i.concat(Model.detect_i(k, alpha_i, beta_i, beta_q, phi_c, tau, As, Au));
        recv_chips_q = recv_chips_q.concat(Model.detect_q(k, alpha_q, beta_i, beta_q, phi_c, tau, As, Au));
    }
    
    // Interlace chips again ...
    var flat_chips = [];
    
    for (var i=0; i<recv_chips_i.length; i++) {
    	flat_chips = flat_chips.concat(recv_chips_i[i])
    	flat_chips = flat_chips.concat(recv_chips_q[i])
    }
    
    return flat_chips;
};

Model.detect_packet = function (chips) {
	var result = [];
	
	for (var i=0; i<chips.length; i++) {
		result.push((chips[i] >= 0) ? 1 : -1);
	}
	
	return result;
};


/**************************************************
 * Debugging Code
 */

Model.chips_to_str = function (chips) {
	str = "";
		
	for (var i=0; i<chips.length; i++) {
		if (i!=0 && !(i%32)) {
			str += " ";
		}
		
		str += (chips[i] >= 0) ? 1 : 0;
	}
	
	return str;
};

Model.qa_detect_packet = function () {
	alpha = DSSS.map_syms([13, 14]);
	beta  = DSSS.map_chips([2]);
	
	$("#dbg1")[0].innerHTML = Model.chips_to_str(alpha);
	$("#dbg2")[0].innerHTML = Model.chips_to_str(beta);
	
	recv_chips = Model.demod(alpha, beta, phi=0.0, tau=32.0, 1.0, 100.0);
	$("#dbg3")[0].innerHTML = Model.chips_to_str(recv_chips);
	result = Model.detect_packet(recv_chips);

	alert(result);
	
	return result;
};

Model.qa_detect_bit = function () {
	var k = 0;
	var alpha_i = [-1, 1,-1, 1,-1,-1];
	var alpha_q = [ 1, 1,-1,-1,-1, 1];
	var beta_i  = [-1, 1,-1, 1, 1,-1];
	var beta_q  = [-1,-1,-1, 1,-1, 1];
	var phi_c = Math.PI/4;
	var tau = -0.0;
	var As = 1.0;
	var Au = 100.0;
	
	recv_chips = Model.detect_q(k, alpha_q, beta_i, beta_q, phi_c, tau, As, Au);
	
	$("#dbg1")[0].innerHTML = Model.chips_to_str(recv_chips);
};

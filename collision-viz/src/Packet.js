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

function Packet (UI, symbols) {
	this.UI = UI;
	this.symbols = symbols;
	this.chip_errors = new Array(symbols.length);
	this.sym_corr = new Array(symbols.length);
	
	this.chips = DSSS.map_syms(this.symbols);
	this.chips_i = Model.deinterlace(this.chips, true);
	this.chips_q = Model.deinterlace(this.chips, false);
	
	this.init = function () {
		this.update_cerrs();
	}
	
	/*********************/
	this.update = function (sPacket, uPacket) {
		var alpha = sPacket.chips;
		var beta  = uPacket.chips;
		
		soft_chips = Model.demod(alpha, beta, this.UI.phi_c, this.UI.tau, this.UI.As, this.UI.Au);
		this.chips = Model.detect_packet(soft_chips)
		
		this.chips_i = Model.deinterlace(this.chips, true);
		this.chips_q = Model.deinterlace(this.chips, false);
		
		this.symbols = DSSS.detect_corr(soft_chips);
		
		this.update_cerrs();
		this.update_corr();
	};
	
	/*********************/
	this.update_cerrs = function () {
		for (var i=0; i<this.symbols.length; i++) {
			this.chip_errors[i] = DSSS.sym_dist(this.symbols[i], this.chips.slice(i*32, (i*32)+32));
		}
	}
	
	/*********************/
	this.update_corr = function () {
		for (var i=0; i<this.symbols.length; i++) {
			this.sym_corr[i] = DSSS.correlate(DSSS.chips[this.symbols[i]], this.chips.slice(i*32, (i*32)+32)) / 32;
		}
	}
	
	/*********************/
	this.set_syms = function (syms) {
		this.symbols = syms;
		
		this.chips = DSSS.map_syms(this.symbols);
		this.chips_i = Model.deinterlace(this.chips, true);
		this.chips_q = Model.deinterlace(this.chips, false);
		
		this.update_cerrs();
	};
	
	/*********************/
	this.set_sym = function (i, sym) {
		if (i < 0 || i > this.symbols.length) {
			return;
		} else {
			this.symbols[i] = sym;
			
			this.set_syms(this.symbols);
		}
	}
	
	/*********************/
	this.set_chips = function (chips) {
		this.chips = chips;
		
		this.chips_i = Model.deinterlace(this.chips, true);
		this.chips_q = Model.deinterlace(this.chips, false);
		
		this.symbols = DSSS.detect_corr(chips);
		this.update_cerrs();
	};
	
	/*********************/
	this.set_chips_iq = function (chips_i, chips_q) {
		this.chips_i = chips_i;
		this.chips_q = chips_q;
		
		this.chips = Model.interlace(chips_i, chips_q);
		
		this.symbols = DSSS.detect_corr(this.chips);
		this.update_cerrs();
	};
}

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

function barSyms (ctx, parent, packet, Xmin, Ymin) {
	this.ctx = ctx;
	this.parent = parent;
	this.packet = packet;
	this.Xmin = Xmin;
	this.Ymin = Ymin;
	
	this.header_height = this.parent.bit_height + this.parent.bit_yskip;
	
	/*********************/
	this.draw = function () {
		this.draw_header();
		this.draw_syms();
	}
	
	/*********************/
	this.draw_header = function () {
		this.ctx.save();
		
        this.ctx.font = "bold 10pt sans-serif";
    	this.ctx.fillText("Symbols", this.Xmin + this.parent.tau_offset + this.parent.header_width/2, this.Ymin + this.header_height/2);
    	
    	this.ctx.strokeRect(this.Xmin + this.parent.tau_offset, this.Ymin, this.parent.header_width, this.header_height + this.parent.border_skip);
    	
    	this.ctx.restore();
	};
	
	/*********************/
	this.draw_syms = function () {
		this.ctx.save();
		
    	xmin = this.Xmin + this.parent.tau_offset + this.parent.header_width + (17/2 * this.parent.bit_width + 7*this.parent.bit_xskip);
		for (var i=0; i<this.packet.symbols.length; i++) {
			
			var xoff = i*(this.parent.sym_xskip + this.parent.sym_width);
			this.ctx.font = "bold 14pt sans-serif";
			this.ctx.fillText(this.packet.symbols[i].toString(16).toUpperCase(), xmin + xoff, this.Ymin + this.header_height/2);
			this.ctx.font = "bold 8pt sans-serif";
			this.ctx.fillText(this.packet.chip_errors[i], xmin + xoff + this.parent.header_width - 30, this.Ymin + this.header_height - 5);
		}
		
		// draw background of symbols in alternating colors
		for (var i=0; i<this.packet.symbols.length; i++) {
			if (i%2) {
				this.ctx.fillStyle = "rgba(255, 255, 0, 0.2)";
			} else {
				this.ctx.fillStyle = "rgba(0, 255, 0, 0.2)";
			}
			
			this.ctx.fillRect(this.Xmin + this.parent.header_width + this.parent.border_skip + this.parent.tau_offset + i*this.parent.sym_width, 
							  this.Ymin, 
					          this.parent.sym_width, 
					          this.header_height + this.parent.border_skip);
		}
		
		// draw border all-around chips
		this.ctx.strokeRect(this.Xmin + this.parent.header_width + this.parent.tau_offset, 
							this.Ymin, 
							this.packet.symbols.length * this.parent.sym_width + 2*this.parent.border_skip + (this.parent.bit_width + this.parent.bit_xskip)/2, 
							this.header_height + this.parent.border_skip);
		
		this.ctx.restore();
	};
	
	/*********************/
	this.mouseDown = function (ev) {
	    var x = ev.pageX - $(UI.canvas).offset().left;
	    var y = ev.pageY - $(UI.canvas).offset().top;
	    
	    if (y > this.Ymin && y < this.Ymin + this.header_height) {
	    	curr_x = this.Xmin + this.parent.tau_offset + this.parent.header_width;
	    	
	    	for (var i=0; i<this.packet.symbols.length; i++) {	
	    		if (x > curr_x && x < curr_x + this.parent.sym_width) {
	    			this.packet.set_sym(i, (this.packet.symbols[i]+1)%16);
	    			
	    			return true;
	    		}
	    		
	    		curr_x += this.parent.sym_width + this.parent.sym_xskip;
	    	}
	    }
		
		return false;
	}
};

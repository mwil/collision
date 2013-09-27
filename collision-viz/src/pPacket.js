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

function pPacket (UI, packet, name, Xmin, Ymin, movable, readonly) {
	this.UI = UI;
	this.ctx = UI.context;
	this.packet = packet;
	this.name = name;
	this.Xmin = Xmin;
	this.Ymin = Ymin;
	this.movable = movable;
	this.readonly = readonly;
	
		
	this.bit_width = 8;
	this.bit_height = 32;
	this.bit_xskip = 2;
	this.bit_yskip = 4;
	
	this.header_width = 100;
	this.header_height = 2*this.bit_height + this.bit_yskip;
	
	this.border_skip = 4;
	
	this.sym_length = 16;
	this.sym_width = this.sym_length * (this.bit_width + this.bit_xskip); 
	this.sym_xskip = 0;//16;
	
	this.bC = new barChips(this.ctx, this, packet, Xmin, Ymin);
	this.bS = new barSyms(this.ctx, this, packet, Xmin, Ymin + this.header_height + this.border_skip);
	
	this.tau_offset = 0;
	
	/*********************/
	this.draw = function () {
		if (this.movable) {
			this.tau_offset = UI.tau * (this.bit_xskip + this.bit_width)/2;
		}
		
		this.bC.draw();
		this.bS.draw();
		
		// draw packet names to the left
		// http://stackoverflow.com/questions/3167928/drawing-rotated-text-on-a-html5-canvas
		this.ctx.save();
		this.ctx.font = "bold 16pt sans-serif";
		
		this.ctx.rotate(-Math.PI/2);
		this.ctx.fillText(this.name, -(this.Ymin + (this.bC.header_height + this.bS.header_height)/2), this.Xmin - 20 + this.tau_offset);
		this.ctx.restore();
	};
	
	/*********************/
	this.mouseDown = function (ev) {
		result = false;
		
		if (!this.readonly) {
			result |= this.bC.mouseDown(ev);
			result |= this.bS.mouseDown(ev);
		}
	    
	    return result;
	};
};

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

// Run once the DOM is ready
/**/
$(document).ready(
    function () {
    	UI.init();
    }
);

var UI = {};

UI.init = function () {
	UI.canvas = $('#CollisionCanvas')[0];
	UI.context = UI.canvas.getContext("2d");
	
	UI.canvas.width  = window.innerWidth - 25;
	UI.canvas.height = window.innerHeight - 50;
	
	UI.context.textAlign = "center";
	UI.context.textBaseline = "middle";
	UI.context.fillStyle = "black";
	
	$(UI.canvas).bind('mousedown', UI.mouseDown);
	
	UI.reset();
	
	UI.pM = new PaneMain(UI, 0, 0, UI.canvas.width, UI.canvas.height);
	
	UI.update();
};

UI.reset = function () {
	UI.packets = {'SYNC'  : new Packet(this, [1, 9, 2, 10]),
				  'USYNC' : new Packet(this, [0, 8, 1, 9]),
				  'RECV'  : new Packet(this, [])};
	
	this.packets["SYNC"].init();
	this.packets["USYNC"].init();
	this.packets["RECV"].init();
	
	UI.As    = 1.0;
	UI.Au    = 100.0;
	UI.phi_c = 0.0;
	UI.tau   = 0.0;
};

UI.update = function () {
	UI.As    = 1.0;
	UI.Au    = Math.pow(10,  parseFloat($("#AuAs")[0].value)/10);
	UI.phi_c = parseFloat($("#phi_c")[0].value) * Math.PI;
	UI.tau   = parseFloat($("#tau")[0].value);
	
	UI.packets['RECV'].update(UI.packets['SYNC'], UI.packets['USYNC']);
	
	UI.pM.update();
};

UI.mouseDown = function(ev) {
	if (UI.pM.mouseDown(ev)) {
		UI.update();
	}
};

/**/
/* The old code * 
 
// Run once the DOM is ready
$(document).ready(
    function () {
        UI.changed();
    }
);

var UI = {nsyms : 8};

UI.changed = function() {
	var ssyms = new Array(UI.nsyms);
	var usyms = new Array(UI.nsyms);
	
	var As    = 1.0;
	var Au    = Math.pow(10, parseFloat($("#AuAs")[0].value)/10);
	var phi_c = parseFloat($("#phi_c")[0].value) * Math.PI;
	var tau   = parseFloat($("#tau")[0].value);
	
	// collect the synchronized symbols from the form
	for (var i=0; i<UI.nsyms; i++) {
		var sym = $(".ssym")[i].value;
		
		if (sym == "") {
			ssyms[i] = "None";
		} else {
			ssyms[i] = parseInt(sym, 16);
		}
	}
	
	// collect the unsynchronized symbols from the form
	for (var i=0; i<UI.nsyms; i++) {
		var sym = $(".usym")[i].value;
		
		if (sym == "") {
			usyms[i] = "None";
		} else {
			usyms[i] = parseInt(sym, 16);
		}
	}
	
	// calculate stuff
	var alpha = DSSS.map_syms(ssyms);
	var beta  = DSSS.map_syms(usyms);
	
	recv_chips = Model.demod(alpha, beta, phi_c, tau, As, Au);
	
	result = DSSS.detect_corr(recv_chips);
	
	for (var i=0; i<UI.nsyms; i++) {
		$(".rsym")[i].value = result[i].toString(16);
	}
};
/*/

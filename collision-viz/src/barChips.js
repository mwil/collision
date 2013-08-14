function barChips (ctx, parent, packet, Xmin, Ymin) {
	this.ctx = ctx;
	this.parent = parent;
	this.packet = packet;
	this.Xmin = Xmin;
	this.Ymin = Ymin;
	
	this.header_height = 2*this.parent.bit_height + this.parent.bit_yskip;
	
	/*********************/
	this.draw = function () {
		this.draw_header();
		this.draw_chips();
	}
	
	/*********************/
	this.draw_header = function () {
		this.ctx.save();
		
        this.ctx.font = "bold 10pt sans-serif";
    	
    	this.ctx.fillText("Chips", this.Xmin + this.parent.tau_offset + this.parent.header_width/2, this.Ymin + this.header_height/2);
    	this.ctx.fillText("I", this.Xmin + this.parent.tau_offset + this.parent.header_width - 15, this.Ymin + this.parent.bit_height/2);
    	this.ctx.fillText("Q", this.Xmin + this.parent.tau_offset + this.parent.header_width - 15, this.Ymin + this.parent.bit_yskip + 3*this.parent.bit_height/2);
    	
    	this.ctx.strokeRect(this.Xmin + this.parent.tau_offset, this.Ymin - this.parent.border_skip, 
    						this.parent.header_width, this.header_height + 2*this.parent.border_skip);
    	this.ctx.restore();
	};
	
	/*********************/
	this.draw_chips = function () {
		var curr_x = this.Xmin + this.parent.tau_offset + this.parent.header_width + this.parent.border_skip;
		var curr_y = this.Ymin;
		
		chips = [this.packet.chips_i, this.packet.chips_q];
		
		this.ctx.save();
		
		for (var i=0; i<chips.length; i++) {
			curr_chips = chips[i];
			
			for (var chip=0; chip< curr_chips.length; chip++) {
				this.ctx.strokeRect(curr_x, curr_y, this.parent.bit_width, this.parent.bit_height);
				
				if (curr_chips[chip] == -1) {
		    		this.ctx.fillStyle = "black";
		    	} else {
		    		this.ctx.fillStyle = "white";
		    	}
				
				this.ctx.fillRect(curr_x, curr_y, this.parent.bit_width, this.parent.bit_height);
				
				curr_x += this.parent.bit_width + this.parent.bit_xskip;
				if (chip != 0 && !((chip+1)%this.parent.sym_length)) {
					curr_x += this.parent.sym_xskip;
				}
			}
			
			// reset initial position for the Q chips, keep up to date with curr_x above! 
			curr_x = this.Xmin + this.parent.tau_offset + this.parent.border_skip + this.parent.header_width + (this.parent.bit_width + this.parent.bit_xskip)/2;
			curr_y += this.parent.bit_height + this.parent.bit_yskip;
		}
		
		// draw background of symbols in alternating colors
		for (var i=0; i<this.packet.symbols.length; i++) {
			if (i%2) {
				this.ctx.fillStyle = "rgba(255, 255, 0, 0.2)";
			} else {
				this.ctx.fillStyle = "rgba(0, 255, 0, 0.2)";
			}
			
			this.ctx.fillRect(this.Xmin + this.parent.header_width + this.parent.border_skip + this.parent.tau_offset + i*this.parent.sym_width, 
							  this.Ymin - this.parent.border_skip, 
					          this.parent.sym_width, 
					          this.header_height + 2*this.parent.border_skip);
		}
		
		// draw border all-around chips
		this.ctx.strokeRect(this.Xmin + this.parent.header_width + this.parent.tau_offset, 
							this.Ymin - this.parent.border_skip, 
							this.packet.symbols.length * this.parent.sym_width + 2*this.parent.border_skip + (this.parent.bit_width + this.parent.bit_xskip)/2, 
							this.header_height + 2*this.parent.border_skip);
		
		this.ctx.restore();
	};
	
	/*********************/
	this.mouseDown = function (ev) {
	    var x = ev.pageX - $(UI.canvas).offset().left;
	    var y = ev.pageY - $(UI.canvas).offset().top;
	   
	    chips = null;
	    
	    if (y > this.Ymin && y < this.Ymin + this.parent.bit_height) {
	    	chips = this.packet.chips_i;
	    	curr_x = this.Xmin + this.parent.tau_offset + this.parent.header_width + this.parent.border_skip;
	    }
	    
	    if (y > this.Ymin + this.parent.bit_height + this.parent.bit_xskip && y < this.Ymin + 2*this.parent.bit_height + this.parent.bit_xskip) {
	    	chips = this.packet.chips_q;
	    	curr_x = this.Xmin + this.parent.tau_offset + this.parent.border_skip + this.parent.header_width + (this.parent.bit_width + this.parent.bit_xskip)/2;
	    }
	    
	    if (!chips) {
	    	return false;
	    } else {
	    	for (var i=0; i<chips.length; i++) {
	    		if (x > curr_x && x < curr_x + this.parent.bit_width) {
	    			if (chips[i] == -1) {
	    				chips[i] = 1;
	    			} else {
	    				chips[i] = -1;
	    			}
	    			
	    			this.packet.set_chips_iq(this.packet.chips_i, this.packet.chips_q);
	    			
	    			return true;
	    		}
	    		
	    		curr_x += this.parent.bit_width + this.parent.bit_xskip;
				if (i != 0 && !((i+1)%this.parent.sym_length)) {
					curr_x += this.parent.sym_xskip;
				}
	    	}
	    }
	    
	    return false;
	};
};

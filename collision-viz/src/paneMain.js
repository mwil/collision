function PaneMain (parent, Xmin, Ymin, width, height) {
	this.UI = parent;
	this.ctx = parent.context;
	
	this.Xmin = Xmin;
	this.Ymin = Ymin;
	this.width = width;
	this.height = height;
	
	this.sync_xmin = 50;
	this.sync_ymin = 25;
	
	this.usync_xmin = 50;
	this.usync_ymin = 150;
	
	this.recv_xmin = 50;
	this.recv_ymin = 275;
	
	this.pSync  = new pPacket(this.UI, this.UI.packets["SYNC"], "sync", this.sync_xmin, this.sync_ymin, movable=false, readonly=false)
	this.pUSync = new pPacket(this.UI, this.UI.packets["USYNC"], "usync", this.usync_xmin, this.usync_ymin, movable=true, readonly=false)
	this.pRecv  = new pPacket(this.UI, this.UI.packets["RECV"], "recv", this.recv_xmin, this.recv_ymin, movable=false, readonly=true)
	
	/*********************/
	this.update = function () {
		this.ctx.clearRect(this.Xmin, this.Ymin, this.width, this.height);
		
		this.pSync.draw();
		this.pUSync.draw();
		this.pRecv.draw();
	};
	
	/*********************/
	this.mouseDown = function (ev) {
		result = false;
		
		result = this.pSync.mouseDown(ev);
		result |= this.pUSync.mouseDown(ev);
	    
	    return result;
	};
};

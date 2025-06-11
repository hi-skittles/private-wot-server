/*

    Interpreter: Turbogears Python Interactive Interpreter
    Based heavily on the Javascript Interactive Interpreter MochiKit Demo

*/

function console_input_toggle() {
	var cb = getElement("isMultiline");

	var elem1 = getElement("console_input_line");
	var elem2 = getElement("console_input_block");

	if (!cb.checked) {
		elem1.style.visibility = "visible";
		elem1.style.display = "block";
		elem2.style.visibility = "hidden";
		elem2.style.display = "none";
	    updateNodeAttributes("exec", {
    		"onclick": interpreterManager.submit
    	});
	} else {
		elem1.style.visibility = "hidden";
		elem1.style.display = "none";
		elem2.style.visibility = "visible";
		elem2.style.display = "block";
	    updateNodeAttributes("exec", {
    		"onclick": interpreterManager.multilineSubmit
    	});
	}

	// Adjust the console area
	interpreterManager.fill();
};

InterpreterManager = function () {
    bindMethods(this);
};

InterpreterManager.prototype.initialize = function () {
    updateNodeAttributes("interpreter_text", {
        "onkeyup": this.keyUp
    });
    updateNodeAttributes("interpreter_block_text", {
        "onkeydown": this.keySubmit
    });
    updateNodeAttributes("interpreter_form", {
        "onsubmit": this.submit
    });
    updateNodeAttributes("exec", {
    	"onclick": this.submit
    });
    this.lines = [];
    this.history = [];
    this.currentHistory = "";
    this.historyPos = -1;

	var cb = getElement("isMultiline");
	cb.checked = false;

	this.frame = getElement( "interpreter_area" );

	// Resize the output pane to fill the predefined dimensions, or the entire
	// window in any unspecified direction
	this.fill = function()
	{
		var opos = elementPosition( this.frame );
		var odim = elementDimensions( this.frame );
		var wdim = getViewportDimensions();

		var ci = getElement("console_input");
		var cidim = elementDimensions( ci );

		odim.w = wdim.w - opos.x - 40;
		odim.h = wdim.h - opos.y - cidim.h - 40;
		setElementDimensions( this.frame, odim );
	}

	window.addEventListener( "resize",
							 function(){ interpreterManager.fill(); },
							 false );

	this.fill();
	
	// Add userChanged listener
	jQuery( BW ).on( 'userChanged', this.revertToListPage );
};

InterpreterManager.prototype.revertToListPage = function (e, newUser) {
	// Redirect to consoles list as new user
	window.location = 'consoles?user=' + newUser;
}

InterpreterManager.prototype.banner = function (str) {
    appendChildNodes("interpreter_output",
        SPAN({"class": "console_banner"},
            str),
        BR()
    );
};

InterpreterManager.prototype.submit = function () {
    this.doSubmit();
    this.doScroll();
    return false;
};

InterpreterManager.prototype.multilineSubmit = function () {
	this.doMultilineSubmit();
	this.doScroll();
	return false;
};

InterpreterManager.prototype.doScroll = function () {
    var p = getElement("interpreter_output").lastChild;
    if (typeof(p) == "undefined" || p == null) {
        return;
    }
    var area = getElement("interpreter_area");
    if (area.offsetHeight > area.scrollHeight) {
        area.scrollTop = 0;
    } else {
        area.scrollTop = area.scrollHeight;
    }
};

InterpreterManager.prototype.moveHistory = function (dir) {
    // totally bogus value
    if (dir == 0 || this.history.length == 0) {
        return;
    }
    var elem = getElement("interpreter_text");
    if (this.historyPos == -1) {
        this.currentHistory = elem.value;
        if (dir > 0) {
            return;
        }
        this.historyPos = this.history.length - 1;
        elem.value = this.history[this.historyPos];
        return;
    }
    if (this.historyPos == 0 && dir < 0) {
        return;
    }
    if (this.historyPos == this.history.length - 1 && dir > 0) {
        this.historyPos = -1;
        elem.value = this.currentHistory;
        return;
    }
    this.historyPos += dir;
    elem.value = this.history[this.historyPos];
};

InterpreterManager.prototype.keySubmit = function (e) {
    e = e || window.event;
    if(e.keyCode == 13 && e.ctrlKey == true) {
      this.doMultilineSubmit();
	    this.doScroll();
      return false;
    }
    return true;
};

InterpreterManager.prototype.keyUp = function (e) {
    e = e || window.event;
    switch (e.keyCode) {
        case 38: this.moveHistory(-1); break;
        case 40: this.moveHistory(1); break;
        default: return true;
    }
    e.cancelBubble = true;
    return false;
};

InterpreterManager.prototype.doSubmit = function () {
    var elem = getElement("interpreter_text");
    var code = elem.value;
    elem.value = "";

    elem = getElement("component_host");
	var host = elem.value;

    elem = getElement("component_port");
	var port = elem.value;

    this.history.push(code);
    this.historyPos = -1;
    this.currentHistory = "";

    var d = loadJSONDoc("process_request?line="+encodeURIComponent(code) + "&host="+encodeURIComponent(host) + "&port="+encodeURIComponent(port));
    d.addCallback(this.showResult);

    return;
};

InterpreterManager.prototype.doMultilineSubmit = function () {
	var elem = getElement("interpreter_block_text");
    var code = elem.value;

    elem = getElement("component_host");
	var host = elem.value;

    elem = getElement("component_port");
	var port = elem.value;

    lines = code.split("\n");
    for ( var i = 0; i < lines.length; i++ ) {
        this.history.push(lines[i]);
    }

    this.historyPos = -1;
    this.currentHistory = "";

    var d = loadJSONDoc( "process_multiline_request?block="+encodeURIComponent(code) + "&host="+encodeURIComponent(host) + "&port="+encodeURIComponent(port));
    d.addCallback(this.showResult);

    return;
}

InterpreterManager.prototype.showResult = function (res) {
    var lines = res["output"].split("\n");
	for ( var i = 0; i < lines.length; i++ ) {
		var lineclass = "console_data";

		// highlight input code.
		// assumption: only input code starts with ">>> " or "... "
		var lineprefix = lines[i].substr(0,4);
		if ( lineprefix == ">>> " || lineprefix == "... " ) {
			lineclass = "console_code";
		}

		appendChildNodes("interpreter_output",
			SPAN({"class": lineclass}, lines[i]), BR()
		);
	}

	this.doScroll();
	$("prompt").innerHTML = res["more"] ? "... " : ">>> ";
};

interpreterManager = new InterpreterManager();
addLoadEvent(interpreterManager.initialize);

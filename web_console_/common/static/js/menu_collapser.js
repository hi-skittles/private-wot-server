MenuCollapser = function ()
{
	bindMethods( this );
	this.__init__();
};


MenuCollapser.prototype.__init__ = function ()
{
	
	this.collapserDiv = MochiKit.DOM.getElement( "menu_collapser" );
	this.navigationMenu = MochiKit.DOM.getElement( "navigation" );

	this.isCollapsed = false;

	this.collapseImg = IMG( {'src':'/static/images/collapse_menu_normal.png',
						'align':'left', 'valign':'top',
						'onclick': this.toggleVisibility } );

	this.expandImg = IMG( {'src':'/static/images/expand_menu_normal.png',
						'align':'left', 'valign':'top',
						'onclick': this.toggleVisibility } );

	this.collapseHoverImg = IMG( {'src':'/static/images/collapse_menu_hover.png',
						'align':'left', 'valign':'top',
						'onclick': this.toggleVisibility } );

	this.expandHoverImg = IMG( {'src':'/static/images/expand_menu_hover.png',
						'align':'left', 'valign':'top',
						'onclick': this.toggleVisibility } );

	MochiKit.DOM.replaceChildNodes( this.collapserDiv, this.collapseImg );

	MochiKit.Signal.connect( this.collapserDiv, "onmouseover",
		partial( this.toggleMouseOver, true ) );
	MochiKit.Signal.connect( this.collapserDiv, "onmouseout",
		partial( this.toggleMouseOver, false ) );
};


MenuCollapser.prototype.toggleMouseOver = function ( isOver )
{

	if (!this.isCollapsed)
	{
		if (isOver)
		{
			MochiKit.DOM.replaceChildNodes( this.collapserDiv, this.collapseHoverImg );
		}
		else
		{
			MochiKit.DOM.replaceChildNodes( this.collapserDiv, this.collapseImg );
		}
	}
	else
	{
		if (isOver)
		{
			MochiKit.DOM.replaceChildNodes( this.collapserDiv, this.expandHoverImg );
		}
		else
		{
			MochiKit.DOM.replaceChildNodes( this.collapserDiv, this.expandImg );
		}
	}
};


MenuCollapser.prototype.toggleVisibility = function ()
{

	if (this.isCollapsed)
	{
		// Expand
		MochiKit.DOM.replaceChildNodes( this.collapserDiv, this.collapseHoverImg );
		this.navigationMenu.style.visibility = "visible";
		this.navigationMenu.style.display = "block";
	}
	else
	{
		// Collapse
		MochiKit.DOM.replaceChildNodes( this.collapserDiv, this.expandHoverImg );
		this.navigationMenu.style.visibility = "hidden";
		this.navigationMenu.style.display = "none";
	}

	// Post a fake resize event.
	var fakeEvent = {};
	signal( window, "onresize", fakeEvent );

	this.isCollapsed = !this.isCollapsed;
};


function onMenuLoad()
{
	var collapser = new MenuCollapser();
}

addLoadEvent( onMenuLoad );

// menu_collapser.js

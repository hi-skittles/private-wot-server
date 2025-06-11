"use strict";

// namespace
var SV = {};

SV.debug = 0;
SV.debugDrawing = 0;
SV.debugTooltip = 0;

// Class/static data

/** magnitude of zoom for zoom in/out. */
SV.ZOOM_FACTOR = 2.0;

/** Min world distance that can be shown in canvas x dimension,
*   effectively max viewport zoom (worldspace, metres). */
SV.MIN_PAGE_SIZE = 3;

/** Max world distance that can be shown in canvas x dimension,
*   effectively min viewport zoom (worldspace, metres). */
SV.MAX_PAGE_SIZE = 50000;

/** Data model poll interval (msec). */
SV.POLL_INTERVAL = 1000;

/** The background image file name, used when tileset is not available. */
SV.BG_IMAGE_FILE_NAME = "map.jpg";

/** Colour offset for calculating entity type colours */
SV.STARTING_ENTITY_HUE = 0;

SV.BASEURL_ENTITY_ICONS = 'resources/scripts/server_data/space_viewer_images';

/** Draw throttle -- min time that must pass before redrawing the scene.
*   Used to prevent unnecessary redraws when many events are happening at once. */
SV.MIN_DRAW_INTERVAL = 16.67; // msec frame time (1000msec / 60fps)


/**
*	UI canvas style singleton. Most keys correspond to canvas styles,
*	others refer to things like margins & positioning that are used within
*	their respective draw* methods.
*
*	All numerical values in px unless noted.
*/
var UI =
{
	// msec/frame meter
	fps:
	{
		enabled: false,
	},

	// space image and BG colour, plus tinting of space image
	spaceBackgroundImage:
	{
		enabled: true,
		fillStyle: '#fff',	 // colour to tint bg image with, or use when not present
		imageAlpha: 0.7,	// 0 means zero image, 1.0 means zero fill colour.
		strokeStyle: '#111', // only used when no space image present
		lineWidth: 1,
		canvasClearRectIsFaster: (navigator.userAgent.indexOf('Firefox') > 0),
	},

	// general cell label styles
	cellLabel:
	{
		enabled: true,
		font: '14px/16px "Trebuchet MS", "Arial", "sans-serif"',
		lineHeight: 16,		// should match font spec above
		color: '#e0e0e0',	// text colour
		backgroundColor: 'rgba( 40, 40, 40, 0.65 )', // label BG fill colour
		strokeStyle: '#444',
		lineWidth: 1,
		paddingX: 8,		// padding around text; label background size
		paddingY: 5,		// padding around text; label background size
		borderRadius: 8,	// degree of rounding of corners
		textBaseline: "middle",
		textAlign: "center",
		highlight:			// style applied to selected cell label BG
		{
			animStartColour: [ 0, 0, 100, 0.4 ],
			animEndColour: [ 40, 40, 40, 0 ],
			animDuration: 0,
			strokeStyle: '#fff',
			lineWidth: 1,
		},
	},

	// individual text lines of cell label
	cellLabel_cellId: { enabled: true, },
	cellLabel_ipAddress: { enabled: true, },
	cellLabel_load: { enabled: true, },

	// selected cell boundary style
	cellBoundary:
	{
		enabled: true,

		// plain shaded rect
		// fillStyle: 'rgba( 0, 0, 50, 0.2 )',
		strokeStyle: 'rgba( 0, 0, 50, 0.35 )',
		lineWidth: 12, // cell boundary rect thinkness
		offset: 6, // number of pixels inwards from actual cell boundary
	},

	// cell BG load tint
	cellLoad:
	{
		enabled: false,

		// absolute load colouring
		lowestLoad: [ 255, 255, 100, 0.15 ], // array form of rgba for interpolating
		highestLoad: [ 215, 0, 0, 0.35 ],	// array form of rgba for interpolating
		minAbsoluteLoadCutoff: 0.35, // the load at which the lowestLoad colour will be applied

		// relative load colouring
		lowestRelativeLoad: [ 0, 0, 255, 0.25 ], // array form of rgba for interpolating
		highestRelativeLoad: [ 255, 0, 0, 0.25 ], // array form of rgba for interpolating
		minRelativeLoadCutoff: 0.1, // defined min diff from avg load for scaling

		strokeStyle: '#444', // indicator gradient border line
		lineWidth: 1,		// indicator gradient border width

		// indicator stuff
		indicator:
		{
			// positioning
			width: 8,	// horiz width of indicator
			height: 120,	// height of indicator
			left: 8,		// from left edge of canvas
			bottom: 38,  // from bottom edge of canvas

			// label tick lines
			strokeStyle: '#444',// indicator tick lines
			lineWidth: 1,		// indicator tick thinkness
			tickLength: 3,		// distance from label text to tick
			labelMargin: 2,		// distance from label text to tick

			// indicator label text
			textAlign: 'left',
			textBaseline: 'middle',
			font: '11px "Trebuchet MS", Arial, sans-serif',
			fillStyle: 'rgba( 0, 0, 0, 0.8 )', // text colour
			// shadowBlur: 3,
			// shadowColor: '#fff',
		}
	},

	// relative|absolute load mode toggle
	cellLoad_useRelativeLoad: { enabled: true },

	retiringCell: { 
		fillStyle: 'rgba( 199, 43, 7, 0.20)',
	},

	menuIcon: {
		offset: 10, // menu icon offset to cell boundary, in px
	},

	// partition line style only
	partitionLine:
	{
		enabled: true,
		lineWidth: 2,
		strokeStyle: 'rgba( 0, 51, 255, 0.6 )',
		// strokeStyle: 'rgba( 65, 115, 255, 0.8 )',
		shadowColor: '#eee',
		shadowBlur: 2,

		selectDelta: 10, // the delta distance allowed to select, px on canvas
	},
	
	draggablePartitionStyle:
	{
		strokeStyle: 'rgba( 59, 206, 47, 0.6 )',
	},

	draggedPartitionStyle:
	{
		strokeStyle: 'rgba( 59, 206, 47, 0.2 )',
	},

	draggingPartitionStyle:
	{
		strokeStyle: 'rgba( 212, 255, 145, 1 )',
	},

	// general partition label style; disabling disables load & aggr labels too
	partitionLabel:
	{
		enabled: true,
		font: '14px/14px "Trebuchet MS", "Arial", "sans-serif"',
		fillStyle: 'rgba( 0, 51, 255, 0.9 )', // text colour
		shadowColor: '#fff',
		shadowBlur: 6,
		textAlign: "center",
		textBaseline: "middle",
		margin: 8,		// gap between label and line
		paddingX: 10,	// left/right padding around text; label BG
		paddingY: 10,	// top/bottom padding around text; label BG
	},

	// text label only
	partitionLabel_load: { enabled: false },
	partitionLabel_aggression: { enabled: false },
	
	// partition menu settings
	popupMenu:
	{
		fadeInDuration: 0, // cell menu fade in time
		fadeOutDuration: 250, // cell menu fade out time
		fadeOutDelay: 0, // Delay before a cell menu begins fading out
		maxTotalDuration: 8000, // Max time a cell menu can stay shown
	},

	// real entities / general entity settings
	entity:
	{
		enabled: true,
		strokeStyle: 'rgba( 0, 0, 0, 0.9 )',	// default line colour
		lineWidth: 1,	// circle border thinkness
		radius: 2.5,		// adjusts size of entity when drawn as a circle
		radiusMultipleWhenHighlighted: 1.0, // relative addition to size when highlighted
		highlightRadius: 0,		// adjusts size of entity when drawn as a circle
		excluded: {},	// map of entityTypeId -> boolean. true means 'don't draw'.
		highlighted: {}, // map of entityTypeId -> boolean

		// note: entity colours initialised from entity type IDs
		colours: [ 'rgba( 10, 90, 255, 0.9 )' ], // <- minimal default
		saturation: '100%', // see _generateEntityColours
		brightness: '60%',	// see _generateEntityColours
	},

	// ghost-specific settings
	ghostEntity:
	{
		enabled: true,
		strokeStyle: 'rgba( 47, 47, 47, 0.75 )', // border
		fillStyle: 'rgba( 255, 255, 255, 0.6 )', // default only; overridden by entity type colour
		lineWidth: 1, // border

		// note: ghost colours initialised from entity type IDs
		colours: [ 'rgba( 10, 90, 255, 0.35 )' ], // <- minimal default
		saturation: '40%', // see _generateEntityColours
		brightness: '55%', // see _generateEntityColours
	},

	entityIcons:
	{
		enabled: true,
		images: {}, // map of entityTypeID -> Image
		radiusInflation: 10, // # pixels to add to icon size vs as circles
		ghostAlpha: 0.6,	// alpha at which to draw ghosts
	},

	entityTooltip:
	{
		enabled: true,
		showColour: false, // include colour of entity type in tooltip?
		hoverDuration: 100, // #msec mouse must be stationary before testing for entity tooltip
		fadeInDuration: 0, // Tooltip fade in time
		fadeOutDuration: 250, // Tooltip fade out time
		fadeOutDelay: 0, // Delay before a tooltip begins fading out
		maxTotalDuration: 8000, // Max time a tooltip can stay shown
	},

	/** Zero duration means no animation. */
	animation:
	{
		enabled: true,

		/** Zoom in/out */
		zoom:
		{
			enabled: true,
			duration: 250, // msec
		},

		pan:
		{
			enabled: true,
			duration: 250, // msec
		},

		/** zoomToSpace* operations. */
		zoomToRect:
		{
			enabled: true,
			duration: 400, // msec
		},

		setSelectedCell:
		{
			enabled: true,
			duration: 500, // msec
		}
	},

	interpolation:
	{
		enabled: true,
		delay: 500, // msec a data frame will be delayed for interpolation smoothing
		targetFps: 15,
		partitionSpeedup: 3, // move partitions X times faster (>= 1.0)
	},

	scaleIndicator:
	{
		enabled: true,
		strokeStyle: 'rgba( 0, 0, 0, 0.7 )',
		lineWidth: 2,
		shadowBlur: 3,
		shadowColor: "#fff",
		left: 10,		// distance from left of map
		bottom: 10,		// distance from bottom of map
		maxWidth: 210,	// max width of horiz line
		height: 6,		// height of vertical ticks on line
	},

	scaleIndicatorLabel:
	{
		enabled: true,
		fillStyle: 'rgba( 0, 0, 0, 0.8 )', // text colour
		font: '12px/12px "Trebuchet MS", Arial, sans-serif',
		shadowColor: '#fff',
		shadowBlur: 4,
		textBaseline: "middle",
		textAlign: 'left',	// relative label text pos
		offsetX: 6,			// distance from scale line
		offsetY: 2,			// distance from scale line
	},

	chunkBounds:
	{
		enabled: false,
		lineWidth: 1,
		strokeStyle: 'rgba( 0, 255, 0, 0.8 )',
		shadowColor: '#fff',
		shadowBlur: 0,
	},

	entityBounds:
	{
		enabled: false,
		lineWidth: 1, // 2
		fillStyle: 'rgba( 80, 0, 40, 0.075 )',
		strokeStyle: 'rgba( 80, 0, 40, 0.4 )',
		shadowColor: '#fff',
		shadowBlur: 0,
	},
};

/** Default options for a SV.SpaceViewSurface instance. */
SV.OPTIONS = {

	// identifies the <canvas/> to draw on, jquery selector syntax
	div: "#space_viewer",

	// image object to use as space background.
	// null means derive image name from space mapping
	backgroundImage: null,

	// map of: int entityTypeId -> String entityTypeName.
	// null means get from server
	entityTypes: null,

	// init default keyboard events?
	keyboardEvents: true,

	// init default mouse events?
	mouseEvents: true,

	// init default touch events?
	touchEvents: true,

	// init animation internals?
	// note: false also implies that returned instance will also not
	// be zoomed or panned.
	animation: true,

	// list of functions that will be called at the end of construction
	postInitHooks: [],
};


/** Constructor */
SV.SpaceViewSurface = function( /*int*/ spaceId, /*Map*/ options )
{
	// permit no argument construction for derived sub-classes
	if (!spaceId)
	{
		return;
	}

	// merge user opts with defaults. Note: deep copy.
	options = jQuery.extend( true, {}, SV.OPTIONS, options );
	if (SV.debug)
	{
		console.log( "creating new SpaceViewSurface: spaceId="
				   + spaceId
				   + ", container='"
				   + options.div
				   + "', options: " );
		console.dir( options );
		this._timestampCreated = +new Date;
	}
	if (SV.debug > 1)
	{
		var strings = [];
		for (var k in options)
		{
			strings.push( " " + k + "=" + options[k] );
		}
		console.log( "options: %s", strings.toString() );
	}

	this.spaceId = spaceId;

	this.entityTypes = options.entityTypes;
	if (!this.entityTypes)
		this.requestEntityTypes();

	var canvas = this.canvas = this._findOrCreateCanvas( options.div );
	this.context = canvas.getContext( "2d" );

	// server is in production mode or not
	this.isProductionMode = true;

	// this is corresponding to the watcher debugging/shouldLoadBalance,
	// it controls whether the cell boundary could change during the backend
	// automatic load balance
	this.svrLoadBalanceEnabled = true;

	// this is corresponding to the watcher debugging/shouldMetaLoadBalance,
	// it controls whether one cell could be created or retired during the 
	// backend automatic load balance 
	this.metaLoadBalanceEnabled = true;

	// this controls whether user can do manual load balance on UI
	this.manualLoadBalanceEnabled = false;

	// whether there is available cellapp for adding new cell to current space
	this.notEnoughCellApps = true;

	// init load balance status
	this._initLoadBalanceStatus();

	this.greenArrowImgH = new Image();
	this.greenArrowImgH.src = "static/images/green_arrows_h.png";

	this.greenArrowImgV = new Image();
	this.greenArrowImgV.src = "static/images/green_arrows_v.png";

	this.menuIconImg = new Image();
	this.menuIconImg.src = "static/images/menu_icon.png";

	// used when mouse is over the menu icon area
	this.menuIconClickableImg = new Image();
	this.menuIconClickableImg.src = "static/images/menu_icon_clickable.png";

	// space background image
	this.backgroundImage = options.backgroundImage || new Image();

	// data map
	this.data = undefined;
	
	// worldspace distance displayed by the canvas in the x-dimension.
	// xPageSize:canvas.width ratio = current display scale.
	this.xPageSize = 800;

	// worldspace point corresponding to top-left canvas point.
	this.xPosition = - this.xPageSize / 2;
	this.yPosition = this.xPageSize / 2;

	// drag progress/state
	this.dragState = null;

	// model polling state
	this._timer = null;

	// init dom elements
	var dom = {};
	dom.canvas = jQuery( canvas );
	dom.container = jQuery( canvas.parentNode );
	dom.title = jQuery( ".sv-space-title", dom.container );
	dom.header = jQuery( ".sv-header", dom.container );
	dom.bounds = jQuery( ".sv-bounds", dom.container );
	dom.coords = jQuery( ".sv-coords", dom.container );
	dom.coordsX = jQuery( ".x_pos", dom.container );
	dom.coordsY = jQuery( ".y_pos", dom.container );
	dom.cellStats = jQuery( ".sv-cell-stats", dom.container );
	dom.entityStats = jQuery( ".sv-entity-stats", dom.container );

	dom.popupMenu = jQuery( ".sv-popup-menu", dom.container );
	dom.popupMenuTitle = jQuery( ".popup-menu-title", dom.popupMenu );
	dom.popupMenuList = jQuery( ".sv-popup-menu-list", dom.popupMenu );
	dom.retireLink =  jQuery( ".retire-cell", dom.popupMenu );
	dom.cancelRetireLink =  jQuery( ".cancel-retire", dom.popupMenu );
	dom.splitLink =  jQuery( ".split-cell", dom.popupMenu );

	this.dom = dom;

	//	init starting state of bounds/coords divs
	dom.bounds.css( 'display', 'block' );
	dom.coords.hide();

	// init mouse position on canvas
	this.mousePos = { x: -1, y: -1 };

	//	init events
	this.backgroundImage.onload = function()
	{
		if (SV.debug)
		{
			console.log(
				"background image '%s' loaded in %.1f msec",
				this.backgroundImage.src,
				+new Date - this._timestampCreated
			);
		}

		this.draw();
		jQuery( this ).triggerHandler( "ready.sv" );
	}.bind( this );

	jQuery( this ).on( 'viewportChange.sv', this._updateBoundsUI.bind( this ) );

	jQuery( window ).on( 'unload', function() {
		if (this._xhr)
		{
			this._xhr.abort();
			this._xhr = null;
		}
	});

	if (options.mouseEvents)
	{
		this.initMouseEvents();
	}
	if (options.keyboardEvents)
	{
		this.initKeyboardEvents();
	}
	if (options.touchEvents)
	{
		this.initTouchEvents();
	}
	if (options.animation)
	{
		this.initAnimation();
	}

	this.rescaleWindow();

	for (var i in options.postInitHooks)
	{
		options.postInitHooks[ i ].call( this );
	}
};


// Object def
SV.SpaceViewSurface.prototype =
{
	_findOrCreateCanvas: function( expression )
	{
		if (!expression) throw new Error( 'No expression given' );

		// if a string, it's a jquery selector expression, else assume it's a
		// jquery object wrapper around a canvas
		var canvas;

		if (typeof expression === 'string')
		{
			canvas = jQuery( expression );
			if (!canvas.is('canvas'))
			{
				throw new Error(
					"expression '" + expression + "' does not identify a canvas" );
			}

			return canvas.get( 0 );
		}

		if (expression.is && expression.is('canvas'))
		{
			return expression.get( 0 );
		}

		canvas = expression.find( 'canvas' ).get( 0 );
		if (!canvas)
		{
			throw new Error(
				"jQuery object does not contain a HTML canvas element" );
		}

		return canvas;
	},


	initKeyboardEvents: function()
	{
		var _this = this;

		jQuery( document ).on({
			keyup: function( ev )
			{
				// _this._pressed is a firefox workaround;
				// see keypress event below
				if (ev.which == 0 && _this._pressed)
				{
					ev.which = _this._pressed;
					delete _this._pressed;
				}

				// don't do anything if CTRL or ALT depressed
				if (ev.ctrlKey || ev.metaKey)
				{
					return;
				}

				switch (ev.which)
				{
					case 32: // ' '
						_this.zoomToSpaceBounds();
						break;

					case 37: // right arrow
						_this.pan( -_this.xPageSize / 4, 0, true );
						break;

					case 38: // up arrow
						_this.pan( 0, _this.xPageSize / 4, true );
						break;

					case 39: // left arrow
						_this.pan( _this.xPageSize / 4, 0, true );
						break;

					case 40: // down arrow
						_this.pan( 0, -_this.xPageSize / 4, true );
						break;

					case 66: // 'b'
						UI.entityBounds.enabled = !UI.entityBounds.enabled;
						jQuery( _this ).triggerHandler( "configChanged.sv" );
						_this.draw();
						break;

					case 67: // 'c'
						UI.cellLabel.enabled = !UI.cellLabel.enabled;
						jQuery( _this ).triggerHandler( "configChanged.sv" );
						_this.draw();
						break;

					case 69: // 'e'
						UI.entity.enabled = !UI.entity.enabled;
						jQuery( _this ).triggerHandler( "configChanged.sv" );
						_this.draw();
						break;

					case 71: // 'g'
						UI.ghostEntity.enabled = !UI.ghostEntity.enabled;
						jQuery( _this ).triggerHandler( "configChanged.sv" );
						_this.draw();
						break;

					case 73: // 'i'
						UI.entityIcons.enabled = !UI.entityIcons.enabled;
						jQuery( _this ).triggerHandler( "configChanged.sv" );
						_this.draw();
						break;

					case 75: // 'k'
						UI.chunkBounds.enabled = !UI.chunkBounds.enabled;
						jQuery( _this ).triggerHandler( "configChanged.sv" );
						_this.draw();
						break;

					case 76: // 'l'
						// flip load on/off *unless* load is on and we are
						// toggling between absolute/relative load
						if (! (UI.cellLoad.enabled &&
							UI.cellLoad_useRelativeLoad.enabled == ev.shiftKey))
						{
							UI.cellLoad.enabled = !UI.cellLoad.enabled;
						}
						UI.cellLoad_useRelativeLoad.enabled = !ev.shiftKey;
						jQuery( _this ).triggerHandler( "configChanged.sv" );
						_this.draw();
						break;

					case 80: // 'p'
						UI.partitionLine.enabled = !UI.partitionLine.enabled;
						jQuery( _this ).triggerHandler( "configChanged.sv" );
						_this.draw();
						break;

					case 86: // 'v'
						_this.zoomToSpaceView();
						break;

					case 33:  // PgUp
					case 61:  // '='/'+' on firefox
					case 107: // Keypad '+'
					case 187: // '='/'+'
						_this.zoomIn();
						break;

					case 34:  // PgDown
					case 109: // '-' on firefox
					case 173: // '-' on firefox 23 (note: this is prob a FF bug)
					case 189: // '-'
						_this.zoomOut();
						break;

					case 188: // ','/'<'
						if (ev.shiftKey)
						{
							_this.selectPrevCell();
							_this.zoomToCell();
						}
						else
						{
							_this.selectPrevCell( true );
							_this.draw();
						}
						break;

					case 190: // '.'/'>'
						if (ev.shiftKey)
						{
							_this.selectNextCell();
							_this.zoomToCell();
						}
						else
						{
							_this.selectNextCell( true );
							_this.draw();
						}
						break;

					case 191: // '/'
						if (ev.shiftKey)
						{
							_this.zoomToEntityBounds();
						}
						else if (_this.cells.length > 1)
						{
							_this.zoomToCell();
						}
						else
						{
							_this.zoomToSpaceBounds();
						}
						break;

					default: return;
				};

				ev.stopImmediatePropagation();
				ev.preventDefault();
				return false;
			},

			// workaround specifically for firefox, which doesn't set
			// a value to ev.which in the keyup event for shift key +
			// {comma, full-stop, forward-slash}. keypress always occurs
			// before keyup.
			keypress: function( ev )
			{
				// don't do anything if CTRL or ALT depressed
				if (ev.ctrlKey || ev.metaKey)
				{
					return;
				}

				switch (ev.which)
				{
					case 60: // shift + ','/'<'
						_this._pressed = 188;
						break;

					case 62: // shift + '.'/'>'
						_this._pressed = 190;
						break;

					case 63: // shift + '/'
						_this._pressed = 191;
						break;

					default: return;
				};

				ev.preventDefault();
				return false;
			},

		}); // end jQuery.on()
	},


	initMouseEvents: function()
	{
		var _this = this;

		jQuery( this.canvas ).on({

			mousemove: function( ev )
			{
				_this._onMouseMove( ev );
				return false;
			},

			mouseover: function()
			{
				if (!_this._areCoordsAnimating)
				{
					_this._areCoordsAnimating = true;
					_this.dom.bounds.fadeOut( 100, function() {
						_this.dom.coords.fadeIn( 100 );
						_this._areCoordsAnimating = false;
					});
				}
				return false;
			},

			mouseout: function( ev )
			{
				// set mouse position value
				_this.mousePos.x = -1;
				_this.mousePos.y = -1;

				// don't do anything if the element we're mousing out to
				// has CSS class 'sv-event-ignore'.
				if (jQuery( ev.relatedTarget ).hasClass('sv-event-ignore'))
				{
					ev.stopImmediatePropagation();
					return false;
				}

				if (!_this._areCoordsAnimating)
				{
					_this.dom.coords.fadeOut( 100, function() {
						_this.dom.bounds.fadeIn( 100 );
						_this._areCoordsAnimating = false;
					});
				}

				// prevent "sticky" mouse drag
				_this.dragState = null;
				_this.dragPartition = null;

				if (_this.tooltipState)
				{
					_this.hideTooltip();
				}

				return false;
			},

			mousedown: function( ev )
			{
				// for left side
				if (ev.which == 1)
				{
					_this._onMouseDown( ev );
				}
				return false;
			},

			mouseup: function( ev )
			{
				// for left side
				if (ev.which == 1)
				{
					_this._onMouseUp( ev );
				}
				
				return false;
			},

			contextmenu: function( ev )
			{	
				// for right click				
				_this.onRightClick( ev );
			},

			dblclick:  function( ev )
			{
				_this._deriveCanvasCoords( ev );
				_this.zoom( ev.canvasX, ev.canvasY, SV.ZOOM_FACTOR, true );
				return false;
			},

			mousewheel: function( ev, delta, deltaX, deltaY )
			{
				_this._deriveCanvasCoords( ev );

				// ignore horizontal delta
				_this.zoom( ev.canvasX, ev.canvasY, Math.pow( 1.1, deltaY ), false );
				return false;
			}
		});
	},


	initTouchEvents: function()
	{
		if (!this.dom.canvas.hammer)
		{
			new Alert.Warning(
				"Touch support library not loaded, so touch support disabled" );

			return;
		}

		// prevent UA from default action of moving all body content on touchmove
		jQuery( document ).on( 'touchmove', function( ev )
		{
			if (!jQuery( ev.target ).parents().hasClass( 'touch-moveable' ))
			{
				 ev.preventDefault();
			}
		});

		var c = this.dom.canvas.hammer( { swipe_max_touches: 3 } );
		var _this = this;
		c.on({
			touch: function( ev )
			{
				var g = ev.gesture;
				// new Alert( "touch" + g.touches.length, { duration: 500 } );
				if (g.touches.length > 1) return;

				_this._onMouseDown( g.center );
			},

			release: function( ev )
			{
				var g = ev.gesture;
				if (g.touches.length > 1) return;

				// new Alert( "release", { duration: 500 } );
				_this._onMouseUp( g.center );
			},

			doubletap: function( ev )
			{
				var g = ev.gesture;
				var tap = g.center;
				_this._deriveCanvasCoords( tap );

				var mag = (g.touches.length > 1) ?
					(1 / SV.ZOOM_FACTOR) : SV.ZOOM_FACTOR;

				// new Alert( "doubletap", { duration: 500 } );
				_this.zoom( tap.canvasX, tap.canvasY, mag, true );
			},

			drag: function( ev )
			{
				var g = ev.gesture;
				// new Alert( "drag" + g.touches.length, { duration: 500 } );
				if (g.touches.length > 1) return;

				var centre = g.center;
				_this._deriveCanvasCoords( centre );

				if (_this.dragState)
				{
					_this.dragTo( centre.canvasX, centre.canvasY );
				}
			},

			pinch: function( ev )
			{
				if (ev.gesture.touches.length != 2) return;

				ev.preventDefault();
				ev.gesture.stopPropagation();
				_this.dragState = null;

				// geometric centre of all touches
				var centre = ev.gesture.center;
				_this._deriveCanvasCoords( centre );

				// new Alert( "pinch", { duration: 500 } );
				_this.zoom( centre.canvasX, centre.canvasY, ev.gesture.scale, false );
				return false;
			},

			swipeleft: function( ev )
			{
				// new Alert( "swipeleft#" + ev.gesture.touches.length, { duration: 200 } );
				if (ev.gesture.touches.length >= 2)
				{
					var url = document.location.href;

					url = url.replace( /spaceId=(\d+)/,
						function( /*String*/ match, /*String*/ spaceId ) {
							return "spaceId=" + (parseInt( spaceId ) + 1); } );

					// new Alert( "swipeleft: " + url, { duration: 500 } );
					document.location.href = url;
				}
			},

			swiperight: function( ev )
			{
				// new Alert( "swiperight#" + ev.gesture.touches.length, { duration: 200 } );
				if (ev.gesture.touches.length >= 2)
				{
					var url = document.location.href;

					url = url.replace( /spaceId=(\d+)/,
						function( /*String*/ match, /*String*/ spaceId ) {
							return "spaceId=" + (parseInt( spaceId ) - 1); } );

					// new Alert( "swiperight: " + url, { duration: 500 } );
					document.location.href = url;
				}
			},
		});
	},


	initAnimation: function()
	{
		// used for animation of all viewport-related changes:
		// see zoom(), pan(), zoomToRect()
		this.viewportAnimation = new Animation(
		{
			id: 'viewportAnimation',
			// targetFps: 35,
			transition: Animation.Fx.easeInOut, // Animation.Fx.linear,

			startX: 0,
			startY: 0,
			startZ: 0,

			deltaX: 0,
			deltaY: 0,
			deltaZ: 0,

			renderFrame: function( animation )
			{
				var delta = animation.progressDelta;
				this.xPosition += animation.deltaX * delta;
				this.yPosition += animation.deltaY * delta;
				this.xPageSize += animation.deltaZ * delta;
				this.draw();
				jQuery( this ).triggerHandler( 'viewportChange.sv' );
			}
			.bind( this ),

			finalFrame: function( animation )
			{
				this.xPosition = animation.startX + animation.deltaX;
				this.yPosition = animation.startY + animation.deltaY;
				this.xPageSize = animation.startZ + animation.deltaZ;
				this.draw();
				jQuery( this ).triggerHandler( 'viewportChange.sv' );
				if (SV.debug)
				{
					console.log( "%s: %f fps", animation.id, animation.fps );
				}
			}
			.bind( this ),
		});


		// var originalStroke = selectedCellBound.strokeStyle;

		// used for animating the selection of a cell
		this.selectedCellAnimation = new Animation({
			id: 'selectedCellAnimation',
			duration: UI.cellLabel.highlight.animDuration,
			transition: Animation.Fx.extremeEaseIn,
			// targetFps: 20,

			beforeFirstFrame: function(	 /*Animation*/ a )
			{
				var start = UI.cellLabel.highlight.animStartColour;
				var end = UI.cellLabel.highlight.animEndColour;

				a.colour = start.slice(); // copy
				a.startColour = start;
				a.deltaColour = [
					end[0] - start[0],
					end[1] - start[1],
					end[2] - start[2],
					end[3] - start[3],
				];
			},

			renderFrame: function( /*Animation*/ a )
			{
				var delta = a.progress;
				var c = a.colour;

				c[0] = a.startColour[0] + a.deltaColour[0] * delta;
				c[1] = a.startColour[1] + a.deltaColour[1] * delta;
				c[2] = a.startColour[2] + a.deltaColour[2] * delta;
				c[3] = a.startColour[3] + a.deltaColour[3] * delta;

				var colour = 'rgba(' +
					Math.round( c[0] ) + ',' +
					Math.round( c[1] ) + ',' +
					Math.round( c[2] ) + ',' +
					c[3] + ')';

				// selectedCellBound.strokeStyle = colour;
				UI.cellBoundary.fillStyle = colour;
				// UI.cellLabel.highlight.fillStyle = colour;

				this.draw();
			}
			.bind( this ),

			finalFrame: function( /*Animation*/ a )
			{
				// selectedCellBound.strokeStyle = 'rgba(' + a.endColour.join(',') + ')';
				// selectedCellBound.strokeStyle = originalStroke;
				delete UI.cellBoundary.fillStyle;
				// delete UI.cellLabel.highlight.fillStyle;
				this.draw();

				if (SV.debug)
				{
					console.log( "%s: %f fps", a.id, a.fps );
				}
			}
			.bind( this ),
		});

		// used to animate highlighted entities
		this.entityHighlightAnimation = new Animation({
			id: 'entityHighlightAnimation',
			duration: Infinity,
			targetFps: 10,

			startRadius: UI.entity.radiusMultipleWhenHighlighted,

			renderFrame: function( /*Animation*/ a )
			{
				var period = a.timeElapsed / 100;
				var delta = Math.sin( period ) / 5;
				UI.entity.radiusMultipleWhenHighlighted = a.startRadius + delta;
				this.draw();
			}
			.bind( this ),
		});

		jQuery( this.entityHighlightAnimation ).on( 'stop.animation', function() {
			UI.entity.radiusMultipleWhenHighlighted = this.startRadius;
		});


		// interpolation of partitions/entities
		this.interpol = new Animation({
			id: "dataInterpolation",
			targetFps: UI.interpolation.targetFps,
			duration: Infinity,
			renderFrame: this.draw.bind( this ),
		});
	},


	/**
	*	Begin polling the data model for data. Generates 'connect.model.sv'
	*	event once started.
	*/
	connectModel: function()
	{
		if (!this._timer)
		{
			this.requestModelUpdate();
			this._timer = window.setInterval(
				this.requestModelUpdate.bind( this ),
				SV.POLL_INTERVAL
			);
			if (SV.debug)
			{
				console.log( "Spaceviewer for space "
						   + this.spaceId
						   + " started"
				);
			}
			jQuery( this ).triggerHandler( "connect.model.sv" );
		}

		if (UI.interpolation.enabled && !this._isInterpolating)
		{
			this.startInterpolation();
		}
	},


	/**
	*	Cease polling the data model for data. Generates 'disconnect.model.sv'
	*	event once stopped.
	*/
	disconnectModel: function()
	{
		if (this._timer)
		{
			window.clearTimeout( this._timer );
			this._timer = null;
			if (SV.debug)
			{
				console.log( "Spaceviewer for space "
						   + this.spaceId
						   + " stopped"	 );
			}
			jQuery( this ).triggerHandler( "disconnect.model.sv" );

			if (this._isInterpolating)
			{
				this.stopInterpolation();
			}
		}
	},


	/** Returns true if model is being polled. */
	isModelConnected: function()
	{
		return (this._timer != null);
	},


	/**
	*	Resizes viewport to given dimensions, or to canvas container width/height
	*	if not given, preserving current world view (ie: current view is scaled to
	*	new viewport size).
	*/
	rescaleWindow: function( /*(optional) int*/ width, /*(optional) int*/ height )
	{
		var cnv = this.canvas;

		if (!width)
		{
			width = this.dom.container.width();
		}

		if (!height)
		{
			height = this.dom.container.innerHeight() - this.dom.header.outerHeight();
		}

		if (cnv.width == width && cnv.height == height)
		{
			return;
		}

		if (SV.debug > 1)
		{
			console.log( "window resize: "
					   + cnv.width
					   + "px,"
					   + cnv.height
					   + "px -> "
					   + width
					   + "px,"
					   + height
					   + "px, "
					   + (width / this.xPageSize).toPrecision( 2 )
					   + " pix/m");
		}

		cnv.width = width;
		cnv.height = height;

		this.draw();
	},


	/**
	*	Resizes viewport to given dimensions, or to canvas container width/height
	*	if not given, preserving current world:view ratio (ie: world view is
	*	clipped/expanded to new viewport size).
	*/
	resizeWindow: function( /*(optional) int*/ width, /*(optional) int*/ height )
	{
		var cnv = this.canvas;

		if (!width)
		{
			width = this.dom.container.width();
		}

		if (!height)
		{
			height = this.dom.container.innerHeight() -
				this.dom.header.outerHeight();
		}

		if (cnv.width == width && cnv.height == height)
		{
			return;
		}

		if (SV.debug > 1)
		{
			console.log( "window resize: " + cnv.width + "px," +
					cnv.height + "px -> " + width + "px," + height + "px");
		}

		this.xPageSize *= (width / cnv.width);
		cnv.width = width;
		cnv.height = height;

		this.draw( true );
		jQuery( this ).triggerHandler( 'viewportChange.sv' );
	},


	/**
	*	Generate a series of colours for entities and ghosts based on
	*	known entity types.
	*/
	_generateEntityColours: function( /*Object*/ ui )
	{
		var entityTypes = this.entityTypes;

		var entity = ui.entity;
		var ghostEnt = ui.ghostEntity;

		var entityColours = ui.entity.colours; // Array
		var ghostColours = ui.ghostEntity.colours; // Array

		var hue;
		var startingHue = SV.STARTING_ENTITY_HUE;
		var saturationEntities = ui.entity.saturation;
		var saturationGhosts = ui.ghostEntity.saturation;

		var numColours = Object.keys( entityTypes ).length;

		for (var entityTypeId in entityTypes)
		{
			hue = (startingHue + entityTypeId * 360 / numColours) % 360;

			entity.colours[ entityTypeId ] = "hsl(" + hue.toFixed() + "," +
					entity.saturation + "," +
					entity.brightness + ')';

			ghostEnt.colours[ entityTypeId ] = "hsl(" + hue.toFixed() + "," +
					ghostEnt.saturation + "," +
					ghostEnt.brightness + ')';
		}
	},


	/**
	*	Convert page x/y coordinates from a jQuery event into canvas-relative
	*	coordinates. This func will be called often, so coords are set directly
	*	on passed event object as ev.canvasX, ev.canvasY.
	*/
	_deriveCanvasCoords: function( ev )
	{
		var offset = this.dom.canvas.offset();
		ev.canvasX = ev.pageX - offset.left;
		ev.canvasY = ev.pageY - offset.top;
		// if (SV.debugEvents)
		//	console.log( ev.pageX + "," + ev.pageY + " -> " + ev.canvasX + "," + ev.canvasY );
	},


	/** Set drag-begin state. */
	_onMouseDown: function( ev )
	{
		this._deriveCanvasCoords( ev );
		
		var worldX = this.convertScreenToWorldX( ev.canvasX );
		var worldY = this.convertScreenToWorldY( ev.canvasY );
		
		this.dragState = {
			startPos: { x: ev.canvasX, y: ev.canvasY },
			worldRef: { x: this.xPosition, y: this.yPosition },
			inProgress: false
		};

		if (this.manualLoadBalanceEnabled)
		{
			this._clearOverPartition();

			// we use the dragPartition to identify what kind of dragging is
			// going on. If dragPartition is not null, then user is dragging
			// one partition, otherwise dragging the whole viewport
			var partition = this._partitionAt( worldX, worldY ); 
			if (partition)
			{
				this.dragPartition = {
					partition: partition,
					originalPos: partition.screenPosition, 
					released: false,
				}
				
				this._addOverPartition( partition );	
			}
			else
			{
				this.dragPartition = null;
			}
		}
	},


	_onMouseMove: function( ev )
	{
		this._deriveCanvasCoords( ev );

		this.mousePos.x = ev.canvasX;
		this.mousePos.y = ev.canvasY;

		var worldX = this.convertScreenToWorldX( ev.canvasX, false );
		var worldY = this.convertScreenToWorldY( ev.canvasY, false );

		//	update UI
		this.dom.coordsX.html( worldX.toFixed( 2 ) );
		this.dom.coordsY.html( worldY.toFixed( 2 ) );

		if (this.dragState)
		{
			this.dragTo( ev.canvasX, ev.canvasY );
		}
		else if (this.manualLoadBalanceEnabled)
		{
			if (!this._checkMouseOverCellMenu())
			{
				this._checkOverPartition( ev.canvasX, ev.canvasY );
			}
		}

		//	entity tooltip stuff
		if (!UI.entityTooltip.enabled)
		{
			return;
		}

		// mouse has moved, so clear entity test timer
		if (this._tooltipTimer)
		{
			clearTimeout( this._tooltipTimer );
		}

		// shorten entity position test delay if a tooltip already exists
		var delay = this.tooltipState ? 10 : UI.entityTooltip.hoverDuration;
		var mouseHasMoved = false;

		if (this.tooltipState)
		{
			// tolerate a small amount of mouse movement over an entity
			mouseHasMoved = (
				Math.abs( ev.canvasX - this.tooltipState.startX ) > 5 ||
				Math.abs( ev.canvasY - this.tooltipState.startY ) > 5
			);

			// kill tooltip if mouse moves away from entity
			if (mouseHasMoved)
			{
				if (SV.debugTooltip) console.log("hiding tooltip due to mouse move");
				this.hideTooltip();
			}
		}

		if (mouseHasMoved || !this.tooltipState)
		{
			// install timer to test if we're hovering over an entity

			var entityTooltipTest = function()
			{
				this._tooltipTimer = null;
				if (SV.debugTooltip > 1) console.log("testing for entity");
				var entity = this.entityAt( worldX, worldY, this._getEntitySize() );
				if (entity)
				{
					this.showTooltip( entity );
				}
			};

			this._tooltipTimer = setTimeout(
				entityTooltipTest.bind( this ), delay );
		}
	},
	
	onRightClick: function( /*MouseEvent*/ ev )
	{
		if (!this.manualLoadBalanceEnabled)
		{
			return;
		}
		
		ev.preventDefault();
		
		this._deriveCanvasCoords( ev );	
		
		var cell = this.cellAt( this.convertScreenToWorldX( ev.canvasX ),
								this.convertScreenToWorldY( ev.canvasY ) );

		this.selectCell( cell );
		this.showMenu( ev.canvasX, ev.canvasY, cell );
	},
	
	showMenu: function( /*int*/ x, /*int*/ y, /*object*/ cell )
	{
		this.hideMenu();
		
		// adjust the p position
		y += this.canvas.offsetTop;
		
		// set menu title
		this.dom.popupMenuTitle.text( "Cell " + cell.appID );

		// set menu items 
		var menu = this.dom.popupMenu;

		if (cell.isRetiring)
		{
			menu.removeClass( "cell-retirable" );
			menu.addClass( "cell-retiring" );

			this.dom.cancelRetireLink.click( function()
			{
				this.hideMenu();
				this._cancelRetiringCell( cell );
			}.bind( this ) );
		}
		else
		{
			// retire cell menu item
			menu.removeClass( "cell-retiring" );
			menu.addClass( "cell-retirable" );

			this.dom.retireLink.click( function()
			{
				this.hideMenu();
				this._retireCell( cell );
			}.bind( this ) );

		}

		if (this.notEnoughCellApps)
		{
			menu.addClass( "not-enough-cellapps" );
			this.dom.splitLink.off( "click" );
		}
		else
		{
			menu.removeClass( "not-enough-cellapps" );

			this.dom.splitLink.click( function()
			{
				this.hideMenu();
				this._splitCell( cell )
			}.bind( this ) );
		}

		// kill menu if we pan/zoom/etc as position will likely be wrong
		jQuery( this ).one( 'viewportChange.sv', this.hideMenu.bind( this ) );

		// kill menu if use clicked mouse 
		jQuery( this.canvas ).one( 'mousedown', this.hideMenu.bind( this ) );

		menu.fadeIn( UI.popupMenu.fadeInDuration );
		
		var menuWidth = this.dom.popupMenuList.outerWidth();
		var menuHeight = this.dom.popupMenuList.outerHeight();
		if (x + menuWidth > this.canvas.width)
		{
			//make sure that menu is drawn with in canvas right bound
			x = this.canvas.width - menuWidth;
		}

		if (y + menuHeight > this.canvas.height)
		{
			//draw above when there is no space below
			y = this.canvas.height - menuHeight;
		}
		
		menu.css( { left: x, top: y } );

		var reaperTimer = setTimeout(
			this.hideMenu.bind( this ),
			UI.popupMenu.maxTotalDuration
		);

		this.menuState = {
			cell: cell,
			reaperTimer: reaperTimer,
		};
	},

	hideMenu: function()
	{
		if (!this.menuState)
		{
			return;
		}

		// un-hook the click event, otherwise the hooked one will accumulate
		this.dom.retireLink.off( "click" );
		this.dom.cancelRetireLink.off( "click" );
		this.dom.splitLink.off( "click" );

		// fadeOut seems not work well on this absolutely positioned menu
		this.dom.popupMenu.hide();
		clearTimeout( this.menuState.reaperTimer );
		this.menuState = null;
	},
	
	showTooltip: function( entity )
	{
		if (this.tooltipState && this.tooltipState.entity[3] == entity[3])
		{
			// a tooltip already exists for this entityId
			return;
		}
		this.hideTooltip();

		var x = this.convertWorldToScreenX( entity[0] );
		var y = this.convertWorldToScreenY( entity[1] );

		var tooltip = jQuery( "<div/>" );

		// ensure tooltips are eventually removed
		var reaperTimer = setTimeout(
			function()
			{
				if (SV.debugTooltip)
				{
					console.log( "reaping tooltip " + tooltip.attr( 'id' ) );
				}
				this.tooltipState.tooltip.delay(
					UI.entityTooltip.fadeOutDelay ).fadeOut(
						UI.entityTooltip.fadeOutDuration, function() {
						   jQuery( this ).remove(); });
			}
			.bind( this ),
			UI.entityTooltip.maxTotalDuration
		);

		tooltip.attr( { class: "sv-tooltip", id: entity[3] } );

		// add actual content
		var tooltipContent = jQuery( '<div/>' ).attr( 'class', 'sv-tooltip-content' );

		// tooltip content of form: "Guard #1234"
		tooltipContent.html(
			(UI.entityTooltip.showColour ?
			'<div class="sv-entity" style="float: left; margin: 3px; background: ' +
			UI.entity.colours[ entity[2] ] +
			'" />' : '') +
			(this.entityTypes[ entity[2] ]
			|| "<em>Unknown entity type</em>") + " #" + entity[3] );
		tooltipContent.appendTo( tooltip );

		// add tooltip tip
		jQuery( '<div class="sv-tooltip-tip-container"><div class="sv-tooltip-tip" /></div>' )
			.appendTo( tooltip );

		// hide tooltip if we pan/zoom/etc as position will likely be wrong
		jQuery( this ).one( 'viewportChange.sv', this.hideTooltip.bind( this ) );

		// kill tooltip if user manages to mouse over it
		tooltip.one( 'mousemove', this.hideTooltip.bind( this ) );

		// prevent tooltips from interfering with canvas events
		tooltip.find( 'div' ).addClass( 'sv-event-ignore' );

		// set left/top *before* width/height calc to account for content reflow
		// that will occur at canvas edges.
		tooltip.css( { left: x, top: y } );

		this.dom.container.append( tooltip );
		tooltip.fadeIn( UI.entityTooltip.fadeInDuration );

		this.tooltipState = {
		   entity: entity,
		   tooltip: tooltip,
		   startX: x,
		   startY: y,
		   reaperTimer: reaperTimer,
		};

		// position tooltip horiz centred, floating above entity
		x -= tooltip.outerWidth() / 2;
		y -= tooltipContent.height();

		x += 1.5; // adjust for border width
		y -= 3; // adjust height for aesthetics

		tooltip.css( { left: x, top: y } );

		// below code is a stub for making tooltip move when entity moves;
		// requires us to be interpolating position, which will likely be
		// added soon
		/*
		if (entity.length >= 8 )
		{
		   // var delta = this.convertWorldToScreenDist( entity[6], entity[7] );
		   // tooltip.animate(
			//    {
			// 	   left: entity[6] < 0 ?
			// 		   '-=' + Math.abs( delta.x ) :
			// 		   '+=' + delta.x,
			// 	   top: entity[7] > 0 ?
			// 	   '-=' + Math.abs( delta.y ) :
			// 	   '+=' + delta.y,
			//    }, 1400, 'linear'
		   // );
		   var updateEntityPosition = function()
		   {
			   if (!this.tooltipState)
			   {
				   jQuery( this ).unbind( 'draw.sv', updateEntityPosition );
				   return;
			   }


		   };

		   jQuery( this ).on({
			   'draw.sv': function()
			   {
			   }
		   });
		}
		*/

		if (SV.debugTooltip)
		{
			console.log( "showing tooltip for entity %d at %dpx,%dpx", entity[3], x, y );
		}
	},


	hideTooltip: function()
	{
		if (!this.tooltipState)
		{
			return;
		}

		var entity = this.tooltipState.entity;
		var entityId = entity[3];
		if (SV.debugTooltip)
		{
			console.log("hiding tooltip for entity %d", entityId );
		}

		// remove tooltip from DOM after some delay/fade out.
		this.tooltipState.tooltip.delay(
			UI.entityTooltip.fadeOutDelay ).fadeOut(
				UI.entityTooltip.fadeOutDuration, function() {
					jQuery( this ).remove();
				});

		clearTimeout( this.tooltipState.reaperTimer );
		this.tooltipState = null;
	},
	
	/**
	*   Make the cell selected if it is not
	*/
	selectCell: function( /*Object*/ cell)
	{
		var selectedCell = this.getSelectedCell();
		
		if (this.getSelectedCell().appID == cell.appID)
		{
			return;
		}

		this.setSelectedCell( cell, true );
		this._reparentEntities( selectedCell, cell, cell.worldRect );

		// if interpolating, we need to reparent the entities for the
		// *next* data frame as well as the current data frame.
		if (this._isInterpolating)
		{
			// traverse next data frame BSP to find the cells we need
			var c1, c2;
			this.visitBsp( this._nextData.root, function( node, visitor )
			{
				if (node.appID === selectedCell.appID)
				{
					c1 = node;
				}
				else if (node.appID === cell.appID)
				{
					c2 = node;
				}
				if (c1 && c2)
					visitor.shouldStopTraversing = true;
			});

			this._reparentEntities( c1, c2, cell.worldRect );
		}

		this.requestModelUpdate();
		this.draw();
	},

	/**
	*   Select the next cell in depth-first order. If makeVisible
	*   is true then next cell will be made visible in the current
	*   viewport if it is outside the current viewport.
	*/
	selectNextCell: function( /*boolean*/ makeVisible )
	{
		var cells = this.cells;
		var cell;

		if (!cells || cells.length == 0)
		{
			return;
		}

		if (!this.selectedCellId || cells.length == 1)
		{
			this.selectedCellId = cells[0].appID;
			return;
		}

		var i = 0;
		while (i < cells.length)
		{
			cell = cells[i++];
			if (cell.appID == this.selectedCellId)
			{
				break;
			}
		}

		cell = i < cells.length ? cells[i] : cells[0];
		this.setSelectedCell( cell, true );

		if (makeVisible && !cell.screenRect)
		{
			this.zoomToCell( cell );
		}
	},


	/** Select the previous cell in depth-first order. */
	selectPrevCell: function( /*boolean*/ makeVisible )
	{
		var cells = this.cells;
		if (!cells || cells.length == 0)
		{
			return;
		}

		if (!this.selectedCellId || cells.length == 1)
		{
			this.selectedCellId = cells[0].appID;
			return;
		}

		var i = cells.length - 1;
		while (i >= 0)
		{
			if (cells[i--].appID == this.selectedCellId)
			{
				break;
			}
		}

		var cell = (i >= 0) ? cells[i] : cells[ cells.length - 1 ];
		this.setSelectedCell( cell, true );

		if (makeVisible && !cell.screenRect)
		{
			this.zoomToCell( cell );
		}
	},


	/** Drag map to given canvas/pixel coordinates. */
	dragTo: function( /*int*/ canvasX, /*int*/ canvasY )
	{
		var drag = this.dragState;
		if (!drag)
		{
			console.warn("No drag state set");
			return;
		}

		var xDelta = canvasX - drag.startPos.x;
		var yDelta = canvasY - drag.startPos.y;

		if (!drag.inProgress)
		{
			if (Math.max( Math.abs( xDelta ), Math.abs( yDelta ) ) > 3)
			{
				drag.inProgress = true;
			}
		}

		if (drag.inProgress)
		{
			if (this.dragPartition)
			{
				// dragging partition
				var partition = this.dragPartition.partition;
				if (partition.isHorizontal)
				{
					partition.screenPosition =	
							this.dragPartition.originalPos + yDelta;
				}
				else
				{
					partition.screenPosition =
							this.dragPartition.originalPos + xDelta;
				}
				
				this.draw();
			}
			else
			{
				// dragging the whole space
				var delta = this.convertScreenToWorldDist( xDelta, yDelta );
				this.xPosition = drag.worldRef.x - delta.x;
				this.yPosition = drag.worldRef.y - delta.y;

				this.draw();
				jQuery( this ).triggerHandler( 'viewportChange.sv' );
			}
		}
	},


	_onMouseUp: function( /*MouseEvent*/ ev )
	{
		this._deriveCanvasCoords( ev );
		if (this.dragState && !this.dragState.inProgress)
		{
			// just click
			var cell = this.cellAt( this.convertScreenToWorldX( ev.canvasX ),
									this.convertScreenToWorldY( ev.canvasY ) );

			this.selectCell( cell );

			// check whether is over cell menu
			if (this.manualLoadBalanceEnabled
					&& this._isMouseOverCellMenu( cell ))
			{
				this.showMenu( ev.canvasX, ev.canvasY, cell );
			}
		}

		if (this.dragState)
		{
			this.dragTo( ev.canvasX, ev.canvasY );
			
			if (this.dragPartition)
			{
				this.dragPartition.released = true;
				this._clearOverPartition();

				// update the position of dragged partition
				var partition = this.dragPartition.partition;
				var screenPosition = partition.screenPosition;
				var worldPos;

				if (partition.isHorizontal)
				{
					worldPos = this.convertScreenToWorldY( screenPosition );
				}
				else
				{
					worldPos = this.convertScreenToWorldX( screenPosition );
				}
		
				this._updateSvrPartitionPos( partition, worldPos );			
			}
			
			// reset dragState, but keep dragged partition in its new position
			// wait until next updateData, otherwise the partition line would
			// bounce
			this.dragState = null;
		}
	},


	_reparentEntities: function( fromCell, toCell, rect )
	{
		if (!rect) return;

		var oldReals = fromCell.realEntities;
		var oldGhosts = fromCell.ghostEntities;

		var newReals = toCell.realEntities || [];
		var newGhosts = toCell.ghostEntities || [];

		// append old reals
		if (oldReals && oldReals.length)
		{
			newGhosts = newGhosts.concat( oldReals );
		}

		var i, e;
		for (i in oldGhosts)
		{
			e = oldGhosts[ i ];
			if (e[0] > rect.minX && e[0] < rect.maxX &&
				e[1] > rect.minY && e[1] < rect.maxY)
			{
				newReals.push( e )
			}
			else
			{
				newGhosts.push( e )
			}
		}

		fromCell.realEntities = fromCell.ghostEntities = null;
		toCell.realEntities = newReals;
		toCell.ghostEntities = newGhosts;

		this._sortEntitiesByType( toCell );
	},


	/**
	*   Partition the entities of the given cell according to current space
	*   partitioning
	*/
	_partitionEntities: function( fromCell )
	{
		var ghosts = fromCell.ghostEntities;
		fromCell.ghostEntities = null;

		this.visitBsp( this.data.root, function( node ) {
			if (node.isHorizontal !== undefined)
			{
				// partition
				var ents = node.realEntities || ghosts;
				var leftEnts = node.left.realEntities || [];
				var rightEnts = node.right.realEntities || [];

				if (node.isHorizontal)
				{
					// partition horizontal, compare entity y to partition pos
					for (var i in ents)
					{
						if (ents[i][1] < node.position)
						{
							leftEnts.push( ents[i] );
						}
						else
						{
							rightEnts.push( ents[i] );
						}
					}
				}
				else
				{
					// partition vertical, compare entity x to partition pos
					for (var i in ents)
					{
						if (ents[i][0] < node.position)
						{
							leftEnts.push( ents[i] );
						}
						else
						{
							rightEnts.push( ents[i] );
						}
					}
				}

				// delete temporary association of entities with partition
				delete node.realEntities;

				console.log( "partition %d has %d left reals, %d right",
					node.bspPos, leftEnts.length, rightEnts.length );

				node.left.realEntities = leftEnts;
				node.right.realEntities = rightEnts;
			}
			else
			{
				// // cell
				console.log( "cell %d now has %d reals",
					node.appID, node.realEntities.length );
			}
		});
	},


	/** Centres the current view on the given x and y worldspace coords. */
	centreViewAt: function( /*int*/ worldX, /*int*/ worldY, /*boolean*/ shouldAnimate )
	{
		var centreX = this.convertScreenToWorldX( this.canvas.width / 2 );
		var centreY = this.convertScreenToWorldY( this.canvas.height / 2 );

		if (SV.debug)
		{
			console.log("centreViewAt: " + worldX + "," + worldY );
		}

		if (shouldAnimate === undefined)
		{
			shouldAnimate = UI.animation.pan > 0;
		}

		this.pan( worldX - centreX, worldY - centreY, shouldAnimate );
	},


	/** Pans view by the given worldspace delta X/Y. */
	pan: function( /*int*/ deltaX, /*int*/ deltaY, /*boolean*/ shouldAnimate )
	{
		var newX = this.xPosition + deltaX;
		var newY = this.yPosition + deltaY;

		var duration = UI.animation.pan.duration;
		var viewportAnim = this.viewportAnimation;

		shouldAnimate = shouldAnimate && UI.animation.enabled &&
				UI.animation.pan.enabled && duration > 0;

		if (shouldAnimate)
		{
			// make animation take slightly longer when panning over large distances
			var distFactor = 5 * Math.log( Math.pow( deltaX, 2 ) + Math.pow( deltaY, 2 ) );
			viewportAnim.duration = duration + distFactor;

			viewportAnim.deltaX = deltaX;
			viewportAnim.deltaY = deltaY;
			viewportAnim.deltaZ = 0;

			viewportAnim.startX = this.xPosition;
			viewportAnim.startY = this.yPosition;
			viewportAnim.startZ = this.xPageSize;

			viewportAnim.play();
		}
		else
		{
			this.xPosition = newX;
			this.yPosition = newY;
			this.draw();
		}
		if (SV.debug)
		{
			console.log("pan: " + deltaX + "," + deltaY );
		}

		jQuery( this ).triggerHandler( 'viewportChange.sv' );
	},


	/** Pans view by the given canvas pixel delta X/Y. */
	panCanvas: function( /*int*/ deltaPixelX, /*int*/ deltaPixelY, shouldAnimate )
	{
		var deltaWorld =
			this.convertScreenToWorldDist( deltaPixelX, deltaPixelY );
		this.pan( deltaWorld.x, deltaWorld.y, shouldAnimate );
	},


	zoomIn: function()
	{
		this.zoom( this.canvas.width / 2, this.canvas.height / 2,
				SV.ZOOM_FACTOR, true );
	},


	zoomOut: function()
	{
		this.zoom( this.canvas.width / 2, this.canvas.height / 2,
				1 / SV.ZOOM_FACTOR, true );
	},


	/**
	*	Zoom to the given canvas (pixel) coordinates, with the given zoom
	*	magnitude. Magnitudes of > 1 zoom in, < 1 zoom out.
	*/
	zoom: function( x, y, mag, /*boolean*/ shouldAnimate )
	{
		if (!x || !y)
		{
			console.dir( arguments );
			throw new Error( "Invalid arguments" );
		}

		if (x < 0 || y < 0)
		{
			console.dir( arguments );
			throw new Error( "Expected positive integer coords" );
		}

		// zoom
		var newXPageSize = this.xPageSize / mag;

		// check for min/max zoom
		if (newXPageSize >= SV.MAX_PAGE_SIZE)
		{
			if (SV.debug > 1)
			{
				console.log( "zoom: max zoom exceeded" );
			}
			return;
		}

		if (newXPageSize <= SV.MIN_PAGE_SIZE)
		{
			if (SV.debug > 1)
			{
				console.log("zoom: min zoom exceeded");
			}
			return;
		}

		// pan viewport x/y to same world x/y as before zoom
		var deltaZ = newXPageSize - this.xPageSize;
		var viewportDelta = -deltaZ / this.canvas.width;
		var deltaX = viewportDelta * x;
		var deltaY = -viewportDelta * y;

		if (SV.debug >= 1)
		{
			console.log( "zoom: x" + mag.toFixed( 3 ) +
					" at (" + x + "px," + y + "px): " +
					"viewport-x " + this.xPageSize.toPrecision( 2 ) + "m -> " +
					newXPageSize.toPrecision( 2 ) + "m, " +
					(this.canvas.width / newXPageSize).toPrecision( 2 ) +
					" pix/m" );
		}

		var duration = UI.animation.zoom.duration; //msec
		var viewportAnim = this.viewportAnimation;

		if (shouldAnimate && UI.animation.enabled && duration > 0)
		{
			viewportAnim.duration = duration;

			viewportAnim.deltaX = deltaX;
			viewportAnim.deltaY = deltaY;
			viewportAnim.deltaZ = deltaZ;

			viewportAnim.startX = this.xPosition;
			viewportAnim.startY = this.yPosition;
			viewportAnim.startZ = this.xPageSize;

			viewportAnim.play();
		}
		else
		{
			this.xPageSize = newXPageSize;
			this.xPosition += deltaX;
			this.yPosition += deltaY;
			this.draw();
			jQuery( this ).triggerHandler( 'viewportChange.sv' );
		}
	},


	/** Updates UI elements after a zoom or pan */
	_updateBoundsUI: function()
	{
		var dom = this.dom;

		// update world bounds rect
		var viewport = this.getScreenBounds();

		var digits = 1;
		if (this.xPageSize > 10000)
		{
			digits = 0;
		}

		dom.bounds.html( viewport.minX.toFixed( digits ) + ", " +
				viewport.minY.toFixed( digits ) + " to " +
				viewport.maxX.toFixed( digits ) + ", " +
				viewport.maxY.toFixed( digits ) );
	},


	/**
	*	Set the viewport to the bounding box of the given worldspace coordinates.
	*/
	zoomToRect: function( /*Object*/ worldRect, /*boolean*/ shouldAnimate )
	{
		if (shouldAnimate === undefined)
		{
			shouldAnimate = true;
		}

		if (SV.debug)
		{
			var current = this.getScreenBounds();
			console.log(
				"zoomToRect: (%f, %f, %f, %f) -> (%f, %f, %f, %f)",
				current.minX, current.minY, current.maxX, current.maxY,
				worldRect.minX, worldRect.minY, worldRect.maxX, worldRect.maxY
			);
		}

		var xw = worldRect.maxX - worldRect.minX;
		var yw = worldRect.maxY - worldRect.minY;

		// Can't calculate deltas until after viewport adjustments have
		// already been made, so if we are animating, we take a snapshot
		// of viewport properties prior to changes for later use in animation.
		var saved;
		var viewportAnim = this.viewportAnimation;
		var duration = UI.animation.zoomToRect.duration;
		shouldAnimate &= (UI.animation.enabled &&
			UI.animation.zoomToRect.enabled && duration > 0);

		if (shouldAnimate)
		{
			saved = {
				xPosition: this.xPosition,
				yPosition: this.yPosition,
				xPageSize: this.xPageSize,
			};
		}

		// calculate changes
		this.xPosition = worldRect.minX;
		this.yPosition = worldRect.maxY;
		this.xPageSize = xw;

		var width = this.canvas.width;
		var height = this.canvas.height;

		if (!width || !height)
			throw new Error("Zero width and/or height");

		if (xw / width > yw / height)
		{
			this.xPageSize = xw;
			var nyw = -this.convertScreenToWorldY( height ) + this.yPosition;
			this.yPosition += (nyw - yw) / 2;
		}
		else
		{
			this.xPageSize = yw * width / height;
			var nxw = this.convertScreenToWorldX( width ) - this.xPosition;
			this.xPosition -= (nxw - xw) / 2;
		}

		// animate or draw
		if (shouldAnimate)
		{
			viewportAnim.duration = duration;

			viewportAnim.deltaX = this.xPosition - saved.xPosition;
			viewportAnim.deltaY = this.yPosition - saved.yPosition;
			viewportAnim.deltaZ = this.xPageSize - saved.xPageSize;

			viewportAnim.startX = this.xPosition = saved.xPosition;
			viewportAnim.startY = this.yPosition = saved.yPosition;
			viewportAnim.startZ = this.xPageSize = saved.xPageSize;

			viewportAnim.play();
		}
		else
		{
			this.draw();
			jQuery( this ).triggerHandler( 'viewportChange.sv' );
		}
	},


	/** Returns worldspace bounds of space. */
	getSpaceBounds: function()
	{
		var bounds3D = this.data.spaceBounds;
		return {
			minX: bounds3D[0],
			minY: bounds3D[2],
			maxX: bounds3D[3],
			maxY: bounds3D[5]
		};
	},


	/** Returns the worldspace bounds rectangle of the current viewport. */
	getScreenBounds: function()
	{
		return {
			minX: this.xPosition,
			minY: this.convertScreenToWorldY( this.canvas.height, false ),
			maxX: this.xPosition + this.xPageSize,
			maxY: this.yPosition
		};
	},


	/** Returns all real entities. */
	getRealEntities: function()
	{
		return this.getSelectedCell().realEntities || [];
	},


	/** Returns all ghosted entities. */
	getGhostEntities: function()
	{
		return this.getSelectedCell().ghostEntities || [];
	},


	/**
	*   Zooms viewport to the intersection of the passed cell's world rect
	*   and the current space's space bounds.
	*/
	zoomToCell: function( /*optional cell obj or int*/ cell )
	{
		if (!cell)
		{
			cell = this.getSelectedCell();
		}
		else if (typeof cell === 'number')
		{
			// get cell object if passed a cell id
			cell = this.getCell( cell );
		}

		if (!cell.worldRect)
		{
			return;
		}

		var cellBounds = this._intersectRect( cell.worldRect, this.getSpaceBounds() );
		this._scaleRect( cellBounds, 1.1 );
		this.zoomToRect( cellBounds );
	},


	zoomToEntityBounds: function( /*optional cell obj or int*/ cell )
	{
		var highlightedEntities = UI.entity.highlighted;
		if (Object.keys( highlightedEntities ).length > 0)
		{
			var rect = {
				minX: Number.MAX_VALUE,
				minY: Number.MAX_VALUE,
				maxX: Number.MIN_VALUE,
				maxY: Number.MIN_VALUE,
			};

			var entities = this.getRealEntities();
			var e;
			for (var i in entities)
			{
				e = entities[i];
				if (!highlightedEntities[ e[2] ])
					continue;

				if (e[0] < rect.minX) rect.minX = e[0];
				if (e[0] > rect.maxX) rect.maxX = e[0];
				if (e[1] < rect.minY) rect.minY = e[1];
				if (e[1] > rect.maxY) rect.maxY = e[1];
			}

			// expand rect by 50 metres
			rect.minX -= 50;
			rect.maxX += 50;
			rect.minY -= 50;
			rect.maxY += 50;

			// and expand rect bounds by 10%
			this._scaleRect( rect, 1.1 );

			this.zoomToRect( rect );

			return rect;
		}

		if (!cell)
		{
			cell = this.getSelectedCell();
		}
		else if (typeof cell === 'number')
		{
			// get cell object if passed a cell id
			cell = this.getCell( cell );
		}

		if (cell.entityBoundLevels)
		{
			var entityBounds = this._copyRect( cell.entityBoundLevels[4] );

			// expand rect bounds by 10%
			this._scaleRect( entityBounds, 1.1 );

			this.zoomToRect( entityBounds );

			return entityBounds;
		}
	},


	/** Set the viewport zoom level to show the entire space bounds. */
	zoomToSpaceBounds: function( /*boolean*/ shouldAnimate )
	{
		var bounds = this.getSpaceBounds();
		this.zoomToRect( bounds, shouldAnimate );
	},


	/** Set the viewport zoom level to fill the current viewport. */
	zoomToSpaceView: function()
	{
		var bounds = this.getSpaceBounds();

		var xw = bounds.maxX - bounds.minX;
		var yw = bounds.maxY - bounds.minY;
		var width = this.canvas.width;
		var height = this.canvas.height;

		if (xw / yw < width / height)
		{
			// vert aspect is greater, shrink rect height
			var bit = (yw - xw * height / width) / 2;
			bounds.minY += bit;
			bounds.maxY -= bit;
		}
		else
		{
			// horiz aspect is greater, shrink rect width
			var bit = (xw - yw * width / height) / 2;
			bounds.minX += bit;
			bounds.maxX -= bit;
		}

		this.zoomToRect( bounds, true );
	},


	/**
	*	Tranforms worldspace coords to pixel coords on canvas.
	*
	*	shouldRound - apply rounding to values, defaults to false if not given.
	*/
	convertWorldToScreenX: function( x, /*(optional) boolean*/ shouldRound )
	{
		var px = (x - this.xPosition) / this.xPageSize * this.canvas.width;
		return shouldRound ? Math.round( px ) : px;
	},


	/**
	*	Transforms worldspace coords to pixel coords on canvas.
	*
	*	shouldRound - apply rounding to values, defaults to false if not given.
	*/
	convertWorldToScreenY: function( y, /*(optional) boolean*/ shouldRound )
	{
		var py = (this.yPosition - y) / this.xPageSize * this.canvas.width;
		return shouldRound ? Math.round( py ) : py;
	},


	/**
	*	Project a distance vector in worldspace to canvas.
	*
	*	shouldRound - apply rounding to values, defaults to false if not given.
	*/
	convertWorldToScreenDist: function( /*number*/ dx,
									  /*number*/ dy,
									  /*(optional) boolean*/ shouldRound )
	{
		var dx2 = dx / this.xPageSize * this.canvas.width;
		var dy2 = -dy / this.xPageSize * this.canvas.width;

		return (shouldRound ?
				{ x: Math.round( dx2 ), y: Math.round( dy2 ) } :
				{ x: dx2, y: dy2 });
	},


	/**
	*	Transform a worldspace 2D area (rectangle) to canvas coordinates.
	*
	*	shouldRound - apply rounding to values, defaults to false if not given.
	*/
	convertWorldToScreenRect: function( rect, /*(optional) boolean*/ shouldRound )
	{
		return {
			minX: this.convertWorldToScreenX( rect.minX, shouldRound ),
			minY: this.convertWorldToScreenY( rect.maxY, shouldRound ),
			maxX: this.convertWorldToScreenX( rect.maxX, shouldRound ),
			maxY: this.convertWorldToScreenY( rect.minY, shouldRound ) };
	},


	/**
	*	Transforms canvas pixel coords to worldspace coords.
	*
	*	shouldRound - apply rounding to values, defaults to false if not given.
	*/
	convertScreenToWorldX: function( x, /*(optional) boolean*/ shouldRound )
	{
		var worldX = (x / this.canvas.width * this.xPageSize) + this.xPosition;
		return shouldRound ? Math.round( worldX ) : worldX;
	},


	/**
	*	Transforms canvas pixel coords to worldspace coords.
	*
	*	shouldRound - apply rounding to values, defaults to false if not given.
	*/
	convertScreenToWorldY: function( y, /*(optional) boolean*/ shouldRound )
	{
		var worldY = this.yPosition - (y / this.canvas.width * this.xPageSize);
		return shouldRound ? Math.round( worldY ) : worldY;
	},


	/**
	*	Transforms a canvas distance/vector to worldspace.
	*
	*	shouldRound - apply rounding to values, defaults to false if not given.
	*/
	convertScreenToWorldDist: function( /*number*/ canvasX,
									/*number*/ canvasY,
									/*(optional) boolean*/ shouldRound )
	{
		var worldX = canvasX / this.canvas.width * this.xPageSize;
		var worldY = -canvasY / this.canvas.width * this.xPageSize;

		return (shouldRound ?
				{ x: Math.round( worldX ), y: Math.round( worldY ) } :
				{ x: worldX, y: worldY });
	},


	/**
	*	Asynchronously poll model for data. Causes the "requestUpdate.model.sv"
	*	event passing (url, spaceData) when call completes. Causes the
	*	"failedRequestUpdate.model.sv" event passing (jqXHR, textStatus, exception)
	*	on a poll fail.
	*   When force is set to true, force to re-request and updateData upon result
	*/
	requestModelUpdate: function( /*?boolean*/ force )
	{
		var selectedCellId = this.selectedCellId;

		// prevent multiple concurrent data requests (eg: rapid clicking on
		//	a cell).
		if (this._requestInProgress && this._requestInProgress === selectedCellId)
		{
			if (force)
			{
				this._xhr.abort();
				
				if (SV.debug > 1)
				{
					console.log( "Forced to request space data" );
				}
			}
			else
			{
				if (SV.debug > 1)
				{
					console.log(
						"request already in progress for cell %d, ignoring",
						selectedCellId
					);
				}

				return null;
			}
		}

		var url = "get_space?space=" + this.spaceId;
		if (this.selectedCellId)
		{
			url += ";cell=" + selectedCellId;
		}

		if (SV.debug > 1)
		{
			console.log( 'requestModelUpdate requesting: ' + url );
			console.time( 'requestModelUpdate: ' + url );
		}

		this._requestInProgress = selectedCellId;
		var _this = this;
		this._xhr = jQuery.ajax({
			url: url,
			dataType: "json",
			timeout: 10000, // 10 secs
			success: function( spaceData )
			{
				if (SV.debug > 1)
					console.timeEnd( 'requestModelUpdate: ' + url );

				jQuery( _this ).triggerHandler( "requestUpdate.model.sv",
					[ url, spaceData ] );
				
				if (force)
				{
					_this._nextData = null;
					_this.updateData( spaceData );
				}
				if (this._isInterpolating)
				{
					// smooth interpolation by delaying data frames by a small
					// amount to account for network & model latency
					setTimeout(
						function() {
							_this.updateData( spaceData );
						}, UI.interpolation.delay
					);
				}
				else
				{
					_this.updateData( spaceData );
				}

				_this._requestModelUpdateFailedLastTime = false;
				_this._requestInProgress = false;
				_this._xhr = null;
			},

			error: function( jqXHR, textStatus, except )
			{
				// abort is triggered intentionally
				if (textStatus !=  "abort")
				{
					if (SV.debug > 1)
						console.timeEnd( 'requestModelUpdate: ' + url );

					console.warn( new Date() +
						" Ajax call to " + url + " failed: " + textStatus );

					_this._requestInProgress = false;
					this._xhr = null;

					jQuery( _this ).triggerHandler(
							"failedRequestUpdate.model.sv",
							[ jqXHR, textStatus, except ] );
				}
			},
		});
		
		return this._xhr;
	},


	/**
	*	Asynchronous requests Map of defined entity types from the server.
	*	Triggers a jQuery event named "receiveEntityTypes.sv" on successful
	*	retrieval.
	*/
	requestEntityTypes: function()
	{
		var url = "get_entity_types?space=" + this.spaceId;
		jQuery.getJSON( url, function( data ) {

			this.entityTypes = data;

			// init colours for entities/ghosts
			this._generateEntityColours( UI );

			this._loadEntityIcons();

			jQuery( this ).triggerHandler("receiveEntityTypes.sv");
		}
		.bind( this ) );
	},


	_loadEntityIcons: function( /*optional*/ iconMap )
	{
		var entityTypes = this.entityTypes;
		if (!iconMap)
		{
			iconMap = UI.entityIcons.images = {};
		}

		var queue = Object.keys( entityTypes );
		var start = +new Date;
		var countSuccess = 0;

		var loader = new ChainLoader.Image({ numConcurrentJobs: 3, delay: 0 });

		jQuery( loader ).one( 'finish.loading',
			function()
			{
				if (SV.debug)
				{
					var elapsed = +new Date - start;
					console.log( "loaded %d/%d entity icons in %d msec",
						countSuccess, queue.length, elapsed );
				}
				var iconlessEntityTypes = [];
				for (var typeId in entityTypes)
				{
					if (iconMap[ typeId ]) continue;
					iconlessEntityTypes.push( entityTypes[ typeId ] );
				}

				if (UI.entityIcons.enabled && iconlessEntityTypes.length == queue.length)
				{
					// none of the entity types have icons
					new Alert.Warning(
						"No entity icons found in res path, disabling entity " +
						"icon drawing option.<br/>See the <a href=\"help\">" +
						"help page</a> for further information.",
						{ id: 'no-entity-icons-present', duration: 10000 }
					);
					UI.entityIcons.enabled = false;
					jQuery( this ).triggerHandler( 'configChanged.sv' );
				}
				else if (UI.entityIcons.enabled && iconlessEntityTypes.length > 0)
				{
					var n = new Alert.Info(
						'Not all entities have icons.<br/>' +
						'<span class="missing_entity_icons_list" style="display: none; font-size: smaller">' +
						'<ul><li>' +
						iconlessEntityTypes.sort().join( '</li><li>' ) +
						'</li></ul>' +
						'See the <a href="/sv/help#Entity_Icons">help page</a> ' +
						'for further information.</span>'
					);
					n.jquery.hover(
						function() { jQuery('.missing_entity_icons_list', this).fadeIn(); },
						function() { jQuery('.missing_entity_icons_list', this).fadeOut(); }
					);
				}
			}.bind( this )
		);

		for (var i in queue)
		{
			var typeId = queue[ i ];
			var url = SV.BASEURL_ENTITY_ICONS + '/' + entityTypes[ typeId ] + '.png';

			var img = new Image();

			img.entityTypeId = typeId;

			jQuery( img ).one( 'load', function() {
				iconMap[ this.entityTypeId ] = this;
				countSuccess++;
			});

			loader.schedule( typeId, url, img );
		}

		loader.load();
	},


	_sortEntitiesByType: function( cell )
	{
		var entities = cell.realEntities;
		if (entities)
		{
			entities.sort( function( a, b ) { return a[2] - b[2]; } );
		}

		entities = cell.ghostEntities;
		if (entities)
		{
			entities.sort( function( a, b ) { return a[2] - b[2]; } );
		}
	},


	/** Update internal state with the given data, and redraw. */
	updateData: function( data )
	{
		if (!data)
		{
			throw new Error( "Null data" );
		}

		var hadData = !!this.data;

		//	sanity checks

		if (data.error)
		{
			new Alert.Error(
				data.error + '<br/><a href="spaces">Return to spaces list</a>',
				{ id: 'server-error' }
			);
			this.disconnectModel();
			return;
		}
		else
		{
			Alert.dismiss( 'server-error' );
		}

		if (!data.gridResolution)
		{
			new Alert.Warning(
				"Space data for space " + this.spaceId +
				" has no gridResolution set, defaulting to 100",
				{ id: "sv-invalid-gridres" }
			);
			data.gridResolution = 100;
		}
		else
		{
			Alert.dismiss( 'sv-invalid-gridres' );
		}

		var sb = data.spaceBounds;
		if (sb && (sb[0] === sb[3] || sb[2] === sb[5]))
		{
			sb = data.spaceBounds = [-100, -100, -100, 100, 100, 100];
			new Alert.Warning(
				"Space bounds of space " + this.spaceId +
				" has zero x/z dimension(s), using a default spaceBounds: " + sb,
				{ id: "sv-invalid-spacebounds-dimensions" }
			);
		}
		else if (!data.root || !sb)
		{
			// absence of these properties (usually) indicates the server is in
			// a transitory state (just started up, in process of shutting down).
			new Alert.Info(
				"Waiting for server...",
				{ id: 'waiting-for-server', duration: 1800 }
			);
			console.log( "invalid data tick: %O", data );
			return;
		}
		else
		{
			Alert.dismiss( 'sv-invalid-spacebounds-dimensions' );
			Alert.dismiss( 'waiting-for-server' );
		}

		// calc interpolation data
		if (this._isInterpolating)
		{
			this._lastUpdate = data._whenReceived = +new Date; // msecs
			if (this._nextData)
			{
				this.data = this._nextData;
				this._nextData = data;
				this.data._pollInterval = data._whenReceived - this.data._whenReceived;

				if (SV.debug > 1)
					console.log( 'pollInterval: %f', this.data._pollInterval );

				this._calcInterpolationDeltas( this.data, data );
			}
			else
			{
				// this is the first frame of data since interpolation started
				this.data = this._nextData = data;
			}
		}
		else
		{
			this.data = data;
		}

		// preprocess new data:
		// 1) get refs to cells/partitions from BSP for later use.
		// 2) pre-sort entities by type in order to have a defined
		//    draw order for entities and a consistent behaviour for entity
		//    detection (entityAt method).
		// 3) generate bspId for each node (same to bspPos, but bspPos
		//    will be only generated when interpolation is on)
		var cells = new Array();
		var partitions = new Array();
		var sortEntitiesByType = this._sortEntitiesByType;
		this.data.root.bspId = 1;

		this.visitBsp(
			this.data.root,
			function( node )
			{
				if (node.isHorizontal === undefined)
				{
					// node is a cell
					cells.push( node );

					if (node.realEntities || node.ghostEntities)
					{
						sortEntitiesByType( node );
					}
				}
				else
				{
					// node is a partition
					partitions.push( node );
					
					if (this.dragState && this.dragPartition)
					{
						// reset drag partition state if bsb has changed
						// when partition with same bspId have different
						// isHorizontal value
						var selected= this.dragPartition.partition;
						
						if (node.bspId == selected.bspId
							&& node.isHorizontal != selected.isHorizontal )
						{
							this.dragState = null;
							this.dragPartition = null;
						}
					}

					node.left.bspId = node.bspId << 1; // * 2
					node.right.bspId = ( node.bspId << 1 ) | 1; // * 2 + 1
				}
			}
		);
		this.partitions = partitions;
		this.cells = cells;

		// if this is the first time we've received data, then zoom viewport
		// to correct spacebounds.
		if (!hadData)
		{
			this.zoomToSpaceBounds( false );
		}

		// determine backgroundImage from mapping name if not already given
		if (this.backgroundImage.src === "")
		{
			this.spaceName = "";
			if (data.mappings.length)
			{
				this.spaceName = this.data.geometry || data.mappings[0][2];

				if (SV.debug)
				{
					console.log("space mapping name: %s", this.spaceName );
				}

				if (this.spaceName)
				{
					this.setBackgroundImage(
						"/sv/resources/" + this.spaceName + "/space_viewer/"
						+ SV.BG_IMAGE_FILE_NAME	);

					this.dom.title.html( "Space " + this.spaceId + ": " +
							this.spaceName );
				}
			}
		}

		// selectedCellId will (normally) not be set until first data model poll
		if (data.selectedCell && !this.selectedCellId)
		{
			this.setSelectedCell( data.selectedCell );
		}

		// update status bar entity/ghost info
		var selectedCell = this.getSelectedCell();
		if (selectedCell && selectedCell.realEntities)
		{
			this.dom.entityStats.html( selectedCell.realEntities.length +
					" real entities, " + selectedCell.ghostEntities.length +
					" ghost entities" );
		}

		// update status bar cellapp info
		var stats = data.stats;
		if (stats)
		{
			// cellapp info
			this.dom.cellStats.html( stats.cells + " of " + stats.cellapps +
					" cellapps," );
			
			if (stats.cells >= stats.cellapps)
			{
				this.notEnoughCellApps = true;
			}
			else
			{
				this.notEnoughCellApps = false;
			}
		}

		jQuery( this ).triggerHandler( 'updateModel.sv' );

		// no need to issue a draw call if we're interpolating at X fps
		if (!this._isInterpolating)
		{
			this.draw();
		}
	},


	setBackgroundImage: function( /*String URL or Image*/ image )
	{
		if (typeof image === 'string')
		{
			if (SV.debug)
			{
				console.log( "setting background image: %s", image);
			}
			this.backgroundImage.src = image;
		}
		else
		{
			this.backgroundImage = image;
			this.draw();
		}
	},


	getCell: function( /*int*/ cellId )
	{
		var cells = this.cells;
		for (var i in cells)
		{
			if (cells[i].appID == cellId)
			{
				return cells[i];
			}
		}
		return null;
	},


	getSelectedCell: function()
	{
		var cell = this.getCell( this.selectedCellId );
		if (!cell && this.selectedCellId)
		{
			// ie: we've received data in the past but selected cell
			// is no longer present in the data, so choose one arbitrarily
			cell = this.cells[0];
			if (SV.debug)
			{
				console.log("selectedCell " + this.selectedCellId +
						" no longer exists, setting selectedCell = " + cell.appID );
			}
			this.selectedCellId = cell.appID;
		}
		return cell;
	},


	setSelectedCell: function( /*int or Object*/ cell, /*boolean*/ shouldAnimate )
	{
		var cellId = (typeof cell === "object") ? cell.appID : cell;

		// validity check
		cell = this.getCell( cellId );

		if (!cell)
		{
			console.warn( "No cell with id %d in current data", cellId );
			return;
		}

		this.selectedCellId = cellId;
		if (SV.debug)
		{
			console.log("selectedCell = " + cellId);
		}

		// do not animate selecting a cell for now
		if (shouldAnimate && UI.animation.enabled)
		{
			this.selectedCellAnimation.play();
		}

		jQuery( this ).triggerHandler( 'changeSelectedCell.sv', cell );
	},


	/**
	*	Traverses BSP to pre-calculate screen coords from world coords.
	*/
	_calcTraversal: function()
	{
		if (!this.data)
			return;

		if (this._isInterpolating && this._nextData)
		{
			this._interpolateFrame();
		}

		var bspRoot = this.data.root;
		bspRoot.worldRect = {
			minX: -Number.MAX_VALUE,
			minY: -Number.MAX_VALUE,
			maxX: Number.MAX_VALUE,
			maxY: Number.MAX_VALUE,
		};
		var screenBounds = this.getScreenBounds();

		this.visitBsp(
			bspRoot,
			function( node )
			{
				var worldRect = node.worldRect;
				var screenRect = this._intersectRect( worldRect, screenBounds );
				if (screenRect)
				{
					node.screenRect = this.convertWorldToScreenRect( screenRect );
				}
				else
				{
					// partition/cell is not in the current viewport
					// note: for partitions, screenRect refers to the rect
					// the partition bisects, for cells it is cell area.
					node.screenRect = null;
				}

				if (node.isHorizontal === undefined)
				{
					// node is a cell
					return;
				}

				// else node is a partition
				var leftRect  = this._copyRect( worldRect );
				var rightRect = this._copyRect( worldRect );
				var position = node.position;

				if (node.isHorizontal)
				{
					leftRect.maxY = position;
					rightRect.minY = position;
					
					// don't update the screen position if this partition is
					// being dragged
					if (this._isDraggedPartition( node ))
					{
						node.screenPosition =
							this.dragPartition.partition.screenPosition;
						this.dragPartition.partition = node;
					}
					else
					{
						node.screenPosition =
								this.convertWorldToScreenY( position );
					}
				}
				else
				{
					leftRect.maxX = position;
					rightRect.minX = position;

					// don't update the screen position if this partition is
					// being dragged
					if (this._isDraggedPartition( node ))
					{
						node.screenPosition =
							this.dragPartition.partition.screenPosition;
						this.dragPartition.partition = node;
					}
					else
					{
						node.screenPosition =
								this.convertWorldToScreenX( position );
					}
				}

				// set world bounds of children
				// note: left/right children can be partitions OR cells
				node.left.worldRect = leftRect;
				node.right.worldRect = rightRect;
			}
		);
	},


	_blankCanvas: function() {  this._blankCanvasSetWidth();  },


	/** Clear canvas. */
	_blankCanvasSetWidth: function()
	{
		this.canvas.width = this.canvas.width;
	},


	_blankCanvasClearRect: function()
	{
		this.context.clearRect( 0, 0, this.canvas.width, this.canvas.height );
	},


	/** Clears canvas and draws scene. */
	draw: function( /*boolean*/ forceRedraw )
	{
		var start = + new Date();
		if (!forceRedraw && (start - this._frame < SV.MIN_DRAW_INTERVAL))
        {
            if (this._futureFrame)
                return;

            this._futureFrame = setTimeout(
                function()
                {
                    this.draw();
                    this._futureFrame = null;
                }
                .bind( this ),
                SV.MIN_DRAW_INTERVAL - (start - this._frame)
            );
            return;
        }

		// pre-calculate screen coords prior to drawing
		this._calcTraversal();

		var partitions = this.partitions;
		var cells = this.cells;
		var i;

		var selectedCell = this.getSelectedCell();

		// clear canvas; allow for browser-specific clears
		this._blankCanvas();

		// background image
		if (this.data)
			this.drawBackground();

		// cell load background tint
		if (UI.cellLoad.enabled)
		{
			for (i in cells)
				this.drawCellLoad( cells[i] );
		}

		// selected cell chunk bounds
		if (UI.chunkBounds.enabled && selectedCell)
		{
			this.drawChunkBounds( selectedCell );
		}

		// entity bound levels
		if (UI.entityBounds.enabled)
		{
			for (i in cells)
				this.drawEntityBounds( cells[i] );
		}

		// selected cell boundary
		if (UI.cellBoundary.enabled && selectedCell)
		{
			this.drawCellBoundary( selectedCell );
		}

		// entities

		if (UI.ghostEntity.enabled && selectedCell)
		{
			this.drawGhostEntities( selectedCell );
		}

		if (UI.entity.enabled && selectedCell)
		{
			this.drawEntities( selectedCell );
		}

		// partitions
		if (UI.partitionLine.enabled)
		{
			for (i in partitions)
				this.drawPartition( partitions[i] );
		}

		// check if the mouse is currently over partition 
		if (this.manualLoadBalanceEnabled)
		{
			if (!this._checkMouseOverCellMenu())
			{
				this._checkOverPartition( this.mousePos.x, this.mousePos.y );
			}
		}

		// draw retiring effect
		for (i in cells)
		{
			if (cells[ i ].isRetiring)
			{
				this._drawRetiringEffect( cells[ i ] );
			}
		}

		// cell labels
		if (UI.cellLabel.enabled)
		{
			for (i in cells)
			{
				this.drawCellLabel( cells[i] );
			}
		}

		if (UI.scaleIndicator.enabled)
		{
			this.drawScaleIndicator();
		}

		if (UI.cellLoad.enabled)
		{
			this.drawCellLoadIndicator();
		}

		if (this.manualLoadBalanceEnabled)
		{
			this._drawMenuIcon();
		}

		this._frame = +new Date;
		this._frameTime = this._frame - start;

		jQuery( this ).triggerHandler( 'draw.sv' );
	},


	_getEntitySize: function()
	{
		return UI.entity.radius +
			12 / Math.log( this.xPageSize ) +
			this.convertWorldToScreenDist( 0.5, 0 ).x;
	},


	drawCellLoadIndicator: function()
	{
		var ctx = this.context;
		var cellLoadStyle = UI.cellLoad;
		var indicatorStyle = cellLoadStyle.indicator;
		var stats = this.data.stats;

		ctx.save();
		this.setStyle( cellLoadStyle );

		// indicator size
		var width = indicatorStyle.width;
		var height = indicatorStyle.height;

		// indicator position
		var left = indicatorStyle.left;
		var top =
			Math.max( 0, this.canvas.height - indicatorStyle.bottom - height );
		var bottom = top + height;
		var textLeft = left + width + indicatorStyle.tickLength;

		var gradient = ctx.createLinearGradient( left, top, left, bottom );

		var colourLow;
		var colourHigh;
		var avgPosition;
		var maxLoad;
		var minLoad;
		var avgLoad;

		if (UI.cellLoad_useRelativeLoad.enabled)
		{
			colourLow = "rgb(" + UI.cellLoad.lowestRelativeLoad.slice( 0, 3 ).join(",") + ")";
			colourHigh = "rgb(" + UI.cellLoad.highestRelativeLoad.slice( 0, 3 ).join(",") + ")";

			// var avg = (stats.avgLoad - stats.minLoad) / (stats.maxLoad - stats.minLoad);
			avgLoad = stats.avgLoad;
			var cutoff = cellLoadStyle.minRelativeLoadCutoff || 0.1;
			minLoad = Math.max( 0, Math.min( avgLoad - cutoff, stats.minLoad ) );
			maxLoad = Math.max( avgLoad + cutoff, stats.maxLoad );

			/*
			// make avg tick move with actual avg, to show distribution of vals
			var avg = (stats.avgLoad - stats.minLoad) / (stats.maxLoad - stats.minLoad);
			avgPosition = top + height * avg;
			gradient.addColorStop( avg, "rgba( 0, 0, 0, 0 )" );
			*/
			avgPosition = (top + bottom) / 2;
			gradient.addColorStop( 0.5, "rgba( 0, 0, 0, 0 )" );
			gradient.addColorStop( 0, colourHigh );
			gradient.addColorStop( 1, colourLow );
		}
		else
		{
			minLoad = 0;
			maxLoad = 1;
			// colourLow = "rgb(" + UI.cellLoad.lowestLoad.slice( 0, 3 ).join(",") + ")";
			colourLow = "rgba(" + UI.cellLoad.lowestLoad.slice( 0, 3 ).join(",") + ",0.25)";
			colourHigh = "rgb(" + UI.cellLoad.highestLoad.slice( 0, 3 ).join(",") + ")";
			gradient.addColorStop( 0, colourHigh );
			gradient.addColorStop( 0.65, colourLow );
			gradient.addColorStop( 1, 'rgba(0,0,0,0)' );
		}

		// background for indicator gradient
		// ctx.fillStyle = '#fff';
		// ctx.fillRect( x, y, width, height );

		// draw gradient
		ctx.fillStyle = gradient;
		ctx.fillRect( left, top, width, height );

		// border for gradient
		if (cellLoadStyle.lineWidth)
		{
			ctx.strokeRect( left, top, width, height );
		}

		// draw indicator lines across the scale
		this.setStyle( indicatorStyle );

		// top tick
		ctx.moveTo( left, top );
		ctx.lineTo( textLeft, top );
		ctx.stroke();

		// bottom tick
		ctx.moveTo( left, bottom );
		ctx.lineTo( textLeft, bottom );
		ctx.stroke();

		// draw indicator text labels
		if (UI.cellLoad_useRelativeLoad.enabled)
		{
			// middle tick
			ctx.moveTo( left, avgPosition );
			ctx.lineTo( textLeft, avgPosition );
			ctx.stroke();

			textLeft += indicatorStyle.labelMargin; // gap between scale & text
			this.drawText( maxLoad.toFixed( 2 ), textLeft, top );
			this.drawText( minLoad.toFixed( 2 ), textLeft, bottom );
			this.drawText( avgLoad.toFixed( 2 ), textLeft, avgPosition );
		}
		else
		{
			textLeft += indicatorStyle.labelMargin; // gap between scale & text
			this.drawText( maxLoad.toFixed( 2 ), textLeft, top );
			this.drawText( minLoad.toFixed( 2 ), textLeft, bottom );
		}

		ctx.restore();
	},


	/** Draw cell (absolute or relative) load as background tint. */
	drawCellLoad: function( cell )
	{
		var rect = cell.screenRect;
		if (!rect)
		{
			// cell is not visible in current viewport
			return;
		}

		var ctx = this.context;
		ctx.save();

		var allCells = this.data.stats;
		var lo;
		var hi;
		var load;
		var alpha;

		if (UI.cellLoad_useRelativeLoad.enabled)
		{
			lo = UI.cellLoad.lowestRelativeLoad;
			hi = UI.cellLoad.highestRelativeLoad;
			var cutoff = UI.cellLoad.minRelativeLoadCutoff;

			var highestLoad = Math.max( allCells.maxLoad, allCells.avgLoad + cutoff );
			var lowestLoad = Math.min( allCells.minLoad, allCells.avgLoad - cutoff );

			load = (cell.load - allCells.minLoad) / (highestLoad - lowestLoad);
			var relLoad = Math.abs((cell.load - allCells.avgLoad) / (highestLoad - lowestLoad));

			ctx.globalAlpha = relLoad < cutoff ? 0 : relLoad;
			alpha = 0.4;
		}
		else
		{
			// absolute load
			lo = UI.cellLoad.lowestLoad;
			hi = UI.cellLoad.highestLoad;
			load = cell.load / Math.max( 1, allCells.maxLoad );

			// rescale load so that load of 0-0.35 shows no colour
			// load = Math.max( 0.35, load );
			load -= UI.cellLoad.minAbsoluteLoadCutoff;
			load /= (1 - UI.cellLoad.minAbsoluteLoadCutoff);

			// load can sometimes be > 1 if entity count load balancing is used
			// so cap at 1.0 for colour scale calc.
			load = Math.min( cell.load, 1.0 );

			if (load < 0)
			{
				load = 0;
				alpha = 0;
			}
			else
			{
				alpha = (lo[3] + ((hi[3] - lo[3]) * load));
			}
		}

		// calc colour range from min/max colours
		var rgba = [
			Math.round( lo[0] + ((hi[0] - lo[0]) * load) ),
			Math.round( lo[1] + ((hi[1] - lo[1]) * load) ),
			Math.round( lo[2] + ((hi[2] - lo[2]) * load) ), alpha ];
		var colour = "rgba(" + rgba.join(",") + ")";

		ctx.fillStyle = colour;
		ctx.fillRect( rect.minX, rect.minY,
			rect.maxX - rect.minX, rect.maxY - rect.minY );

		ctx.restore();
	},


	drawCellLabel: function( cell )
	{
		var screen = cell.screenRect;
		if (!screen)
		{
			// cell not visible in current viewport
			return;
		}

		// label text lines
		var lines = new Array();

		if (UI.cellLabel_cellId.enabled)
			lines.push("Cell " + cell.appID);

		if (UI.cellLabel_ipAddress.enabled)
			lines.push( cell.addr );

		if (UI.cellLabel_load.enabled)
			lines.push( cell.load.toFixed( 3 ) );

		if (cell.isRetiring)
			lines.push("Retiring");

		if (cell.isOverloaded)
			lines.push("OVERLOADED");

		if (lines.length == 0)
		{
			// UI.cellLabel.enabled = false;
			return;
		}

		// draw label at centre of cell
		var centreX = (screen.minX + screen.maxX) / 2;
		var centreY = (screen.minY + screen.maxY) / 2;

		var shouldHighlight = (cell.appID == this.selectedCellId);

		this.drawCellLabelText( lines, centreX, centreY, shouldHighlight );
	},


	drawCellBoundary: function( cell )
	{
		var r = cell.screenRect;
		if (!r)
		{
			// cell not visible in current viewport
			return;
		}

		var ctx = this.context;
		ctx.save();

		this.setStyle( UI.cellBoundary );
		var offset = UI.cellBoundary.offset;

		var width = r.maxX - r.minX;
		var height = r.maxY - r.minY;

		if (SV.debugDrawing)
		{
			console.log( "(%f,%f,%f,%f) cell %f boundary rect",
				r.minX, r.minY, width, height, cell.appID );
		}

		// clip to cell boundary to avoid overdraw for thin cells
		// note: firefox requires a beginPath() or the clip() call will
		// prevent all subsequent draw calls.
		ctx.beginPath();
		ctx.rect( r.minX, r.minY, width, height );
		ctx.clip();

		ctx.strokeRect( r.minX + offset, r.minY + offset,
				width - (2 * offset), height - (2 * offset) );

		// optional cell fill
		if (UI.cellBoundary.fillStyle)
		{
			ctx.fillRect( r.minX, r.minY, width, height );
		}

		ctx.restore();
	},


	drawEntities: function( /*Object*/ cell )
	{
		var entities = cell.realEntities;
		if (SV.debug > 1)
		{
			console.log( "drawing %i reals for cell %d",
				entities ? entities.length : 0, cell.appID );
		}

		if (!entities)
		{
			return;
		}

		// console.log( "drawing %i reals", entities.length );
		if (UI.entityIcons.enabled)
		{
			this._drawEntitiesAsIcons( entities, UI.entity,
				UI.entity.excluded, UI.entity.highlighted );
		}
		else
		{
			this._drawEntities( entities, UI.entity,
				UI.entity.excluded, UI.entity.highlighted );
		}
	},


	drawGhostEntities: function( /*Object*/ cell )
	{
		var entities = cell.ghostEntities;
		if (SV.debug > 1)
		{
			console.log( "drawing %i ghosts for cell %d",
				entities ? entities.length : 0, cell.appID );
		}

		if (!entities)
		{
			return;
		}

		if (UI.entityIcons.enabled)
		{
			this._drawEntitiesAsIcons( entities, UI.ghostEntity,
				UI.entity.excluded, UI.entity.highlighted );
		}
		else
		{
			this._drawEntities( entities, UI.ghostEntity,
				UI.entity.excluded, UI.entity.highlighted );
		}
	},


	_drawEntities: function( entities, style, excludeMap, highlightMap )
	{
		var ctx = this.context;
		var entityTypes = this.entityTypes;

		if (!excludeMap)
			excludeMap = {};

		if (!highlightMap)
			highlightMap = {};

		ctx.save();
		this.setStyle( style );

		// adjust entity radius to be slightly larger when zoomed in
		var radius = this._getEntitySize();

		var colours = style.colours;
		var highlightList = [];
		var seen = {};
		var entityTypeId;
		var entity;

		var screenBounds = this.getScreenBounds();
		screenBounds.minX -= radius;
		screenBounds.minY -= radius;
		screenBounds.maxX += radius;
		screenBounds.maxY += radius;

		// assumes entities have been sorted already by entityTypeId
		// in updateData() -- ctx.fillStyle is only called for the first
		// entity of each entity type.
		for (var e = entities.length - 1; e >= 0; e--)
		{
			entity = entities[ e ];

			if (entity[0] < screenBounds.minX ||
				entity[0] > screenBounds.maxX ||
				entity[1] < screenBounds.minY ||
				entity[1] > screenBounds.maxY)
			{
				continue;
			}

			entityTypeId = entity[ 2 ];

			if (excludeMap[ entityTypeId ])
			{
				continue;
			}

			// if entity is highlighted, then defer drawing until after
			// all other entities drawn
			if (highlightMap[ entityTypeId ])
			{
				highlightList.push( entity );
				continue;
			}

			var x = this.convertWorldToScreenX( entity[0] );
			var y = this.convertWorldToScreenY( entity[1] );

			if (!seen[ entityTypeId ])
			{
				ctx.fillStyle = colours[ entityTypeId % colours.length ];
				seen[ entityTypeId ] = true;
			}

			if (SV.debugTooltip)
			{
				ctx.beginPath();
				ctx.strokeRect( x - radius, y - radius, radius * 2, radius * 2 );
			}

			ctx.moveTo( x, y );
			ctx.beginPath();
			ctx.arc( x, y, radius, 0, Math.PI*2, false );
			ctx.fill();
			ctx.stroke();
		}
		ctx.restore();

		if (highlightList.length > 0)
		{
			var highlightRadius = radius * UI.entity.radiusMultipleWhenHighlighted;
			UI.entity.radius += highlightRadius;
			this._drawEntities( highlightList, style );
			UI.entity.radius -= highlightRadius;
		}
	},


	_drawEntitiesAsIcons: function( entities, style, excludeMap, highlightMap )
	{
		var ctx = this.context;
		var entityTypes = this.entityTypes;
		var entityIcons = UI.entityIcons;
		var icons = entityIcons.images || {};
		var colours = style.colours;

		if (!excludeMap)
			excludeMap = {};

		if (!highlightMap)
			highlightMap = {};

		ctx.save();
		var highlightList = [];
		// var seen = {};
		var entityTypeId;
		var entity;

		// entity radius varies with zoom level
		var radius = this._getEntitySize();

		// pre-calc & rescale size of entity icons for current zoom level
		var targetSize = (UI.entityIcons.radiusInflation + 2 * radius);
		for (entityTypeId in icons)
		{
			var icon = icons[ entityTypeId ];
			if (!icon || !icon.width) continue;

			// scale icon such that icon dimensions are equidistant from
			// target size, ie: longest dimension - size == size - shortest.
			var avg = (icon.width + icon.height) / 2;
			icon.w = targetSize * icon.width / avg;

			if (entityTypes[ entityTypeId ] == 'Dragon')
				icon.w *= 1.5;

			icon.h = icon.w * icon.height / icon.width;
			icon.left = icon.w / 2;
			icon.top = icon.h / 2;
		}

		// assumes entities have been sorted already by entityTypeId
		// in updateData() -- ctx.fillStyle is only called for the first
		// entity of each entity type.
		for (var e = entities.length - 1; e >= 0; e--)
		{
			entity = entities[ e ];
			entityTypeId = entity[ 2 ];

			if (excludeMap[ entityTypeId ])
			{
				continue;
			}

			// if entity is highlighted, then defer drawing until after
			// all other entities drawn
			if (highlightMap[ entityTypeId ])
			{
				highlightList.push( entity );
				continue;
			}

			var x = this.convertWorldToScreenX( entity[0] );
			var y = this.convertWorldToScreenY( entity[1] );

			if (style === UI.ghostEntity)
			{
				ctx.globalAlpha = UI.ghostEntity.iconAlpha;
			}

			var icon = icons[ entityTypeId ];
			if (icon && icon.width)
			{
				ctx.drawImage( icon, x - icon.left, y - icon.top, icon.w, icon.h );
			}
			else
			{
				// no icon or not loaded; use a fallback
				ctx.beginPath();
				ctx.fillStyle = colours[ entityTypeId % colours.length ];
				ctx.arc( x, y, radius, 0, Math.PI*2, false );
				ctx.fill();
				ctx.stroke();
			}

			if (style === UI.ghostEntity) ctx.globalAlpha = 1;
			if (SV.debugTooltip)
			{
				ctx.beginPath();
				ctx.strokeRect( x - radius, y - radius, radius * 2, radius * 2 );
			}
		}
		ctx.restore();

		if (highlightList.length > 0)
		{
			var highlightRadius = radius * UI.entity.radiusMultipleWhenHighlighted;
			UI.entity.radius += highlightRadius;
			this._drawEntitiesAsIcons( highlightList, style );
			UI.entity.radius -= highlightRadius;
		}
	},


	drawPartition: function( partition )
	{
		var labelText = this.getPartitionLabelText( partition );
		var shouldDrawLabel = labelText && UI.partitionLabel.enabled;
		var lineStyle = jQuery.extend( {}, UI.partitionLine );
		var pos = partition.screenPosition;
		var drawArrow = false;

		if (this.manualLoadBalanceEnabled)
		{
			lineStyle = jQuery.extend( lineStyle, UI.draggablePartitionStyle );
			var drawArrow = true;
		}

		if (this.dragState && this._isDraggedPartition( partition ) )
		{
			//draw the original partition line if mouse hasn't been released
			if (!this.dragPartition.released)
			{
				var originalPos = this.dragPartition.originalPos;
				var draggedLineStyle = jQuery.extend( lineStyle,
											UI.draggedPartitionStyle );

				if (shouldDrawLabel)
				{
					this.drawPartitionWithLabel( partition, labelText,
							originalPos, draggedLineStyle );
				}
				else
				{
					this.drawPartitionWithoutLabel( partition, originalPos,
							draggedLineStyle, false );
				}
			}

			// apply dragging style
			lineStyle = jQuery.extend( lineStyle, UI.draggingPartitionStyle );
		}
		else if( this.manualLoadBalanceEnabled
				&& !this._isDraggedPartition( partition )
				&& this._isUnderMouse( partition ))
		{
			// apply dragging style for the line that is under mouse
			lineStyle = jQuery.extend( lineStyle, UI.draggingPartitionStyle );
		}

		if (shouldDrawLabel)
		{
			this.drawPartitionWithLabel( partition, labelText, pos, lineStyle );
		}
		else
		{
			this.drawPartitionWithoutLabel( partition, pos, lineStyle,
					drawArrow );
		}
	},


	drawPartitionWithLabel: function( partition, labelText, pos, lineStyle )
	{
		var rect = partition.screenRect;
		if (!rect)
		{
			// the rect that this partition bisects is entirely outside
			// the current viewport
			return;
		}

		var ctx = this.context;

		// inflate labelWidth slightly as measureText under-reports metrics
		var labelWidth = Math.ceil( ctx.measureText( labelText ).width * 1.2 ); // px
		var halfLength = (partition.isHorizontal) ?
				(rect.maxX - rect.minX) / 2 :
				(rect.maxY - rect.minY) / 2;

		var margin = UI.partitionLabel.margin || 0; // px
		var lineLength = halfLength - labelWidth / 2 - margin;

		// don't draw labels for short partitions (ie: < 8px)
		if (!labelText || lineLength <= 8)
		{
			this.drawPartitionWithoutLabel( partition, pos, lineStyle );
			return;
		}

		if (partition.isHorizontal)
		{
			// draw label
			ctx.save();
			this.setStyle( UI.partitionLabel );
			this.drawText( labelText, rect.minX + halfLength, pos );
			ctx.restore();

			// draw lines
			ctx.save();
			this.setStyle( lineStyle );
			this.drawLine( rect.minX, pos, rect.minX + lineLength, pos );
			this.drawLine( rect.maxX - lineLength, pos, rect.maxX, pos );
			ctx.restore();
		}
		else
		{
			// partition is vertical

			// draw label
			ctx.save();
			this.setStyle( UI.partitionLabel );
			var ac_90 = -90 * Math.PI / 180;
			this.drawText( labelText, pos, rect.minY + halfLength, ac_90 );
			ctx.restore();

			// draw lines
			ctx.save();
			this.setStyle( lineStyle );
			this.drawLine( pos, rect.minY, pos, rect.minY + lineLength );
			this.drawLine( pos, rect.maxY - lineLength, pos, rect.maxY );
			ctx.restore();
		}
	},


	drawPartitionWithoutLabel: function( partition, pos, lineStyle, drawArrow )
	{
		var rect = partition.screenRect;
		if (!rect)
		{
			// the rect that this partition bisects is entirely outside
			// the current viewport
			return;
		}

		if (pos === undefined)
		{
			console.error(
				"partition screenPosition property is undefined: %O",
				partition
			);
		}

		var ctx = this.context;

		ctx.save();
		this.setStyle( lineStyle );

		if (partition.isHorizontal)
		{
			this.drawLine( rect.minX, pos, rect.maxX, pos );

			if (drawArrow)
			{
				var img = this.greenArrowImgH;
				var xPos = ( rect.minX + rect.maxX ) / 2 - img.width / 2;

				pos = pos - img.height / 2; 
				ctx.drawImage( img, xPos, pos );
			}
		}
		else
		{
			this.drawLine( pos, rect.minY, pos, rect.maxY );

			if (drawArrow)
			{
				var img = this.greenArrowImgV;
				var yPos = ( rect.minY + rect.maxY ) / 2 - img.height / 2;

				pos = pos - img.width / 2;
				ctx.drawImage( img, pos, yPos );
			}
		}
		ctx.restore();
	},


	drawLine: function( x1, y1, x2, y2 )
	{
		if (SV.debugDrawing > 1)
		{
			console.log( "(" + Math.round( x1 ) + "," + Math.round( y1 ) + ")" +
				" to " + "(" + Math.round( x2 ) + "," + Math.round( y2 ) + ")" +
				" line" );
		}
		var ctx = this.context;
		ctx.beginPath();
		ctx.moveTo( Math.round( x1 ), Math.round( y1 ) );
		ctx.lineTo( Math.round( x2 ), Math.round( y2 ) );
		ctx.stroke();
	},


	getPartitionLabelText: function( partition )
	{
		// build partition label
		var partitionLabelElements = new Array();

		if (UI.partitionLabel_load.enabled)
		{
			partitionLabelElements.push( partition.load.toFixed( 3 ) );
		}

		if (UI.partitionLabel_aggression.enabled)
		{
			partitionLabelElements.push( partition.aggression.toFixed( 3 ) );
		}

		return partitionLabelElements.join(" / ");
	},


	drawEntityBounds: function( /*Object*/ cell )
	{
		this.context.save();
		this.setStyle( UI.entityBounds );

		var ebl;
		for (var i in cell.entityBoundLevels)
		{
			ebl = cell.entityBoundLevels[i];

			// strange canvas bug where drawing extremely large rects
			// is not consistent, sometimes draws rect over entire canvas,
			// sometimes does not draw rect at all, sometimes draws a partial
			// rect.
			if (ebl.minX < -1e30 || ebl.maxX > 1e30 ||
				ebl.minY < -1e30 || ebl.maxY > 1e30)
					continue;

			this.drawRect( ebl );
		}
		this.context.restore();
	},


	drawChunkBounds: function( /*Object*/ cell )
	{
		var gridResolution = this.data ? this.data.gridResolution : 0;

		// it's an infinite loop if gridRes is anything but a positive int.
		if (! (gridResolution > 0))
		{
			if (SV.debug)
			{
				console.error(
					"Cannot draw chunk bounds, invalid gridResolution: " +
					gridResolution
				);
			}
			return;
		}

		if (SV.debugDrawing)
		{
			console.log("drawChunkBounds: cell " + cell.appID );
		}

		var ctx = this.context;

		ctx.save();
		this.setStyle( UI.chunkBounds );

		var spaceBounds = this.getSpaceBounds();
		var chunkBounds = cell.chunkBounds;

		var worldBounds = {
			minX: Math.max( chunkBounds.minX, spaceBounds.minX ),
			minY: Math.max( chunkBounds.minY, spaceBounds.minY ),
			maxX: Math.min( chunkBounds.maxX, spaceBounds.maxX ),
			maxY: Math.min( chunkBounds.maxY, spaceBounds.maxY ) };

		var screenBounds = this.convertWorldToScreenRect( worldBounds, false );

		var width = this.canvas.width;
		var height = this.canvas.height;
		var x = worldBounds.minX;

		while (x <= worldBounds.maxX)
		{
			var screenX = this.convertWorldToScreenX( x );
			if (screenX >= 0)
			{
				if (screenX >= width)
				{
					break;
				}

				ctx.beginPath();
				ctx.moveTo( screenX, screenBounds.minY );
				ctx.lineTo( screenX, screenBounds.maxY );
				ctx.stroke();
			}

			x += gridResolution;
		}

		var y = worldBounds.minY;
		while (y <= worldBounds.maxY)
		{
			var screenY = this.convertWorldToScreenY( y );
			if (screenY < height)
			{
				if (screenY <= 0)
				{
					break;
				}

				ctx.beginPath();
				ctx.moveTo( screenBounds.minX, screenY );
				ctx.lineTo( screenBounds.maxX, screenY );
				ctx.stroke();
			}

			y += gridResolution;
		}
		ctx.restore();
	},


	/** Draws background image or blank rectangle if not present. */
	drawBackground: function()
	{
		var sbRect = this.convertWorldToScreenRect( this.getSpaceBounds() );
		var image = this.backgroundImage;
		var ctx = this.context;

		if (!image.width || !UI.spaceBackgroundImage.enabled)
		{
			// draw space as blank box
			ctx.save();
			this.setStyle( UI.spaceBackgroundImage );
			ctx.fillRect( sbRect.minX, sbRect.minY,
				sbRect.maxX - sbRect.minX, sbRect.maxY - sbRect.minY );
			ctx.strokeRect( sbRect.minX, sbRect.minY,
				sbRect.maxX - sbRect.minX, sbRect.maxY - sbRect.minY );
			ctx.restore();
			return;
		}

		if (SV.debugDrawing > 1)
		{
			console.log( "drawBackground: image w=" + image.width + ", h=" +
					image.height + ", viewport clip x=" + sbRect.minX +
					", y=" + sbRect.minY + ", w=" +
					(sbRect.maxX - sbRect.minX) + ", h=" +
					(sbRect.maxY - sbRect.minY) );
		}

		ctx.save();
		if (UI.spaceBackgroundImage.imageAlpha < 1)
		{
			ctx.fillStyle = UI.spaceBackgroundImage.fillStyle;
			ctx.fillRect( sbRect.minX, sbRect.minY,
					sbRect.maxX - sbRect.minX, sbRect.maxY - sbRect.minY );
		}

		if (UI.spaceBackgroundImage.imageAlpha > 0)
		{
			// blend with fillStyle
			ctx.globalAlpha = Math.min( 1, UI.spaceBackgroundImage.imageAlpha );
			ctx.drawImage(
				image, 0, 0,
				image.width, image.height,
				sbRect.minX, sbRect.minY,
				sbRect.maxX - sbRect.minX,
				sbRect.maxY - sbRect.minY
			);
		}
		ctx.restore();
	},


	/** Draws a filled and stroked rectangle given as worldspace coordinates. */
	drawRect: function( worldRect )
	{
		var r = this.convertWorldToScreenRect( worldRect, false );
		this.context.fillRect( r.minX, r.minY, r.maxX - r.minX, r.maxY - r.minY );
		this.context.strokeRect( r.minX, r.minY, r.maxX - r.minX, r.maxY - r.minY );
	},


	/** Returns the Cell at the given worldspace coordinates. */
	cellAt: function( /*int*/ x, /*int*/ y, /*(optional Object)*/ node )
	{
		if (!node)
		{
			node = this.data.root;
		}

		if (node.appID !== undefined)
		{
			return node;
		}

		if ((!node.isHorizontal && (x < node.position)) ||
			(node.isHorizontal && (y < node.position)))
		{
			return this.cellAt( x, y, node.left );
		}
		else
		{
			return this.cellAt( x, y, node.right );
		}
	},


	/** World coords. */
	entityAt: function( /*int*/ x, /*int*/ y, /*int*/ proximity, cell )
	{
		if (!cell)
		{
			// cell = this.cellAt( x, y );
			cell = this.getSelectedCell();
			if (!cell)
			{
				console.warn( 'No selected cell, nothing to test' );
				return;
			}
		}

		if (SV.debugTooltip > 1)
		{
			console.log("looking for ent within %f at %f,%f", proximity, x, y );
		}

		proximity = this.convertScreenToWorldDist( proximity, 0 ).x;

		var minX = x - proximity, maxX = x + proximity;
		var minY = y - proximity, maxY = y + proximity;

		// //	optimisation: if point is outside cell's EBLs, then no entities
		// //	will be found by definition.
		// if (cell.entityBoundLevels)
		// {
		//	var ebl = cell.entityBoundLevels[0];
		//	if (minX < ebl.minX || maxX > ebl.maxX || minY < ebl.minY || maxY > ebl.maxY)
		//	{
		//		if (SV.debugTooltip > 1) console.log("outside EBL");
		//		return null;
		//	}
		// }

		var entities, e, i;

		entities = cell.realEntities;
		if (entities)
		{
			for (i in entities)
			{
				e = entities[i];
				if (e[0] < minX || e[0] > maxX || e[1] < minY || e[1] > maxY)
				{
					continue;
				}
				if (SV.debugTooltip > 2) console.log("found real");
				return e;
			}
			if (SV.debugTooltip > 2) console.log("not a real");
		}

		entities = cell.ghostEntities;
		if (entities)
		{
			for (i in entities)
			{
				e = entities[i];
				if (e[0] < minX || e[0] > maxX || e[1] < minY || e[1] > maxY)
				{
					continue;
				}
				if (SV.debugTooltip > 2) console.log("found ghost");
				return e;
			}
			if (SV.debugTooltip > 2) console.log("not a ghost");
		}

		if (SV.debugTooltip > 2) console.log("no entities found");
		return null;
	},


	/**
	*	Draw a styled text label.
	*
	*	Should probably change this into a generalised "drawLabel"
	*	method and allow passed in per-line styles.
	*
	*	Examples:
	*
	*		drawCellLabelText( "text", x, y, true )
	*		drawCellLabelText( ["multiple", "lines"], x, y, false)
	*/
	drawCellLabelText: function( text, x, y, shouldHighlight )
	{
		var textArray = (text instanceof Array) ? text : [text];
		var numLines = textArray.length;
		var ctx = this.context;

		ctx.save();
		ctx.beginPath();

		var labelStyle = UI.cellLabel;
		this.setStyle( labelStyle );
		ctx.fillStyle = labelStyle.backgroundColor;
		
		// calc half width of widest text line
		var halfTextWidth = 0;

		for (var i = 0; i < numLines; i++)
		{
			var width = ctx.measureText( textArray[i] ).width;

			if (width > halfTextWidth)
			{
				halfTextWidth = width;
			}
		}
		halfTextWidth /= 2;

		// half height of all lines
		var halfTextHeight = labelStyle.lineHeight * numLines / 2; // px

		// draw label background
		var left = x - halfTextWidth - labelStyle.paddingX;
		var right = x + halfTextWidth + labelStyle.paddingX;
		var top = y - halfTextHeight - labelStyle.paddingY;
		var bottom = y + halfTextHeight + labelStyle.paddingY;
		var br = labelStyle.borderRadius;

		ctx.moveTo( left + br, top );
		ctx.lineTo( right - br, top );
		ctx.arc( right - br, top + br, br, 1.5 * Math.PI, 0 * Math.PI );

		ctx.lineTo( right, bottom - br );
		ctx.arc( right - br, bottom - br, br, 0 * Math.PI, 0.5 * Math.PI );

		ctx.lineTo( left + br, bottom );
		ctx.arc( left + br, bottom - br, br, 0.5 * Math.PI, 1.0 * Math.PI );

		ctx.lineTo( left, top + br );
		ctx.arc( left + br, top + br, br, 1.0 * Math.PI, 1.5 * Math.PI );

		if (shouldHighlight)
		{
			this.setStyle( UI.cellLabel.highlight );
		}

		ctx.stroke();
		ctx.fill();

		// draw text lines
		ctx.fillStyle = labelStyle.color;
		ctx.strokeStyle = labelStyle.color;

		y -= (labelStyle.lineHeight * (numLines - 1) / 2);

		for (var i = 0; i < numLines; i++)
		{
			this.drawText( textArray[i], x, y );
			y += labelStyle.lineHeight;
		}

		ctx.restore();
	},


	/**
	*	Sets canvas styles from the given hash; non-canvas-related
	*	hash keys skipped.
	*
	*	Typical usage:
	*
	*		ctx.save();
	*		this.setStyle( { ... } );
	*
	*		// draw stuff here...
	*
	*		ctx.restore();
	*/
	setStyle: function( /*Object*/ style )
	{
		var ctx = this.context;
		for (var key in style)
		{
			if (ctx[key] !== undefined)
			{
				ctx[key] = style[key];
			}
		}
	},


	/**
	*	Same as canvas.fillText method, but text is first rotated by
	*	the given angle (in radians).
	*/
	drawText: function( text, x, y, angle )
	{
		if (x === undefined || y === undefined)
		{
			throw new Error( "Invalid coords: (" + x + "," + y + ")" );
		}

		if (!text)
		{
			throw new Error( "No text given" );
		}

		var ctx = this.context;
		if (angle)
		{
			ctx.save();
			var radius = Math.sqrt( Math.pow( x, 2 ) + Math.pow( y, 2 ) );
			var theta = Math.atan2( y, x ) + angle;
			var sin = Math.sin( angle );
			var cos = Math.cos( angle );
			var dx = x - radius * Math.cos( theta );
			var dy = y - radius * Math.sin( theta );

			if (SV.debugDrawing > 1)
			{
				console.log( "(" + x.toFixed() + "," + y.toFixed() + ") " +
						"rotated text: '" + text + "' " +
						"(angle=" + (180 * angle / Math.PI) + ")" );
			}
			ctx.transform( cos, sin, -sin, cos, dx, dy );
			ctx.fillText( text, x, y );
			ctx.restore();
		}
		else
		{
			if (SV.debugDrawing > 1)
			{
				console.log( "(" + x.toFixed() + "," + y.toFixed() + ") " +
						"text: '" + text + "'" );
			}
			ctx.fillText( text, x, y );
		}
	},


	/**
	*	Draws scale indicator control on canvas; style and position taken
	*	from UI.scaleIndicator and UI.scaleIndicatorLabel.
	*/
	drawScaleIndicator: function()
	{
		var ctx = this.context;

		var indicatorStyle = UI.scaleIndicator;
		var labelStyle = UI.scaleIndicatorLabel;
		var minWidth = indicatorStyle.minWidth; // px
		var maxWidth = indicatorStyle.maxWidth; // px
		var height = indicatorStyle.height;		// px

		var scale = this.calcScaleIndicator( indicatorStyle.maxWidth );
		var text = scale.text;
		var width = scale.width;

		// x,y = top-left of widget
		var x = indicatorStyle.left;
		var y = this.canvas.height - indicatorStyle.bottom - height;

		if (SV.debugDrawing > 1)
		{
			console.log("(" + x + "," + y + ") scale indicator, width = " + width);
		}

		// scale indicator line
		ctx.save();
		this.setStyle( indicatorStyle );

		ctx.beginPath();
		ctx.moveTo( x, y );
		ctx.lineTo( x, y + height );
		ctx.lineTo( x + width, y + height );
		ctx.lineTo( x + width, y );

		ctx.stroke();
		ctx.restore();

		// scale indicator label
		ctx.save();
		this.setStyle( labelStyle );

		if (labelStyle.textAlign === "right")
		{
			// adjust for right align of text
			labelStyle.offsetX = width - labelStyle.offsetX;
		}

		this.drawText( text, x + labelStyle.offsetX, y - labelStyle.offsetY );

		ctx.restore();
	},


	/**
	*	Derives a suitable scale indicator size/value for the given max pixel
	*	length, rounded to have a prefix of 1, 2 or 5.
	*	Returns an object of form:
	*
	*	{
	*		text: "5m",		// value + unit
	*		val: 5,		// value only
	*		width: 169	// scale indicator length for <text> in pixels
	*	}
	*/
	calcScaleIndicator: function( /*number*/ maxScreenWidth ) /*returns Object*/
	{
		var maxWorldWidth =
			this.convertScreenToWorldDist( maxScreenWidth, 0, false ).x;

		// round to nearest power of 10
		var exp = Math.floor( Math.log( maxWorldWidth ) / Math.LN10 ); // log10
		var worldWidth = Math.pow( 10, exp ); // Smaller power of 10.

		var prefix = maxWorldWidth / worldWidth;

		if (prefix >= 5.0)
		{
			worldWidth *= 5.0;
		}
		else if (prefix >= 2.0)
		{
			worldWidth *= 2.0;
		}

		var widthInUnits = worldWidth;
		var unit = 'm';

		if (widthInUnits < 0.01)
		{
			unit = 'mm';
			widthInUnits *= 1000;
		}
		else if (widthInUnits < 1.0)
		{
			unit = "cm";
			widthInUnits *= 100;
		}
		else if (widthInUnits >= 1000)
		{
			unit = 'km';
			widthInUnits /= 1000;
		}

		var text = widthInUnits + unit;

		return {
			text: text,
			val: widthInUnits,
			width: this.convertWorldToScreenDist( worldWidth, 0 ).x
		};
	},


	/**
	*	Generic depth-first traversal method over the partition/cell binary
	*	space partition (BSP).
	*
	*	Arguments:
	*	node - starting/current node
	*	nodeVisitor - callback function that is called as:
	*
	*		nodeVisitor.call( this, node, nodeVisitor )
	*
	*	Traversal can be terminated early by setting:
	*
	*		nodeVisitor.shouldStopTraversing = true;
	*/
	visitBsp: function( /*Object*/ node, /*function*/ nodeVisitor )
	{
		// visit node
		nodeVisitor.call( this, node, nodeVisitor );

		// test for traversal stop condition
		if (nodeVisitor.shouldStopTraversing)
		{
			return;
		}

		if (node.isHorizontal === undefined)
		{
			// node is a cell
			return;
		}

		// node is a partition
		this.visitBsp( node.left, nodeVisitor );
		this.visitBsp( node.right, nodeVisitor );
	},


	startInterpolation: function()
	{
		if (this._isInterpolating)
		{
			if (SV.debug)
			{
				console.warn(
					"startInterpolation called while interpolation already running" );
			}
			return;
		}

		this._isInterpolating = true;
		this._nextData = null;
		this.interpol.play();
		if (SV.debug)
		{
			console.log( "starting interpolation, targetFps=" +
				this.interpol.targetFps );
		}
	},


	stopInterpolation: function()
	{
		if (!this._isInterpolating)
		{
			if (SV.debug)
			{
				console.warn(
					"stopInterpolation called but interpolation not running" );
			}
			return;
		}

		this._isInterpolating = false;
		this.interpol.stop();
		if (SV.debug)
		{
			console.log( "stopped interpolation, average fps=" +
				this.interpol.fps );
		}
	},


	_interpolateFrame: function()
	{
		if (!this._nextData || !this.data._pollInterval)
			return;

		var now = +new Date;
		var delta = (now - this.data._whenReceived - SV.POLL_INTERVAL)
			/ (this._nextData._whenReceived - this.data._whenReceived);

		// console.log( "interval = " + this.data._pollInterval + ", delta = " + delta );
		// console.log( "delta = " + delta );
		if (!delta)
		{
			return;
		}

		/*
		if (delta > 1)
		{
			console.log( "_interpolateFrame: delta > 1: %f; pollInterval: %f",
				delta, this.data._pollInterval );

			// delta = 1;
		}
		else if (delta < 0)
		{
			console.log( "_interpolateFrame: delta < 0: %f; pollInterval: %f",
				delta, this.data._pollInterval );

			// delta = 0;
		}
		// else console.log( "_interpolateFrame: delta: ", delta );
		*/

		//	update entity and partition positions with delta time
		this.visitBsp(
			this.data.root,
			function( node )
			{
				if (node.appID)
				{
					//	node is cell
					if (node.realEntities)
					{
						this._updateEntities( node.realEntities, delta );
					}
					if (node.ghostEntities)
					{
						this._updateEntities( node.ghostEntities, delta );
					}
				}
				else
				{
					//	node is partition
					if (node.positionDelta !== undefined)
					{
						node.position = node.positionStart +
							node.positionDelta * Math.min(
								UI.interpolation.partitionSpeedup * delta, 1 );
					}
				}
			}
		);
	},


	_calcInterpolationDeltas: function( currentData, newData )
	{
		var newBsp = newData.bspPositions = { 1: newData.root }; // newData.root;
		newData.root.bspPos = 1;
		var currentBsp = currentData.bspPositions || {};

		this.visitBsp(
			newData.root,
			function( node )
			{
				//	record BSP node positions
				if (node.left)
				{
					node.left.bspPos = node.bspPos << 1;
				}
				if (node.right)
				{
					node.right.bspPos = (node.bspPos << 1) | 1;
				}
				newBsp[node.bspPos] = node;

				if (node.appID)
				{
					//	node is cell
					this._compareEntities( currentData, newData, node );
				}
				else
				{
					//	node is partition; compare to node in same position
					//	in the last BSP.
					//	calc partition position deltas
					var currentNode = currentBsp[ node.bspPos ];

					if (!currentNode ||
						currentNode.isHorizontal === undefined ||
						node.isHorizontal ^ currentNode.isHorizontal)
					{
						return;
					}

					var positionDiff = node.position - currentNode.position;
					if (positionDiff < -500 || positionDiff > 500)
					{
						return;
					}
					currentNode.positionStart = currentNode.position;
					currentNode.positionDelta = positionDiff;
				}
			}
		);
	},


	/**
	*   Update (interpolate) entity positions with given delta.
	*   As of current, an uninterpolated Entity is:
	*
	*       [ x, y, type, id ]
	*
	*   while an interpolated entity will look like:
	*
	*       [ x, y, type, id, lastX, lastY, deltaX, deltaY ]
	*
	*   where last* comes from the previous data frame, and delta*
	*   is the delta between the last data frame and the data frame we're
	*   interpolating towards (ie: lastX + deltaX == x of next frame).
	*/
	_updateEntities: function( entities, delta )
	{
		var e;
		for (var i in entities)
		{
			e = entities[i];
			if (e.length === 4)
			{
				continue;
			}
			e[0] = e[4] + e[6] * delta;
			e[1] = e[5] + e[7] * delta;
		}
	},


	/**
	*   Compare and calculate position deltas between the entities of
	*   the passed cell between the 2 given data frames.
	*
	*   In the general case, currentData will be this.data, and newData
	*   will be a new/incoming data frame.
	*/
	_compareEntities: function( currentData, newData, newCell )
	{
		var newRealEntities = newCell.realEntities;
		var newGhostEntities = newCell.ghostEntities;

		var entities;
		var newEnt, existingEnt, dx, dy;

		entities = newData.entities;
		if (!entities)
		{
			entities = newData.entities = {};
		}

		var existingEntities = currentData.entities;
		if (!existingEntities)
		{
			existingEntities = currentData.entities = {};
		}

		var existingGhostEntities = currentData.ghostEntities;
		if (!existingGhostEntities)
		{
			existingGhostEntities = currentData.ghostEntities = {};
		}

		// process reals
		if (newRealEntities)
		{
			for (var i in newRealEntities)
			{
				newEnt = newRealEntities[i];
				entities[ newEnt[3] ] = newEnt;
				existingEnt = existingEntities[ newEnt[3] ];

				if (!existingEnt)
				{
					// allow for real -> ghost
					existingEnt = existingGhostEntities[ newEnt[3] ];
					if (!existingEnt)
					{
						continue;
					}
				}
				dx = newEnt[0] - existingEnt[0];
				dy = newEnt[1] - existingEnt[1];

				existingEnt.splice( 4, 4, existingEnt[0], existingEnt[1], dx, dy );
				// console.log("ent %d: %d, %d: ", newEnt[3], dx, dy, existingEnt );
			}
		}

		// process ghosts
		entities = newData.ghostEntities;
		if (!entities)
		{
			entities = newData.ghostEntities = {};
		}

		if (newGhostEntities)
		{
			for (var i in newGhostEntities)
			{
				newEnt = newGhostEntities[i];
				entities[ newEnt[3] ] = newEnt;
				existingEnt = existingGhostEntities[ newEnt[3] ];

				if (!existingEnt)
				{
					// allow for ghost -> real
					existingEnt = existingEntities[ newEnt[3] ];
					if (!existingEnt)
					{
						continue;
					}
				}
				dx = newEnt[0] - existingEnt[0];
				dy = newEnt[1] - existingEnt[1];

				existingEnt.splice( 4, 4, existingEnt[0], existingEnt[1], dx, dy );
				// console.log("ent %d: %d, %d: ", newEnt[3], dx, dy, existingEnt );
			}
		}
	},


	_copyRect: function( /*Object*/ rect )
	{
		return {
			minX: rect.minX,
			minY: rect.minY,
			maxX: rect.maxX,
			maxY: rect.maxY,
		};
	},


	/**
	*   Scale passed rect proportionately in each dimension by passed magnitude.
	*   Values > 1 enlargen rect, values 0-1 shrink rect.
	*/
	_scaleRect: function( /*Object*/ rect, /*float*/ mag )
	{
		mag = (mag - 1) / 2;
		var dx = (rect.maxX - rect.minX) * mag;
		var dy = (rect.maxY - rect.minY) * mag;

		rect.minX -= dx;
		rect.minY -= dy;
		rect.maxX += dx;
		rect.maxY += dy;
	},


	/**
	*   Returns a new rect representing the intersection of the passed 2 rects
	*   or null if rects do not intersect.
	*/
	_intersectRect: function( /*Object*/ rect1, /*Object*/ rect2 )
	{
		if (!rect1 || !rect2)
		{
			console.dir( arguments );
			throw new Error( "Null rect" );
		}

		// test for intersection
		if (rect1.minX > rect2.maxX ||
			rect1.maxX < rect2.minX ||
			rect1.minY > rect2.maxY ||
			rect1.maxY < rect2.minY)
		{
			return null;
		}

		// else rects do intersect
		return {
			minX: Math.max( rect1.minX, rect2.minX ),
			minY: Math.max( rect1.minY, rect2.minY ),
			maxX: Math.min( rect1.maxX, rect2.maxX ),
			maxY: Math.min( rect1.maxY, rect2.maxY ),
		};
	},
};


SV.SpaceViewSurface.prototype.perfGraph = function( divSelector, divContainer )
{
	var div = jQuery( divSelector, divContainer );
	if (div.length === 0)
		console.error( "No div found by selector '%s'", divSelector );

	div.show();
	div.parents().show();

	this._frame = 0;
	var cnv = jQuery('<canvas/>').appendTo( div ).get( 0 );
	var ctx = cnv.getContext('2d');
	ctx.lineWidth = 1;

	var w = 200, h = 60, d = 1;
	cnv.height = h;
	cnv.width = w;

	var advance = function()
	{
		ctx.putImageData( ctx.getImageData( 1, 0, w, h ), 0, 0 );
	};

	var drawLine = function( value, lastValue, colour )
	{
		value = Math.min( (value || 0), h );
		lastValue = Math.min( (lastValue || 0), h );
		ctx.strokeStyle = colour || 'red';

		ctx.beginPath();
		ctx.moveTo( w - 2, h - lastValue );
		ctx.lineTo( w - 1, h - value );
		ctx.stroke();
	};

	var drawVerticalMarker = function( value, colour )
	{
		value = Math.min( (value || 0), h - 1 );
		ctx.strokeStyle = colour || 'blue';
		ctx.beginPath();
		if (value > 0)
		{
			ctx.moveTo( w - 2, value );
			ctx.lineTo( w - 2, 0 );
		}
		else
		{
			ctx.moveTo( w - 2, h + value - 1 );
			ctx.lineTo( w - 2, h - 1 );
		}
		ctx.stroke();
	};

	var last = {};

	jQuery( this ).on({
		'draw.sv': function()
		{
			drawLine( this._frameTime, last.frameTime, 'rgba( 255, 0, 0, 0.75 )' );
			last.frameTime = this._frameTime;

			var now = Date.now();
			var fps = 1000 / (now - last.draw);

			drawLine( fps, last.fps, 'rgba( 220, 0, 200, 0.65 )' );
			last.draw = now;
			last.fps = fps;

			if (this.tileset && this.tileset.tileQueue)
			{
				drawLine( this.tileset.tileQueue.length, last.qLength, 'rgba( 0, 60, 0, 0.65 )' );
				last.qLength = this.tileset.tileQueue.length;
			}

			advance();
		},

		'tileZoomChange.sv': function()
		{
			drawVerticalMarker( -20, 'rgba( 0, 0, 200, 0.75 )' );
			advance();
		},

		'loadTile.sv': function()
		{
			drawVerticalMarker( 20, 'rgba( 0, 150, 0, 0.65 )' );
			// advance();
		},

		'unloadTile.sv': function()
		{
			drawVerticalMarker( -10, 'rgba( 0, 50, 0, 0.6 )' );
			// advance();
		},

		'requestUpdate.model.sv': function()
		{
			drawVerticalMarker( -5, 'rgba( 0, 0, 0, 0.25 )' );
		},
	});
};


SV.SpaceViewSurface.prototype._blankCanvas =
	UI.spaceBackgroundImage.canvasClearRectIsFaster ?
		SV.SpaceViewSurface.prototype._blankCanvasClearRect :
		SV.SpaceViewSurface.prototype._blankCanvasSetWidth;


SV.SpaceViewSurface.prototype._initLoadBalanceStatus = function()
{
	// init dom elments
	this.loadBalancePanel = jQuery( "#load-balance-panel" );
	
	// update load balance setting panel with default value
	this._updateLoadBalancePanel();

	// init dom events
	this.loadBalancePanel.find( "input:radio[name=server_load_balancing]" ).
		change( function( ev )
		{
			this._updateSvrLoadBalance( ev.target.value );	
		}.bind( this ) );

	this.loadBalancePanel.find( "input:radio[name=meta_load_balancing]" ).
		change( function( ev )
		{
			this._updateMetaLoadBalance( ev.target.value );	
		}.bind( this ) );

	this.loadBalancePanel.find( "input:radio[name=manual_load_balancing]" ).
		change( function( ev )
		{
			this._updateManualLoadBalance( ev.target.value );	
		}.bind( this ) );

	// get load balance related status from server 
	this._getLoadBalanceStatus();
};

SV.SpaceViewSurface.prototype._retireCell = function( /*Object*/ cell )
{
	var path = this._getCellWatcherPath( cell );
	if (path != null)
	{
		path += "isRetiring";
		this._setCellAppMgrWatcher( path, "True" );
	}
	else
	{
		console.error( "Failed to compose watcher path of cell:" + cell.appID );
	}
};


SV.SpaceViewSurface.prototype._cancelRetiringCell = function( /*Object*/ cell )
{
	var path = this._getCellWatcherPath( cell );
	if (path != null)
	{
		path += "isRetiring";
		this._setCellAppMgrWatcher( path, "False" );
	}
	else
	{
		console.error( "Failed to compose watcher path of cell:" + cell.appID );
	}
};


SV.SpaceViewSurface.prototype._splitCell = function( /*Object*/ cell )
{
	var path = this._getCellWatcherPath( cell );
	if (path != null)
	{
		path += "isLeaf";
		this._setCellAppMgrWatcher( path, "False" );
	}
	else
	{
		console.error( "Failed to compose watcher path of cell:" + cell.appID );
	}
};


SV.SpaceViewSurface.prototype._updateSvrLoadBalance =
function( /*String*/ value )
{
	var watcherValue = "False";

	if (value == "enabled")
	{
		watcherValue = "True"
	}

	this._setCellAppMgrWatcher( "debugging/shouldLoadBalance",
								watcherValue,	
								this._getLoadBalanceStatus );
};


SV.SpaceViewSurface.prototype._updateMetaLoadBalance =
function( /*String*/ value )
{
	var watcherValue = "False";

	if (value == "enabled")
	{
		watcherValue = "True"
	}

	this._setCellAppMgrWatcher( "debugging/shouldMetaLoadBalance",
								watcherValue,	
								this._getLoadBalanceStatus );
};


SV.SpaceViewSurface.prototype._updateManualLoadBalance =
function( /*String*/ value )
{
	if (value == "enabled")
	{
		this.manualLoadBalanceEnabled = true;
	}
	else
	{
		this.manualLoadBalanceEnabled = false;
	}

	this.draw();
};


SV.SpaceViewSurface.prototype._getLoadBalanceStatus =function()
{
	jQuery.ajax( {
		url: "getLoadBalanceStatus",
		context: this,
		dataType: "json",
		success: this._updateLoadBalanceStatus.bind(this)
	} );
};


SV.SpaceViewSurface.prototype._updateLoadBalanceStatus =
function( /*Object*/ data )
{
	this.svrLoadBalanceEnabled = data.svrLoadBalanceEnabled;
	this.metaLoadBalanceEnabled = data.metaLoadBalanceEnabled;
	this.isProductionMode = data.isProductionMode;

	this._updateLoadBalancePanel();
}


SV.SpaceViewSurface.prototype._updateLoadBalancePanel = function()
{
	if (this.isProductionMode)
	{
		this.loadBalancePanel.addClass( "production-mode" );
		this.loadBalancePanel.find( "input:radio" ).prop( "disabled", 
															"disabled" );
	}
	else
	{
		this.loadBalancePanel.removeClass( "production-mode" );
		this.loadBalancePanel.find( "input:radio" ).removeProp( "disabled" );
	}

	this._updateRadioButton( this.loadBalancePanel,
							"server_load_balancing",
							this.svrLoadBalanceEnabled );

	this._updateRadioButton( this.loadBalancePanel,
							"meta_load_balancing",
							this.metaLoadBalanceEnabled );

	this._updateRadioButton( this.loadBalancePanel,
							"manual_load_balancing",
							this.manualLoadBalanceEnabled );
};


SV.SpaceViewSurface.prototype._updateRadioButton =
function( /*Object*/container, /*String*/ radioName, /*Boolean*/ value )
{
	var selector = "input:radio[name=" + radioName + "][value=";

	if (value)
	{
		selector += "enabled]";
	}
	else
	{
		selector += "disabled]"
	}
	
	jQuery( selector ).prop( "checked", true );
};


SV.SpaceViewSurface.prototype._updateSvrPartitionPos =
function( /*Object*/ partition, /*number*/ worldPos )
{
	var watcherPath = this._getPartitionWatcherPath( partition );

	if (watcherPath)
	{
		watcherPath += "position";	
		this._setCellAppMgrWatcher( watcherPath,
									worldPos,
									this._refreshSpaceData );
	}
	else
	{
		console.warn("Couldn't find watcher path. Probably partition changed");
	}
};


// this is to refresh space viewer data after dragging partition
SV.SpaceViewSurface.prototype._refreshSpaceData = function()
{
	var jqXHR = this.requestModelUpdate( true );

	// clear the drag partition state after request returns
	jqXHR.always( function()
	{		
		if (!this.dragState && this.dragPartition)
		{
			this.dragPartition = null;
			
			// force to draw the new data, otherwise the partition line
			// may bounce
			this._nextData = null;
		}
	}.bind(this) );

};


SV.SpaceViewSurface.prototype._setCellAppMgrWatcher =
function( /*String*/ path, /*String*/ value, /*Function*/ callback )
{
	var _this = this; //save this for callback function	

	jQuery.ajax( {
		url: "setCellAppMgrWatcher",
		context: this,
		data: {	'path': path, 'value': value },
		dataType: 'json',
		success: function( /*Object*/ data, /*String*/ textStatus, jqxhr )
		{
			if (SV.debug)
			{
				console.log( "Set watcher %s successfully", data.path );
			}

			if (typeof callback !== 'undefined')
			{
				callback.call( _this, data );
			}
		},
	} );
};


SV.SpaceViewSurface.prototype._getCellAppMgrWatcher =
function( /*String*/ path, /*Function*/ callback )
{
	var _this = this; //save this for callback function	

	jQuery.ajax( {
		url: "getCellAppMgrWatcher",
		context: this,
		data: {	'path': path },
		dataType: 'json',
		success: function( /*Object*/ data, /*String*/ textStatus, jqxhr )
		{
			if (SV.debug)
			{
				console.log( "Got watcher %s : %s ", data.path,	data.value );
			}

			if (typeof callback !== 'undefined')
			{
				callback.call( _this, data );
			}
		},
	} );
};


// compose the watcher path of certain cell, starting from root
SV.SpaceViewSurface.prototype._getCellWatcherPath =
function( /*Object*/ node, /*?Object*/root, /*?String*/ path )
{
	if (root===undefined)
	{
		root = this.data.root;
		path = "spaces/" + this.spaceId + "/bsp/";
	}

	if (root.isHorizontal !== undefined)
	{
		var newPath = this._getCellWatcherPath( node, root.left, 
												path + "left/" );
		if (newPath != null)
		{
			return newPath;
		}

		newPath = this._getCellWatcherPath( node, root.right, 
											path + "right/" );
		if (newPath != null)
		{
			return newPath;
		}
	}
	else if (node.appID == root.appID)
	{
		return path; 
	}

	return null;
};


// compose the watcher path of certain cell, starting from root
SV.SpaceViewSurface.prototype._getPartitionWatcherPath =
function( /*Object*/ partition, /*?Object*/root, /*?String*/ path )
{
	if (root===undefined)
	{
		root = this.data.root;
		path = "spaces/" + this.spaceId + "/bsp/";
	}

	if (root.isHorizontal !== undefined)
	{
		// node is a partition
		if (root.bspId == partition.bspId)
		{
			return path;
		}

		var newPath = this._getPartitionWatcherPath( partition, root.left,
												path + "left/" );
		if (newPath != null)
		{
			return newPath;
		}

		newPath = this._getPartitionWatcherPath( partition, root.right,
											path + "right/" );
		if (newPath != null)
		{
			return newPath;
		}
	}
	else
	{
		// node is a cell
		return null; 
	}

};


SV.SpaceViewSurface.prototype._partitionAt =
function( /*number*/ worldX, /*number*/ worldY )
{
	// allowed select delta in world distance
	var delta = ( ( UI.partitionLine.selectDelta / this.canvas.width )
				* this.xPageSize )

	for (var i in this.partitions)
	{
		var partition = this.partitions[ i ];
		var rect = partition.worldRect;

		if (!rect)
		{
			// this could happen after update data but before draw
			return;
		}

		if( partition.isHorizontal )
		{
			if (Math.abs( partition.position - worldY ) <= delta 
				&& worldX >= rect.minX
				&& worldX <= rect.maxX)
			{	
				return partition;
			}
		}
		else
		{
			if (Math.abs( partition.position - worldX ) <= delta
				&& worldY >= rect.minY
				&& worldY <= rect.maxY)
			{
				return partition;
			}
		}
	}
};


SV.SpaceViewSurface.prototype._isDraggedPartition =
function( /*Object*/ partition )
{
	if (this.dragPartition)
	{
		var draggedPartition = this.dragPartition.partition;

		if (partition.bspId == draggedPartition.bspId
			&& partition.isHorizontal == draggedPartition.isHorizontal)
		{
			return true;
		}
	}
	
	return false;
};


// check whether the mouse is currently over any partition
SV.SpaceViewSurface.prototype._checkOverPartition =
function( /*number*/ canvasX, /*number*/ canvasY)
{
	if (this.dragState && this.dragPartition)
	{
		// dragging, return
		return;
	}
	
	if (canvasX < 0 || canvasY < 0)
	{
		// mouse is out of canvas, return
		this._clearOverPartition();
		return;
	}

	var worldX = this.convertScreenToWorldX ( this.mousePos.x );
	var worldY = this.convertScreenToWorldY ( this.mousePos.y );
	var partition = this._partitionAt( worldX, worldY );

	if (partition)
	{
		this._addOverPartition( partition );
		return true;
	}
	else
	{
		this._clearOverPartition();
		return false;
	}
};


SV.SpaceViewSurface.prototype._addOverPartition = function( partition )
{
	if (partition.isHorizontal)
	{
		this.dom.container.removeClass( "dragging-vertical" );
		this.dom.container.addClass( "dragging-horizontal" );
	}
	else
	{
		this.dom.container.removeClass( "dragging-horizontal" );
		this.dom.container.addClass( "dragging-vertical" );
	}
};


SV.SpaceViewSurface.prototype._clearOverPartition = function()
{
	this.dom.container.removeClass( "dragging-horizontal" );
	this.dom.container.removeClass( "dragging-vertical" );
};


SV.SpaceViewSurface.prototype._checkMouseOverCellMenu = function()
{
	for (var i in this.cells)
	{
		if (this._isMouseOverCellMenu( this.cells[ i ]))
		{
			this.dom.container.addClass( "over-cell-menu" );
			return true;
		}
	}

	this.dom.container.removeClass( "over-cell-menu" );
	return false;
};


SV.SpaceViewSurface.prototype._clearOverCellMenu = function()
{
	this.dom.container.removeClass( "over-cell-menu" );
};


SV.SpaceViewSurface.prototype._isUnderMouse=
function( /*Object*/ partition )
{
	if (!partition || partition.screenPosition === undefined
		|| this.mousePos.x < 0 )
	{
		return false;
	}

	var rect = partition.screenRect;

	if (!rect)
	{
		// this could happen after update data but before draw
		return false;
	}

	var partitionPos = partition.screenPosition;
	var mouseX = this.mousePos.x;
	var mouseY = this.mousePos.y;
	var delta = UI.partitionLine.selectDelta;

	if( partition.isHorizontal )
	{
		if (Math.abs( mouseY - partitionPos ) <= delta 
			&& mouseX >= rect.minX
			&& mouseX <= rect.maxX)
		{	
			return true ;
		}
	}
	else
	{
		if (Math.abs( mouseX - partitionPos ) <= delta
			&& mouseY >= rect.minY
			&& mouseY <= rect.maxY)
		{
			return true;
		}
	}

	return false;
};


SV.SpaceViewSurface.prototype._drawMenuIcon = function()
{
	if (!this.manualLoadBalanceEnabled)
	{
		return;
	}

	for (var i in this.cells )
	{	
		var cell = this.cells[ i ];

		if (this._isMouseOverCellMenu( cell ) )
		{
			this._doDrawMenuIcon( cell, this.menuIconClickableImg );	
		}
		else if (this._isMouseOverCell( cell ) )
		{
			this._doDrawMenuIcon( cell, this.menuIconImg);	
		}
	}
};


SV.SpaceViewSurface.prototype._doDrawMenuIcon =
function( /*Object*/ cell, /*Object*/ img )
{
	var rect = cell.screenRect;

	if (!rect)
	{
		// cell is probably not visible
		return;
	}
	
	var offset = UI.menuIcon.offset;
	var x = rect.maxX - img.width - offset;
	var y = rect.minY + offset;

	this.context.drawImage( img, x, y );
};


// check whether menu icon should be drawn for this cell
SV.SpaceViewSurface.prototype._isMouseOverCell =
function( /*Object*/ cell)
{
	if (!this.manualLoadBalanceEnabled || !cell)
	{
		return false;
	}

	var rect = cell.screenRect;

	if (!rect)
	{
		// cell is not visible
		return false;
	}

	if (this.mousePos.x >= rect.minX && this.mousePos.x <= rect.maxX
		&& this.mousePos.y >= rect.minY && this.mousePos.y <= rect.maxY)
	{
		return true;
	}

	return false;
};


// check whether the mouse is currently over the menu icon of this cell 
SV.SpaceViewSurface.prototype._isMouseOverCellMenu =
function( /*Object*/ cell)
{
	if (!this.manualLoadBalanceEnabled || !cell)
	{
		return false;
	}

	var rect = cell.screenRect;

	if (!rect)
	{
		// cell is not visible
		return false;
	}

	var maxX = rect.maxX - UI.menuIcon.offset;
	var minX = maxX - this.menuIconImg.width; 
	var minY = rect.minY + UI.menuIcon.offset;
	var maxY = minY + this.menuIconImg.height;

	if (this.mousePos.x >= minX && this.mousePos.x <= maxX
		&& this.mousePos.y >= minY && this.mousePos.y <= maxY)
	{
		return true;
	}

	return false;
};


SV.SpaceViewSurface.prototype._drawRetiringEffect =
function( /*object*/ cell )
{
	if (!cell || !cell.screenRect)
	{
		console.warn( "Invalid cell data" );
		return;
	}
	
	var ctx = this.context;
	ctx.save();

	this.setStyle( UI.retiringCell );	

	var rect = cell.screenRect;
	var x = rect.minX;
	var y = rect.minY;
	var width = rect.maxX - rect.minX;
	var height = rect.maxY - rect.minY;
	
	ctx.fillRect( x, y, width, height );	

	ctx.restore();
};

// spaceviewer_canvas.js

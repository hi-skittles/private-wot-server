
if (!SV || !SV.SpaceViewSurface)
{
	throw new Error(
		"SV.MiniMap requires SV.SpaceViewSurface to be loaded before this class"
	);
}


SV.DEFAULT_MINIMAP_OPTIONS =
{
	div: '#minimap',
	entityTypes: {},
	animation: false,
	mouseEvents: false,
	keyboardEvents: false,
};


UI.minimap = UI.minimap || {
    enabled: true,
	showGuides: false,

	// style of the main viewport rect drawn on minimap
	fillStyle: 'rgba( 0, 51, 255, 0.25 )',
	strokeStyle: 'rgb( 0, 51, 255 )',
	lineWidth: 1,

	// style of selected cell rect drawn on minimap
	selectedCell: {
		fillStyle: 'rgba( 0, 0, 0, 0.2 )',
		strokeStyle: 'rgba( 0, 0, 0, 0.5 )',
	}
};


SV.MiniMap = function( /*SpaceViewSurface*/ s, /*Map*/ options )
{
	var opts = jQuery.extend( true, {}, SV.DEFAULT_MINIMAP_OPTIONS, options );
	SV.SpaceViewSurface.call( this, s.spaceId, opts );
	this.parentSpaceViewer = s;

	jQuery( this.canvas ).on({

		mousedown: function( ev )
		{
			this._deriveCanvasCoords( ev );
			var worldX = this.convertScreenToWorldX( ev.canvasX, false );
			var worldY = this.convertScreenToWorldY( ev.canvasY, false );

			this.parentSpaceViewer.centreViewAt( worldX, worldY, true );
			this.dragState = true;

			return false;
		}
		.bind( this ),

		mousemove: function( ev )
		{
			if (this.dragState)
			{
				this._deriveCanvasCoords( ev );
				var worldX = this.convertScreenToWorldX( ev.canvasX, false );
				var worldY = this.convertScreenToWorldY( ev.canvasY, false );

				this.parentSpaceViewer.centreViewAt( worldX, worldY, false );
			}
			return false;
		}
		.bind( this ),

		mouseup: function( ev )
		{
			this.dragState = false;
			return false;
		}
		.bind( this ),

		mousewheel: function( ev, delta, deltaX, deltaY )
		{
			var s = this.parentSpaceViewer;
			s.zoom(
				s.canvas.width / 2,
				s.canvas.height / 2,
				Math.pow( 1.1, deltaY ),
				false
			);

			return false;
		}
		.bind( this ),
	});

	jQuery( this.parentSpaceViewer ).on({

        // shallow copy parent's data for each new data frame
		'updateModel.sv': function( ev )
		{
			var firstUpdate = !this.data;
			var parentSv = this.parentSpaceViewer;

			this.data = parentSv.data;
			this.entityTypes = parentSv.entityTypes;

			if (firstUpdate)
			{
				this.backgroundImage = parentSv.backgroundImage;
				this.rescaleWindow();
				this.zoomToSpaceBounds( false );
			}
		}
		.bind( this ),

		'tilesetChange.sv': function()
		{
			this.tileset = this.parentSpaceViewer.tileset;
			this.draw();
		}
		.bind( this ),

		'loadTile.sv': function( ev, tileId )
		{
			if (tileId === '0:0:0')
			{
				this.draw();
			}
		}
		.bind( this ),

		// redraw only on a viewport change
		'viewportChange.sv': function( ev )
		{
		    if (!UI.minimap.enabled)
		        return;

			var s = this.parentSpaceViewer;
			var svHeight = Math.abs( s.convertScreenToWorldDist( 0, s.canvas.height ).y );
			var miniHeight = Math.abs( this.convertScreenToWorldDist( 0, this.canvas.height ).y );

			// if viewport is larger than spacebounds then fade out minimap div
			if ((s.xPageSize * 1.1 < this.xPageSize) || (svHeight * 1.1 < miniHeight))
			{
				jQuery( '.sv-minimap', s.dom.container ).fadeIn( 250 );
			}
			else
			{
				jQuery( '.sv-minimap', s.dom.container ).fadeOut( 750 );
				return;
			}

			this.draw();
		}
		.bind( this ),

		// redraw when a new cell is selected or the parent is redrawn
		'changeSelectedCell.sv draw.sv': this.draw.bind( this ),
	});
};


// class SV.MiniMap extends SV.SpaceViewSurface
SV.MiniMap.prototype = new SV.SpaceViewSurface;
SV.MiniMap.prototype.constructor = SV.SpaceViewSurface;


/** Overridden from SV.SpaceViewSurface.draw */
SV.MiniMap.prototype.draw = function()
{
	if (!this.data || !UI.minimap.enabled)
		return;

	var s = this.parentSpaceViewer;
	var bounds = s.getScreenBounds();

	var ctx = this.context;
	var w = this.canvas.width;
	var h = this.canvas.height;

	this._blankCanvas();
	this.drawBackground();

	// draw selected cell rect, if any
	if (s.cells && s.cells.length > 1)
	{
		var sc = s.getSelectedCell();
		if (!sc.worldRect)
		{
			// no world rect calculated means we've likely been called in between
			// a draw and an update, ie: the BSP of the incoming data tick has
			// not yet been traversed and had its worldRect calculated.
			return;
		}

		var viewableSelectedCellRect = 
			this._intersectRect( sc.worldRect, this.getScreenBounds() );

		if (!viewableSelectedCellRect)
		{
			// cell does not intersect spacebounds, which means it is
			// off the minimap, so draw nothing
			return;
		}

		ctx.save();
		this.setStyle( UI.minimap.selectedCell );
		this.drawRect( viewableSelectedCellRect );
		ctx.restore();
	}


	ctx.save();
	this.setStyle( UI.minimap );
	var b = this.convertWorldToScreenRect( bounds );

	if (UI.minimap.showGuides || (b.maxX - b.minX) < 10 /*pixels*/)
	{
		ctx.beginPath();
		ctx.moveTo( b.minX, 0 );
		ctx.lineTo( b.minX, h );

		ctx.moveTo( b.maxX, 0 );
		ctx.lineTo( b.maxX, h );

		ctx.moveTo( 0, b.minY );
		ctx.lineTo( w, b.minY );

		ctx.moveTo( 0, b.maxY );
		ctx.lineTo( w, b.maxY );

		ctx.stroke();
		ctx.fillRect(
			b.minX, b.minY,
			b.maxX - b.minX, b.maxY - b.minY
		);
	}
	else
	{
		this.drawRect( bounds );
	}

	ctx.restore();
};


// spaceviewer_minimap.js


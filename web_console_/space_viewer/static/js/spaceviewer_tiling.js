"use strict";

// check for required libs
if (!jQuery)
{
	throw new Error(
		"jQuery is not defined. this class requires jquery"
	);
}

if (!SV || !SV.SpaceViewSurface)
{
	throw new Error(
		"SV.SpaceViewSurface is not defined (have you loaded spaceviewer_canvas.js?)"
	);
}

if (!ChainLoader || !ChainLoader.Image)
{
	throw new Error(
		"ChainLoader.Image is not defined (have you loaded chainloader.js?)"
	);
}


/* Configuration */
SV.debugTiling = 0;

// resolution difference of tiles between zoom levels
var TILE_DIV = 2;

// number of source (tile) pixels in horizontal dimension at which
// canvas/render performance begins to degrade. this value is
// browser/platform-specific.
var browserTilePixelLimit = 4000; // px

// add tiling config to default spaceviewer UI config
UI.spaceBackgroundTileLayer = UI.spaceBackgroundTileLayer ||
{
	enabled: true,

	// added to zoomLevel; allows manual forcing of zoom level up/down
	zoomLevelAdjust: 0,

	// working lower limit of tile cache
	// note: this should be *at least* the max number of tiles that may
	// be viewable on-screen at one time for any zoomLevel.
	minTileCacheSize: 16, // tiles

	// working upper limit of tile cache
	// note: tile cache may (temporarily) grow beyond maxTileCacheSize
	// for up to minTimeBeforeExpiry seconds.
	maxTileCacheSize: 32, // tiles

	// time since a tile was loaded before it will be considered for unloading
	minTimeBeforeExpiry: 2000, // msec
};


SV.OPTIONS.postInitHooks.push(

	/** Add tiling-related event hooks */
	function()
	{
		this._tileBaseurl = '/sv/resources/';

		this.tileLoader = new ChainLoader.Image({
			numConcurrentJobs: 3,
			delay: 15,
			// debug: 1,
		});

		// load tileset after 1 frame of data
		jQuery( this ).one( 'updateModel.sv', this.requestTileSet );

		// preload tiles for the end state of a viewport animation
		// (eg: animated zoom/pan/zooToRect).
		this._initPreloadTilesOnAnimation();

		// jQuery( this ).on( 'tileZoomChange.sv', this._stopLoadingUneededTiles );

		// if debugging, report tile:screen pixel ratio
		if (jQuery('.sv-debug .tiling:visible', this.dom.container).length)
		{
			jQuery( this ).on( 'viewportChange.sv tileZoomChange.sv', function()
			{
				if (!this.tileset) return;

				var pixPerMetre = this.tileset.rootTilePpm
						* Math.pow( TILE_DIV, this.tileZoomLevel );

				var numTilePixels = this.xPageSize * pixPerMetre;
				var tileToScreenPixelRatio = numTilePixels / this.canvas.width;

				jQuery('.sv-debug .tiling:visible', this.dom.container ).html(
					'zoomLevel: ' + this.tileZoomLevel +
					' (' + pixPerMetre.toFixed( 3 ) + ' px/m)' +
					'<br/>' +
					'tile/screen: ' + tileToScreenPixelRatio.toFixed( 3 ) +
					' (' + numTilePixels.toFixed() + ' px/' +
					this.canvas.width.toFixed() + ' px)' +
					'<br/>' +
					'<a href="#" onclick="SV.debugTiling++">debug++</a>/' +
					'<a href="#" onclick="SV.debugTiling=0">debug--</a>'
				);
			});
		}
	}
);


/* Implementation */

/** Redefines the base drawBackground */
SV.SpaceViewSurface.prototype.drawBackgroundBasic = SV.SpaceViewSurface.prototype.drawBackground;


/**
*	Proxy the basic drawBackground method to add the high-res background
*	drawing path.
*/
SV.SpaceViewSurface.prototype.drawBackground = function()
{
	var tilesEnabled = UI.spaceBackgroundImage.enabled &&
						UI.spaceBackgroundTileLayer.enabled;

	var tilesReady = !!this.tileset;

	if (!tilesEnabled || !tilesReady)
	{
		this.drawBackgroundBasic();
		return;
	}

	this.drawBackgroundFromTiles();
};


/**
*	Draw a high-resolution space background into the current 2D context
*	using a pre-generated, high-res tile service with dynamic loading/unloading.
*/
SV.SpaceViewSurface.prototype.drawBackgroundFromTiles =
function( /*rect*/ worldRect, /*int*/ zoomLevel )
{
	// console.time( 'tiles' );
	worldRect = worldRect || this.getScreenBounds();
	zoomLevel = zoomLevel >= 0 ? zoomLevel : this.getTileZoomLevel();

	var ctx = this.context;
	var sb = this.getSpaceBounds();

	// bounding rect of tile imagery intersected with spacebounds
	var tilesetWorldBounds = this.tileset.spaceBounds;
	var tilesetScreenBounds = this.convertWorldToScreenRect( tilesetWorldBounds );

	// if spacebounds exceeds tileset bounds, draw space boundary
	// first, and layer tiles over it
	if (sb.minX < tilesetWorldBounds.minX ||
		sb.maxX > tilesetWorldBounds.maxX ||
		sb.minY < tilesetWorldBounds.minY ||
		sb.maxY > tilesetWorldBounds.maxY )
	{
		this.setStyle( UI.spaceBackgroundImage );
		this.drawRect( sb );
	}

	var tileRect = this.getTileRect( worldRect, zoomLevel );
	if (!tileRect)
	{
		// no portion of spacebounds is visible in current viewport,
		// so no need to draw anything.
		return;
	}

	var now = +new Date;
	var tileMap = this.tileset.tileCache;
	var tileSize = this.tileset.tileSize;

	for (var tileY = tileRect.minY; tileY <= tileRect.maxY; tileY++ )
	{
		for (var tileX = tileRect.minX; tileX <= tileRect.maxX; tileX++ )
		{
			var tileWorldRect = this.convertTileToWorldRect( zoomLevel, tileX, tileY );
			var tileScreenRect = this.convertWorldToScreenRect( tileWorldRect );

			// clip tiles (which may be black padded) to space and tile bounds
			var destRect = this._intersectRect( tileScreenRect, tilesetScreenBounds );

			// project dest screen rect to tile rect to derive source image rect
			var scale = tileSize / (tileScreenRect.maxX - tileScreenRect.minX);
			var srcRect = {
				minX: (destRect.minX - tileScreenRect.minX) * scale,
				minY: (destRect.minY - tileScreenRect.minY) * scale,
				maxX: (destRect.maxX - tileScreenRect.minX) * scale,
				maxY: (destRect.maxY - tileScreenRect.minY) * scale,
			};

			var tileId = zoomLevel + ":" + tileX + ":" + tileY;
			var tile = tileMap[ tileId ];

			if (tile && tile.image)
			{
				// tile already loaded
				this._drawTile( tile, srcRect, destRect );
				tile.lastUsed = now;
			}
			else
			{
				// tile image has not been loaded
				if (!this.viewportAnimation || !this.viewportAnimation.inProgress)
				{
					this.requestLoadTile( zoomLevel, tileX, tileY );
				}

				// fallback: use pixels from next best already-loaded tile
				// while waiting for async load to complete. while it's
				// possible to elegantly handle this situation by calling this
				// function recursively, ie:
				//   this.drawBackgroundFromTiles( tileWorldRect, zoomLevel - 1 );
				//   continue;
				// however, the performance sucks and causes too many frame time spikes.

				// walk up tile tree hierarchy looking for tiles that are in the
				// active tile cache; if found, derive from it the tile rect
				// corresponding to the pixels we need, and then draw.
				for (var z = zoomLevel - 1; z >= 0; z-- )
				{
					var p = zoomLevel - z;
					var parentTileId = z + ":" + (tileX >> p) + ":" + (tileY >> p);
					var parentTile = tileMap[ parentTileId ];
					if (parentTile && parentTile.image)
					{
						var relSize = Math.pow( TILE_DIV, zoomLevel - z );
						var parentTileSize = tileSize / relSize;
						var offsetX = (tileX - (tileX >> p) * relSize) * parentTileSize;
						var offsetY = (tileY - (tileY >> p) * relSize) * parentTileSize;
						srcRect = {
							minX: offsetX + srcRect.minX / relSize,
							minY: offsetY + srcRect.minY / relSize,
							maxX: offsetX + srcRect.maxX / relSize,
							maxY: offsetY + srcRect.maxY / relSize,
						};

						this._drawTile( parentTile, srcRect, destRect, true );
						break;
					}
				}

				if (!parentTile || !parentTile.image)
				{
					// no parent tiles, not even root tile, so request
					// root tile immediately. This should only ever happen if
					// tile cache has been forcibly flushed manually - root tile
					// is special-cased to never be unloaded in the general case.
					this.requestLoadTile( 0, 0, 0, true );
				}
			}
		} // for tileX
	} // for tileY

	this.tileLoader.load();

	var tileZoomChanged = (this.tileZoomLevel != zoomLevel);
	this.tileZoomLevel = zoomLevel;
	if (tileZoomChanged)
	{
		jQuery( this ).trigger( 'tileZoomChange.sv', zoomLevel );
	}

	// console.timeEnd( 'tiles' );
};


SV.SpaceViewSurface.prototype._drawTile = function( tile, srcRect, destScreenRect, isFallbackTile )
{
	var ctx = this.context;

	// round to precise rects to avoid seaming
	// note: rounding of srcRect only needed on Firefox 16 and
	// only with hardware accel on
	var sx = Math.round( srcRect.minX );
	var sy = Math.round( srcRect.minY );
	var sw = Math.round( srcRect.maxX ) - sx;
	var sh = Math.round( srcRect.maxY ) - sy;

	var dx = Math.round( destScreenRect.minX );
	var dy = Math.round( destScreenRect.minY );
	var dw = Math.round( destScreenRect.maxX ) - dx;
	var dh = Math.round( destScreenRect.maxY ) - dy;

	if (SV.debugTiling > 1)
	{
		console.log(
			"drawing from tile %s [%f, %f, %f, %f] " +
			"to screen rect [%f, %f, %f, %f]",
			tile.id,
			sx, sy, sx + sw, sy + sh,
			dx, dy, dx + dw, dy + dh
		);
	}

	ctx.drawImage(
		tile.image,
		sx, sy, sw, sh,
		dx, dy, dw, dh
	);

	if (SV.debugTiling)
	{
		ctx.save();
		ctx.fillStyle = ctx.strokeStyle = (isFallbackTile ? 'red' : 'orange');
		ctx.font = 'bold 12px Arial';
		ctx.strokeRect( dx, dy, dw, dh );
		ctx.fillText( tile.id, dx + 5, dy + 15 );

		ctx.restore();
	}
};


SV.SpaceViewSurface.prototype.requestTileSet = function()
{
	if (!this.spaceName)
	{
		console.warn( "No space name; can't request tileset" );
		return;
	}

	var url = this._tileBaseurl + this.spaceName + "/space_viewer/tileset/tileset.json";
	if (SV.debug || SV.debugTiling)
	{
		console.log( "loading tileset: %s", url );
	}

	jQuery.ajax({
		url: url,
		cache: false, // force chrome to issue request
		dataType: 'json',
		success: this.initTileSet.bind( this ),
		error: function( jqXhr, status, ex )
		{
			console.log( "Couldn't load tileset: ", url );
			new Alert.Warning( "No tileset available for space<br/>" +
				'See <a href="help">help page</a> for further information' );
		}
		.bind( this )
	});
};


SV.SpaceViewSurface.prototype.initTileSet = function( tileset )
{
	var rt = tileset.worldBoundsOfRootTile;

	// sanity checks
	if (!rt)
	{
		console.error(
			"Tileset config at %s missing required object '%s'",
			url, 'worldBoundsOfRootTile' );
	}
	if (!(rt.minX < rt.maxX) || !(rt.minY < rt.maxY))
	{
		console.error(
			"Tileset config at %s has invalid values for '%s', should be %s",
			url, 'worldBoundsOfRootTile',
			'{ "minX": <float>, "maxX": <float>, "minY": <float>, "maxY": <float> }'
		);
	}
	if (!(tileset.depth >= 0))
	{
		console.error(
			"Tileset config at %s missing required int value for '%s'",
			url, 'depth' );
	}
	if (!(tileset.tileSize > 0))
	{
		console.error(
			"Tileset config at %s missing required int value for '%s'",
			url, 'tileSize' );
	}

	// calc pixels per metre of root tile
	tileset.rootTilePpm = tileset.tileSize / (rt.maxX - rt.minX);

	var sb = this.getSpaceBounds();
	sb = tileset.spaceBounds = this._intersectRect( sb, rt );

	if (tileset.worldBoundsOfSpaceGeometry)
	{
		sb = tileset.spaceBounds = this._intersectRect( sb, tileset.worldBoundsOfSpaceGeometry );
	}

	if (SV.debug || SV.debugTiling)
	{
		console.log(
			"tileset: size=%i, depth=%i, rootTilePixelsPerMetre=%f " +
			"(worldBounds of root tile=[%f,%f,%f,%f]; " +
			"spaceBounds=[%f,%f,%f,%f])",
			tileset.tileSize, tileset.depth, tileset.rootTilePpm,
			rt.minX, rt.minY, rt.maxX, rt.maxY,
			sb.minX, sb.minY, sb.maxX, sb.maxY
		);
	}

	// pre-calculate tile world size at diff zoom levels
	tileset.worldSize = [];
	for (var z = 0; z <= tileset.depth; z++ )
	{
		var pixelsPerMetre = tileset.rootTilePpm * Math.pow( TILE_DIV, z );
		tileset.worldSize[ z ] = tileset.tileSize / pixelsPerMetre;
	}

	this.tileset = tileset;

	// tile cache, keyed by tile id
	tileset.tileCache = {};

	// queue of LRU <-> MRU
	tileset.tileQueue = [];

	// request root tile early as it is used as the final fallback for
	// the case where we need pixels from tiles that aren't yet loaded
	this.requestLoadTile( 0, 0, 0, true );

	jQuery( this ).triggerHandler( 'tilesetChange.sv' );
};


/**
*   Schedule the loading of the background tile for the given params.
*   Tile image will not be actually be loaded by this method until
*   this.tileLoader.load() called, or loadImmediately = true.
*/
SV.SpaceViewSurface.prototype.requestLoadTile =
function( /*int*/ zoomLevel, /*int*/ tileX, /*int*/ tileY, /*bool*/ loadImmediately )
{
	var tileMap = this.tileset.tileCache;
	var tileId = zoomLevel + ":" + tileX + ":" + tileY;

	if (tileMap[ tileId ])
		return;

	// use load time as a placeholder in cache to indicate a loading tile.
	// note that this also serves to prevent reloading tiles that don't exist
	// or are invalid.
	tileMap[ tileId ] = +new Date;

	var url = this._tileBaseurl + this.spaceName + "/space_viewer/tileset/" +
			zoomLevel + "/" + tileX + "/" + tileY + ".jpg";

	if (SV.debugTiling > 1)
	{
		console.log( "loading %s: ", tileId, url );
	}

	var tileImage = new Image();

	jQuery( tileImage ).one(
	{
		load: function()
		{
			var ts = this.tileset;

			// sanity check incoming tile images
			if (tileImage.width != ts.tileSize || tileImage.height != ts.tileSize)
			{
				console.error(
					"Tile dimensions (%f,%f) differ from tileset.tileSize (%i)",
					tileImage.width, tileImage.height, ts.tileSize
				);
				return;
			}

			// create new tile
			var tile = {
				id: tileId,
				lastUsed: +new Date,
				image: tileImage,
				z: zoomLevel,
				x: tileX,
				y: tileY,
			};

			if (SV.debugTiling)
			{
				console.log(
					"loaded tile %s (%i msec)",
					tileId, tile.lastUsed - tileMap[ tileId ]
				);
			}

			// cache tile
			ts.tileCache[ tileId ] = tile;
			ts.tileQueue.push( tileId );

			// expire tiles from cache if needed
			if (ts.tileQueue.length > UI.spaceBackgroundTileLayer.maxTileCacheSize)
			{
				this._flushTileCache();
			}

			if (!this._isInterpolating)
			{
				this.draw();
			}

			tileImage = null;
			jQuery( this ).triggerHandler( 'loadTile.sv', tileId );
		}
		.bind( this ),

		error: function()
		{
			// by this point, we've already checked that a valid tileset has been
			// correctly loaded, and that a serviceapp to serve the images is
			// present. since the requested tiles *should* exist, try to reload
			// the tile after 2.5secs so as not to hammer the tile service.
			console.warn( 'Tile image "%s" failed to load', tileId );
			new Alert.Info(
				"One or more tile images failed to load. " +
				"You may wish to reload the page and check the generated " +
				"tileset if the problem persists.",
				{ id: 'load-tile-image-failed' }
			);
			setTimeout( function() { delete tileMap[ tileId ]; }, 2500 );
		},
	});

	if (loadImmediately)
	{
		tileImage.src = url;
	}
	else
	{
		this.tileLoader.schedule( tileId, url, tileImage );
	}
};


/**
*   Converts from tile coordinates (zoom, tile x-position, y-position) to
*   world coordinates.
*/
SV.SpaceViewSurface.prototype.convertTileToWorldRect = function( z, x, y )
{
	var ts = this.tileset;
	var worldSizeOfTile = ts.worldSize[ z ];
	var worldX = ts.worldBoundsOfRootTile.minX + x * worldSizeOfTile;
	var worldY = ts.worldBoundsOfRootTile.maxY - y * worldSizeOfTile;

	return {
		minX: worldX, // west
		maxY: worldY, // north
		maxX: worldX + worldSizeOfTile, // east
		minY: worldY - worldSizeOfTile  // south
	};
};


/**
*	Unloads excess tiles. If the removeAll argument is boolean true,
*	unloads *all* tiles.
*/
SV.SpaceViewSurface.prototype._flushTileCache = function( /*boolean*/ removeAll )
{
	var tile, tileId;

	if (removeAll)
	{
		// remove all events/refs from images explicitly
		for (tileId in this.tileset.tileCache)
		{
			tile = this.tileset.tileCache[ tileId ];
			if (tile.image)
			{
				jQuery( tile.image ).remove();
				tile.image = null;
			}
		}

		this.tileset.tileCache = {};
		this.tileset.tileQueue = [];
		return;
	}

	var q = this.tileset.tileQueue;
	var tileMap = this.tileset.tileCache;
	var config = UI.spaceBackgroundTileLayer;

	// don't remove from cache if tile has just recently been loaded
	var dontExpireTimestamp = (+new Date) - config.minTimeBeforeExpiry;

	// remove first (oldest) tiles in a block
	var toRemove = q.splice( 0, q.length - config.minTileCacheSize );

	// re-add tiles to queue if we're not done with them
	var toAdd = [];

	for (var i in toRemove)
	{
		tileId = toRemove[ i ]
		tile = tileMap[ tileId ];

		// don't unload tiles if:
		// 1) it's a tile that has been in loading state for < 2secs, or
		// 2) it's a tile that was just recently loaded (< 2secs since used), or
		// 3) it's the root tile (as it's needed as a fallback)
		if ((!tile.image && tile > dontExpireTimestamp) ||
			tile.lastUsed > dontExpireTimestamp ||
			tileId === '0:0:0')
		{
			toAdd.push( tileId );
			continue;
		}

		if (SV.debugTiling)
		{
			console.log( "flushing %s from tile cache", tileId );
		}

		delete tileMap[ tileId ];
		jQuery( tile.image ).remove();
		tile.image = null;
	}

	if (toAdd.length > 0)
	{
		Array.prototype.push.apply( q, toAdd );
	}

	var numRemoved = toRemove.length - toAdd.length;
	if (numRemoved > 0)
	{
		jQuery( this ).triggerHandler( 'unloadTile.sv' );
	}
	return numRemoved;
};



/**
*	Determine the "zoom level" the current viewport for the purposes of
*	selecting which background tiles to draw.
*/
SV.SpaceViewSurface.prototype.getTileZoomLevel =
function( /*(optional) rect*/ worldRect )
{
	var worldWidth = worldRect ? worldRect.maxX - worldRect.minX : this.xPageSize;
	var tile0_ppm = this.tileset.rootTilePpm;

	// naive calculation of zoom level
	var z = Math.log(
		this.canvas.width / (worldWidth * tile0_ppm) )
			/ Math.log( TILE_DIV );

	// calc zoom level at which current browser performance degrades
	var perfCutoffZoom = Math.floor( Math.log(
		browserTilePixelLimit / (worldWidth * tile0_ppm) )
			/ Math.log( TILE_DIV ) );

	// allow for random console hackery
	z += UI.spaceBackgroundTileLayer.zoomLevelAdjust;

	// hack for wales
	if (this.tileset.tileSize > 1024)
		z -= 0.5;

	// clip to limit of available tiles and perf cutoff
	z = Math.max( Math.min(
		Math.ceil( z ), perfCutoffZoom, this.tileset.depth ), 0 );
		// Math.round( z ), perfCutoffZoom, this.tileset.depth ), 0 );

	return z;
};


/**
*	Returns the bounding rect of tile ids sufficient to render the given
*	(world) rect at the given tile zoom level.
*/
SV.SpaceViewSurface.prototype.getTileRect =
function( /*(optional) rect*/ worldRect, /*(optional) uint*/ zoomLevel )
{
	var sb = this.tileset.worldBoundsOfRootTile;
	worldRect = worldRect || this.getScreenBounds();
	worldRect = this._intersectRect( worldRect, this.tileset.spaceBounds );

	if (!worldRect)
	{
		// spacebounds not even in screen viewport, no tiles req'd
		return;
	}

	zoomLevel = zoomLevel >= 0 ? zoomLevel : this.getTileZoomLevel( worldRect );
	var tileWorldSize = this.tileset.worldSize[ zoomLevel ];

	var tileRect = {
		minX: Math.floor( (worldRect.minX - sb.minX) / tileWorldSize ),
		minY: Math.floor( (sb.maxY - worldRect.maxY) / tileWorldSize ),
		maxX: Math.max( 0, Math.floor( (worldRect.maxX - sb.minX - 0.001) / tileWorldSize ) ),
		maxY: Math.max( 0, Math.floor( (sb.maxY - worldRect.minY - 0.001) / tileWorldSize ) ),
	};

	if (SV.debugTiling > 1)
	{
		console.log(
			"tile rect at z=%i: [ %f,%f, %f,%f ], worldRect: [ %f, %f, %f, %f ]",
			zoomLevel, tileRect.minX, tileRect.minY, tileRect.maxX, tileRect.maxY,
			worldRect.minX, worldRect.minY, worldRect.maxX, worldRect.maxY
		);
	}

	return tileRect;
};


SV.SpaceViewSurface.prototype._initPreloadTilesOnAnimation = function()
{
	if (!this.viewportAnimation)
		return;

	var anim = this.viewportAnimation;
	jQuery( this.viewportAnimation ).on( 'start.animation', function()
	{
		if (!this.tileset) return;

		var xPageSize = anim.startZ + anim.deltaZ;
		var yPageSize = this.canvas.height / this.canvas.width * xPageSize;

		var futureWorldRect = {
			minX: anim.startX + anim.deltaX,
			maxX: anim.startX + anim.deltaX + xPageSize,
			minY: anim.startY + anim.deltaY - yPageSize,
			maxY: anim.startY + anim.deltaY,
		};

		var futureZoom = this.getTileZoomLevel( futureWorldRect );
		var tileRect = this.getTileRect( futureWorldRect, futureZoom );
		if (!tileRect)
		{
			// no part of destination rect intersects spacebounds
			return;
		}

		if (SV.debugTiling)
		{
			console.log(
				"preloading tiles for animation: %i:%i:%i - %i:%i:%i",
				futureZoom, tileRect.minX, tileRect.minY,
				futureZoom, tileRect.maxX, tileRect.maxY
			);
		}

		for (var y = tileRect.minY; y <= tileRect.maxY; y++ )
		{
			for (var x = tileRect.minX; x <= tileRect.maxX; x++ )
			{
				this.requestLoadTile( futureZoom, x, y );
			}
		}

		this.tileLoader.load();
	}
	.bind( this ) );
};

// spaceviewer_tiling.js

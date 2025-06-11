"use strict";

// Dygraph doesn't expose a method for changing the data it draws, so we add one.
assert( Dygraph, "Dygraph not loaded" );
assert( !Dygraph.prototype.setData, "setData already defined in Dygraph" );

if (BW.Chart)
	throw new Error(
		"A BW.Chart implementation already appears to be loaded: " + BW.Chart );

BW.require( "BW.ChartInteractionModel" );


/*~~~~~~~~~~~~~~~~~~~~~~~~~~~~ class BW.Chart ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~*/

/** Graph-drawing class. */
BW.Chart = function( /*jQuery*/ domTarget, /*Object*/ options )
{
	// dom references
	var dom = this.dom = {};
	dom.container = jQuery( domTarget );

	// recursively merge options
	var opt = {};
	// opt.highlightCallback = this._onHighlight.bind( this );
	opt.zoomCallback = this._onZoom.bind( this );

	// deep copy
	this.options = jQuery.extend( true,
		opt, BW.Chart.DEFAULT_DYGRAPH_OPTIONS, options );

	// BW.GraphiteSeries instance
	this.series = null;

	// Dygraph instance
	this.dygraph = null;

	this.resolution = opt.defaultResolution || 0;
};


// see http://dygraphs.com/options.html
BW.Chart.DEFAULT_DYGRAPH_OPTIONS =
{
	digitsAfterDecimal: 3,

	// accent every individual point
	drawPoints: false,

	// fill under lines
	fillGraph: true,

	stackedGraph: false,

	// stepPlot: true,

	// K/M/B for thousands, millions, billions
	labelsKMB: true,

	axisLabelFontSize: 11, // px

	// force y-axis to always include zero.
	includeZero: true,

	// interactionModel: Dygraph.Interaction.dragIsPanInteractionModel,
	interactionModel: BW.ChartInteractionModel,

	// rollPeriod: 3,
	// showRoller: true,
	// connectSeparatedPoints: true,

	strokeWidth: 1.25,
	fillAlpha: 0.25,

	// errorBars: true,
	// customBars: true,
	// sigma: 2, // #stddevs

	highlightCircleSize: 2.5,
	highlightSeriesBackgroundAlpha: 0.5,
	highlightSeriesOpts:
	{
		strokeWidth: 2.5,
		strokeBorderWidth: 1.5,
		highlightCircleSize: 3,
	},

	// yAxisLabelWidth: 40,
	rightGap: 0,

	// ylabel: '%',
	// valueRange: [0.0, 1.05],

	axes:
	{
		x:
		{
			pixelsPerLabel: 100,
		},
		y:
		{
			drawAxis: false,
		}
	},

	// legend: 'always',

	// logscale: true,

	// showRangeSelector: true,

	// DOM id of an element that will receive legend content
	// note: no '#' prefix; must be identified by id not class.
	labelsDiv: 'chart-legend',

	titleHeight: 20, // px

	// showLabelsOnHighlight: false,

	// connectSeparatedPoints: true,

	/*~~~~~ non-dygraph options ~~~~~*/

	title: '',

	// Map of series
	seriesPreferences: {},

	// number of points at which chart will attempt to reload
	// current series at a lower resolution
	maxPointsBreakpoint: 500, // points

	// min number of points to fetch in a single ajax request
	minFetchPoints: 20, // points

	// max number of points to fetch in a single ajax request
	maxFetchPoints: 75, // points

	defaultResolution: 0,

	// if a boolean true value, rescale each series to that series' max Y value.
	normaliseY: true,
};


/**
*   Linked charts all redraw when any of them draw.
*   Passed array not checked for dupes. Over-writes any existing links.
*/
BW.Chart.linkCharts = /*static*/ function( /*Array of BW.Chart*/ charts )
{
	charts = charts.slice();
	// console.debug( "linking charts: %O", charts );
	for (var i in charts)
	{
		// all for one, and one for all
		charts[i]._syncedCharts = charts;
	}
};


BW.Chart.prototype._onZoom = function( minDate, maxDate )
{
	jQuery( this ).triggerHandler( 'changeViewportX', this.getViewRangeX() );
};


/**
*   Considers the current number of points drawn in the view, and increases or
*   decreases series resolution if the number of points exceeds a certain range.
*
*   Returns a boolean false value if the resolution level was not changed, or
*   an ajax deferred if it was.
*/
BW.Chart.prototype._checkResolution = function()
{
	var xViewRange = this.getViewRangeX();
	if (!xViewRange)
	{
		// nothing drawn yet
		// console.warn( "xViewRange not yet defined (no data yet?)" );
		return;
	}

	var model = this.series.model;
	var maxPoints = this.options.maxPointsBreakpoint;
	assert( maxPoints > 0 );

	var now = Date.now() / 1000;
	var range = xViewRange[1] - xViewRange[0];
	var timeDelta = Math.floor( now - xViewRange[0] );

	for (var r = 0; r < model.aggregationIntervals.length; r++)
	{
		if (timeDelta > model.aggregationPeriods[r])
		{
			// console.log( "@r=%s: %s > %s", r, timeDelta, model.aggregationPeriods[r] );
			continue;
		}

		var numPoints = range / model.aggregationIntervals[r];
		// console.log( "points @ r=%s: %s", r, numPoints );
		if (numPoints < maxPoints) break;
	}

	// console.debug( "resolution should be: %s (%ssec)", r, model.aggregationIntervals[r] );
	return this.setResolution( r );
};


/**
*   Explicitly set the resolution level of this chart. Must be in the range of
*   `model.aggregationIntervals`.
*
*   Note that the current series' model `aggregationPeriods` settings and
*   the option `maxPointsBreakpoint` may immediately reset the resolution
*   level if the number of points falls outside their range.
*
*   Changing resolution causes the `changeResolution` event, eg:
*
*       jQuery( chart ).on( 'changeResolution',
*           function( event, newResolution ) { ... } );
*/
BW.Chart.prototype.setResolution = function( /*uint*/ resolution )
{
	var series = this.series;
	var target = series.target;
	var model  = series.model;

	if (resolution >= model.aggregationIntervals.length)
	{
		resolution = model.aggregationIntervals.length - 1;
	}

	if (resolution < 0)
	{
		resolution = 0;
	}

	if (resolution == this.resolution)
	{
		// no change
		return;
	}

	jQuery( this ).triggerHandler( 'changeResolution', [resolution] );

	this.resolution = resolution;

	if (series.fetchInProgress)
	{
		series.abortFetch();
	}

	// initially load the most recent quarter of the current view range
	var xViewRange = this.getViewRangeX();
	var xFetchRange = [xViewRange[1] - ((xViewRange[1] - xViewRange[0]) / 4), xViewRange[1]]

	assert( xFetchRange[1] > xFetchRange[0], xFetchRange )
	// var xFetchRange = xViewRange;

	var newInterval = model.aggregationIntervals[resolution];
	assert( newInterval, "interval=%s, resolution=%s", newInterval, resolution );

	// round xFetchRange to new interval (expand to nearest multiple)
	xFetchRange[0] -= (xFetchRange[0] % newInterval);
	xFetchRange[1] += (newInterval - (xFetchRange[1] % newInterval));
	// console.debug( "after rounding to interval: ", xFetchRange );

	// check if we're going to a load a shitload of points; a warning for now
	var numPoints = 1 + (xFetchRange[1] - xFetchRange[0]) / newInterval;
	if (numPoints > this.options.maxPointsBreakpoint)
	{
		console.warn( "Fetching a large number of points: " + numPoints );
	}

	// clearing here is only for freeing some memory; no loss of function
	// if not cleared; series data will just be cached for next time.
	// potential todo: optimise caching behaviour
	series.clear();

	series = this.series = model.getSeriesAtResolution( series, newInterval );

	var _this = this;
	var updateAndDraw = function()
	{
		_this.draw();
	};

	if (series.fetchInProgress)
	{
		return series.fetchInProgress.then( updateAndDraw );
	}
	else
	{
		if (xFetchRange[0] >= xFetchRange[1]) return;
		
		// requesting time ranges beyond the max recordable time range is a
		// fatal exception in graphite
		var oldestDataTime = this._getOldestDataTime();
		
		if (xFetchRange[0] < oldestDataTime || xFetchRange[1] < oldestDataTime)
		{
			new Alert.Warning(
				"View range is beyond maximum data recording range" );
			
			// the end is beyond the oldest data time, just return
			if (xFetchRange[1] < oldestDataTime)
			{
				return;
			}
			
			// the start is beyond the oldest data time while the end is within
			this._drawVerticalLine( oldestDataTime, 'red' );
			xFetchRange[0] = oldestDataTime;
		}

		console.debug(
			"re-fetching series (%s-%s) at lower resolution (%s points @ %ssec)",
			xFetchRange[0], xFetchRange[1], numPoints, newInterval
		);

		return series.fetch( xFetchRange[0], xFetchRange[1] ).then( updateAndDraw );
	}
};


BW.Chart.prototype.addSeries = function( /*BW.GraphiteSeries*/ series )
{
	// this.series.push( series );
	assert( !this.series, "todo: >1 series per chart" );
	this.series = series;
};


BW.Chart.prototype.getTitle = function()
{
	if (this.options.title)
	{
		return this.options.title;
	}

	return (this.targetMask || this.series.target)
		+ " ("
		+ this.getInterval()
		+ "sec)";
};


/** Extract [Dygraph] data model from this chart's [BW.GraphiteSeries]. */
BW.Chart.prototype.getData = function()
{
	var seriesList = this.series.childSeriesCount
		? this.series.getChildSeries()
		: [this.series];

	if (this.targetMask)
	{
		// filter series targets by targetMask expression (currently can
		// be a String or RegExp), first stripping target expression of
		// embedded graphite functions (ie: match only the base target).
		var mask = this.targetMask;
		var namingScheme = this.series.model.namingScheme;
		seriesList = seriesList.filter( function( s ) {
			return namingScheme.stripTarget( s.target ).match( mask ); } );
	}

	if (!seriesList || !seriesList.length)
	{
		console.warn( "No series to draw for chart: %s", this.getTitle() );
		return;
	}

	var dygraphData = this.series.model.getDygraphModelFor( seriesList );

	this._targets = seriesList.map( function( s ) { return s.target; } );

	// init labels and colours
	this._initLabels();
	this._initColours();

	return dygraphData;
};


BW.Chart.prototype._initLabels = function()
{
	var targets = this._targets;
	var labels = this.options.labelGenerator;

	if (labels && (labels instanceof Function))
	{
		// explicit label-generating function
		labels = labels.call( this, targets );

		// #labels must correspond to #series in seriesList && be unique
		if (labels.length !== targets.length + 1)
		{
			throw new Error(
				"Length of returned label array (%s) differs from expected (%s) "
				+ "(did you forget to add x-axis label at index 0?)",
				labels.length, targets.length + 1
			);
		}
	}
	else
	{
		// determine labels from target names using a heuristic
		labels = this.extractUniqueLabels( targets );
	}

	this.labels = labels;
};


/**
*   Update graph with new data & redraw. Triggers the `changeData` event, eg:
*
*       jQuery( chart ).on( 'changeData', function( event, newData ) { ... };
*
*   Incoming data can be modified through the `newData` reference.
*/
BW.Chart.prototype.setData = function( /*Array of Array of Number*/ data )
{
	assert( data );

	jQuery( this ).triggerHandler( 'changeData', [data] );

	this.dygraph.updateOptions( { file: data } );
};


BW.Chart.prototype._getSeriesMaximums = function()
{
	if (this.seriesMax) return this.seriesMax;

	if (!this.seriesPreferences)
	{
		this.seriesMax = [null];
		return this.seriesMax;
	}

	if (!this.labels)
	{
		console.error( "No series labels available" );
		this.seriesMax = [null];
		return this.seriesMax;
	}

	var prefs = this.seriesPreferences;

	// note: labels always has the x-dimension (time) at index 0
	var labels = this.labels.map(
		function( x ) { return x.replace( /.+\./, '' ); } );

	this.seriesMax = labels.map(
		function( x ) { if (!prefs[x]) return 0; return prefs[x].max; } );

	return this.seriesMax;
};


/**
*   Transform y-values to [0, 1] by re-scaling to respective series max value.
*
*   Note: passed array values are modified in situ.
*/
BW.Chart.prototype._normaliseY = function( /*Array of Array*/ data )
{
	var numPoints = data.length;
	var numSeries = data[0].length;
	var seriesMax = this._getSeriesMaximums();

	// find each series' max
	var max;
	for (var s = 1; s < numSeries; s++)
	{
		max = seriesMax[s] || 0;
		for (var p = 0; p < numPoints; p++)
		{
			if (data[p][s] > max)
			{
				max = data[p][s];
			}
		}

		seriesMax[s] = max;
	}

	// normalise each series to its respective max
	for (var s = 1; s < numSeries; s++)
	{
		max = seriesMax[s];
		if (!max) continue;

		for (var p = 0; p < numPoints; p++)
		{
			// skip nulls as null / 1 == 0 in JS and nulls need to preserved in
			// order to be drawn as gaps in charts
			if (!data[p][s]) continue;

			data[p][s] /= max;
		}
	}
};


BW.Chart.prototype.draw = function()
{
	var series = this.series;
	var data = this.getData();

	if (!data)
	{
		console.log( "no data to draw for chart: %s", this.getTitle() );
		this._loadMoreDataIfNeeded();
		return;
	}

	if (this.options.normaliseY)
	{
		this._normaliseY( data );
		// this.options.valueRange = [0, 1];
	}

	var options = this.options;
	options.labels = this.labels;
	options.colors = this.colours;
	options.title = this.getTitle();

	if (this.dygraph)
	{
		var dg = this.dygraph;
		dg.updateOptions( options, /*blockRedraw*/ true );

		// set data + redraw
		this.setData( data );
	}
	else
	{
		options.drawCallback = this._drawCallback.bind( this );

		var domTarget = this.dom.container[0];

		this.dygraph = new Dygraph( domTarget, data, options );
		this.dygraph.bw_chart = this;
	}
};


/**
*   Returns the number of seconds between datapoints at the given resolution
*   level, or the number of seconds between datapoints at the current resolution
*   if not given.
*/
BW.Chart.prototype.getInterval = function( /*int?*/ r ) /*returns Integer sec*/
{
	return this.series.model.aggregationIntervals[r || this.resolution || 0];
};


BW.Chart.prototype.getViewRangeX = function() /*returns Integer numSecs*/
{
	if (!this.dygraph) return;

	var xViewRange = this.dygraph.xAxisRange().slice();
	// console.log( "viewRange before: ", xViewRange );

	if (xViewRange[0].getTime)
	{
		xViewRange[0] = xViewRange[0].getTime();
	}

	if (xViewRange[1].getTime)
	{
		xViewRange[1] = xViewRange[1].getTime();
	}
	// console.log( "viewRange: " + xViewRange );

	// msec -> sec
	xViewRange[0] /= 1000;
	xViewRange[1] /= 1000;

	assert( xViewRange[0] < xViewRange[1], "Invalid range: ", xViewRange );
	// console.log( "viewRange: " + xViewRange );

	return xViewRange;
};

/**
*   Set the current view range in epoch seconds.
*/
BW.Chart.prototype.setViewRangeX = function( /*Array of int*/ range )
{
	assert( range );
	assert( range[1] > range[0], range );

	var g = this.dygraph;
	if (!g)
	{
		console.warn(
			"setViewRangeX for chart %s called before being drawn",
			this.getTitle()
		);
		return;
	}
	
	var newRange = [ range[0] * 1000, range[1] * 1000 ];
	// ensure we redraw ourselves
	this._dontSkipRedraw = true;

	g.updateOptions( { dateWindow: newRange } );

	jQuery( this ).triggerHandler( 'changeViewportX', newRange );
};


/**
*   Set the current view range to the given number of seconds. If no argument
*   provided, the current view is time-shifted to the current time and the
*   existing range is preserved.
*/
BW.Chart.prototype.setViewRange = function( /*int?*/ span /*seconds*/ )
{
	var g = this.dygraph;
	var now = Date.now();
	var interval = this.getInterval();

	// round down to nearest interval
	now -= (now % (interval * 1000));

	var viewRange = this.getViewRangeX();
	var range;

	if (span)
	{
		if (!(span > 0)) throw new Error( "Invalid span: " + span )

		range = [viewRange[1] - span, viewRange[1]];

		range[0] *= 1000;
		range[1] *= 1000;

		if (range[1] > now)
		{
			range[0] -= range[1] - now;
			range[1] = now;
		}
	}
	else
	{
		span = 1000 * (viewRange[1] - viewRange[0]);
		range = [now - span, now];
	}

	// ensure we redraw ourselves
	this._dontSkipRedraw = true;

	assert( range[1] > range[0], "Invalid range: ", range );
	// console.debug( "setting date range: ", range );

	g.updateOptions( { dateWindow: range } );

	jQuery( this ).triggerHandler( 'changeViewportX', range );
};


BW.Chart.prototype.getDataRangeX = function() /*returns Integer numSecs*/
{
	if (!this.dygraph) return;

	var xDataRange = this.dygraph.xAxisExtremes().slice();

	if (xDataRange[0].getTime)
	{
		xDataRange[0] = xDataRange[0].getTime();
	}

	if (xDataRange[1].getTime)
	{
		xDataRange[1] = xDataRange[1].getTime();
	}

	// msec -> sec
	xDataRange[0] /= 1000;
	xDataRange[1] /= 1000;

	// console.log( "dataRange: " + xDataRange );
	return xDataRange;
};



BW.Chart.prototype._drawCallback = function( /*Dygraph*/ dygraph, /*boolean*/ isInitialDraw )
{
	this._checkResolution();
	this._loadMoreDataIfNeeded();

	if (!isInitialDraw)
	{
		var drawTime = dygraph.drawingTimeMs_;
		if (drawTime > 100)
		{
			console.warn(
				"Performance warning: drawTime = %s for chart ",
				drawTime, this.getTitle()
			);
		}
	}

	this._syncLinkedCharts();

	jQuery( this ).triggerHandler( 'draw' );
};


BW.Chart.prototype._showMissingData = function( from, until )
{
	var d = this.dygraph;
	var ctx = d.hidden_ctx_;
	var area = d.layout_.getPlotArea();

	var fromX = d.toDomXCoord( 1000 * from );
	var untilX = d.toDomXCoord( 1000 * until );

	ctx.save();

	ctx.fillStyle = 'rgba(0,0,0,0.1)';
	ctx.fillRect(
		area.x + fromX
		, area.y
		, untilX - fromX
		, area.h
	);

	ctx.restore();
};


BW.Chart.prototype._drawVerticalLine = function( /*int*/ epochSeconds, /*String?*/ strokeStyle )
{
	var d = this.dygraph;
	var ctx = d.hidden_ctx_;
	var area = d.layout_.getPlotArea();

	var timeX = d.toDomXCoord( 1000 * epochSeconds );

	ctx.save();

	ctx.strokeStyle = strokeStyle || 'rgba(0,0,0,0.5)';

	ctx.beginPath();
	ctx.moveTo( area.x + timeX, area.y );
	ctx.lineTo( area.x + timeX, area.y + area.h );
	ctx.stroke();

	ctx.restore();
};


BW.Chart.prototype._loadMoreDataIfNeeded = function()
{
	var xViewRange = this.getViewRangeX();
	var xDataRange = this.getDataRangeX();
	if (!xViewRange || !xDataRange) return;

	var interval = this.getInterval();
	assert( interval > 0, "int=%s, res=%s", interval, this.resolution );

	var now = Date.now() / 1000;

	// requesting time ranges beyond the max recordable time range is a
	// fatal exception in graphite
	var oldestDataTime = this._getOldestDataTime();

	if (xViewRange[0] < oldestDataTime)
	{
		new Alert.Warning(
			"View range is beyond maximum data recording range" );

		this._drawVerticalLine( oldestDataTime, 'red' );
	}

	if (xViewRange[0] < xDataRange[0])
	{
		this._showMissingData( xViewRange[0], xDataRange[0] );
	}

	if (xViewRange[1] > xDataRange[1])
	{
		this._showMissingData( xDataRange[1], xViewRange[1] );
	}

	if (xViewRange[0] < xDataRange[0])
	{
		// there is unloaded data to the left

		if (xViewRange[1] < xDataRange[0])
		{
			// view is entirely outside of data range (possibly by a lot),
			// so discard existing data and re-fetch.
			this.series.clear();
			xDataRange[1] = xDataRange[0] = xViewRange[1];
		}

		// view exceeds range of data, fetch more -
		// start with 150% of difference in view range vs data range
		var delta = 1.5 * (xDataRange[0] - xViewRange[0]);

		// apply limits to fetch
		delta = Math.max( this.options.minFetchPoints * interval,
			Math.min( this.options.maxFetchPoints * interval, delta ) );

		var requiredDataRange = [xDataRange[0] - delta, xDataRange[0]];
		if (requiredDataRange[0] < oldestDataTime)
		{
			requiredDataRange[0] = oldestDataTime;
		}

		// graphite doesn't like floats
		requiredDataRange = requiredDataRange.map( Math.floor );

		// round lower bound to nearest interval secs
		requiredDataRange[0] -= (requiredDataRange[0] % interval);

		this.fetchData( requiredDataRange[0], requiredDataRange[1] );

		return;
	}

	if (xViewRange[1] > xDataRange[1])
	{
		// there is unloaded data to the right

		// don't attempt to fetch data too close to "now"
		if (xDataRange[1] > now - 2 * interval)
		{
			if (this._fetchLater) return;

			this._fetchLater = setTimeout(
				function()
				{
					this._fetchLater = null;
					this.draw();
				}
				.bind( this ), interval * 1000
			);

			return;
		}

		if (xDataRange[1] < xViewRange[0])
		{
			// view is entirely outside of data range (possibly by a lot),
			// so discard existing data and re-fetch.
			this.series.clear();
			xDataRange[1] = xDataRange[0] = xViewRange[0];
		}

		// view exceeds range of data, fetch more -
		// start with 150% of difference in view range vs data range
		var delta = 1.5 * (xViewRange[1] - xDataRange[1]);

		// apply limits to fetch
		delta = Math.max( this.options.minFetchPoints * interval,
			Math.min( this.options.maxFetchPoints * interval, delta ) );

		var requiredDataRange = [xDataRange[1], xDataRange[1] + delta];

		if (requiredDataRange[1] > now)
		{
			requiredDataRange[1] = now;
		}

		if ((requiredDataRange[1] - requiredDataRange[0]) < interval)
		{
			return;
		}

		// graphite doesn't like floats
		requiredDataRange = requiredDataRange.map( Math.floor );

		// round to nearest interval
		requiredDataRange[0] -= (requiredDataRange[0] % interval);
		requiredDataRange[1] -= (requiredDataRange[1] % interval);

		this.fetchData( requiredDataRange[0], requiredDataRange[1] );

		return;
	}

	if (this._fetchLater)
	{
		clearTimeout( this._fetchLater );
		this._fetchLater = null;
	}
};


BW.Chart.prototype.fetchData = function( /*int*/ from, /*int*/ until )
{
	if (from >= until)
	{
		console.warn( "Invalid time range, until is earlier than from" );
		return false;
	}
	
	if (this.series.fetchInProgress)
	{
		// if the ongoing fetch intersects with the required range, redraw
		// after fetch is returned, otherwise abort the ongoing the fetch
		// and re-fetch
		if (this.series.intersectFetch( from, until ))
		{
			this.series.fetchInProgress.then( this.draw.bind( this ) );				
		}
		else
		{
			this.series.abortFetch();
			this.series.fetch( from, until ).then( this.draw.bind( this ) );
		}
	}
	else
	{
		this.series.fetch( from, until ).then( this.draw.bind( this ) );
	}
}


BW.Chart.prototype._getOldestDataTime = function()
{
	var now = Date.now() / 1000;
	var aggPeriods = this.series.model.aggregationPeriods;
	
	return now - aggPeriods[aggPeriods.length - 1];
};


/**
*   Sync the view range of all charts that are linked to this one.
*
*   Charts are ordinarily *not* redrawn if the view range of the current chart
*   is the same as the view range of the first chart that caused the sync. This
*   optimisation can be bypassed by setting the property `_dontSkipRedraw`.
*/
BW.Chart.prototype._syncLinkedCharts = function()
{
	if (this._blockSync) return;
	if (!this._syncedCharts || !this._syncedCharts.length) return;

	var g = this.dygraph;
	if (!g) return;

	var currentView = {
		dateWindow: g.xAxisRange(),
		// valueRange: g.yAxisRange(), // don't sync on y-axis
	}

	// avoid infinite recursion
	this._blockSync = true;
	var syncedCharts = this._syncedCharts || [];

	for (var i in syncedCharts)
	{
		var c = syncedCharts[i];
		if (!c.dygraph) continue;

		var view = c.dygraph.xAxisRange();
		if (view[0] == currentView.dateWindow[0]
			&& view[1] == currentView.dateWindow[1]
			&& !c._dontSkipRedraw)
		{
			continue;
		}

		c._blockSync = true;
		delete c._dontSkipRedraw;
		c.dygraph.updateOptions( currentView );
	}

	for (i in syncedCharts)
	{
		syncedCharts[i]._blockSync = false;
	}
	this._blockSync = false;
};


BW.Chart.prototype._initColours = function()
{
	var prefs = this.seriesPreferences;
	if (!prefs) return;

	// colours by label instead of by series shortname
	// note: first label is always the x-axis label
	var ns = this.series.model.namingScheme;
	var labels = this.labels;
	assert( labels );

	var colours = new Array( labels.length - 1 );
	var colourGenerator = this.options.colourGenerator
		|| function() { return '#aaaaaa'; /*default to grey*/ };

	for (var i = 1; i < labels.length; i++)
	{
		var label = labels[i];

		if (prefs[label] && prefs[label].colour)
		{
			colours[i - 1] = prefs[label].colour;
		}
		else
		{
			colours[i - 1] = colourGenerator.call( this, label );
		}
	}

	this.colours = colours;
};


/**
*   Creates unique labels for the given Graphite targets, stripping label
*   parts that are common to all targets in the list.
*
*   Eg1: given:
*
*       [ "someFunction( xxx.machine_aaa.user_bbb.process_ccc.stat_Ddd )",
*         "someFunction( xxx.machine_aaa.user_bbb.process_ccc.stat_Eee )",
*         "someFunction( xxx.machine_aaa.user_bbb.process_ccc.stat_Fff )" ]
*
*   this method would return:
*
*       ["Ddd", "Eee", "Fff"]
*
*   Eg2: given:
*
*       [ "xxx.machine_aaa.user_Fred.process_ccc.stat_Xxx )",
*         "xxx.machine_aaa.user_Alice.process_ccc.stat_Xxx )",
*         "xxx.machine_aaa.user_Bob.process_ccc.stat_Xxx )" ]
*
*   this method would return:
*
*       ["Fred", "Alice", "Bob"]
*/
BW.Chart.prototype.extractUniqueLabels = function( /*Array of String*/ targets )
{
	assert( targets.length, "Expected >0 targets: %O", targets );
	var namingScheme = this.series.model.namingScheme;
	var labelParts = new Array( targets.length );

	for (var i = 0; i < targets.length; i++)
	{
		// strip function(s) if present
		var baseTarget = targets[i].replace( /^.+\(/, '' ).replace( /,.+$/, '' ).toLowerCase();

		// split into Array of (name, value) tuples
		var targetElements = namingScheme.splitTarget( baseTarget );

		// extract value parts
		labelParts[i] = targetElements.map(
			function( tuple ) { return tuple[1] || tuple[0]; } );
	}

	// strip common parts
	var col = 0;
	while (col < labelParts[0].length && labelParts[0].length > 1)
	{
		var seen = {};
		for (var i = 0; i < labelParts.length; i++)
		{
			if (!seen[labelParts[i][col]])
				seen[labelParts[i][col]] = true;
		}

		if (Object.keys( seen ).length === 1)
		{
			// console.log( "remove: " + labelParts[0][col] );
			for (i = 0; i < labelParts.length; i++)
			{
				labelParts[i].splice( col, 1 );
			}
			continue;
		}

		col++;
	}

	var labels = labelParts.map( function( x ) { return x.join( '.' ); });

	// x-axis label must be at index 0
	labels.unshift( 'time' );

	return labels;
};


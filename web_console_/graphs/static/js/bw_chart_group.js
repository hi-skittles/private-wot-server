"use strict";

BW.require( "jQuery" );
BW.require( "BW.Chart" );
// assert( BW.user, "Expected BW.user to be initialised" );


/**
*   Chart collection-drawing class that draws the data of a `BW.GraphiteSeries`
*   into 1-many `BW.Chart`s.
*/
BW.ChartGroup = function( /*jQuery*/ domTarget, /*Object*/ options )
{
	// dom refs
	var dom = this.dom = {};
	dom.container = jQuery( domTarget );

	// recursively merge options, except for a 'prefs' object, which
	// should be common to all charts.
	var chartPrefs = options.prefs;
	delete options.prefs;
	var opt = this.options = jQuery.extend( true,
		{}, BW.ChartGroup.DEFAULT_OPTIONS, options );

	opt.prefs = chartPrefs || {};

	// BW.GraphiteModel
	this.model = opt.model || new BW.GraphiteModel( opt.graphiteHost );

	// subscribe to fetch events (to show fetch progress)
	jQuery( this.model ).on({
		fetch: this._onFetch.bind( this ),
		fetchComplete: this._onFetchComplete.bind( this ),
	});

	// predraw callback for drawing fetch progress
	opt.chartOptions.underlayCallback = this._onBeforeDrawChart.bind( this );

	// Array of BW.Chart
	this.charts = [];

	// String
	this.targets = opt.targets;

	if (opt.groups instanceof Array)
	{
		// one graph per group
		this.createCharts( opt.groups )
	}
	else
	{
		// one graph per stat matching target expression
		// requires additional graphite lookup
		this._fetchStatNamesThenCreateCharts( opt.groups || opt.targets );
	}
};

BW.ChartGroup.extends( BW.Chart );

// wrap BW.Chart's methods into BW.ChartGroup's prototype so that they
// can be delegated to all BW.Chart's (via the first one).
(function()
{
	var _wrap = function( /*Function*/ f )
	{
		return function() {
			var chart = this.charts[0];
			// consle.debug( "(delegated method)" );
			var args = Array.prototype.slice.apply( arguments );
			return f.apply( chart, args );
		};
	};

	for (var k in BW.Chart.prototype)
	{
		if (BW.Chart.prototype.hasOwnProperty( k )
			&& typeof( BW.Chart.prototype[k] ) === 'function')
				BW.ChartGroup.prototype[k] = _wrap( BW.Chart.prototype[k] );
	}
})();


BW.ChartGroup._hash = function( /*String*/ label )
{
	// simple hashing function adapted from sdbm algorithm
	// works well for short, similar strings
	var hash = 5381;
	assert( label.length );

	var c;
	for (var i = 0; i < label.length; i++)
	{
		c = label.charCodeAt( i );
		hash = hash + (c << 6) + (c << 16) - c;
		hash %= 360;
	}

	return hash;
};


// see http://dygraphs.com/options.html
BW.ChartGroup.DEFAULT_OPTIONS =
{
	// series configuration object, common to all `BW.Chart`s
	prefs: {},

	// options object that will be passed to BW.Chart constructors
	chartOptions:
	{
		// generates a colour for uncoloured series labels (deterministic)
		colourGenerator: function( /*String*/ seriesLabel )
		{
			var seriesPrefs = this.seriesPreferences;
			var hue = BW.ChartGroup._hash( seriesLabel );
			var rgb = Dygraph.hsvToRGB( hue / 360, 0.75, 0.5 );

			console.debug(
				"No colour defined for label '%s', assigning ",
				seriesLabel, rgb
			);

			if (!seriesPrefs[seriesLabel])
			{
				seriesPrefs[seriesLabel] = { colour: rgb };
			}
			else if (!seriesPrefs[seriesLabel].colour)
			{
				seriesPrefs[seriesLabel].colour = rgb;
			}

			return rgb;
		},
	},

	graphiteHost: "http://bwsandbox01",

	// Any String Graphite target expression that is legal to the
	// `BW.GraphiteModel.getSeries` factory constructor.
	targets: "stat_logger.machine_*",

	// Array of String substrings to group charts by, or
	// a wildcarded string expression with which to match metrics.
	// undefined means 1 chart per stat returned by `targets` filter above.
	groups: undefined,

	// Array of String chart titles. Defaults to group name if not given.
	titles: undefined,

	// Default 'from' argument.
	from: "-302s",

	// Default 'until' argument.
	until: "now",

	cssChartContainer: 'chart-container',
};


BW.ChartGroup.prototype._onFetch = function( ev, /*BW.GraphiteSeries*/ series, from, until )
{
	// console.log( "fetch from %s until %s", new Date( from * 1000 ), new Date( until * 1000 ) );
	this._fetchingFrom = from;
	this._fetchingUntil = until;
};


BW.ChartGroup.prototype._onFetchComplete = function( ev, /*BW.GraphiteSeries*/ series, from, until )
{
	// console.log( "fetched from %s until %s", new Date( from * 1000 ), new Date( until * 1000 ) );
	this._fetchingFrom = 0;
	this._fetchingUntil = 0;
};


BW.ChartGroup.prototype._onBeforeDrawChart =
function( /*CanvasRenderingContext2D*/ ctx, /*Object*/ area, /*Dygraph*/ d )
{
	var from = this._fetchingFrom;
	var until = this._fetchingUntil;

	if (from > 0 && until > 0)
	{
		var fromX = Math.max( d.toDomXCoord( 1000 * from ), 0 );
		var untilX = Math.min( d.toDomXCoord( 1000 * until ), area.x + area.w );
		var y = Math.floor( area.y + area.h / 2 );
		var width = untilX - fromX;
		var spacing = 6; // pixels
		var msg = 'loading';
		ctx.save();

		ctx.font = '12px Arial, sans-serif';
		var msgWidth = ctx.measureText( msg ).width;
		if (width >= msgWidth + 10)
		{
			width -= msgWidth;
			width -= spacing;
			width /= 2;
		}
		else
		{
			// not enough space to fit message
			msgWidth = 0;
			spacing = 0;
			width /= 2;
		}

		ctx.fillStyle = 'rgba(10,0,100,0.25)';
		ctx.fillRect(
			area.x + fromX
			, y + 3
			, width
			, 6
		);

		ctx.fillRect(
			area.x + fromX + width + msgWidth + spacing
			, y + 3
			, width
			, 6
		);

		if (msgWidth)
		{
			ctx.textBaseline = 'middle';
			ctx.fillStyle = 'rgba(10,0,100,0.5)';
			ctx.fillText( msg, area.x + fromX + width + spacing / 2, y + 6 );
		}

		ctx.restore();
	}
};


BW.ChartGroup.prototype.draw = function()
{
	var prefs = this.options.prefs;
	for (var i in this.charts)
	{
		var chart = this.charts[i];
		chart.seriesPreferences = prefs;
		// chart.options.timingName = "chart" + i;
		chart.draw();
	}
};


/**
*   Resizes all charts to the size of the parent DOM container.
*/
BW.ChartGroup.prototype.resize = function()
{
	// reverse order as it mysteriously avoids the issue where the top chart
	// is drawn without a rightGap but other charts are.
	var charts = this.charts;
	for (var i = charts.length - 1; i >= 0; i--)
	{
		var g = this.charts[i].dygraph;
		if (!g) continue;

		g.resize();
	}
};


/** Returns the BW.Chart corrsponding to the given id (ie: title). */
BW.ChartGroup.prototype.getChart = function( /*String*/ id )
{
	for (var i in this.charts)
	{
		if (id === this.charts[i].getTitle())
		{
			return this.charts[i];
		}
	}
};


/**
*   Sets whether data gaps will be shown or not.
*/
BW.ChartGroup.prototype.showGaps = function( /*boolean*/ showGaps )
{
	for (var i in this.charts)
	{
		this.charts[i].options.connectSeparatedPoints = !showGaps;
	}

	this.draw();
};


/**
*   Sets whether Y axis will be shown or not.
*/
BW.ChartGroup.prototype.showYAxis = function( /*boolean*/ showYAxis )
{
	for (var i in this.charts)
	{
		this.charts[i].options.axes.y.drawAxis = showYAxis;
	}

	this.draw();
};


/**
*   Given a graphite target prefix of form `"stat_logger.machine_*"`, query
*   graphite to find metric names, then create a chart for each one.
*/
BW.ChartGroup.prototype._fetchStatNamesThenCreateCharts = function( /*String*/ filter )
{
	var seen = {};
	var statNames = [];

	// strip anything not understood by graphite as a metric name filter by
	// stripping back to bare target (ie: no functions).
	filter = this.model.namingScheme.stripTarget( filter );

	this.model.searchMetrics( filter ).then(
		function( /*Object*/ response )
		{
			var targetList = response.metrics;

			for (var i in targetList)
			{
				if (!targetList[i].is_leaf) continue;

				var statName = targetList[i].name;
				if (seen[statName]) continue;
				seen[statName] = true;

				// targets.push( targetPrefix + '.' + statName );
				statNames.push( statName );
			}

			// console.log( "targets by stat name: %O", targets );
			// this.createCharts( targets, targetPrefix );

			console.log( "targets by stat name: %O", statNames );

			this.createCharts( statNames );
		}
		.bind( this )
	)
	.fail( this._fetchStatNamesFailed.bind( this ) );
};


/** Called when an ajax request for series names fails. */
BW.ChartGroup.prototype._fetchStatNamesFailed =
function( /*jQuery.ajax*/ xhr, /*String*/ statusMsg )
{
	console.error( "_fetchStatNamesThenCreateCharts failed: status=%s, xhr=%O", statusMsg, xhr );
	new Alert.Error( "Failed to initialise metrics" );
};


/**
*   Instantiates `BW.Chart`s, 1 per group passed. The `Array` of `BW.Chart`s
*   created is accessible via the `charts` property.
*/
BW.ChartGroup.prototype.createCharts = function( /*Array of String*/ groups )
{
	var model = this.model;
	var opt = this.options;
	var charts = this.charts;
	var titles = opt.titles || groups;

	// console.debug( "creating charts %O for target: %s", groups, this.targets );
	var rootSeries = this.rootSeries = model.getSeries( this.targets );
	// rootSeries.clear();

	for (var i in groups)
	{
		var container = this._createChartDom( groups[i], titles[i] );

		var chart = new BW.Chart( container, opt.chartOptions );
		chart.targetMask = groups[i];
		chart.series = rootSeries;
		chart.options.title = titles[i];

		charts.push( chart );
	}
	console.debug( "created charts: %O", charts );

	var draw = function()
	{
		console.debug(
			'drawing %s series: %O',
			(rootSeries.childSeriesCount || 1), rootSeries );

		this.draw();
		BW.Chart.linkCharts( charts );
		jQuery( this ).triggerHandler( 'init' );
	}
	.bind( this );

	var fetchFail = function()
	{
		console.error( 'Cannot fetch data' );
		jQuery( this ).triggerHandler( 'fail' );
	}
	.bind( this );

	return rootSeries.fetch( opt.from, opt.until ).then( draw )
	.fail( fetchFail );
};


/** Begins polling this `BW.ChartGroup`s charts for data. */
BW.ChartGroup.prototype.startPolling = function()
{
	if (this._isPolling)
	{
		console.warn( "Polling already active" );
		return;
	}

	var pollOnce = function()
	{
		var interval = 1000 * (this.getInterval() || this.model.aggregationIntervals[0]);
		this._isPolling = window.setTimeout( pollOnce,  interval );
		this._updateForLiveMode();
	}
	.bind( this );

	pollOnce();
	console.debug( "Polling started" );
};


/** Stops polling this `BW.ChartGroup`s charts for data. Noop if not polling. */
BW.ChartGroup.prototype.stopPolling = function()
{
	if (!this._isPolling) return;

	console.debug( "Polling stopped" );
	window.clearTimeout( this._isPolling );
	this._isPolling = false;
};


/** Called once per update interval when polling is active (see `startPolling`). */
BW.ChartGroup.prototype._updateForLiveMode = function()
{
	// shift view range so that upper view bound is "now"
	this.setViewRange();
};


/**
*   Creates and appends required DOM structure for a `BW.Chart` to this
*   `BW.ChartGroup`s `dom.container`.
*/
BW.ChartGroup.prototype._createChartDom = function( /*String*/ id, /*String*/ title )
{
	var elem = jQuery( '<div></div>' );
	elem.addClass( this.options.cssChartContainer );
	elem.appendTo( this.dom.container );
	elem.attr( 'data-chart-title', title );
	elem.attr( 'data-chart-id', id );
	return elem;
};


/** Removes DOM and references to existing `BW.Chart`s and their data. */
BW.ChartGroup.prototype.removeCharts = function()
{
	for (var i in this.charts)
	{
		var c = this.charts[i];
		if (c.dygraph)
		{
			c.dygraph.destroy();
			c.dygraph = null;
		}
		c.dom.container.remove();

		if (c.series && c.series.fetchInProgress)
		{
			c.series.fetchInProgress.abort();
		}
		jQuery( c ).unbind();
	}
	this.charts = [];
};



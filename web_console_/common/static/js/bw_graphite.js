"use strict";

var BW = window.BW || {};


/**
*   Implements data access to a Graphite service. Factory creates
*   L{BW.GraphiteSeries} instances, which implement access to individual data
*   series through the Graphite web query API.
*
*   Typical usage:
*
*       var model = new BW.GraphiteModel( "http://bwsandbox01" );
*       var target = "stat_logger.machine_sgi02.user_matth.process_cellapp0*.stat_Process_CPU";
*       var series = model.getSeries( target );
*
*       function doSomething() {}
*       series.fetch().then( doSomething );
*/
BW.GraphiteModel = function( /*String*/ graphiteHost, /*Object?*/ options )
{
	if (!graphiteHost)
	{
		throw new Error( "Invalid graphiteHost: " + graphiteHost );
	}
	this.host = graphiteHost;

	var opt = this.options = jQuery.extend( {}, BW.GraphiteModel.DEFAULTS, options );

	// Map of String target expression to BW.GraphiteSeries
	this.seriesByTarget = {};

	this.namingScheme = opt.namingScheme
		|| new BW.GraphiteSeries.DefaultNamingScheme();

	this.aggregationIntervals = opt.aggregationIntervals;
	this.aggregationPeriods = opt.aggregationPeriods;
	assert( this.aggregationIntervals.length >= this.aggregationPeriods.length );

	console.debug(
		"graphite host: '%s'; aggregation intervals: %O, period: %O (secs)",
		this.host, this.aggregationIntervals, this.aggregationPeriods
	);
};


BW.GraphiteModel.DEFAULTS =
{
	// fetch an additional 2sec of data for the case where points within 1
	// interval of now do not contain data and are shaved.
	defaultFrom: "-302s",
	fetchUrl: "/render",
	allMetricsUrl: "/metrics/index.json",
	searchMetricsUrl: "/metrics/find?format=completer&query=",
	namingScheme: null, // BW.GraphiteSeries.DefaultNamingScheme

	// Array of integer seconds corresponding to the period represented by
	// a single point at each aggregation level.
	aggregationIntervals: [2, 20, 300, 3600, 86400],

	// Array of integer seconds corresponding to the total period covered
	// by each aggregation level.
	aggregationPeriods: [86400, 172800, 2592000, 31536000, 31536000],
};


BW.GraphiteModel.prototype.getSeries = function( /*String*/ expr )
{
	// check for cached copy
	var series = this.seriesByTarget[expr];
	if (series)
	{
		// console.debug( "(returning cached series: %s)", expr );
		return series;
	}
	else
	{
		// console.debug( "(returning new series: %s)", expr );
		series = new BW.GraphiteSeries( this, expr );
		this.seriesByTarget[expr] = series;
		return series;
	}
};


BW.GraphiteModel.prototype.getSeriesAtResolution =
function( /*BW.Series*/ series, /*int*/ numSeconds )
{
	assert( numSeconds > 0 );
	var targets = series.target.split( '&' );

	var newTargets = [];

	for (var i in targets)
	{
		var expr = targets[i];

		// graphite function syntax is:
		// summarize(<target-expr>,<period-bucket-size>,<aggregation-func-name>)
		// eg: summarize(<target-expr>,"1min","max",true)
		if (expr.match( /^summarize\(/ ))
		{
			// expr is already being aggregated
			// strip leading func name and trailing func arguments
			expr = expr.replace( /^summarize\(\s*/, '' );
			expr = expr.replace( /(?:,\s*[\w"]+\s*){2,3}\)$/, '' );
			// console.debug( "stripped expr: ", expr );
		}


		// no need to summarise if numSeconds resolution == finest resolution
		// of the data known to the model
		var newTarget;
		if (numSeconds === this.aggregationIntervals[0])
		{
			newTarget = expr;
		}
		else
		{
			newTarget = 'summarize('
				+ expr
				+ ',"'
				+ numSeconds
				+ 's","'
				+ (series.aggregationFunc || 'avg')
				+ '")';
		}

		newTargets.push( newTarget );
	}

	return this.getSeries( newTargets.join( '&' ) );
};


/** Query Graphite host for all metrics matching the given filter expression. */
BW.GraphiteModel.prototype.searchMetrics = function( /*String*/ filter )
{
	var url = filter
		? this.host
		+ this.options.searchMetricsUrl
		+ window.encodeURIComponent( filter )
		: this.host
		+ this.options.allMetricsUrl;

	return jQuery.ajax({
		url: url,
		context: this,
		dataType: 'json',
		success: function( /*Object*/ response )
		{
			if (filter)
			{
				assert( response.metrics, "No matching metrics: %O", response );
				console.debug( "Metrics matching filter '%s': %O", filter, response.metrics );
			}
			else
			{
				console.debug( "Fetched all metric names: %O", response );
				this.metricNameList = response;
			}
		},
		error: function()
		{
			console.log( "Failed to search metrics: %s", url );
		},
	});
};


/*~~~~~~~~~~~~~~~~~~~~~~~~~~ class BW.GraphiteSeries ~~~~~~~~~~~~~~~~~~~~~~~~~~~~*/

/**
*   BW.GraphiteSeries encapsulates a Graphite target. A target can be any valid
*   Graphite target expression, including wildcards, and any number of nested
*   function calls, etc. Target expressions that return multiple series will have
*   "child series", and can be retrieved and tested for using the `childSeries`
*   (Map of String target to child BW.GraphiteSeries) and `childSeriesCount`
*   (int) properties.
*
*   Objects of this class are generally expected to be instantiated by the
*   `BW.GraphiteModel.getSeries` method.
*/
BW.GraphiteSeries = function( /*BW.GraphiteModel*/ model, /*String*/ graphiteExpr )
{
	assert( graphiteExpr, "Invalid graphiteExpression: ", graphiteExpr );

	// BW.GraphiteModel
	this.model = model;

	// Map of String:BW.GraphiteSeries
	this.childSeries = {};
	this.childSeriesCount = 0;

	this.target = graphiteExpr;

	this.capacity = 2048;
	this.aggregationFunc = "avg";
};


BW.GraphiteSeries.prototype.groupBy =
function( /*uint*/ pathIndex, /*String*/ aggregationFuncName )
{
	assert( !this.target.matches( /summarize/ ),
		"No support for unwrapping funcs yet" );

	var groupedTarget = 'groupByNode('
		+ this.target
		+ ','
		+ pathIndex
		+ ','
		+ aggregationFuncName
		+ ')';

	return this.model.getSeries( groupedTarget );
};


/**
*   Fetch data for this series (target) for the period given, otherwise
*   from the defaultFrom options to now. Arguments `from` and `until` can be
*   any mix of the following:
*     * a `Date` instance,
*     * a String relative time, eg: '-10min', '-2h', '-4w'
*     * a String absolute time in epoch seconds
*
*   Returns the jQuery.ajax object created. Typical usage:
*
*       function doSomething( data ) { ... }
*       series.fetch( '-10min' ).then( doSomething );
*
*   Remote fetches trigger the `fetch` event on this series' [BW.GraphiteModel],
*   eg:
*
*       jQuery( model ).on( 'fetch', function( event, series, from, until ) { ... } );
*/
BW.GraphiteSeries.prototype.fetch =
function( /*String|Date|Number?*/ from, /*String|Date|Number?*/ until )
{
	if (this.fetchInProgress)
	{
		console.debug( '(fetch in progress)' );
		// return;
		return this.fetchInProgress;
	}

	if (from)
	{
		// String|Date|Number
		if (from.getTime)
		{
			// Date; convert to seconds
			from = Math.floor( from.getTime() / 1000 );
		}
		else if (isFinite( from ))
		{
			// number
			if (from < 0)
			{
				throw new Error( "Invalid 'from' argument: " + from );
			}
		}
		// else take String as given
	}
	else
	{
		var timeRange = this.getFetchedTimeRange();
		if (timeRange)
		{
			// from last received timestamp of existing data
			from = timeRange[1];
		}
		else
		{
			from = this.model.options.defaultFrom;
		}
	}

	if (until)
	{
		if (until.getTime)
		{
			// Date; convert to seconds
			until = Math.floor( until.getTime() / 1000 );
		}
		else if (isFinite( until ))
		{
			// number
			if (until < 0)
			{
				throw new Error( "Invalid 'until' argument: " + until );
			}
		}
		// else take String as given
	}
	else
	{
		until = "now";
	}

	if (from >= until)
	{
		throw new Error( "Fetch from time >= until time" );
	}

	// HACK!!! carbon not returning requested fetch range inexplicably for certain
	// request ranges near "now". Hack is to return without fetching when we
	// get back-to-back fetches for the same time range.
	if (from === this._lastFetchFrom && until === this._lastFetchUntil)
	{
		console.warn( 'ignoring repeat fetch' );
		return {
			then: function( callback )
			{
				// do nothing for 2sec, then call
				setTimeout( callback, 2000 );
			}
		};
	}

	// console.debug( "fetching from %s to %s", from, until );
	return this._fetch( from, until );
};


BW.GraphiteSeries.prototype._fetch = function( from, until )
{
	var model = this.model;
	var targets = this.target.split( '&' );
	var url = model.host + model.options.fetchUrl;

	// ensure hostname begins with protocol prefix else it will be interpreted
	// as a relative URL
	if (!url.match( /^(?:https?:)?\// ))
	{
		console.warn(
			"graphite model host '%s' should have a 'http(s):// prefix (and port)",
			model.host
		);
		url = 'http://' + url;
	}

	var params = {
		target: targets,
		from: from,
		until: until,
		format: 'json',
	};

	this._lastFetchFrom = from;
	this._lastFetchUntil = until;

	jQuery( model ).triggerHandler( 'fetch', [this, from, until] );

	return this._fetchUrl( url, params ).always( function() {
		jQuery( this.model ).triggerHandler( 'fetchComplete', [this, from, until] );
	});
};


BW.GraphiteSeries.prototype._fetchUrl = function( /*String*/ url, /*Object*/ params )
{
	this.fetchInProgress = jQuery.ajax({
		url: url,
		data: params,
		traditional: true,
		dataType: 'json',
		context: this,
		success: this._onFetchSuccess,
		error: this._onFetchError,
	});

	return this.fetchInProgress;
};


BW.GraphiteSeries.prototype._onFetchSuccess = function( /*Object*/ response )
{
	this.fetchInProgress = false;
	if (!response || !response.length)
	{
		new Alert.Info( "No data available" );
	}

	this._shaveRaggedEnds( response );
	this._shaveNullPronePoints( response );
	var datapoints = response[0].datapoints;

	if (!datapoints.length)
	{
		// console.warn( "received 0 points for series: %s", this.target );
		return;
	}

	var fromTime = datapoints[0][1];
	var untilTime = datapoints[datapoints.length - 1][1];

	// console.log(
	// 	"fetched %s points for %s series (%s-%s): %s",
	// 	datapoints.length, response.length,
	// 	fromTime, untilTime,
	// 	this.target
	// );

	var updated = {};
	for (var i in response)
	{
		var target = response[i].target;
		datapoints = response[i].datapoints;

		assert( datapoints[0][1] === fromTime,
			"Unmatched fromTime (%s, expected: %s) for series: %s",
			datapoints[0][1], fromTime, target );

		assert( datapoints[datapoints.length - 1][1] === untilTime,
			"Unmatched untilTime (%s, expected: %s) for series: %s",
			datapoints[datapoints.length - 1][1], untilTime, target );

		var series = this.model.getSeries( target );

		if (target != this.target)
		{
			// this is a wildcard series
			if (!this.childSeries[target])
			{
				this.childSeriesCount++;
			}
			this.childSeries[target] = series;
		}

		jQuery( this.model ).triggerHandler( 'update', [series, datapoints] );
		series.update( datapoints );
		updated[target] = true;
	}

	if (!updated[this.target])
	{
		jQuery( this.model ).triggerHandler( 'update', [this] );
	}
};


BW.GraphiteSeries.prototype._onFetchError = function( xhr, /*String*/ status )
{
	this.fetchInProgress = false;
	// console.log( "No data returned for series: '%s'", this.target );
};


BW.GraphiteSeries.prototype.abortFetch = function()
{
	if (this.fetchInProgress)
	{
		console.debug( "(aborting series fetchInProgress)" );
		this.fetchInProgress.abort();
		this.fetchInProgress = false;
	}
}


/**
 *	Check whether given range(from, until) intersects with ongoing fetch
 */
BW.GraphiteSeries.prototype.intersectFetch = function( /*int*/ from,
														/*int*/ until )
{
	if (this.fetchInProgress)
	{
		if (from > this._lastFetchUntil || until < this._lastFetchFrom)
		{
			return false;
		}
		else
		{
			return true;
		}
	}
	
	return false;
}



/**
*   Culls points that are within 1 interval of now, as Graphite will frequently
*   and incorrectly return nulls for these points.
*/
BW.GraphiteSeries.prototype._shaveNullPronePoints = function( /*Array of Object*/ rawData )
{
	if (!rawData.length) return;

	var points = rawData[0].datapoints;
	if (!points.length) return;

	var now = Date.now() / 1000;
	var interval = points.length > 1
		? points[1][1] - points[0][1]
		: this.model.aggregationIntervals[0];

	var cutoffTime = now - (now % interval);
	if (points[points.length - 1][1] >= cutoffTime)
	{
		// console.debug( "shaving null-prone points" )
		for (var i in rawData)
		{
			rawData[i].datapoints.pop();
		}
	}
};


/**
*   Graphite occasionally returns series with start/end times that are off by one;
*   that is, one or more series arrays are longer than others by 1. This causes
*   graphics and fetching glitches due to unpredictable holes and overlaps in
*   requested data so this method ensures all returned data has the same start
*   & end time.
*/
BW.GraphiteSeries.prototype._shaveRaggedEnds = function( /*Array of Object*/ rawData )
{
	assert( rawData.length );
	if (rawData.length === 1) return;
	// if (rawData[0].datapoints.length === 1) return;

	// console.dir( rawData );
	var maxStartTime = Math.max.apply( Math, rawData.map(
		function( d ) { return d.datapoints.length ? d.datapoints[0][1] : 0; } ) );

	var minEndTime = Math.min.apply( Math, rawData.map(
		function( d ) { return d.datapoints.length
			? d.datapoints[d.datapoints.length - 1][1] : Infinity; }) );

	assert( isFinite( maxStartTime ) );
	assert( maxStartTime <= minEndTime );

	// console.debug( "data range: %s-%s", maxStartTime, minEndTime );
	var numShavings = 0;
	for (var i in rawData)
	{
		var datapoints = rawData[i].datapoints;
		if (!datapoints.length) continue;

		if (datapoints[0][1] < maxStartTime)
		{
			console.warn( "shaving data from start of ", rawData[i].target );
			datapoints.shift();
			numShavings++;
			assert(
				datapoints.length === 0 ||
				datapoints[0][1] === maxStartTime,
				"datapoints still not even: %s != %s", maxStartTime,
				datapoints[0][1]
			);
		}

		if (datapoints[datapoints.length - 1][1] > minEndTime)
		{
			// console.warn( "shaving data from end of ", rawData[i].target );
			datapoints.pop();
			numShavings++;
			assert(
				datapoints.length === 0 ||
				datapoints[datapoints.length - 1][1] === minEndTime,
				"datapoints still not even: %s != %s", minEndTime,
				datapoints[datapoints.length - 1][1]
			);
		}

		// assert( datapoints.length );
	}

	if (numShavings)
	{
		console.debug( "(shaved %s ragged points from %s series)",
			numShavings, rawData.length );
	}
};


/** Discards all points. */
BW.GraphiteSeries.prototype.clear = function()
{
	if (this.childSeriesCount > 0)
	{
		var childSeries = this.getChildSeries();
		for (var i in childSeries)
		{
			childSeries[i].clear();
		}
		return;
	}

	this.data = null;
};


/** Adds the given data to existing series data (if existing). */
BW.GraphiteSeries.prototype.update = function( /*Array of Array*/ data )
{
	assert( data );

	if (!data.length)
	{
		// console.debug( "(data update is empty, ignoring)" );
		return;
	}

	if (!this.data)
	{
		this.data = data;
		return;
	}

	// console.debug(
	// 	"existing data range: %s-%s, new data range %s-%s"
	// 	, this.data[0][1]
	// 	, this.data[this.data.length - 1][1]
	// 	, data[0][1]
	// 	, data[data.length - 1][1]
	// );

	var mergedData = this._mergeOverlappingArrays( data, this.data );
	if (!mergedData)
	{
		console.warn( "Discarding old data" );
		this.data = data;
		return;
	}

	this.data = mergedData;
};


/**
*   Assumes (requires) arrays of form:
*
*      [[<value_1>, <timestamp_1>], [<value_n>, <timestamp_n>]]
*
*   Arrays must be sorted by timestamp, timestamps must be integers & points
*   must have evenly distributed timestamps.
*/
BW.GraphiteSeries.prototype._mergeOverlappingArrays =
function( /*Array of Array*/ data, /*Array of Array*/ data2 )
{
	if (!data2.length) return data;
	if (!data.length) return data2;

	// used to test the difference of values at the same timepoint in the 2 arrays
	var valuesAreDifferent = function( v1, v2 )
	{
		if (v1 === v2) return false;
		if (v1 === null || v2 === null) return false;
		return (Math.abs( v1 - v2 ) / (v1 || v2 || 0.5) > 0.5); // 50%
	}

	// we pick the earliest array to be the destination array as it will also
	// be the longest one in the common case, and it's faster in JS to extend
	// arrays to the right.
	var dest, src;
	if (data[0][1] < data2[0][1])
	{
		dest = data;
		src = data2;
	}
	else
	{
		dest = data2;
		src = data;
	}

	// console.debug(
	// 	"dest range %s-%s, src range %s-%s",
	// 	dest[0][1], dest[dest.length - 1][1], src[0][1], src[src.length - 1][1]
	// );

	var interval = (dest[dest.length - 1][1] - dest[0][1])
		/ Math.max( 1, dest.length - 1 );

	var intervalSrc = (src[src.length - 1][1] - src[0][1])
		/ Math.max( 1, src.length - 1 );

	// console.log( "intervals: %s %s", interval, intervalSrc );

	// sanity checks
	assert( interval > 0, "expected interval to be > 0: " + interval );
	assert( isFinite( interval ), "expected interval to be an int: " + interval );

	// check src & dest intervals are equal (except if src length is 1).
	if (src.length !== 1 && interval !== intervalSrc)
	{
		console.error(
			"array point intervals not equal: " +
			"dest interval=%s, src interval=%s, dest range=%s-%s, src range=%s-%s",
			interval, intervalSrc,
			dest[0][1], dest[dest.length - 1][1],
			src[0][1], src[src.length - 1][1]
		);
		return;
	}

	// check that there is not a >1 interval gap between dest & src
	if (src[0][1] > dest[dest.length - 1][1] + interval)
	{
		console.error(
			"Arrays have a gap of %s (gap = %s-%s; interval = %s)",
			(dest[dest.length - 1][1] - src[0][1]),
			dest[dest.length - 1][1], src[0][1], interval
		);
		return;
	}

	// merge the arrays. array index in dest should be a constant offset from
	// the same timepoint in src
	var destIndex;
	var destOffset = dest[0][1];
	var destMaxIndex = dest.length - 1;
	var indexOffset = (src[0][1] - dest[0][1]) / interval;

	assert( indexOffset >= 0, "expected indexOffset >= 0: %s", indexOffset );
	assert( isFinite( indexOffset ), "expected integer: %s", indexOffset );

	// iterate backwards through src in order to resize dest once, to its
	// max size on first iteration.
	for (var i = src.length - 1; i >= 0; i--)
	{
		destIndex = i + indexOffset;
		if (destIndex === destMaxIndex)
		{
			// values at the same timepoint should theoretically be identical,
			// in practise, when looking at an aggregated period (ie: use of
			// `summarize` function), the endpoints of existing and incoming
			// series data may differ by a small amount.

			// // compare only 1 point and stop copying array at this point.
			// if (valuesAreDifferent( dest[destIndex][0], src[i][0] ))
			// {
			// 	console.warn(
			// 		"Value of end points at time %s are different: %s@i%s != %s@i%s",
			// 		dest[destIndex][1], dest[destIndex][0], destIndex,
			// 		src[i][0], i
			// 	);
			// }

			// console.log( "arrays intersect at dest index %s, src index %s", destIndex, i );
			break;
		}

		// copy point
		dest[destIndex] = src[i];
	}

	return dest;
};


/**
*   Returns [<earliest timestamp>, <oldest timestamp>] in seconds.
*/
BW.GraphiteSeries.prototype.getFetchedTimeRange = function()
{
	if (this.childSeriesCount > 0)
	{
		var childSeries = this.getChildSeries();
		return childSeries[0].getFetchedTimeRange();
	}

	if (!this.data || !this.data.length) return;

	var oldestPoint = this.data[this.data.length - 1];
	var earliestPoint = this.data[0];

	assert( earliestPoint[1] <= oldestPoint[1] );

	return [earliestPoint[1], oldestPoint[1]];
};


/** Returns the time interval between points in the current series in seconds. */
BW.GraphiteSeries.prototype.getInterval = function()
{
	if (this.childSeriesCount > 0)
	{
		var childSeries = this.getChildSeries();
		return childSeries[0].getInterval();
	}

	if (!this.data) return;

	var data = this.data;
	var timeDelta = (data[data.length - 1][1] - data[0][1]); // msec
	return Math.round( timeDelta / (data.length - 1) );
};


BW.GraphiteSeries.prototype.getDygraphModel = function()
{
	if (this.childSeriesCount)
	{
		// this is a wildcard series; all data hold by childSeries
		var childSeries = this.getChildSeries();
		return this.model.getDygraphModelFor( childSeries );
	}
	else if (this.data)
	{
		// a regular, data-holding series
		return this.data.map(
			function( point ) { return [new Date( 1000 * point[1] ), point[0]]; } );
	}
	else
	{
		console.warn( "No data fetched yet: ", this.target );
		return;
	}
};


BW.GraphiteSeries.prototype.getChildSeries = function()
{
	if (!this.childSeriesCount)
	{
		console.warn( "No child series" );
		return;
	}

	var childSeries = this.childSeries;
	console.assert( childSeries );

	var targetList = Object.keys( childSeries ).sort();
	var seriesList = targetList.map( function( t ) { return childSeries[t]; });

	return seriesList;
};


/**
*   Returns an unsorted Array of String unique statistic names for the
*   current series, as given by the `splitTarget` method of the current
*   `NamingScheme`.
*/
BW.GraphiteSeries.prototype.getUniqueStatisticNames = function()
{
	var targets;
	if (this.childSeriesCount)
	{
		targets = Object.keys( this.childSeries );
	}
	else
	{
		targets = [this.target];
	}

	var namingScheme = this.model.namingScheme;
	var unique = {};

	for (var i in targets)
	{
		var a = namingScheme.splitTarget( targets[i] );
		var name = a[a.length - 1][1];
		unique[name] = true;
	}

	return Object.keys( unique );
};


/**
*   Converts the points of the passed array of BW.GraphiteSeries to
*   Dygraph's native array data structure.
*
*   Graphite data format for _each_ series:
*
*       [[value1, date1], [value2, date2], [value*, date*]]
*
*   Returned Dygraph data format:
*
*       [ [date1, series1Value1, series*Value1],
*         [date2, series1Value2, series*Value2],
*         [date*, series1Value*, series*Value*] ]
*/
BW.GraphiteModel.prototype.getDygraphModelFor =
function( /*Array of BW.GraphiteSeries*/ seriesList )
{
	if (!seriesList || !seriesList.length)
	{
		console.warn( "No series" );
		return;
	}

	var minInterval = Infinity;
	var minTime = Infinity;
	var maxTime = -1;
	var interval;
	var series;
	var min;
	var max;
	var i;

	// find min/max time and min interval (all in seconds)
	for (i = 0; i < seriesList.length; i++)
	{
		series = seriesList[i].data;
		if (!series || !series.length)
		{
			continue;
		}

		min = series[0][1];
		max = series[series.length - 1][1];

		if (min < minTime)
		{
			minTime = min;
		}

		if (max > maxTime)
		{
			maxTime = max;
		}

		if (series.length < 2) continue;

		interval = (max - min) / (series.length - 1);

		if (interval < minInterval)
		{
			minInterval = interval;
		}
		// console.log( "min=%s, max=%s, interval=%s", min, max, interval );
	}
	// console.log( "overall min=%s, max=%s, interval=%s", minTime, maxTime, minInterval );

	if (!min || !max)
	{
		// ie: no series had data
		console.warn( "No series has data" );
		return;
	}

	// check minInterval is an int
	interval = minInterval;
	minInterval = Math.round( minInterval );
	assert( minInterval >= 1 );
	assert( interval === minInterval, "%s != %s", interval, minInterval );

	// allocate data structure
	var numPoints = 1 + ((maxTime - minTime) / minInterval);
	var allPoints = new Array( numPoints );// = seriesList.map( function() { return new Array( numPoints ); } );

	// populate date column
	for (i = 0; i < numPoints; i++)
	{
		allPoints[i] = new Array( seriesList.length + 1 );
		allPoints[i][0] = new Date( 1000 * (minTime + minInterval * i) );
	}

	// populate the data columns
	var seriesPoints, index;
	for (var s = 1; s <= seriesList.length; s++)
	{
		series = seriesList[s - 1].data;

		for (i = 0; i < series.length; i++)
		{
			index = (series[i][1] - minTime) / minInterval;
			allPoints[index][s] = series[i][0];
		}
	}

	return allPoints;
};


/*~~~~~~~~~~~~~~~~~ class BW.GraphiteSeries.DefaultNamingScheme ~~~~~~~~~~~~~~~~~*/

BW.GraphiteSeries.DefaultNamingScheme = function()
{
	// String that separates a path fragment from a path value
	this.pathValueDelimiter = '_';
};


/**
*   Splits a Graphite base target name into an Array of [path-fragment, path-value],
*   eg: graphite target:
*
*       'stat_logger.machine_{sgi02,sgi01}.user_matth.process_*.stat_*'
*
*    would return:
*
*        [ ['stat_logger', null]
*        , ['machine', '{sgi02,sgi01}']
*        , ['user', 'matth']
*        , ['process', '*']
*        , ['stat', '*']
*        ]
*
*   Note: the first path is never split.
*/
BW.GraphiteSeries.DefaultNamingScheme.prototype.splitTarget =
function( /*String*/ baseTarget )
{
	var c = this.pathValueDelimiter || '_';
	var paths = baseTarget.split( '.' );

	paths[0] = [paths[0], null];

	if (paths.length === 1) return paths;

	for (var i = 1; i < paths.length; i++)
	{
		var path = paths[i];
		var idx = path.indexOf( c );
		if (idx === -1)
		{
			paths[i] = [path, null];
			continue;
		}
		paths[i] = [path.substr( 0, idx ), path.substr( idx + c.length )];
	}

	return paths;
};


/**
*   Returns the String target formed by re-joining the given Array form of a
*   target as produced by `splitTarget`.
*/
BW.GraphiteSeries.DefaultNamingScheme.prototype.assembleTarget =
function( /*Array of Array*/ targetPathList )
{
	var c = this.pathValueDelimiter || '_';
	var paths = new Array( targetPathList.length );

	for (var i in targetPathList)
	{
		if (!targetPathList[i][1])
		{
			paths[i] = targetPathList[i][0];
			continue;
		}
		paths[i] = targetPathList[i][0] + c + targetPathList[i][1];
	}

	return paths.join( '.' );
};


/**
*   Extracts and returns the final path ("statistic name") of the passed
*   target expression. Eg: given:
*
*       "stat_logger.machine_sgi02.stat_Machine_CPU"
*
*   this method would return:
*
*       "machine_cpu"
*/
BW.GraphiteSeries.DefaultNamingScheme.prototype.getStatisticName =
function( /*String*/ target )
{
	var targetPaths = this.splitTarget( this.stripTarget( target ) );
	var statName = targetPaths[targetPaths.length - 1][1]
		|| targetPaths[targetPaths.length - 1][0];

	if (!statName)
	{
		console.warn( "Couldn't derive a statistic name for target: %s", target );
		return;
	}

	return statName.toLowerCase();
};


/**
*   Strips any/all graphite functions from the current series target expression.
*   Eg: given:
*
*       "averageSeriesWithWildcards(stat_logger.machine_{sgi01,sgi02}.stat_*,1)"
*
*    this method would return:
*
*        "stat_logger.machine_{sgi01,sgi02}.stat_*"
*
*/
BW.GraphiteSeries.DefaultNamingScheme.prototype.stripTarget =
function( /*String*/ targetExpr )
{
	if(!targetExpr || !targetExpr.length )
		throw new Error( "Invalid target expression: " + targetExpr );

	// attempts to strip function prefix/suffix
	return targetExpr.replace( /^.+\(/, '' ).replace( /,[^}]+$/, '' );
};


/*~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ testing ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~*/

var Test = Test || {};
Test.BW = Test.BW || {};
Test.BW.GraphiteModel = {};
Test.BW.GraphiteModel.HOST = 'http://bwsandbox01';

Test.BW.GraphiteModel.fetch = function()
{

	var target = "stat_logger.machine_*.user_matth.process_baseappmgr.stat_Process_CPU&stat_logger.machine_*.user_matth.process_cellappmgr.stat_Process_CPU"
	var model  = new BW.GraphiteModel( Test.BW.GraphiteModel.HOST );
	var series = model.getSeries( target );

	series.fetch( "-5min", "now" );
};



Test.BW.GraphiteModel.getDygraphModelFor = function()
{
	var model  = new BW.GraphiteModel( Test.BW.GraphiteModel.HOST );

	var now = Math.floor( Date.now() / 1000 );
	var s1 = { data: [[0.1, now], [0.2, now + 2], [0.3, now + 4]] };
	var s2 = { data: [            [0.2, now + 2], [0.3, now + 4]] };
	var s3 = { data: [[0.1, now],                 [0.3, now + 4]] };
	var s4 = { data: [[0.1, now], [0.2, now + 2]                ] };
	var s5 = { data: [] };

	var result = model.getDygraphModelFor( [s1, s2, s3, s4, s5] );
	assert( result[0][2] === undefined );
	assert( result[1][3] === undefined );
	assert( result[2][4] === undefined );
};


Test.BW.GraphiteSeries = {};

Test.BW.GraphiteSeries.mergeOverlappingArrays = function()
{
	var t = 1;
	var mergeArrays = BW.GraphiteSeries.prototype._mergeOverlappingArrays;

	var testMergeArrays = function( a1, a2 )
	{
		console.log( "test %s: merging %O and %O", t++, a1, a2 );
		var a = mergeArrays( a1, a2 );

		console.log( "merged: %O", a );
		var len = 1 + ((a2[a2.length - 1][1] - a1[0][1]) / (a1[1][1] - a1[0][1]));
		assert( a && a.length === len );
	}

	testMergeArrays(
		[[1, 100], [1, 102], [1, 104], [1, 106]],
		[[1, 104], [1, 106], [1, 108], [1, 110], [1, 112], [1, 114], [1, 116]]
	);

	testMergeArrays(
		[[1, 100], [1, 102], [1, 104], [1, 106]],
		[[1, 106]]
	);

	testMergeArrays(
		[[1, 100], [1, 102], [1, 104], [1, 106]],
		[[1, 108], [1, 110]]
	);

	testMergeArrays(
		[[1, 100], [1, 102], [1, 104], [1, 106]],
		[[1, 100], [1, 102]]
	);
};


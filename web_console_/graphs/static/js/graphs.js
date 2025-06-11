"use strict";

console.dump = console.dump || console.dir.bind( console );

BW.ChartGroup.MAX_CHARTS_PER_PAGE = 6;

var chartGroup;        // BW.ChartGroup
var model;             // BW.GraphiteModel
var chartConfig;       // Object
var params;            // Map of query string param -> value
var topLevelContainer; // jQuery

var prefs = {};
var chartConfigStack = [];
var isLegendShowing = false;

var datePickerShown = false;


// aggregate all stats by process type.
// note that process types with appIDs have to be aggregated specially
var defaultProcessesTarget =
	'averageSeriesWithWildcards(PREFIX.machine_*.user_'
	+ BW.user.effectiveServerUser
	+ '.process_{cellappmgr,baseappmgr,dbmgr,dbappmgr}.stat_*, 1)'
	+ '&'
	+ ['loginapp','cellapp', 'baseapp', 'dbapp', 'serviceapp'].map( function( app ) {
		return (
			'aliasSub(averageSeriesWithWildcards(PREFIX.machine_*.user_'
			+ BW.user.effectiveServerUser
			+ '.process_'
			+ app
			+ '*[0-9].stat_*,1,3),"\.stat",".process_'
			+ app
			+ 's.stat")'
		);
	}).join( '&' );

var defaultProcessGroups = ['cellappmgr', 'baseappmgr', 'dbmgr', 'dbappmgr',
	'loginapps', 'cellapps', 'baseapps', 'dbapps', 'serviceapps'];


jQuery( document ).ready( function()
{
	jQuery( 'select' ).chosen();

	topLevelContainer = jQuery( '.statgrapher-container' );
	topLevelContainer.find( '.specific-time' ).val( new Date().toDateString() );
	attachUiEvents();

	params = document.location.search.substring( 1 ).toMap();

	requestFetchPreferences().then( initPrefs ).then( initApp );
});


function initApp()
{
	var graphiteHost = params.host ? 'http://' + params.host[0] : prefs.model.host;

	if (!graphiteHost)
	{
		new Alert.Error( 'No Graphite-Web service available' );
		return;
	}

	model = new BW.GraphiteModel( graphiteHost, {
		aggregationIntervals: prefs.retention.intervals,
		aggregationPeriods: prefs.retention.periods,
	});


	initFetchNotifications( model );

	// model.searchMetrics().then( initTreeSelect );

	if (params.target && params.target.length)
	{
		var targets = params.target.join( '&' );
		var groups = (params.groups && params.groups.length) ? params.groups : null;

		chartConfig = {
			title: "Graphs",
			targets: targets,
			groups: groups,
			adhoc: true,
		};

		initChartView();
	}
	else if (document.location.href.match( 'process' ))
	{
		initProcessesPage();
	}
	else
	{
		initMachinesPage();
	}
}


/** Extracts series and aggregation settings from stat_logger `preferences.xml`. */
function initPrefs( /*Document*/ xml )
{
	/*global*/ prefs = {};
	var pref = jQuery( xml );

	// extract graphite host
	var graphite = prefs.model = {
		host: window.GRAPHITE_HOST || pref.find( 'carbon host' ).text(),
		port: pref.find( 'carbon port' ).text(),
		prefix: pref.find( 'carbon prefix' ).text(),
	};

	if (!graphite.host || graphite.host === 'localhost')
	{
		// graphite.host = document.location.origin;
		graphite.host = undefined;
		return;
	}

	// extract aggregation config
	var baseInterval = + pref.find( 'options sampleTickInterval' ).text();
	assert( baseInterval > 0 );

	prefs.retention = {};
	var aggregationIntervals = prefs.retention.intervals = [];
	var aggregationPeriods = prefs.retention.periods = [];

	pref.find( 'aggregation window' ).each( function()
	{
		var node = jQuery( this );
		var numPoints = node.children( 'samples' ).text();
		var numSamplesPerPoint = node.children( 'samplePeriodTicks' ).text();

		aggregationIntervals.push( baseInterval * numSamplesPerPoint );
		aggregationPeriods.push( baseInterval * numPoints * numSamplesPerPoint );
	});

	// extract series display preferences
	var seriesPrefs = prefs.series = {};
	pref.find( 'statistic' ).each( function()
	{
		var node = jQuery( this );
		var name = node.children( 'name' ).text();
		var max  = node.children( 'maxAt' ).text();
		var colour = node.find( 'colour' ).text();

		// convert preferences.xml name -> graphite name
		name = name.replace( /\s/g, '_' ).replace( /[\(\)]/g, '' ).toLowerCase();
		assert( !seriesPrefs[name], "duplicate stat name '%s'", name );

		seriesPrefs[name] = {
			name: name,
			max: + max,
			colour: colour,
		};
	});

	console.debug( 'loaded statlogger preferences: %O', prefs );

	assert( prefs.model.prefix );
	defaultProcessesTarget = defaultProcessesTarget.replace(
		/PREFIX/g, prefs.model.prefix );
}


function initProcessesPage()
{
	/* Processes page */
	topLevelContainer.addClass( 'processes' );
	topLevelContainer.removeClass( 'machines' );
	topLevelContainer.find( 'h2' ).first().html( 'Process Graphs' );

	// var defaultProcessGroups = ['CPU', 'Memory', 'Load', 'Bases', 'Services', 'Entities',
	// 	'Witnesses', 'Proxies', 'AoI', 'Spaces', 'Cell'];
	chartConfig = {
		chartGroupId: "All Processes",
		targets: defaultProcessesTarget,
		groups: defaultProcessGroups,
	};

	if (params.process && params.process.length)
	{
		chartConfigStack.push( jQuery.extend( {}, chartConfig ) );
		chartConfig = { chartGroupId: params.process.join( ',' ) };
		buildGraphiteTargetForProcesses( params.process );
		initChartView();
		return;
	}

	initChartView();
}


function initMachinesPage()
{
	/* Machines page */
	chartConfig = {};
	chartConfig.chartGroupId = 'All Machines';
	topLevelContainer.addClass( 'machines' );
	topLevelContainer.removeClass( 'processes' );
	topLevelContainer.find( 'h2' ).first().html( 'Machine Graphs' );

	if (params.machine && params.machine.length)
	{
		buildGraphiteTargetForMachines( params.machine );
		initChartView();
		return;
	}

	var searchFail = function()
	{
		var graphiteHost = params.host ? 'http://' + params.host[0] : prefs.model.host;
		console.error( 'Cannot fetch data' );
		new Alert.Error( 'Cannot fetch data from ' + graphiteHost );
	}
	.bind( this );

	// need to query graphite for list of metrics names
	// before initialising charts.
	model.searchMetrics( prefs.model.prefix + '.machine_*' ).then(
		function( response )
		{
			var machineNames = extractUniqueNames( response );
			buildGraphiteTargetForMachines( machineNames );
			initChartView();
		}
	).fail( searchFail );
}


function enterStatisticsView()
{
	var statNames = chartGroup.rootSeries.getUniqueStatisticNames();
	statNames.sort();

	// statistic view is simply grouping current target set by statistic instead
	// of by process type or machine group.
	chartConfig.chartGroupId = "by statistic";
	chartConfig.groups = chartConfig.titles = statNames;

	// anchor statistic name match to end of stat name so as to avoid including
	// targets that have _Min/_Max/etc suffixes. This blows out the number of
	// charts shown but avoids adding a bunch of additional series names to
	// the legend.
	chartConfig.groups = statNames.map( function( n )
	{
		return new RegExp( 'stat_' + n + '$' );
	});

	chartConfig.chartOptions =
	{
		normaliseY: false,
		axes: {
			y: {
				drawAxis: true
			}
		},
		labelGenerator: function( /*Array of String*/ targets )
		{
			// extract process/machine name from targets
			var labels = new Array( targets.length );
			var namingScheme = model.namingScheme;

			for (var i = 0; i < targets.length; i++)
			{
				var target = namingScheme.stripTarget( targets[i] );
				var targetPaths = namingScheme.splitTarget( target );

				for (var j = 0; j < targetPaths.length; j++)
				{
					if (targetPaths[j][0] === 'process')
					{
						labels[i] = targetPaths[j][1];
						break;
					}
					else if (targetPaths[j][0] === 'machine')
					{
						labels[i] = targetPaths[j][1];
						break;
					}
				}

				assert( labels[i],
					"Expected a process or machine qualifier: %s", target );
			}

			// x-axis label has to be at index 0
			labels.unshift( 'time' );

			return labels;
		},
	};

	initChartView();

	// update UI
	topLevelContainer.addClass( 'by-statistic-view' );
	topLevelContainer.find( '.toggle-statistic-view.button' ).addClass( 'depressed' );
	
	// Y axis will be displayed
	uiEnableYAxis();
}

function exitStatisticsView()
{
	topLevelContainer.removeClass( 'by-statistic-view' );
	topLevelContainer.find( '.toggle-statistic-view.button' ).removeClass( 'depressed' );

	// simply reload the current chartConfig
	loadConfig( -1 );
}


function attachUiEvents()
{
	// init time picker event
	initTimePicker();
	
	// select a view period
	jQuery( ':input.time-range-control' ).change(
		function( ev )
		{
			var timeRangeSecs = jQuery( this ).val();
			chartGroup.setViewRange( timeRangeSecs );
			topLevelContainer.removeClass( 'custom-time-range' );

			// if in live mode, also snap to end as live mode may be
			// unintentionally disabled when changing from a lower resolution
			// to a higher one and the view is no longer within 1 (new) interval
			// of now.
			if (chartGroup._isPolling)
			{
				// snap to now
				chartGroup.setViewRange();
			}
		}
	);

	// skip view period to now
	jQuery( '.skip-to-end-control' ).click(
		function( ev ) { chartGroup.setViewRange(); } );

	// show/hide gaps
	jQuery( '.smoothing-control' ).click( function( ev )
	{
		if (topLevelContainer.hasClass( 'gaps-hidden' ))
		{
			topLevelContainer.removeClass( 'gaps-hidden' );
			topLevelContainer.find( '.smoothing-control.button' ).removeClass( 'depressed' );
			chartGroup.showGaps( true );
		}
		else
		{
			topLevelContainer.addClass( 'gaps-hidden' );
			topLevelContainer.find( '.smoothing-control.button' ).addClass( 'depressed' );
			chartGroup.showGaps( false );
		}
	});

	// show/hide legend
	jQuery( '.legend-control' ).toggle( showLegend, hideLegend );

	// highlight series in charts when mouseovering a series in the legend
	topLevelContainer.on( 'mouseenter', '#chart-legend .series', function( ev )
	{
		if (!chartGroup) return;
		if (!chartGroup.charts) return;

		var seriesId = jQuery( this ).attr( 'data-label' );

		setLegendSelectedSeries( seriesId );
	});

	// unhighlight series in charts when mouseleaving
	topLevelContainer.on( 'mouseleave', '.showing-legend #chart-legend', function( ev )
	{
		clearLegendSelectedSeries();
		clearLegendState();
		clearLegendSeriesData();
	});

	topLevelContainer.on( 'mouseenter', '.chart-container', function( ev )
	{
		if (!isLegendShowing) return;

		topLevelContainer.find( '#chart-legend' ).removeClass( 'prevent-updates' );
	});

	topLevelContainer.on( 'mouseleave', '.chart-container', function( ev )
	{
		if (!isLegendShowing) return;

		clearLegendSelectedSeries();
		clearLegendState();
		clearLegendSeriesData();

		topLevelContainer.find( '#chart-legend' ).addClass( 'prevent-updates' );
	});

	// toggle "by statistic" view
	jQuery( '.toggle-statistic-view' ).click( function()
	{
		var control = jQuery( this );
		if (topLevelContainer.hasClass( 'by-statistic-view' ))
		{
			exitStatisticsView();
		}
		else
		{
			enterStatisticsView();
		}
	});

	// show/hide y axis
	jQuery( '.toggle-y-axis' ).click( toggleYAxis );

	// time (x-axis) control
	jQuery( '.custom-time-range' ).click( function()
	{
		topLevelContainer.removeClass( 'custom-time-range' );
		chartGroup.charts[0].dygraph.resetZoom();
	});

	// toggle live mode
	jQuery( '.live-mode-control' ).click( toggleLiveMode );

	// click on machines chart title "drills into" that machine-group
	jQuery( document ).on( 'click', '.machines:not( .by-statistic-view ) .dygraph-title', function( ev )
	{
		if (!chartConfig) return;

		var chartContainer = jQuery( this ).parents( '.chart-container' ).first();
		assert( chartContainer.length,
			"Element %O does not have a .chart-container parent", this );

		var chartId = chartContainer.attr( 'data-chart-id' );
		assert( chartId, "Chart container %O does not have a 'data-chart-id' attr",
			chartContainer );

		if (chartId === chartConfig.chartGroupId)
		{
			// we're already showing this graph
			return false;
		}

		assert( chartId, "No 'data-chart-id' attribute: %O", chartContainer );
		var groupList = chartConfig.groupsByAlias[chartId];
		console.debug( "selection group: %O", groupList );

		console.debug( "redrawing charts: %s", chartId );
		buildGraphiteTargetForMachines( groupList );
		chartConfig.chartGroupId = chartId;
		initChartView();
	});

	// click on processes chart title drills into that process-type/process group
	jQuery( document ).on( 'click', '.processes:not( .by-statistic-view ) .dygraph-title', function( ev )
	{
		var chartContainer = jQuery( this ).parents( '.chart-container' );
		var chartId = chartContainer.attr( 'data-chart-id' );
		assert( chartId, "No 'data-chart-id' attribute: %O", chartContainer );

		if (chartId === chartConfig.chartGroupId)
		{
			// we're already showing this graph
			return false;
		}

		if (chartConfig.groupsByAlias)
		{
			// then we're drilling into a group of processes
			var groupList = chartConfig.groupsByAlias[chartId];
			console.debug( "selection group: %O", groupList );

			console.debug( "redrawing charts: %s", chartId );
			buildGraphiteTargetForProcesses( groupList );
			chartConfig.chartGroupId = chartId;

			initChartView();
		}
		else if (chartId.match( /mgr$/ ))
		{
			// then we're drilling into a mgr process
			chartConfig.targets = prefs.model.prefix
				+ '.machine_*.user_'
				+ BW.user.effectiveServerUser
				+ '.process_'
				+ chartId
				+ '.stat_*';
			chartConfig.groups = [chartId];
			chartConfig.chartGroupId = chartId;

			initChartView();
		}
		else if (chartId.match( /apps$/ ))
		{
			// then we're drilling into a app group
			var filter = prefs.model.prefix
				+ '.machine_*.user_'
				+ BW.user.effectiveServerUser
				+ '.process_'
				+ chartId.replace( /s$/, '' )
				+ '[0-9]*';

			// lookup apps
			model.searchMetrics( filter ).then(
				function( response )
				{
					var processNames = extractUniqueNames( response );
					buildGraphiteTargetForProcesses( processNames );
					chartConfig.chartGroupId = chartId;
					initChartView();
				}
			);
		}
		else
		{
			assert( false, "unexpected chart title: '%s'", chartId );
		}
	});
}


function initTimePicker()
{
	var timeInput = jQuery( 'input.specific-time' );
	var calendarIcon = jQuery( '.calendar-button' );
	
	timeInput.datetimepicker({
		dateFormat: 'D d M yy',
		// note: millisecs support but doesn't handle millisec values
		// without exactly 3 digits
		// timeFormat: 'HH:mm:ss.l',
		// showMillisec: true,
		timeFormat: 'HH:mm:ss',
		showSecond: true,
		showButtonPanel: false,
		firstDay: 1, // Monday
		alwaysSetTime: false,
		maxDateTime: new Date(),
		
		onClose: timePickerClosed,

		beforeShow: function( text, datePickerInst )
		{
			// Before picker is shown, set max date time to now **WOT-732**
			datePickerInst.settings.maxDateTime = new Date();

			// Inject our own action button to timepicker.
			// HAVE to hack the timepicker. When we switch month on the
			// timepick pane, the whole pane will be redrawn. However, there is
			// no events to hook to redraw our Cancel/Go button pane when the
			// timepicker gets redrawn, as the exposed onSelect or onChange call
			// back will be called before redrawing timepicker pange. Here we
			// hack the timepicker function of injecting time pane. And it seems
			// there will be only one timepicker instance, so we have to check
			// whether it has been already hacked, otherwise this will cause
			// infinite loop.
			var timePickerInst = datePickerInst.settings.timepicker;
			if (timePickerInst._base_addTimePicker === undefined)
			{
				timePickerInst._base_addTimePicker = timePickerInst._addTimePicker;
				timePickerInst._addTimePicker = function( inst ) {
					this._base_addTimePicker( inst );
					beforeShowTimePicker( inst.dpDiv );
				}
			}
			
		}
	});
	
	calendarIcon.mousedown( toggleTimePicker );

	timeInput.focus( function()
	{
		jQuery( this ).select();
		
		// need to update some css of timepicker		
		modifyTimePickerStyle();
	} );
	
	timeInput.blur( function()
	{
		// keep the time text input focused when time picker is shown, which
		// will cause the text in that field to be selected
		if (datePickerShown)
		{
			timeInput.focus();
		}
	} );
}


function toggleTimePicker( /*Object*/ event )
{
	if (datePickerShown)
	{
		hideTimePicker();
	}
	else
	{
		showTimePicker();
	}
	
	// stop propagation of this event, because timepicker hook on the event of
	// the root document
	event.stopPropagation();
}


function showTimePicker()
{
	// trigger the focus event of the time input element which will trigger the
	// time picker to show
	jQuery( 'input.specific-time' ).focus();
}

function hideTimePicker()
{
	// currently, this is the only way we have found out to hide the time picker
	topLevelContainer.mousedown();
}


function beforeShowTimePicker( /*jQuery Object*/ parentDiv )
{
	// avoid duplicate insertion of our button
	if (parentDiv.find("div.datepicker-button-pane").length === 0)
	{
		// generate and insert element
		var actionPane = jQuery( "<div class='datepicker-button-pane'/>" );
		var cancelButton = jQuery(
				"<button class='cancel-button'>Cancel</button>" );
		var goButton = jQuery(
				"<button class='go-button'>Go</button>" );
		
		actionPane.append( cancelButton );
		actionPane.append( goButton );

		parentDiv.append( actionPane );

		// hook event		
		jQuery("button.go-button").mousedown( function( ev )
		{
			hideTimePicker();
			selectTime( jQuery( "input.specific-time" ).val() );
			
		} );
		
		jQuery("button.cancel-button").mousedown( function( ev )
		{
			hideTimePicker();
		} );

		datePickerShown = true;
		topLevelContainer.addClass( "date-picker-shown" );
		jQuery( '.calendar-button' ).addClass( "depressed" );
		
		modifyTimePickerStyle();
	}
}


function timePickerClosed()
{
	datePickerShown = false;
	topLevelContainer.removeClass( "date-picker-shown" );
	jQuery( '.calendar-button' ).removeClass( "depressed" );
}


function selectTime( /*string*/ endTime )
{
	var range = chartGroup.charts[0].getViewRangeX();
	var rangeEnd = Date.parse( endTime ) / 1000;
	var newRange = new Array();
	
	
	newRange[0] = range[0] - ( range[1] - rangeEnd )
	newRange[1] = rangeEnd;
	
	disableLiveMode();
	chartGroup.setViewRangeX( newRange );
}


// change some css style of time picker
function modifyTimePickerStyle()
{
	jQuery('#ui-datepicker-div').css( {
		"z-index": 999,
	} );
		
	jQuery("dd.ui_tpicker_time").css( {
		"font-weight": "bold",
	} );
}


function toggleLiveMode()
{
	if (chartGroup._isPolling)
	{
		disableLiveMode();
	}
	else
	{
		enableLiveMode();
	}
}


/**
*   Live mode continuously polls for new data and forces upper time bound to stay
*   within 0 - <current interval> sec of now.
*/
function enableLiveMode()
{
	topLevelContainer.addClass( 'live-mode' );
	topLevelContainer.find( '.live-mode-control.button' ).addClass( 'depressed' );
	chartGroup.startPolling();
}


function disableLiveMode()
{
	topLevelContainer.removeClass( 'live-mode' );
	topLevelContainer.find( '.live-mode-control.button' ).removeClass( 'depressed' );
	chartGroup.stopPolling();
}


function isInLiveMode()
{
	return topLevelContainer.hasClass( 'live-mode' );
}


function toggleYAxis()
{		
	if (topLevelContainer.hasClass( 'show-y-axis' ))
	{
		uiDisableYAxis();		
		chartGroup.showYAxis( false );
	}
	else
	{
		uiEnableYAxis();
		chartGroup.showYAxis( true );
	}
}


function uiDisableYAxis()
{
	topLevelContainer.removeClass( 'show-y-axis' );
	topLevelContainer.find( '.toggle-y-axis.button' ).removeClass( 'depressed' );
}


function uiEnableYAxis()
{
	topLevelContainer.addClass( 'show-y-axis' );
	topLevelContainer.find( '.toggle-y-axis.button' ).addClass( 'depressed' );
}


/** Extract unique names from a graphite metric name lookup response. */
function extractUniqueNames( /*Object*/ response )
{
	assert( response );
	assert( response.metrics.length );

	var seen = {};
	return response.metrics.map(
		function( m ) { return m.name.replace( /^[a-z]+_/, '' ); } ).filter(
		function( m ) { if (seen[m]) return false; return (seen[m] = true); } );
}


/**
*   Partition given array into up to `maxGroups` sub-arrays. This implementation
*   favours even-length sub-arrays over evenly-distributed sub-array lengths.
*/
function partition( /*Array*/ list, /*uint*/ maxGroups ) /*returns Array of Array*/
{
	var numNamesPerChart = Math.ceil( list.length / (maxGroups || list.length) );
	var groupNames = [];

	for (var i = 0; i < list.length; i++)
	{
		if (i % numNamesPerChart)
		{
			groupNames[groupNames.length - 1].push( list[i] );
		}
		else
		{
			groupNames.push( [list[i]] );
		}
	}

	return groupNames;
}


function buildGraphiteTargetForMachines( /*Array of String*/ machineNames )
{
	assert( chartConfig );
	assert( machineNames.length );

	var targets = [];
	chartConfig.groups = [];
	chartConfig.titles = [];
	chartConfig.groupsByAlias = {};
	var groupNames = partition( machineNames, BW.ChartGroup.MAX_CHARTS_PER_PAGE );

	for (var i in groupNames)
	{
		var groupList = groupNames[i];
		var selectionExpression = groupList.join( ',' );
		var groupAlias = groupList.length > 1
			? groupList[0] + '-' + groupList[groupList.length - 1]
			: groupList[0];

		var title = groupList[0];
		if (groupList.length > 1)
		{
			title += ' - '
				+ groupList[groupList.length - 1]
				+ ' ('
				+ groupList.length
				+ ' machines)';
		}

		var targetExpr = 'aliasSub(averageSeriesWithWildcards('
			+ prefs.model.prefix
			+ '.machine_{'
			+ selectionExpression
			+ '}.stat_*, 1),"^'
			+ prefs.model.prefix
			+ '","'
			+ prefs.model.prefix
			+ '.machine_'
			+ groupAlias
			+ '")';

		chartConfig.groupsByAlias[groupAlias] = groupList;
		chartConfig.groups.push( groupAlias );
		chartConfig.titles.push( title );
		targets.push( targetExpr );
	}

	chartConfig.targets = targets.join( '&' );
}



function buildGraphiteTargetForProcesses( /*Array of String*/ processNames )
{
	assert( chartConfig );
	assert( processNames.length );

	var targets = [];
	chartConfig.groups = [];
	chartConfig.titles = [];
	chartConfig.groupsByAlias = {};
	var groupNames = partition( processNames, BW.ChartGroup.MAX_CHARTS_PER_PAGE );

	for (var i in groupNames)
	{
		var groupList = groupNames[i];
		var selectionExpression = groupList.join( ',' );
		var groupAlias = groupList.length > 1
			? groupList[0] + '-' + groupList[groupList.length - 1]
			: groupList[0];

		var title = groupList[0];
		if (groupList.length > 1)
		{
			title += ' - ' + groupList[groupList.length - 1];
		}

		var targetExpr =
			'aliasSub(averageSeriesWithWildcards('
			+ prefs.model.prefix
			+ '.machine_*.user_'
			+ BW.user.effectiveServerUser
			+ '.process_{'
			+ selectionExpression
			+ '}.stat_*, 1, 3),"^'
			+ prefs.model.prefix
			+ '","'
			+ prefs.model.prefix
			+ '.process_'
			+ groupAlias
			+ '")';

		chartConfig.groupsByAlias[groupAlias] = groupList;
		chartConfig.groups.push( groupAlias );
		chartConfig.titles.push( title );
		targets.push( targetExpr );
	}

	chartConfig.targets = targets.join( '&' );
	return chartConfig;
}


/**
*   Creates a new `chartGroup` view from current `chartConfig`, preserving current
*   view range (if any). Discards/disposes existing chartGroup. Old
*   `chartConfig` will still exist as the 2nd to last element of `chartConfigStack`
*   on return; new `chartConfig` will be last element.
*/
function initChartView()
{
	console.info( "initialising view '%s'", chartConfig.chartGroupId );

	var wasInLiveMode = chartGroup && chartGroup._isPolling;
	if (wasInLiveMode)
	{
		chartGroup.stopPolling();
	}

	// preserve view range of current BW.ChartGroup
	var viewRange;
	if (chartGroup)
	{
		viewRange = chartGroup.getViewRangeX();
		chartGroup.removeCharts();
	}

	// merge config options: param options > chartConfig options
	var showYAxis = topLevelContainer.hasClass( 'show-y-axis' );
	var uiState = {
		connectSeparatedPoints: topLevelContainer.hasClass( 'gaps-hidden' ),
		axes: {
			y: {
				drawAxis: showYAxis
			}
		}
	};
	var chartConfigOptions = chartConfig.chartOptions || {};
	var paramOptions = params.chartOptions
		? JSON.parse( decodeURIComponent( params.chartOptions[0] ) ) : {};
	var chartOptions = jQuery.extend( true, {}, uiState, chartConfigOptions, paramOptions );

	if (chartOptions.connectSeparatedPoints)
	{
		topLevelContainer.find(
			'.smoothing-control.button' ).addClass( 'depressed' );
	}
	
	if (showYAxis)
	{
		topLevelContainer.find(
			'.toggle-y-axis.button' ).addClass( 'depressed' );
	}
	
	if (chartOptions.axes && chartOptions.axes.y.drawAxis)
	{
		uiEnableYAxis();
	}
	else
	{
		uiDisableYAxis();
	}

	var chartGroupOptions = {
		targets: chartConfig.targets,
		groups: chartConfig.groups,
		titles: chartConfig.titles,
		prefs: prefs.series,
		model: model,
		chartOptions: chartOptions,
	};

	if (viewRange)
	{
		if (viewRange[0] > (Date.now() / 1000))
		{
			// viewport is entirely in the future. Allow it to rubberband
			// back to the default view range.
			new Alert.Info(
				"View range has been reset from future to now in " +
				"order to include visible data"
			);
		}
		else
		{
			// set the view range to be the same as previous view
			chartGroupOptions.from = Math.floor( viewRange[0] );
			chartGroupOptions.until = Math.floor( viewRange[1] );
		}
	}

	console.debug(
		'chartGroup options: %O, chart options: %O',
		chartGroupOptions, chartOptions
	);

	chartGroup = new BW.ChartGroup( '.charts-container', chartGroupOptions );

	jQuery( chartGroup ).on( 'init', function()
	{
		if (wasInLiveMode)
		{
			this.startPolling();
		}
		else if (topLevelContainer.hasClass( 'live-mode' ))
		{
			enableLiveMode();
		}

		generateLegend();
	});

	jQuery( chartGroup ).on( 'fail', function()
	{
		var graphiteHost = params.host ? 'http://' + params.host[0] : prefs.model.host;
		new Alert.Error( 'Cannot fetch data from ' + graphiteHost );
	});

	initChartGroupEvents();
	updateBreadcrumbs();
}


/**
*   Render breadcrumb DOM from current `chartConfigStack`.
*/
function updateBreadcrumbs()
{
	if (chartConfig.chartGroupId === 'by statistic') return;

	var breadcrumbsContainer = topLevelContainer.find( '.breadcrumbs' );
	breadcrumbsContainer.empty();

	for (var i in chartConfigStack)
	{
		var config = chartConfigStack[i];

		var link = jQuery( '<li><a href="javascript:loadConfig( '
			+ i
			+ ' )">'
			+ config.chartGroupId
			+ '</a></li>'
		);
		breadcrumbsContainer.append( link );
	}

	if (chartConfigStack.length)
	{
		breadcrumbsContainer.append(
			'<li>' + chartConfig.chartGroupId + '</li>' );
	}

	var chartConfigCopy = jQuery.extend( true, {}, chartConfig );
	chartConfigStack.push( chartConfigCopy );
}


/**
*   Render view of the `chartConfig` corresponding to given index of
*   `chartConfigStack`. Negative indexes count back from tail, eg:
*
*       loadConfig( -1 ); // reload current view
*       loadConfig( -2 ); // reload previous view
*       loadConfig( 0 );  // reload top-level/root view
*/
function loadConfig( /*int*/ i )
{
	if (i < 0) i += chartConfigStack.length;

	chartConfig = chartConfigStack[i];
	chartConfigStack = chartConfigStack.slice( 0, i );

	console.warn( "load config %s: %O", i, chartConfig );
	assert( chartConfig );

	if (topLevelContainer.hasClass( 'by-statistic-view' ))
	{
		enterStatisticsView();
	}
	else
	{
		initChartView();
	}
}


/** Add a bunch of UI events to current `chartGroup` object. */
function initChartGroupEvents()
{
	jQuery( chartGroup.charts[0] ).on( 'draw', function()
	{
		var view = this.getViewRangeX();
		if (!view) return;

		var until = new Date( 1000 * view[1] ).toBigWorldDateString( false );
		
		if (!datePickerShown)
		{
			topLevelContainer.find( '.specific-time' ).val( until );
		}
	});

	// progress stuff
	var progress = {};
	progress.dom = jQuery( '.chart-progress' );

	jQuery( chartGroup.charts[0] ).on(
	{
		changeViewportX: function( x1, x2 )
		{
			var dataRange = this.getDataRangeX();
			var alreadyLoaded = Math.max( 0,
				Math.min( dataRange[1], x2 ) - Math.max( dataRange[0], x1 ) );
		},

		draw: function()
		{
			var viewRange = this.getViewRangeX();
			var dataRange = this.getDataRangeX();
			if (!viewRange || !dataRange) return;

			// console.log( "view: %O, data: %O", viewRange, dataRange );
			var now = Date.now() / 1000; // secs
			var viewSpan = viewRange[1] - viewRange[0];

			var rangeControl = jQuery( ':input[name = "range"]' );
			var rangeControl2 = jQuery( ':input[name = "range_"]' );
			var setTimeRange = rangeControl.val();

			// update time range selector state (if needed)
			var interval = this.getInterval();
			if (Math.abs( viewSpan - setTimeRange ) > interval)
			{
				topLevelContainer.addClass( 'custom-time-range' );
				rangeControl2.val( 'custom' ).trigger( 'liszt:updated' );
			}
			else
			{
				topLevelContainer.removeClass( 'custom-time-range' );
			}

			// cancel liveMode if user has panned
			if (chartGroup._isPolling)
			{
				var interval = this.getInterval();
				if (Math.abs( viewRange[1] - now) > 2 * interval)
				{
					disableLiveMode();
					new Alert.Info( "Live mode suspended" );
				}
			}

			// if still in live mode && legend is showing, show live values
			if (chartGroup._isPolling && isLegendShowing)
			{
				var legend = topLevelContainer.find( '#chart-legend' );
				var highlightedChart = legend.attr( 'data-highlighted-chart' );
				var highlightedSeries = legend.attr( 'data-highlighted-series' );

				if (highlightedChart)
				{
					var chart = chartGroup.getChart( highlightedChart );
					if (!chart) return;

					var dataRange = chart.getDataRangeX();
					if (!dataRange)
					{
						// there's no data being returned
						return;
					}

					var highestX = dataRange[1] * 1000;
					var lastRow = chart.dygraph.numRows() - 1;

					chart.dygraph.setSelection( lastRow, highlightedSeries );
				}
			}
		},

		changeData: function()
		{
			if (chartConfig.adhoc && isLegendShowing)
			{
				generateLegend();
			}
		},
	});
}


function initFetchNotifications( /*BW.GraphiteModel*/ model )
{
	jQuery( model ).on( 'fetch', function( ev, /*BW.GraphiteSeries*/ series, from, until )
	{
		topLevelContainer.addClass( 'fetch-in-progress' );

		// progress stuff disabled temporarily
		// var id = series.target + '-' + from + '-' + until;
		// id = id.replace( /\W/g, '_' );

		// from = isFinite( from )
		// 	? new Date( 1000 * from ).toBigWorldDateString(
		// 		/*showMillisecs*/ false ) : from;
		// until = isFinite( until )
		// 	? new Date( 1000 * until ).toBigWorldDateString(
		// 		/*showMillisecs*/ false ) : until;

		// new Alert.Info(
		// 	"Fetching from "
		// 	+ (isFinite( from ) ? new Date( 1000 * from ).toBigWorldDateString(
		// 		/*showMillisecs*/ false ) : from)
		// 	+ " to "
		// 	+ (isFinite( until ) ? new Date( 1000 * until ).toBigWorldDateString(
		// 		/*showMillisecs*/ false ) : until)
		// 	, { duration: 0, fadeOut: 0, fadeIn: 0, id: id }
		// );
	});

	jQuery( model ).on( 'fetchComplete', function( ev, /*BW.GraphiteSeries*/ series, from, until )
	{
		topLevelContainer.removeClass( 'fetch-in-progress' );

		// progress stuff disabled temporarily
		// var id = series.target + '-' + from + '-' + until;
		// id = id.replace( /\W/g, '_' );
		// Alert.dismiss( id );
	});
}


function initTreeSelect( /*Array of String*/ targets )
{
	var isStatLogger = new RegExp( '^' + prefs.model.prefix );
	var isUser = new RegExp( '\.user_' + BW.user.name + '\.' );

	// aggregate by machine name, process type, statistic name
	var byMachine = {}, byProcess = {}, byMachineStat = {}, byProcessStat = {};

	for (var i in targets)
	{
		var t = targets[i];

		// exclude non-statlogger metrics
		if (!isStatLogger.test( t )) continue;

		// convert metric names to map of discriminators -> values
		var obj = t.substring( prefs.model.prefix.length + 1 ).toMap( '.', '_' );
		obj.target = t;

		if (obj.process)
		{
			// it's a process stat

			// exclude non-user procs
			if (!isUser.test( t )) continue;

			var type = obj.processType = obj.process[0].replace( /\d+$/, '' );
			byProcess[type] = byProcess[type] || [];
			byProcess[type].push( obj );

			var stat = obj.stat[0];
			byProcessStat[stat] = byProcessStat[stat] || [];
			byProcessStat[stat].push( obj );
		}
		else
		{
			// it's a machine stat
			var machine = obj.machine[0];
			byMachine[machine] = byMachine[machine] || [];
			byMachine[machine].push( obj );

			var stat = obj.stat[0];
			byMachineStat[stat] = byMachineStat[stat] || [];
			byMachineStat[stat].push( obj );
		}
	}

	model.targetsByType = {
		machine: byMachine,
		process: byProcess,
		machineStat: byMachineStat,
		processStat: byProcessStat,
	};
	console.debug( "Collated metrics: %O", model.targetsByType );

	var c = jQuery( '<div/>' ).appendTo( '.chart-container' );
	c.addClass( 'graph-select' );

	var ol = jQuery( '<ol/>' ).appendTo( c );
}


function requestFetchPreferences( /*String*/ url )
{
	return jQuery.ajax(
	{
		url: url || 'prefs',
		dataType: 'xml',
	})
	.error( function()
	{
		new Alert.Warning( "Couldn't load StatLogger preferences." );
	});
}


function generateLegend()
{
	var legend = topLevelContainer.find( '#chart-legend' );
	legend.empty();

	var seriesByLabel = {};
	var charts = chartGroup.charts;
	if (!charts || !charts.length) return;

	// compile the set of series labels
	// skip first label as it's for the x-axis ("time")
	var labels, label, i, j;
	for (i in charts)
	{
		labels = charts[i].labels;
		if (!labels) continue;

		assert( labels[0] === 'time' );
		for (j = 1; j < labels.length; j++)
		{
			label = labels[j];
			if (seriesByLabel[label])
			{
				seriesByLabel[label] += 1;
			}
			else
			{
				seriesByLabel[label] = 1;
			}
		}
	}

	labels = Object.keys( seriesByLabel );
	labels.sort();

	console.debug( "legend labels: %O", labels );

	var html = '<div>';

	var colour;
	var series;
	for (i = 0; i < labels.length; i++)
	{
		label = labels[i];
		series = prefs.series[label];
		// assert( series, "no colour for series '%s'", label );
		colour = series ? series.colour : '#aaa';

		html += '<div class="series" style="color: '
			+ colour
			+ '" data-label="'
			+ label
			+ '">'
			+ '<label>' + label + '</label>'
			+ '<span></span>'
			+ "</div>";
	}
	html += '</div>';

	legend.html( html );
}


/** Overriden */
Dygraph.Plugins.Legend.prototype.select = function( e )
{
	if (!isLegendShowing) return;

	var xValue = e.selectedX;
	var selectedPoints = e.selectedPoints;

	// if selectedPoints is not given, it means mouse is not over a chart,
	// so avoid lots of expensive legend HTML updates here (this method is
	// triggered on every draw of every chart) - we will do a single legend update
	// once in the .series mouseenter handler.
	if (!selectedPoints.length) return;

	if (topLevelContainer.find( '#chart-legend' ).hasClass( 'prevent-updates' ))
	{
		return;
	}

	updateLegend( e.dygraph, xValue, selectedPoints );
};


/** Overridden */
Dygraph.Plugins.Legend.prototype.deselect = function() { /*NOOP*/ };


/** Override Dygraph findClosestPoint. In the original method, the row is
	calculated by distance, which may be not accurate. It is more accurate to
	calculate the row just based on the X axis */
Dygraph.prototype._findClosestPoint = Dygraph.prototype.findClosestPoint;
Dygraph.prototype.findClosestPoint = function( domX, domY )
{
	var point = this._findClosestPoint( domX, domY);
	var row = this.findClosestRow( domX );
	
	point.row = row;
	
	return point;
};


/**
 * Add this new function to Dygraph to get the point by row and series index
 */
Dygraph.prototype.findPoint = function( /*int*/ row, /*int*/ seriesIndex )
{
	// the seriesIndex to for the points is less than the index from name by 1
	seriesIndex -= 1;
	
	var points = this.layout_.points[ seriesIndex ];
	var rowInView = row - this.getLeftBoundary_( seriesIndex );
	
	if (!points)
	{
		return null;
	}
	
	if (rowInView < points.length)
	{
       return points[ rowInView ];
	}
	
	return null;
}


function updateLegend( /*Dygraph*/ g, /*int*/ xValue, /*Array of Dygraph point*/ points )
{
	var legend = topLevelContainer.find( '#chart-legend' );

	var highlightChart = g.bw_chart.getTitle();
	var highlightSeries = g.getHighlightSeries();

	var currentlyHighlightedX = legend.attr( 'data-highlighted-x' );
	var currentlyHighlightedChart = legend.attr( 'data-highlighted-chart' );
	var currentlyHighlightedSeries = legend.attr( 'data-highlighted-series' );

	if (highlightChart === currentlyHighlightedChart
		&& highlightSeries === currentlyHighlightedSeries
		&& xValue == currentlyHighlightedX) return;

	clearLegendSeriesData();

	// console.log( 'update legend: %s, %s, %s (from %s, %s, %s)',
	// 	highlightChart, highlightSeries, xValue,
	// 	currentlyHighlightedChart, currentlyHighlightedSeries, currentlyHighlightedX
	// );

	var i;

	// update highlighted series
	if (highlightSeries)
	{
		legend.attr( 'data-highlighted-series', highlightSeries );
		legend.find( '.series[data-label = "' + highlightSeries + '"]' ).addClass( 'is-highlighted' );
	}

	// if there are selected points (eg: user is hovering over a chart),
	// then show current values
	var pointsAreNormalised = g.bw_chart.options.normaliseY;
	if (points)
	{
		legend.find( 'span' ).empty();
		var pointValues = points.map( function( pt ) { return pt.yval; } );

		if (pointsAreNormalised)
		{
			// get max values for shown points; note that not all series may have
			// defined points at the given time, in which case they will not be present
			// in the `points` array, hence we need to filter the `seriesMax` array to
			// get the correct point maxes.
			var maxByLabel = {};
			var labels = g.bw_chart.labels;
			var seriesMaxValues = g.bw_chart.seriesMax;
			assert( labels.length === seriesMaxValues.length );

			for (i = 0; i < seriesMaxValues.length; i++)
			{
				maxByLabel[labels[i]] = seriesMaxValues[i];
			}

			// un-normalise point values
			var max;
			for (i = 0; i < points.length; i++)
			{
				max = maxByLabel[points[i].name];
				pointValues[i] *= max;
			}
		}

		// format values and insert into DOM
		var value, point, row;
		var getOptions = g.getOption.bind( g );

		for (i = 0; i < points.length; i++)
		{
			point = points[i];
			value = pointValues[i];
			value = Dygraph.numberValueFormatter( value, getOptions, point );
			row = legend.find( '.series[data-label = "' + points[i].name + '"]' );
			row.addClass( 'is-in-chart' );
			row.children( 'span' ).html( value );
		}
	}

	legend.attr( 'data-highlighted-series', highlightSeries );
	legend.attr( 'data-highlighted-chart', highlightChart );
	legend.attr( 'data-highlighted-x', xValue );
}


function showLegend()
{
	assert( chartGroup );

	topLevelContainer.addClass( 'showing-legend' );
	topLevelContainer.find( '.legend-control.button' ).addClass( 'depressed' );

	jQuery( '#chart-legend' ).show();
	isLegendShowing = true;
	chartGroup.resize();
}


function hideLegend()
{
	assert( chartGroup );

	topLevelContainer.removeClass( 'showing-legend' );
	topLevelContainer.find( '.legend-control.button' ).removeClass( 'depressed' );

	jQuery( '#chart-legend' ).hide();
	isLegendShowing = false;
	chartGroup.resize();
}


function clearLegendState()
{
	var legend = topLevelContainer.find( '#chart-legend' );

	legend.removeAttr( 'data-highlighted-chart' );
	legend.removeAttr( 'data-highlighted-series' );
	legend.removeAttr( 'data-highlighted-x' );
}


function clearLegendSeriesData()
{
	var legend = topLevelContainer.find( '#chart-legend' );

	legend.find( '.series.is-highlighted' ).removeClass( 'is-highlighted' );
	legend.find( '.series.is-in-chart' ).removeClass( 'is-in-chart' );
	legend.find( '.series span:not( :empty )' ).empty();
}


function clearLegendSelectedSeries()
{
	if (!chartGroup) return;

	var charts = chartGroup.charts;
	if (!charts) return;

	for (var i in charts)
	{
		if (!charts[i].dygraph) continue;
		charts[i].dygraph.clearSelection();
	}

	topLevelContainer.removeClass( 'showing-selected-charts' );
}


function setLegendSelectedSeries( /*String*/ seriesId )
{
	assert( seriesId );
	assert( chartGroup );
	assert( chartGroup.charts );
	assert( chartGroup.charts.length );

	clearLegendSeriesData();

	var charts = chartGroup.charts;
	for (var i in charts)
	{
		if (!charts[i].dygraph) continue;
		if (charts[i].labels.indexOf( seriesId ) != -1)
		{
			charts[i].dom.container.attr( 'data-selected', seriesId );
			charts[i].dygraph.setSelection( false, seriesId, true );
		}
		else
		{
			charts[i].dom.container.removeAttr( 'data-selected' );
			charts[i].dygraph.clearSelection();
		}
		// charts[i].dygraph.setSelection( false, seriesId, true );
	}

	topLevelContainer.addClass( 'showing-selected-charts' );
}


function showValueTooltips( /*object*/ dygraph, /*int*/ canvasX,
	/*int*/ canvasY )
{
	if (isInLiveMode())
	{
		return;
	}

	hideValueTooltips();
	
	var highlightedSeries = dygraph.getHighlightSeries();
	var seriesIndex = dygraph.indexFromSetName( highlightedSeries );
	var row = dygraph.findClosestRow( canvasX );
	var point = dygraph.findPoint( row, seriesIndex );
	
	if (!point)
	{
		return;
	}
	
	jQuery( '.select-line' ).css({
		left: point.canvasx,
		display: 'block',
	})
	
	var charts = chartGroup.charts;
	for (var i in charts)
	{
		if (!charts[i].dygraph) continue;
		
		showValueTooltip( charts[i], i, row, highlightedSeries );
	}
}


function showValueTooltip( /*object*/ chart, /*int*/ chartIndex,
	/*int*/ row, /*String*/ highlightedSeries )
{
	var dygraph = chart.dygraph;
	var seriesIndex = dygraph.indexFromSetName( highlightedSeries );
	var value = dygraph.getValue( row, seriesIndex );
	
	if (value === null || !isFinite( value ))
	{
		return;
	}
	
	var point = dygraph.findPoint( row, seriesIndex );
	if(!point)
	{
		return;
	}
	
	var offset = chart.dom.container.position();
	var canvasX = Math.ceil( point.canvasx );
	var canvasY = Math.ceil( point.canvasy );

	var tooltipHtml = "<div class='value-tooltip' id='value-tooltip_"
						+ chartIndex+ "'></div>";
	var tooltip = jQuery( tooltipHtml );

	tooltip.html( highlightedSeries + " = " + value.toFixed( 3 ) );

	var chartsContainer = chart.dom.container.parents( ".charts-container");
	
	// first display the tool tip, so that we can get its width
	tooltip.css({
		left: offset.left,
		top: offset.top,
		"z-index": 999
	});
	
	tooltip.appendTo( chartsContainer );

	// now adjust the tool tip postion. Keep a gap between tooltip and point
	var gap = 10;
	var left = offset.left + canvasX + gap;
	var top = offset.top + canvasY - tooltip.height() / 2;
	
	var tipBoxShadowSize = getBoxShadowSize( tooltip );
	var tipWidth = tooltip.outerWidth( true ) + tipBoxShadowSize.width;
	var tipHeight = tooltip.outerHeight( true ) + tipBoxShadowSize.height;

	if (left + tipWidth > dygraph.width_)
	{
		left = offset.left + canvasX - tipWidth - gap;
	}

	if (canvasY + tipHeight / 2 >= dygraph.height_)
	{
		top = offset.top + dygraph.height_ - tipHeight;
	}

	tooltip.css({
		left: left,
		top: top,
		"z-index": 999
	});
}


function hideValueTooltips()
{
	if (isInLiveMode())
	{
		return;
	}
	
	var charts = chartGroup.charts;
	for (var i in charts)
	{
		if (!charts[i].dygraph) continue;
		
		var selector = "div#value-tooltip_" + i;
		jQuery( selector ).remove();
	}
	
	jQuery( '.select-line' ).hide();
}


function getBoxShadowSize( /*jQuery Object*/ element )
{
	var width = 0;
	var height = 0;
	
	// get the css attr, the result of this is in the format like
	// "rgb(68, 68, 68) 0px 2px 4px 0px", we need to parse out the width and
	// height from this.
	var str = element.css("box-shadow");
	
	// Remove all possible color definitions, will result in "0px 2px 4px 0px"
	str = str.replace(/rgba?\([^\)]+\)/gi, '');
	str = str.replace(/#[0-9a-f]+/gi, '');
	
	// Remove any alpha characters (the px), will result in "0 2 4 0"
	str = str.replace(/[a-z]+/gi, '').trim();
	
	//parse out values
	var values = str.split(' ');
	if (values && values.length > 0)
	{
		for (var i = 0; i < values.length; ++i)
		{
			values[i] = parseInt( values[i] );
		}

		// width equals h position + blur size + spread
		width = Math.abs( values[0] ) + values[2] + values[3];
		
		//height equals v position + blur size + spread
		height = Math.abs( values[1] ) + values[2] + values[3];
	}

	return { width : width,
			height : height };
}

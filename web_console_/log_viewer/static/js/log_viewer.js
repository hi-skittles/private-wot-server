"use strict";

// requires jquery
if (!window.jQuery)
{
	throw new Error( 'required jquery lib not present' );
}

// requires jquery-deserialize plugin
if (!jQuery( window ).deserialize)
{
	throw new Error( 'required jquery-deserialize plugin not present' );
}

// requires Alert lib
if (!window.Alert)
{
	throw new Error( 'required Alert lib not present' );
}

var LogViewer = window.LogViewer || {};


/** Matches characters that are precluded from use in saved query names */
LogViewer.VALID_QUERY_NAME_REGEXP = /^[\w\s,]+$/;


/**
*   Implements stand-alone (headless) message_logger queries, and abstracts
*   persisting to, and initialising from, HTML forms, CGI query strings, and
*   the Web Console user data persistence layer.
*
*   new LogViewer.Query( jQuery( '.some form' ) );
*   new LogViewer.Query( 'procs=CellApp&procs=LoginApp&message=blah' );
*   new LogViewer.Query( { message: 'blah', procs: [ 'CellApp', 'LoginApp' ] } );
*/
LogViewer.Query = function( /*(Map|jqueryForm|String)*/ querySource, /*Map?*/ options )
{
	// permit simple subclassing
	if (querySource === undefined)
	{
		return;
	}

	this.options = jQuery.extend( {}, LogViewer.Query.Defaults, options );

	// init query params from passed (polymorphic) source.
	if (querySource.is && querySource.is( 'form' ))
	{
		this._initFromForm( querySource );
	}
	else if (typeof( querySource ) === 'string')
	{
		this._initFromQueryString( querySource );
	}
	else if (typeof( querySource ) === 'object')
	{
		if (this.options.debug)
			console.log( 'init query from passed Map: %O', querySource );

		this.params = querySource;
	}
	else
	{
		console.error( "Unsupported query source:" );
		console.dir( querySource );
	}
};


LogViewer.Query.Defaults =
{
	debug: 0,

	// default number of lines to retrieve per request
	limit: 100,

	queryUrl: '/log/fetch2',
	asyncQueryUrl: "/log/fetchAsync",
	// asyncQueryUrl: "/log/fetch",

	saveQueryUrl: '/log/saveQuery',
	fetchQueryUrl: '/log/fetchQueries',

	// interval used between polls when queries are performed asynchronously;
	// see {LogViewer.AsyncQuery}.
	asyncPollInterval: 500, // msec
};


/** Init this query's params from the values in the passed jQuery-wrapped form. */
LogViewer.Query.prototype._initFromForm = function( /*jQuery*/ form )
{
	var map = {};
	var params = form.serializeArray();

	// convert params from array of name+value objects to a map of
	// param name to value(s).
	for (var i in params)
	{
		var name = params[i].name;
		if (map[name] !== undefined)
		{
			if (map[name] instanceof Array)
			{
				map[name].push( params[i].value );
			}
			else
			{
				map[name] = [ map[name], params[i].value ];
			}
		}
		else
		{
			map[name] = params[i].value;
		}
	}

	if (this.options.debug)
	{
		console.log( 'init query from jquery( form element )' );
		console.dir( map );
	}
	this.params = map;
};


/** Init this query's params from a (URI-decoded) query string. */
LogViewer.Query.prototype._initFromQueryString = function( /*String*/ queryString )
{
	var paramsAndValues = queryString.split( /&|;/ );
	var queryParams = {};

	for (var i = 0; i < paramsAndValues.length; i++)
	{
		var paramAndValue = paramsAndValues[i].split( '=', 2 );
		// Replace '+' with '%20' before decoding so that '%2B' does not
		// double-decode into space
		var valueURI = paramAndValue[1].replace(/\+/g, "%20");
		var paramValue = window.decodeURIComponent( valueURI );

		if (paramAndValue[0] in queryParams)
		{
			queryParams[ paramAndValue[0] ].push( paramValue );
		}
		else
		{
			queryParams[ paramAndValue[0] ] = [ paramValue ];
		}
	}

	if (this.options.debug)
	{
		console.log( "init from query string '%s':", queryString );
	}

	this.params = queryParams;
};


/**
*   Fetch the results of this query, and call the given callback with the
*   result if given. Callback is called with returned data as first argument,
*   or null if fetch call was unsuccessful, and 'this' pointing to the
*   LogViewer.Query instance on which the fetch was called.
*
*   Also triggers the 'fetch.lv' event on success, and 'fetchFailed.lv' on failure.
*   These are triggered after the passed callback (if provided).
*/
LogViewer.Query.prototype.fetch =
function( /*Function?*/ callback, /*int?*/ limit, /*String?*/ fromIndex )
{
	var params = jQuery.extend( {}, this.params ); // shallow copy
	params.limit = limit || this.options.limit;
	var q = this;

	if (this.rangeEnd)
	{
		params.startAddr = this.rangeEnd.join( ',' );
		// params.startAddr = this.rangeEnd;
	}

	if (params.startAddr)
	{
		// startAddr is inclusive - need to get 1 extra line as first line will
		// be the last line of the previous fetch
		params.limit++;
		if (this.options.debug)
		{
			console.log(
				'requesting next %s records from %s',
				params.limit, params.startAddr
			);
		}
	}
	else
	{
		if (this.options.debug)
		{
			console.log( 'requesting %s records', params.limit );
		}
	}

	this._fetchAjax = jQuery.ajax({
		url: this.options.queryUrl,
		data: params,
		traditional: true,
		dataType: 'json',
		timeout: 1000,
		success: function( /*Map*/ data, /*String*/ textStatus, jqxhr )
		{
			q._fetchAjax = null;

			q.data = data;
			q.rangeEnd = data.rangeEnd;
			q.rangeStart = data.rangeStart;
			if (data.reverse)
			{
				q.rangeEnd = data.rangeStart;
				q.rangeStart = data.rangeEnd;
			}

			if (q.options.debug > 1)
			{
				console.log( "fetch successful" );
				console.dir( data );
			}

			if (callback) callback.call( q, data );
			jQuery( q ).triggerHandler( 'fetch.lv', [ data ] );
		},
		error: function( jqxhr, /*String*/ textStatus, /*String?*/ errorThrown )
		{
			q._fetchAjax = null;
			if (textStatus === 'timeout')
			{
				new Alert.Warning( 'Query timed out.' );
			}
			else
			{
				new Alert.Error( 'Web Console appears to be down', { id: true } );
				console.warn( "log fetch query failed: %s ", textStatus, errorThrown );
				if (callback) callback.call( q, null );
				jQuery( q ).triggerHandler( 'fetchFailed.lv' );
			}
		}
	});
};


/** Terminate a fetch() in progress. No effect if fetch not in progress. */
LogViewer.Query.prototype.terminateFetch = function()
{
	if (this._fetchAjax)
	{
		this._fetchAjax.abort();
		this._fetchInProgress = false;
		jQuery( this ).triggerHandler( 'terminated.query.lv' );
	}
};


/**
*   Persist this query to Web Console under the given name. Defaults to
*   the name 'most recent' if not specified.
*/
LogViewer.Query.prototype.saveAs = function( /*String?*/ name )
{
	if (!name || !name.match( LogViewer.VALID_QUERY_NAME_REGEXP ))
	{
		new Alert.Error(
			"Invalid query name: query names must " +
			'contain only alphanumeric characters, spaces and commas.'
		);
		return;
	}

	var queryParams = this.params;
	queryParams.name = name;
	var q = this;

	jQuery.ajax({
		url: this.options.saveQueryUrl,
		data: queryParams,
		traditional: true,
		dataType: 'json',
		success: function( /*Map*/ data, /*String*/ textStatus, jqxhr )
		{
			new Alert.Info( "Successfully saved query '" + queryParams.name + "'." );
			jQuery( q ).triggerHandler( 'save.query.logs', [ data ] );
		},
		error: function( jqxhr, /*String*/ textStatus, /*String?*/ errorThrown )
		{
			new Alert.Warning( 'Save query failed' );
			jQuery( q ).triggerHandler( 'saveFailed.query.logs', [ data ] );
		}
	});
};


/**
*   Returns query parameters as a map of query param name to param value,
*   in which multi-valued params are packed into an Array.
*/
LogViewer.Query.prototype.getParams = function()
{
	return this.params;
};


/** Returns this query as a URL-encoded query string. */
LogViewer.Query.prototype.toQueryString = function()
{
	var queryString = jQuery.param( this.params, true );

	// handle '+'/space conversion specially
	queryString = queryString.replace( /\+/g, '%20' );

	return queryString;
};


/**
*   Returns this query as an URL that could be used to fetch logs matching the
*   current query params.
*/
LogViewer.Query.prototype.toStringUrl = function()
{
	return this.options.queryUrl + '?' + this.toQueryString();
};


/** Populate the given form with this query's params. */
LogViewer.Query.prototype.toForm = function( /*jQuery*/ form )
{
	if (this.options.debug)
	{
		console.log( 'deserialising query params to form:' );
		console.dir( params );
	}
	form.deserialize( this.getParams() );
};


/*~~~~~~~~~~~~~~~~~~~~~~~~ class LogViewer.AsyncQuery ~~~~~~~~~~~~~~~~~~~~~~~~~~~*/

/** Sub-class of {LogViewer.Query} for performing queries asynchronously. */
LogViewer.AsyncQuery = function( /*(Map|jqueryForm|String)*/ querySource, /*Map?*/ options )
{
	LogViewer.Query.prototype.constructor.call( this, querySource, options );
};

LogViewer.AsyncQuery.extends( LogViewer.Query );


/** Terminate a fetch() in progress. No effect if fetch not in progress. */
LogViewer.AsyncQuery.prototype.terminateFetch = function()
{
	if (this._fetchInProgress)
	{
		this.task.terminate();
		this._fetchInProgress = false;
		jQuery( this ).triggerHandler( 'terminated.query.lv' );
	}
};


/**
*   Fetch results for this query asynchronously. Generates the following events:
*
*       - 'begin.query.lv' on acquiring a asynchronous task ID on the web server
*       - 'update.query.lv' on receiving query results.
*       - 'no_update.query.lv' on receiving a reply from the server containing
*         an empty set of query results (query continues).
*       - 'progress.query.lv' on receiving a query progress/status message.
*       - 'finished.query.lv' on reaching the end of results for this query.
*       - 'terminated.query.lv' on the query being prematurely terminated.
*       - 'error.query.lv' on the query being prematurely terminated.
*
*/
LogViewer.AsyncQuery.prototype.fetch = function( /*int?*/ pollInterval )
{
	if (this._fetchInProgress) return;
	this._fetchInProgress = true;

	this.count = 0;
	this.seen = 0;
	this.currTotal = -1;
	this.moreAvailable = false;
	var _this = this;

	var onID = function( id, response )
	{
		if (response.validationErrors)
		{
			// merely report param validation fails to console for now,
			// a future rev can think about better UI reporting
			var invalidParams = response.invalidParams;
			console.log( "params that did not validate: %O", invalidParams );

			for (var i in response.validationErrors)
			{
				new Alert.Warning( response.validationErrors[i] );
			}
		}

		jQuery( _this ).triggerHandler( 'begin.query.lv', [ response ] );
	};

	var onUpdate = function( state, data )
	{
		if (state == "results")
		{
			jQuery( _this ).triggerHandler( 'update.query.lv', [ data ] );
		}
		else if (state == "progress")
		{
			_this.queryID = data[0];
			_this.count = data[1];
			_this.seen = data[2];
			_this.currTotal = data[3] || -1;
			_this.moreAvailable = data[4] || false;
			jQuery( _this ).triggerHandler( 'progress.query.lv', [ data ] );
		}
		else if (state == "truncated")
		{
			_this.task.terminate();
			_this.queryID = data;
			this._fetchInProgress = false;
			jQuery( _this ).triggerHandler( 'finished.query.lv', data );
		}
	};

	var onNoUpdate = function( data )
	{
		jQuery( _this ).triggerHandler( 'no_update.query.lv' );
	};

	var onFinished = function()
	{
		this._fetchInProgress = false;
		jQuery( _this ).triggerHandler( 'finished.query.lv' );
	};

	// This is a server-side timeout in the python AsyncTask.
	var onTimeout = function()
	{
		new Alert.Warning( "The back-end query task has timed out. This is " +
							"probably because the server is generating too " +
							"many logs for WebConsole to handle. You can " +
							"try to limit the amount of logs transferred " +
							"during each update by enabling and decreasing " +
							"the web_console.log_max_poll_lines in " +
							"WebConsole configuration file." );
		_this.terminateFetch();
	};

	// Handle poll URL failures
	var onAjaxPollError = function ( status, jqxhr, data )
	{
		if (!_this._fetchInProgress || (data.id != _this.task.id))
		{
			// Poll errors on a terminated task are to be expected, and can be
			// ignored.
			return;
		}

		if (status == "timeout")
		{
			// This is an ajax timeout, which occurs when the WebConsole server
			// does not respond to a poll URL requests.
			new Alert.Error( "Fetching log results has timed out. The " +
				"WebConsole server may be overloaded or the network " +
				"latency may be too high." )
		}
		else
		{
			new Alert.Error( "An unexpected error occurred whilst waiting for " +
				"query results. Terminating fetch." )
		}
		_this.terminateFetch();
	}

	var interval = pollInterval || this.options.asyncPollInterval || 500;
	this.task = new AsyncTask.AsyncTask(
		onID, onUpdate, onNoUpdate, onFinished, onTimeout, onAjaxPollError, 
		interval, false );

	if (this.options.debug)
	{
		console.log( "(starting async query task)" );
	}
	
	var onError = function ( status, jqxhr )
	{
		jQuery( _this ).triggerHandler( 'terminated.query.lv' );
	}
	
	this.task.start( this.options.asyncQueryUrl, this.params, onError );
};


/*~~~~~~~~~~~~~~~~~~~~~~~~ class LogViewer.QueryForm ~~~~~~~~~~~~~~~~~~~~~~~~~~~~*/

LogViewer.QueryForm = function( /*String|DOM*/ domTarget, /*Map*/ options )
{
	this.options = jQuery.extend( {}, LogViewer.QueryForm.Defaults, options );

	if (this.options.debug)
	{
		console.log( 'query form options:' );
		console.dir( this.options );
	}

	this.outputPane = new LogViewer.OutputPane( this.options.logOutput );
	this.initDom( domTarget );
	this.initEvents();
};


LogViewer.QueryForm.Defaults =
{
	debug: 0,

	serverTimezone: 0, // server timezone in delta sec

	// serialises query params to location #hash if true.
	// note you still have to bind hashchange event to actually submit the
	// query on browser forwards/back event.
	addToHistory: true,

	hideFiltersOnFetch: false,

	deleteQueryUrl: '/log/deleteQuery',

	// DOM selectors for various form components (jquery syntax).
	// all of these *must* descend from the DOM target element given
	// at construction or jquery will not find them.
	activeQueries: '.active-queries-container',
	inactiveQueries: '.inactive-queries-container',
	inactiveQueriesMenu: '.inactive-queries.dropdown-menu',
	submitFetchTrigger: '.fetch-logs',
	submitContinuousFetchTrigger: '.tail-logs',

	// DOM target for query results
	// note: this element doesn't need to live inside initial DOM container
	logOutput: '.log-output',

	progressIndicator: '.query-progress-indicator',
};


LogViewer.QueryForm.prototype.initDom = function( /*String|DOM*/ domTarget )
{
	var opt = this.options;
	var dom = this.dom = {};

	dom.container = jQuery( domTarget ).first();
	dom.activeQueries = dom.container.find( opt.activeQueries );
	dom.inactiveQueries = dom.container.find( opt.inactiveQueries );
	dom.inactiveQueriesMenu = dom.container.find( opt.inactiveQueriesMenu );
	dom.progressIndicator = dom.container.parent().find( opt.progressIndicator );

	// sanity checks
	if (!dom.container.length)
	{
		console.error( "No DOM element matches selector '%s'", domTarget );
	}

	if (!dom.activeQueries.length)
	{
		console.error(
			"No DOM element '%s' in container '%s'",
			opt.activeQueries, domTarget
		);
	}

	if (!dom.inactiveQueries.length)
	{
		console.error(
			"No DOM element '%s' in container '%s'",
			opt.inactiveQueries, domTarget
		);
	}

	if (!dom.inactiveQueriesMenu.length)
	{
		console.error(
			"No DOM element '%s' in container '%s'",
			opt.inactiveQueriesMenu, domTarget
		);
	}

	// set the ordering of query types from the order they are given in the HTML,
	// and preserve this ordering in both active and inactive query containers.
	var queryTypes = this.getQueryTypes();
	this.queryTypeOrder = [];
	var i = 1;
	for (var type in queryTypes)
	{
		jQuery( queryTypes[type] ).attr( 'display-order', i++ );
		this.queryTypeOrder.push( type );
	}

	if (this.options.debug)
	{
		console.log( "query type order: %s", Object.keys( queryTypes ).join( ' > ' ) );
	}
};


LogViewer.QueryForm.prototype.initEvents = function()
{
	this._initFilterEvents();
	this._initQueryEvents();
	this._initFormEvents();

	jQuery( '.toggle-show-hide-filters' ).toggle(
		function()
		{
			// hide filters
			this.dom.container.addClass( 'filters-hidden' );
			this.dom.activeQueries.slideUp();
		}
		.bind( this ),

		function()
		{
			// show filters
			this.dom.container.removeClass( 'filters-hidden' );
			this.dom.activeQueries.slideDown();
		}
		.bind( this )
	);
};

/*
// event handler, 'this' points at DOM element that is subject of event
LogViewer.QueryForm.prototype._showMenu = function( ev )
{
	var menuContainer = jQuery( this ).parents( '.dropdown-menu-container' ).first();
	var menu = menuContainer.find( '.dropdown-menu' );
	if (menu.is( ':visible' ))
	{
		menuContainer.removeClass( 'menu-open' );
		menu.fadeOut( 'bw_menu_fade_out' );
		return false;
	}

	jQuery( '.dropdown-menu' ).removeClass( 'menu-open' ).fadeOut( 'bw_menu_fade_out' );

	jQuery( document ).one( 'click', function()
	{
		menuContainer.removeClass( 'menu-open' );
		menu.fadeOut( 'bw_menu_fade_out' );
	});

	menuContainer.addClass( 'menu-open' );
	menu.fadeIn( 'bw_menu_fade_in' );

	return false;
};
*/

LogViewer.QueryForm.prototype._initFilterEvents = function()
{
	var savedFiltersMenu = this.dom.container.find( '.saved-queries.dropdown-menu' );

	if (!savedFiltersMenu.length)
		console.error( "No element in container for selector '.saved-queries.dropdown-menu'" );

	// open saved filters menu on clicking trigger
	this.dom.container.find( '.load-query .dropdown-menu-opener' ).click( function()
	{
		if (savedFiltersMenu.is( ':visible' ))
		{
			savedFiltersMenu.fadeOut( 'bw_menu_fade_out' );
			return false;
		}
		jQuery( '.dropdown-menu' ).fadeOut( 'bw_menu_fade_out' );

		if (this.options.hideFiltersOnFetch)
		{
			this.dom.activeQueries.slideDown( 200 );
		}
		savedFiltersMenu.fadeIn( 'bw_menu_fade_in' );
		return false;
	}
	.bind( this ));

	// close menu on click anywhere
	jQuery( document ).on( 'click touchend', function()
	{
		savedFiltersMenu.fadeOut( 'bw_menu_fade_out' );
	});

	// load saved query on menu-item click
	this.dom.container.on( 'click', '.saved-queries.dropdown-menu li', function( ev )
	{
		var savedQueryName = jQuery( ev.target ).attr( 'query-name' );
		if (!savedQueryName)
		{
			console.error( "Menu item has no 'query-name' attribute:" );
			console.dir( ev.target );
			return;
		}
		this.loadSavedQuery( savedQueryName );
	}
	.bind( this ));

	// save filter trigger
	this.dom.container.on( 'click', '.save-current-query', function( ev )
	{
        this.dom.activeQueries.show();

		// edge case where a shown menu will not receive a document click to hide
		// itself because we are using window.prompt, so force hide all dropdown-menus
		// just in case. note that window.prompt blocks, so must be immediate hide.
		jQuery( '.dropdown-menu' ).hide();

		var queryName = window.prompt(
			'Provide a name to save query as:', 'default' );

		if (queryName === null)
		{
			// user clicked 'cancel'
			return false;
		}

		var q = this.getQuery();
		jQuery( q ).one( 'save.query.logs', this.requestSavedQueries.bind( this ) );

		q.saveAs( queryName || '' );
	}
	.bind( this ));
};


LogViewer.QueryForm.prototype._initQueryEvents = function()
{
	// remove a filter
	this.dom.container.on( 'click', '.remove-filter', function( ev )
	{
		if (this.options.debug > 1)
		{
			console.log( '(container .remove-filter.click)' );
		}
		var queryFragment = jQuery( ev.target ).parents( '.query-fragment' );
		var queryType = queryFragment.attr( 'query-type' );
		this.inactivateQueryType( queryType, queryFragment );
	}
	.bind( this ));

	// add a filter
	this.dom.container.on( 'click', '.add-filter', function( ev )
	{
		if (this.options.debug > 1)
		{
			console.log( '(container .add-filter.click)' );
		}

		if (this.options.hideFiltersOnFetch)
		{
			this.dom.activeQueries.slideDown( 200 );
		}

		this.showAvailableQueriesMenu( ev.target );

		// consume event to prevent body.click event firing
		return false;
	}
	.bind( this ));

	// toggle active/inactive filter
	this.dom.inactiveQueriesMenu.on( 'click', 'li', function( ev )
	{
		var queryType = jQuery( ev.target ).attr( 'query-type' );
		if (this.options.debug > 1)
		{
			console.log( "(inactive menu li.click '%s')", queryType );
		}
		this.toggleActive( queryType );
	}
	.bind( this ));

	// remove saved queries
	this.dom.container.on( 'click', '.saved-queries i.icon-remove', function( ev )
	{
		var menuItem = jQuery( ev.target ).parent();
		var queryName = menuItem.attr( 'query-name' );

		if (!queryName)
		{
			console.error( "Menu list item has no 'query-name' attr:" );
			console.dir( ev.target );
			return;
		}

		var confirmed = window.confirm(
			'Are you sure you want to delete saved query "' + queryName + '"?' );
		if (confirmed)
		{
			if (this.options.debug)
			{
				console.log( "deleting query named '%s'", queryName );
			}

			jQuery.ajax({
				url: this.options.deleteQueryUrl,
				data: { name: queryName },
				dataType: 'json',
				success: function()
				{
					new Alert.Info( 'Deleted saved query "' + queryName + '"' );
					menuItem.parents( '.dropdown-menu' ).fadeOut( 'bw_menu_fade_out' );
					this.requestSavedQueries();
				}
				.bind( this ),
				error: function()
				{
					new Alert.Warning(
						'Failed to delete saved query "' + queryName + '"' );
				},
			});
		}

		return false;
	}
	.bind( this ));

	// install query time datepicker
	var timeInput = this.dom.container.find( 'input.specific-time' );
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
	});
	// Remove keyboard events from datetime picker (prevents unwanted behaviour
	// when pressing enter)
	jQuery( timeInput ).off( 'keydown keyup' );
	
	var deltaTz = this.options.serverTimezone - new Date().getTimezoneOffset() * 60;
	var logViewer = this;

	// need to update queryTime form field when datepicker is used to pick a date
	// as datepicker uses a proxy throwaway field.
	timeInput.change( function( ev )
	{
		var inputElem = jQuery( this );
		var inputTime = inputElem.val();
		// console.log( "inputTime = ", inputTime );

		// convert datetime to secs since epoch
		var d = new Date( inputTime );
		
		// If the date is invalid, don't allow the query to be made.
		// Show warning, disable Fetch button, and remove keyboard event
		if(d == "Invalid Date")
		{
			new Alert.Warning( 'Invalid date. Use format ' 
				+ '"Day DD Mon YYYY HH:MM:SS.ms"' );
			jQuery( logViewer.options.submitFetchTrigger ).css( {
				'pointer-events' : 'none', 'color' : '#aaa'} );
			jQuery( this ).off( 'keyup' );
		}
		else
		{
			// Else reset events and set query date as normal
			jQuery( logViewer.options.submitFetchTrigger ).css( {
				'pointer-events' : 'auto', 'color' : '#000'} );
			jQuery( this ).on( 'keyup', function ( ev ) {
				if (ev.which === 13)
				{
					queryForm.submit();
					ev.preventDefault();
				}
			} );
			
			var time = Date.parse( d.toISOString() ) / 1000;

			// firefox does not parse out millisecs in a Date string (time will be NaN)
			// fallback to extracting millisec and adding separately
			if (inputTime && !time)
			{
				var decimalPoint = inputTime.indexOf( '.' );

				// extract and add millisecs, note substring is ".XXX", ie: seconds
				var msec = + inputTime.substring( decimalPoint );
				if (msec >= 0)
				{
					time = Date.parse( inputTime.substring( 0, decimalPoint ) ) / 1000;
					time += msec;
				}
			}

			if (time > 0)
			{
				// adjust for timezone difference
				time += deltaTz;

				// console.log( 'setting queryTime = %s from %s', time, inputTime );
				var periodFragment = inputElem.parents( '.query-fragment' ).first();
				var option = periodFragment.find(
					':input[name = "queryTime"] option.specific-time' );
				option.val( time );
			}
		}
		return false;
	});
	
	// When the period filter is removed, reset listeners and button state
	// in case it had been disabled.
	jQuery( this ).on( 'inactivate.query.lv', 
		function( ev, queryType, queryFragment )
		{
			if(queryType == 'period')
			{
				jQuery( logViewer.options.submitFetchTrigger ).css( 
					{ 'pointer-events' : 'auto', 'color' : '#000'} );
				jQuery( 'input:text:not( .chzn-container input )', 
					queryFragment ).on("keyup", function( ev ) {
						if (ev.which === 13)
						{
							queryForm.submit();
							ev.preventDefault();
						}
				} );
			}
		}
	);

	// if submitting form by hitting <enter> in input.specific-time, ensure
	// that time is synced to option.specific-time.
	timeInput.on( 'keydown', function( ev )
	{
		if (ev.which === 13)
		{
			jQuery( this ).change();
		}
	});

	this.dom.container.find( ':input[name="queryTime"]' ).change(
		this._updatePeriodFilter.bind( this ) );

	this.dom.container.find( ':input[name="period"]' ).change(
		this._updatePeriodFilter.bind( this ) );

	this.dom.container.find( ':input[name="metadata_condition"]' ).change(
		this._updateMetadataFilter.bind( this ) );
};


/** Synchronise form state of period query fragment to UI state. */
LogViewer.QueryForm.prototype._updatePeriodFilter = function()
{
	var periodFragment = this.getQueryFragment( 'period' );

	var queryTimeInput = periodFragment.find( ':input[name = "queryTime"]' );
	var queryTime = queryTimeInput.val();

	var periodInput = periodFragment.find( ':input[name = "period"]' );
	var period = periodInput.val();

	// console.log( "period filter changed: queryTime = '%s', period = '%s'", queryTime, period );

	// show/hide datepicker
	if (queryTime === 'specific time')
	{
		periodFragment.find( '.queryTime-datepicker' ).show();

		periodFragment.find( 'input.specific-time' ).val( '' );
	}
	else if (/^\d+/.test( queryTime ))
	{
		// queryTime is a timestamp (epoch seconds)
		periodFragment.find( '.queryTime-datepicker' ).show();

		// update datepicker's input element
		var deltaTz = this.options.serverTimezone - new Date().getTimezoneOffset() * 60;
		var msec = (parseFloat( queryTime ) - deltaTz) * 1000;
		var date = new Date( Math.floor( msec ) );
		var formattedDate = date.toBigWorldDateString();

		// console.log( 'setting input.specific-time to %s from %s', formattedDate, queryTime );
		periodFragment.find( 'input.specific-time' ).val( formattedDate );
	}
	else
	{
		periodFragment.find( '.queryTime-datepicker' ).hide();
	}

	// disable period options that are logically unfeasible for queryTime
	periodInput.find( 'option' ).removeAttr( 'disabled' );
	if (queryTime === 'now')
	{
		periodInput.find( 'option.present' ).attr( 'disabled', 'true' );
		periodInput.find( 'option.forwards' ).attr( 'disabled', 'true' );
		periodInput.find( 'option.either-side' ).attr( 'disabled', 'true' );

		if (period === 'to present' ||
			period === 'forwards' ||
			period === 'either side')
		{
			period = '';
			periodInput.val( period );
		}
	}
	else if (queryTime === 'beginning of logs')
	{
		periodInput.find( 'option.beginning' ).attr( 'disabled', 'true' );
		periodInput.find( 'option.backwards' ).attr( 'disabled', 'true' );
		periodInput.find( 'option.either-side' ).attr( 'disabled', 'true' );

		if (period === 'to beginning of logs' ||
			period === 'backwards' ||
			period === 'either side')
		{
			period = '';
			periodInput.val( period );
		}
	}

	// show/hide period selection
	if (period === 'forwards' || period === 'backwards' || period === 'either side')
	{
		periodFragment.find( '.period-datepicker' ).fadeIn( 'fast' );
	}
	else
	{
		// hide() after fadeOut() to handle the case where DOM element is
		// not visible and fadeOut() returns immediately without hiding element.
		periodFragment.find( '.period-datepicker' ).fadeOut( 'fast' ).hide();
	}

	// notify select replacement widget of change
	periodInput.triggerHandler( 'liszt:updated' );

	if (this.options.debug)
	{
		console.log(
			"_updatePeriodFilter: queryTime = '%s', period = '%s'",
			queryTimeInput.val(), periodInput.val() );
	}
};


/** Synchronise form state of metadata query fragment to UI state. */
LogViewer.QueryForm.prototype._updateMetadataFilter = function()
{
	var metadataFragment = this.getQueryFragment( 'metadata_key_value' );

	var metadataInput = metadataFragment.find( ':input[name = "metadata_condition"]' );
	var metadataValue = metadataFragment.find( ':input[name = "metadata_value"]' );
	var condition = metadataInput.val();

	// show/hide metadata value section
	if (condition === 'is' || condition === 'is_not')
	{
		metadataFragment.find( '.metadata_value_input' ).fadeIn( 'fast' );
	}
	else
	{
		// hide() after fadeOut() to handle the case where DOM element is
		// not visible and fadeOut() returns immediately without hiding element.
		metadataFragment.find( '.metadata_value_input' ).fadeOut( 'fast' ).hide();
		metadataValue.val( "" );
	}

	// notify select replacement widget of change
	metadataInput.triggerHandler( 'liszt:updated' );

	if (this.options.debug)
	{
		console.log(
			"_updateMetadataFilter: metadataCondition = '%s'",
			metadataInput.val() );
	}
};


LogViewer.QueryForm.prototype._initFormEvents = function()
{
	// click form submit trigger submits form
	this.dom.container.find( this.options.submitFetchTrigger ).click( function()
	{
		if (this.dom.container.hasClass( 'query-in-progress' ))
		{
			// a query fetch is in progress; terminate it
			this.outputPane.boundQuery.terminateFetch();
			this.dom.container.removeClass( 'query-in-progress' );
		}
		else
		{
			// no query active; submit query form
			if (this.options.hideFiltersOnFetch)
			{
				this.dom.activeQueries.slideUp( 200 );
			}
			this.submit();
			// this.dom.container.addClass( 'query-in-progress' );
		}
	}
	.bind( this ) );

	// click "live output" trigger submits form + tailing
	this.dom.container.find( this.options.submitContinuousFetchTrigger ).click(
		function( ev )
		{
			if (this.outputPane.isTailing)
			{
				// tailing is on; turn it off
				if (this.options.hideFiltersOnFetch)
				{
					this.dom.activeQueries.slideUp( 200 );
				}

				this.dom.container.removeClass( 'tailing-in-progress' );

				// this.activateQueryType( 'period' );
				this.outputPane.options.tailLogs = false;
				this.outputPane.stopTailing();
			}
			else
			{
				// tailing is off; turn it on
				if (this.options.hideFiltersOnFetch)
				{
					this.dom.activeQueries.slideDown( 200 );
				}

				// this.dom.container.addClass( 'tailing-in-progress' );

				// this.inactivateQueryType( 'period' );
				this.outputPane.options.tailLogs = true;
				this.submit();
			}
		}
		.bind( this )
	);

	this.dom.container.on( 'click', '.metadata-icon', function( ev )
	{
		$(this).parent().next().slideToggle('fast');
		if ($(this).attr( "class" ) == "metadata-icon icon-plus-sign")
		{
			$(this).parent().addClass( 'chosen-metadata-block' );
			$(this).attr( "class", "metadata-icon icon-minus-sign" );
			$(this).attr( "title", "Collapse Metadata Section" );
		}
		else
		{
			$(this).parent().removeClass( 'chosen-metadata-block' );
			$(this).attr( "class", "metadata-icon icon-plus-sign" );
			$(this).attr( "title", "Expand Metadata Section" );
		}
	});

	this.dom.container.on( 'click', '.metadata-block-close', function( ev )
	{
		$(this).parent().slideToggle('fast');
		$(this).parent().prev().removeClass( 'chosen-metadata-block' );
		$(this).parent().prev().children().attr( "class",
			"metadata-icon icon-plus-sign" );
		$(this).parent().prev().children().attr( "title",
			"Expand Metadata Section" );
	});
};


/** Submit the query form's current query state. */
LogViewer.QueryForm.prototype.submit = function()
{
	if (!this.dom.activeQueries.is( 'form' ))
	{
		console.error(
			"Expected '%s' selector to refer to a form element - not submitted",
			this.dom.activeQueries
		);
		return;
	}

	var q = this.getQuery();
	this.outputPane.alreadyDisplayed = 0;

	if (this.outputPane.options.tailLogs)
	{
		this.dom.container.addClass( 'tailing-in-progress' );
		this.outputPane.tail( q );
		this._updateUi_queryStarted();
	}
	else
	{
		this.dom.container.addClass( 'query-in-progress' );
		this.outputPane.requestContent( q );
		this._updateUi_queryStarted();
	}

	if (this.options.addToHistory)
	{
		window.location.hash = '#' + q.toQueryString();
	}
};


/**
*   Returns a new LogViewer.Query instance populated with parameters from all the
*   currently active query fragments.
*/
LogViewer.QueryForm.prototype.getQuery = function()
{
	// return new LogViewer.Query( this.dom.activeQueries );
	var q = new LogViewer.AsyncQuery( this.dom.activeQueries );
	q.terminatedEarly = false;
	var form = this;

	jQuery( q ).on({
		'begin.query.lv': function( ev, data )
		{
			// console.log( 'begin' );
			// console.dir( data );

			this.outputPane.add( data );
			this._updateUi_queryStarted();
		}
		.bind( this ),

		'update.query.lv': function( ev, data )
		{
			// console.log( 'update' );
			// console.dir( data );

			this.outputPane.add( data );

			// no need to update UI progress here, as UI progress will be
			// updated in the progress.query.lv event callback,
			// which occurs right after this update event.
		}
		.bind( this ),

		'progress.query.lv': this._updateUi_queryInProgress.bind( this ),

		'no_update.query.lv': this._updateUi_queryInProgress.bind( this ),

		'finished.query.lv': function()
		{
			this._fetchInProgress = false;
			form.dom.container.removeClass( "tailing-in-progress" );
			form.dom.container.removeClass( "query-in-progress" );
			form._updateUi_queryComplete();
		},

		'terminated.query.lv': function()
		{
			this._fetchInProgress = false;
			this.terminatedEarly = true;
			form.dom.container.removeClass( "tailing-in-progress" );
			form.dom.container.removeClass( "query-in-progress" );
			form._updateUi_queryComplete();
		},
	});

	return q;
};


LogViewer.QueryForm.prototype._updateUi_queryStarted = function()
{
	this.dom.progressIndicator.html( 'Query in progress' );
};


LogViewer.QueryForm.prototype._updateUi_queryInProgress = function()
{
	var pi = this.dom.progressIndicator;
	var outputPane = this.outputPane;
	var query = this.outputPane.boundQuery;

	if (!query)
	{
		pi.html( '<!-- no query -->' );
		return;
	}

	if (query._fetchInProgress)
	{
		var percentComplete = Math.round( 100 *
			Math.max(
				query.seen / query.currTotal,
				outputPane.lineCount / outputPane.options.maxLineCount
			)
		);

		if (this.outputPane.isTailing)
		{
			pi.html( 'Displaying results to ' + new Date() );
		}
		else
		{
			pi.html( 'Query in progress (' + percentComplete + '% complete)' );
		}
	}
};


LogViewer.QueryForm.prototype._updateUi_queryComplete = function()
{
	// update saved queries once query has finished
	this.requestSavedQueries();

	var pi = this.dom.progressIndicator;
	var outputPane = this.outputPane;
	var query = this.outputPane.boundQuery;

	if (query.count === 0)
	{
		pi.html( 'No results to display' );
		return;
	}

	if (query.moreAvailable && !query.terminatedEarly)
	{
		var moreLinkText = "more"

		// truncated search, more results pending
		if (query.currTotal > 0)
		{
			var linesRemaining = query.currTotal - query.seen;
			pi.html( "Displaying results " +
				(outputPane.alreadyDisplayed - outputPane.lineCount + 1) + " to " +
				outputPane.alreadyDisplayed + " (" + linesRemaining +
				" possible results remain... "
			);
		}
		else
		{
			var linesRemaining = query.currTotal - query.seen;
			pi.html( "Displaying results " +
				(outputPane.alreadyDisplayed - outputPane.lineCount + 1) + " to " +
				outputPane.alreadyDisplayed + " ("
			);
			moreLinkText = "more available"
		}

		// add "more" link to fetch another page of results
		var requestMoreLink = jQuery( '<a href="javascript:void(0)">' +
										moreLinkText + '</a>' );
		requestMoreLink.click( function()
		{
			var q = this.getQuery();
			var currentQuery = this.outputPane.boundQuery;

			q.params.queryID = query.queryID

			this.outputPane.clear();
			this.outputPane.requestContent( q );
			this._updateUi_queryStarted();
		}
		.bind( this ));

		pi.append( requestMoreLink );
		pi.append( ')' );
	}
	else if ((query.seen == query.currTotal &&
			  outputPane.alreadyDisplayed == outputPane.lineCount) ||
			 query.isTailing ||
			 query.terminatedEarly)
	{
		// Completed search and all results fit on a single page
		pi.html( "Displaying " + outputPane.lineCount + " results" );
	}
	else
	{
		// Completed a multi-page search
		// pi.html( "Displaying " + outputPane.lineCount + " results" );
		pi.html( "Displaying results " +
			(outputPane.alreadyDisplayed - outputPane.lineCount + 1) + " to " +
			outputPane.alreadyDisplayed + " (search complete)" );
	}
};


/**
*	Request list of saved queries for the current WC user and update DOM.
*/
LogViewer.QueryForm.prototype.requestSavedQueries = function()
{
	jQuery.ajax({
		url: '/log/fetchQueries',
		dataType: 'json',
		success: function( data )
		{
			if (!data.queries)
			{
				console.error( "Expected a 'query' property, got:" );
				console.dir( data );
				return;
			}

			this.savedQueries = data.queries;

			// update menu
			var menu = this.dom.container.find( '.saved-queries.dropdown-menu' );
			menu.empty();

			// create a <li/> for each saved query; add a separator after
			// saved queries 'default' and 'most recent'.
			var separator = '<hr/>';
			for (var i in data.queries)
			{
				var queryName = data.queries[i].name;

				if (separator && queryName !== 'default' && queryName !== 'most recent')
				{
					menu.append( separator );
					separator = false;
				}

				var li = jQuery( '<li/>' );
				li.attr( 'query-name', queryName );
				li.text( queryName );
				li.append( '<i class="icon-remove" title="Delete this query"></i>' );

				menu.append( li );
			}

			if (this.options.debug)
			{
				console.log( "updated 'saved-queries' menu" );
			}
		}
		.bind( this ),
		error: function( jqxhr, /*String*/ textStatus, /*String?*/ exception )
		{
			console.warn( "fetchQueries failed: %s %s", textStatus, exception );
		}
	});
};


/**
*   Requests the given named query from Web Console for the current WC user, and
*   populates this query form with its query parameters. Note: Doesn't submit the
*   form.
*/
LogViewer.QueryForm.prototype.loadSavedQuery = function( /*String*/ queryName )
{
	if (!queryName)
	{
		console.warn( "Missing 'queryName' argument" );
		return;
	}

	if (!this.savedQueries)
	{
		console.warn( 'No saved queries' );
		return;
	}

	var savedQuery;
	for (var i in this.savedQueries)
	{
		if (this.savedQueries[i].name === queryName)
		{
			savedQuery = this.savedQueries[i];
			break;
		}
	}

	if (!savedQuery)
	{
		console.warn( "No saved query with name '" + queryName + "'" );
		new Alert.Warning( "No saved query with name '" + queryName + "'." );
		return;
	}

	var queryString = savedQuery.query_string;
	if (queryString === undefined)
	{
		console.warn( "saved query '%s' has no 'query_string' property", queryName );
		return;
	}

	this.loadQueryString( queryString );
};


/**
*   Populates the form with parameters from the given URI-encoded query string.
*/
LogViewer.QueryForm.prototype.loadQueryString = function( /*String*/ queryString )
{
	var query = new LogViewer.Query( queryString );
	this.loadQuery( query.getParams() );
};


/**
*   Populates the form with parameters from the given map. Map should be of form:
*
*       { pid: 1234, procs: [ 'BaseApp', 'CellApp' ], appid: [ 1 ] }
*
*   (note that single values can be given as just the value or a 1-element array)
*
*   Returns the list of DOM elements whose values were changed.
*/
LogViewer.QueryForm.prototype.loadQuery = function( /*Map*/ queryParams )
{
	if (!(typeof( queryParams ) === 'object'))
	{
		console.error( "Expected a map, but received %s", typeof( queryParams ) );
		return;
	}

	// remove queryParams with special meanings
	delete queryParams.name;

	// determine which query fragments need to be displayed by finding the
	// query types that contain the input elements with given param names.
	var container = this.dom.container;
	var queryTypesNeeded = {};
	var queryType;

	for (var paramName in queryParams)
	{
		var inputElem = container.find( ':input[name="' + paramName + '"]' ).first();
		if (inputElem.length === 0)
		{
			if (this.options.debug)
			{
				console.log(
					"Input element with name '%s' not found in container, skipping",
					paramName
				);
			}
			continue;
		}

		queryType = inputElem.parents( '.query-fragment' ).attr( 'query-type' );
		if (!queryType)
		{
			console.warn( "Couldn't determine query type of input elem '%s'", paramName );
			continue;
		}

		queryTypesNeeded[queryType] = true;
	}

	var activeQueryFragmentsByType = this.getActiveQueryTypes();
	var inactiveQueryFragmentsByType = this.getInactiveQueryTypes();

	if (this.options.debug)
	{
		console.log( "query types needed: ", Object.keys( queryTypesNeeded ) );
		console.log( "active: ", Object.keys( activeQueryFragmentsByType ) );
		console.log( "inactive: ", Object.keys( inactiveQueryFragmentsByType ) );
	}

	// then activate/inactivate those query types in the form
	for (queryType in activeQueryFragmentsByType)
	{
		if (!(queryType in queryTypesNeeded))
		{
			this.inactivateQueryType( queryType );
		}
	}

	for (queryType in inactiveQueryFragmentsByType)
	{
		if (queryType in queryTypesNeeded)
		{
			this.activateQueryType( queryType );
		}
	}

	// then finally sync the form to the query
	return this.syncFormToParams( this.dom.activeQueries, queryParams );
};


/**
*	Sets the values of form elements contained in the passed (jQuery-wrapped) form
*	to the values in the passed param map, or the currently bound {LogViewer.Query}
*	instance if not given. Eg:
*
*		queryForm.syncFormToParams( queryForm.dom.activeQueries )
*/
LogViewer.QueryForm.prototype.syncFormToParams = function( /*jQuery*/ form, /*Map?*/ params )
{
	var queryParams = params || this.outputPane.boundQuery.getParams();

	if (this.options.debug)
	{
		console.log( 'deserialising params to form:' );
		console.dir( queryParams );
	}

	// Special case handling required for multi-selects and checkboxes that
	// have options that are selected/checked in the form.
	// These have to be explicitly set to unselected/unchecked prior to
	// deserialising params into form as the deserialize call will not
	// unselect/uncheck these options.
	form.find( ':input' ).each( function()
	{
		// skip form elements that are not in the map of params
		if (!(this.name in queryParams))
			return;

		// ensure the element is not disabled in the form
		form.find( ':input[name = "' + this.name + '"]:disabled' ).removeAttr( 'disabled' );

		if (this.type === 'select-multiple' || this.type === 'checkbox')
		{
			// console.log( "reseting '%s' to no value", this.name );
			jQuery( this ).val( '' );
		}
	});

	if (queryParams['queryTime'] > 0)
	{
		// special case for queryTime, which can be one of several symbolic strings
		// or a numeric timestamp. if timestamp, then update the value for the
		// 'specific-time' option in the queryTime select menu.
		var sec = +queryParams['queryTime'];

		// console.log( "updating specific-time option: " + sec );
		form.find( 'option.specific-time' ).val( sec );
	}

	var changed = [];
	form.deserialize(
		queryParams, { change: function() { changed.push( this ); } } );

	this._updatePeriodFilter();

	this._updateMetadataFilter();

	if (this.options.debug > 1)
	{
		console.log( "form elements that changed value:" );
		console.dir( changed );
	}

	// rebuild the select-replacement widgets (jquery 'chosen' plugin)
	form.find( 'select' ).each( function()
	{
		jQuery( this ).triggerHandler( 'liszt:updated' );
	});

	return changed;
};


/** Lookup and return query fragment by query type. */
LogViewer.QueryForm.prototype.getQueryFragment = function( /*String*/ queryType )
{
	return this.dom.container.find(
		'.query-fragment[query-type="' + queryType.toLowerCase() + '"]' );
};


/**
*   Toggle query fragment corresponding to given type between
*   inactive/active containers. Returns true if query fragment is now
*   active or false otherwise.
*/
LogViewer.QueryForm.prototype.toggleActive = function( queryType )
{
	var queryFragment = this.getQueryFragment( queryType );

	// is query active or inactive?
	if (this.dom.inactiveQueries.find( queryFragment ).length)
	{
		this.activateQueryType( queryType, queryFragment );
		return true;
	}
	else if (this.dom.activeQueries.find( queryFragment ).length)
	{
		this.inactivateQueryType( queryType, queryFragment );
		return false;
	}
	else
	{
		console.error(
			"Query fragment not found in either inactive " +
			"or active query containers using selector '%s'",
			queryFragSelector
		);
		return;
	}
};


/**
*   Shifts query fragment corresponding to given type from inactive
*   to active query container.
*/
LogViewer.QueryForm.prototype.activateQueryType =
function( /*String*/ queryType, /*jQuery?*/ queryFragment )
{
	if (this.options.debug)
		console.log( "activating '%s' query fragment", queryType );

	if (!queryFragment || queryFragment.length === 0)
	{
		queryFragment = this.getQueryFragment( queryType );
	}

	queryFragment.detach();
	this._insert( queryFragment, this.dom.activeQueries );
	queryFragment.hide();
	queryFragment.addClass( 'activating' );
	queryFragment.slideDown( function() { queryFragment.removeClass( 'activating' ); } );

	jQuery( this ).triggerHandler(
		'activate.query.lv', [ queryType, queryFragment ] );
};


/**
*   Insert the given (jQuery-wrapped) query fragment into the provided container,
*   in the correct position, as determined by the value of the 'display-order'
*   attribute.
*/
LogViewer.QueryForm.prototype._insert = function( /*jQuery*/ queryFragment, /*jQuery*/ container )
{
	var queryFragmentOrder = parseInt( queryFragment.attr( 'display-order' ) );
	var queryTypes = this.getQueryTypes( container );
	var inserted = false;

	for (var type in queryTypes)
	{
		var qf = jQuery( queryTypes[type] );
		var qfOrder = parseInt( qf.attr( 'display-order' ) );
		if (queryFragmentOrder < qfOrder)
		{
			queryFragment.insertBefore( qf );
			inserted = true;
			break;
		}
	}
	if (!inserted)
	{
		queryFragment.appendTo( container );
	}
};


/**
*   Shifts query fragment corresponding to given type from active
*   to inactive query container.
*/
LogViewer.QueryForm.prototype.inactivateQueryType =
function( /*String*/ queryType, /*jQuery?*/ queryFragment )
{
	if (this.options.debug)
		console.log( "inactivating '%s' query fragment", queryType );

	if (!queryFragment || queryFragment.length === 0)
	{
		queryFragment = this.getQueryFragment( queryType );
	}

	queryFragment.addClass( 'inactivating' );
	queryFragment.slideUp( function()
	{
		queryFragment.removeClass( 'inactivating' );
		queryFragment.detach();
		this._insert( queryFragment, this.dom.inactiveQueries );

		// reset form to default values
		var form = this.dom.inactiveQueries.get( 0 );
		form.reset();

		// init form with current query's params
		this.syncFormToParams( this.dom.inactiveQueries );

		jQuery( this ).triggerHandler(
			'inactivate.query.lv', [ queryType, queryFragment ] );
	}
	.bind( this ));
};


/**
*   Show menu of available queries at DOM element target.
*   Target can be either a jQuery selector, jQuery object or DOM element.
*/
LogViewer.QueryForm.prototype.showAvailableQueriesMenu =
function( /*String|DOM|jQuery*/ domTarget )
{
	var menu = this.getAvailableQueriesMenu();
	if (!menu || menu.is( ':empty' ))
	{
		// queries menu is empty; no query fragments left to show
		// this.dom.container.find( '.add-filter' ).addClass( 'disabled' );
		return;
	}

	if (menu.is( ':visible' ))
	{
		// console.log( 'hiding queries menu (already visible)' );
		menu.fadeOut( 'bw_menu_fade_out' );
		return;
	}
	jQuery( '.dropdown-menu' ).fadeOut( 'bw_menu_fade_out' );

	// hide on click
	jQuery( document ).one( 'click', function() {
		// console.log( 'hiding queries menu due to document click' );
		menu.fadeOut( 'bw_menu_fade_out' );
	});

	menu.fadeIn( 'bw_menu_fade_in' );
};


/** Returns up-to-date menu of current inactive query fragments. */
LogViewer.QueryForm.prototype.getAvailableQueriesMenu = function()
{
	// get list of inactive query fragments
	var queryFragments = this.dom.container.find(
		'.inactive-queries-container .query-fragment' );

	var menu = this.dom.inactiveQueriesMenu;
	menu.empty();

	if (queryFragments.length === 0)
	{
		// no inactive queries; all of them are active, return empty menu
		return menu;
	}

	// populate menu from current state
	queryFragments.each( function( index, queryDiv )
	{
		var q = jQuery( queryDiv );

		// determine display name
		var displayName = q.attr( 'display-name' );
		if (!displayName)
		{
			console.error( "Element missing required 'displayName' attribute:" );
			console.dir( queryDiv );
			return;
		}

		// determine query type
		var queryType = q.attr( 'query-type' );
		if (!queryType)
		{
			console.error( "Element missing required 'query-type' attribute:" );
			console.dir( queryDiv );
			return;
		}

		var menuItem = jQuery( '<li/>' );
		menuItem.attr( 'query-type', queryType );
		menuItem.append( displayName );
		menuItem.appendTo( menu );
	});

	return menu;
};


/**
*   Returns a map of query type name to DOM query fragment for query fragments
*   that are active in the form.
*/
LogViewer.QueryForm.prototype.getActiveQueryTypes = function()
{
	return this.getQueryTypes( this.dom.activeQueries );
};


/**
*   Returns a map of query type name to DOM query fragment for query fragments
*   that are inactive in the form.
*/
LogViewer.QueryForm.prototype.getInactiveQueryTypes = function()
{
	return this.getQueryTypes( this.dom.inactiveQueries );
};


/**
*   Returns a map of query type name to DOM query fragment for queries that
*   descend from the passed container. Defaults to the DOM container of this
*   LogViewer.QueryForm.
*/
LogViewer.QueryForm.prototype.getQueryTypes = function( /*jQuery?*/ container )
{
	container = container || this.dom.container;

	var queryTypes = {};
	var queryFragments = container.find( '.query-fragment' );
	queryFragments.each( function( index, queryFragment )
	{
		var queryType = jQuery( queryFragment ).attr( 'query-type' );
		if (!queryType)
		{
			console.error( "Element missing required 'query-type' attribute:" );
			console.dir( queryFragment );
			return;
		}

		queryTypes[queryType] = queryFragment;
	});

	return queryTypes;
};


/*~~~~~~~~~~~~~~~~~~~~~~~ class LogViewer.OutputPane ~~~~~~~~~~~~~~~~~~~~~~~~~~~~*/

LogViewer.OutputPane = function( /*String|DOM*/ domTarget, /*Map*/ options )
{
	this.options = jQuery.extend( {}, LogViewer.OutputPane.Defaults, options );

	if (this.options.debug)
	{
		console.log( 'output-pane options:' );
		console.dir( this.options );
	}

	var dom = this.dom = {};
	dom.output = jQuery( domTarget );

	if (!(dom.output.length > 0))
	{
		console.error(
			"Dom target identified by selector '%s' doesn't exist in document",
			domTarget
		);
	}
	dom.container = dom.output.parent();

	this.scrollTop = 0;
	this.lineCount = 0;
	this.alreadyDisplayed = 0;

	this.initEvents();
};


LogViewer.OutputPane.Defaults =
{
	debug: 0,
	scrollTriggerHeight: 100, // px
	alwaysFollowOutput: false,
	tailPollInterval: 1000, // msec
	maxLineCount: 10000, // lines
};


LogViewer.OutputPane.prototype.initEvents = function()
{
	// this.dom.container.on( 'scroll', function( ev )
	// {
	// 	if (!this._updateInProgress && this.needsContent())
	// 	{
	// 		this.requestContent();
	// 	}
	// }
	// .bind( this ));
};


LogViewer.OutputPane.prototype.needsContent = function()
{
	this._followOutput = false;
	if (this.options.alwaysFollowOutput)
	{
		if (this.options.debug > 1)
		{
			console.log( '(alwaysFollowOutput = true)' );
		}
		return true;
	}

	var offscreenHeight = this.dom.container.scrollTop();
	var onscreenHeight = this.dom.container.prop( 'clientHeight' );
	var contentHeight = this.dom.container.prop( 'scrollHeight' );

	if (this._lastScrollHeight === offscreenHeight)
	{
		return false;
	}
	this._lastScrollHeight = offscreenHeight;

	if (offscreenHeight === 0)
	{
		// content doesn't exceed container - no scroll bars
		if (this.options.debug > 1)
		{
			console.log( '(at top of content)' );
		}
		return false;
	}

	var distFromBottom = contentHeight - (onscreenHeight + offscreenHeight);

	if (distFromBottom === 0)
	{
		if (this.options.debug > 1)
		{
			console.log( '(at bottom of content)' );
		}
		this._followOutput = true;
		return true;
	}

	if (distFromBottom < this.options.scrollTriggerHeight)
	{
		if (this.options.debug > 1)
		{
			console.log(
				'(distFromBottom = %s (threshold = %s), needsContent: true)',
				distFromBottom, this.options.scrollTriggerHeight
			);
		}
		return true;
	}

	if (this.options.debug > 1)
	{
		console.log( '(distFromBottom = %s, needsContent: false)', distFromBottom );
		// console.log(
		// 	'offscreenHeight = %s, onscreenHeight = %s, contentHeight = %s: %s',
		// 	offscreenHeight, onscreenHeight, contentHeight, needsContent
		// );
	}

	return false;
};


/**
*   Requests log lines via one or more fetch calls on the passed {LogViewer.Query}
*   instance (if given), otherwise the current {boundQuery} property.
*/
LogViewer.OutputPane.prototype.requestContent = function( /*LogViewer.Query?*/ q )
{
	if ( q && q instanceof LogViewer.Query )
	{
		if (this.options.debug)
		{
			console.log( 'binding to new query, clearing content' );
		}
		this.boundQuery = q;
		this.clear();
	}

	if (!this.boundQuery)
	{
		console.error( 'No LogViewer.Query ever provided' );
		return;
	}

	if (this.options.debug)
	{
		console.log( 'requesting content, query:' );
		console.dir( this.boundQuery );
	}

	if (this.isTailing)
	{
		this.boundQuery.fetch( this.options.tailPollInterval || 1000 );
	}
	else
	{
		this.boundQuery.fetch();
	}
};


/**
*   Follow the output of the current bound query, a la unix CLI utility "tail".
*   Results are propoagated via the "*.query.lv" family of events on the query
*   object.
*/
LogViewer.OutputPane.prototype.tail = function( /*LogViewer.Query*/ q )
{
	if (this.isTailing)
	{
		console.warn( "already tailing, returning..." );
		return;
	}

	if (!q)
	{
		console.error( "Missing query argument" );
		return;
	}

	if (this.options.debug)
	{
		console.log( 'begin tailing' );
	}

	this.isTailing = true;
	q.params.queryTime = 'now';
	q.params.period = 'to present';
	q.params.live = 1;
	q.params.limit = 0;

	this.requestContent( q );
	delete q.params.context;
	delete q.params.live;
	delete q.params.queryTime;
	delete q.params.period;
	delete q.params.limit;

	if (q instanceof LogViewer.AsyncQuery)
	{
		// no polling required; it's implicit; nothing to do here.
	}
	else
	{
		this.isTailing = setInterval(
			this.requestContent.bind( this ), this.options.tailPollInterval );
	}
};


/**
*   Stop following a tailed query.
*/
LogViewer.OutputPane.prototype.stopTailing = function()
{
	this.boundQuery.terminateFetch();

	// isTailing can be a boolean or a setInterval timer, depending on
	// whether we're using a LogViewer.AsyncQuery or synchronous LogViewer.Query.
	// A simple check for an int > 1 indicates a timer ID.
	if (this.isTailing > 1)
	{
		// it's a setInterval timer ID
		if (this.options.debug)
		{
			console.log( 'stop tailing' );
		}

		clearInterval( this.isTailing );
	}
	this.isTailing = false;
};


/** Clear this output pane of output. */
LogViewer.OutputPane.prototype.clear = function()
{
	this.lineCount = 0;
	this.dom.output.empty();

	if (this.options.debug)
	{
		console.log( '(output pane cleared)' );
	}
};


/**
*   Add lines to this output pane. Passed Map is expected to have a
*   'lines' property set to an array of lines, and an optional 'reverse'
*   boolean property indicating whether incoming lines should be appended
*   or prepended to existing log output.
*/
LogViewer.OutputPane.prototype.add = function( /*Map*/ data )
{
	if (!data.lines || data.lines.length === 0)
	{
		// console.warn( "(no lines to add)" );
		return;
	}

	if (this.options.debug)
	{
		console.log( '(%s %s lines)',
			(data.reverse ? "prepending" : "appending"), data.lines.length );

		if (this.options.debug > 1)
		{
			console.dir( data );
		}
	}

	var shouldScrollToBottom = this.shouldScrollToBottom();

	// use a temporary DOM DocumentFragment instead of adding lines via jQuery
	// because it's > an order of magnitude faster
	var docFragment = document.createDocumentFragment();

	var outputDiv = this.dom.output;

	for (var i in data.lines)
	{
		var div = document.createElement( "div" );
		if (data.lines[i].metadata != null && data.lines[i].metadata != "")
		{
			var img_link = document.createElement( 'a' );
			img_link.href = "javascript:void(0)";
			img_link.title = "Expand Metadata Section";
			img_link.className = "metadata-icon icon-plus-sign";

			var log_text_div = document.createElement( 'div' );
			log_text_div.appendChild( document.createTextNode( " " ) );
			log_text_div.appendChild( img_link );
			log_text_div.appendChild( document.createTextNode(
				data.lines[i].message ) );
			div.appendChild( log_text_div );

			var metadata_div = document.createElement( "div" );
			var close_link = document.createElement( 'a' );
			close_link.href = "javascript:void(0)";
			close_link.title = "Collapse Metadata Section";
			close_link.className = "metadata-block-close icon-remove";
			metadata_div.appendChild( close_link );
			for (var key in data.lines[i].metadata)
			{
				metadata_div.innerHTML += "<b>" + key + ":</b> " +
					data.lines[i].metadata[key] + "<br />";
			}
			metadata_div.className = "metadata-block";
			div.appendChild( metadata_div );
		}
		else
		{
			div.appendChild( document.createTextNode( "   " +
				data.lines[i].message ) );
		}

		if (!data.reverse)
		{
			docFragment.appendChild( div );
		}
		else
		{
			docFragment.insertBefore( div, docFragment.childNodes[0] );
		}
	}

	if (!data.reverse)
	{
		outputDiv.append( docFragment );
	}
	else
	{
		outputDiv.prepend( docFragment );
	}

	this.lineCount += data.lines.length;
	this.alreadyDisplayed += data.lines.length;

	// remove lines if necessary
	if (this.lineCount > this.options.maxLineCount)
	{
		var numToRemove = this.lineCount - this.options.maxLineCount;
		if (this.options.debug)
		{
			console.log( '(removing %s lines from %s)',
				numToRemove, data.reverse ? "end" :"beginning" );
		}

		if (!data.reverse)
		{
			outputDiv.children().slice( 0, numToRemove ).remove();
		}
		else
		{
			outputDiv.children().slice( this.lineCount - numToRemove ).remove();
		}

		this.lineCount -= numToRemove;
	}

	if (shouldScrollToBottom)
	{
		this.scrollToBottom();
	}
};


/**
*   Sets the user's view to the bottom of the current container content.
*/
LogViewer.OutputPane.prototype.scrollToBottom = function()
{
	var onscreenHeight = this.dom.container.prop( 'clientHeight' );
	var contentHeight = this.dom.container.prop( 'scrollHeight' );
	if (contentHeight > onscreenHeight)
	{
		// console.log( '(force scroll to bottom)' );
		this.dom.container.scrollTop( contentHeight - onscreenHeight );
	}
};


LogViewer.OutputPane.prototype.shouldScrollToBottom = function()
{
	if (this.options.alwaysFollowOutput)
	{
		// console.log( '(alwaysFollowOutput = true)' );
		return true;
	}

	// height user has scrolled content offscreen (px)
	var offscreenHeight = this.dom.container.scrollTop();

	// height of the content in container (px)
	var onscreenHeight = this.dom.container.prop( 'clientHeight' );

	// full height of container content, uncropped by container bounds (px)
	var contentHeight = this.dom.container.prop( 'scrollHeight' );

	if (this.options.debug > 1)
	{
		console.log(
			'onscreen = %s, offscreen = %s, contentHeight = %s',
			onscreenHeight, offscreenHeight, contentHeight
		);
	}

	if (offscreenHeight === 0)
	{
		// view is at top of content
		// console.log( '(at top of content)' );
		if (this.isTailing && (contentHeight <= onscreenHeight))
		{
			// begin tailing logs by default
			return true;
		}
		return false;
	}

	var distFromBottom = contentHeight - (onscreenHeight + offscreenHeight);

	if (distFromBottom === 0)
	{
		// console.log( '(at bottom of content)' );
		return true;
	}

	return false;
};


/* log_viewer.js */

"use strict";

/*
*   Classes for remotely starting and monitoring BigWorld server processes.
*   Monitoring capability is pretty rudimentary - merely follows message_logger
*   logs to infer process progress/state/exit.
*/

window.BigWorld = window.BigWorld || {};


/**
*	Simple base class for starting and monitoring a BigWorld server process.
*/
BigWorld.Process = function( /*Object*/ options )
{
	if (!arguments.length)
	{
		return;
	}

	jQuery.extend( this, BigWorld.Process.DEFAULTS, options );
};


BigWorld.Process.DEFAULTS =
{
	// displayed name of the process
	name: '',

	// url that will start this process (see JSON api docs)
	url: '',

	// machine name or IP on which to run the process
	machine: '',

	// DOM destination of log output
	logOutput: jQuery( '.output' ),

	// LogViewer query params that will be used to tail the logs
	// for this process
	logviewerQuery: {},

	// length of time after which a process will be considered to have terminated
	// if no log lines received.
	logOutputTimeout: 30000, // msec

	// time interval between timeout checks
	logOutputTimeoutCheckFrequency: 2000, // msec
};


/** Returns the URL that will start this process on the server. */
BigWorld.Process.prototype.getUrl = function()
{
	if (this.machine)
	{
		return this.url + '?machine=' + encodeURIComponent( this.machine );
	}

	return this.url;
};


/** Starts this process on the server. */
BigWorld.Process.prototype.start = function()
{
	if (this._operationInProgress)
	{
		new Alert.Warning( this.name + ' in progress' );
		return;
	}

	if (!this.logOutput || !this.logOutput.length)
		console.warn( "(output destination doesn't exist in DOM)" );

	// create a LogViewer query to tail the logs for the consolidate operation
	this.logs = new LogViewer.AsyncQuery( this.logviewerQueryParams );

	// record lines produced
	this.logs.outputLines = [];

	this._lastLogUpdate = Date.now();

	// watch incoming logs for progress messages
	var _this = this;
	jQuery( this.logs ).on({
		'update.query.lv': function( /*jQuery.Event*/ event, /*Object*/ data )
		{
			var line;
			for (var i in data.lines)
			{
				line = data.lines[i];
				_this.logs.outputLines.push( line.message );

				// 'live' queries unconditionally return 10 lines of logs prior
				// to actual query results, so discard these 10 lines.
				if (_this.logs.outputLines.length <= 10) continue;

				var lineDiv = jQuery( '<div>' + line.message + '</div>' );
				_this.logOutput.append( lineDiv );

				_this.onReceiveLine( line.message, lineDiv );
			}

			// timestamp receipt of log update
			if (data.lines.length > 0)
			{
				_this._lastLogUpdate = Date.now();
			}
		},
	});

	// start following logs *before* starting process
	_this.logs.fetch();

	// start
	var jqXhr = this._operationInProgress = jQuery.ajax(
	{
		url: this.getUrl(),
		dataType: 'json',
		success: function( /*Object*/ process )
		{
			if (process.error)
			{
				new Alert.Error(
					"Start process failed:</br>" + process.error,
					{ duration: 10000 }
				);
				return;
			}

			this.process = process;

			_this.logOutput.append(
				'<div>Started '
				+ _this.name
				+ ' on '
				+ process.hostname
				+ ', pid is '
				+ process.pid
				+ ', awaiting progress</div>'
			);

			_this._timeoutChecker = window.setInterval(
				_this._checkForTimeout.bind( _this ), _this.logOutputTimeoutCheckFrequency );
		},
		error: function( xhr, /*String*/ textStatus, /*String?*/ error )
		{
			try
			{
				var errorResponse = jQuery.parseJSON( xhr.responseText );
				var errorMsg = errorResponse.message +
					". Check bwmachined logs for further details.";

				_this.logOutput.append( '<div>' + errorMsg + '</div>' );
				new Alert.Error(
					"Operation failed:<br/>" + errorMsg,
					{ duration: 10000 }
				);
			}
			catch ( ex )
			{
				console.warn( "Expected JSON, got: '%s'", xhr.responseText );
				new Alert.Error(
					_this.name + " failed:</br>" + error,
					{ duration: 10000 }
				);
			}

			_this.onExit();
		},
	});

	return jqXhr;
}


BigWorld.Process.prototype._checkForTimeout = function( )
{
	if (!this._timeoutChecker)
	{
		// no longer/not checking for log query timeout
		return;
	}

	if (!this.logs)
	{
		// not logging
		return;
	}

	var now = Date.now();
	var elapsed = now - this._lastLogUpdate;

	if (elapsed < this.logOutputTimeout)
	{
		// no timeout
		console.debug( "%d msecs since last logs received", elapsed );
		return;
	}

	// timed out,
	clearTimeout( this._timeoutChecker );
	delete this._timeoutChecker;

	console.warn(
		"terminating log tail as no new logs seen for %d secs",
		elapsed / 1000
	);

	new Alert.Warning(
		"Process appears to have exited prematurely or failed due " +
		"to an unknown error. Check the logs."
	);

	this.onExit();
};


BigWorld.Process.prototype.onReceiveLine =
/*abstract*/ function( /*String*/ line, /*jQuery*/ lineDiv )
{
	// abstract method, do nothing
};


BigWorld.Process.prototype.onExit = function()
{
	if (this.logs)
	{
		this.logs.terminateFetch();
	}

	if (this._timeoutChecker)
	{
		window.clearInterval( this._timeoutChecker );
		delete this._timeoutChecker;
	}

	this._operationInProgress = null;
	jQuery( this ).triggerHandler( 'exit' );
};


/*~~~~~~~~~~~~~~~~~~~ class BigWorld.ConsolidateDBsProcess ~~~~~~~~~~~~~~~~~~~~~~*/

BigWorld.ConsolidateDBsProcess = function( /*Object*/ options )
{
	var opts = jQuery.extend(
		{}, BigWorld.ConsolidateDBsProcess.DEFAULTS, options );

	BigWorld.Process.call( this, opts );

	if (this.clearDbs)
	{
		this.name += ' --clear';
		this.url = this.clearDbsUrl;
	}
};

BigWorld.ConsolidateDBsProcess.extends( BigWorld.Process );

BigWorld.ConsolidateDBsProcess.DEFAULTS =
{
	name: 'consolidate_dbs',
	url: '/cc/consolidateSecondaryDatabases',

	clearDbs: false,
	clearDbsUrl: '/cc/clearSecondaryDatabases',

	logviewerQueryParams:
	{
		live: true,
		queryTime: 'now',
		period: 'to present',
		procs: ['ConsolidateDBs'],
		source: ['C++'],
		show: ['time', 'category', 'message'],
	}
};


BigWorld.ConsolidateDBsProcess.prototype.onReceiveLine =
function( /*String*/ line, /*jQuery*/ lineDiv )
{
	if (line.match( "No secondary databases to consolidate" ))
	{
		this.onExit();
	}
	else if (line.match( "ConsolidateDBsApp::clearSecondaryDBEntries: Cleared" ))
	{
		this.logOutput.append( '<div>complete</div>' );
		jQuery( this ).triggerHandler( 'success' );
		this.onExit();
	}
	else if (
		line.match( "Failed to establish a locked connection to the database" ) ||
		line.match( "Unable to connect" ) )
	{
		jQuery( this ).triggerHandler( 'databaseConnectFailed' );
		lineDiv.addClass( 'error' );
		this.onExit();
	}
};


/*~~~~~~~~~~~~~~~~~~~~~~ class BigWorld.SyncDBProcess ~~~~~~~~~~~~~~~~~~~~~~~~~~*/

BigWorld.SyncDBProcess = function( /*Object*/ options )
{
	var opts = jQuery.extend(
		{}, BigWorld.SyncDBProcess.DEFAULTS, options );

	BigWorld.Process.call( this, opts );
};

BigWorld.SyncDBProcess.extends( BigWorld.Process );

BigWorld.SyncDBProcess.DEFAULTS =
{
	name: 'sync_db',
	url: '/cc/syncEntityDefs',
	logviewerQueryParams:
	{
		live: true,
		queryTime: 'now',
		period: 'to present',
		procs: ['SyncDB'],
		// source: ['C++'],
		show: ['time', 'severity', 'process', 'category', 'message'],
	}
};


BigWorld.SyncDBProcess.prototype.onReceiveLine =
function( /*String*/ line, /*jQuery*/ lineDiv )
{
	if (line.match( "Sync to database successful" ))
	{
		jQuery( this ).triggerHandler( 'success' );
		this.onExit();
	}
	else if (line.match( "Initialisation failed" ))
	{
		this.onExit();
	}
	else if (line.match( "Sync to database failed" ))
	{
		this.onExit();
	}
	else if (
		line.match( "Failed to establish a locked connection to the database" ) ||
		line.match( "Unable to connect" ) )
	{
		jQuery( this ).triggerHandler( 'databaseConnectFailed' );
		lineDiv.addClass( 'error' );
		this.onExit();
	}
};



/*~~~~~~~~~~~~~~~~~~~~~~ class BigWorld.ClearAutoLoadProcess ~~~~~~~~~~~~~~~~~~~~~~~~~~*/

BigWorld.ClearAutoLoadProcess = function( /*Object*/ options )
{
	var opts = jQuery.extend(
		{}, BigWorld.ClearAutoLoadProcess.DEFAULTS, options );

	BigWorld.Process.call( this, opts );
};

BigWorld.ClearAutoLoadProcess.extends( BigWorld.Process );


BigWorld.ClearAutoLoadProcess.DEFAULTS =
{
	name: 'clear_autoload',
	url: '/cc/clearAutoloadedEntities',
	logviewerQueryParams:
	{
		live: true,
		queryTime: 'now',
		period: 'to present',
		procs: ['ClearAutoLoad'],
		source: ['C++'],
		show: ['time', 'severity', 'process', 'category', 'message'],
	}
};


BigWorld.ClearAutoLoadProcess.prototype.onReceiveLine =
function( /*String*/ line, /*jQuery*/ lineDiv )
{
	if (line.match( "Cleared auto-load data" ))
	{
		jQuery( this ).triggerHandler( 'success' );
		this.onExit();
	}
	else if (
		line.match( "Failed to establish a locked connection to the database" ) ||
		line.match( "Unable to connect" ) )
	{
		jQuery( this ).triggerHandler( 'databaseConnectFailed' );
		lineDiv.addClass( 'error' );
		this.onExit();
	}
	else if (line.match( "Failed to initialise Entity Type Mappings" ))
	{
		jQuery( this ).triggerHandler( 'entityTypeMappingsInitialisationFailed' );
		lineDiv.addClass( 'error' );
		this.onExit();
	}
};



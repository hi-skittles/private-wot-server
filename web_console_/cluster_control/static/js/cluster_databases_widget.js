"use strict";

window.BigWorld = window.BigWorld || {};

/**
*   Widget has 2 states:
*   1. initial (awaiting user to select action, no CSS class)
*   2. process is in the running state (CSS class 'running-process')
*/
BigWorld.DatabaseWidget = function( /*String|jQuery|DOM*/ domSelector )
{
	this.initDom( jQuery( domSelector ) );
	this.initEvents();
};


BigWorld.DatabaseWidget.prototype.initDom = function( /*jQuery*/ container )
{
	console.assert( container );
	console.assert( container.length,
		"container '%s' doesn't exist in DOM", container.selector );

	var dom = this.dom = {};
	dom.container = container;
	dom.output = container.find( '.output' );
	if (!dom.output.length)
	{
		console.warn(
			"output selector '%s' not found in DOM",
			dom.output.selector
		);
	}

	return dom;
};


BigWorld.DatabaseWidget.prototype.initEvents = function()
{
	var container = this.dom.container;

	container.on( 'click', '.cluster-control-actions button', function( ev )
	{
		if (this.runningProcess)
		{
			console.warn( this.runningProcess.name + " in progress, ignoring" );
			return false;
		}

		var action = jQuery( ev.target ).attr( 'action' );
		console.assert( action );

		jQuery( '.alert-notification-container' ).empty();
		container.addClass( 'running-process ' + action );
		this.execute( action );
	}
	.bind( this ));
};


BigWorld.DatabaseWidget.prototype.execute = function( /*String*/ action )
{
	this.action = action;
	var output = this.dom.output;
	console.assert( output && output.length, output );

	var options = { logOutput: output };
	var machine = this.dom.container.find( 'select[name = "machine"]' ).val();
	if (machine)
	{
		options.machine = machine;
	}

	switch( action )
	{
		case "consolidate_dbs":
			return this.startProcess(
				BigWorld.ConsolidateDBsProcess, options );

		case "clear_dbs":
			options.clearDbs = true;
			return this.startProcess(
				BigWorld.ConsolidateDBsProcess, options );

		case "clear_autoload":
			return this.startProcess(
				BigWorld.ClearAutoLoadProcess, options );

		case "sync_db":
			return this.startProcess(
				BigWorld.SyncDBProcess, options );
	}
};


BigWorld.DatabaseWidget.prototype.startProcess =
function( /*BigWorld.Process class*/ Process, /*object*/ options )
{
	if (this.runningProcess)
	{
		console.warn(
			"%s already in progress, ignoring",
			this.runningProcess.name
		);
		return;
	}

	var running = this.runningProcess = new Process( options );
	this.dom.output.html(
		'<div>Attempting to start process ' + running.name +
		' on ' + (running.machine || 'any machine') + '...</div>'
	);
	running.start();

	var _this = this;
	jQuery( running ).on(
	{
		exit: function()
		{
			console.log( "%s exited", this.name );
			_this.runningProcess = null;
			_this.dom.container.removeClass(
				'running-process ' + _this.action );
		},

		success: function()
		{
			new Alert.Info( this.name + " complete" );
			_this.runningProcess = null;
			_this.dom.container.removeClass(
				'running-process ' + _this.action );
			_this.dom.output.append( '<div>Process complete</div>' );
		},

		databaseConnectFailed: function()
		{
			new Alert.Error(
				this.name +
				" failed: Could not connect to the database. ",
				{ duration: 10000 }
			);
			_this.runningProcess = null;
			_this.dom.container.removeClass(
				'running-process ' + _this.action );
			_this.dom.output.append(
				'<div>Process exited prematurely as it could not connect to the database</div>' );
		},
		
		
		entityTypeMappingsInitialisationFailed : function()
		{
			new Alert.Error(
				this.name +
				" failed: Could not initialise Entity Type Mappings. ",
				{ duration: 10000 }
			);
			_this.runningProcess = null;
			_this.dom.container.removeClass(
				'running-process ' + _this.action );
			_this.dom.output.append(
				'<div>Process exited prematurely as it could not initialise Entity Type Mappings</div>' );
		},
	});

	return running;
};


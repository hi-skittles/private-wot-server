"use strict";

if (!window.jQuery) throw new Error( "jquery lib not loaded" );
if (!window.jQuery.fn.dataTable) throw new Error( "jquery-dataTable plugin lib not loaded" );
if (!window.DynamicTable) throw new Error( "DynamicTable lib not loaded" );


/**
*   Synopsis:
*
*		new ControlClusterWidget( '#cluster-control-div' );
*/
var ControlClusterWidget = function( /*string or jquery*/ domTarget, /*Map*/ options )
{
	var opts = jQuery.extend( true, {}, ControlClusterWidget.DEFAULTS, options );
	DynamicTable.call( this, domTarget, opts );

	// map of layout errors that have been shown to user
	this._shownLayoutErrors = {};
};


/* class ControlClusterWidget extends DynamicTable */
ControlClusterWidget.prototype = new DynamicTable;
ControlClusterWidget.prototype.constructor = ControlClusterWidget;


ControlClusterWidget._roundPercent = function( value, reason, process )
{
	if (reason === 'sort' || reason === 'type')
		return value;

	if (value >= 0)
	{
		return (Math.round( value * 1000 ) / 10 ) + '%';
	}
};


ControlClusterWidget.DEFAULTS = {

	user: '',
	title: "Process list",
	baseurl: '/cc/api/procs',
	poll: 2500, // msecs
	showContextMenu: true,

	/* datatable opts */

	sDom: 'R<"dynamic-table-header"fr>' +
		'<"dynamic-table-header cluster-control-actions">' +
		't' +
		'<"dynamic-table-footer"ip>',

	// bServerSide: true,
	bServerSide: false,

	// json path to the data for rows returned by 'baseurl'
	sAjaxDataProp: 'procs',

	bDeferRender: true,
	iDisplayLength: 50, // rows

	aaSorting: [ [1, 'asc'], [0, 'asc'] ],
	aoColumns:
	[
		{
			// column 0
			sTitle: 'Process',
			mData: 'label',
			sClass: "proc",
			mRender: function( label, ignore, process, t )
			{
				return '<a href="/watchers/tree/show?machine=' +
					process.machine.name + ';pid=' + process.pid + '">' +
					label + '</a>';
			},
		},
		{
			// column 1
			// this is a hidden column used only for sorting
			bVisible: false,
			sTitle: 'Component',
			mData: 'isSingletonProcess',
			sDefaultContent: '',
			mRender: function( isSingletonProcess )
			{
				// make world processes sort before worker processes
				return isSingletonProcess ? 1 : 2;
			}
		},
		{
			// column 2
			sTitle: 'Machine',
			mData: 'machine.name',
			sClass: "machine",
			mRender: function( machine, reason, process )
			{
				return '<a href="/cc/machine?machine=' + process.machine.name +
					'">' + machine + '</a>';
			},
		},
		{
			// column 3
			bVisible: false,
			sTitle: 'User',
			mData: 'username',
			sClass: "user",
		},
		{
			sTitle: 'CPU Load',
			mData: 'load',
			bSearchable: false,
			asSorting: [ 'desc', 'asc' ],
			mRender: ControlClusterWidget._roundPercent,
		},
		{
			sTitle: 'Memory Usage',
			mData: 'mem',
			bSearchable: false,
			asSorting: [ 'desc', 'asc' ],
			mRender: ControlClusterWidget._roundPercent,
		},
		{
			sTitle: 'PID',
			mData: 'pid',
		},
		{
			sTitle: 'Actions',
			mData: 'pid',
			bSortable: false,
			bSearchable: false,
			sClass: "process-actions",
			mRender: function( pid, ignore, process, t )
			{
				// note: no 'this' pointer to a ControlClusterWidget in this context
				var actions = ControlClusterWidget.prototype.getActionsForProcess( process );

				var items = [];
				var hasNestedItems = false;
				var visit = function( stack )
				{
					while (stack.length > 0)
					{
						var element = stack.shift();

						if (element instanceof Array)
						{
							hasNestedItems = true;
							items.push( '<div class="context-menu nested-menu">' );
							visit( element );
							items.push( '</div>' );
							return;
						}

						items.push( element );
					}
				};
				visit( actions );

				if (hasNestedItems)
				{
					items.push( '<i class="icon-caret-down nested-menu-opener"></i>' );
				}

				return items.join( '' );

				// show icon+link only for top-level/common actions
				var topLevelActions = [];
				for (var i in actions)
				{
					if (actions[i] instanceof Array)
					{
						continue;
					}
					topLevel.push( actions[i] );
				}
			},
		},
	],

	sAjaxSource: "dummy", // a dummy (true) value to make "sLoadingRecords" appear

	oLanguage: {
		sInfo: "Showing _START_ to _END_ of _TOTAL_ processes",
		sInfoEmpty: "",
		sEmptyTable: "No processes",
		sZeroRecords: "No matching processes",
		sLoadingRecords: "Waiting for Server...",
	},

	fnCreatedRow: function( tableRow, columnData, rowIndex )
	{
		var rowId = columnData.label;
		jQuery( tableRow ).attr( 'row-id', rowId );
	},

	fnDrawCallback: function( datatableSettings )
	{
		// table already has a default sorting of singleton processes first, then
		// ascending process name alphabetic, so initially override the dataTables
		// default to show that the column is sorted.
		var sortCols = datatableSettings.aaSorting;
		if (sortCols.length === 2 && sortCols[ 0 ][ 0 ] === 1 && sortCols[ 1 ][ 0 ] === 0)
		{
			var th = this.find( 'thead .sorting_asc' );
			th.removeClass( 'sorting_asc' ).addClass( 'sorting' );
		}
	},
};


/**
*   Returns array of menu-items, which may coappid=' + process.id + 'ntain nested arrays, which is
*   intended to indicate a nominal grouping of action items. Nested array can
*   be flattened into a single array with the expression:
*
*       flattenedArray = jQuery.map( nestedArray, function( el ) { return el; } );
*/
ControlClusterWidget.prototype.getActionsForProcess = function( /*Object*/ process )
{
	var universalActions = [
		'<a href="/watchers/tree/show?machine=' +
		process.machine.name + ';pid=' + process.pid +
		'" title="View watchers">' +
		'<i class="icon-search"></i></a>'
	];

	if (process.type)
	{
		universalActions.push(
			'<a href="/log/search#procs=' + process.type +
			';serveruser=' + process.username + ';queryTime=server+startup' +
			((process.id > 0) ? ';appid=' + process.id : '') +
			'" title="View logs">' +
			'<i class="icon-book"></i></a>'
		);
	}

	if (process.hasPythonConsole)
	{
		universalActions.push(
			'<a href="/console/console?process=' + process.label +
			';host=' + process.machine.ip + ';user=' + process.username +
			'" title="Open python console">' +
			'<i class="icon-list-alt"></i></a>'
		);
	}

	// process-type-specific actions
	var otherActions = [];
	if (process.label === 'message_logger')
	{
		otherActions.push(
			'<a class="async" title="Roll logs" href="' +
			'/callExposed?type=process;method=breakSegments;machine=' +
			process.machine.name + ';pid=' + process.pid +
			'"><i class="icon-share-alt"></i></a>'
		);
	}

	if (process.label.match( /^bots/ ))
	{
		otherActions.push(
			'<a class="prompt-for-bots" title="Add bots" href="' +
			'/callExposed?type=process;method=addBots;machine=' +
			process.machine.name + ';pid=' + process.pid +
			';__num=1"><i class="icon-plus"></i></a>'
		);

		otherActions.push(
			'<a class="prompt-for-bots" title="Remove bots" href="' +
			'/callExposed?type=process;method=delBots;machine=' +
			process.machine.name + ';pid=' + process.pid +
			';__num=1"><i class="icon-minus"></i></a>'
		);
	}

	// process actions
	if (process.isRetirable)
	{
		otherActions.push(
			'<a class="dangerous async" href="retireApp?machine=' +
			process.machine.name + ';pid='  + process.pid  + ';user=' +
			process.username + '" title="Retire process">' +
			'<i class="icon-off"></i></a>'
		);
	}

	if (process.isStoppable)
	{
		otherActions.push(
			'<a class="dangerous" href="killproc?machine=' +
			process.machine.name + ';pid=' + process.pid + ';signal=9" ' +
			'title="Kill process">' +
			'<i class="icon-stop"></i></a>',

			'<a class="dangerous" href="killproc?machine=' +
			process.machine.name + ';pid=' + process.pid + ';signal=3"' +
			'title="Kill process and dump core">' +
			'<i class="icon-bolt"></i></a>'
		);
	}

	if (otherActions.length > 0)
		universalActions.push( otherActions );

	return universalActions;
};


/** See http://www.datatables.net/usage/server-side for explanation of params. */
ControlClusterWidget.prototype.getModelUpdateUrl = function( /*Array of Object*/ datatableParams )
{
	return (
		this.options.user
		? this.options.baseurl + '?user=' + this.options.user
		: this.options.baseurl
	);
};


ControlClusterWidget.prototype._initEvents = function()
{
	DynamicTable.prototype._initEvents.call( this );

	// add rclick menu
	this._initContextMenu();

	// attach per-update event handler to show cluster actions that are
	// appropriate to current server state.
	this._initClusterActions();

	// make process action links with class "dangerous" require explicit confirmation
	// note this will only work for links that reside within this container.
	this.dom.container.on( 'click', 'a.dangerous', function( ev )
	{
		if (!this.title)
		{
			console.dir( this );
			throw new Error( "Dangerous links require 'title' attribute" );
		}

		if (window.confirm( "Confirm action: " + this.title ))
		{
			// user clicked 'OK'
			return true;
		}
		else
		{
			// user clicked 'cancel'
			ev.stopImmediatePropagation();
			return false;
		}

		return confirmed;
	});

	// make links with class "async" execute as ajax calls with an Alert.
	// have to bind 2 events separately as .context-menu's do not live
	// inside the table DOM container div.
	this.dom.container.on( 'click', 'a.async', this._execAsyncAction );
	jQuery( document ).on( 'click', '.context-menu a.async', this._execAsyncAction );

	// special-case for 'bots' process, which requires user input
	jQuery( document ).on( 'click', 'a.prompt-for-bots', function( ev )
	{
		var a = jQuery( this );
		var action = a.prop( 'title' ) || a.prop( 'text' ) || 'Web Console';
		var numBots = window.prompt( action + ': Enter the number of bots' );

		if (!numBots) return false;
		numBots = parseInt( numBots );
		if (!(numBots > 0)) return false;

		this.href = this.href.replace( /__num=\d+/, '__num=' + numBots );

		ev.stopImmediatePropagation();
		a.parents( '.context-menu' ).click();

		ControlClusterWidget.prototype._execAsyncAction.call( this, ev );
		return false;
	});

	// show per-process links in a nested menu on click
	this.dom.container.on( 'click touchend', '.nested-menu-opener', function( ev )
	{
		var td = jQuery( ev.target ).parents( '.process-actions' );
		var position = td.offset();
		position.left += td.outerWidth();
		position.top += td.outerHeight();

		var td = jQuery( ev.target ).parents( 'td' );
		var tr = td.parent().get( 0 );
		var process = this.datatable.fnGetData( tr );

		var menu = jQuery( '<div/>' );
		menu.addClass( 'context-menu contextual-menu-showing' );
		menu.css({
			position: 'absolute',
			display: 'none',
		});

		menu.append( '<h3>' + process.label + ' on ' + process.machine.name + '</h3>' );

		var actions = this.getActionsForProcess( process );

		// flatten array
		actions = jQuery.map( actions, function( el ) { return el; } );

		for (var i in actions)
		{
			menu.append( actions[ i ] );
		}

		jQuery( '.contextual-menu-showing' ).remove();
		menu.appendTo( 'body' );

		menu.find( 'a' ).each( function() {
			var a = jQuery( this );
			var t = a.prop( 'title' );
			a.removeAttr( 'title' );
			a.append( jQuery( '<label/>' ).append( t ) );
		});

		menu.addClass( 'contextual-menu-showing' );
		position.left -= menu.outerWidth();
		menu.css({ left: position.left, top: position.top });

		var removeMenu = function()
		{
			if (menu)
			{
				menu.fadeOut( 200, function()
				{
					menu.remove();
					menu = null;
				});
			}
		};
		menu.on( 'click', removeMenu );
		jQuery( document ).one( 'click', removeMenu );

		ev.stopPropagation();
		menu.fadeIn();
	}
	.bind( this ));

	// //	click on the <td> for process name opens watcher page for process
	// this.dom.table.on( 'click touchend', 'td.proc', function( ev )
	// {
	// 	var tr = ev.target.parentNode;
	// 	var process = this.datatable.fnGetData( tr );

	// 	this.disconnectModel();
	// 	document.location = '/watchers/tree/show?machine=' +
	// 		process.machine.name + ';pid=' + process.pid;
	// }
	// .bind( this ));

	// //	click on the <td> for machine name opens machine detail page
	// this.dom.table.on( 'click touchend', 'td.machine', function( ev )
	// {
	// 	var tr = ev.target.parentNode;
	// 	var process = this.datatable.fnGetData( tr );

	// 	this.disconnectModel();
	// 	document.location = 'machine?machine=' + process.machine.name;
	// }
	// .bind( this ));
}


/** Event handler; 'this' points to a HTMLAnchor */
ControlClusterWidget.prototype._execAsyncAction = function( ev )
{
	var a = jQuery( this );
	var url = a.prop( 'href' );
	var action = a.prop( 'title' ) || a.prop( 'text' ) || 'Action';

	jQuery.ajax({
		url: url,
		dataType: 'json',
		success: function( data )
		{
			var error = data.error || data.warning;
			if (error)
			{
				new Alert.Warning( action + ': ' + error );
			}
			else
			{
				if (data.info)
				{
					new Alert.Info( action + ' successful: ' + data.info );
				}
				else
				{
					new Alert.Info( action + ' successful' );
				}
			}
		},
		error: function()
		{
			new Alert.Warning( action + ' failed' );
		},
	});

	ev.stopImmediatePropagation();
	return false;
};


ControlClusterWidget.prototype._makeButton = function( /*String*/ url, /*String*/ text )
{
	// note: doesn't handle URLs with existing params
	return ( this.options.user
		? '<a href="' + url + '?user=' + this.options.user + '" class="button">' + text + '</a>'
		: '<a href="' + url + '" class="button">' + text + '</a>'
	);
};


ControlClusterWidget.prototype._initClusterActions = function()
{
	this.dom.clusterActions = jQuery( '.cluster-control-actions', this.dom.container );
	this.dom.clusterActions.html( this._makeButton( 'startproc', 'Start Processes' ) );

	// update cluster actions on every update tick
	jQuery( this ).on( 'updateModel.dt', function( event, data )
	{
		if (data.isServerRunning)
		{
			this.dom.clusterActions.html([
				this._makeButton( 'startproc', 'Start Processes' ),
				this._makeButton( 'restart', 'Restart Server' )
			].join( '' ));

			// if server is missing key processes, then show a 'kill' option
			// as 'stop' is not deterministic
			if (data.missingProcessTypes)
			{
				this.dom.clusterActions.append(
					this._makeButton( 'kill', 'Stop Server' ) );
			}
			else
			{
				this.dom.clusterActions.append(
					this._makeButton( 'stop', 'Stop Server' ) );
			}

			// save layout link requires a little extra love because of the
			// window.prompt and the unreliable nature of 'return false' in
			// inline event handlers.
			var saveLayoutButton = jQuery(
				'<a class="async button" title="Save layout" ' +
				'href="saveLayout?name=default">Save Layout</a>' );

			saveLayoutButton.click( function( ev )
			{
				var name = prompt( 'Please enter a name to save this layout as' );
				if (name)
				{
					this.href = 'saveLayout?name=' + name;
				}
				else
				{
					new Alert.Info( 'Save layout cancelled' );
					ev.preventDefault();
					return false;
				}
			});
			this.dom.clusterActions.append( saveLayoutButton );
		}
		else
		{
			Alert.dismiss( 'missing-server-procs' );

			this.dom.clusterActions.html(
				this._makeButton( 'start', 'Start The Server' ) );
		}

		if (data.missingProcessTypes)
		{
			var missingProcs = data.missingProcessTypes.join( ', ' );
			var message = "Missing critical server procs: " + missingProcs;

			var alert = new Alert.Error( message, {
				id: 'missing-server-procs',
				duration: 5000,
			});
		}

		// show layout errors as notifications
		// don't show the same layout error more than once.
		if (data.layoutErrors && data.layoutErrors.length > 0)
		{
			var alerts = jQuery( '.alert-notification-container' );
			for (var i in data.layoutErrors)
			{
				var message = data.layoutErrors[ i ];
				var id = Alert.getIdForMessage( message );
				if (this._shownLayoutErrors[ id ])
				{
					continue;
				}

				var alert = new Alert.Warning( message, {
					id: id,
					duration: 0,
					dismissable: true,
				});

				this._shownLayoutErrors[ id ] = true;
			}
		}
	});
};


ControlClusterWidget.prototype.connectModel = function()
{
	if (this._isConnected)
	{
		console.warn( "model already connected, ignoring..." );
		return;
	}

	var pollOnce = function()
	{
		this.requestModelUpdate();

		// adjust polling frequency based on #processes
		var pollInterval = this.options.pollInterval;
		if (this.data && this.data.procs)
		{
			var numProcs = this.data.procs.length;
			if (numProcs > 10)
			{
				var k = Math.log( numProcs ) / Math.LN10;
				pollInterval *= k;
			}
		}

		this._isConnected = window.setTimeout( pollOnce, pollInterval );
	}
	.bind( this );

	this._isConnected = window.setTimeout( pollOnce, this.options.pollInterval );
};


ControlClusterWidget.prototype._initContextMenu = function()
{
	if (!this.options.showContextMenu)
	{
		console.warn( "context menu currently disabled" );
		return;
	}

	this.datatable.on( 'contextmenu', 'tbody tr', function( ev )
	{
		ev.preventDefault();
		var process = this.datatable._( ev.currentTarget )[ 0 ];

		var menu = jQuery( '<div/>' );
		menu.addClass( 'context-menu contextual-menu-showing' );
		menu.css({
			display: 'none',
			left: ev.pageX,
			top: ev.pageY,
		});

		menu.append( '<h3>' + process.label + ' on ' + process.machine.name + '</h3>' );

		var actions = this.getActionsForProcess( process );

		// flatten array - discard nested structure
		actions = jQuery.map( actions, function( el ) { return el; } );

		for (var i in actions)
		{
			menu.append( actions[ i ] );
		}

		jQuery( '.contextual-menu-showing' ).remove();
		menu.appendTo( 'body' );

		var removeMenu = function()
		{
			if (menu)
			{
				jQuery( menu ).fadeOut( 200, function()
				{
					jQuery( this ).remove();
					menu = null;
				});
			}
		};

		menu.fadeIn( 200, function() {
			jQuery( document ).one( 'click', removeMenu );
		});
		menu.on( 'click', removeMenu );

		menu.find( 'a' ).each( function() {
			var a = jQuery( this );
			var t = a.prop( 'title' );
			a.removeAttr( 'title' );
			a.append( jQuery( '<label/>' ).append( t ) );
		});

		return false;
	}
	.bind( this ));
};


// cluster_control_widget.js

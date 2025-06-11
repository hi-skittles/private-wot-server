"use strict";

/* dependencies */

// uses jQuery
if (!window.jQuery) throw new Error( "jquery lib not loaded" );

// uses jQuery-dataTable plugin
if (!window.jQuery.fn.dataTable) throw new Error( "jquery-dataTable plugin lib not loaded" );

// uses Alert lib for notifications
if (!window.Alert) throw new Error( "alert lib not loaded" );


/**
*	Thin wrapper around the jQuery-dataTable plugin for implementing
*	ajax/json-driven HTML DOM tables.
*
*	Basic usage:
*
*		var myTableWidget = new DynamicTable( '.any-jquery-expression' )
*		var myTableWidget = new DynamicTable( 'body', options )
*		var myTableWidget = new DynamicTable( '#main', {
*			title: 'Spaces',
*			aoColumns: [
*				{ sTitle: 'col1 title', mData: 'col1_json_key'  }, // column 1
*				{ sTitle: 'col2 title', mData: 'col1_json_key'  }, // column 2
*				// etc...
*			]
*		);
*
*   See DynamicTable.DEFAULTS and http://www.datatables.net/ref for the full
*   list of available options.
*/
var DynamicTable = function( /*string or jquery*/ domTarget, /*Map*/ options )
{
	// permit simple subclassing
	if (arguments.length == 0)
	{
		return;
	}

	// deep merge default & user options
	var opts = this.options = jQuery.extend( true,
		{},
		DynamicTable.DEFAULTS,
		DynamicTable.DEFAULT_DATATABLE_OPTS,
		options
	);

	var dom = this.dom = {};

	// target dom table can be a string jquery selector expression or
	// a jquery object.
	if (typeof domTarget === 'string')
	{
		dom.table = jQuery( domTarget ).first();

		// sanity check that a dom element exists
		if (dom.table.length == 0)
		{
			throw new Error(
				"Target dom element identified by selector '" +
				domTarget +
				"' doesn't exist"
			);
		}
	}
	else
	{
		// assume it's a jquery expression; use only the first DOM element
		dom.table = domTarget.first();
	}

	// dataTables expects to be passed a jQuery( table ).
	if (dom.table.is('table'))
	{
		dom.container = dom.table.parent();
	}
	else
	{
		// else create one
		dom.container = dom.table;
		dom.table = jQuery('<table/>').appendTo( dom.container );
	}

	// construct and init datatable
	var table = this.datatable = this._createDataTable( dom.table );

	dom.tableHeader = dom.container.find( '.dynamic-table-header' ).first();
	dom.tableFooter = dom.container.find( '.dynamic-table-footer' ).last();

	var settings = jQuery( '<div class="user-settings"></div>' ).prependTo( dom.tableHeader );
	dom.tableHeader.prepend( '<h2>' + opts.title + '</h2>' );

	this._initEvents();
};


/** Class-specific options. */
DynamicTable.DEFAULTS =
{
	debug: 0,

	// Nominal table title
	title: '<!-- (no title) -->',

	// Interval between table data updates in msec
	pollInterval: 2500,

	// URL to data service
	baseurl: '?tg_format=json;'
};


/** DataTable-specific options. */
DynamicTable.DEFAULT_DATATABLE_OPTS =
{
	// dom config of injected table - see doco
	sDom: 'R<"dynamic-table-header"fr>t<"dynamic-table-footer"ip>',

	oLanguage:
	{
		// no text prefix on filter control
		sSearch: '',
	},

	// update from web console
	bServerSide: false,

	// object path to table data
	sAjaxDataProp: 'arrayOfRowsProperty',

	bDeferRender: true,

	iDisplayLength: 25, // 25 rows by default
	bPaginate: true,

	// bStateSave: true,

	// sScrollY: "500px",
	// bScrollCollapse: true,
	// bScrollInfinite: true,

	// show selector for number of rows to display
	// bLengthChange: true,

	// add 'row-id' attribute to new rows to facilitate DOM lookups.
	fnCreatedRow: function( tableRow, columnData, rowIndex )
	{
		var rowId = columnData.id;
		jQuery( tableRow ).attr( 'row-id', rowId );
	},
};


/** Constructs the DataTable instance that handles most of the actual DOM rendering. */
DynamicTable.prototype._createDataTable = function( jqueryTarget )
{
	var _this = this;
	var datatableOptions =
	{
		fnServerData: function( /*String*/ url
							, /*Array of Object*/ params
							, /*Function*/ modelUpdateCallback )
		{
			_this._datatableModelUpdate(
				/*DT settings Object*/ this, url, params, modelUpdateCallback );
		}
	};

	// deep merge options
	jQuery.extend( true, datatableOptions, this.options );

	// sanity check options, datatable falls in a heap without certain opts given
	if ( !(datatableOptions.aoColumns instanceof Array) ||
		 !datatableOptions.aoColumns.length )
	{
		console.warn( "No columns (option 'aoColumns') defined" );
	}

	if (this.options.debug)
	{
		console.log( "datatable options:" );
		console.dir( datatableOptions );
	}

	return jqueryTarget.dataTable( datatableOptions );
};


/** Called after construction to init widget-releated events. */
DynamicTable.prototype._initEvents = function()
{
	// add 'Filter' to search bar when not actively searching
	var filter = this.dom.container.find( 'input[type="text"]' );
	var clearFilter = jQuery( '<i class="icon-remove"></i>' );

	filter.on({
		focus: function()
		{
			if (this.value === 'Filter')
			{
				this.value = '';
				this.style.color = '#444';
			}
		},
		blur: function()
		{
			if (this.value === '')
			{
				this.value = 'Filter';
				this.style.color = '#ccc';
				clearFilter.hide();
			}
		},
		keypress: function()
		{
			if (this.value === '')
			{
				clearFilter.hide();
			}
			else
			{
				clearFilter.show();
			}
		}
	}).prop( 'value', 'Filter' ).css( 'color', '#ccc' );

	clearFilter.appendTo( '.dataTables_filter label');

	clearFilter.on({
		click: function()
		{
			filter.prop( 'value', '' );
			jQuery( this ).hide();
			filter.trigger( 'keyup' );
			filter.blur();
		},
	});

	// use of hidden column in 'aoColumns' causes datatables to set a
	// fixed width through the table's "style" attr, so attempt to remove it
	// just in case so that table will self-resize and page-specific CSS
	// can be used.
	this.dom.table.removeAttr( 'style' );

	jQuery( this ).triggerHandler( 'initialised.dt' );

	jQuery( '.dynamic-table-header' ).append( '<a id="pause_updates_btn" ' +
		'href="javascript:void(0)" title="Pause/Resume Live Updates"' +
		'class="button live-update-button depressed">' +
		'<img src="/static/images/throbber_16.gif"/></a>' );
	
	var page = this;
	jQuery( '#pause_updates_btn' ).on( 'click', function ()
	{
		if (!page._isConnected)
		{
			page.connectModel();
		}
		else
		{
			page.disconnectModel();
		}
		page.updatePauseUpdatesButtonConnectionStatus();
	});
};


DynamicTable.prototype.updatePauseUpdatesButtonConnectionStatus = function()
{
	var pauseUpdatesButton = jQuery( '#pause_updates_btn' );
	if (this._isConnected)
	{
		pauseUpdatesButton.addClass( 'depressed' );
		jQuery( 'img', pauseUpdatesButton ).attr( 'src', 
			'/static/images/throbber_16.gif' );
	}
	else
	{
		jQuery( pauseUpdatesButton ).removeClass( 'depressed' );
		jQuery( 'img', pauseUpdatesButton ).attr( 'src', 
			'/static/images/throbber_16_o.gif' );
	}
}


/** Update model and redraw table. */
DynamicTable.prototype.requestModelUpdate = function()
{
	if (this.options.bServerSide)
	{
		this.datatable.fnDraw( false );
	}
	else
	{
		this.datatable.fnReloadAjax();
	}
};


/** Begin polling */
DynamicTable.prototype.connectModel = function()
{
	if (this._isConnected)
	{
		console.warn( "dynamic table model already connected, ignoring..." );
		return;
	}

	return this._isConnected = setInterval(
		this.requestModelUpdate.bind( this ), this.options.pollInterval );
};


/** Stop polling */
DynamicTable.prototype.disconnectModel = function()
{
	if (!this._isConnected)
	{
		console.warn( "dynamic table model not connected, ignoring..." );
		return;
	}

	clearInterval( this._isConnected );
	this._isConnected = false;
};


/**
*   Called by jquery-dataTable plugin in response to UI events.
*   See: http://www.datatables.net/usage/server-side
*/
DynamicTable.prototype._datatableModelUpdate =
function( /*Object*/ datatableSettings
		, /*string*/ url
		, /*Array of Object*/ datatableParams
		, /*Function*/ datatableCallback )
{
	// ignore url that datatable passes; we'll build it ourselves
	url = this.getModelUpdateUrl( datatableParams );

	datatableSettings.jqXHR = jQuery.ajax({
		"dataType": 'json',
		"type": "GET",
		"url": url,
		"success": function( data )
		{
			this._lastPollFailed = false;
			Alert.dismiss( 'web-console-is-down' );

			// intercept ajax callback to inject web console notifications

			if (data.error)
			{
				console.warn( "web console error: %s", data.error );
				new Alert.Error( data.error, { id: true } );
			}

			if (data.warning)
			{
				console.warn( "web console warning: %s", data.warning );
				new Alert.Warning( data.warning, { id: true } );
			}

			if (data.info)
			{
				console.log( "web console info: %s", data.info );
				new Alert.Info( data.info, { id: true } );
			}

			if (data.iTotalRecords === undefined)
			{
				var colProperty = this.options.sAjaxDataProp
				if (data[colProperty] && data[colProperty].length !== undefined)
				{
					if (this.options.debug > 1)
					{
						console.log( "iTotalRecords not given; setting to #rows in resultset" );
					}
					data.iTotalRecords = data[colProperty].length;
				}
				else
				{
					console.error( "Couldn't determine #records from property '%s' of data:", colProperty );
					console.dir( data );
				}
			}

			if (data.iTotalDisplayRecords === undefined)
			{
				if (this.options.debug > 1)
				{
					console.log(
						"iTotalDisplayRecords not given; setting to iTotalRecords (%s)",
						data.iTotalRecords
					);
				}
				data.iTotalDisplayRecords = data.iTotalRecords;
			}

			this._updateDatatable = datatableCallback;
			this.updateModel( data );
		}
		.bind( this ),

		error: function( jqXHR, textStatus, errorThrown )
		{
			if (this._lastPollFailed)
			{
				console.warn( "AJAX call failed (%s): %s", textStatus, url );
				new Alert.Error(
					"Web Console appears to be down",
					{ id: "web-console-is-down", dismissable: false }
				);
			}
			this._lastPollFailed = true;
		}
		.bind( this ),
	});
};


/** Update table data. This implictly redraws the table with the new data. */
DynamicTable.prototype.updateModel = function( /*Object*/ data )
{
	this.data = data;

	// _updateDatatable is a callback passed by Datatables to update
	// and redraw table. If not set, then requestModelUpdate has probably
	// never been called.
	if (!this._updateDatatable)
	{
		throw new Error( "Direct model updates not currently supported" );
	}
	this._updateDatatable( data );
	jQuery( this ).triggerHandler( 'updateModel.dt', [ data ] );
};


/** See http://www.datatables.net/usage/server-side for explanation of params. */
DynamicTable.prototype.getModelUpdateUrl = function( /*Array of Object*/ datatableParams )
{
	// collapse array of singleton name=value objects into single object
	var params = {};
	for (var i in datatableParams)
	{
		var param = datatableParams[ i ];
		params[ param.name ] = param.value;
	}

	// by default, datatables passes far more params than it really needs.
	// below are the params we actually need to form request url;
	// key = datatables param name, value = param name we will use.
	var requiredParams = {
		iDisplayStart: 'index',
		iDisplayLength: 'limit',
		iSortCol_0: 'sortby',
		sSortDir_0: 'sortdir',
		sSearch: 'query',
		sEcho: '_'
	};

	// discard params we dont need/use
	var paramTuples = [];
	var columnDefs = this.options.aoColumns;

	for (var paramName in params)
	{
		if (!requiredParams[ paramName ])
		{
			continue;
		}

		params[ paramName ] = params[ paramName ];

		// request sortby param by name not column index
		if (paramName == 'iSortCol_0')
		{
			paramTuples.push( requiredParams[ paramName ] + "=" + columnDefs[ params[ paramName ] ].mData );
			continue;
		}

		paramTuples.push( requiredParams[ paramName ] + "=" + params[ paramName ] );
	}

	var url = this.options.baseurl + paramTuples.join( ';' );

	return url;
};


/* dynamic_table.js */

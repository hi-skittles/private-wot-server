PageManager = function ()
{
	bindMethods( this );
	this.__init__();
};


PageManager.prototype.__init__ = function ()
{
	this.filters = [];
	// Filter has been run at least once
	this.isFilterTested = false;

	this.procField = getElement( "process_filter" );
	this.pathField = getElement( "path" );

	this.fetchButton = getElement( "fetch" );
	this.asCSVButton = getElement( "as_csv" );
	this.saveButton =  getElement( "save_as" );
	this.delButton =   getElement( "delete" );

	this.filterList = getElement( "saved_filter_list" );

	this.outputPane = getElement( "output_pane" );

	this.descriptionField = getElement( "description_text" );

	this.attachEvents();
	this.loadFiltersFromDB();
};


PageManager.prototype.fetch = function ()
{
	this.procField.value = this.procField.value.trim();
	this.pathField.value = this.pathField.value.trim();
	var processes = this.procField.value;
	var path = this.pathField.value;

	var d = loadJSONDoc( "get_filtered_tree?" +
			"processes=" + encodeURIComponent( processes ) +
			"&path=" + encodeURIComponent( path ) );
	d.addCallbacks( this.showResult, this.onFetchFailure );

	this.disableForm();

	return;
};


PageManager.prototype.displayError = function ( msg )
{
	MochiKit.DOM.replaceChildNodes( this.outputPane, null );
	alert( msg );
}


PageManager.prototype.showResult = function ( res )
{
	if (!res.status)
	{
		this.displayError( res.errorMsg );
		this.enableForm();
		return;
	}

	var tree = res.tree;
	var values = tree.values;
	var subPaths = tree.subPaths;
	subPaths.unshift( "app" );

	var commonKeys = findCommonKeys( values, subPaths.length - 1 );

	if (commonKeys == undefined)
	{
		var tables = createTables( "", values, subPaths );
	}
	else
	{
		// All the sub-tables have the same keys so make it unified.

		var processes = keys( values );

		// If only one process, don't make a column for it.
		if (processes.length == 1)
		{
			subPaths.shift();
			var label = processes[0];
			var tables = createUnifiedTable( values[label], subPaths, commonKeys, label );
		}
		else
		{
			var tables = createUnifiedTable( values, subPaths, commonKeys, "Results" );
		}
	}

	MochiKit.DOM.replaceChildNodes( this.outputPane, tables );
	Table.init();

	// Now the filter has been tested, we can modify the button state.
	this.isFilterTested = true;
	this.enableForm();
};


PageManager.prototype.onFetchFailure = function ( res )
{
	alert( "Server error: Unable to fetch filter." );

	this.enableForm();
};


// ---- Output functions ----

function getFirst( obj )
{
	for (var x in obj)
	{
		return obj[x];
	}
};


function createTitleRow( titleKeys, prefixes )
{
	if (prefixes != undefined)
	{
		var pathBase = function( path )
			{
				return path.slice( path.lastIndexOf( '/' ) + 1 );
			}

		var newPrefixes = map( pathBase, prefixes );
		var labels = newPrefixes.concat( titleKeys );
	}
	else
	{
		var labels = titleKeys;
	}

	var data = map( partial( TD, {'class':'colheader'} ), labels );
	return TR( {'class' : 'sortrow'}, data );
};


function createRow( row, titleKeys, labels )
{
// from pycommon/watcher_constants.py
// TYPE_UNKNOWN    = 0
// TYPE_INT        = 1
// TYPE_UINT       = 2
// TYPE_FLOAT      = 3
// TYPE_BOOL       = 4
// TYPE_STRING     = 5
// TYPE_TUPLE      = 6
// TYPE_TYPE       = 7

	var result = [];

	if (labels != undefined)
	{
		result = map( partial( TD, null ), labels );
	}

	for (var key in titleKeys)
	{
		var value = row[ titleKeys[ key ] ][ 0 ];

		if (value == 3.4028234663852886e+38)
		{
			value = "FLT_MAX";
		}
		else if (value == "<DIR>")
		{
			value = "dir";
		}

		result.push( TD( null, value ) );
	};

	return TR( null, result );
}


function createRows( rows, titleKeys )
{
	var result = [];
	var keysArray = keys( rows ).sort();

	for (var i in keysArray)
	{
		var key = keysArray[i];
		result.push( createRow( rows[ key ], titleKeys, [key] ) );
	};

	return result;
};


function createTitleKeys( tree )
{
	return keys( tree ).sort();
}


function createTable2D( label, tree, prefix )
{
	var titleKeys = createTitleKeys( getFirst( tree ) );

	var newTable = TABLE( {'class': 'sortable', 'id': 'temp'},
		TBODY( null,
			TH( {'class' : 'heading', 'colspan' : "100"}, label ),
			createTitleRow( titleKeys, [prefix] ),
			createRows( tree, titleKeys ) ));

	return newTable;
}


// Checks whether all child Objects have the same keys.
function is2DTable( tree )
{
	var getSubKeys = function ( item )
	{
		return keys( item[1] );
	};

	var result = map( getSubKeys, items( tree ) );

	for (var x in result)
	{
		if (!arrayEqual( result[0], result[x] ))
		{
			return false;
		}
	}

	return true;
}


function createTable1D( label, tree )
{
	var titleKeys = createTitleKeys( tree );
	var newTable = TABLE( {'class': 'sortable', 'id': 'temp'},
		TBODY( null,
			TH( {'class' : 'heading', 'colspan' : "100"}, label ),
			createTitleRow( titleKeys ),
			createRow( tree, titleKeys ) ) );

	return newTable;
}


function createTables( label, tree, subPaths )
{
	var depth = subPaths.length - 1;

	if (depth == 1)
	{
		return createTable1D( label, tree );
	}
	else if (depth == 2)
	{
		if (is2DTable( tree ))
		{
			return createTable2D( label, tree, subPaths[0] );
		}
	}

	if (label != "")
	{
		label += "/";
	}

	var tables = [];
	var tailPaths = subPaths.slice( 1 );

	for (var key in tree)
	{
		tables.push( createTables( label + key, tree[key], tailPaths ) );
		tables.push( BR() );
	}
	return tables;
}


function createUnifiedRows( tree, titleKeys, depth, path )
{
	if (depth == 1)
	{
		return [createRow( tree, titleKeys, path )];
	}

	var rows = [];

	var childKeys = keys( tree );
	childKeys.sort();

	for (var i in childKeys)
	{
		var key = childKeys[i];
		rows = rows.concat(
				createUnifiedRows( tree[ key ],
					titleKeys, depth - 1, path.concat([key]) ) );
	}

	return rows;
}


// Creates one table instead of multiple tables with the same columns
function createUnifiedTable( tree, subPaths, titleKeys, label )
{
	var depth = subPaths.length - 1;

	var newTable = TABLE( {'class': 'sortable', 'id': 'temp'},
		TBODY( null,
			TH( {'class' : 'heading', 'colspan' : "100"}, label ),
			createTitleRow( titleKeys, subPaths.slice( 0, -2 ) ),
			createUnifiedRows( tree, titleKeys, depth, [] ) ) );

	return newTable;
}


// Returns the column keys if all tables have the same, otherwise undefined.
function findCommonKeys( tree, depth )
{
	if (depth < 2)
	{
		return undefined;
	}
	else if (depth == 2)
	{
		if (is2DTable( tree ))
		{
			return createTitleKeys( getFirst( tree ) );
		}
		else
		{
			return undefined;
		}
	}

	var commonKeys = undefined;

	for (var key in tree)
	{
		var newKeys = findCommonKeys( tree[key], depth - 1 );

		if (newKeys == undefined)
		{
			return undefined;
		}

		if (commonKeys == undefined)
		{
			commonKeys = newKeys;
		}
		else if (!MochiKit.Base.arrayEqual( commonKeys, newKeys ))
		{
			return undefined;
		}
	}

	return commonKeys;
};


// ---- Input functions ----


PageManager.prototype.onDeleteSuccess = function ( res )
{
	if (!res.status)
	{
		alert( res.message );
		return;
	}

	// If the delete was successful, update the page
	this.loadFiltersFromDB();
};


PageManager.prototype.onDeleteFailure = function ( res )
{
	MochiKit.Logging.log( "onDeleteFailure" );
};


PageManager.prototype.deleteFilter = function ( srcEvent )
{
	// Note: currently only deleting filters by name. The deletion assumes
	// that the filter is owned by the current user session. It might be
	// better to switch this to a DB id for tracking.
	selectedItem = this.getSelectedItem();
	filter = this.filters[ selectedItem.value ];
	name = filter.name;

	if (!window.confirm( "About to delete filter '" + name + "'." ))
	{
		MochiKit.Logging.log( "Delete filter operation cancelled." );
		return;
	}

	var d = loadJSONDoc( "delete_filter?name=" + encodeURIComponent( name ) );
	d.addCallbacks( this.onDeleteSuccess, this.onDeleteFailure );
};


PageManager.prototype.onSaveSuccess = function ( res )
{
	// If the save failed, tell the user why
	if (!res.status)
	{
		alert( res.message );
		return;
	}

	// If the save was successful, update the page
	this.loadFiltersFromDB();
};


PageManager.prototype.onSaveFailure = function ( res )
{
	MochiKit.Logging.log( "onSaveFailure" );

};


PageManager.prototype.saveFilter = function ()
{
	var name = window.prompt( "Save filter as...", "Custom filter name" );

	if (name == undefined)
	{
		MochiKit.Logging.log( "Save filter operation cancelled." );
		return;
	}

	var processes = this.procField.value;
	var path = this.pathField.value;

	var d = loadJSONDoc( "save_new_filter?" +
			"name=" + encodeURIComponent( name ) + "&" +
			"processes=" + encodeURIComponent( processes ) + "&" +
			"path=" + encodeURIComponent( path ) );
	d.addCallbacks( this.onSaveSuccess, this.onSaveFailure );
};


function stripFilename( str )
{
	return str.replace( / /g, '_' ).replace( /:/g, '' ).replace( /\(/g, '' ).replace( /\)/g, '' );
}


PageManager.prototype.asCSV = function ()
{
	var processes = this.procField.value;
	var path = this.pathField.value;

	var filename = stripFilename( this.getSelectedItem().text ) + '_' +
			stripFilename( toISOTimestamp( new Date() ) ).replace( /-/g, '' ) + ".csv";

	document.location = "/watchers/filtered/csv?" +
		"processes=" + encodeURIComponent( processes ) +
		"&path=" + encodeURIComponent( path ) +
		"&filename=" + encodeURIComponent( filename );
};


PageManager.prototype.disableForm = function ()
{
	this.fetchButton.disabled = true;
	this.asCSVButton.disabled = true;
	this.saveButton.disabled = true;
	this.delButton.disabled = true;

	this.procField.disabled = true;
	this.pathField.disabled = true;

	this.filterList.disabled = true;
};


PageManager.prototype.enableForm = function ()
{
	this.procField.disabled = false;
	this.pathField.disabled = false;

	this.filterList.disabled = false;

	this.updateButtonState();
};


PageManager.prototype.updateButtonState = function ()
{
	this.fetchButton.disabled = !this.isRunnable();
	this.asCSVButton.disabled = !this.isRunnable();
	this.saveButton.disabled = !this.isSaveable();
	this.delButton.disabled = !this.isDeleteable();
};


PageManager.prototype.isRunnable = function ()
{
	return ((this.procField.value.trim().length > 0) &&
			(this.pathField.value.trim().length > 0));
};


PageManager.prototype.isSaveable = function ()
{
	// has been run once
	return this.isFilterTested;
};


PageManager.prototype.isDeleteable = function ()
{
	// Note: getAttribute returns a string, not the original bool we stored
	return (this.getSelectedItem().getAttribute( "deletable" ) == "true");
};


PageManager.prototype.getSelectedItem = function ()
{
	// We can only delete the custom user filters.
	return list( ifilter( itemgetter('selected'), this.filterList.options ) )[0];
};


PageManager.prototype.onTextModified = function ( srcEvent )
{
	if (srcEvent.target().lastValue != undefined)
	{
		if (srcEvent.target().lastValue != srcEvent.target().value)
		{
			this.isFilterTested = false;
		}
	}
	srcEvent.target().lastValue = srcEvent.target().value;

	this.updateButtonState();
};


PageManager.prototype.onFilterChange = function ( srcEvent )
{
	var listOption = srcEvent.target().value;
	if (listOption > (this.filters.length - 1))
	{
		// TODO: Error out, there is no such item to be selected
		MochiKit.Logging.log( "onFilterChange: Invalid selection attempted, " +
								listOption );
		return;
	}

	var shouldPopulateFields = true;

	if (listOption == -1)
	{
		if (this.hasNewBeenClicked == undefined)
		{
			this.hasNewBeenClicked = true;
			shouldPopulateFields = false;
		}

		// Create empty fields
		var filter = { "processes" : "", "path" : "", "description" : "" };

		// Set the state for the buttons
		this.isFilterTested = false;

		MochiKit.DOM.replaceChildNodes( this.outputPane, null );
	}
	else
	{
		var filter = this.filters[ listOption ];

		// Set the state for the buttons
		this.isFilterTested = true;
	}

	if (shouldPopulateFields)
	{
		// Fill in the saved filter pane now
		this.procField.value = filter.processes;
		this.pathField.value = filter.path;
		var descText = filter.description;
		if (descText == undefined)
		{
			descText = filter.name;
		}

		this.descriptionField.innerHTML = descText;
	}

	// Finally set the buttons to their initial state
	this.updateButtonState();

	if (this.isRunnable())
	{
		this.fetch();
	}
};


PageManager.prototype.onDBFetchSuccess = function ( res )
{
	var filters = [];

	// Special entry that enables a new filter to be created
	newFilterOption = OPTION( { "value": "-1",
									"class": "primary_option_special",
									"selected": true },
								"(new)");
	filters.push( newFilterOption );

	// Special heading
	if (res.userFilters.length > 0)
	{
		headingOption = OPTION( { "value": "-2",
									"class": "primary_option_title",
									"disabled": true},
								"Pre-Configured");
		filters.push( headingOption );
	}

	var globalCounter = 0;
	// Add the filters available to all users
	for (var i in res.globalFilters)
	{
		dbEntry = res.globalFilters[ i ];
		this.filters[ globalCounter ] = dbEntry;

		filters.push( OPTION( { "value": globalCounter,
									"class": "primary_option" },
							dbEntry.name) );
		globalCounter++;
	}


	// Special heading
	if (res.userFilters.length > 0)
	{
		headingOption = OPTION( { "value": "-2",
										"class": "primary_option_title",
										"disabled": true},
									"User Filters");
		filters.push( headingOption );

		// Add the custom user filters
		for (var i in res.userFilters)
		{
			dbEntry = res.userFilters[ i ];
			this.filters[ globalCounter ] = dbEntry;

			userOption = OPTION( { "value": globalCounter,
									"class": "primary_option"},
								dbEntry.name );

			// Note: <elem>.setAttribute() apparently doesn't play well with IE.
			userOption.setAttribute( "deletable", true );
			filters.push( userOption );
			globalCounter++;
		}
	}


	MochiKit.DOM.replaceChildNodes( this.filterList, filters );

	// triggers a fake DOM event for the above handler
	var fakeEvent = { target:newFilterOption };
	MochiKit.Signal.signal( this.filterList, "onchange", fakeEvent );

	// Set the focus onto the list now so highlighting looks correct.
	this.filterList.focus();
};


PageManager.prototype.onDBFetchFailure = function ( res )
{
	MochiKit.Logging.log( "onDBFetchFailure" );

	// create the 'new' entry ? or just barf and display an error

};


PageManager.prototype.loadFiltersFromDB = function ()
{
	var d = loadJSONDoc( "get_saved_filters" );
	d.addCallbacks( this.onDBFetchSuccess, this.onDBFetchFailure );
};


PageManager.prototype.attachEvents = function ()
{
	// Text input events
	MochiKit.Signal.connect( this.procField, "onkeyup", this.onTextModified );
	MochiKit.Signal.connect( this.pathField, "onkeyup", this.onTextModified );


	// Button events
	MochiKit.DOM.updateNodeAttributes( this.fetchButton, { "onclick": this.fetch } );
	MochiKit.DOM.updateNodeAttributes( this.asCSVButton, { "onclick": this.asCSV } );
	MochiKit.DOM.updateNodeAttributes( this.saveButton, { "onclick": this.saveFilter } );
	MochiKit.DOM.updateNodeAttributes( this.delButton, { "onclick": this.deleteFilter } );

	MochiKit.Signal.connect( this.filterList, "onchange", this.onFilterChange );
};


function onFilteredLoad()
{
	var mgr = new PageManager();
}


addLoadEvent( onFilteredLoad );

// filtered.js

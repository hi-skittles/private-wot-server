/**
 * RunScript javascript file.
 *
 * This file contains the js code for WebConsole's RunScripts page.
 * Also see argtypes.js
 *
 * THINGS TO KNOW:
 * 
 * Scripts are organised in the following hierarchy:
 * - Type: The source of the scripts  
 *    - Category: Each source is composed of multiple categories
 *       - Script: Every script belongs to one category.
 *
 * At the moment, the only "Types" are "db" and "watcher".
 *
 * TODO: If we aren't going to continue using database-stored scripts and instead
 *       rely only on watcher scripts, we can remove the use of "type" from the
 *       hierarchy.
 *
 * In this JavaScript file, every script has an ID associated with it which
 * gives WebConsole enough information to execute the script on the BigWorld 
 * server.
 *
 * For watcher scripts, this id takes the form:
 * watcher:<procType>:<runType>:<watcherPath>
 * e.g. "watcher:cellapp:all:command/addGuards"
 *
 * For db scripts, this id takes the form:
 * db:<dbId>
 * e.g. "db:4"
 *
 * For database scripts, all information about the script is pulled from
 * the WebConsole database, hence only the ID is needed. Whereas, the
 * Watcher exposed functions need extra information in order to be called,
 * which is why it goes in the ID string.
 */

var RunScript = {
	/*------------------------------------------
	 * Variables
	 *------------------------------------------*/
	
	// Position variables to store pixel offsets of certain HTML elements
	outputPanePos: 0,
	scriptListPos: 0,

	// Associative array of (script id string)->(script object)
	scripts: {},

	// Associative array of (category name string)->(list of script id strings)
	categories: {},

	// The currently selected RunScript source. Possible options are: "db" and "watcher".
	selectedType: null,

	// A string containing the currently selected category 
	// (from the category dropdown box)
	selectedCategory: null,

	// The string ID of the currently selected scripts,
	selectedScriptID: null,

	// The relative URLs which we call on WebConsole.
	executeURL: 'executescript',
	infoURL: 'scriptinfo',
	scriptsURL: 'getscripts',

	/*------------------------------------------
	 * Functions
	 *------------------------------------------*/
	/**
	 * Initial setup function on page load.
	 */
	init: function()
	{
		MochiKit.Signal.connect( window, 'onresize', RunScript, 
			'resizeContent' );
		
		MochiKit.Signal.connect( "scriptSelect", "onchange", RunScript,
			"onSelectScript" );

		this.resizeContent();
	},

	/**
	 * Execute a script, given a script id and arguments
	 *
	 * @param id      The script ID to run.
	 * @param args    The list of argument strings entered in the input fields.
	 * @param runType The method of running the scripts. Possible values are:
	 *                "all", "any" or a comma delimited string of ids.
	 *                (in reality the possible value could be any string, it's
	 *                up to the WebConsole side to handle this).
	 */
	executeScript: function( id, args, runType )
	{
		var script = this.scripts[id];
		var argList = [];
		for (var i = 0; i < args.length; i++)
		{
			argList.push( [args[i], script.args[i][1]] );
		}
		var query = MochiKit.Base.queryString(
			{ "id": script.id,
				"args": MochiKit.Base.serializeJSON( argList ),
				"runType": runType
			} ); 
		var url = this.executeURL + "?" + query;
		d = MochiKit.Async.loadJSONDoc( url )
		d.addCallback( MochiKit.Base.method( this, this.printResponse ) );
		this.clearResultPane();
		this.clearOutputPane();
		this.showExecuting();
	},

	/**
	 * Takes the "response" object returned from making the "executescript" 
	 * remote call and process it for displaying in our div output boxes.
	 *
	 * If the response object has any errors, then response.errors will be an
	 * array containing one or more string items. The presence of any items
	 * in this array is used to determine whether executing a script succeeded 
	 * or not.
	 *
	 * @param responseDict    The response object directly converted from the
	 *                        RunScriptOutput object on the WebConsole server 
	 *                        side.
	 */
	printResponse: function( responseDict )
	{
		var response = responseDict.output;
		if (response.errors.length > 0)
		{
			this.printResultFailed();
			this.printErrors( response.errors );
		}
		else
		{
			this.printResult( response.result );
		}
		
		this.printOutput( response.output );
	},

	/**
	 * Initialise the our list of categories with a one-level tree of 
	 * categories. 
	 *
	 * We want to know about these categories from the start
	 * of loading the webpage, so that the categories dropdown box
	 * can be immediately populated for the user to get started.
	 *
	 * This function is called from "runscript.kid", and is run while the 
	 * HTML page is loading.
	 *
	 * @param categories A dictionary of:
	 *                   RunScript type string->list of category names
	 *                   e.g. { "db": ["report","admin", "test"], 
	 *                          "watcher": ["report", "entityManipulation"] }
	 *
	 * See comments at the top of this file for info on runscript "Types".
	 */
	initCategories: function( categories )
	{
		for (var type in categories)
		{
			this.categories[type] = {};
			
			for (var i = 0; i < categories[type].length; i++)
			{
				var category = categories[type][i];
				this.categories[type][category] = null;
			}
		}
	},


	/**
	 * Given a script ID, populate the "scriptParamPane" and "executePane"
	 * with fields
	 * for the user to enter arguments and select other options relating
	 * to running that script.
	 *
	 * To do this, we need the details of script arguments and the script 
	 * description for the specified script. If we don't have this info,
	 * then make a remote query to the server to get it.
	 *
	 * Otherwise, move straight on to populating the page with the script 
	 * details.
	 *
	 * @param scriptID       The ID of the script for we want to display 
	 *                       information. See comments at top of file for
	 *                       information on string IDs.
	 */
	retrieveScriptInfo: function( scriptID )
	{
		var script = this.scripts[scriptID];
		if (script.hasInfo)
		{
			if (this.selectedScriptID == scriptID)
			{
				this.setScriptInfo( scriptID );
			}
			return;
		}
		//this.printMsg( "DEBUG", "Retrieving info for '" + script.title + ".." );
		var query = MochiKit.Base.queryString( { "id": script.id } ); 
		var url = this.infoURL + "?" + query;
		d = MochiKit.Async.loadJSONDoc( url )
		d.addCallback( MochiKit.Base.method( this, this.receiveScriptInfo, scriptID ) );
		d.addErrback( MochiKit.Base.method( this, this.printAJAXError ) );
		this.setScriptLoading( scriptID );
	},

	/**
	 * Callback function for when we receive script information from the 
	 * server. We save the info to the script object's attributes and then
	 * call the method to populate the web page elements with the script's
	 * information.
	 *
	 * The initiating remote server call is made in the above function 
	 * "retrieveScriptInfo".
	 *
	 * @param scriptID    The ID string of the script we're receiving info for
	 * @param scriptInfo  The data object returned from the webserver 
	 *                    containing information about this script.
	 */
	receiveScriptInfo: function( scriptID, scriptInfo )
	{
		var script = this.scripts[scriptID];
		script.hasInfo = true;
		script.args = scriptInfo.args;
		script.procType = scriptInfo.procType;
		script.runType = scriptInfo.runType;
		script.desc = scriptInfo.desc;
		if (this.selectedScriptID == scriptID)
		{
			this.setScriptInfo( scriptID );
		}
	},

	/**
	 * Switch what "type" of scripts to allow the user to use 
	 * (i.e. "watcher" or "db" scripts). See comment at top of the file
	 * for more information on "type".
	 *
	 * Also used for switching the "category" of scripts too.
	 *
	 * Possiblys involve making a remote server call to get the list of scripts
	 * which belongs to a category, if we haven't already retrieved this list 
	 * previously.
	 *
	 * @param type      The "type" of scripts we want to use
	 * @param category  The "category" of scripts we want to use 
	 *                  (null for no category)
	 */
	switchCategory: function( type, category )
	{
		this.setScriptInfo( null );
		this.populateScriptArgs( null );

		if (type != this.selectedType)
		{
			this.selectedType = type;
		}

		this.selectedCategory = category;

		if ((category != null) && (this.categories[type][category] == null))
		{
			// Make AJAX call...
			var query = MochiKit.Base.queryString( { "type": type,
				"category": category } );
			var url = this.scriptsURL + "?" + query;
			//logDebug( "URL: ", url );
			d = MochiKit.Async.loadJSONDoc( url );
			d.addCallback( MochiKit.Base.method( this, this.receiveScripts, 
				type, category ) );
		}
		else
		{
			this.populateScripts();
		}
	},


	/**
	 * Receive a list of scripts from the server belonging to a certain
	 * category.
	 *
	 * @param type     The "Type" to which the list of scripts belongs.
	 * @param category The category (within the type) to which the list of 
	 *                 scripts corresponds.
	 * @param response The actual server response object, converted from JSON 
	 *                 encoded string. We only need the "scripts" attribute 
	 *                 out of this object.
	 */
	receiveScripts: function( type, category, response )
	{
		//this.scripts[type][category] = response.scripts;

		// TODO: Clear existing list
		this.categories[type][category] = [];

		for (var i=0; i < response.scripts.length; i++)
		{
			var scriptInfo = response.scripts[i];
			
			this.scripts[scriptInfo.id] = scriptInfo;
			this.categories[type][category].push( scriptInfo.id );
		}

		this.populateScripts();
	},

	/**
	 * Event handler for when the user selects a script from the dropdown box.
	 */
	onSelectScript: function( event )
	{

		var scriptID = event.target().value;

		if (scriptID == "__info__")
		{
			return;
		}

		this.selectScript( scriptID );
	},

	/**
	 * Make the specified script the current one with which
	 * the user can enter argument values and execute.
	 *
	 * @param id The ID string of the script. See comments at top of file for
	 *           what an ID string looks like.
	 */
	selectScript: function( id )
	{
		if (this.selectedScriptID == id)
		{
			return;
		}

		this.selectedScriptID = id;
		this.retrieveScriptInfo( id );
	},
	
	/*------------------------------------------
	 * DOM manipulation functions
	 *------------------------------------------*/
	/**
	 * Clear all text from the output pane
	 */
	clearOutputPane: function()
	{
		var outputPane = $("outputPane");
		while (outputPane.hasChildNodes())
		{
			outputPane.removeChild( outputPane.firstChild );
		}
	},

	/**
	 * Clear all text from the result pane
	 */
	clearResultPane: function()
	{
		var resultPane = $("resultPane");
		while (resultPane.hasChildNodes())
		{
			resultPane.removeChild( resultPane.firstChild );
		}
	},

	/**
	 * Show on the page that we're currently executing a script.
	 *
	 * TODO: Replace with displaying a spinny graphic thing?
	 */
	showExecuting: function()
	{
		var script = this.scripts[this.selectedScriptID];

		MochiKit.DOM.appendChildNodes( "resultPane", "Executing script " + script.title + "..." );
	},

	/**
	 * Display any AJAX errors in the output pane.
	 *
	 * @param e    AJAX error object
	 */
	printAJAXError: function( e )
	{
		this.printErrors( [e] );
	},

	/**
	 * Display any Runscript output errors in the output pane.
	 *
	 * @param errors    A list of error strings
	 */
	printErrors: function( errors )
	{
		if (errors == null || errors.length == 0)
		{
			return;
		}
		else
		{
			for (var i = 0; i < errors.length; i++)
			{
				output = SPAN( {"class": "error"}, errors[i] );
				MochiKit.DOM.appendChildNodes( "outputPane", output, BR() );
			}
		}
	},

	/**
	 * Display output in the output pane.
	 *
	 * @param output    A list of output strings
	 */
	printOutput: function( output )
	{
		if (output == null || output.length == 0)
		{
			/*MochiKit.DOM.appendChildNodes( this.outputPane, SPAN( {},
				"Function did not print any output", BR()) );*/
			return;
		}
		else
		{
			for (var i = 0; i < output.length; i++)
			{
				var line = SPAN( {}, output[i] );
				MochiKit.DOM.appendChildNodes( "outputPane", line, BR() );
			}
		}
	},

	/**
	 * Display return value of executing script in the result pane.
	 *
	 * If there was no return value (i.e. result is null) then display
	 * that the function executed successfully.
	 *
	 * @param result	A string indicating the value of the result
	 */
	printResult: function( result )
	{
		this.clearResultPane();

		if (result == null || result.length == 0)
		{
			return;
		}
		else
		{
			for (var i = 0; i < result.length; i++)
			{
				var line = SPAN( {}, result[i] );
				MochiKit.DOM.appendChildNodes( "resultPane", line, BR() );
			}
		}

	},

	/**
	 * If we failed to executing the script on the server, indicated 
	 * by a "fail" status when receiving the Watcher response, then
	 * we print that here.
	 */
	printResultFailed: function( )
	{
		this.clearResultPane();
		MochiKit.DOM.appendChildNodes( "resultPane",
			SPAN( { "class": "fail" }, 
			"Function failed to execute") );
	},

	/**
	 * Resize content to fit viewing area size.
	 *
	 * TODO: Better resizing method. This method will have to be 
	 *       reimplemented when the final web page interface layout 
	 *       and the placement of elements is finalised.
	 */
	resizeContent: function()
	{
		var margin = 30;

		var vpDim = MochiKit.DOM.getViewportDimensions();
		var opPos = MochiKit.DOM.elementPosition( "outputPane" );

		MochiKit.DOM.setElementDimensions( "outputPane", 
			{"h": vpDim.h - opPos.y - margin} );
	},



	/**
	 * Populate the script dropdown box with the list of scripts belonging
	 * to the currently selected category.
	 *
	 * NOTE: Currently selected category is stored in the variable 
	 *       "selectedCategory". We also use "selectedType" to know which
	 *       type to pull the category from.
	 */
	populateScripts: function( )
	{
		var scriptElems = [];
		var scriptCount = 0;
		for (var category in this.categories[this.selectedType])
		{
			var scriptIDList = this.categories[this.selectedType][category];
			// TODO: address subdirectories / recursive categories
			if (scriptIDList != null)
			{
				for (var i=0; i < scriptIDList.length; i++)
				{
					var scriptID = scriptIDList[i];
					var script = this.scripts[scriptID];
					script.prettyTitle = script.title.toUpperCase()[0] +
									script.title.substring(1).replace(  /([A-Z])/g, " $1" );


					var newTitle = script.title.toUpperCase()[0] +
									script.title.substring(1).replace(  /([A-Z])/g, " $1" );

					//scriptElems.push( OPTION({value:scriptID}, script.title) );
					scriptElems.push( OPTION( { "value": scriptID,
							"class": "primary_option"},
						script.prettyTitle) );
					scriptCount++;
				}
			}

		}

		// If we didn't find any scripts to put in the list make sure we
		// change the page so the user knows what is happening.
		if (scriptCount == 0)
		{
			scriptElems = [ OPTION( { "value": "__info__", "class": "info"},
				"No scripts...") ];
			
			MochiKit.DOM.replaceChildNodes( "scriptTitlePane",
				STRONG("No scripts found."), BR() );
			MochiKit.DOM.replaceChildNodes( "scriptParamPane", BR());
		}

		MochiKit.DOM.replaceChildNodes( "scriptSelect", scriptElems );
	},

	/**
	 * Given a script ID, fill the param form with fields to enter arguments.
	 *
	 * @param scriptID     The string ID of the script. See comments at top of file
	 *                     for information on script IDs.
	 */
	populateScriptArgs: function( scriptID )
	{
		//logDebug( "Populate: ScriptID: ", scriptID );

		if (scriptID == null)
		{
			MochiKit.DOM.replaceChildNodes( "scriptParamPane", null );
			return;
		}

		var script = this.scripts[scriptID];
		if (script.args.length <= 0)
		{
			MochiKit.DOM.replaceChildNodes( "scriptParamPane", null );
			return;
		}

		//logDebug( "script args " + scriptID + ": " + script.args );


		// TODO: Instead of just creating text input elements, have
		// more specific input fields for arguments of certain types.
		//
		// e.g. "Bool" types
		//
		// Suggest that you implement this in argtypes.js, there's already
		// a function stub there named "generateInputField" which takes
		// in an integer corresponding to the WatcherDataType enum.
		//

		var elements = [];
		var newTable = MochiKit.DOM.createDOM( "table", {id:"argTable"} );

		// For each argument, create a new row, and add 2 cells to that
		// row.
		for ( var i = 0; i < script.args.length; i++ )
		{
			var arg = script.args[i];
			var type = ArgTypes.typeToLabel[arg[1]];
			var cellTitle = MochiKit.DOM.createDOM( "td", {id:"argCell"} );
			var cellInput = MochiKit.DOM.createDOM( "td", {id:"argCell"} );
			var newRow = MochiKit.DOM.createDOM( "tr" );

			MochiKit.DOM.replaceChildNodes( cellTitle, arg[0] + ": " );
			MochiKit.DOM.replaceChildNodes( cellInput, 
				INPUT( {"size": 10,
						"type": "text",
						"id": "arg"+arg[0], 
						"autocomplete": "off"},
					null) );

			MochiKit.DOM.replaceChildNodes( newRow, [ cellTitle, cellInput ] );

			elements.push( newRow );

			//elements.push( SPAN( {class:"param"}, 
			//	arg[0] + ": ",
			//	INPUT({size: 10, type:"text", id:"arg"+arg[0]}, null)), BR() 
			//);
		}

		// Put all the generated argument rows into the table
		MochiKit.DOM.replaceChildNodes( newTable, elements );
		MochiKit.DOM.replaceChildNodes( "scriptParamPane", newTable );
	},

	/**
	 * Populate the infoPane DIV with information about the script.
	 * At this point, we already should have such information.
	 *
	 * @param scriptID     The string ID of the script. See comments at top of file
	 *                     for information on script IDs.
	 */
	setScriptInfo: function( scriptID )
	{
		MochiKit.DOM.replaceChildNodes( "scriptTitlePane", null );

		if (scriptID == null)
		{
			return;
		}

		var script = this.scripts[scriptID];

		MochiKit.DOM.replaceChildNodes( "scriptTitlePane",
			STRONG(script.prettyTitle + ": ") );

		// If we have a description, split the string by newlines and instead 
		// use BRs where the newlines were.
		if (script.desc != "")
		{
			var descLines = script.desc.split('\n');

			for (var i = 0; i < descLines.length; i++)
			{
				MochiKit.DOM.appendChildNodes( "scriptTitlePane",
					descLines[i] );

				if (i != descLines.length - 1)
				{
					MochiKit.DOM.appendChildNodes( "scriptTitlePane",
						BR() );
				}
			}

		}

		// Fill the argument div with the arg list for this call.
		this.populateScriptArgs( scriptID );
		
		// Populate the radio button checklist
		MochiKit.DOM.replaceChildNodes( "scriptExecutePane", 
			INPUT( {"type":"hidden",
					"name": "runType",
					"value": script.runType } ),
			 INPUT( {"class": "submitButton",
			 		"type": "submit",
			 		"value":"Execute"})
		);
	},

	/**
	 * Display on the screen the information that we are currently retrieving 
	 * information via
	 *
	 * @param scriptID     The string ID of the script. See comments at top of
	 *                     file for information on script IDs.
	 */
	setScriptLoading: function( scriptID )
	{			
		var script = this.scripts[scriptID];
		MochiKit.DOM.replaceChildNodes( "scriptTitlePane", 
			"Loading info for script " + script.title + "..." );
		this.populateScriptArgs( null );
	},

	/**
	 * Event handler for when the "Execute script" form button is 
	 * pressed.
	 *
	 * We collect the data from the form and passes it to the
	 * "executeScript" function as usable javascript variables.
	 */
	executeScriptFromForm: function()
	{
		if (this.selectedScriptID == null)
		{
			//this.printMsg( "ERROR", "You haven't selected a script yet!" );
			return;
		}

		// Gather arguments
		var script = this.scripts[this.selectedScriptID];
		var args = script.args;
		var vals = [];

		for (var i = 0; i < args.length; i++)
		{
			var formName = "arg" + args[i][0];
			var value = $(formName).value;
			vals.push( value );
		}

		// Get runType from Radiobutton/text field
		var form = document.executeForm;
		var runType = null;
		if (form.runType.value != "")
		{
			runType = form.runType.value;
		}

		// Execute the script
		this.executeScript( this.selectedScriptID, vals, runType );
	}

}

MochiKit.DOM.addLoadEvent( MochiKit.Base.bind( RunScript.init, RunScript ) );

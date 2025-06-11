/*
 * This file provides functionality associated with the actions table
 * found in common/templates/common.kid actionsMenu().
 */

// Page global collection of row id's and associated actions.
var actionsForTable = {};


function addAction( rowID, actionID, action )
{
	var actionDict = actionsForTable[ rowID ];
	if (actionDict == undefined)
	{
		actionDict = {};
		actionsForTable[ rowID ] = actionDict;
	}

	actionDict[ actionID ] = action;
}


function performAction( rowID, actionElement )
{
	var actionDict = actionsForTable[ rowID ];
	if (actionDict == undefined)
	{
		alert( "ERROR: No data defined for ID: " + rowID );
		return;
	}

	var actionID = actionElement.options[ actionElement.selectedIndex ].text;
	var action = actionDict[ actionID ];
	if (action == undefined)
	{
		if (actionID != "Action...")
		{
			alert( "ERROR: No action defined" );
		}
		return;
	}


	actionElement.selectedIndex = 0;

	// perform the action
	eval( action );
}

// action_table.js

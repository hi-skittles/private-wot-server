var prefTree = null;
var currentCategory = null;
var selectedStatIds = new Object();
var displayPrefs = null;
var displayVal = true;

var colourPicker = null;
var flashProxy = null;

jQuery.noConflict();

jQuery( document ).ready( function () {
	colourPicker = jQuery('#colourpicker');
});


/**
 *	Numeric sort comparator function.
 */
function sortNumber( a, b )
{
	return a - b;
}

/**
 * This function is used from the flash files to send debugging
 * output back to the webpage. It should not be used most of
 * the time but is kept here to prevent having to re-impliment
 * it for debugging each time.
 */
function flashDebug( str )
{
	MochiKit.DOM.appendChildNodes( "flashDebugOutput",
		str + "\n", BR() );
}


function hideColourPicker()
{
	colourPicker.fadeOut();
}


function showLegendDiv()
{
	var legendCell = $( "legendCell" );
	var flashCell = $( "flashCell" );

	// Reveal div
	MochiKit.DOM.setDisplayForElement( "table-cell", legendCell );

	// Resize divs
	MochiKit.DOM.updateNodeAttributes( legendCell, {style:{width:'20%'}} );
	MochiKit.DOM.updateNodeAttributes( flashCell, {style:{width:'80%'}} );
}


function setPrefTree( newPrefTree )
{
	prefTree = newPrefTree;
}


function setDisplayPrefs( newDisplayPrefs )
{
	//console.log( "Received display prefs!" );
	displayPrefs = newDisplayPrefs;
}


function isLegendShown()
{
	var legendDiv = document.getElementById( "legendDiv" );

	if (legendDiv.style.display == "none")
	{
		return false;
	}

	return true;
}


function showLegend()
{
	showLegendDiv();
	setLegendType( currentCategory );
}


function hideLegend()
{
	var legendCell = document.getElementById( "legendCell" );
	legendCell.style.display = "none";

	var flash = document.getElementById( "flashCell" );
	flash.width = "100%";
}


function activateStat( category, newSelectedStatId )
{
	//console.log( 'activateStat( category=' + category +
	//	', newSelectedStatId=' + newSelectedStatId + " ): selectedStatId=" +
	//	selectedStatId );

	if (selectedStatIds[category] != null)
	{
		var oldSelectedStatId = selectedStatIds[category];
		selectedStatIds[category] = null;
		refreshStat( category, oldSelectedStatId );
		if (oldSelectedStatId == newSelectedStatId)
		{
			flashProxy.call( 'setSelectedStat', category, null );
			return;
		}
	}

	if (newSelectedStatId != null)
	{
		selectedStatIds[category] = newSelectedStatId;
		refreshStat( category, selectedStatIds[category] );
	}

	flashProxy.call( 'setSelectedStat', category, newSelectedStatId );
}


function isStatEnabled( category, statId )
{
	var categoryEnabledStatList = getCategoryEnabledStatList( category );
	for (var i = 0; i < categoryEnabledStatList.length; ++i)
	{
		if (categoryEnabledStatList[i] == statId)
		{
			return true;
		}
	}
	return false;
}

function getStatPrefs( category )
{
	if (category == "machine")
	{
		return prefTree.machineStatPrefs;
	}
	else
	{
		return prefTree.procPrefs[category].statPrefs;
	}
}

function getDisplayPrefs( category )
{
	if (category == "machine")
	{
		return displayPrefs.machineStatPrefs;
	}
	else
	{
		return displayPrefs.procPrefs[category];
	}
}

function getCategoryEnabledStatList( category )
{
	if (category == "machine")
	{
		return displayPrefs.enabledMachineStatOrder;
	}
	else
	{
		return displayPrefs.enabledProcStatOrder[category];
	}
}


function beginSetColour( category, statId )
{
	var colourBoxId = "#colourBox_" + statId;
	var colourBox = jQuery( colourBoxId );
	if (!colourBox)
	{
		throw new Error("couldn't find " + colourBoxId );
	}

	//  align to bottom of colour box row
	var y = colourBox.offset().top + 15;
	colourPicker.css('right', "10px" );
	colourPicker.css('top', y + "px" );

	colourPicker.fadeIn( 150, function() {
		//	hide colourpicker on doc click (note: a click on
		//	colour select box also triggers this handler).
		jQuery( document ).one( "click", function( ev ) {
			console.log("doc click hide");
			colourPicker.fadeOut();
		});
	});

	jQuery( '#colourpicker' ).one( "click", "td", function( ev ) {

		//  the colourpicker <td/> that was clicked
		var td = jQuery( ev.target );
		var newColour = td.css( 'background-color' );

		colourBox.css( 'background-color', newColour );

		var pos = newColour.search( /rgb\(/i );
		if (pos !== -1) // "rgb( 11, 22, 33 )"
		{
			//	convert to form '112233'
			var rgb = newColour.substring( pos + 4 ).split( ',' );
			var col = [
				parseInt( rgb[0] ).toString( 16 ),
				parseInt( rgb[1] ).toString( 16 ),
				parseInt( rgb[2] ).toString( 16 )
			];
			if (col[0].length == 1) col[0] = '0' + col[0];
			if (col[1].length == 1) col[1] = '0' + col[1];
			if (col[2].length == 1) col[2] = '0' + col[2];

			col = col.join('');
			flashProxy.call( 'setStatColour', currentCategory, statId, col );

			//	not really necessary as document.click handler will
			//	likely have been installed by now, but fadeOut just
			//	in case it hasn't
			colourPicker.fadeOut();
		}
		else throw new Error("unrecognised colour spec: " + newColour );
	});
}


/**
 * Set the appropriate style of the statistic row
 * in the legend.
 */
function refreshStat( category, statId )
{
	if (!isStatEnabled( category, statId ))
	{
		return;
	}
	var row = document.getElementById( "row_" + statId );

	if (statId == selectedStatIds[category] )
	{
		row.className = "selected";
	}
	else
	{
		row.className = "enabled";
	}
}

/**
 * Populate the legend with the current statistics.
 */
function setCurrentStats( stats )
{
	if (displayVal == false)
	{
		return;
	}

	var legendCell = document.getElementById( "legendCell" );
	if (legendCell.style.display == null)
	{
		return;
	}

	if (currentCategory == null)
	{
		return;
	}

	if (stats == null)
	{
		//console.log( "Stats is null!" );
		var statPrefs = getStatPrefs( currentCategory );
		for (i in statPrefs)
		{
			if (isStatEnabled( currentCategory, i ))
			{
				var td = document.getElementById( "val_" + i );
				//console.log( td );
				while (td.hasChildNodes())
				{
					td.removeChild( td.firstChild );
				}
			}
		}
		return;
	}

	for (var i in stats)
	{
		var val = stats[i];

		if (isStatEnabled( currentCategory, i ))
		{
			var td = document.getElementById( "val_" + i );
			while (td.hasChildNodes())
			{
				td.removeChild( td.firstChild );
			}

			if (val != null)
			{
				if (val == 0)
				{
					var text = document.createTextNode( val );
					td.appendChild( text );
				}
				else
				{
					var exp = Math.floor( Math.log( val ) / Math.LN10 );

					if ((exp >= 0) && (exp < 6))
					{
						var text = document.createTextNode(
							val.toPrecision( exp + 1 ) );
						td.appendChild( text );
					}
					else if ((exp > -3) && (exp < 0))
					{

						var text = document.createTextNode(
							val.toPrecision( 2 ) );
						td.appendChild( text );
					}
					else
					{
						// Scientific notation
						var exp = Math.floor( Math.log( val ) / Math.LN10 );
						var coefficient = val / Math.pow( 10, exp );

						var text = document.createTextNode(
							coefficient.toPrecision( 2 ) + "e" +
							(exp > 0 ? "+" + exp : exp));
						td.appendChild( text );
					}
				}
			}
		}
	}
}


/**
 * Change the category shown in the legend
 */
function setLegendType( category )
{
	hideColourPicker();

	// Ignore if category is exactly the same
	//
	// Why continue if it's null?
	//
	// Because the initial state of currentCategory is null,
	// and if we stop here we won't go through to
	// recreateLegend() which will then put some text
	// in the legend saying "No graphs selected".
	if ((category != null) && (category == currentCategory))
	{
		return;
	}

	currentCategory = category;

	var legendShown = isLegendShown();

	if (legendShown == false)
	{
		return;
	}

	// Construct the new legend
	recreateLegend();
}

/**
 * Recreate the table rows of the legend
 */
function recreateLegend()
{
	var legendDiv = document.getElementById( "legendDiv" );

	while(legendDiv.hasChildNodes())
	{
		legendDiv.removeChild( legendDiv.firstChild );
	}

	if (currentCategory == null)
	{
		var text = document.createTextNode( "To display the legend, select a graph by clicking on it." );
		legendDiv.appendChild( text );

		legendDiv.appendChild( P() );

		return;
	}
	else
	{
		var heading = document.createElement( "b" );
		var categoryStatPrefs = getStatPrefs( currentCategory );
		var categoryDisplayPrefs = getDisplayPrefs( currentCategory );
		var enabledStatList = getCategoryEnabledStatList( currentCategory );

		var headingText = null;
		if (currentCategory == "machine")
		{
			headingText = "Machine";
		}
		else
		{
			headingText = currentCategory;
		}
		heading.appendChild( document.createTextNode( headingText ) );
		legendDiv.appendChild( heading );

		legendDiv.appendChild( BR() );

		var openEditDialog = document.createElement( "a" );
		openEditDialog.href = "javascript:void(null);";
		openEditDialog.style.fontSize = "smaller";
		openEditDialog.appendChild(
			document.createTextNode( "Preferences..." ) );
		openEditDialog.onclick = openStatPrefEditDialog;
		legendDiv.appendChild( openEditDialog );

		var table = document.createElement( "table" );
		table.setAttribute( "class", "legendTable" );
		legendDiv.appendChild( table );

		var tr = document.createElement( "tr" );

		var th = document.createElement( "th" );
		th.setAttribute( "colspan", 2 );
		th.appendChild( document.createTextNode( "Statistic" ) );
		tr.appendChild( th );

		var th = document.createElement( "th" );
		th.appendChild( document.createTextNode( "Value" ) );
		tr.appendChild( th );

		table.appendChild( tr );

		for (var enabledIndex = 0;
				enabledIndex < enabledStatList.length;
				++enabledIndex)
		{
			var statPrefId = enabledStatList[enabledIndex];
			var statPref = categoryStatPrefs[statPrefId];
			var statDisplayPref = categoryDisplayPrefs[statPrefId];
			var tr = document.createElement( "tr" );
			tr.id = "row_" + statPrefId;
			tr.setAttribute( "class", "legendRow" );

			var colour = document.createElement( "td" );
			colour.className = "legendCell";
			var colourBox = document.createElement( "div" );
			colourBox.id = "colourBox_" + statPrefId;
			colourBox.style.width = "10px";
			colourBox.style.height = "10px";
			colourBox.style.backgroundColor = "#" + statDisplayPref.colour;
			colourBox.style.borderRight
			colourBox.setAttribute( "statId", statPrefId );
			//alert( prefColours[ statPref.dbId ] );
			colour.appendChild( colourBox );

			colourBox.onclick = function()
			{
				var statId = this.getAttribute( "statId" );
				beginSetColour( currentCategory, statId );
			}

			var name = document.createElement( "td" );
			var nameText = document.createTextNode( statPref.name );
			name.appendChild( nameText );
			name.setAttribute( "statId", statPrefId );
			name.setAttribute( "title", statDisplayPref.description );
			name.onclick = function()
			{
				var statId = this.getAttribute( "statId" );
				//console.log( "stat pref name (statId=" + statId +
				//	").onClick " );
				activateStat( currentCategory, statId );
			}


			var value = document.createElement( "td" );
			value.className = "value";
			value.id = "val_" + statPrefId;

			tr.appendChild( colour );
			tr.appendChild( name );
			tr.appendChild( value );

			tr.style.cursor = "pointer";
			table.appendChild( tr );

			refreshStat( currentCategory, statPrefId );
		}
	}

	// Get current stats
	flashProxy.call( 'getCurrentStats' );
}


function showPreferenceDialog()
{
	jQuery( '#flashDiv' ).hide();
	jQuery( '#stat_pref_edit_dialog' ).fadeIn();
}


function hidePreferenceDialog()
{
	jQuery( '#stat_pref_edit_dialog' ).hide();
	jQuery( '#flashDiv' ).fadeIn();
}


/**
 *	Open the statistics preference editing dialog.
 */
function openStatPrefEditDialog()
{
	var statPrefs = getStatPrefs( currentCategory );
	var enabledStatList = getCategoryEnabledStatList( currentCategory );

	var contents = $( "stat_pref_edit_contents" );

	// clear the dialog contents
	while (contents.hasChildNodes())
	{
		contents.removeChild( contents.firstChild );
	}

	// title
	var title = document.createElement( 'h1' );
	title.appendChild( document.createTextNode(
		"Edit Statistics Preferences" ) );
	contents.appendChild( title );

	// statistics disabled select list (those that aren't currently shown)
	var statsDisabledList = document.createElement( 'select' );
	statsDisabledList.setAttribute( 'id', 'disabledList' );
	statsDisabledList.setAttribute( 'size', '10' );
	statsDisabledList.setAttribute( 'multiple', 'true' );

	// populate the disabled statistics select list
	var disabledStatOrder = new Array();

	for (var statPrefId in statPrefs)
	{
		// filter only those stats that are disabled
		if (!isStatEnabled( currentCategory, statPrefId ))
		{
			disabledStatOrder.push( statPrefId );
		}
	}
	disabledStatOrder.sort( sortNumber );
	for (var i = 0; i < disabledStatOrder.length; ++i)
	{
		var statPrefId = disabledStatOrder[i];
		var statPref = statPrefs[statPrefId];
		var prefOption = document.createElement( 'option' );
		prefOption.name = statPrefId;
		prefOption.appendChild( document.createTextNode( statPref.name ) );
		statsDisabledList.appendChild( prefOption );
	}

	if (statsDisabledList.options.length == 0)
		// add null pref option if it's empty
	{
		statsDisabledList.appendChild( makeNullPrefOption() );
	}

	// statistics disabled table cell
	var disabledCell = document.createElement( 'td' );
	var disabledDiv = document.createElement( 'div' );
	disabledDiv.setAttribute( 'class', 'stat_select_list' );
	disabledCell.appendChild( disabledDiv );
	disabledDiv.appendChild(
		document.createTextNode( 'Disabled statistics' ) );
	disabledDiv.appendChild( BR() );
	disabledDiv.appendChild( statsDisabledList );

	// statistics enabled select list (those that are currently shown)
	var statsEnabledList = document.createElement( 'select' );
	statsEnabledList.setAttribute( 'id', 'enabledList' );
	statsEnabledList.setAttribute( 'size', '10' );
	statsEnabledList.setAttribute( 'multiple', 'true' );

	for (var i = 0; i < enabledStatList.length; ++i)
	{
		var statPrefId = enabledStatList[i];
		// filter only those stats that are enabled
		var statPref = statPrefs[statPrefId];

		var prefOption = document.createElement( 'option' );
		prefOption.name = statPrefId;
		prefOption.appendChild( document.createTextNode( statPref.name ) );
		statsEnabledList.appendChild( prefOption );
	}
	if (statsEnabledList.options.length == 0)
		// add null pref option if it's empty
	{
		statsEnabledList.appendChild( makeNullPrefOption() );
	}

	// statistics enabled table cell
	var enabledCell = document.createElement( 'td' );
	var enabledDiv = document.createElement( 'div' );
	enabledDiv.setAttribute( 'class', 'stat_select_list' );
	enabledCell.appendChild( enabledDiv );
	enabledDiv.appendChild(
		document.createTextNode( 'Enabled statistics' ) );
	enabledDiv.appendChild( BR() );
	enabledDiv.appendChild( statsEnabledList );

	// button for transfer from enabled to disabled lists
	// (i.e. disabling the stat)
	var makeEnabledButton = document.createElement( 'input' );
	makeEnabledButton.setAttribute( 'type', 'button' );
	makeEnabledButton.setAttribute( 'value', '>>' );

	makeEnabledButton.onclick = function()
	{
		moveSelectedItems( document.getElementById( 'disabledList' ),
			document.getElementById( 'enabledList' ) );
	}

	// button for transfer from disabled to enabled lists
	// (i.e. enabling the stat)
	var makeDisabledButton = document.createElement( 'input' );
	makeDisabledButton.setAttribute( 'type', 'button' );
	makeDisabledButton.setAttribute( 'value', '<<' );
	makeDisabledButton.onclick = function()
	{
		moveSelectedItems( document.getElementById( 'enabledList' ),
			document.getElementById( 'disabledList' ) );
	}

	// table cell for transfer button controls
	var transferCell = document.createElement( 'td' );
	transferCell.setAttribute( 'valign', "center" );
	transferCell.setAttribute( 'align', "center" );
	transferCell.appendChild( makeEnabledButton );
	transferCell.appendChild( BR() );
	transferCell.appendChild( makeDisabledButton );

	// shift selected enabled stats up button
	var shiftUpButton = document.createElement( 'input' );
	shiftUpButton.setAttribute( 'id', 'shift_up' );
	shiftUpButton.setAttribute( 'type', 'button' );
	shiftUpButton.setAttribute( 'value', 'up' );
	shiftUpButton.onclick = function()
	{
		shiftSelectedItems(
			document.getElementById( 'enabledList' ),
			false // down
		);
	}

	// shift selected enabled stats down button
	var shiftDownButton = document.createElement( 'input' );
	shiftDownButton.setAttribute( 'id', 'shift_down' );
	shiftDownButton.setAttribute( 'type', 'button' );
	shiftDownButton.setAttribute( 'value', 'down' );
	shiftDownButton.onclick = function()
	{
		shiftSelectedItems(
			document.getElementById( 'enabledList' ),
			true // down
		);
	}

	// selected statistic shift control table cell
	var shiftCell = document.createElement( 'td' );
	shiftCell.setAttribute( 'valign', "center" );
	shiftCell.setAttribute( 'align', "center" );
	shiftCell.appendChild( shiftUpButton );
	shiftCell.appendChild( BR() );
	shiftCell.appendChild( shiftDownButton );

	// dialog table
	var table = document.createElement( 'table' );
	var row = document.createElement( 'tr' );

	row.appendChild( disabledCell );
	row.appendChild( transferCell );
	row.appendChild( enabledCell );
	row.appendChild( shiftCell );
	table.appendChild( row );

	contents.appendChild( table );

	// save button
	var buttonDiv = document.createElement( 'div' );
	buttonDiv.setAttribute( "class", "buttons" );
	var save = document.createElement( 'input' );
	save.setAttribute( 'type', 'button' );
	save.setAttribute( 'value', 'Save' );
	save.onclick = function()
	{
		hidePreferenceDialog();
		saveStatsPrefs( statsEnabledList, statsDisabledList );
	}
	buttonDiv.appendChild( save );

	// cancel button
	var cancel = document.createElement( 'input' );
	cancel.setAttribute( 'type', 'button' );
	cancel.setAttribute( 'value', 'Cancel' );
	cancel.onclick = function()
	{
		hidePreferenceDialog();
	}
	buttonDiv.appendChild( cancel );

	contents.appendChild( buttonDiv );

	showPreferenceDialog();
}

/**
 *	Move selected HTML Option elements from the source list to the end of the
 *	destination list. This preserves any attributes set on the HTML Option
 *	elements. Ignores any null preference options.
 *
 *	@param srcSelect	the source HTML select list element
 *	@param destSelect	the destination HTML select list element
 */
function moveSelectedItems( srcSelect, destSelect )
{
	var itemsToMove = new Array();

	// do a non-mutating pass to collect the selected option elements to move
	for (var selected = 0; selected < srcSelect.length; ++selected)
	{
		var selectedItem = srcSelect.options[selected];
		if (selectedItem.name == 'none' ||
			!selectedItem.selected)
		{
			// got the null value
			selectedItem.selected = false;
			continue;
		}
		itemsToMove.push( selectedItem );
	}

	// remove the null pref option if it exists in the destination
	if (destSelect.length == 1 &&
			destSelect.options[0].name == 'none' &&
			itemsToMove.length > 0)
	{
		destSelect.removeChild( destSelect.options[0] );
	}

	// get the selected option elements, and move the from source to destination
	for (var selected in itemsToMove)
	{
		var selectedItem = itemsToMove[selected];

		srcSelect.removeChild( selectedItem );
		destSelect.appendChild( selectedItem );
	}

	// add the null pref option if source list is empty
	if (srcSelect.length == 0)
	{
		srcSelect.appendChild( makeNullPrefOption() );
	}
}


/**
 *	Make a new null preferences option with the name 'none' and value
 *	'-- none --' for use in the statistics preference HTML select lists.
 */
function makeNullPrefOption()
{
	var nullPrefOption = document.createElement( 'option' );
	nullPrefOption.name = 'none';
	nullPrefOption.appendChild( document.createTextNode( "-- none --" ) );
	return nullPrefOption;
}


/**
 *	Move the selected options in a HTML select element up or down. If it hits
 *	the boundary, selected items push out any unselected items in between them.
 *
 *	@param selectList 	the select list element
 *	@param down 		true for rotating down, or false for rotating up
 */

function shiftSelectedItems( selectList, down )
{
	// get the selected items
	var selectedIndices = new Array();

	for (var selectIndex = 0; selectIndex < selectList.length; ++selectIndex)
	{
		if (selectList.options[selectIndex].selected)
		{
			selectedIndices.push( selectIndex );
		}
	}

	if (!down)
	{
		// we are moving selected items up the list
		for (var selectIndex = 1;
			selectIndex < selectList.length;
			++selectIndex)
		{
			var lastElement = selectList.options[selectIndex - 1];
			var thisElement = selectList.options[selectIndex];
			if (!lastElement.selected && thisElement.selected)
			{
				swapSelectListItem( selectList, selectIndex - 1, selectIndex );
			}
		}

	}
	else
	{
		// we are moving selected items down the list
		for (var selectIndex = selectList.length - 1;
			selectIndex > 0;
			--selectIndex)
		{
			var nextElement = selectList.options[selectIndex];
			var thisElement = selectList.options[selectIndex - 1];
			if (!nextElement.selected && thisElement.selected)
			{
				swapSelectListItem( selectList, selectIndex - 1, selectIndex );
			}
		}
	}
}


/**
 *	Swap two items in a HTML select list element.
 *
 *	@param selectList 		the HTML Select element
 *	@param elementIndex1 	the index of the first element
 *	@param elementIndex2 	the index of the second element
 *
 */
function swapSelectListItem( selectList, elementIndex1, elementIndex2 )
{
	var options = selectList.options;
	var element1 = options[elementIndex1];
	var element2 = options[elementIndex2];

	var element1Copy = document.createElement( 'option' );
	element1Copy.text = element1.text;
	element1Copy.name = element1.name;
	element1Copy.selected = element1.selected;

	var element2Copy = document.createElement( 'option' );
	element2Copy.text = element2.text;
	element2Copy.name = element2.name;
	element2Copy.selected = element2.selected;

	options[elementIndex2] = element1Copy;
	options[elementIndex1] = element2Copy;
}


/**
 *	Save the statistics preferences for each statistic given in the HTML select
 *	list.
 *
 *	@param statEnableList	the HTML select list of statistics to enable.
 *	@param statDisableList	the HTML select list of statistics to disable.
 */
function saveStatsPrefs( statEnableList, statDisableList )
{
	var categoryEnabledList = getCategoryEnabledStatList( currentCategory );
	while (categoryEnabledList.length)
	{
		categoryEnabledList.pop();
	}

	var categoryDisabledList = new Array();

	// stats enabled list
	for (var listIndex = 0;
			listIndex < statEnableList.options.length;
			++listIndex)
	{
		if (statEnableList.options[listIndex].name == 'none')
		{
			continue;
		}

		var option = statEnableList.options[listIndex];
		var statId = option.name;

		categoryEnabledList.push( statId );
	}

	for (var listIndex = 0;
			listIndex < statDisableList.options.length;
			++listIndex)
	{
		if (statDisableList.options[listIndex].name == 'none')
		{
			continue;
		}

		var option = statDisableList.options[listIndex];
		var statId = option.name;

		categoryDisabledList.push( statId );
	}

	// force recreation of legend stats
	recreateLegend( currentCategory );

	flashProxy.call( 'saveEnabledStatOrder',
		currentCategory, categoryEnabledList, categoryDisabledList );
}


"use strict";

jQuery.noConflict();

var sv;							// SV.SpaceViewSurface
var mini;						// SV.MiniMap
var configIsShowing = false;
var loadBalanceIsShowing = false;
var isEntityTypeTableGenerated = false;

//	Map of UI elements that can have their colour changed. Values of
//	map are the property names of the UI element style object that
//	are re-colourable. The first element of this property array will
//	be used to init the BG colour of the colour selector.
var recolourableElements =
{
	cellLabel: ['backgroundColor'],
	partitionLine: ['strokeStyle'],
	entity: ['fillStyle'],
	ghostEntity: ['fillStyle'],
	chunkBounds: ['strokeStyle'],
	entityBounds: ['strokeStyle', 'fillStyle'],
};

jQuery( document ).ready( function()
{
	sv = new SV.SpaceViewSurface( spaceId );

	var configPanel = jQuery("#sv-config-panel");

	/*	bind events	 */

	//	recalc width of sv container manually on resize.
	//	manual resize is needed because config panel is fixed width
	jQuery( window ).on( 'resize', resizeSpaceviewerContainer );

	//	resize spaceviewer when left nav menu is hidden
	jQuery('#menu_collapser').on( "click", resizeMainContent );

	//	bind spaceviewer events
	jQuery( sv ).on({
		"disconnect.model.sv": notifyNotConnected,
		"failedRequestUpdate.model.sv": notifyNotConnected
	});

	if (UI.fps.enabled)
    {
        jQuery( '.sv-debug .fps', sv.dom.container ).show();
        jQuery( sv ).on({
            'draw.sv': function()
            {
                if (!sv._frameTimeSmoothed)
                {
                    sv._frameTimeSmoothed = this._frameTime;
                }
                this._frameTimeSmoothed -= this._frameTimeSmoothed / 5;
                this._frameTimeSmoothed += this._frameTime / 5;

                jQuery( '.sv-debug .fps', sv.dom.container ).html(
                    'frameTime: ' + this._frameTimeSmoothed.toFixed( 1 ) + " msec" );
            }
        });
	}

	// make a click on checkbox label click its checkbox
	configPanel.on( 'click', 'tr td:last-child', function() {
		var c = jQuery( this ).parent().find( ':checkbox' );
		c.click();
	});

	// click on entity type checkbox adds it to the exclude list for drawing
	configPanel.on( 'click', '#sv-config-entityTypes :checkbox', function() {
		var entityTypeId = jQuery( this ).parent().parent().attr( 'entity-type-id' );
		UI.entity.excluded[ entityTypeId ] = !UI.entity.excluded[ entityTypeId ];
		sv.draw();
	});

	// mouseover on an entity type row highlights all entities of that type
	configPanel.on( 'mouseover', '#sv-config-entityTypes tr', function() {
		var entityTypeId = jQuery( this ).attr( 'entity-type-id' );
		UI.entity.highlighted[ entityTypeId ] = true;
		sv.draw();
		sv.entityHighlightAnimation.play();
	});

	// mouseout on entity type row unhighlights
	configPanel.on( 'mouseout', '#sv-config-entityTypes tr', function() {
		var entityTypeId = jQuery( this ).attr( 'entity-type-id' );
		delete UI.entity.highlighted[ entityTypeId ];
		sv.draw();
		sv.entityHighlightAnimation.stop();
	});

	sv.connectModel();
	mini = new SV.MiniMap( sv );

	if (UI.fps.enabled)
	{
		sv.perfGraph( "#sv-perfgraph", sv.dom.container );
	}

	if (!numInitialServiceApps)
	{
		new Alert.Error(
			"No ServiceApps are running a HTTPResTreeService. " +
			"Background tiles and entity icons cannot be displayed.",
			{ duration: 30000 }
		);
	}
});


function notifyNotConnected()
{
	if (Alert.isVisible( 'sv-not-connected' ))
	{
		// notification already displayed
		return;
	}

	var persistentNotification = new Alert.Warning(
		'SpaceViewer is not currently connected to a BigWorld server<br/>',
		{ id: 'sv-not-connected', dismissable: false, duration: 0 }
	);

	var href = jQuery( '<a/>' ).attr( 'href', '#' ).html( 'Reconnect' );
	href.one( 'click', function() {

		persistentNotification.dismiss();

		jQuery( sv ).one( 'failedRequestUpdate.model.sv', function() {
			new Alert.Error(
				'The Web Console server is no longer running',
				{ id: 'sv-webconsole-is-down', duration: 5000 }
			);
		});
		sv.connectModel();
		return false;
	});
	// persistentNotification.append( href );
	persistentNotification.jquery.append( href );

	jQuery( sv ).one( 'requestUpdate.model.sv', function() {
		if (persistentNotification)
		{
			persistentNotification.dismiss();
			new Alert.Info( "SpaceViewer reconnected", { id: 'sv-reconnected', duration: 2000 } );
		}

		Alert.dismiss( 'sv-webconsole-is-down' );

		if (!sv._isInterpolating)
			sv.startInterpolation();
	});

	if (sv._isInterpolating)
		sv.stopInterpolation();
}


/**
*	Resizes content and navigation divs taking into account div#navigation
*	shown/hidden state.
*/
function resizeMainContent()
{
	var mainDiv = jQuery('#main');
	if ( jQuery('#navmenu_cell').hasClass( 'menu-collapsed' ) )
	{
		//	navigation div was just hidden, make css left equal
		//	to css right & resize canvas.
		mainDiv.attr( 'originalLeft', parseInt( mainDiv.css('left') ) );
		var targetLeft = parseInt( mainDiv.css('right') ); // ie: equal left & right
		if (SV.debug)
		{
			console.log( "#main.left: "
					   + mainDiv.attr( 'originalLeft' )
					   + "px -> "
					   + targetLeft
					   + "px" );
		}

		//	animate resize
		var lastLeft = mainDiv.attr( 'originalLeft' );
		mainDiv.animate( { left: targetLeft }, {
			duration: 100,
			step: function( currentLeft ) {
				var delta = lastLeft - currentLeft;
				sv.panCanvas( -delta, 0 );
				sv.dom.container.width( '+=' + Math.round(delta) );
				sv.resizeWindow();
				lastLeft = currentLeft;
			},
			complete: function() {  sv.resizeWindow();  },
		});
	}
	else
	{
		//	navigation div was just unhidden, make css left equal
		//	to css right & resize canvas.
		var lastLeft = parseInt( mainDiv.css('left') );
		if (SV.debug)
		{
			console.log( "#main.left: "
					   + lastLeft
					   + "px -> "
					   + mainDiv.attr( 'originalLeft' )
					   + "px" );
		}

		mainDiv.animate( { left: mainDiv.attr('originalLeft') }, {
			duration: 100,
			step: function( currentLeft ) {
				var delta = lastLeft - currentLeft;
				sv.panCanvas( -delta, 0 );
				sv.dom.container.width( '+=' + Math.round(delta) );
				sv.resizeWindow();
				lastLeft = currentLeft;
			},
			complete: function() {  sv.resizeWindow();  },
		});
	}
}


/** Update config panel colour selectors to current SV state. */
function updateColourSelectorState()
{
	jQuery("#sv-config-panel div.sv-config-colour-selector").each(
		function( index )
		{
			var div = jQuery( this );
			var id = div.attr( 'id' ).substring( "colour_".length );
			var propertyNames = recolourableElements[id];

			if (! propertyNames)
				throw new Error("UI element id '" + id + "' not configurable");

			if (! UI[id])
				throw new Error("No UI element with id '" + id + "'");

			//	initial colour comes from first property
			var propName = propertyNames[0];
			var colour = convertToRgb( UI[id][propName] );
			div.css('background-color', colour );

			//	open colour selector on click
			div.click( function( ev ) {
				ev.stopPropagation();
				showColourPicker( id, ev.target );
			});
		}
	);
}


/** Update config panel checkbox state to current SV config state. */
function updateCheckboxState()
{
	//	check checkboxes for enabled UI elements
	jQuery("#sv-config-panel :checkbox").each( function() {
		var chkbox = jQuery( this );
		var id = chkbox.attr("id");
		if (id)
		{
			var key = id.substr( 7 );
			if (key && UI[key] !== undefined)
			{
				var enabled = UI[key].enabled;
				chkbox.attr( "checked", enabled );

				if (SV.debug > 1)
					console.log( key + ": "
						+ (enabled ? "enabled" : "disabled") );
			}
		}
		else console.warn("missing id attribute on " + this );
	});

	updateEntityIcons();
}


/**
*   Dynamically (re-)create the entity type section of the config panel.
*/
function createEntityTypeTable()
{
	jQuery( '#sv-config-entityTypes' ).remove();

	var table = jQuery('#sv-config-panel table');

	//	generate the following html structure:
	/*
	<tr><th colspan="3">Entity types</th></tr>
	<tr>
		<td><input type="checkbox" /></td>
		<td><div class="sv-config-colour-selector sv-entity"></div></td>
		<td>Merchant NPC</td>
	</tr>
	*/

	// add <tbody/>
	var t = jQuery( '<tbody/>' );
	// t.appendTo( table );
	t.prop( 'id', 'sv-config-entityTypes' );

	// <th/> header
	jQuery('<tr><th colspan="3">Entity types</th></tr>').appendTo( t );

	// sort entity types alphabetically by type name
	var types = sv.entityTypes;
	var colours = UI.entity.colours;

	var id, type;
	var typesByName = {};
	var orderedTypes = new Array();

	for (id in types)
	{
		orderedTypes.push( types[id] );
		typesByName[ types[id] ] = id;
	}

	// sort alphabetic 'a' before 'z'
	orderedTypes.sort( function( a, b ) {
		return (a > b) - (a < b);
	});

	// create and append table rows for each entity type
	var tr, td, chkbox, count = 0;
	for ( var i in orderedTypes )
	{
		type = orderedTypes[i];
		id = typesByName[type];

		// create & append <tr/>
		tr = jQuery( '<tr/>');
		tr.attr({
			'entity-type-id': id,
			'entity-type-name': type
		});
		tr.appendTo( t );

		// create & append <td/> for checkbox
		td = jQuery('<td/>').appendTo( tr );
		chkbox = jQuery('<input type="checkbox"/>');
		chkbox.appendTo( td ).prop({ 'id': 'chkbox_entity_' + id, checked: true });

		// create & append <td/> for colour indicator
		td = jQuery('<td/>').appendTo( tr );
		td.append( '<div style="background-color:'
				 + colours[ id ]
				 + '" class="sv-entity"></div><img src="'
				 + SV.BASEURL_ENTITY_ICONS
				 + '/'
				 + type
				 + '.png" class="sv-fade-animation sv-entity-icon" '
				 + 'onerror="jQuery( this ).siblings().addClass(\'sv-entity-icon\'); jQuery( this ).detach()" />'
				 );

		// create & append <td/> for type name
		td = jQuery('<td/>').appendTo( tr );
		var abbr = jQuery('<abbr/>').appendTo( td );
		abbr.append( type );
		abbr.attr( 'title', "entity type '" + type + "'" );
		jQuery('<span/>').appendTo( abbr );

		count++;
	}

	t.appendTo( table );

	if (SV.debug)
	{
		console.log("created entity type table with " + count + " type(s)");
	}
}


/**
*   Update displayed state of the entity type section ("#sv-config-entityTypes")
*   of the config panel to reflect current # of reals & ghosts. Entity types
*   without any entities are hidden from view.
*/
function updateEntityTypeTable( /*boolean*/ shouldAnimate )
{
	var countByType = {};
	var total = 0;

	var entities = sv.getRealEntities();
	total += entities.length;
	for (var i in entities)
	{
		var count = countByType[ entities[ i ][ 2 ] ] || 0;
		countByType[ entities[ i ][ 2 ] ] = count + 1;
	}

	entities = sv.getGhostEntities();
	total += entities.length;
	for (var i in entities)
	{
		var count = countByType[ entities[ i ][ 2 ] ] || 0;
		countByType[ entities[ i ][ 2 ] ] = count + 1;
	}

	if (!total) return;

	var animDuration = (shouldAnimate === false) ? 0 : 750;

	jQuery( '#sv-config-entityTypes tr[entity-type-id]' ).each( function() {
		var tr = jQuery( this );
		var id = tr.attr( 'entity-type-id' );
		var count = countByType[ id ];
		if ( count )
		{
			tr.css( 'background', '#eaf8fd' ).fadeIn( animDuration );
			tr.find( 'span' ).html( ' (' + count + ')' );
		}
		else
		{
			tr.css( 'background', '#eee' ).delay( animDuration ).fadeOut( animDuration );
			tr.find( 'span' ).html( ' (none)' );
		}
	});

	updateEntityIcons();
}


/**
*	Resize .sv-container and canvas taking into account config panel state.
*
*	Assumes the following CSS structure:
*
*		(parent container)
*		|
*		+-- div.sv-container (position: absolute)
*		|
*		+-- div.sv-config-panel (position: absolute)
*/
function resizeSpaceviewerContainer()
{
	var svDiv = jQuery('.sv-container');

	if ( configIsShowing )
	{
		var configPanel = jQuery( '#sv-config-panel' );
		svDiv.width( svDiv.parent().width() -
						configPanel.outerWidth(true) - 12 );
	}
	else if (loadBalanceIsShowing)
	{
		var loadBalancePanel = jQuery( '#load-balance-panel' );
		svDiv.width( svDiv.parent().width() -
						loadBalancePanel.outerWidth(true) - 12 );
	}
	else
	{
		svDiv.width( svDiv.parent().width() );
	}

	sv.resizeWindow();
}


/** Show/hide config panel. */
function toggleSettings( /*Button*/ b )
{
	if (configIsShowing)
	{
		hideSettings( b );	
	}
	else
	{
		showSettings( b );
	}
}

function showSettings( /*?Button*/ b )
{
	// hide load balance panel if it's being shown
	if (loadBalanceIsShowing)
	{
		hideLoadBalance();
	}

	var configPanel = jQuery( '#sv-config-panel' );

	//	shrink canvas, show settings
	if (!isEntityTypeTableGenerated)
	{
		createEntityTypeTable();
		isEntityTypeTableGenerated = true;
		updateCheckboxState();
		updateColourSelectorState();
	}
	updateEntityTypeTable( false );

	jQuery( sv ).on({
		'configChanged.sv': updateCheckboxState,
		'updateModel.sv': updateEntityTypeTable,
	});

	//	animated show 
	showPanel( configPanel );

	if (b)
	{
		// button is passed in as dom element
		b.innerHTML = 'Hide Settings';
	}
	else
	{
		jQuery( '.setting-button' ).text( 'Hide Settings');
	}

	configIsShowing = true;
}


function hideSettings( /*?Button*/ b )
{
	var configPanel = jQuery( '#sv-config-panel' );

	jQuery( sv ).off({
		'configChanged.sv': updateCheckboxState,
		'updateModel.sv': updateEntityTypeTable,
	});

	//	hide config, rescale canvas back to size
	hidePanel( configPanel );

	if (b)
	{
		// button is passed in as dom element
		b.innerHTML = 'Settings';
	}
	else
	{
		jQuery( '.setting-button' ).text( 'Settings');
	}

	configIsShowing = false;
}


/** Show/hide load balance panel. */
function toggleLoadBalancePanel( /*Button*/ b )
{
	if (loadBalanceIsShowing)
	{
		hideLoadBalance( b );
	}
	else
	{
		showLoadBalance( b );
	}
}


function showLoadBalance( /*?Button*/ b )
{
	// hide setting first if it's being shown
	if (configIsShowing)
	{
		hideSettings();
	}

	showPanel( jQuery( '#load-balance-panel' ) );

	if (b)
	{
		// button is passed in as dom element
		b.innerHTML = 'Hide Load Balancing';
	}
	else
	{
		jQuery( '.load-balance-button' ).text( 'Hide Load Balancing');
	}

	loadBalanceIsShowing = true;
}


function hideLoadBalance( /*?Button*/ b )
{
	hidePanel( jQuery( '#load-balance-panel' ) );

	if (b)
	{
		// button is passed in as dom element
		b.innerHTML = 'Load Balancing';
	}
	else
	{
		jQuery( '.load-balance-button' ).text( 'Load Balancing');
	}

	loadBalanceIsShowing = false;
}


/** Show panel */
function showPanel( /*Object*/ panel )
{
	var svDiv = jQuery('.sv-container'), targetWidth;

	//	animated show
	targetWidth = svDiv.parent().width() - panel.outerWidth(true) - 12;
	svDiv.animate(
		{ width: targetWidth },
		{
			duration: 100,
			step: function() { sv.resizeWindow(); },
			complete: function() {
				sv.resizeWindow();
				panel.fadeIn( 200, updateEntityIcons );
			}
		}
	);
}


/** Hide panel */
function hidePanel( /*Object*/ panel )
{
	var svDiv = jQuery('.sv-container'), targetWidth;

	//	hide config, rescale canvas back to size
	targetWidth = svDiv.parent().width();
	panel.fadeOut( 200 );
	svDiv.animate(
		{ width: targetWidth },
		{
			duration: 200,
			step: function() { sv.resizeWindow(); },
			complete: function() { sv.resizeWindow(); }
		}
	);
}


/**
*   Show colour picker widget for the given DOM element.
*
*	id - The ID of the UI element to show colour picker for.
*	div - Reference to the DOM element for the colour div for id.
*/
function showColourPicker( /*String*/ id, /*HTMLDomElement*/ div )
{
	//	check there is a style object for given id
	if (!UI[ id ])
	{
		throw new Error("No UI style object named " + id );
	}

	var cp = jQuery( '#colourpicker' );
	if ( cp.css( 'display' ) != 'none' )
	{
		cp.fadeOut();
		return;
	}

	//	align to bottom of <tr/>
	var el = jQuery( div );
	var y = el.offset().top - el.offsetParent().offset().top + 17;
	cp.css('right', "0px" );
	cp.css('top', y + "px" );
	cp.fadeIn();

	//	clicking outside the colourpicker (ie: on document) hides
	//	the colourpicker.
	jQuery( document ).one( "click", function( ev ) {
		cp.fadeOut();
	});

	//	install event handler that will re-colour all relevant UI element
	//	colour properties.
	//
	//	current behaviour is to hide colourpicker after a single click
	//	or selection.
	cp.one( "click", "td", function( ev ) {

		//	the colourpicker <td/> that was clicked
		var td = jQuery( ev.target );
		var newColour = td.css('background-color');

		var colourProperties = recolourableElements[ id ];
		var elementStyle = UI[id];

		for ( var p in colourProperties )
		{
			var colourProp = colourProperties[p];
			if (!elementStyle[ colourProp ])
			{
				console.warn("UI style '" + id + "' has no property '" + colourProp + "'");
				continue;
			}

			var alpha = getAlpha( elementStyle[ colourProp ] ) || 1;
			var rgba = convertToRgba( newColour, alpha );

			if (SV.debug)
				console.log( "setting " + id + "." + colourProp + " = " + rgba );

			elementStyle[ colourProp ] = rgba;
			el.css('background-color', newColour );
		}

		sv.draw();
	});

}


/**
*	convertToRgb( "rgba( 0, 0, 0, 0.5 )" ) returns "rgb( 0, 0, 0 )"
*/
function convertToRgb( /*string*/ rgba ) /* returns string */
{
	// if (rgba.match( /rgb\(\s*(\d+)\s*,\s*(\d+)\s*,(\d+)\s*,(\d(?:\.\d+)?)\s*\)/i ))
	if (rgba.match( /rgb\(/i ))
		return rgba;

	if (rgba.match( /rgba\(/i ))
	{
		return ( "rgb"
			   + rgba.substring( 4, rgba.lastIndexOf(',') )
			   + ')' );
	}

	throw new Error("unparseable '" + rgba + "'");
}


//	convertToRgba( "rgb( 0, 0, 0 )", 0.5 ) returns "rgb( 0, 0, 0, 0.5 )"
function convertToRgba( rgb, alpha )
{
	return ( "rgba"
		   + rgb.substring( 3, rgb.lastIndexOf(')') )
		   + ', '
		   + alpha
		   + ')' );
}


//	getAlpha( "rgba( 0, 0, 0, 0.4 )" ) returns 0.4
function getAlpha( colour )
{
	if (colour.match( /rgba\(/i ))
	{
		return parseFloat(
			colour.substring(
				colour.lastIndexOf(',') + 1 ) );
	}
	else
	{
		console.warn("not an RGBA colour, presuming alpha=1");
		return 1;
	}
}


function toggleInterpolation()
{
	if (UI.interpolation.enabled)
	{
		if (sv._isInterpolating)
			sv.stopInterpolation();

		UI.interpolation.enabled = false;
	}
	else
	{
		if (!sv._isInterpolating)
			sv.startInterpolation();

		UI.interpolation.enabled = true;
	}
}


function toggleMinimap()
{
	if (UI.minimap.enabled)
	{
		jQuery( '.sv-minimap', sv.dom.container ).hide();
		UI.minimap.enabled = false;
	}
	else
	{
		jQuery( '.sv-minimap', sv.dom.container ).show();
		UI.minimap.enabled = true;
		mini.draw();
	}
}


/**
*   Sync displayed state of entities as either circles or icons
*   according to the set value of UI.entityIcons.enabled
*/
function updateEntityIcons()
{
	if (UI.entityIcons.enabled)
	{
		jQuery( '.sv-entity:not(.sv-entity-icon)' ).hide();
		jQuery( '.sv-entity-icon' ).show();
	}
	else
	{
		jQuery( '.sv-entity-icon:not(.sv-entity)' ).hide();
		jQuery( '.sv-entity' ).show();
	}
}

// spaceviewer_detail_page.js

"use strict";

if (window.UI)
{
	//  initial UI element state for spaceviewer previews
	UI.chunkBounds.enabled = false;
	UI.entityBounds.enabled = false;
	UI.cellLabel.enabled = false;
	UI.partitionLabel.enabled = false;
	UI.fps.enabled = false;
	UI.scaleIndicator.maxWidth = 100; // px
}


var spacesTable;
jQuery( document ).ready( function()
{
	spacesTable = new SpacesWidget( '#dynamic-spacelist' );
	spacesTable.connectModel();

	jQuery( document ).one( 'keypress', function() {
		spacesTable.dom.container.find( 'input[type="text"]' ).focus();
	});

});


function getSpaceviewer( domContext )
{
	var spaceId = jQuery( domContext ).parents( '[space-id]' ).attr( 'space-id' );
	return spacesTable.spaceViewers[ spaceId ];
}


// show_spaces.js

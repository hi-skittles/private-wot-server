/*
 * Toggle the visibility of table cells with the advanced action menu
 */
function toggleAdvancedOptions()
{
	if (document.pageOptions.showAdvanced.checked)
	{
		jQuery( 'td.advancedMenu' ).css( 'display', 'table-cell' );
	}
	else
	{
		jQuery( 'td.advancedMenu' ).css( 'display', 'none' );
	}
}

function createFilteredView( component, path )
{
	document.location = "/watchers/filtered?" +
			"processes=" + encodeURIComponent( component ) +
			"&path=" + encodeURIComponent( path );
}

// tree.js

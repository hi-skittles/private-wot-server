"use strict"

jQuery.noConflict();

var viewPanel;

jQuery( document ).ready( function()
{
	viewPanel = jQuery( ".trace-viewer-panel" )[0];
	var fileNames = ['/uploads/' + userName + '/' + fileName];

	// initialize tracing viewer component
	tvcm.ui.decorate( viewPanel, tracing.TimelineView );
	loadTraces( fileNames, createViewFromTraces );
});

function createViewFromTraces(fileNames, traces)
{
	var traceModel = new tracing.TraceModel();
	var importTraceProgress = traceModel.importTracesWithProgressDialog(traces,
																	 true);
	importTraceProgress.then(
		function()
		{
			viewPanel.model = traceModel;
			viewPanel.tabIndex = 1;
			if (viewPanel.timeline)
			{
				viewPanel.timeline.focusElement = viewPanel;
			}
			viewPanel.viewTitle = fileNames;
		},
		function( err )
		{
			var overlay = new tvcm.ui.Overlay();
			overlay.textContent = base.normalizeException(err).message;
			overlay.title = 'Import error';
			overlay.visible = true;
		} );
}

function loadTraces( fileNames, onTracesLoaded )
{
	var traces = [];
	for (var i = 0; i < fileNames.length; i++)
	{
		traces.push( undefined );
	}
	var numTracesPending = fileNames.length;

	fileNames.forEach( function( filename, i )
	{
		getAsync( filename, function( trace )
		{
			traces[i] = trace;
			numTracesPending--;
			if (numTracesPending == 0)
			{
				onTracesLoaded( fileNames, traces );
			}
		} );
	});
} 

//just for test, copied from google's example
function getAsync(url, cb)
{
	var req = new XMLHttpRequest();
	var is_binary = /[.]gz$/.test(url) || /[.]zip$/.test(url);
	req.overrideMimeType( 'text/plain; charset=x-user-defined' );
	req.open('GET', url, true);
	if (is_binary)
	{
	  req.responseType = 'arraybuffer';
	}
	
	req.onreadystatechange = function( aEvt )
	{
		if (req.readyState == 4)
		{
			window.setTimeout( function()
			{
			if (req.status == 200)
			{
				cb( is_binary ? req.response : req.responseText );
			} 
			else
			{
				console.log( 'Failed to load ' + url );
			}
			}, 0 );
		}
	};
	req.send( null );
}

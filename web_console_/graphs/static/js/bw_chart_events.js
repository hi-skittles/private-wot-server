"use strict";

/**
*   Singleton object plugin that defines UI behaviour for L{BW.Chart}s.
*/

assert( Dygraph );
assert( Dygraph.Interaction );
assert( Dygraph.Interaction.defaultModel.dblclick );


BW.ChartInteractionModel = BW.ChartInteractionModel
	|| jQuery.extend( {}, Dygraph.Interaction.defaultModel );


BW.ChartInteractionModel.mousedown = function( event, g, context )
{
	BW.ChartInteractionModel.context = context;
	context.initializeMouseDown( event, g, context );
	if ( event.altKey || event.shiftKey )
	{
		Dygraph.startZoom( event, g, context );
	}
	else
	{
		Dygraph.startPan( event, g, context );
	}

	hideValueTooltips();
};


BW.ChartInteractionModel.mouseout = function( event, g, context )
{
	hideValueTooltips();
	
	Dygraph.Interaction.defaultModel.mouseout( event, g, context );
};


BW.ChartInteractionModel.mousemove = function( event, g, context )
{
	BW.ChartInteractionModel.context = context;
	if ( context.isPanning )
	{
		Dygraph.movePan( event, g, context );
	}
	else if ( context.isZooming )
	{
		Dygraph.moveZoom( event, g, context );
	}
	else
	{
		var coords = g.eventToDomCoords( event );
		var canvasX = coords[0];
		var canvasY = coords[1];	
		
		showValueTooltips( g, canvasX, canvasY );
	}
};


BW.ChartInteractionModel.mouseup = function( event, g, context )
{
	BW.ChartInteractionModel.context = context;
	if ( context.isPanning )
	{
		Dygraph.endPan( event, g, context );
	}
	else if ( context.isZooming )
	{
		Dygraph.endZoom( event, g, context );
	}
};


// Take the offset of a mouse event on the dygraph canvas and
// convert it to a pair of percentages from the bottom left.
// ( Not top left, bottom is where the lower value is.)
BW.ChartInteractionModel.offsetToPercentage = function( g, offsetX, offsetY )
{
	// This is calculating the pixel offset of the leftmost date.
	var xOffset = g.toDomCoords( g.xAxisRange()[0], null )[0];
	var yar0 = g.yAxisRange( 0 );

	// This is calculating the pixel of the higest value. ( Top pixel )
	var yOffset = g.toDomCoords( null, yar0[1])[1];

	// x y w and h are relative to the corner of the drawing area,
	// so that the upper corner of the drawing area is ( 0, 0 ).
	var x = offsetX - xOffset;
	var y = offsetY - yOffset;

	// This is computing the rightmost pixel, effectively defining the
	// width.
	var w = g.toDomCoords( g.xAxisRange()[1], null )[0] - xOffset;

	// This is computing the lowest pixel, effectively defining the height.
	var h = g.toDomCoords( null, yar0[0])[1] - yOffset;

	// Percentage from the left.
	var xPct = w == 0 ? 0 : ( x / w );
	// Percentage from the top.
	var yPct = h == 0 ? 0 : ( y / h );

	// The ( 1-) part below changes it from "% distance down from the top"
	// to "% distance up from the bottom".
	return [xPct, ( 1-yPct )];
};


BW.ChartInteractionModel.dblclick = function( event, g, context )
{
	BW.ChartInteractionModel.context = context;
	g.resetZoom();
	
	hideValueTooltips();
};

// BW.ChartInteractionModel.dblclick = Dygraph.Interaction.defaultModel.dblclick;
// function( event, g, context )
// {
// 	// Reducing by 20% makes it 80% the original size, which means
// 	// to restore to original size it must grow by 25%

// 	if (!( event.offsetX && event.offsetY ))
// 	{
// 		event.offsetX = event.layerX - event.target.offsetLeft;
// 		event.offsetY = event.layerY - event.target.offsetTop;
// 	}

// 	var percentages = BW.ChartInteractionModel.offsetToPercentage( g, event.offsetX, event.offsetY );
// 	var xPct = percentages[0];
// 	var yPct = percentages[1];

// 	if ( event.ctrlKey )
// 	{
// 		BW.ChartInteractionModel.zoom( g, -.25, xPct, yPct );
// 	}
// 	else
// 	{
// 		BW.ChartInteractionModel.zoom( g, +.2, xPct, yPct );
// 	}
// };


BW.ChartInteractionModel.click = function( event, g, context )
{
	BW.ChartInteractionModel.context = context;
	Dygraph.cancelEvent( event );
};


BW.ChartInteractionModel.mousewheel = function( event, g, context )
{
	if (!event.shiftKey) return;

	BW.ChartInteractionModel.context = context;
	var normal = event.detail ? event.detail * -1 : event.wheelDelta / 40;
	// For me the normalized value shows 0.075 for one click. If I took
	// that verbatim, it would be a 7.5%.
	var percentage = normal / 50;

	if (!( event.offsetX && event.offsetY ))
	{
		event.offsetX = event.layerX - event.target.offsetLeft;
		event.offsetY = event.layerY - event.target.offsetTop;
	}

	var percentages = BW.ChartInteractionModel.offsetToPercentage( g, event.offsetX, event.offsetY );
	var xPct = percentages[0];
	var yPct = percentages[1];

	BW.ChartInteractionModel.zoom( g, percentage, xPct, yPct );
	Dygraph.cancelEvent( event );
	
	hideValueTooltips();
};


// Adjusts [x, y] toward each other by zoomInPercentage%
// Split it so the left/bottom axis gets xBias/yBias of that change and
// tight/top gets ( 1-xBias )/( 1-yBias ) of that change.
//
// If a bias is missing it splits it down the middle.
BW.ChartInteractionModel.zoom = function( g, zoomInPercentage, xBias, yBias )
{
	xBias = xBias || 0.5;
	yBias = yBias || 0.5;

	function adjustAxis( axis, zoomInPercentage, bias )
	{
		var delta = axis[1] - axis[0];
		var increment = delta * zoomInPercentage;
		var foo = [increment * bias, increment * ( 1-bias )];
		return [ axis[0] + foo[0], axis[1] - foo[1] ];
	}

	// var yAxes = g.yAxisRanges();
	// var newYAxes = [];
	// for ( var i = 0; i < yAxes.length; i++)
	// {
	//	newYAxes[i] = adjustAxis( yAxes[i], zoomInPercentage, yBias );
	// }

	g.updateOptions({
		dateWindow: adjustAxis( g.xAxisRange(), zoomInPercentage, xBias ),
		// valueRange: newYAxes[0]
	});
};

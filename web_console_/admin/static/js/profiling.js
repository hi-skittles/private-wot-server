"use strict";


var MIN_SIZE_PER_SEC = 10;
var MAX_SIZE_PER_SEC = 25;

var disablePage = function()
{
	jQuery( '#startStopButton' ).addClass( "disabled" );
	jQuery( '.profiling-dump-time' ).addClass( "disabled" );
	jQuery( '#statusText' ).html( "Error" );
}

var updateStatus = function()
{
	jQuery.getJSON( "/admin/profilingStatus", function( data )
	{
		if (data == undefined)
		{
			new Alert.Error( "Unable to determine WebConsole self profiling " +
				"status." );
		}

		if (!data.hasOwnProperty( 'isEnabled' ))
		{
			new Alert.Error( "Unable to determine if WebConsole self " +
				"profiling is enabled." );
			disablePage();
			return;
		}

		if (!data.hasOwnProperty( 'statusText' ))
		{
			new Alert.Error( "Unable to determine WebConsole self profiling " +
				"status." );
			disablePage();
			return;
		}

		var startStopButton = jQuery( '#startStopButton' );
		var startStopButtonText = jQuery( '#startStopButtonText' );
		var dumpTimeInput = jQuery( '.profiling-dump-time' );
		if (data.isEnabled == 0)
		{
			startStopButtonText.html( "Start Profiling" );
			startStopButton.removeClass( 'cancel-button' ).addClass(
				'start-button' );
			dumpTimeInput.removeAttr( 'disabled' );
		}
		else
		{
			startStopButtonText.html( "Cancel Profiling" );
			startStopButton.removeClass( 'start-button' ) .addClass(
				'cancel-button' );
			dumpTimeInput.attr( 'disabled', 'disabled' );
		}

		if (jQuery( '#statusText' ).html() == "Completed" && data.statusText
				== "Disabled")
		{
			return;
		}

		jQuery( '#statusText' ).html( data.statusText );

		if (data.hasOwnProperty( 'outputFilePath' ) )
		{
			jQuery( '#outputFilePath' ).html( data.outputFilePath );
		}

		if (data.statusText == "Completed")
		{
			profilingStartStop();
		}
	});
}

var dumpTimeChanged = function( /* number */ warning_dump_time )
{
	var dump_time = Number( jQuery( '.profiling-dump-time' ).val().trim() );
	var profilingError = jQuery( '.dump-time-input-error' );
	var profilingWarning = jQuery( '.dump-time-size-warning' );
	var profilingWarningSeconds = jQuery('.warning-seconds');
	var profilingWarningSize = jQuery('.warning-size');

	if (dump_time == '')
	{
		profilingError.hide();
		profilingWarning.hide();
		jQuery( '#startStopButton' ).addClass( 'disabled' );
	}
	else if (isNaN( dump_time ) || dump_time <= 0)
	{
		profilingError.html( "Invalid dump time" );
		profilingError.show();
		profilingWarning.hide();
		jQuery( '.profiling-dump-time' ).addClass( 'dump-time-text-error' );
		jQuery( '#startStopButton' ).addClass( 'disabled' );
	}
	else
	{
		if (dump_time > warning_dump_time)
		{
			profilingWarningSeconds.html( dump_time );
			profilingWarningSize.html( dump_time * MIN_SIZE_PER_SEC + ' to ' +
					dump_time * MAX_SIZE_PER_SEC );
			profilingError.hide();
			profilingWarning.show();
			jQuery( '.profiling-dump-time' ).addClass( 'dump-time-text-error' );
		}
		else
		{
			profilingError.hide();
			profilingWarning.hide();
			jQuery( '.profiling-dump-time' ).removeClass( 'dump-time-text-error'
					);
		}
		jQuery( '#startStopButton' ).removeClass( 'disabled' );
	}
}

var profilingStartStop = function()
{
	if (jQuery( '#startStopButton' ).hasClass( 'disabled' )) {
		return;
	}
	var dump_time = Number( jQuery( '.profiling-dump-time' ).val().trim() );
	if (isNaN( dump_time ) || dump_time <= 0)
	{
		new Alert.Error( "Unable to record self profiling because the " +
				"dump time provided is invalid." );
		return;
	}

	jQuery.ajax( {
		url: "/admin/profilingStartStop",
		data: { 'dump_time': dump_time },
		dataType: 'json',
		success: function( data )
		{
			if (data == undefined)
			{
				new Alert.Error( "Unable to start WebConsole self profiling." );
				return;
			}

			if (data.hasOwnProperty( 'message' ))
			{
				var alertType = "Warning";

				if (data.hasOwnProperty( 'alertType' ))
				{
					alertType = data.alertType;
				}

				switch (alertType)
				{
					case "Info":
						new Alert.Info( data.message, { duration: 10000 } );
						break;
					case "Warning":
						new Alert.Warning( data.message );
						break;
					case "Error":
						new Alert.Error( data.message );
						break;
					default:
						new Alert.Error( "Alert type " + alertType +
							" unknown. Message:<br>" + data.message );
						break;
				}
			}

			// Ensure the screen picks up any changes from starting/stopping
			updateStatus();

		},
		error: function()
		{
			new Alert.Error( "Unable to start WebConsole self profiling." );
			return;
		}
	} );
}

// Upon screen creation, update the profiling status
updateStatus();

setInterval(function() { updateStatus(); }, 1000);

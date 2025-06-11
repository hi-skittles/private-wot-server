"use strict";

/*
*   Top-level page init and gloval functions/handlers.
*/
console.assert( window.jQuery );

var BW = window.BW || {};
BW.page = BW.page || {};


// set default jquery animation speeds
//jQuery.fx.speeds._default = 350; // msec

// Fade-in constant
// usable as jQuery( element ).fadeIn( "bw_menu_fade_in" );
jQuery.fx.speeds.bw_menu_fade_in = 0; // msec

// Fade-out constant
// usable as jQuery( element ).fadeOut( "bw_menu_fade_out" );
jQuery.fx.speeds.bw_menu_fade_out = 200; // msec


/**
*	Runtime check that given library has been loaded.
*/
BW.require = function( /*String*/ library )
{
	var paths = library.split( '.' );
	var object = window;
	for (var i in paths)
	{
		object = object[paths[i]];
		if (object === undefined)
			throw new Error( "Required lib '" + library + "' not loaded" );
	}
};


/**
*   Page init. This should be the first ready() callback.
*/
jQuery( document ).ready( function()
{
	BW.page.initAjaxErrorHandler();
	BW.page.initInterfaceEvents();
	BW.page.initTouchSupport();
    BW.page.initLoginSupport();
});


/**
*   Sets GLOBAL ajax error callback.
*/
BW.page.initAjaxErrorHandler = function()
{
	jQuery( document ).ajaxError(
		function( ev, xhr, settings, exception )
		{
			if (xhr.bwExceptionHandled)
			{
				return;
			}
			// don't make a fuss about aborted ajax fetches
			if (exception === 'abort')
			{
				console.debug( "(ajax call aborted)" );
				return;
			}

			console.warn(
				"Unhandled ajax error: xhr=%O, settings=%O, except=%O",
				xhr, settings, exception
			);

			if (!xhr.responseText)
			{
				// usually occurs when web_console being restarted
				console.log( "ajax call returned error with no responseText" );
				return;
			}

			var response;
			try
			{
				response = JSON.parse( xhr.responseText );
				console.assert( response.message );
			}
			catch (syntaxError)
			{
				console.warn(
					"Error response not valid JSON: ",
					xhr.responseText.length > 200
					? xhr.responseText.substring( 0, 200 ) + "...(truncated)"
						: xhr.responseText
				);

				response = {
					status: xhr.status,
					message: xhr.responseText || xhr.statusText,
				};
			}

			if (window.Alert)
			{
				new Alert.Error( response.message, { id: true } );
			}
			else
			{
				console.warn( "load alert.js to avoid using alert() in the future" );
				alert( response.message );
			}
		}
	);
};


BW.page.initInterfaceEvents = function()
{
	// left-menu collapse control
	// a click on the show/hide control removes/adds the 'menu-collapsed'
	// state on all "resizable" elements.
	jQuery( '.menu_collapser' ).on( 'click touchend', function()
	{
		if (jQuery( this ).hasClass( 'menu-collapsed' ))
		{
			jQuery( '.resizable' ).removeClass( 'menu-collapsed' );
		}
		else
		{
			jQuery( '.resizable' ).addClass( 'menu-collapsed' );
		}
	});

	// show/hide user menu
	jQuery( document ).on( 'click', '.show-profile.button', function( ev ) {
		BW.user.toggleShowingUserProfile();
	});

	// graceful fade between page changes; hides/distracts from
	// early DOM updates, layout and initialisation artifacts
	jQuery( '.content' ).first().hide().fadeIn( 250 );
	
	// Set up feedback menu button animations
	jQuery( '.navmenu .user-feedback-button' ).on( 'hover', function( e ) {
		if (e.type === 'mouseenter')
		{
			jQuery( e.currentTarget ).animate( { width: '85px' },
				{ duration: 100, queue: false } ).css( 'overflow', 'visible' );

			jQuery( 'span', e.currentTarget ).animate( { opacity: '1',
				left: '25px' }, { duration: 100, queue: false } );
			
		}
		else if (e.type === 'mouseleave')
		{
			jQuery( e.currentTarget ).animate( { width: '30px' }, 
				{ duration: 100, queue: false } ).css( 'overflow', 'visible' );

			jQuery( 'span', e.currentTarget ).animate( { opacity: '0',
				left: '-40px' }, { duration: 100, queue: false } );
		}
	});
};


BW.page.initTouchSupport = function()
{
	if ('ontouchstart' in window)
	{
		jQuery.getScript( '/static/third_party/jquery.hammer.js', function() {
			console.log( "loaded touch support" );
		});

		jQuery( 'html' ).addClass( 'touch-enabled' );
	}
};

BW.page.initLoginSupport = function()
{
    var loginErrorAlert = null;

    jQuery( document ).on( 'submit', '#loginForm', function ()
    {
        if ( loginErrorAlert && loginErrorAlert.isVisible() )
        {
            loginErrorAlert.dismiss();
        }
        var submitButton = jQuery( 'input[type=submit]', this );
        submitButton.attr( 'disabled', 'disabled' );
        jQuery.ajax( {
            url: jQuery( this ).attr( 'action' ),
            type: jQuery( this ).attr( 'method' ),
            dataType: 'json',
            data: jQuery( this ).serialize(),
            success: function ( data ) {
                location.reload();
            },
            error: function ( xhr, status, error )
            {
                var msg = null;
                try
                {
                    msg = jQuery.parseJSON( xhr.responseText )['message'];
                }
                catch ( e )
                {
                    msg = null;
                }
                msg = msg || 'Login failed';

                if ( !!window.Alert )
                {
                    // Can remove this append once the alerts are refactored
                    // as part of BWT-24156
                    if ( !jQuery( '.alert-notification-container' ).length )
                    {
                        var alertDiv = jQuery( '<div/>' );
                        alertDiv.addClass( 'alert-notification-container' );
                        alertDiv.css( { top: 0, right: '6px' } );
                        alertDiv.appendTo( '#main' );
                    }

                    // Create the alert, but make sure we only see one
                    // at a time
                    if ( loginErrorAlert && loginErrorAlert.isVisible() )
                    {
                        jQuery( loginErrorAlert ).on( 'dismiss.alert',
                                                      function () {
                            loginErrorAlert = new Alert.Error( msg,
                                                               { duration: 0 });
                        });
                        loginErrorAlert.dismiss();
                    }
                    else
                    {
                        loginErrorAlert = new Alert.Error( msg,
                                                           { duration: 0 } );
                    }
                }
                else
                {
                    console.warn( "alert.js not loaded. Login failure info: %s",
                                    msg );
                    alert( msg );
                }
                submitButton.removeAttr( 'disabled' );
                jQuery( '#username' ).select();
            }
        });
        return false;
    });
};

BW.page.showVersionInfo = function()
{
	return jQuery.getJSON( "/version", function( /*Object*/ data )
	{
		var isAlertLibraryLoaded = !!window.Alert;
		var messageString = "BigWorld WebConsole ";
		var buildKnown = false;
		var breakString = "\x3Cbr\x3E"; // <br>

		if (!isAlertLibraryLoaded)
		{
			// using console, no line break
			breakString = " ";
		}

		if (!data)
		{
			var errMsg = "Unable to access version information";
			if (window.Alert)
			{
				new Alert.error( errMsg );
			}
			else
			{
				console.warn( errMsg );
			}
			return true;
		}

		if (data.versionNumber)
		{
			messageString += "Version " + data.versionNumber;
		}

		messageString += breakString + "Build: ";

		if (data.packageType)
		{
			buildKnown = true;
			messageString += data.packageType + " ";
		}

		if (data.repositoryType)
		{
			buildKnown = true;
			messageString += data.repositoryType + " ";
		}

		if (data.revisionNumber)
		{
			buildKnown = true;
			messageString += "Revision " + data.revisionNumber;
		}

		if (data.modStatus)
		{
			buildKnown = true;
			messageString += "(" + data.modStatus + ")";
		}

		if (!buildKnown)
		{
			messageString += "Unknown";
		}

		if (isAlertLibraryLoaded)
		{
			// filthy hack to make sure there is a div in the DOM to receive
			// alerts. default container class name comes from
			// `DEFAULT_OPTIONS.targetDiv` in alert.js.
			//
			// this conditional should be removed if/when any remaining
			// table-based layout pages (layout.kid) get ported to layout_css.kid.
            //
            // Update: still required for numerous pages even after removal
            // of layout.kid, but can be removed once the alerts are refactored
            // as part of BWT-24156
			//
			if (!jQuery( '.alert-notification-container' ).length)
			{
				console.warn(
					"NOTE: page does not define a .alert-notification-container: "
					+ "adding one to #main. "
				);

				var alertContainer = jQuery( '<div/>' );
				alertContainer.addClass( 'alert-notification-container' );
				alertContainer.css({ top: 0, right: '6px' });
				alertContainer.appendTo( '#main' );
			}

			new Alert.Info( messageString, { duration: 10000 } );
		}
		else
		{
			console.dir( data );
			console.warn( "alert.js not loaded. Version info: %s", messageString );
			alert( messageString );
		}
	});
};

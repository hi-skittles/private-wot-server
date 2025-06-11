
if (!jQuery) throw new Error( "required jquery library is not loaded" );

/**
Lightweight and flexible alert notification class.

Example usage:

	// basic messages
	new Alert( "some message" ); // all defaults

	new Alert.Info( "message" );
	new Alert.Warning( "message" );
	new Alert.Error( "message" );

	// indivualised config
	new Alert( "some message", {
		duration: 30000,
		dimissable: false,
		targetDiv: ".your-div"
	});

	// chained alerts
	var warning = new Alert.Warning( "blah" );
	jQuery( warning ).on( 'dismiss.alert', function() {
		new Alert.Info( "secondary alert" );
	});

	// programmatically dismiss an alert
	warning.dismiss();

	// named alerts; only 1 instance of specific message ever shown
	new Alert( "Server is down", { id: 'alert-server-down' });
	Alert.dismiss( 'alert-server-down' );

*/
var Alert = function( message, options )
{
	// permit simple subclassing
	if (arguments.length == 0) return;

	var opts = jQuery.extend( {}, Alert.Default_Options, options );
	var alert;

	// if given an id, check to see if alert with that css class already
	// exists in target container element (and is visible).
	if (opts.id)
	{
		if (opts.id === true)
		{
			// auto-generate an ID
			opts.id = Alert.getIdForMessage( message );
		}

		alert = jQuery( "." + opts.id + ":visible", opts.targetDiv );
		if (alert.length && alert.hasClass( opts.cssClass ))
		{
			// then a visible DOM element exists for this alert,
			// so no need to re-create, just update and return.

			if (opts.debug)
			{
				console.log( "alert '%s' already exists in %s", opts.id, opts.targetDiv );
			}
			this.jquery = alert;
			this.opts = opts;
			this._timer = alert.attr( 'timer' );

			// overwrite existing message
			if (message)
			{
				alert.html( message );
			}

			this.show();
			return;
		}
	}

	if (!message) throw new Error( "No message passed" );

	this.opts = opts;
	this._created = +new Date;

	alert = this.jquery = jQuery( '<div/>' );

	alert.addClass( opts.defaultCss + ' ' + opts.cssClass );
	if (opts.id) alert.addClass( opts.id );
	alert.html( message );

	// dismissable = false means client needs to remove alert themselves
	if (opts.dismissable)
	{
		alert.on( 'click', this.dismiss.bind( this ) );

		// add dismissable attribute to facillitate CSS styling
		alert.attr( 'dismissable', 'true' );
	}

	// prevent an alert from disappearing if user mouses over it
	alert.on( 'mouseover', function()
	{
		if (this._timer)
		{
			window.clearTimeout( this._timer );
			this._timer = null;
		}
	}.bind( this ));

	// reinstate duration if user mouses out
	alert.on( 'mouseout', this.touch.bind( this ));

	jQuery( opts.targetDiv ).append( alert );

	this.show();
};


/** Attach events to alert and make visible. */
Alert.prototype.show = function()
{
	this.jquery.fadeIn(  this.opts.fadeIn, this.touch.bind( this ) );
};


/** Sets (or resets) show duration. No timer set if alert has duration set to 0. */
Alert.prototype.touch = function()
{
	if (this._timer)
	{
		window.clearTimeout( this._timer );
		this._timer = null;
	}

	if (!this.opts.duration)
	{
		return;
	}

	this._timer = window.setTimeout( this.dismiss.bind( this ), this.opts.duration );
	this.jquery.attr( 'timer', this._timer );
};


/** Gracefully dismiss an alert, triggers the 'dismiss.alert' event. */
Alert.prototype.dismiss = function()
{
	if (this.jquery)
	{
		this.jquery.fadeOut( this.opts.fadeOut / 2,
			function()
			{
				jQuery( this ).triggerHandler( 'dismiss.alert' );
				this._destroy();
			}
			.bind( this )
		);
	}
};


/**
*   Remove an alert immediately from DOM as well as any/all attached events.
*   Called routinely for all alerts at the end of their lifecycle to break any
*   potential cyclic references or stray references to DOM objects. Triggers
*   the 'expire.alert' event.
*/
Alert.prototype._destroy = function()
{
	if (this._timer)
	{
		window.clearTimeout( this._timer );
		this._timer = null;
	}

	if (this.jquery)
	{
		this.jquery.remove();
		this.jquery = null;
		jQuery( this ).triggerHandler( 'expire.alert' );
	}
};


/**
*   True if the current alert occupies screen space in the DOM.
*   See also: http://api.jquery.com/visible-selector
*/
Alert.prototype.isVisible = function()
{
	return (this.jquery && this.jquery.is( ':visible' ));
};


/* Class/convenience methods */

/** Create an alert (DOM) identifier from given message text. */
Alert.getIdForMessage = function( message )
{
	// simple hashing function, see:
	// http://stackoverflow.com/a/8831937/1199298
	var hash = 0;
	if (message.length === 0)
	{
		return hash;
	}

	var c;
	for (var i = 0; i < message.length; i++)
	{
		c = message.charCodeAt( i );
		hash = ((hash << 5) - hash) + c;
		hash = hash & hash; // Convert to 32bit int
	}

	return 'alert-' + hash;
};


/**
*   Convenience method to obtain a reference to an Alert with given
*   identifier in the given dom container (or current document if not given).
*
*   Note: class method, must be called as Alert.forName( ... ).
*/
Alert.forName = function( /*string*/ id, /*optional*/ domContainer )
{
	var jquery = jQuery( '.' + id, domContainer );
	if (jquery.length === 0)
	{
		return null;
	}

	var a = new Alert(); // null, { id: id } );
	a.jquery = jquery;
	a.opts = Alert.Default_Options;

	return a;
};


/**
*   Convenience method to check whether an Alert with given id exists and
*   is visible in the given dom container (or current document if not given).
*/
Alert.isVisible = function( /*string*/ id, domContainer )
{
	var a = Alert.forName( id, domContainer );
	return (a && a.isVisible());
};


/**
*   Convenience method to dismiss an Alert with given id; no effect if an
*   alert with given id is not in given DOM container (or current document).
*/
Alert.dismiss = function( /*string*/ id, domContainer )
{
	var a = Alert.forName( id, domContainer );
	if (a && a.isVisible())
	{
		a.dismiss();
	}
};


/* class Alert.Info extends Alert */

Alert.Info = function( message, options )
{
	var opts = jQuery.extend( {}, Alert.Info.Default_Options, options );
	Alert.call( this, message, opts );
};

Alert.Info.extends( Alert );

/* class Alert.Warning extends Alert */

Alert.Warning = function( message, options )
{
	var opts = jQuery.extend( {}, Alert.Warning.Default_Options, options );
	Alert.call( this, message, opts );
};

Alert.Warning.extends( Alert );


/* class Alert.Error extends Alert */

Alert.Error = function( message, options )
{
	var opts = jQuery.extend( {}, Alert.Error.Default_Options, options );
	Alert.call( this, message, opts );
};

Alert.Error.extends( Alert );

/* default config */

/** Default constructor options */
Alert.Default_Options = {

	// id for an alert.
	//
	// if id == a boolean false expression, the alert is not a singleton, so
	// multiple alerts with the same message will appear.
	//
	// if id == a string, the string becomes the unique id for the alert,
	// that is, only 1 instance will ever appear per alert container.
	//
	// if id === true, it means an id will be derived from the passed message;
	// no other alerts with the exact same message will appear.
	id: true,

	// CSS class(es) to append to class list for this Alert, space-separated
	cssClass: 'alert-severity-info',

	// target DOM node; must be either a jQuery object, selector String, or DOM node
	targetDiv: '.alert-notification-container',

	// default CSS class to append to class list (intended to be overriden by subclasses)
	defaultCss: 'alert-notification',

	fadeIn: 100,    // msec
	duration: 5000, // msec
	fadeOut: 200,   // msec

	// whether a user can dismiss this message
	dismissable: true,
};

/** Default constructor options for an Alert.Info */
Alert.Info.Default_Options = {
	cssClass: "alert-severity-info"
};

/** Default constructor options for an Alert.Warning */
Alert.Warning.Default_Options = {
	cssClass: "alert-severity-warning"
};

/** Default constructor options for an Alert.Error */
Alert.Error.Default_Options = {
	cssClass: "alert-severity-error",
	duration: 0,
};


// alert.js

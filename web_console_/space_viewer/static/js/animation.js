"use strict";


/**
*   Implementation of Bezier curves with P0 locked at (0, 0) and
*   P3 locked at (1, 1). See: http://en.wikipedia.org/wiki/Bezier_curve
*
*   Usage:
*       var spline = new BezierSpline( 0.25, 0.1, 0.25, 1.0 )
*       spline.get( x ) // returns y at x. x must be 0 - 1.
*/
var BezierSpline = function( x1, y1, x2, y2 )
{
	// only publicly exposed method
	this.get = function( x )
	{
		if (x1 == y1 && x2 == y2)
		{
			return x; // linear
		}
		return calcBezier( getTforX( x ), y1, y2 );
	}

	// private/internal methods below here
	function A( a1, a2 ) { return 1 - 3 * a2 + 3 * a1; }
	function B( a1, a2 ) { return 3 * a2 - 6 * a1; }
	function C( a1 ) { return 3 * a1; }

	// Returns x(t) given t, x1, and x2, or y(t) given t, y1, and y2.
	function calcBezier( t, a1, a2 )
	{
		return ((A( a1, a2 ) * t + B( a1, a2 )) * t + C( a1 )) * t;
	}

	// Returns dx/dt given t, x1, and x2, or dy/dt given t, y1, and y2.
	function getSlope( t, a1, a2 )
	{
		return 3 * A( a1, a2 ) * t * t + 2 * B( a1, a2 ) * t + C( a1 );
	}

	function getTforX( x )
	{
		// Newton raphson iteration
		var approxT = x;
		for (var i = 0; i < 4; ++i)
		{
			var currentSlope = getSlope( approxT, x1, x2 );
			if (currentSlope == 0)
			{
				return approxT;
			}
			var currentX = calcBezier( approxT, x1, x2 ) - x;
			approxT -= currentX / currentSlope;
		}
		return approxT;
	}
};


/**
*   Base class for implementing changes over time.
*/
var Animation = function( options )
{
	if (typeof options === 'object')
	{
		for (var key in options)
		{
			this[key] = options[key];
		}
	}
	else if (typeof options === 'function')
	{
		this.renderFrame = options;
	}
	else return;

	if (!this.id)
	{
		if (!Animation.nextAnimationId)
		{
			Animation.nextAnimationId = 0;
		}
		this.id = "animation_" + ++Animation.nextAnimationId;
	}

	if (this.debug)
	{
		jQuery( this ).on('start.animation stop.animation end.animation',
			function( ev )
			{
				console.log( this.timeElapsed + ": " + this.id + " " + ev.type );
			}
		);
	}
};


/**
*   Named animation transition functions. These names/functions match the
*   standard values for the CSS3 'transition-timing-function' property.
*/
Animation.Fx =
{
	linear: new BezierSpline( 0, 0, 1.0, 1.0 ),
	ease: new BezierSpline( 0.25, 0.1, 0.25, 1.0 ),
	easeIn: new BezierSpline( 0.42, 0, 1.0, 1.0 ),
	easeOut: new BezierSpline( 0, 0, 0.58, 1.0 ),
	easeInOut: new BezierSpline( 0.42, 0.0, 0.58, 1.0 ),
	extremeEaseIn: new function() { this.get = function( x ) { return Math.pow( x, 3 ) }},
};


// Object definition
Animation.prototype =
{
	debug: 0,


	/** Duration of animation. Set to Infinity for continuous animations. */
	duration: 100, // msec


	/** FPS limit. Note that actual FPS is likely to be lower than this value. */
	targetFps: Infinity, // unlimited


	/**
	*   Animation transition function; must provide a method with the
	*   called 'get' which accepts a float in range( 0, 1 ) and returns
	*   a float in range( 0, 1 ).
	*/
	transition: Animation.Fx.easeIn,


	/** Time in msec since animation was started. */
	timeElapsed: 0,


	/**
	*   Called once animation has started (from play()) but before the first
	*   frame has been rendered.
	*/
	beforeFirstFrame: function ( animation ) { /* do nothing */ },


	/**
	*   Render one frame of this Animation. Default implementation
	*   does nothing; it's intended to be overridden.
	*/
	renderFrame: function( animation )
	{
		// Do nothing useful; clients of this class are expected to
		// override this method.
		// Default implementation for debugging purposes only.

		console.log( this.timeElapsed + ": " + this.id +
		   " renderFrame, fps=" + this.fps );
	},


	/**
	*   Renders the final frame of a timed animation (ie: those with a
	*   finite duration). Default implementation does nothing; it's
	*   intended to be overridden.
	*/
	finalFrame: function( animation ) { /* do nothing */ },


	/** Average FPS since this animation started. */
	get fps()
	{
		if (!this.timeElapsed || !this.duration)
		{
			return 0;
		}
		return 1000 * this.frame / this.timeElapsed;
	},


	/** Progress ratio (0-1.0) modified by the current transition property. */
	get progress()
	{
		var elapsed = this.timeElapsed;
		var duration = this.duration;
		if (!elapsed || !duration)
		{
			return 0;
		}

		var progress = Math.min( 1, elapsed / duration );
		return this.transition.get( progress );
	},


	/** Begin playing this animation. */
	play: function( /*optional Object*/ animationTarget )
	{
		animationTarget = animationTarget || this;
		this.frameTime = this.startTime = performance.now();
		var duration = this.duration;
		this.timeElapsed = 0;
		this.frame = 0;
		var timeDelta;

		// 980 gives an actual FPS closer to targetFps
		var msecPerFrame = 980 / this.targetFps;

		var animation = this;

		this.animationFrame = function( timestamp )
		{
			if (!animation.inProgress)
			{
				return;
			}
			timeDelta = timestamp - animation.frameTime;
			animation.timeElapsed = timestamp - animation.startTime;

			//	throttle down to targetFps
			if (animation.timeElapsed < duration && timeDelta < msecPerFrame)
			{
				animation.requestFrame();
				return;
			}

			animation.frameTime = timestamp;
			animation.progressDelta = Math.min( 1, timeDelta / duration ) ;
			animation.timeDelta = timeDelta;
			animation.frame++;

			if (animation.timeElapsed < duration)
			{
				animation.requestFrame();
				animation.renderFrame.call( animationTarget, animation );
			}
			else
			{
				// animation.renderFrame.call( target, animation );
				animation.finalFrame.call( animationTarget, animation );
				jQuery( animation ).trigger("end.animation");
				animation.inProgress = false;
			}
		};

		this.beforeFirstFrame.call( animationTarget, this );
		this.requestFrame();
		jQuery( this ).trigger("start.animation");
	},


	/** Stop (pause) this animation. */
	stop: function()
	{
		if (!this.inProgress)
		{
			return;
		}

		if (this._id)
		{
			cancelAnimationFrame( this._id );
			this._id = null;
		}

		this.inProgress = false;
		jQuery( this ).trigger("stop.animation");
	},


	clone: function()
	{
		return new Animation( this );
	},


	playAfter: function( animation )
	{
		var copy = animation.clone();
		var _this = this;
		jQuery( copy ).on( 'end.animation', function()
			{
				_this.play();
			});
		// copy.id += "-" + this.id;
		return copy;
	},


	requestFrame: function()
	{
		this.inProgress = true;
		this._id = requestAnimationFrame( this.animationFrame );
	},


	log: function()
	{
		console.log( arguments );
	}
};


// currently unused; may become useful in near future so leaving in for now.
/*
var SimpleAnimation = function( options )
{
	if (options.renderFrame)
	{
		options._renderFrame = options.renderFrame;
		delete options.renderFrame;
	}

	if (options.finalFrame)
	{
		options._finalFrame = options.finalFrame;
		delete options.finalFrame;
	}

	if (options.target)
	{
		options._target = options.target;
		delete options.target;
	}

	Animation.call( this, options );

	if (! (this.properties instanceof Array))
	{
		throw new Error("Expected an array argument for 'properties' property");
	}

	if (! (this.values instanceof Array))
	{
		throw new Error("Expected an array argument for 'values' property");
	}

	if (this.properties.length !== this.values.length)
	{
		throw new Error("'properties' and 'values' properties must be equal length");
	}

	var initialValues = this.initialValues = [];
	var deltaValues = this.deltaValues = [];
	var props = this.properties;
	var values = this.values;
	var target = this._target;
	var initialValue;

	for (var i in props)
	{
		initialValue = target[ props[i] ];
		if (this.debug)
		{
			console.log( "initial value of property '%s'=",
				props[i], initialValue );
		}
		if (initialValue === undefined)
		{
			throw new Error(
				"Initial value of property '" + props[i] + "' cannot be undefined"
			);
		}
		if (values[i] === undefined)
		{
			throw new Error(
				"Target value of property '" + props[i] + "' cannot be undefined"
			);
		}
		initialValues.push( initialValue );
		deltaValues.push( values[i] - initialValue );
	}

	if (this.debug)
	{
		for (var i in props)
		{
			console.log("property " + props[i] +
				": initialValue=" + initialValues[i] +
				", targetValue=" + values[i] +
				", deltaValue=" + deltaValues[i]
			);
		}
	}
};


SimpleAnimation.prototype = new Animation;
SimpleAnimation.prototype.constructor = SimpleAnimation;


SimpleAnimation.prototype._renderFrame =
SimpleAnimation.prototype._finalFrame = function() { }; // do nothing

SimpleAnimation.prototype.renderFrame = function( animation )
{
	var delta = animation.progressDelta;
	if (!delta)
	{
		return;
	}
	if (delta > 1)
	{
		if (this.debug)
		{
			this.log( "delta > 1, dropping frame" );
		}
		return;
	}

	var initialValues = this.initialValues;
	var deltaValues = this.deltaValues;
	var props = this.properties;
	var target = this._target;

	for (var i in props)
	{
		var newVal = initialValues[i] + deltaValues[i] * delta;
		if (this.debug)
		{
			this.log( props[i] + ": " + target[ props[i] ] + " -> " + newVal );
		}
		target[ props[i] ] = newVal;
	}

	this._renderFrame.call( target, animation );
};


SimpleAnimation.prototype.finalFrame = function( animation )
{
	var finalValues = this.values;
	var props = this.properties;
	var target = this._target;

	for (var i = 0; i < props.length; i++)
	{
		target[ props[i] ] = finalValues[i];
	}

	this._finalFrame.call( target, animation );
};
*/

// Animation.js


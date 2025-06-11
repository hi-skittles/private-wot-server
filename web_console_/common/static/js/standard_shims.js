/**
 *	 Fallback implementations of (now) standard javascript functions.
 *
 *	 See http://kangax.github.com/es5-compat-table/ for a support matrix.
 */


/** Object.keys */
if (!Object.keys)
{
	console.warn("browser does not support Object.keys, using shim");
	Object.keys = (function ()
	{
		var hasOwnProperty = Object.prototype.hasOwnProperty;
		var hasDontEnumBug = !({toString: null}).propertyIsEnumerable( 'toString' );
		var dontEnums = [
			'toString',
			'toLocaleString',
			'valueOf',
			'hasOwnProperty',
			'isPrototypeOf',
			'propertyIsEnumerable',
			'constructor'
		];
		var dontEnumsLength = dontEnums.length;

		return function (obj)
		{
			if (typeof obj !== 'object' && typeof obj !== 'function' || obj === null)
			{
				throw new TypeError('Object.keys called on non-object');
			}

			var result = [];

			for (var prop in obj)
			{
				if (hasOwnProperty.call( obj, prop ))
				{
					result.push( prop );
				}
			}

			if (hasDontEnumBug)
			{
				for (var i = 0; i < dontEnumsLength; i++)
				{
					if (hasOwnProperty.call( obj, dontEnums[i] ))
					{
						result.push( dontEnums[i] );
					}
				}
			}
			return result
		};
	})();
};


/** Function.bind shim */
if (!Function.prototype.bind)
{
	console.warn("browser does not support Function.bind, using shim");
	Function.prototype.bind = function( intendedThis )
	{
		if (typeof this !== "function")
		{
			throw new TypeError(
				"Function.prototype.bind: Argument to be bound is not callable");
		}

		var aArgs = Array.prototype.slice.call( arguments, 1 );
		var functionToBind = this;
		var noopFunc = function() {};

		var boundFunction = function ()
		{
			return functionToBind.apply(
				this instanceof noopFunc ? this : intendedThis,
				aArgs.concat( Array.prototype.slice.call( arguments ) )
				);
		};

		noopFunc.prototype = this.prototype;
		boundFunction.prototype = new noopFunc();

		return boundFunction;
	};
}



/*~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ performance.now ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~*/

if (!window.performance)
{
	console.warn( "using performance shim" );
	window.performance = {};
}

performance.now = (function() {
	return performance.now	  ||
		performance.mozNow	  ||
		performance.msNow	  ||
		performance.oNow	  ||
		performance.webkitNow ||
		function() { return new Date().getTime(); };
})();


/*~~~~~~~~~~~~~~ requestAnimationFrame and cancelAnimationFrame ~~~~~~~~~~~~~~~~~*/

window.requestAnimationFrame =
	window.requestAnimationFrame ||
	window.webkitRequestAnimationFrame ||
	window.mozRequestAnimationFrame ||
	window.oRequestAnimationFrame ||
	window.msRequestAnimationFrame ||
	(function() {
			console.warn( "using requestAnimationFrame shim" );

			var lastTime = 0;
			return function( callback, element ) {
				var currTime = new Date().getTime();
				var timeToCall = Math.max( 0, 16 - (currTime - lastTime) );
				var id = window.setTimeout(
					function() { callback( currTime + timeToCall ); }, timeToCall );
				lastTime = currTime + timeToCall;

				return id;
			};
	}());


window.cancelAnimationFrame =
		window.cancelAnimationFrame ||
		window.webkitCancelAnimationFrame ||
		window.mozCancelAnimationFrame ||
		window.oCancelAnimationFrame ||
		window.msCancelAnimationFrame ||
		window.clearTimeout;


/*~~~~~~~~~~~~~~~ Other useful enhancements to core classes ~~~~~~~~~~~~~~~~~~~~~*/

if (!window.assert)
{
	window.assert = function( expr )
	{
		if (!expr)
		{
			if (arguments.length > 1)
			{
				var args = Array.prototype.slice.apply( arguments ).slice( 1 );
				args[0] = "Assertion failed: " + args[0];

				console.error.apply( console, args );
			}
			else
			{
				console.error( "Assertion failed" );
			}
			if (window.BW && BW.ASSERTIONS_ARE_FATAL)
			{
				throw new Error(
					"Assertion is fatal. " +
					"Make non-fatal by assigning a false value to " +
					"'BW.ASSERTIONS_ARE_FATAL'."
				);
			}
		}
	};

	if (!console.assert)
	{
		console.warn( "using console.assert shim" );
		console.assert = assert;
	}
}


String.prototype.escapeHtml = function()
{
	return ( this
		.replace( /&/g, "&amp;" )
		.replace( /</g, "&lt;"  )
		.replace( />/g, "&gt;"  )
		.replace( /"/g, "&quot;" )
		.replace( /'/g, "&apos;" )
	);
};


/**
*	Splits this String sequentially by the given delimiters, returning an Object.
*	Delimiters default to `/[&;]/` and `=`. For example:
*
*		"xxx=111&yyy=222&yyy=333".toMap()
*
*	would return `{ xxx: [111], yyy: [222, 333] }`. Note that without arguments,
*	values in the returned Object will each have been URL-decoded by
*	`decodeURIComponent` for the common use case:
*
*		document.location.search.substring( 1 ).toMap()
*
*	to convert a URL query string into a map of parameters.
*/
String.prototype.toMap = function( /*String|RegExp?*/ delim1, /*String|RegExp?*/ delim2 )
{
	if (!this.length) return {};

	delim1 = delim1 || /&|;/;
	delim2 = delim2 || '=';

	var paramsAndValues = this.split( delim1 );
	var map = {};

	for (var i = 0; i < paramsAndValues.length; i++)
	{
		var j = paramsAndValues[i].indexOf( delim2 );
		var paramAndValue = j > 0
			? [paramsAndValues[i].slice( 0, j ), paramsAndValues[i].slice( j + delim2.length )]
			: [paramsAndValues[i], undefined];
		var paramValue = arguments.length
			? window.decodeURIComponent( paramAndValue[1] )
			: paramAndValue[1];

		if (paramAndValue[0] in map)
		{
			map[ paramAndValue[0] ].push( paramValue );
		}
		else
		{
			map[ paramAndValue[0] ] = [ paramValue ];
		}
	}

	return map;
};

String.prototype.toMap.DEFAULT_DELIM1 = /&|;/;
String.prototype.toMap.DEFAULT_DELIM2 = '=';

/**
*	Returns a new String consisting of this String repeated the given
*	number of times. Returns '' for integer values < 1, and throws Error
*	on undefined or Infinity.
*/
String.prototype.repeat = function( /*int*/ times )
{
	if (times === undefined || times === Infinity)
		throw new Error( "Invalid argument: " + times );

	if (times < 1)
		return '';

	if (times == 1)
		return this.toString();

	var n = 1;
	var s = "";
	var string = this;

	while ((n << 1) <= times)
	{
		if (times & n)
			s += string;

		string += string;
		n <<= 1;
	}

	return s + string;
};


Number.prototype.leftPadZeros = function( /*int*/ desiredLen )
{
	var numZeros = desiredLen - String( this ).length;
	if (numZeros > 0)
	{
		return "0".repeat( numZeros ) + String( this );
	}
	else
	{
		return String( this );
	}
};


/**
*	Produces dates of form "Wed 27 Mar 2013 16:28:26.147" in the local timezone.
*/
Date.prototype.toBigWorldDateString = function( /*boolean*/ showMillisecs )
{
	if (showMillisecs === undefined)
	{
		showMillisecs = true;
	}

	return [ 'Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat' ][ this.getDay() ] +
		' ' +
		this.getDate() +
		' ' +
		[ 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
		  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec' ][ this.getMonth() ] +
		' ' +
		this.getFullYear() +
		' ' +
		this.getHours().leftPadZeros( 2 ) +
		':' +
		this.getMinutes().leftPadZeros( 2 ) +
		':' +
		this.getSeconds().leftPadZeros( 2 ) +
		(showMillisecs ? ('.' + this.getMilliseconds().leftPadZeros( 3 )) : '')
	;
};


Function.prototype.extends = function( /*Function*/ superclass )
{
	this.prototype = new superclass;
	this.prototype.constructor = this;
};


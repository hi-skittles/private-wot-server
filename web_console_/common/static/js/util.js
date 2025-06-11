/* namespace */ var Util =
{

	error: function( err, lines )
	{
		Util.showDialog( "ERROR", err, lines );
	},

	warning: function( err, lines )
	{
		Util.showDialog( "WARNING", err, lines );
	},

	info: function( msg, lines )
	{
		Util.showDialog( "INFO", msg, lines );
	},

	showDialog: function( level, err, lines )
	{
		var text = level + ": " + err;

		if (lines)
		{
			text += "\n\n";
			for (var i in lines)
				text += lines[i] + "\n";
		}

		window.alert( text );
	},

	errorWindow: function( lines )
	{
		var win = window.open( "/error" );

		var insertErrors = function ()
		{
			var root = win.document.getElementById( "errors" );
			for (var i in lines)
				root.innerHTML += "<pre>" + lines[i] + "</pre>";
		}

		win.addEventListener( "load", insertErrors, true );
		return win;
	},

	dump: function( obj )
	{
		for (var i in obj)
			log( i + ": " + obj[i] );
	},

	toggleVisibility: function( elem1name, elem2name )
	{
		var elem1 = getElement( elem1name );
		var elem2 = getElement( elem2name );

		if (elem1.style.visibility == "hidden")
		{
			elem1.style.visibility = "visible";
			elem1.style.display = "block";
			elem2.style.visibility = "hidden";
			elem2.style.display = "none";
		} else
		{
			elem1.style.visibility = "hidden";
			elem1.style.display = "none";
			elem2.style.visibility = "visible";
			elem2.style.display = "block";
		}
	},

	/**
	 *  Do a dynamic JavaScript include.
	 */
	include: function( url )
	{
		if (Util.includes.indexOf( url ) == -1)
		{
			var script = document.createElement( "script" );
			script.type = "text/javascript";
			script.src = url;
			document.getElementsByTagName( "head" )[0].appendChild( script );
		}
	},

	includes: []
};

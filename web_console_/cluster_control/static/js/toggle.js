/* namespace */ var Toggle =
{
	timerid: -1,
	layout: new Object(),
	lastUpdate: null,

	// Populates the table on the page with info from an update from the server
	display: function()
	{
		for (var process in Toggle.pnames)
		{
			var procDetails = "";
			var dead = 0;
			var nomachine = 0;
			var running = 0;
			var registered = 0;

			// Each entry has the following format
			//  [0] - machine name
			//  [1] - process name (eg: dbapp)
			//  [2] - PID
			//  [3] - process status (eg: registered, dead)
			//  [4] - process status details (currently only used by dbapp)
			for (var entry in Toggle.layout)
			{
				// Check if the entry matches the current process
				if (Toggle.pnames[ process ] == Toggle.layout[ entry ][ 1 ])
				{
					// Update the status if there is anything
					procDetails = Toggle.layout[ entry ][ 4 ];

					// This is a carry over kludge from the old script which
					// avoids a big conditional block. It effectively
					// evaluates to something like "registered"++
					eval( Toggle.layout[ entry ][ 3 ] + "++" );
				}
			}

			// Now we have the details, update the webpage

			// If see a "nomachine" status, this update is bogus (and
			// won't be the last) so it's OK to throw it away.
			if (nomachine > 0)
			{
				$(Toggle.pnames[ process ] + "_dead").innerHTML = "?";
				$(Toggle.pnames[ process ] + "_running").innerHTML = "?";
				$(Toggle.pnames[ process ] + "_registered").innerHTML = "?";
				$(Toggle.pnames[ process ] + "_details").innerHTML = "";
				continue;
			}

			// We always want to update the process details, regardless of the
			// process count updates.
			$(Toggle.pnames[ process ] + "_details").innerHTML = procDetails;

			// Color in the row header with the leftmost non-zero entry
			var style;
			if (dead > 0)
			{
				style = "color: red";
			}
			else if (running > 0)
			{
				style = "color: orange";
			}
			else if (registered > 0)
			{
				style = "color: green";
			}
			else
			{
				// If all process counts have fallen to 0, don't perform any
				// further updates, as we are now receiving layout updates
				// that will over-write the last valid state of the server.
				continue;
			}

			$(Toggle.pnames[ process ] + "_dead").innerHTML = dead;
			$(Toggle.pnames[ process ] + "_running").innerHTML = running;
			$(Toggle.pnames[ process ] + "_registered").innerHTML = registered;
			$(Toggle.pnames[ process ] + "_header").setAttribute( "style", style );
		}
	},

	follow: function()
	{
		var onUpdate = function( state, data )
		{
			if (state == "status")
			{
				Toggle.layout = data.layout;
				Toggle.display();
				Toggle.lastUpdate = data.layout;
			}
		};

		var onFinished = function()
		{
			// Figure out whether or not it actually worked
			var success = true;
			if (Toggle.lastUpdate != null)
			{
				for (var i in Toggle.lastUpdate)
				{
					if ((Toggle.action == "start" || Toggle.action == "restart") &&
						Toggle.lastUpdate[i][3] == "dead")
					{
						success = false;
					}

					if (Toggle.action == "stop" &&
						Toggle.lastUpdate[i][3] != "dead")
					{
						success = false;
					}
				}
			}

			if (success)
			{
				window.location = "procs";
			}
			else
			{
				var errorDiv = $( "toggle_errors" );
				var logAnchor = A( { "href": "/log/search#serveruser=" + Toggle.user },
									"View log output" );

				var killAnchor = A( { "href": "kill" },
									"Kill the server" );

				MochiKit.DOM.replaceChildNodes( errorDiv,
					[ P( null, "Failed to " + Toggle.action + " the server." ),
					UL( null, LI( null, logAnchor ), LI( null, killAnchor ) ) ]
					);
			}
		};

		var task = new AsyncTask.AsyncTask( null, onUpdate, null, onFinished, 
											null, null, 500, false );

		task.setID( Toggle.id );
		task.follow();
	}
};

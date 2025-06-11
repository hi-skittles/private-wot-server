"use strict";

/**
*   This module provides some glue to make it easier to manage server-side
*   AsyncTasks (see pycommon/async_task.py).  The idea is to use this module in
*   conjunction with the server-side AJAX glue in web_console/common/ajax.py.
*/

// requires Ajax
if (!Ajax) throw new Error( "Missing required lib 'Ajax'" );


/* namespace */ var AsyncTask =
{
	/**
	 *  A static list of all currently executing AsyncTasks.  This is needed to
	 *  provide static access to tasks with AsyncTask.get() and to be able to
	 *  clean up running tasks if the user navigates away from the page.
	 */
	s_tasks: [],


	/**
	 *  This class encapsulates an asynchronous task, such as fetching log
	 *  messages from the server.
	 */
	AsyncTask: function( onID, onUpdate, onNoUpdate, onFinished, onTimeout,
						onAjaxPollError, sleepTime, blocking, pollURL, stopURL )
	{
		this.id = -1;
		this.terminated = false;

		this.pollURL = pollURL || "/poll";
		this.stopURL = stopURL || "/terminate";

		// The callback that will be called when the server replies with the ID
		// of this AsyncTask.
		this.onID = onID;

		// The callback that will be called when the server has replied with
		// some new data for this task.
		this.onUpdate = onUpdate;

		// The callback that will be called when the server did not have any new
		// data for this task.
		this.onNoUpdate = onNoUpdate;

		// The callback that will be called when the server indicates that the
		// task has finished.
		this.onFinished = onFinished;

		// The callback that will be called when an error occurs during a poll
		// ajax task.
		this.onAjaxPollError = onAjaxPollError;

		// The callback that will be called when the server indicates that the
		// task has timed out
		this.onTimeout = onTimeout;

		// How long (in milliseconds) to wait between requests to the server
		// for updates.
		this.sleepTime = sleepTime;

		// If true, then a poll for updates will wait on the server until there
		// is some new data available.  Nothing sets this to true at the moment
		// AFAIK, and I can't really see the point of it in an AJAX context,
		// since AJAX is non-blocking by nature.  Hrm ...
		this.blocking = blocking;


		/**
		 *  This method starts this AsyncTask by sending an HTTP request.  If
		 *  the request comes back with errors, onError() will be called.
		 */
		this.start = function( url, params, onError )
		{
			var This = this;

			var onSuccess = function( reply )
			{
				This.id = reply.id;

				// If the task has started on the server successfully, follow
				// the task to completion.
				This.follow();

				if (This.onID)
				{
					This.onID( This.id, reply );
				}
			};

			Ajax.call( url, params, onSuccess, onError );
		}

		// Use this instead of start() when the AsyncTask has already been
		// started and you know the ID
		this.setID = function( id )
		{
			this.id = id;
		}


		/**
		 *  This method will follow the progress of this task to completion,
		 *  calling the supported callbacks (onUpdate, onNoUpdate, onFinished)
		 *  as appropriate.
		 */
		this.follow = function()
		{
			var This = this;

			// Function to poll the server for any updates for this task.
			var poll = function()
			{
				if (!This.terminated)
				{
					Ajax.call( This.pollURL,
							   {id: This.id, blocking: This.blocking},
							   onRecv, This.onAjaxPollError );
				}
			}

			// Callback that is called each time we receive an update for
			// this task from the server.
			var onRecv = function( reply )
			{
				if (This.terminated)
					return;

				var finished = false;
				var warnings = [];
				var errors = [];

				if (reply.status == "updated")
				{
					for (var i in reply.updates)
					{
						var state = reply.updates[i][0];
						var data = reply.updates[i][1];

						if (state == "finished")
						{
							finished = true;

							if (This.onFinished)
							{
								This.onFinished();
							}
						}
						else if (state == "__warning__")
						{
							warnings.push( data );
						}
						else if (state == "__error__")
						{
							errors.push( data );
						}
						else if (This.onUpdate)
						{
							This.onUpdate( state, data );
						}
					}
				}
				else if (reply.status == "timeout")
				{
					if (This.onTimeout)
					{
						This.onTimeout( reply );
					}	
				}

				// If there is no update from the server, call the onNoUpdate()
				// callback.  This can be used to animate a spinner icon to
				// indicate that the task is still in progress and receiving
				// updates.
				else
				{
					if (This.onNoUpdate)
						This.onNoUpdate( reply );
				}

				var utilErrors = []
				if (errors.length > 0)
				{
					console.error( "errors: " + errors );
					if (window.Alert)
					{
						for (var i in errors)
						{
							new Alert.Error( errors[ i ] )
						}
					}
					else if (window.Util)
					{
						utilErrors += errors
					}
				}

				if (warnings.length > 0)
				{
					console.warn( "warnings: " + warnings );
					if (window.Alert)
					{
						for (var i in warnings)
						{
							new Alert.Warning( warnings[ i ] )
						}
					}
					else if (window.Util)
					{
						utilErrors += warnings
					}
				}

				if (utilErrors.length > 0)
				{
					Util.errorWindow( utilErrors );
				}

				// If the task is not finished or terminated, then we will need
				// to poll the server again.  Depending on the nature of this
				// task, we might do it straight away or wait a little while.
				if (!finished && !This.terminated)
				{
					if (This.sleepTime)
						window.setTimeout( poll, This.sleepTime );
					else
						poll();
				}
			}

			// Kick off the polling process.
			poll();
		}


		/**
		 *  This method terminates this task, both on the client and server.
		 */
		this.terminate = function()
		{
			if (this.terminated)
				return;

			this.terminated = true;
			for (var i in AsyncTask.s_tasks)
				if (AsyncTask.s_tasks[i] == this)
					AsyncTask.s_tasks.splice( i, 1 );

			Ajax.call( this.stopURL, { id: this.id } );
		}

		AsyncTask.s_tasks.push( this );
	},


	/**
	 *  This function returns the AsyncTask with the provided id.
	 */
	get: function( id )
	{
		for (var i in AsyncTask.s_tasks)
			if (AsyncTask.s_tasks[i].id == id)
				return AsyncTask.s_tasks[i];
		return null;
	},


	/**
	 *  This method is an event handler for window unload (i.e. navigate away
	 *  from page) that stops all currently executing AsyncTasks.
	 */
	cleanup: function( e )
	{
		for (var i in AsyncTask.s_tasks)
		{
			var task = AsyncTask.s_tasks[i];
			if (task.id != -1 && !task.terminated)
				task.terminate();
		}
	}
};

jQuery( window ).on( 'unload', AsyncTask.cleanup );

// async_task.js

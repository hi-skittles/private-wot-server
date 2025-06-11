"use strict";

// requires jquery
if (!window.jQuery)
{
	throw new Error( 'required jquery lib not present' );
}

// requires Alert lib
if (!window.Alert)
{
	throw new Error( 'required Alert lib not present' );
}

var LiveView = window.LiveView || {}; //just for namespace
var profileInProgress = false; //trigger confirm page when profile is active

// a flag to mark unloading stage, ignore ajax error during this stage
var unloading = false;

var profileForm; 

LiveView.WATCHER_TRUE = "True";
LiveView.WATCHER_FALSE = "False";

/* called when the page is loaded */
function initLiveView( /*String*/ domTarget, /*String*/ machine, /*String*/ pid )
{	
	/* Initiliase the select doms*/
	jQuery( 'select' ).chosen();

	profileForm = new LiveView.ProfileForm( domTarget, machine, pid );
	profileForm.init();

	// font size ++/--
	jQuery( '.increase-font-size' ).on( 'click', function() {
		var logs = jQuery( '.stat-output-pane' );
		logs.css( 'font-size', Math.min( 24, parseInt( logs.css( 'font-size' ) )
									 + 1 ) );
	} );

	jQuery( '.decrease-font-size' ).on( 'click', function() {
		var logs = jQuery( '.stat-output-pane' );
		logs.css( 'font-size', Math.max( 5, parseInt( logs.css( 'font-size' ) ) 
									  - 1 ) );
	} );
}

function beforeUnload()
{
	// set this flag to ignore the ajax error during leaving current page
	unloading = true;

	if (profileInProgress)
	{
		return "Profile is still in progress.";
	}
}


/* function for handling ajax error*/
LiveView.ajaxError = function( jqxhr, /*String*/ textStatus,
						 /*String?*/ errorThrown )
{
	if (unloading)
	{
		// Ignore ajax errors when leaving this page
		jqxhr.bwExceptionHandled = true;
	}
	else if (jqxhr.status == 0)
	{
		// WebConsole may be down
		new Alert.Error( 'Web Console appears to be down', {
			id: 'ajax-error',
			duration: '5000',
		} );
	}
	else if (jqxhr.status ==
				BW.Constants.HTTP_RESPONSE_CODE.ServerStateException)
	{
		// ServerStateException, need to stop profile
		if (profileForm.refreshStatusTimerID !== undefined)
		{
			window.clearInterval( profileForm.refreshStatusTimerID );
			delete profileForm.refreshStatusTimerID;
		}

		if (profileForm.outputPane.isRefreshing)
		{
			profileForm.outputPane.stopRefresh();
		}

		profileForm._profileStopped();
		profileInProgress = false;
		
		profileForm._cancelRecording( false );
	}
};


/*~~~~~~~~~~~~~~~~~~~~~~~~~~ class LiveView.ProfileForm~~~~~~~~~~~~~~~~~~~~~~~*/
LiveView.ProfileForm  = function( /*String*/ domTarget, /*String*/ machine,
							/*String*/ pid )
{
	this.options = LiveView.ProfileForm.Defaults;
	if (this.options.debug)
	{
		console.log( 'profile for %s on ', pid, machine );
	}
	
	this.domTarget = domTarget;
	this.machine = machine;
	this.pid = pid;
};


LiveView.ProfileForm.Defaults= 
{
	debug: 0,
	
	defaultRecordTicks: 15,

	//Interval to refresh profile status
	refreshStatusInterval: 10000, //msec, enabled by default
	refreshStatusInterval_R: 1000, //msec,  enabled when recording

	/*URLs*/
	setWatcherUrl: 'setWatcher',
	getWatcherUrl: 'getWatcher',
	startProfileUrl: 'startProfile',
	stopProfileUrl: 'stopProfile',
	startRecordingUrl: 'startRecording',
	cancelRecordingUrl: 'cancelRecording',
	profileStatusUrl: 'profileStatus',
	getProfileDumpUrl: 'getProfileDump',

	/*watcher path*/
	sortModePath: 'profiler/sortMode',
	exclusivePath: 'profiler/exclusive',
	categoryPath: 'profiler/controls/currentCategory',

	prevEntryPath: 'profiler/controls/prevEntry',	
	nextEntryPath: 'profiler/controls/nextEntry',	
	toggleEntryPath: 'profiler/controls/toggleEntry',	
};


/* init Doms, Events and then refresh the profile status*/
LiveView.ProfileForm.prototype.init = function()
{
	/* init DOMs */
	this.domOptionsControls = jQuery( '.profile-options-controls' );
	this.domSortMode = jQuery( '.sort-mode' );
	this.domExclusive = jQuery( '.exclusive-mode' );
	this.domCategories = jQuery( '.categories' );

	this.domPrevEntry = jQuery( '.prev-entry' );
	this.domNextEntry = jQuery( '.next-entry' );
	this.domToggleEntry = jQuery( '.toggle-entry' );
	
	this.domProfileRecordContainer = jQuery( '.profile-record-container' );
	this.domProfileRecordPane = jQuery( '.profile-record-pane' );
	this.domStartProfileButton = jQuery( '.start-profile' );
	this.domStopProfileButton = jQuery( '.stop-profile' );
	this.domStartRecordButton = jQuery( '.start-record' );

	this.domCancelRecordButton = jQuery( '.cancel-record' );
	this.domDoRecordButton = jQuery ( '.do-record' );
	this.domRecordTicks = jQuery( '.record-ticks' );
	this.domRecordTicksEstimation = jQuery( '#recording-estimation' );
	this.domRecordStatusText = jQuery ( '.record-status-text' );
	this.domRecordResultText = jQuery ( '.record-result-text' );
	this.domViewRecordingLink = jQuery ( '.view-recording' );

	this.outputHeader = jQuery( '.stat-output-header' );
	this.statIndicator = jQuery( '.status-indicator' );
	this.domIdleSpinner = jQuery( '.idle-spinner' );
	this.domProgressSpinner = jQuery( '.progress-spinner' );

	this.outputPane = new LiveView.StatOutputPane( '.stat-output-pane', 
											this.machine, this.pid );
	/* init Events */
	this._initOptionEvents();
	this._initControlEvents();
	this._initActionEvents();

	/* now init the profile status*/
	this._refreshProfileStatus();

	//The profile status may be changed by other means
	//so we need to refresh it regularly
	this.refreshStatusTimerID = window.setInterval( 
									this._refreshProfileStatus.bind( this ), 
									this.options.refreshStatusInterval );
}


/* Init option events, includding sort mode and exclusive. */
LiveView.ProfileForm.prototype._initOptionEvents = function()
{
	this.domSortMode.change( function()
	{
		if (this.outputPane.isRefreshing)
		{
			this._setWatcher( this.options.sortModePath, 
							this.domSortMode.val(),
							this._updateControls
							);
		}
	}.bind( this ) );

	this.domExclusive.change( function()
	{
		if (this.outputPane.isRefreshing)
		{
			this._setWatcher( this.options.exclusivePath,
						this.domExclusive.val(),
						this._refreshStatistics );
		}
	}.bind( this ) );

	this.domCategories.change( function()
	{
		if (this.outputPane.isRefreshing)
		{
			this._setWatcher( this.options.categoryPath,
						this.domCategories.val(),
						this._refreshStatistics );
		}
	}.bind( this ) );
};


/* Init control events, including changing entry and category */
LiveView.ProfileForm.prototype._initControlEvents = function()
{
	this.domPrevEntry.click( function() 
	{
		this._setWatcher( this.options.prevEntryPath,
						LiveView.WATCHER_TRUE,
						this._refreshStatistics );
	}.bind( this ) );

	this.domNextEntry.click( function() 
	{
		this._setWatcher( this.options.nextEntryPath,
						LiveView.WATCHER_TRUE,
						this._refreshStatistics );
	}.bind( this ) );

	this.domToggleEntry.click( function() 
	{
		this._setWatcher( this.options.toggleEntryPath,
						LiveView.WATCHER_TRUE,
						this._refreshStatistics );
	}.bind( this ) );
};


/* Init action events, the button to start/stop/record profile */
LiveView.ProfileForm.prototype._initActionEvents = function()
{
	this.domStartProfileButton.click( function()
	{
		/*start profile and then update the status upon response*/
		this._startProfile( this.domSortMode.val(), 
							this.domExclusive.val(),
							this.domCategories.val() );
	}.bind( this ) );

	this.domStopProfileButton.click( function()
	{
		this._stopProfile();
	}.bind( this) );

	this.domStartRecordButton.click( function()
	{
		this.domStopProfileButton.attr( "disabled", "disabled" );
		this.domProfileRecordPane.removeClass( "downloading-finished" );
		this.domProfileRecordPane.addClass( "to-record" );
		this._recordTicksChanged();
	}.bind( this ) );

	this.domDoRecordButton.click( function()
	{
		var counts = Number( this.domRecordTicks.val() );
		if (isNaN( counts ) || counts <= 0)
		{
			new Alert.Error( "Unable to record profile beacause the" +
				" number of ticks provided is invalid.", {
				id: 'invalid-count-number',
				duration: 5000,				
			} );
			return false;
		}

		this._startRecording( counts );
	}.bind( this ) );

	this.domCancelRecordButton.click( function()
	{
		this._cancelRecording( true );
	}.bind( this ) );

	this.domRecordTicks.on( "change keyup input paste", function()
	{
		this._recordTicksChanged();
	}.bind( this ) );
};

/* Start Profile */
LiveView.ProfileForm.prototype._startProfile = function( /*String*/ sortMode,
														/*String*/ exclusive,
														/*String*/ category )
{
	jQuery.ajax( {
		url: this.options.startProfileUrl,
		data: { 'machine': this.machine, 'pid': this.pid, 'sortMode': sortMode,
				'exclusive': exclusive, 'category': category },
		dataType: 'json',
		success: function( /*Map*/ data, /*String*/ textStatus, jqxhr )
		{
			if (this.options.debug)
			{
				console.log( "start profile successfully " );
			}

			this._updateUi_ProfileStatus( data );

		}.bind( this ),
		error: LiveView.ajaxError
	} );
};


/* Stop Profile */
LiveView.ProfileForm.prototype._stopProfile = function()
{
	jQuery.ajax( {
		url: this.options.stopProfileUrl,
		data: {'machine': this.machine, 'pid': this.pid},
		dataType: 'json',
		success: function( /*Map*/ data, /*String*/ textStatus, jqxhr )
		{
			if (this.options.debug)
			{
				console.log( "stop profile successfully " );
			}

			this._updateUi_ProfileStatus( data );

		}.bind( this ),
		error: LiveView.ajaxError
	} );
};


/* Start Record*/
LiveView.ProfileForm.prototype._startRecording = function( /*number*/ dumpCounts )
{
	jQuery.ajax( {
		url: this.options.startRecordingUrl,
		data: { 'machine': this.machine, 'pid': this.pid,
				'dumpCounts': dumpCounts },
		dataType: 'json',
		success: function( /*Map*/ data, /*String*/ textStatus, jqxhr )
		{
			if (this.options.debug)
			{
				console.log( "start record successfully " );
			}

			this._updateUi_ProfileStatus( data );

		}.bind( this ),
		error: LiveView.ajaxError
	} );
};


/* stop recording */
LiveView.ProfileForm.prototype._cancelRecording =
function( /*boolean*/ sendReq )
{
	this.domStopProfileButton.removeAttr( "disabled" );
	this.domProfileRecordPane.removeClass( "to-record");
	//this.domProfileRecordPane.removeClass( "record-in-progress");

	if (sendReq && this.recording)
	{
		jQuery.ajax( {
			url: this.options.cancelRecordingUrl,
			data: {'machine': this.machine, 'pid': this.pid},
			dataType: 'json',
			success: function( /*Map*/ data, /*String*/ textStatus, jqxhr )
			{
				if (this.options.debug)
				{
					console.log( "stopped recording successfully " );
				}

				this._updateUi_ProfileStatus( data );

			}.bind( this ),
			error: LiveView.ajaxError
		} );
	}
};


/* Download the JSON dump after recording is finished*/
LiveView.ProfileForm.prototype._downloadJsonDump =
function( /*String*/ jsonFilePath )
{
	jQuery.ajax( {
		url: this.options.getProfileDumpUrl,
		data: { 'machine': this.machine,
				'dumpFilePath': jsonFilePath },
		dataType: 'json',
		success: function( /*Map*/ data, /*String*/ textStatus, jqxhr )
		{
			if (this.options.debug)
			{
				console.log( "downloading JSON dump successfully " );
			}

			this._downloadingFinished( data );

		}.bind( this ),
		error: function( jqxhr, textStatus, errorThrown )
		{
			console.log( "Failed to download JSON dump " );
			this._downloadingFailure( jqxhr, textStatus, errorThrown );
		}.bind( this )
	} );
};


/* Get the profile status of this process and change the UI accordingly */
LiveView.ProfileForm.prototype._refreshProfileStatus = function()
{
	jQuery.ajax( {
		url: this.options.profileStatusUrl,
		data: {'machine': this.machine, 'pid': this.pid},
		dataType: 'json',
		success: function( /*Map*/ data, /*String*/ textStatus, jqxhr )
		{
			if (this.options.debug)
			{
				console.log( "get profile status successfully " );
			}

			this._updateUi_ProfileStatus( data );

		}.bind( this ),
		error: LiveView.ajaxError
	} );
};

/* Get statistics for one time, this is called when profile option is changed*/
LiveView.ProfileForm.prototype._refreshStatistics = function()
{
	this.outputPane.fetchStat();
};


LiveView.ProfileForm.prototype._recordTicksChanged = function()
{
	var ticksStr = this.domRecordTicks.val();
	var ticks = Number( ticksStr );

	if (!isNaN( ticks ) && ticks > 0)
	{
		var totalSeconds = ticks / this.ticksPerSecond;
		var minutes = Math.floor( totalSeconds / 60 );
		var seconds = totalSeconds % 60;

		var estmationText = "(Estimated time: ";
		if (minutes > 0)
		{
			estmationText += minutes + " min "
		}
		if (seconds > 0)
		{
			estmationText += seconds + " sec"
		}
		estmationText += ")" 
		
		this.domRecordTicksEstimation.text( estmationText );
		if (totalSeconds > 300)
		{
			this.domRecordTicksEstimation.attr( "class",
					"record-estimation-alert" );
		}
		else
		{
			this.domRecordTicksEstimation.removeClass();
		}
	}
	else
	{
		if( ticksStr )
		{
			this.domRecordTicksEstimation.text( "Invalid number" );
			this.domRecordTicksEstimation.attr( "class",
					"record-estimation-alert" );
		}
		else
		{
			this.domRecordTicksEstimation.text( "" );
			this.domRecordTicksEstimation.removeClass();
		}
	}
};

LiveView.ProfileForm.prototype._updateUi_ProfileStatus = function( /*Map*/ data )
{
	/* unloading can be set to true when onbeforeunload is triggered. However,
		user may choose cancel on the confirmwindow to stay on current page,
		thus we need set the flag to false again and here is a good place */
	unloading = false;

	//profile has just started
	if (!profileInProgress && data.enabled)
	{
		this._profileStarted();		
	}

	//profile has just stopped 
	if (profileInProgress && !data.enabled)
	{
		this._profileStopped();		
	}

	
	if (data.dumpState == 3)
	{
		// json dump is in error state, may be beause failing to create file
		this._recordingError();
	}
	else
	{
		//recording has just started
		if (!this.recording && data.recording)
		{
			this._recordingStarted( data.dumpFilePath );
		}

		//recording has just finished 
		if (this.recording && !data.recording)
		{
			this._recordingFinished( data.dumpFilePath );
		}
	}
	
	if (data.ticksPerSecond && !isNaN( data.ticksPerSecond )
			&& data.ticksPerSecond > 0 )
	{
		this.ticksPerSecond = data.ticksPerSecond;
	}
	else
	{
		this.ticksPerSecond = 10;
	}
	
	this.recording = data.recording;
	profileInProgress  = data.enabled;
	if (!profileInProgress)
	{
		this.domStartRecordButton.attr( "disabled", "disabled" );
	}

	if (this.recording)
	{
		var jsonDumpCount = data.jsonDumpCount;
		var jsonDumpIndex = data.jsonDumpIndex;
		var recordingText = "Step 1/2:  Recording... ";
		
		// jsonDumpIndex may be null for older server processes 
		if ( !isNaN( jsonDumpIndex ) && jsonDumpIndex > 0 )
		{
			var percentage = Math.floor( 
								( jsonDumpIndex * 100 ) / jsonDumpCount )
			recordingText += percentage + "%";
		}	 

		this.domRecordStatusText.text( recordingText );
		this.domRecordStatusText.attr( "title",
				"Path: " + this.machine + ":" + data.dumpFilePath );
	}
	
	//update the options, controls status
	this._updateOptionsControls( data );
};


LiveView.ProfileForm.prototype._profileStarted = 
function()
{
	this.domProfileRecordContainer.addClass( 'profile-in-progress' );
	this.domStartRecordButton.removeAttr( "disabled" );

	var statusTxt = 'Profile is in progress';
	this.statIndicator.html( statusTxt );
	this.domProgressSpinner.show();
	this.domIdleSpinner.hide();

	if (!this.outputPane.isRefreshing)
	{
		this.outputPane.startRefresh();
	}
};


LiveView.ProfileForm.prototype._profileStopped = function()
{
	this.domProfileRecordContainer.removeClass( 'profile-in-progress' );
	this.domStartRecordButton.attr( "disabled", "disabled" );

	var statusTxt = 'Profile is stopped';
	this.statIndicator.html( statusTxt );
	this.domProgressSpinner.hide();
	this.domIdleSpinner.show();

	/* stop the frequen refresher which is enabled for recording 
	  when profile is stopped */
	if (this.refreshStatusTimerID_R)
	{
		window.clearInterval( this.refreshStatusTimerID_R );
		delete this.refreshStatusTimerID_R;
	}
	
	if (this.outputPane.isRefreshing)
	{
		this.outputPane.stopRefresh();
	}
};


LiveView.ProfileForm.prototype._recordingStarted =
function( /* String */ dumpFilePath )
{
	this.domProfileRecordPane.removeClass( "to-record" );
	this.domProfileRecordPane.addClass( "record-in-progress" );

	/* refresh more frequently as the recording may be done at any time */
	if (!this.refreshStatusTimerID_R)
	{
		this.refreshStatusTimerID_R = 
			window.setInterval( this._refreshProfileStatus.bind( this ), 
							this.options.refreshStatusInterval_R );
	}
};


LiveView.ProfileForm.prototype._recordingFinished =
function( /*String*/ dumpFilePath )
{
	this._downloadJsonDump( dumpFilePath );
	this.domRecordStatusText.text( "Step 2/2:  Downloading... " );

	/* stop the frequent refresher which is enabled for recording */
	if (this.refreshStatusTimerID_R)
	{
		window.clearInterval( this.refreshStatusTimerID_R );
		delete this.refreshStatusTimerID_R;
	}
};


LiveView.ProfileForm.prototype._recordingError =
function()
{
	this._cancelRecording( false );
	
	new Alert.Error( "Recording failed, which might be due to failing to "
		+ "create recording file.",
		{ id: 'recording-error',	duration: '5000' } );
}


LiveView.ProfileForm.prototype._downloadingFinished =
function( /*String*/ data )
{
	this.domStopProfileButton.removeAttr( "disabled" );

	this.domProfileRecordPane.removeClass( "record-in-progress");
	this.domProfileRecordPane.addClass( "downloading-finished" );
	this.domRecordResultText.attr( "title",
			"File name: " + this._getFileNameFromPath( data.dumpFilePath ) );
			
	if (this._browserSupported())
	{
		this.domViewRecordingLink.attr( "href",
			"view?fileName=" + this._getFileNameFromPath( data.dumpFilePath ) );
	}
	else
	{
		this.domViewRecordingLink.hide();
	}
};


LiveView.ProfileForm.prototype._browserSupported = function()
{
	// only Chrome with version 25 or later is supportet because there is new
	// standard (web components) used in the trace view library which is only
	//supported by Chrome with version 25 or later.
	if ((BrowserDetect.browser == "Chrome") && (BrowserDetect.version >= 25))
    {
		return true;
	}
	
	return false;
};


LiveView.ProfileForm.prototype._downloadingFailure =
function( jqxhr, /*String*/ textStatus, /*String?*/ errorThrown )
{
	this.domStopProfileButton.removeAttr( "disabled" );

	this.domProfileRecordPane.removeClass( "record-in-progress");
	
	var responseJson = JSON.parse( jqxhr.responseText );
	var exceptionType = responseJson.exception;
	var message = responseJson.message;

	if(exceptionType == "ProfileDownloadFailure")
	{
		this._alertDumpFilePath( message );
	}
	else
	{
		LiveView.ajaxError( jqxhr, textStatus, errorThrown );
	}
	
	jqxhr.bwExceptionHandled = true;
};


LiveView.ProfileForm.prototype._updateOptionsControls =
function( /*Object*/ data )
{
	this.domSortMode.val( data.sortMode );
	this.domExclusive.val( String( data.exclusive ) );

	//refresh the category select
	this.domCategories.empty();
	var categories = data.categories.split( ';' );
	for (var i in categories)
	{
		this.domCategories.append( new Option( categories[i],
								categories[i] ) );
	}   
	this.domCategories.val( data.currentCategory );

	// rebuild the select-replacement widgets( jquery 'chosen' plugin )
	this.domOptionsControls.find( 'select' ).each( function()
	{
		jQuery( this ).triggerHandler( 'liszt:updated' );
	} );
	
	this._updateControls();
}

/* toggle the entry controls when the sort mode changed from/to hierachical */
LiveView.ProfileForm.prototype._updateControls = function()
{
	if (profileInProgress && this.domSortMode.val() === 'HIERARCHICAL')
	{
		this.domPrevEntry.show( "bw_menu_fade_in" );
		this.domNextEntry.show( "bw_menu_fade_in" );
		this.domToggleEntry.show( "bw_menu_fade_in" );
	}
	else
	{
		this.domPrevEntry.hide( "bw_menu_fade_out" );
		this.domNextEntry.hide( "bw_menu_fade_out" );
		this.domToggleEntry.hide( "bw_menu_fade_out" );
	}
};


LiveView.ProfileForm.prototype._alertDumpFilePath = 
function( /*String*/ dumpFilePath )
{ 
		var alertContent = 'Failed to download the recording file. '
				+ 'This is probably because no proper serviceapp is running. '
				+'You can manually upload this recording to '
				+ '<span class="alert-recording-link">'
				+ '<a href="dumps">Recordings</a></span> to view the content:'
				+ '<div contenteditable="true" class="alert-recording-content">'
				+ '<textarea class="alert-recording-text">'
				+ this.machine + ':' + dumpFilePath 
				+ '</textarea></div>'
				+ '<div class="alert-recording-action">'
				+ '<span class="alert-recording-copy">'
				+ 'Press CTRL-C to copy above text</span>'
                + '<button class="alert-recording-button">Close</button></div>';
		
		var alertOptions = { dismissable: false,
							duration: 600000 } ;
							
		var alert = new Alert.Warning( alertContent, alertOptions );
		var textElement = alert.jquery.find( '.alert-recording-text' );
		var copyHint = alert.jquery.find( '.alert-recording-copy' );
		var closeButton = alert.jquery.find( 'button' );

		textElement[0].style.height = textElement[0].scrollHeight + 'px';
		textElement.focus();
		textElement.select();
		textElement.on( 'hover', function()
		{
			textElement.select(); 
			copyHint.css( 'visibility', 'visible')
		} );
 
		textElement.on( 'blur', function()
		{
			copyHint.css( 'visibility', 'hidden');
		} );

		closeButton.on( 'click', function()
		{
			alert.dismiss();
		} );
};

LiveView.ProfileForm.prototype._getFileNameFromPath =
function( /*String*/ filePath )
{
	var lastForwardSlash = filePath.lastIndexOf('/');
	
	if (lastForwardSlash >= 0)
	{
		return filePath.substring( lastForwardSlash + 1 );
	}
	else
	{
		return filePath;
	}
}


LiveView.ProfileForm.prototype._setWatcher = function( /*String*/ path,
														/*String*/ value,
														/*Function*/ callback )
{
	var p = this; //save this for callback function
	jQuery.ajax( {
		url: this.options.setWatcherUrl,
		context: this,
		data: { 'machine': this.machine,
				'pid': this.pid,
				'path': path,
				'value': value },
		dataType: 'json',
		success: function( /*Map*/ data, /*String*/ textStatus, jqxhr )
		{
			if (this.options.debug)
			{
				console.log( "set watcher %s successfully", data.path,
								data.value );
			}

			if (typeof callback !== 'undefined')
			{
				callback.call( p );
			}
		},
		error: LiveView.ajaxError 
	} );
};


/*~~~~~~~~~~~~~~~~~~~~~~~~~ class LiveView.ProfileOutputPane ~~~~~~~~~~~~~~~~~*/

LiveView.StatOutputPane = function( /*String*/ domTarget, /*String*/machine, 
								/*String*/ pid )
{
	this.options = LiveView.StatOutputPane.Defaults;
	var dom = this.dom = {};
	dom.output = jQuery( domTarget );

	if (!( dom.output.length > 0 ))
	{
		console.error(
			"Dom target identified by selector '%s' doesn't exist",
			domTarget
		);
	}
	dom.container = dom.output.parent();

	this.fetchParams = { 'machine': machine, 'pid': pid };
	this.isRefreshing = false;

	this.fillInData( "No profile data is available." );
};


LiveView.StatOutputPane.Defaults= 
{
	profileStatUrl: 'statistics',
	refreshInterval: 500, //msec
	timeoutPeriod: 2000
};


/* Profile is in progress, start rereshing profile statistics */
LiveView.StatOutputPane.prototype.startRefresh = function()
{
	if (this.isRefreshing)
	{
		console.log( "already refreshing, returning..." );
		return;
	}

	this.isRefreshing = true;
	this.fetchStat();
	this.refreshTimerId = window.setInterval( this.fetchStat.bind( this ),
							  this.options.refreshInterval );
};


/* Profile is stopped, stop refreshing profile statistics*/
LiveView.StatOutputPane.prototype.stopRefresh = function()
{
	if (!this.isRefreshing)
	{
		console.log( "not refreshing, no need to stop, just return" );
		return;
	}

	clearInterval( this.refreshTimerId );
	this.isRefreshing = false;
};


/* fetch profile statistics from WebConsole */
LiveView.StatOutputPane.prototype.fetchStat = function()
{
	if (!this.isRefreshing)
	{
		console.warn( "not refreshing, shouldn't fetch, just return" )
		return;
	}

	jQuery.ajax( {
		url: this.options.profileStatUrl,
		data: this.fetchParams,
		dataType: 'json',
		timeout: this.timeoutPeriod,
		success: function( /*Map*/ data, /*String*/ textStatus, jqxhr )
		{
			this._handleData( data );
		}.bind( this ),
		error: LiveView.ajaxError 
	} );
};


LiveView.StatOutputPane.prototype._handleData = function( /*Object*/ data )
{
	this.fillInData( data.statistics );
}


/* Fill the statistics data into the pane*/
LiveView.StatOutputPane.prototype.fillInData = function( /*Array*/ lines )
{
	var docFragment = document.createDocumentFragment();
	var div = document.createElement( "div" );
	div.appendChild( document.createTextNode( lines ) );
	docFragment.appendChild( div );
	
	this.dom.output.empty();
	this.dom.output.append( docFragment );
}   

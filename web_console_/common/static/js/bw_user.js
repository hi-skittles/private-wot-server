"use strict";

console.assert( window.jQuery );

var BW = window.BW || {};


/**
*   Abstraction of WebConsole users. In general, there is likely to only be
*   1 instance of this class, as the page-scoped singleton `BW.user`.
*
*   Properties          | Description
*   --------------------|---------------------------------------------
*   name                | WebConsole user name
*   serverUser          | BigWorld server user name
*   effectiveServerUser | BigWorld server user name
*   ownerRights         | Array of user's rights as page owner
*   otherRights         | Array of user's rights when not page owner
*   isCurrentPageOwner  | Whether user "owns" this page
*/
BW.User = function( /*Map<String,Any>*/ options )
{
	jQuery.extend( this, options );

	// create Map versions of Array of both sets of rights
	var map = this.ownerRightsMap = {};
	if (this.ownerRights)
		for (var i in this.ownerRights)
			map[this.ownerRights[i]] = true;

	map = this.otherRightsMap = {};
	if (this.otherRights)
		for (var i in this.otherRights)
			map[this.otherRights[i]] = true;

	console.assert( this.serverUser !== undefined );
	console.assert( this.effectiveServerUser !== undefined );

	this.isCurrentPageOwner = (this.serverUser === this.effectiveServerUser);
	
	jQuery( document ).on( 'click', '.input-div .dropdown-button', 
		function() { 
			BW.user.displayRecentUsers();
		}
	);
};


/**
*   Loads WebConsole resource permissions; initialises page-scoped
*   singleton `BW.permissions`.
*/
BW.User.loadPermissions = /*static*/ function()
{
	jQuery.getJSON( '/permissions', function( /*Object*/ p ) {
		console.log( "loaded permissions" );
		BW.permissions = p;
	});
};


/** Sets user- and permission-related CSS classes on the root `html` element. */
BW.User.initPermissions = /*static*/ function()
{
	console.assert( BW.user );

	if (BW.user.isAdmin())
	{
		jQuery( 'html' ).addClass( 'acting-as-admin' );
	}
	else if (BW.user.isCurrentPageOwner)
	{
		var ownerRights = BW.user.ownerRights.map(
			function( r ) { return "can-" + r; } ).join( ' ' );

		jQuery( 'html' ).addClass( 'acting-as-owner ' + ownerRights );
	}
	else
	{
		var otherRights = BW.user.otherRights.map(
			function( r ) { return "can-" + r; } ).join( ' ' );

		jQuery( 'html' ).addClass( 'acting-as-other ' + otherRights );
	}

	if (!BW.user.hasOtherPermissions( ['view'] ))
	{
		jQuery( 'html' ).addClass( 'cant-view-other' );
	}
}


BW.User.prototype.isAdmin = function()
{
	return this.name === 'admin';
};


BW.User.prototype.hasOwnerPermissions = function( /*Array of String*/ rights )
{
	console.log( "user has owner rights: ", this.ownerRights );
	for (var i in rights)
		if (! (rights[i] in this.ownerRightsMap) )
			return false;

	return true;
};


BW.User.prototype.hasOtherPermissions = function( /*Array of String*/ rights )
{
	console.log( "user has other rights: ", this.otherRights );
	for (var i in rights)
		if (! (rights[i] in this.otherRightsMap) )
			return false;

	return true;
};


/**
*   Compare this user's permissions against those associated to the passed
*   URL (resource). Requires `BW.permissions` to be set.
*/
BW.User.prototype.canAccess = function( /*String*/ url )
{
	if (!BW.permissions)
	{
		console.error( "BW.permissions not initialised, access control disabled" );
		return true;
	}

	// assume all javascript urls are accessible, no check req'd
	if (url.match( /^\s*javascript:/ ))
	{
		return true;
	}

	console.log( "checking rights for url: %s", url );
	var url_params = url.split( '?' );

	console.assert( url_params[0] );
	console.assert( url_params.length <= 2 );
	var paths = url_params[0].split( '/' );

	// if trailing slash at end of URL, pop off empty string path fragment
	if (!paths[paths.length - 1])
		paths.pop();

	if (!paths)
	{
		console.warn( 'No paths to check: ', url );
		return true;
	}

	// examine params to determine "ownership" of resource
	var params = {};
	var parts = (url_params[1] || '').split( /&|;/ );
	for (var i in parts)
	{
		var param_value = parts[i].split( '=' );
		params[param_value[0]] = param_value[1];
	}
	console.log( "params: %O", params );


	// isOwner should be false if page we're on has a user=xxx param, where
	// xxx is not the current user
	var isOwner = this.isCurrentPageOwner;

	if (params.user)
	{
		isOwner = (params.user === BW.user.serverUser);
	}
	console.log(
		"user is owner=%s: user.serveruser='%s', user param='%s'",
		isOwner, BW.user.serverUser, params.user || '(none)'
	);

	// determine permissions required to access link
	var requiredRights;
	var path = paths.pop();
	while (requiredRights === undefined)
	{
		console.log( "checking rights for '%s'", path );
		requiredRights = BW.permissions[path];

		if (!paths.length) break;
		path = paths.pop() + '/' + path;
	}

	if (!requiredRights)
	{
		// resource doesn't have permissions
		console.log( "resource not rights-protected" );
		return true;
	}
	console.log( "resource requires rights: ", requiredRights );

	var canAccess = ( isOwner
					? BW.user.hasOwnerPermissions( requiredRights )
					: BW.user.hasOtherPermissions( requiredRights ) );

	if (canAccess)
	{
		console.log( "user authorised for link: ", url );
		return true;
	}
	else
	{
		console.log( "user not authorised for link: ", url );
		return false;
	}
};

/**
* Call the getUsers endpoint and process the user list. This occurs when any 
* page is opened, when the change server user dialog is opened, and every 5 
* seconds when the refresh button is enabled.
*/
BW.User.prototype.getUsersListForDialog = function() 
{
	var autoField = jQuery( '#users-input' );
	var accessButton = jQuery( '#access-user-btn' );
	var acceptIcon = jQuery( '.switch-user-dialog .input-div .username-accept' );
	
	jQuery.getJSON( '/cc/getUsers?inactive=1', function( response )
	{
		if (!response.users)
		{
			console.error( "Expected list of users, but got %O", response );
			return;
		}
		
		// Map the response to an array of objects containing user data
		var users = response.users.map( function( u ) {
			var activity = '';
			if (!u.isActive || u.procs.length == 0) {
				activity = '(inactive)';
			}
			else {
				var machines = [];
				for (var p in u.procs) {
					if (u.procs[p].machine != undefined) {
						if (machines.indexOf( u.procs[p].machine.name ) == -1) {
							machines.push( u.procs[p].machine.name );
						}
					}
				}
				activity = u.procs.length + ' processes on ' + 
					machines.length;
				if (machines.length == 1) {
					activity += ' machine';
				}
				else {
					activity += ' machines';
				}
			}
			return { value: u.name, uid: u.uid, activity: activity };
		});
		
		// Save to class for use in recent users list
		BW.user.userList = users;
		
		// Set up autocomplete field
		autoField.autocomplete({
			source: function( request, response ) {
				var results = [];
				for (var i in users) {
					if (users[i].value.toLowerCase().indexOf( 
							request.term.toLowerCase() ) == 0 && 
							users[i].value != BW.user.effectiveServerUser) {
						results.push( users[i] );
					}
				}
				response(results.slice(0, 10));
			},
			select: function( event, ui ) {
				if ( jQuery.grep( BW.user.userList, function( e ) { 
					return e.value == ui.item.value; } ).length == 1)
				{
					acceptIcon.removeClass( 'invalid-input' );
					accessButton.removeClass( 'disabled' );
					accessButton.prop( 'disabled', false );
				}
				else
				{
					accessButton.addClass( 'disabled' );
					accessButton.prop( 'disabled', true );
				}
			}
		});
		// Add a unique class to the autocomplete dropdown for easy finding
		autoField.autocomplete( 'instance' )._renderMenu = 
			function( ul, items )
			{
				var that = this;
				$.each( items, function( index, item ) {
					that._renderItemData( ul, item );
				});
				$( ul ).addClass( 'auto-dropdown' );
			};
		// Render autocomplete items showing extra info
		autoField.autocomplete( 'instance' )._renderItem = 
			function( ul, item ) 
			{
				jQuery( ul ).css( 'z-index', 999 );
				return jQuery( '<li class="switch-users-dropdown"><div>' + 
					item.value + '</div><div>' + item.uid + '</div><div>' + 
					item.activity + '</div></li>' ).appendTo( ul );
			};

		// When field has become empty, disable the Access User button
		// If field is a valid username, display the accept icon, else hide it
		autoField.on( 'input', function() {
			if (autoField.val() == '')
			{
				accessButton.addClass( 'disabled' );
				accessButton.prop( 'disabled', true );
				acceptIcon.addClass( 'invalid-input' );
			}
			else if ( jQuery.grep( BW.user.userList, function( e ) { 
				return e.value == autoField.val(); } ).length == 1)
			{
				accessButton.removeClass( 'disabled' );
				accessButton.prop( 'disabled', false );
				acceptIcon.removeClass( 'invalid-input' );
			}
			else
			{
				accessButton.addClass( 'disabled' );
				accessButton.prop( 'disabled', true );
				acceptIcon.addClass( 'invalid-input' );
			}
		});
		
		// Build all users table
		var sTable = [];
		for (var i in users) {
			if (users[i].value != BW.user.effectiveServerUser)
			{
				sTable.push([users[i].value, users[i].uid, users[i].activity]);
			}
		}

		if (BW.user.usersTable == null) {
			BW.user.usersTable = jQuery( '#all-users-table' ).dataTable( {
				'aaData': sTable,
				'aoColumns': [ 
					{ 'sTitle': 'Username' }, 
					{ 'sTitle': 'UID' }, 
					{ 'sTitle': 'Activity', 'asSorting': ['desc', 'asc'] } 
				],
				'bPaginate': false,
				'sScrollY': '395px',
				'sScrollX': '100%',
				'sScrollXInner': '100%',
				'bInfo': false,
				'bFilter': false,
				'fnRowCallback': function( nRow, aData, iDisplayIndex ) {
					jQuery( nRow ).css( 'cursor', 'pointer' );
					if (iDisplayIndex % 2 == 1)
					{
						jQuery( nRow ).addClass( 'off-white' );
					}
					jQuery( nRow ).on( 'click', function () {
						jQuery( '#users-input' ).val( aData[0] );
						acceptIcon.removeClass( 'invalid-input' );
						accessButton.removeClass( 'disabled' );
						accessButton.prop( 'disabled', false );
						autoField.focus();
					});
				}
			} );
		}
		else
		{
			BW.user.usersTable.fnClearTable();
			BW.user.usersTable.fnAddData( sTable );
			BW.user.usersTable.fnDraw();
		}
	});
};


/**
* Open change server user dialog
*/
BW.User.prototype.switchServerUserDialog = function( /*DOM*/ element )
{
	if (!this.hasOtherPermissions( ['view'] ))
	{
		console.log( "User doesn't have sufficient permissions to switch " + 
			"serveruser" );
		return false;
	}
	
	var dialog = jQuery( '.switch-user-dialog' );
	console.assert( dialog[0] );

	jQuery( 'html' ).addClass( 'switch-user-dialog-showing' );
	jQuery( document ).off( 'keypress' );
	
	// Get relevant elements for easy reference
	var allUsersHeader = jQuery( '.switch-user-dialog .all-users-header' );
	var allUsersList = jQuery( '.switch-user-dialog .all-users-list' );
	var autoField = jQuery( '#users-input' );
	var accessButton = jQuery( '#access-user-btn' );
	var refreshButton = jQuery( '.refresh-users-button' );
	var dropdownButton = jQuery( '.input-div .dropdown-button *' );
	var plusMinusIcon = jQuery( '#header-icon', '.switch-user-dialog' );
	var acceptIcon = jQuery( '.switch-user-dialog .input-div .username-accept' );
	
	autoField.focus();
	refreshButton.removeClass( 'depressed' );
	jQuery( 'img', refreshButton ).attr( 'src', 
		'/static/images/throbber_16_o.gif' );
	acceptIcon.addClass( 'invalid-input' );
	
	accessButton.on( 'click', function ( e ) {
		BW.user.switchServerUser( autoField.val() );
	});
	
	autoField.keypress( function( e ) {
		// Event for the enter key being pressed
		if (e.which == 13 && !accessButton.prop( 'disabled' ))
		{
			BW.user.switchServerUser( autoField.val() );
		}
	});
	
	// Initialise always show checkbox based on cookie value
	if (jQuery.cookie( 'alwaysShowUsers' ) == 'true' )
	{
		allUsersList.css( 'display', 'block' );
		// If user list exists, redraw table
		if (BW.user.userList)
		{
			BW.user.usersTable.fnDraw();
		}
		$( '#alwaysShowUsersCheckbox' ).prop( 'checked', true );
		plusMinusIcon.removeClass( 'icon-plus-sign' )
			.addClass( 'icon-minus-sign' );
	}
	else
	{
		$( '#alwaysShowUsersCheckbox' ).prop( 'checked', false );
		plusMinusIcon.removeClass( 'icon-minus-sign' )
			.addClass( 'icon-plus-sign' );
	}
	
	var closeDialog = function()
	{
		jQuery( 'html' ).removeClass( 'switch-user-dialog-showing' );
		allUsersHeader.off();
		refreshButton.off();
		jQuery( '#alwaysShowUsersCheckbox' ).off();
		allUsersList.css( 'display', 'none' );
		if (BW.user.userListRefreshInterval)
		{
			window.clearInterval( BW.user.userListRefreshInterval );
		}
	};

	// Close button click event
	jQuery( '.switch-user-dialog .close-button' ).one( 'click', function() {
		closeDialog();
	});
	
	// Escape keypress event
	jQuery( document ).one( 'keyup', function( e ) {
		if (e.keyCode  == 27)
		{
			closeDialog();
		}
	});
	
	// All users header events
	allUsersHeader.mouseover( function() {
		allUsersHeader.addClass( 'hover' );
	});
	allUsersHeader.mouseout( function() {
		allUsersHeader.removeClass( 'hover' );
	});
	allUsersHeader.on( 'click', function() {
		if (allUsersList.css( 'display' ) == 'none')
		{
			plusMinusIcon.removeClass( 'icon-plus-sign' )
				.addClass( 'icon-minus-sign' );
			allUsersList.slideDown();
			if (BW.user.userList)
			{
				BW.user.usersTable.fnDraw();
			}
		}
		else 
		{
			plusMinusIcon.removeClass( 'icon-minus-sign' )
				.addClass( 'icon-plus-sign' );
			allUsersList.slideUp();
		}
	});
	
	// Checkbox change event
	jQuery( '#alwaysShowUsersCheckbox' ).on( 'change', function() {
		if (jQuery( this ).is( ':checked' ))
		{
			jQuery.cookie( 'alwaysShowUsers', true, { path: '/' } );
		}
		else
		{
			jQuery.cookie( 'alwaysShowUsers', false, { path: '/' } );
		}
	});
	
	// Refresh timer setup
	BW.user.userListRefreshing = false;
	refreshButton.on( 'click', function() {
		if (BW.user.userListRefreshing)
		{
			BW.user.userListRefreshing = false;
			jQuery( this ).removeClass( 'depressed' );
			jQuery( 'img', this ).attr( 'src', 
				'/static/images/throbber_16_o.gif' );
			window.clearInterval( BW.user.userListRefreshInterval );
		}
		else
		{
			BW.user.userListRefreshing = true;
			jQuery( this ).addClass( 'depressed' );
			jQuery( 'img', this ).attr( 'src', 
				'/static/images/throbber_16.gif' );
			BW.user.userListRefreshInterval = window.setInterval( 
				function() { BW.user.getUsersListForDialog(); }, 5000 );
		}
	});
};


BW.User.prototype.displayRecentUsers = function()
{
	var autoField = jQuery( '#users-input' );
	var accessButton = jQuery( '#access-user-btn' );
	var acceptIcon = jQuery( '.switch-user-dialog .input-div .username-accept' );
	var dropdownButton = jQuery( '.input-div .dropdown-button' );
	var list = jQuery( '.input-div .recent-users-list' )
	
	if (list.is( ':hidden' ))
	{
		jQuery( 'span', dropdownButton ).html( '&#x25b2;' );
		var recentUsersString = jQuery.cookie( 'recentUsers' );
		var listString = '';
		
		if (recentUsersString == '' || recentUsersString == undefined)
		{
			listString += '<li class="footer">No Recent Users...</li>';
		}
		else
		{
			var recentUsers = recentUsersString.split( '|' );
			var recentUsersCount = 0;
			
			for (var i in recentUsers) 
			{
				var userDetailSearch = jQuery.grep( BW.user.userList, 
					function( e )
					{
						return e.value == recentUsers[i];
					}
				);
				if (userDetailSearch.length > 0)
				{
					listString += '<li class="switch-users-dropdown ' + 
						'ui-menu-item" id="' + userDetailSearch[0].value + 
						'"><div>' + userDetailSearch[0].value + 
						'</div><div>' + userDetailSearch[0].uid + 
						'</div><div>' + userDetailSearch[0].activity + 
						'</div></li>';
					recentUsersCount++;
				}
			}
			if (recentUsersCount == 1)
			{
				listString += '<li class="footer">Last User...</li>';
			}
			else
			{
				listString += '<li class="footer">Last ' + 
					recentUsersCount + ' Users...</li>';
			}
		}
		list.html( listString );
		list.width( autoField.width() + 23 ).show();
		list.position({
			my: 'left top',
			at: 'left bottom',
			of: '#users-input'
		});
		
		jQuery( '.input-div .recent-users-list .switch-users-dropdown' )
			.on( 'click', function( e ) 
			{
				autoField.val(
					jQuery( e.target ).closest( 'li' ).attr( 'id' ) );
				autoField.focus();
				accessButton.removeClass( 'disabled' );
				accessButton.prop( 'disabled', false );
				acceptIcon.removeClass( 'invalid-input' );
			}
		);
	
		jQuery( document ).one( 'click', function( e ) {
			if (jQuery( e.target ).is( '.input-div .dropdown-button *' ))
			{
				return;
			}
			else
			{
				jQuery( 'span', dropdownButton ).html( '&#x25bc;' );
				list.hide();
			}
		});
	}
	else
	{
		jQuery( 'span', dropdownButton ).html( '&#x25bc;' );
		list.hide();
	}
}


/**
*   Reloads the given URL (or current URL if not given) as the given serveruser.
*/
BW.User.prototype.switchServerUser =
function( /*String*/ serveruser, /*String?*/ given_url )
{
	console.assert( serveruser );
	
	// Update recent users cookie if not reverting to own user
	if (serveruser != BW.user.name)
	{
		var recentUsersString = jQuery.cookie( 'recentUsers' );
		if (recentUsersString == undefined)
		{
			// Cookie is not present
			var recentUsers = [ serveruser ];
		}
		else
		{
			// Add user to the cookie and pop oldest if necessary
			var recentUsers = recentUsersString.split( '|' );
			if (recentUsers.indexOf( serveruser ) != -1)
			{
				// User is already in list, move to first position
				var element = recentUsers[recentUsers.indexOf( serveruser )]
				recentUsers.splice(recentUsers.indexOf( serveruser ), 1);
				recentUsers.splice(0, 0, element);
			}
			else
			{
				if (recentUsers.length == 5)
				{
					recentUsers.pop();
				}
				recentUsers.unshift( serveruser );
			}
		}
		jQuery.cookie( 'recentUsers', recentUsers.join( '|' ), { path: '/' } );
	}
	
	var url = given_url || document.location.href;
	if (url.match( /(\W)user=(\w+)/ ))
	{
		// urls with an existing user=xxx param
		url = url.replace( /(\W)user=(\w+)/, '$1user=' + serveruser );
	}
	else if (url.match( /\?/ ))
	{
		// urls with existing query params
		url = url.replace( '?', '?user=' + serveruser + ';' );
	}
	else if (url.match( /#/ ))
	{
		// urls with #hash
		url = url.replace( '#', '?user=' + serveruser + '#' );
	}
	else
	{
		// a bare url
		url += '?user=' + serveruser;
	}

	if (jQuery( BW ).data( 'events' ) && 
		jQuery( BW ).data( 'events' ).userChanged)
	{
		// If a userChanged event has been added, trigger that
		jQuery( BW ).trigger( 'userChanged', [ serveruser ] );
	}
	else 
	{
		// Else change user as normal
		document.location = url;
	}
};


BW.User.prototype.revertServerUser = function()
{
	return this.switchServerUser( this.serverUser );
};


BW.User.prototype.toggleShowingUserProfile = function( /*jQuery.Event*/ ev )
{
	var el = jQuery( 'html' );
	if (el.hasClass( 'showing-user-profile' ))
	{
		el.removeClass( 'showing-user-profile' );
		return true;
	}
	else
	{
		el.addClass( 'showing-user-profile' );
		jQuery( document ).one( 'click',
			this.toggleShowingUserProfile.bind( this ) );

		// ev.preventImmediatePropagation();
		return false;
	}
}


BW.User.prototype.showFeedbackDialog = function( exceptionTime )
{
	var dialog = jQuery( '.user-feedback-dialog' );
	console.assert( dialog[0] );
	var setFeedbackSending = this.setFeedbackSending;

	dialog.keypress( function( event )
	{
		event.stopPropagation();
	});

	var disabledOKButton = jQuery( '#user-feedback-disabled-OK' )
	disabledOKButton.on( 'click', function()
	{
		jQuery( 'html' ).removeClass( 'user-feedback-dialog-showing' );
	});

	var sentOKButton = jQuery( '#user-feedback-sent-OK' )
	sentOKButton.on( 'click', function()
	{
		jQuery( 'html' ).removeClass(
			'user-feedback-dialog-showing' );
	});

	jQuery.getJSON( '/getFeedbackData', function( /*User Object*/ response )
	{
		var sendEmailAjaxRequest = null;
		var feedbackDisabledMessage = jQuery( '#user-feedback-disabled-message' );
		var feedbackEntryForm = jQuery( '#user-feedback-form' );

		if (!response.isEnabled || !response.isSmtpServiceOk)
		{
			// Show feedback error message
			var errorMsg;

			if ( !response.isEnabled )
			{
				// User feedback is not enabled
				errorMsg = "User feedback is not currently enabled. "
							+ "Please contact your administrator to have it "
							+ "configured."
			}
			else
			{
				// User feedback is enabled, but configured SMTP service is not
				// accessible at the moment
				errorMsg = "User feedback is not currently available because "
			 				+ "the configured SMTP service is not accessible. "
							+ "Please contact your administrator to check the "
							+ "configuration.";
			}

			feedbackDisabledMessage.find( ".error-message" ).text( errorMsg )
			feedbackDisabledMessage.show();
			feedbackEntryForm.hide();
			jQuery( 'html' ).addClass( 'user-feedback-dialog-showing' );

			return;
		}
		else
		{
			feedbackDisabledMessage.hide();
			feedbackEntryForm.show();
		}

		var sentSection = jQuery( '#user-feedback-sent' );
		var returnEmailRow = jQuery( '#user-feedback-email-row' );
		var commentsRow = jQuery( '#user-feedback-comments-row' );
		var infoRow = jQuery( '#user-feedback-info-row' );
		var actionsBar = jQuery( '#user-feedback-actions-bar' );
		var subjectField = jQuery( '#user-feedback-subject' );
		var returnEmailField = jQuery( '#user-feedback-address' );
		var commentsField = jQuery( '#user-feedback-comments' );
		var attachedInfoField = jQuery( '#user-feedback-attached' );
		var sendButton = jQuery( '#user-feedback-button-send' );
		var cancelButton = jQuery( '#user-feedback-button-cancel' );

		// Initialise the display, in case of a previous cancel/send
		sentSection.hide();
		returnEmailRow.show();
		commentsRow.show();
		infoRow.show();
		actionsBar.show();
		setFeedbackSending( false );
		subjectField.val( document.title + " User Feedback" );
		commentsField.val( "" );

		// returnEmailField is not cleared - it is OK to leave any previously
		// entered value for user convenience

		var attachedInfoFieldText = '';
		if (response.attachedInfo)
		{
			attachedInfoFieldText += response.attachedInfo;
		}
		
		var exceptionData = '';
		if (exceptionTime) 
		{
			subjectField.val( subjectField.val() + ' - Exception' );
			
			var exceptionName = jQuery( '#exceptionName' ).text();
			
			if (exceptionName)
			{
				exceptionData = { 'exception': exceptionName };
				attachedInfoFieldText += '\n\nException Raised: ' + exceptionName;
			}
			
			if (exceptionTime) 
			{
				attachedInfoFieldText += '\nTime: ' + exceptionTime;
				exceptionData.time = exceptionTime;
			}
		
			var stackTrace = jQuery( '#stacktrace pre' ).text();

			if (stackTrace)
			{
				attachedInfoFieldText += '\n\nStack Trace:\n' + stackTrace;
				exceptionData.stackTrace = stackTrace;
			}
		}
		
		if (attachedInfoFieldText !== '') 
		{
			attachedInfoField.val( attachedInfoFieldText );
		}

		// Once configured, display the dialog
		jQuery( 'html' ).addClass( 'user-feedback-dialog-showing' );

		sendButton.on( 'click', function( event )
		{
			event.preventDefault();

			jQuery( '.user-feedback-error' ).hide();
			var hasError = false;


			// Validate the user-entered data:
			// Subject
			var subjectVal = subjectField.val();
			if (subjectVal == "")
			{
				jQuery( '#user-feedback-subject' ).after(
					'<span class="user-feedback-error">' +
					'<div class="message">Please enter a subject.' +
					'</div><span>' );
				hasError = true;
			}

			// Return Email
			var returnEmailVal = returnEmailField.val();

			// This is not a serious email regex because, frankly, it is not
			// recommended to do so. Just look for a simple anything@anything
			// address to ensure the user hasn't done anything obviously wrong
			// (like enter their street address) and be done with it.
			var emailReg = /\S+@\S+/;

			if (returnEmailVal != "" && !emailReg.test( returnEmailVal ))
			{
				jQuery( '#user-feedback-address' ).after(
					'<span class="user-feedback-error">' +
					'<div class="message">Invalid email address.' +
					'</div><span>' );
				hasError = true;
			}

			// Comments
			var commentsVal = jQuery( '#user-feedback-comments' ).val();
			if (commentsVal == "")
			{
				jQuery( '#user-feedback-comments' ).after(
					'<span class="user-feedback-error">' +
					'<div class="message">Feedback comments required.' +
					'</div><span>' );
				hasError = true;
			}


			// Finished validation, send the email if no errors occurred
			if (!hasError)
			{
				setFeedbackSending( true );

				var subjectText = "[WebConsole Feedback] " + subjectVal;
				var getData = { 'subject': subjectText,
						'returnAddress': returnEmailVal,
						'comments': commentsVal,
						'exceptionData': exceptionData };
				
				if (exceptionData !== '') 
				{
					getData.exceptionData = JSON.stringify( exceptionData );
				}

				sendEmailAjaxRequest = jQuery.ajax(
				{
					url: '/sendFeedbackEmail',
					data: getData,
					success: function( /*String*/ successStatus )
					{
						sentSection.show();
						if (returnEmailVal == "")
						{
							returnEmailRow.hide();
						}
						infoRow.hide();
						actionsBar.hide();
					}.bind( this ),
					error: function( xhr, error, thrown )
					{
						jQuery( '#user-feedback-table' ).after(
							'<span class="user-feedback-error">' +
							'<div class="message">An error occurred while ' +
							'sending. Contact your administrator.</div><span>'
							);

						// Reenable the send button to allow retries
						setFeedbackSending( false );

						// Clear the ajax request variable so that we do not
						// try to perform any actions on it
						sendEmailAjaxRequest = null;
					}.bind( this )
				} );
			}
		});

		// Cancel Button
		cancelButton.on( 'click', function()
		{
			// If sending then stop waiting and reenable the screen fields
			if (sendEmailAjaxRequest)
			{
				// Note that although this aborts the ajax query, the server
				// may or may not continue attempting to complete the query in
				// the background
				sendEmailAjaxRequest.abort();
				setFeedbackSending( false );
				sendEmailAjaxRequest = null;
			}
			else
			{
				jQuery( 'html' ).removeClass( 'user-feedback-dialog-showing' );
			}
		});
	});
};


/**
* Adjusts the display of the user feedback dialog based upon whether an email
* is currently being sent
*/
BW.User.prototype.setFeedbackSending = function( /*bool*/ sending )
{
	var subjectField = jQuery( '#user-feedback-subject' );
	var returnEmailField = jQuery( '#user-feedback-address' );
	var commentsField = jQuery( '#user-feedback-comments' );
	var sendButton = jQuery( '#user-feedback-button-send' );

	if (sending)
	{
		subjectField.prop( 'disabled', true );
		returnEmailField.prop( 'disabled', true );
		commentsField.prop( 'disabled', true );
		sendButton.prop( 'disabled', true );
		sendButton.addClass( 'disabled' );
		sendButton.text( "Sending..." );
	}
	else
	{
		subjectField.prop( 'disabled', false );
		returnEmailField.prop( 'disabled', false );
		commentsField.prop( 'disabled', false );
		sendButton.prop( 'disabled', false );
		sendButton.removeClass( 'disabled' );
		sendButton.text( "Send" );
	}
};

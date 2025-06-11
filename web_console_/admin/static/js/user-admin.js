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

var UserAdmin= window.UserAdmin || {}; //just for namespace


function initAddUser()
{
	// if auth by LDAP is not enabled, just return
	if (!authByLdapEnabled)
	{
		return;
	}

	var addUser = new UserAdmin.AddUser();
	
	addUser.init();
}


/* function for handling ajax error*/
UserAdmin.ajaxError = function( jqxhr, /*String*/ textStatus,
						 /*String?*/ errorThrown )
{
	if (textStatus === 'timeout')
	{
		new Alert.Warning( 'Ajax request timed out' );
	}
	else
	{
		//the ajax error may be reported when leaving this page
		//ignore such kind of error by checking whether the status is 0
		new Alert.Error( 'Web Console appears to be down', {
			id: 'ajax-error',
			duration: '5000',
		} );
		console.warn( "failed to perform ajax request: %s ", textStatus,
						errorThrown );
	 }
};


UserAdmin.AddUser = function()
{
	this.domUserName = jQuery( ".user-name" );

	this.domServerUserContainer = jQuery( ".server-user-container" );
	this.domServerUserName = jQuery( ".server-user-name" );

	this.domAddButton = jQuery( ".commit-add" );
	this.domEditButton = jQuery( ".commit-edit" );
}; 


UserAdmin.AddUser.Defaults = 
{
	// time in ms, how long to wait since last typing before querying LDAP
	doneTypingInterval: 500, 

	queryLdapUserUrl: "queryLdapUser"
};

UserAdmin.AddUser.prototype.init = function()
{
	this.options = UserAdmin.AddUser.Defaults;

	this.domUserName.on( "change keyup input paste",
						this._startQueryTimer.bind( this ) );
	this.domUserName.keydown( this._cancelQueryTimer.bind( this ) );
	
	if (this.domAddButton)
	{
		this.domAddButton.attr( "disabled", "disabled" );
	}

	this.queryTimer = null;
};


UserAdmin.AddUser.prototype._startQueryTimer = function()
{
	if (this.queryTimer)
	{
		this._cancelQueryTimer();
	}

	this.queryTimer = window.setTimeout( this._queryLdapUser.bind( this ),
								this.options.doneTypingInterval );
};


UserAdmin.AddUser.prototype._cancelQueryTimer = function()
{
	if (this.queryTimer)
	{
		window.clearTimeout( this.queryTimer );
		this.queryTimer = null;
	}
};


UserAdmin.AddUser.prototype._queryLdapUser = function()
{
	var userName = this.domUserName.val().trim();
	
	if (!userName)
	{
		return;
	}
	
	this.domServerUserContainer.addClass( "query-in-progress" );

	jQuery.ajax( {
		url: this.options.queryLdapUserUrl,
		data: { 'userName': userName },
		dataType: 'json',
		success: function( /*Map*/ data, /*String*/ textStatus, jqxhr )
		{
			if (this.options.debug)
			{
				console.log( " query LDAP account successfully " );
			}

			this._queryLdapSuccess( data.serverUser );

		}.bind( this ),
		error: function( jqxhr, textStatus, errorThrown )
		{
			console.log( "Failed to query LDAP account" );
			this._queryLdapFailure( jqxhr, textStatus, errorThrown );
		}.bind( this )
	} );
};


UserAdmin.AddUser.prototype._queryLdapSuccess = function( /*String*/ serverUser )
{
	this.domServerUserContainer.removeClass( "query-in-progress" );
	this.domServerUserName.removeClass( "server-user-error" );
	this.domServerUserName.text( serverUser );

	if (this.domAddButton)
	{
		this.domAddButton.removeAttr( "disabled" );
	}

	if (this.domEditButton)
	{
		this.domEditButton.removeAttr( "disabled" );
	}
};


UserAdmin.AddUser.prototype._queryLdapFailure =
function( jqxhr, /*String*/ textStatus, /*String?*/ errorThrown )
{
	this.domServerUserContainer.removeClass( "query-in-progress" );

	if (this.domAddButton)
	{
		this.domAddButton.attr( "disabled", "disabled" );
	}

	if (this.domEditButton)
	{
		this.domEditButton.attr( "disabled", "disabled" );
	}

	var responseJson = JSON.parse( jqxhr.responseText );
	var exceptionType = responseJson.exception;
	var message = responseJson.message;

	if(exceptionType == "LdapUserNotExists")
	{
		this.domServerUserName.addClass( "server-user-error" );
		this.domServerUserName.text( "No such LDAP user" );
	}
	else if(exceptionType == "ServerUserNotExists")
	{
		this.domServerUserName.addClass( "server-user-error" );
		this.domServerUserName.text( "No server user attribute" );
	}
	else
	{
		UserAdmin.ajaxError( jqxhr, textStatus, errorThrown );
	}
	
	jqxhr.bwExceptionHandled = true;
};


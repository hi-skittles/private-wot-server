"use strict";

function onSelectMachines( elt )
{
	var singleRadioButton = document.getElementById( "ccStartMachineMode" );
	var groupRadioButton = document.getElementById( "ccStartGroupMode" );
	var layoutRadioButton = document.getElementById( "ccStartLayoutMode" );

	// If no form element passed, work out which one to use from the radio button
	if (elt == null)
	{
		if (singleRadioButton.checked)
			elt = document.startForm.machine;
		else if (groupRadioButton.checked)
			elt = document.startForm.group;
		else if (layoutRadioButton.checked)
			elt = document.startForm.layout;
		else
		{
			Util.error( "No radio button selected!" );
			return;
		}
	}

	var restrictCheckBox =  document.startForm.restrict;
	restrictCheckBox.disabled = true;

	var radiobutton;
	if (elt.name == "machine")
		radiobutton = singleRadioButton;
	else if (elt.name == "layout")
		radiobutton = layoutRadioButton;
	else if (elt.name == "group")
	{
		radiobutton = groupRadioButton;
		restrictCheckBox.disabled = false;
	}
	else
	{
		Util.error( "onSelectMachines:: no radiobutton for " + elt.name );
		return;
	}

	radiobutton.checked = true;
	verifyEnv( elt );
}

function verifyEnv( elt )
{
	var url = '/cc/verifyEnv'
			+ '?type=' + elt.name
			+ ';value=' + elt.value;

	jQuery.ajax({
		url: url,
		dataType: 'json',
		success: function( /*Object*/ data, /*String*/ textStatus, jqXhr )
		{
			var nonFatalError = data._error || data.error || data.warning;
			if (nonFatalError)
			{
				console.log( "Env check (%s) failed:", url );
				console.dir( data );
				// todo: new Alert.Warning( nonFatalError, { targetDiv: 'body', id: true } );
				alert( "Environment check failed: " + nonFatalError );
			}
			setEnv( data.mfroot, data.bwrespath );
			document.getElementById( "ccStartSubmit" ).disabled = false;
		},
		error: function( jqXHR, /*String*/ textStatus, /*String*/ errorThrown )
		{
			// fallback for programming errors and unchecked params
			console.error( "Ajax call to %s failed: %s", url, textStatus );
			setEnv( "<error>", "<error>" );
			document.getElementById( "ccStartSubmit" ).disabled = true;
		},
	});
}

function setEnv( mfroot, bwrespath )
{
	bwrespath = (bwrespath || '').replace( /:/g, "<br/>" );
	jQuery( '#ccStartMFRoot' ).html( mfroot );
	jQuery( '#ccStartBWResPath' ).html( bwrespath );
}

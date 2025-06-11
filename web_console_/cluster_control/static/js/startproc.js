/**
 * Used to enable or disable the text entry field for the number of processes
 * to start. We shouldn't present this an input option for the singleton
 * processes as it doesn't make sense.
 */
function enableInputIfNotSingleton( value )
{
	if ((value == "baseappmgr") || (value == "cellappmgr") ||
		(value == "dbappmgr") || (value == "dbmgr"))
	{
		document.startProcForm.count.value = 1;
		document.startProcForm.count.disabled = true;
	}
	else
	{
		document.startProcForm.count.disabled = false;
	}
}


/**
 * Attached to the page 'onLoad' event to ensure that after the preferences
 * for the user are applied and the last used process type has been set, the
 * input field is updated accordingly.
 */
function onLoadSetEnableStatus()
{
	enableInputIfNotSingleton( document.startProcForm.pname.value );
}


/**
 * This function is provided so that when we use KID template mechanisms
 * for automatically generating <select> blocks, we can pass through a no-op
 * function for the 'onChange' event.
 */
function nullFunc( nullArg )
{}

window.addEventListener( "load", onLoadSetEnableStatus, false );

/*
Macromedia(r) Flash(r) JavaScript Integration Kit License


Copyright (c) 2005 Macromedia, inc. All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
this list of conditions and the following disclaimer in the documentation and/or
other materials provided with the distribution.

3. The end-user documentation included with the redistribution, if any, must
include the following acknowledgment:

"This product includes software developed by Macromedia, Inc.
(http://www.macromedia.com)."

Alternately, this acknowledgment may appear in the software itself, if and
wherever such third-party acknowledgments normally appear.

4. The name Macromedia must not be used to endorse or promote products derived
from this software without prior written permission. For written permission,
please contact devrelations@macromedia.com.

5. Products derived from this software may not be called "Macromedia" or
"Macromedia Flash", nor may "Macromedia" or "Macromedia Flash" appear in their
name.

THIS SOFTWARE IS PROVIDED "AS IS" AND ANY EXPRESSED OR IMPLIED WARRANTIES,
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL MACROMEDIA OR
ITS CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT
OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH
DAMAGE.

--

This code is part of the Flash / JavaScript Integration Kit:
http://www.macromedia.com/go/flashjavascript/

Created by:

Christian Cantrell
http://weblogs.macromedia.com/cantrell/
mailto:cantrell@macromedia.com

Mike Chambers
http://weblogs.macromedia.com/mesh/
mailto:mesh@macromedia.com

Macromedia
*/

/**
 * The FlashProxy object is what proxies function calls between JavaScript and Flash.
 * It handles all argument serialization.
 */

/**
 * Instantiates a new FlashProxy object.
 * lcId: Each FlashProxy needs a unique lcId. This will need to get passed into your Flash content, as well.
 * flashId: the ID or name of your Flash content. This is required to make FSCommand work.
 * proxySwfName: the name (including the path) of the Flash proxy SWF.
 * callbackScope (optional): The scope where you want calls from Flash to JavaScript to go. This argument
 * is optional. If you leave it out, calls will be made on the document level.
 */
function FlashProxy(lcId, flashId, proxySwfName, callbackScope)
{
	FlashProxy.fpmap[lcId] = this;
    this.uid = lcId;
    this.proxySwfName = proxySwfName;
    this.callbackScope = callbackScope;
    this.flashSerializer = new FlashSerializer(false);
    this.q = new Array();

    if (navigator.appName.indexOf ('Internet Explorer') != -1 &&
        navigator.platform.indexOf('Win') != -1 &&
        navigator.userAgent.indexOf('Opera') == -1)
    {
	    setUpVBCallback(flashId);
	}
}

/**
 * Call a function in your Flash content.  Arguments should be:
 * 1. ActionScript function name to call,
 * 2. any number of additional arguments of type object,
 *    array, string, number, boolean, date, null, or undefined. 
 */
FlashProxy.prototype.call = function()
{
    if (arguments.length == 0)
    {
        throw new Exception("Flash Proxy Exception",
                            "The first argument should be the function name followed by any number of additional arguments.");
    }
    
    this.q.push(arguments);
    
    if (this.q.length == 1)
    {
		this._execute(arguments);
    }
}

/**
 * "Private" function.  Don't call.
 */
FlashProxy.prototype._execute = function(args)
{
    var ft = new FlashTag(this.proxySwfName, 1, 1, '6,0,65,0');
    ft.addFlashVar('lcId', this.uid);
    ft.addFlashVar('functionName', args[0]);
    ft.addFlashVar('allowScriptAccess', 'always');
    if (args.length > 1)
    {
        var justArgs = new Array();
        for (var i = 1; i < args.length; ++i)
        {
            justArgs.push(args[i]);
        }
        ft.addFlashVars(this.flashSerializer.serialize(justArgs));
    }

    var divName = '_flash_proxy_' + this.uid;
    if(!document.getElementById(divName))
    {
        var newTarget = document.createElement("div");
        newTarget.id = divName;
        document.body.appendChild(newTarget);
    }
	var target = document.getElementById(divName);
    target.innerHTML = ft.toString();
}

/**
 * This is the function that proxies function calls from Flash to JavaScript.
 * It is called implicitly, so you won't ever need to call it.
 */
FlashProxy.callJS = function(command, args)
{
	var argsArray = eval(args);
	//alert("argsArray " + argsArray[0]);
	var scope = FlashProxy.fpmap[argsArray.shift()].callbackScope;

    if(scope && (command.indexOf('.') < 0))
	{
		var functionToCall = scope[command];
		functionToCall.apply(scope, argsArray);
	}
	else
	{
    	var functionToCall = eval(command);
		functionToCall.apply(functionToCall, argsArray);
	}
}

/**
 * This function gets called when a Flash function call is complete. It checks the
 * queue and figures out whether there is another call to make.
 */
FlashProxy.callComplete = function(uid)
{
	var fp = FlashProxy.fpmap[uid];
	if (fp != null)
	{
		fp.q.shift();
		if (fp.q.length > 0)
		{
			fp._execute(fp.q[0]);
		}
	}
}

FlashProxy.fpmap = new Object();

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
 * Generates a browser-specific Flash tag. Create a new instance, set whatever
 * properties you need, then call either toString() to get the tag as a string, or
 * call write() to write the tag out.
 *
 * The properties src, width, height and version are required when creating a new
 * instance of the FlashTag, but there are setters to let you change them, as well.
 * That way, if you want to render more than one piece of Flash content, you can do
 * so without creating a new instance of the tag.
 *
 * For more information on supported parameters, see:
 * http://www.macromedia.com/cfusion/knowledgebase/index.cfm?id=tn_12701
 */


/**
 * Creates a new instance of the FlashTag.
 * src: The path to the SWF file.
 * width: The width of your Flash content.
 * height: the height of your Flash content.
 * version: the required version of the Flash Player for the specified content.
 *
 * These are the only 4 properites that are required.
 */
function FlashTag(src, width, height, version)
{
    if (arguments.length < 4)
    {
        throw new Exception('RequiredParameterException',
                            'You must pass in a src, width, height, and version when creating a FlashTag.');
    }

    // Required
    this.src            =  src;
    this.width          =  width;
    this.height         =  height;
    this.version        =  version;

    this.id             =  null;
    this.flashVars      =  null;
    this.flashVarsStr   =  null;
    this.genericParam   = new Object();
    this.ie = (navigator.appName.indexOf ("Microsoft") != -1) ? 1 : 0;
}

/**
 * Specifies the location (URL) of the Flash content to be loaded.
 */
FlashTag.prototype.setSource = function(src)
{
    this.src = src; 
}

/**
 * Specifies the width of the Flash content in either pixels or percentage of browser window. 
 */
FlashTag.prototype.setWidth = function(w)
{
    this.width = w; 
}

/**
 * Specifies the height of the Flash content in either pixels or percentage of browser window. 
 */
FlashTag.prototype.setHeight = function(h)
{
    this.h = h; 
}

/**
 * The required version of the Flash Player for the specified content. 
 */
FlashTag.prototype.setVersion = function(v)
{
    this.version = v;
}

/**
 * Identifies the Flash content to the host environment (a web browser, for example) so that
 * it can be referenced using a scripting language. This value will be used for both the 'id'
 * and 'name' attributes depending on the client platform and whether the object or the embed
 * tag are used.
 */
FlashTag.prototype.setId = function(id)
{
    this.id = id;
}

/**
 * Specifies the background color of the Flash content. Use this attribute to override the background
 * color setting specified in the Flash file. This attribute does not affect the background
 * color of the HTML page. 
 */
FlashTag.prototype.setBgcolor = function(bgc)
{
    if (bgc.charAt(0) != '#')
    {
        bgc = '#' + bgc;
    }
    this.genericParam['bgcolor'] = bgc;
}

/**
 * Allows you to set multiple Flash vars at once rather than adding them one at a time. The string
 * you pass in should contain all your Flash vars, properly URL encoded. This function can be used in
 * conjunction with addFlashVar.
 */
FlashTag.prototype.addFlashVars = function(fvs)
{
    this.flashVarsStr = fvs;
}

/**
 * Used to send root level variables to the Flash content. You can add as many name/value pairs as
 * you want. The formatting of the Flash vars (turning them into a query string) is handled automatically.
 */
FlashTag.prototype.addFlashVar = function(n, v)
{
    if (this.flashVars == null)
    {
        this.flashVars = new Object();
    }

    this.flashVars[n] = v;
}

/**
 * Used to remove Flash vars. This is primarily useful if you want to reuse an instance of the FlashTag
 * but you don't want to send the same variables to more than one piece of Flash content. 
 */
FlashTag.prototype.removeFlashVar = function(n)
{
    if (this.flashVars != null)
    {
        this.flashVars[n] = null;
    }
}

/**
 * (true, false) Specifies whether the browser should start Java when loading the Flash Player for the first time.
 * The default value is false if this property is not set. 
 */
FlashTag.prototype.setSwliveconnect = function(swlc)
{
    this.genericParam['swliveconnect'] = swlc;
}

/**
 * (true, false) Specifies whether the Flash content begins playing immediately on loading in the browser.
 * The default value is true if this property is not set. 
 */
FlashTag.prototype.setPlay = function(p)
{
    this.genericParam['play'] = p;
}

/**
 * (true, false) Specifies whether the Flash content repeats indefinitely or stops when it reaches the last frame.
 * The default value is true if this property is not set. 
 */
FlashTag.prototype.setLoop = function(l)
{
    this.genericParam['loop'] = l;
}

/**
 * (true,false) Whether or not to display the full Flash menu. If false, displays a menu that contains only
 * the Settings and the About Flash options. 
 */
FlashTag.prototype.setMenu = function(m)
{
    this.genericParam['menu'] = m;
}

/**
 * (low, high, autolow, autohigh, best) Sets the quality at which the Flash content plays.
 */
FlashTag.prototype.setQuality = function(q)
{
    if (q != 'low' && q != 'high' && q != 'autolow' && q != 'autohigh' && q != 'best')
    {
        throw new Exception('UnsupportedValueException',
                            'Supported values are "low", "high", "autolow", "autohigh", and "best".');
    }
    this.genericParam['quality'] = q;
}

/**
 * (showall, noborder, exactfit) Determins how the Flash content scales.
 */
FlashTag.prototype.setScale = function(sc)
{
    if (sc != 'showall' && sc != 'noborder' && sc != 'exactfit' && sc != 'noscale')
    {
        throw new Exception('UnsupportedValueException',
                            'Supported values are "showall", "noborder", "noscale" and "exactfit".');
    }
    this.genericParam['scale'] = sc;
}

/**
 * (l, t, r, b) Align the Flash content along the corresponding edge of the browser window and crop
 * the remaining three sides as needed.
 */
FlashTag.prototype.setAlign= function(a)
{
    if (a != 'l' && a != 't' && a != 'r' && a != 'b' && a != 'middle')
    {
        throw new Exception('UnsupportedValueException',
                            'Supported values are "l", "t", "r" and "b".');
    }
    this.genericParam['align'] = a;
}

/**
 * (l, t, r, b, tl, tr, bl, br) Align the Flash content along the corresponding edge of the browser
 * window and crop the remaining three sides as needed.
 */
FlashTag.prototype.setSalign= function(sa)
{
    if (sa != 'l' && sa != 't' && sa != 'r' && sa != 'b' && sa != 'tl' && sa != 'tr' && sa != 'bl' && sa != 'br')
    {
        throw new Exception('UnsupportedValueException',
                            'Supported values are "l", "t", "r", "b", "tl", "tr", "bl" and "br".');
    }
    this.genericParam['salign'] = sa;
}

/**
 * (window, opaque, transparent) Sets the Window Mode property of the Flash content for transparency,
 * layering, and positioning in the browser. 
 */
FlashTag.prototype.setWmode = function(wm)
{
    if (wm != 'window' && wm != 'opaque' && wm != 'transparent')
    {
        throw new Exception('UnsupportedValueException',
                            'Supported values are "window", "opaque", and "transparent".');
    }
    this.genericParam['wmode'] = wm;
}

/**
 * Specifies the base directory or URL used to resolve all relative path statements in your Flash content.
 */
FlashTag.prototype.setBase = function(base)
{
    this.genericParam['base'] = base;
}

/**
 * (never, always) Controls the ability to perform outbound scripting from within Flash content. 
 */
FlashTag.prototype.setAllowScriptAccess = function(sa)
{
    if (sa != 'never' && sa != 'always')
    {
        throw new Exception('UnsupportedValueException',
                            'Supported values are "never" and "always".');
    }
    this.genericParam['allowScriptAccess'] = sa;
}

/**
 * Get the Flash tag as a string. 
 */
FlashTag.prototype.toString = function()
{
    var flashTag = new String();
    if (this.ie)
    {
        flashTag += '<object classid="clsid:D27CDB6E-AE6D-11cf-96B8-444553540000" ';
        if (this.id != null)
        {
            flashTag += 'id="'+this.id+'" ';
        }
        flashTag += 'codebase="http://download.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version='+this.version+'" ';
        flashTag += 'width="'+this.width+'" ';
        flashTag += 'height="'+this.height+'">';
        flashTag += '<param name="movie" value="'+this.src+'"/>';

        for (var n in this.genericParam)
        {
            if (this.genericParam[n] != null)
            {
                flashTag += '<param name="'+n+'" value="'+this.genericParam[n]+'"/>';
            }
        }

        if (this.flashVars != null)
        {
            var fv = this.getFlashVarsAsString();
            if (fv.length > 0)
            {
                flashTag += '<param name="flashvars" value="'+fv+'"/>';
            }
        }
        flashTag += '</object>';
    }
    else
    {
        flashTag += '<embed src="'+this.src+'"';
        flashTag += ' width="'+this.width+'"';
        flashTag += ' height="'+this.height+'"';
        flashTag += ' type="application/x-shockwave-flash"';
        if (this.id != null)
        {
            flashTag += ' name="'+this.id+'"';
            flashTag += ' id="'+this.id+'" ';
        }

        for (var n in this.genericParam)
        {
            if (this.genericParam[n] != null)
            {
                flashTag += (' '+n+'="'+this.genericParam[n]+'"');
            }
        }

        if (this.flashVars != null)
        {
            var fv = this.getFlashVarsAsString();
            if (fv.length > 0)
            {
                flashTag += ' flashvars="'+fv+'"';
            }
        }
        flashTag += ' pluginspage="http://www.macromedia.com/go/getflashplayer">';
        flashTag += '</embed>';
    }
    return flashTag;
}

/**
 * Write the Flash tag out. Pass in a reference to the document to write to. 
 */
FlashTag.prototype.write = function(doc)
{
    doc.write(this.toString());
}

/**
 * Write the Flash tag out. Pass in a reference to the document to write to. 
 */
FlashTag.prototype.getFlashVarsAsString = function()
{
    var qs = new String();
    for (var n in this.flashVars)
    {
        if (this.flashVars[n] != null)
        {
            qs += (escape(n)+'='+escape(this.flashVars[n])+'&');
        }
    }

    if (this.flashVarsStr != null)
    {
        return qs + this.flashVarsStr;
    }

    return qs.substring(0, qs.length-1);
}

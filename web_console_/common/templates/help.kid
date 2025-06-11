<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">

<html xmlns="http://www.w3.org/1999/xhtml"
	xmlns:py="http://purl.org/kid/ns#"
	py:layout="'../../common/templates/layout_css.kid'"
	py:extends="'../../common/templates/common.kid'"
	xml:lang="en" lang="en">

<div py:def="moduleContent()" class="help content">

<div class="help-body"
    py:if="not defined( 'helpFormat' )"
    py:content="document( helpContent )"></div>

    
<!--!~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ docbook ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~-->
<div py:strip="True" py:if="defined( 'helpFormat' ) and helpFormat == 'docbook'">
<div class="help-body docbook" py:content="document( helpContent )"></div>
<script type="text/javascript" src="/static/js/help_docbook.js"></script>
<link rel="stylesheet" type="text/css" href="/static/css/docbook.css" />
</div>


<!--!~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ markdown ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~-->    
<div class="help-body ${helpFormat}" py:if="defined( 'helpFormat' ) and helpFormat == 'markdown'">
<pre>
${ helpContent }
</pre>

<script type="text/javascript">//<![CDATA[

    // transcode content of 'helpFrame' iframe from markdown to HTML
    jQuery( document ).ready( function()
    {
        // dynamically load markdown transcoding lib
        jQuery.getScript( '/static/third_party/marked.js', function()
        {
            var markdownSource = jQuery( '.help-body pre' ).text();
            console.log( markdownSource );

            var markdownHtml = marked( markdownSource );
            //console.dir( markdownHtml );

            jQuery( '.help-body' ).empty().append( markdownHtml );

            createTableOfContents();
        });
    });

// ]]>
</script>
</div>


<script type="text/javascript">//<![CDATA[

    document.title = "${ helpTopic.title() } Help - WebConsole";

    /** Dynamically create table of contents from HTML headings */
    function createTableOfContents()
    {
        var tableOfContents = jQuery( '<div class="toc" ><!-- generated TOC --></div>' );
        tableOfContents.insertAfter( 'h1' );

        jQuery( ".help h2, .help h3, .help h4, .help h5, .help h6" ).each(
            function( /*int*/ i )
            {
                var heading = jQuery( this );
                var headingId = heading.attr( "id" );

                if (!headingId)
                {
                    // if no explicit id, auto-generate one
                    headingId = heading.text().toLowerCase().replace( /\W/g, '_' );
                    heading.attr( "id", headingId );
                }

                var gotoTopLink = jQuery(
                    '<a href="javascript:void(0)" class="scroll-to-top"></a>' );
                gotoTopLink.appendTo( heading );

                tableOfContents.append(
                    '<a class="'
                    + this.nodeName.toLowerCase()
                    + '" href="#'
                    + headingId
                    + '" title="'
                    + heading.text()
                    + '">'
                    + heading.text()
                    + '</a>'
                );
            }
        );

        // a click on a '.scroll-to-top' animates scroll to top of help content
        jQuery( '.help.content' ).on( 'click', '.scroll-to-top', function() {
            jQuery( '.help.content' ).animate( { scrollTop: 0 }, 200 );
        });
    }

    jQuery( document ).ready( createTableOfContents );

// ]]>
</script>

</div>
</html>


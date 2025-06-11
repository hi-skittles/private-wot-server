
var QUERY_LANG_ENABLED = false;


/**
*	Creates and initialises LogViewer search page-specific stuff.
*	Returns the created {LogViewer.QueryForm} instance.
*/
function initLogViewerPage()
{
	jQuery( 'select[name = "show"] option' ).each( function( /*int*/ i )
	{
		var value = jQuery( this ).text()
		if (default_columns.indexOf( value ) != -1)
		{
			jQuery( this ).attr( 'selected', true );
		}
		else
		{
			jQuery( this ).removeAttr( 'selected' );
		}
	});

	queryForm = new LogViewer.QueryForm(
	    '.log-viewer', { serverTimezone: serverTimezone } );

	// saved queries are updated at completion (or termination) of fetch, so
	// no real need to pre-fetch, except perhaps in the case of a very slow
	// initial query.
	// queryForm.requestSavedQueries();

	// permit initialising query page from page location hash
	if (document.location.hash)
	{
		var queryString = document.location.hash.substring( 1 );
		queryForm.loadQueryString( queryString );
	}
	else if (defaultQuery)
	{
		// populate page with user's default query
		queryForm.loadQueryString( defaultQuery );
	}

	queryForm.submit();

	// submitting a query adds that query to browser history so user can
	// use browser back/forwards to page through their log queries.
	// note that 'addToHistory' options needs to be added after first submit
	// else the initial query that populates the page will be added to
	// browser history.
	jQuery( window ).on( 'hashchange', function()
	{
		if (document.location.hash)
		{
			var queryString = document.location.hash.substring( 1 );
			queryForm.loadQueryString( queryString );
		}
	});

	// globally replace 'select' form elements with styled alternative
	jQuery( 'select' ).chosen();

	// set message_logger status on DOM container
	if (isMessageLoggerRunning)
	{
		queryForm.dom.container.addClass( 'message-logger-online' );
	}
	else
	{
		new Alert.Info(
			'Logs are not currently being captured as message_logger is not running'
		);

		queryForm.dom.container.addClass( 'message-logger-offline' );
	}

	// font size ++/--
	jQuery( '.increase-font-size' ).on( 'click', function() {
		var logs = jQuery( '.log-output' );
		logs.css( 'font-size', Math.min( 24, parseInt( logs.css( 'font-size' ) ) + 1 ) );
	});

	jQuery( '.decrease-font-size' ).on( 'click', function() {
		var logs = jQuery( '.log-output' );
		logs.css( 'font-size', Math.max( 5, parseInt( logs.css( 'font-size' ) ) - 1 ) );
	});

	// hitting enter in a input type=text submits form
    queryForm.dom.container.find( 'input:text:not( .chzn-container input )' ).on(
        "keyup", function( ev )
		{
			if (ev.which === 13)
			{
				queryForm.submit();
				ev.preventDefault();
			}
		}
	);

    if (QUERY_LANG_ENABLED)
    	{
    		initQueryLanguageEvents();
    	}
    	else
	{
		jQuery( '.filter-container' ).hide();
	}

	return queryForm;
}


function initQueryLanguageEvents()
{
	var filter = queryForm.dom.container.find( '.filter' );
	var notifications = queryForm.dom.container.find( '.filter-notifications' );

	var parserTimer;
	filter.on( 'keyup', function( /*jQuery.Event*/ ev )
    {
        if (parserTimer)
        {
            clearTimeout( parserTimer );
        }

        jQuery( this ).parent().removeClass( 'syntax-error' );
        parserTimer = setTimeout(
            function() { parseFilter( jQuery( ev.target ) ); }, 500 );
    });

    filter.on( 'keydown', function( /*jQuery.Event*/ ev )
    {
        if (ev.which === 13)
        {
            if (ev.shiftKey)
                queryForm.outputPane.options.tailLogs = true;

            queryForm.submit();
            return false;
        }
    });

    filter.on( 'focus', function() { notifications.fadeIn(); } );

    filter.on( 'blur', function() { notifications.fadeOut(); } );

    // jQuery( document ).one( 'keypress', function() { filter.focus(); });
    filter.focus();

    jQuery( 'form[name = "filters"]' ).on( 'change', syncFormToFilter );
}


function parseFilter( /*jQuery*/ input )
{
    var inputText = input.text().trim();
    if (!inputText) return;
    try
    {
        console.log( "filter input text: '%s'", inputText );
        var query = BW.LogQueryParser.parse( inputText );

        queryForm.dom.container.find( '.filter-notifications' ).empty();
        input.parent().removeClass( 'syntax-error' );

        console.log( "parse result: %O", query );
        queryForm.loadQuery( query.params );
    }
    catch ( /*SyntaxError*/ ex )
    {
        if (ex.offset === undefined)
        {
            console.warn( "Non-syntactic parse error: %s\n%s", ex, ex.stack );
            throw ex;
            return;
        }

        console.dir( ex );
        input.parent().addClass( 'syntax-error' );
        queryForm.dom.container.find( '.filter-notifications' ).html(
            ' '.repeat( ex.offset )
            + '^<p>'
            + ex.message
            + '</p>'
        );
    }
}


function syncFormToFilter()
{
    var q = queryForm.getQuery();
    var params = q.params;
    var fragments = [];

    console.debug( 'syncing query to ql: %O', params );

    var not_yet_implemented = function( p, v ) {
        new Alert.Info( "deserialisation of '" + p + "' not yet supported" );
        return undefined;
    };

    // skip these params, they modify other params
    var skip = {
        regex: true,
    };

    // params that require special case rendering
    var render = {
        category:  function( p, v ) { return '[' + v + ']'; },
        period:    not_yet_implemented,
        queryTime: not_yet_implemented,
        message:   function( p, v ) {
                   return params.regex ? ('/' + v + '/') : ('"' + v + '"');  },
        appid:     function( p, v ) { return '0' + v; },
    };

    for (var param in params)
    {
        if (skip[param]) continue;
        if (param.substr( 0, 7 ) === "negate_") continue;

        var values = params[param];
        console.assert( values !== undefined, param );
        var value = (values instanceof Array) ? values.join( ',' ) : values;

        if (params["negate_" + param])
        {
            fragments.push( 'not' );
        }

        var specialCase = render[param];
        if (specialCase)
        {
            value = specialCase( param, value );
        }

        fragments.push( value );
    }

    var ql = fragments.join( ' ' );
    console.debug( 'ql = %s', ql );

    	var filter = queryForm.dom.container.find( '.filter' );
    	filter.html( ql );
}



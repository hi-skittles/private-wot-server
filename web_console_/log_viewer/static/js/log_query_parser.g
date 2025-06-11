/**
*   log_query_parser.g - a PEG grammar for LogViewer queries
*
*   Grammar is designed for expressiveness - almost all "static"
*   terms in LogViewer query params are tokens, which allows queries to be
*   expressed without type qualifiers. Query type is also inferred by query type
*   literals, eg:
*
*   example input           | inferred query
*   --------------------    | -------------------------------------------------------
*   "string"                | a log message query (string literal)
*   /regex/                 | a log message regexp (regex literal)
*   warning                 | a severity (token)
*   info,warning            | a severity list (expression)
*   <=warning               | a severity range (literal)
*   cellapp                 | a process type (token)
*   [Category]              | a category (category literal)
*   [Category1,Category2]   | a category list (expression)
*   c++                     | a source type (token)
*   12345                   | a process id (integer literal)
*   01234                   | an app id (integer literal with leading '0')
*   date( 2012-01-03 )      | a datetime (datetime literal; any valid JS date is valid)
*   now                     | a datetime (token)
*   startup                 | a datetime (token)
*   beginning               | a datetime (token)
*   +3d                     | a period (period literal), 3 days since lest server startup
*   machine( sgi02 )        | a machine name (literal)
*
*   As in LogViewer and mlcat, the default query terms are:
*   queryTime = 'server startup' and period = 'to now'.
*
*   == Logical operators ==
*
*   The only logical operator in this grammar is AND (since AND is the only
*   logical operator supported by message_logger atm), which is expressed as
*   one or more whitespace characters. All query types except date and period
*   can be negated by preceding the query type expression with "not", eg:
*
*       [Database] not trace c++ not "connection"
*
*   In the above query, only severity = 'trace' and message = 'connection' are
*   negated.
*
*
*   == Examples ==
*
*   1) process type = 'cellapp' and app id = '01' and queryTime = 'now' and period = 'backwards 1 hour'
*
*       cellapp 01 now -1h
*
*   2) process type in set('cellapp', 'serviceapp', 'baseapp', 'loginapp') and severity > 'info' and category in set('Chunk', 'Config')
*
*       apps >info [Chunk,Config]
*
*   3) date = 'Tue 28 May 2013 16:15:23.232' and period = 'forwards 60 minutes'
*
*       date( Tue 28 May 2013 16:15:23.232 ) +60m
*
*   4) category = 'Network' and message = 'received' and process type not in set('cellapp', 'baseapp')
*
*       [Network] "received" not cellapp,baseapp
*
*   5) queryTime = 'server startup' and period = 'forwards 10 minutes'
*
*       +10m
*
*/


/* grammar initialisation code */
{

    var query = {
        params: {},         // logviewer query params
        state: {},          // temporary parse state
        ast: null,          // resulting parse AST
    };

    var severities = ['TRACE', 'DEBUG', 'INFO', 'WARNING', 'ERROR'];

    function set( key, value )
    {
        if (query.state.negate)
        {
            setFlag( "negate_" + key, true );
            delete query.state.negate;
        }
        else
        {
            setFlag( "negate_" + key, false );
        }

        query.params[key] = query.params[key] || [];
        query.params[key].push( value );
        return value;
    }

    function setFlag( flag, value )
    {
        query.params[flag] = (value !== undefined) ? value : true;
        return value;
    }

    function filterRange( /*String*/ op, value, valueList )
    {
         var i = valueList.indexOf( value );
         console.assert( i > -1 );

         var comparator;
         eval( 'comparator = function( j ) { return j ' + op + i + '; }' );

         var matchingList = [];
         for (i in valueList)
         {
             if (!comparator( i )) continue;
             matchingList.push( valueList[i] );
         }
         return matchingList;
    }
}


/*---------------------------------------------------------------------------------
|                               |                                                 |
|            grammar            |       humanised names and grammar actions       |
|                               |                                                 |
---------------------------------------------------------------------------------*/
start = q:query                 { query.ast = q; return query; }

query
    = query_fragment
    (logical_op query_fragment_or_error)*

query_fragment_or_error         "query expression"
    = query_fragment
    / c:.                       { throw new BW.LogQueryParser.SyntaxError( ["query expression"], c, offset, line, column ); }


query_fragment
    = (not_op query_type_or_error)
    / query_type
    / date_query

query_type
    = ( severity_query
    / source_query
    / proc_type_query
    / message_query
    / category_query
    / machine_name_query
    / pid_query
    / appid_query
    )

query_type_or_error
    = query_type
    / c:.                       { throw new BW.LogQueryParser.SyntaxError( ["query expression"], c, offset, line, column ); }

severity_query                  "severity list or range"
    = severity_range
    / severity_list

severity_range
    = op:comparison_op
    x:severity_or_error         { query.params.severity = filterRange( op, x.toUpperCase(), severities ); return [op, x]; }

severity_list
    = severity (comma severity_or_error)*

severity_or_error
    = severity
    / c:.                       { throw new BW.LogQueryParser.SyntaxError( ["severity"], c, offset, line, column ); }

severity                        "severity"
    = x:( "trace"i
        / "debug"i
        / "info"i
        / "warning"i
        / "error"i
        )                       { return set( 'severity', x.toUpperCase() ); }

source_query "source" = source

source                          "source type"
    = "c++"i                    { return set( 'source', 'C++' ); }
    / "script"i                 { return set( 'source', 'Script' ); }
    / "python"i                 { return set( 'source', 'Script' ); }


proc_type_query                 "process type list"
    = proc_type
    (comma proc_type_or_error)*

proc_type                       "process type"
    = "serviceapp"i             { return set( 'procs', 'ServiceApp' ); }
    / "cellappmgr"i             { return set( 'procs', 'CellAppMgr' ); }
    / "baseappmgr"i             { return set( 'procs', 'BaseAppMgr' ); }
    / "cellapp"i                { return set( 'procs', 'CellApp' ); }
    / "baseapp"i                { return set( 'procs', 'BaseApp' ); }
    / "loginapp"i               { return set( 'procs', 'LoginApp' ); }
	/ "dbmgr"i                  { return set( 'procs', 'DBMgr' ); }
    / "dbappmgr"i               { return set( 'procs', 'DBAppMgr' ); }
    / "dbapp"i                  { return set( 'procs', 'DBApp' ); }
    / "mgrs"i                   { return ['BaseAppMgr', 'CellAppMgr', 'DBMgr', 'DBAppMgr'].map( function( x ) { return set( 'procs', x ); } ); }
    / "apps"i                   { return ['BaseApp', 'CellApp', 'LoginApp', 'DBApp', 'ServiceApp'].map( function( x ) { return set( 'procs', x ); } ); }
    / "cells"i                  { return ['CellAppMgr', 'CellApp'].map( function( x ) { return set( 'procs', x ); } ); }
    / "bases"i                  { return ['BaseAppMgr', 'BaseApp'].map( function( x ) { return set( 'procs', x ); } ); }

proc_type_or_error
    = proc_type
    / c:.                       { throw new BW.LogQueryParser.SyntaxError( ["process type"], c, offset, line, column ); }

message_query                   "log message string or regexp"
    = s:string                  { return set( 'message', s ); }
    / r:regexp                  { setFlag( 'regex' ); return set( 'message', r ); }


category_query                  "category list"
    = "["
    ws*
    category_or_error (comma category_or_error)*
    ws*
    close_bracket_or_error

category                        "category"
    = id:identifier             { return set( 'category', id ); }

category_or_error
    = category
    / c:.                       { throw new BW.LogQueryParser.SyntaxError( ["category"], c, offset, line, column ); }

close_bracket_or_error
    = "]"
    / c:.                       { throw new BW.LogQueryParser.SyntaxError( ["closing bracket"], c, offset, line, column ); }


machine_name_query              "machine name expression"
    = 'machine('
    ws*
    m:identifier
    ws*
    ')'                         { return set( 'machine', m ); }


pid_query                       "process id"
    = pid:nonzero_unsigned_integer { return set( 'pid', pid ); }


appid_query                     "app id"
    = "0" a:appid_or_error      { return set( 'appid', a ); }

appid_or_error
    = nonzero_unsigned_integer
    / c:.                       { throw new BW.LogQueryParser.SyntaxError( ["app ID"], c, offset, line, column ); }

date_query                      "date and/or period expression"
    = (datetime_expression ws*)?
    period_expression

datetime_expression
    = specific_date_expression
    / server_startup_expression
    / beginning_of_logs_expression
    / now_expression

specific_date_expression        "date expression"
    = "date(" ws* d:[^)]+ ")"   { var sec = new Date( d.join( '' ) ).getTime() / 1000;
                                  if (isNaN( sec ) || !sec) throw new BW.LogQueryParser.SyntaxError( ["valid date"], d[0], offset, line, column );
                                  return set( 'queryTime', sec ); }

server_startup_expression
    = "startup"                 { return set( 'queryTime', 'server startup' ); }

beginning_of_logs_expression
    = "beginning" !(ws* '-')    { return set( 'queryTime', 'beginning of logs' ); }

now_expression
    = "now" !(ws* '+')          { return set( 'queryTime', 'now' ); }

period_expression
    = period_direction period_magnitude period_unit

period_direction
    = '+-'                      { return set( 'period', 'either side' ); }
    / '+'                       { return set( 'period', 'forwards' );    }
    / '-'                       { return set( 'period', 'backwards' );   }

period_magnitude
    = i:nonzero_unsigned_integer { return set( 'periodValue', i ); }

period_unit
    = ( 's'                     { return set( 'periodUnit', 'seconds' ); }
      / 'm'                     { return set( 'periodUnit', 'minutes' ); }
      / 'h'                     { return set( 'periodUnit', 'hours' ); }
      / 'd'                     { return set( 'periodUnit', 'days' ); }
      )

comparison_op                   "comparison operator"
    = ws*
    o:("<=" / ">=" / "<" / ">")
    ws*                         { return o; }

logical_op                      "whitespace"
    = ws+                       { return "<and>"; }

comma                           "comma"
    = ws* "," ws*               { return "<comma>"; }

not_op
    = ws* "not"i ws+            { query.state.negate = true; return "<not>"; }


identifier
    = letters:[a-zA-Z_]+        { return letters.join( '' ); }

string                          "string"
    = ("\"" id:[^"]+ "\"")      { return id.join( '' ); }

regexp                          "regular expression"
    = "/" re:[^/]+ "/"          { return re.join( '' ); }

nonzero_unsigned_integer
    = a:[1-9] b:[0-9]*          { return parseInt( a + (b || []).join( '' ) ); }

ws                              "whitespace"
    = " "


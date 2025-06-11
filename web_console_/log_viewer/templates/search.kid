<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<?python
  layout_params[ "page_specific_css"] = [ "/static/third_party/jquery-ui/css/jquery-ui.css"
                                        , "/static/third_party/jquery-ui/jquery-ui-timepicker-addon.css"
                                        , "/static/third_party/jquery-chosen/chosen.css"
                                        , "static/css/log_viewer.css"
                                        ]
?>

<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#" xmlns:bw="http://bigworldtech.com.au"
	  py:layout="'../../common/templates/layout_css.kid'"
	  py:extends="'../../common/templates/common.kid'">

<div py:def="moduleContent()" class="content">

	<div class="alert-notification-container"></div>

	<div class="flexboxed log-viewer">

        <div class="bordered query-form-container">

            <h2 class="heading">Log Viewer</h2>

            <div class="filter-container"><div class="filter" contenteditable="true" spellcheck="false"></div><div class="filter-notifications"></div></div>
            <div class="toggle-show-hide-filters" title="Toggle show/hide query filters"><a href="javascript:void()"><i class="icon-caret-up"></i></a></div>

            <div class="query-form-actions">

                <div class="fetch-actions">
                    <button class="fetch-logs">Fetch</button>
                    <button class="tail-logs">Live Output</button>
                </div>

                <!-- Add/save/load filters -->
                <div class="filter-actions">
                    <div class="add-filter dropdown-menu-container">
                        <button class="dropdown-menu-opener">Add Filter</button>
                        <ul class="inactive-queries dropdown-menu"></ul>
                    </div>
                    <div class="load-query dropdown-menu-container">
                        <button class="dropdown-menu-opener">Load Query</button>
                        <ul class="saved-queries dropdown-menu"></ul>
                    </div>
                    <button class="save-current-query ui-action-requires-user-input">Save Query</button>
                </div>

            </div><!-- /query-form-actions -->


            <form name="filters" class="active-queries-container">
            <!--~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            !   Active queries
            !
            !   Query fragments selected by the user. Below is hard-coded default.
            !   Query fragments are shifted between the active and inactive containers
            !   in response to user actions (see methods LogViewer.QueryForm.activateQueryType,
            !   LogViewer.QueryForm.inactivateQueryType, and LogViewer.QueryForm.toggleActive).
            !
            -->
                <!-- !initially empty -->
            </form><!-- /active-queries-container -->

            <form name="inactive-filters" class="inactive-queries-container">
            <!--~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            !   Inactive queries
            !
            !   Note: these are outside the main <form/>; params from these form
            !   elements will not be sent to the server.
            !
            -->
                <!-- appid -->
                <fieldset class="query-fragment" query-type="appid" display-name="App ID">
                    <label class="remove-filter button">Remove</label>
                    <label class="query-type">App ID</label>
                    <select name="negate_appid" class="search-field-disabled">
                        <option selected="true" value="">is</option>
                        <option value="1">is not</option>
                    </select>
                    <input type="text" name="appid" />
                </fieldset>

                <!-- category -->
                <fieldset class="query-fragment" query-type="category" display-name="Category">
                    <label class="remove-filter button">Remove</label>
                    <label class="query-type">Category</label>
                    <select name="negate_category" class="search-field-disabled">
                        <option selected="true" value="">is</option>
                        <option value="1">is not</option>
                    </select>
                    <select name="category" multiple="true" data-placeholder="Select categories...">
                        <option py:for="item in categories" py:if="item">${item}</option>
                    </select>
                </fieldset>

                <!-- context -->
				<fieldset py:if="allowContextFilter" class="query-fragment"
						query-type="context_lines" display-name="Context Lines">
                    <label class="remove-filter button">Remove</label>
                    <label>Output includes</label>
                    <input name="context" value="20" type="text" size="3" />
                    <label>lines of context</label>
                </fieldset>

                <!-- log message -->
                <fieldset class="query-fragment" query-type="message" display-name="Log Text">
                    <label class="remove-filter button">Remove</label>
                    <label class="query-type">Log text</label>
                    <label>contains</label>
                    <select name="regex" class="search-field-disabled">
                        <option value="">exact string</option>
                        <option value="1">regex</option>
                    </select>
                    <input type="text" name="message" />
                    <label>but not</label>
                    <input type="text" name="exclude" />
                    <select name="casesens" class="search-field-disabled">
                        <option value="">case insensitive</option>
                        <option value="1">case sensitive</option>
                    </select>
                </fieldset>

                <!-- machine name -->
                <fieldset class="query-fragment" query-type="machine" display-name="Machine Name">
                    <label class="remove-filter button">Remove</label>
                    <label class="query-type">Machine name</label>
                    <select name="negate_host" class="search-field-disabled">
                        <option selected="true" value="">is</option>
                        <option value="1">is not</option>
                    </select>
                    <select name="host" data-placeholder="Select a machine name...">
                        <option></option>
                        <option py:for="h in hostnames" value="${h}">${h}</option>
                    </select>
                </fieldset>

                <!-- source -->
                <fieldset class="query-fragment" query-type="source" display-name="Message Source">
                    <label class="remove-filter button">Remove</label>
                    <label class="query-type">Message source</label>
                    <select name="negate_source" class="search-field-disabled">
                        <option selected="true" value="">is</option>
                        <option value="1">is not</option>
                    </select>
                    <select name="source" multiple="true" data-placeholder="Select sources...">
                        <option selected="true" py:for="item in message_sources">${item}</option>
                    </select>
                </fieldset>

                <!-- output columns -->
                <fieldset class="query-fragment" query-type="output_columns" display-name="Output Columns">
                    <label class="remove-filter button">Remove</label>
                    <label class="query-type">Output columns</label>
                    <label>are</label>
                    <select name="show" multiple="true" data-placeholder="Select columns...">
                        <option selected="true" py:for="item in output_columns">${item}</option>
                    </select>
                </fieldset>

                <!-- pid -->
                <fieldset class="query-fragment" query-type="pid" display-name="Process ID">
                    <label class="remove-filter button">Remove</label>
                    <label class="query-type">Process ID</label>
                    <select name="negate_pid" class="search-field-disabled">
                        <option selected="true" value="">is</option>
                        <option value="1">is not</option>
                    </select>
                    <input type="text" name="pid" />
                </fieldset>

                <!-- process type -->
                <fieldset class="query-fragment" query-type="process" display-name="Process Type">
                    <label class="remove-filter button">Remove</label>
                    <label class="query-type">Process</label>
                    <select name="negate_procs" class="search-field-disabled">
                        <option selected="true" value="">is</option>
                        <option value="1">is not</option>
                    </select>
                    <select name="procs" multiple="true" data-placeholder="Select process types...">
                        <option py:for="p in components">${p}</option>
                    </select>
                </fieldset>

                <!-- Severity -->
                <fieldset class="query-fragment" query-type="severity" display-name="Severity">
                    <label class="remove-filter button">Remove</label>
                    <label class="query-type">Severity</label>
                    <select name="negate_severity" class="search-field-disabled">
                        <option selected="true" value="">is</option>
                        <option value="1">is not</option>
                    </select>
                    <select name="severity" multiple="true" data-placeholder="Select severities...">
                        <option py:for="item in severities">${item}</option>
                    </select>
                </fieldset>

                <!-- Time Interval -->
                <fieldset name="period" class="query-fragment" query-type="period" display-name="Time Interval">
                    <label class="remove-filter button">Remove</label>
                    <label class="query-type">Time interval</label>
                    <label>from</label>
                    <select name="queryTime" class="search-field-disabled">
                        <option class="startup">server startup</option>
                        <option class="beginning">beginning of logs</option>
                        <option class="specific-time">specific time</option>
                        <option class="now">now</option>
                    </select>
                    <div class="queryTime-datepicker" style="display: none">
                        <!-- datepicker trigger -->
                        <input class="specific-time" type="text" value="" placeholder="Day DD Mon YYYY HH:MM:SS.ms" />
                    </div>
                    <select name="period" class="search-field-disabled">
                        <option class="present">to present</option>
                        <option class="beginning">to beginning of logs</option>
                        <option class="forwards">forwards</option>
                        <option class="backwards">backwards</option>
                        <option class="either-side">either side</option>
                    </select>
                    <div class="period-datepicker" style="display: none"><!--         remove space for FF
                     --><input name="periodValue" type="text" value="" min="1" /><!-- remove space for FF
                     --><select name="periodUnit" class="search-field-disabled">
                            <option>seconds</option>
                            <option>minutes</option>
                            <option>hours</option>
                            <option>days</option>
                        </select>
                    </div>
                </fieldset>

                <!-- metadata key/value -->
				<fieldset py:if="allowMetadataFilter" name="metadata"
						class="query-fragment" query-type="metadata_key_value"
						display-name="Metadata Key/Value">
                    <label class="remove-filter button">Remove</label>
                    <label class="query-type">Metadata Key</label>
                    <input type="text" name="metadata_key" />
                    <select name="metadata_condition" class="search-field-disabled">
                        <option value="exist">exists</option>
                        <option value="not_exist">does not exist</option>
                        <option value="is">is</option>
                        <option value="is_not">is not</option>
                    </select>
                    <div class="metadata_value_input" style="display: none"><!-- remove space for FF
                     --><label class="query-type">value</label><!-- remove space for FF
                     --><input type="text" name="metadata_value" /><!-- remove space for FF
                     --><select name="metadata_value_type" class="search-field-disabled">
							<option value="string">string</option>
							<option value="number">number</option>
						</select>
                    </div>
                </fieldset>

            </form><!-- /inactive-queries-container -->

        </div><!-- /query-form-container -->

        <div class="log-output-header">
            <h2>Results</h2>
            <div class="log-output-actions">
                <div class="query-progress-indicator"></div>
                <img class="decrease-font-size" title="Decrease font size" src="/static/images/font_small.png" />
                <img class="increase-font-size" title="Increase font size" src="/static/images/font_large.png" />
                <div class="message-logger-status">
                    <img class="message-logger-online" alt="message_logger is running" title="message_logger is running" src="static/images/online.png" />
                    <img class="message-logger-offline" alt="message_logger is not running" title="message_logger is not running" src="static/images/offline.png" />
                </div>
                <img class="idle spinner" src="/static/images/throbber.png" />
                <img class="progress spinner" src="/static/images/throbber.gif" />
            </div>
        </div>

        <div class="bordered log-output-container">
            <div class="log-output"></div>
        </div>

    </div><!-- /log-viewer -->

    <script src="/static/third_party/jquery-ui/jquery-ui.js" type="text/javascript"></script>
    <script src="/static/third_party/jquery-ui/jquery-ui-timepicker-addon.js" type="text/javascript"></script>
    <script src="/static/third_party/jquery.deserialize.js" type="text/javascript"></script>
    <script src="/static/third_party/jquery-chosen/chosen.jquery.js" type="text/javascript"></script>

    <script src="/static/js/ajax.js" type="text/javascript"></script>
    <script src="/static/js/async_task.js" type="text/javascript"></script>
    <script src="static/js/log_viewer.js" type="text/javascript"></script>
    <script src="static/js/log_viewer_search.js" type="text/javascript"></script>
    <script src="static/js/log_query_parser.js" type="text/javascript"></script>

    <script type="text/javascript">
    //<![CDATA[

        document.title = 'Search Logs - WebConsole';

        // python params
        var mlogStatus = '${mlstatus}';
        var defaultQuery = '${defaultQuery}' || '';
        var isMessageLoggerRunning = ('True' === mlogStatus);
        var serverTimezone = ${ serverTimezone };

		// stringify python tuple into javascript array literal
        var default_columns = ${ repr( list( default_columns ) ) };
        var query_order = ${ repr( list( output_columns ) ) };

        // LogViewer.QueryForm instance, initialised by initLogViewerPage.
        var queryForm;
        jQuery( document ).ready( initLogViewerPage );

        BW.LogViewerModel = {
            categories: ${ repr( categories ) },
            hostnames: ${ repr( hostnames ) },
            processTypes: ${ repr( components ) },
            severities: ${ repr( severities ) },
            messageSources: ${ repr( message_sources ) },
            outputColumns: ${ repr( output_columns ) },
        };
    // ]]>
    </script>


</div><!-- /moduleContent -->

</html>

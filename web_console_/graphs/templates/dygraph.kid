<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<html xmlns="http://www.w3.org/1999/xhtml"
      xmlns:py="http://purl.org/kid/ns#"
      py:layout="'../../common/templates/layout_css.kid'"
      py:extends="'../../common/templates/common.kid'">

<div py:def="moduleContent()" class="content">

<link href="/static/third_party/jquery-chosen/chosen.css" rel="stylesheet" type="text/css" />
<link href="/static/third_party/jquery-ui/css/jquery-ui.css" rel="stylesheet" type="text/css" />
<link href="/static/third_party/jquery-ui/jquery-ui-timepicker-addon.css" type="text/css" />
<link href="static/css/graphs.css" rel="stylesheet" type="text/css" />

<div class="statgrapher-container live-mode">

    <h2 class="heading">Graphs</h2>

    <div class="actions-bar">
        <ol class="breadcrumbs"></ol>
        <label class="legend-control button" title="Show/Hide the Legend"></label>
        <label class="toggle-statistic-view button" title="Enter/Exit by statistic view"></label>
        <label class="toggle-y-axis button" title="Show/Hide y axis"></label>
        <label class="smoothing-control button" title="Show/Hides data gaps"></label>
        <label class="live-mode-control button" title="Toggle live mode"></label>

        <!-- the time periods below *should* (but not necessarily *must*) match the
        aggregation settings of whatever Carbon instance is being queried. -->
        <select name="range" class="time-range-control search-field-disabled" title="Set the current view period">
            <option value="300">5 minutes</option>
            <option value="3600">1 hour</option>
            <option value="86400">1 day</option>
            <option value="604800">1 week</option>
            <option value="2592000">1 month</option>
            <option value="31536000">1 year</option>
        </select>
        <!-- below select should match the above select bar but for addition of 'custom' at top -->
        <select name="range_" class="custom-zoom-control time-range-control search-field-disabled" title="Set the current view period">
            <option name="custom" value="custom">custom</option>
            <option value="300">5 minutes</option>
            <option value="3600">1 hour</option>
            <option value="86400">1 day</option>
            <option value="604800">1 week</option>
            <option value="2592000">1 month</option>
            <option value="31536000">1 year</option>
        </select>
        <label class="calendar-button button" title="Select specific time"></label>
        <input class="specific-time" type="text" value="" />
    </div>
    <div class="charts-container flex-vertically">
	    <div class="select-line"></div>
    </div>

    <div id="chart-legend"></div>

    <!--
    <div class="status-bar">
        <div class="view-range"></div>
    </div>
    -->

</div><!-- .statgrapher-container -->

<div class="alert-notification-container"></div>

<!--<script type="text/javascript" src="static/js/dygraph-combined.js"></script>-->
<script type="text/javascript" src="/static/third_party/jquery-ui/jquery-ui.js"></script>
<script type="text/javascript" src="/static/third_party/jquery-ui/jquery-ui-timepicker-addon.js"></script>
<script type="text/javascript" src="/static/third_party/jquery-chosen/chosen.jquery.js"></script>
<script type="text/javascript" src="static/js/dygraph-combined-dev.js"></script>
<script type="text/javascript" src="/static/js/bw_graphite.js"></script>
<script type="text/javascript" src="static/js/bw_chart_events.js"></script>
<script type="text/javascript" src="static/js/bw_chart_dygraph.js"></script>
<script type="text/javascript" src="static/js/bw_chart_group.js"></script>
<script type="text/javascript" src="static/js/graphs.js"></script>
<script type="text/javascript">
    document.title = 'Process Graphs - WebConsole';
    window.GRAPHITE_HOST = '${tg.config( "web_console.graphs.graphite_host" )}';
    if (!GRAPHITE_HOST)
    {
        new Alert.Warning(
            'No Graphite host is defined in WebConsole configuration - ' +
            'this version of the Graphs module requires a running Graphite-Web service. ' +
            'Please uncomment and/or define a valid graphite host for configuration key ' +
            '"web_console.graphs.graphite_host".',
            { duration: 0 }
        );
    }
	
	if ("${isStatLoggerRunning}" == "False")
	{
		new Alert.Warning( "Statistics are not being captured as StatLogger is not running." );
	}

	if ("${isCarbonEnabled}" == "False")
	{
		new Alert.Warning( "Statistics are not being captured as Carbon store is not enabled in StatLogger configuration file." );
	}
	else if ("${isCarbonRunning}" == "False")
	{
		new Alert.Warning( "Statistics are not being captured as Carbon service is not running." );
	}
</script>

</div>
</html>


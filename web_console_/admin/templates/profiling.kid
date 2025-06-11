<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">

<html xmlns="http://www.w3.org/1999/xhtml"
	  xmlns:py="http://purl.org/kid/ns#"
	  py:layout="'../../common/templates/layout_css.kid'"
	  py:extends="'../../common/templates/common.kid'">



<div py:def="moduleContent()" class="content">

	<link href="static/css/profiling.css" rel="stylesheet" type="text/css" />

	<script type="text/javascript">
		document.title = 'Self Profiling - WebConsole';
	</script>

	<div class="alert-notification-container"></div>

	<div py:if="isAvailable" class="bordered container">
		<script type="text/javascript" src="static/js/profiling.js"></script>

		<h2 class="heading">WebConsole Self Profiling</h2>

		<div class="actions-bar">
			<div class="actions-dock-left">
				<label>Profiling Duration (seconds) </label>
				<input type="text" class="profiling-dump-time"
					value="${default_dump_time}" size="5" />
				<label> Recommended maximum: ${default_dump_time} seconds
				(<a href="help#perform_self_profiling" target="_blank">more...</a>)
				</label>
				<div class="dump-time-size-warning">
					Setting <b>Profiling Duration</b> to
					<label class="warning-text-style warning-seconds"></label>
					seconds will result in very large dump files (at least
					<label class="warning-size"></label> MB).
					<br/><br/>
					These files may be too large to view.
				</div>
				<div class="dump-time-input-error">
				</div>
				<div class="dump-actions">
					<label class="button start-button" id="startStopButton"
						onclick="profilingStartStop()">
						<text id="startStopButtonText">Profiling</text>
					</label>
				</div>
			</div>
		</div>

		<table class="layout-only profiling-status-table">
			<tr>
				<td>Profiling Status:</td>
				<td class="field" id="statusText"></td>
			</tr>
			<tr>
				<td>Output File:</td>
				<td class="field" id="outputFilePath"></td>
			</tr>
		</table>
	</div>

	<div py:if="not isAvailable" class = "bordered container">
		<h2 class="heading">WebConsole Self Profiling</h2>

		<div class="usage-error">
			<p>WebConsole Self Profiling is not configured.</p>

			<p>Configure the environment variable before startup as
			follows:</p>

			<pre class="programlisting">export BW_WEB_CONSOLE_PROFILING=1</pre>

			<p>If installed from an RPM this can be configured in
			/etc/default/web_console. Further settings such as dump time and
			dump directory can be configured in your WebConsole config
			file (web_console.conf or dev.cfg).</p>
		</div>
	</div>

	<script type="text/javascript">
		jQuery( document ).ready( function()
		{
			jQuery( '.profiling-dump-time' ).on( "change keyup input paste",
				function()
				{
					dumpTimeChanged( ${warning_dump_time} );
				})
		});
	</script>

</div>
</html>

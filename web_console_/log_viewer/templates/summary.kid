<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<?python
  layout_params[ "moduleHeader" ] = "Log Viewer"
?>

<html xmlns="http://www.w3.org/1999/xhtml"
	  xmlns:py="http://purl.org/kid/ns#"
	  py:layout="'../../common/templates/layout_css.kid'"
	  py:extends="'../../common/templates/common.kid'">

<div py:def="moduleContent()" class="content">

	<script type="text/javascript" src="/static/js/table.js"/>
	<script type="text/javascript">
		document.title = 'Detailed Log Summary - WebConsole';
		jQuery( document ).ready( Table.init );
	</script>

	<?python
	  import time
	  from pycommon import util
	?>

	<style type="text/css">
        .table-container { display: block; overflow-x: hidden; }
        td { white-space: nowrap; }
	</style>

	<div class="bordered table-container">
        <h2 class="heading">Log Summary for ${logUser}</h2>
        <table class="sortable">
            <thead>
                <tr class="sortrow">
                    <th>SegmentName</th>
                    <th>Start</th>
                    <th>End</th>
                    <th>Duration</th>
                    <th>Entries</th>
                    <th>Size</th>
                </tr>
            </thead>
            <tbody>
                <tr py:for="s in segments">
                    <td>${s.suffix}</td>
                    <td>${time.ctime( s.start )}</td>
                    <td>${time.ctime( s.end )}</td>
                    <td>${util.fmtSecondsLong( int( s.end - s.start ) )}</td>
                    <td class="numeric">${s.nEntries}</td>
                    <td class="numeric">${util.fmtBytes( s.entriesSize + s.argsSize, True )}</td>
                </tr>
            </tbody>
        </table>
    </div>

	<p><a href="summaries">Show summary for all users</a></p>
</div>

</html>

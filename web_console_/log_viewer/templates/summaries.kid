<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<?python
  layout_params[ "moduleHeader" ] = "Log Viewer"
?>

<html xmlns="http://www.w3.org/1999/xhtml"
	  xmlns:py="http://purl.org/kid/ns#"
	  py:layout="'../../common/templates/layout_css.kid'"
	  py:extends="'../../common/templates/common.kid'">

<div py:def="moduleContent()" class="bordered table-container">

	<script type="text/javascript" src="/static/js/table.js"/>
	<script type="text/javascript">
		document.title = 'Log Usage Summary - WebConsole';
		jQuery( document ).ready( Table.init );
	</script>

	<style type="text/css">
        .table-container { display: block; overflow-x: hidden; }
        td { white-space: nowrap; }
    </style>

    <h2 class="heading">Log Summary For All Users</h2>
    <table class="sortable">
        <thead>
            <tr class="sortrow">
                <th>Username</th>
                <th>Size</th>
                <th>Entries</th>
                <th>Segments</th>
                <th>Start</th>
                <th>End</th>
                <th>Duration</th>
            </tr>
        </thead>
        <tbody>
            <tr py:for="i in info">
                <td><a href="${tg.url( 'summary', logUser=i[0] )}">${i[0]}</a></td>
                <td py:for="x in i[1:]" class="numeric">${x}</td>
            </tr>
        </tbody>
    </table>

</div>

</html>

<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<?python
  layout_params[ "pageHeader" ] = "Watchers"
  layout_params[ "page_specific_css"] = [ '../static/css/watchers.css' ]
?>

<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
	  py:layout="'../../common/templates/layout_css.kid'"
	  py:extends="'../../common/templates/common.kid'">

<div py:def="moduleContent()" class="bordered watcher-list-container">

	<script type="text/javascript" src="/static/js/table.js"/>
	<script type="text/javascript">
		document.title = 'Watchers - WebConsole';
		jQuery( document ).ready( function() { Table.init(); } );
	</script>

    <h2 class="heading">Processes for ${user.name}</h2>
    <table class="sortable">
        <thead>
        <tr class="sortrow">
            <th class="colheader">Process Name</th>
            <th class="colheader">Machine</th>
            <th class="colheader">PID</th>
        </tr>
        </thead>
        <tbody>
        <tr py:for="process in processes" class="sortable">
            <!-- Only link to the process watchers if they are supported -->
            <td py:if="process.hasWatchers()"><a href="${tg.url( '/watchers/tree/show', machine=process.machine.name, pid=process.pid)}">${process.label()}</a></td>
            <td py:if="not process.hasWatchers()">${process.label()}</td>

            <td>${process.machine.name}</td>
            <td>${process.pid}</td>
        </tr>
        </tbody>
    </table>

</div>

</html>

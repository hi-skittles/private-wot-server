<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">


<?python
  layout_params[ "page_specific_css"] = [ 'static/css/profiler.css' ]
?>

<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
      py:layout="'../../common/templates/layout_css.kid'"
      py:extends="'../../common/templates/common.kid'">


 <div py:def="moduleContent()" class="bordered profiler-list-container">
    
    <script type="text/javascript" src="/static/js/table.js"/>
    <script type="text/javascript">
        document.title = 'Profiler - WebConsole';
        jQuery( document ).ready( function() { Table.init(); } );
    </script>

    <h2 class="heading">Process for ${user.name}</h2>
    <table class="sortable">
        <thead>
            <tr class="sortrow">
                <th class="colheader">Process Name</th>
                <th class="colheader">Machine</th>
                <th class="colheader">PID</th>
                <th class="colheader">Actions</th>
            </tr>
        </thead>
        <tbody>
            <tr py:for="process in processes" class="sortable">
                <td>${process.label()}</td>
                <td>${process.machine.name}</td>
                <td>${process.pid}</td>
                <td py:if="process.getSupportWebConsoleProfiler()">
                    <a href="${tg.url('liveview', 
                            machine=process.machine.name,
                            pid=process.pid)}">Live View</a>
                </td>
                <td py:if="not process.getSupportWebConsoleProfiler()" 
					class="incompatible-process"
                    title="The process is of version ${process.version} and doesn't support Live View">
                    (Incompatible)
                </td>
            </tr>
            <tr py:if="not processes">
                <td colspan="4" style="text-align: center">No processes</td>
            </tr>
        </tbody>
    </table>

</div>

</html>

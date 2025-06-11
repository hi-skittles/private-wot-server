<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
	  py:layout="'../../common/templates/layout_css.kid'"
	  py:extends="'../../common/templates/common.kid'">


<div py:def="moduleContent()" class="content">

	<script type="text/javascript" src="/static/js/table.js"/>
	<script type="text/javascript">
		document.title = 'Python Console - WebConsole';
		jQuery( document ).ready( function() { Table.init(); } );
	</script>

	<div class="bordered table-container">
        <h2 class="heading">${ 'Console-Enabled Processes For %s' % user.name }</h2>
        <table class="sortable">
            <thead>
                <tr class="sortrow">
                    <th>Process Name</th>
                    <th>Machine</th>
                    <th>Action</th>
                </tr>
            </thead>
            <tbody>
                <tr py:if="procs" py:for="p in procs">

                    <td py:content="p.label()"/>
                    <td py:content="p.machine.name"/>
                    <td>
                        <a href="${tg.url( 'console',
                                 host = p.machine.ip,
                                 port = ports[ p ],
                                 process = labels[ p ])}">Connect</a>
                    </td>
                </tr>
                <tr py:if="not procs">
                    <td colspan="3" style="text-align: center">No server running</td>
                </tr>
            </tbody>
        </table>
	</div>

</div>

</html>

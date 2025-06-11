<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">

<html xmlns="http://www.w3.org/1999/xhtml"
	  xmlns:py="http://purl.org/kid/ns#"
	  py:layout="'../../common/templates/layout_css.kid'"
	  py:extends="'../../common/templates/common.kid'">

<div py:def="moduleContent()" class="content">

    <style type="text/css">
    .content tbody td {
        text-align: center;
    }

    .content thead th:first-child,
    .content tbody td:first-child {
        text-align: right;
    }
    </style>

	<script type="text/javascript" src="/static/js/table.js"/>
	<script type="text/javascript">
		document.title = 'User Groups - WebConsole';
		jQuery( document ).ready( function() { Table.init(); } );
	</script>

	<div class="bordered table-container">
        <h2 class="heading">Groups</h2>
        <table class="sortable">
            <thead>
                <tr class="sortrow">
                    <th>Group name</th>
                    <th py:for="p in permissions">${ p.capitalize() } own</th>
                    <th py:for="p in permissions">${ p.capitalize() } other</th>
                    <th>Admin</th>
                </tr>
            </thead>
            <tbody>
                <tr py:for="g in groups">
                    <td>${ g.group_name }</td>
                    <td py:for="p in permissions"><i class="icon-ok" py:if="groupPermissions[g.group_name][p][0]"></i></td>
                    <td py:for="p in permissions"><i class="icon-ok" py:if="groupPermissions[g.group_name][p][1]"></i></td>
                    <td><i class="icon-ok"  py:if="g.group_name == 'admin'"></i></td>
                </tr>
            </tbody>
        </table>
    </div>

</div>
</html>

<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">

<html xmlns="http://www.w3.org/1999/xhtml"
	  xmlns:py="http://purl.org/kid/ns#"
	  py:layout="'../../common/templates/layout_css.kid'"
	  py:extends="'../../common/templates/common.kid'">

<body>
<div py:def="moduleContent()" class="content">
	<link href="static/css/user-admin.css" rel="stylesheet" type="text/css" />

	<script type="text/javascript" src="/static/js/action_table.js"/>
	<script type="text/javascript" src="/static/js/ajax.js"/>
	<script type="text/javascript" src="/static/js/table.js"/>
	<script type="text/javascript">
		document.title = 'User Accounts - WebConsole';
		jQuery( document ).ready( function() { Table.init(); } );
	</script>

	<div class="bordered table-container">
        <h2 class="heading">Users</h2>
        <table class="sortable">
            <thead>
                <tr class="sortrow">
                    <th>Username</th>
                    <th>Server User</th>
                    <th>Groups</th>
                    <th>Action</th>
                </tr>
            </thead>
            <tbody>
                <tr py:for="user in users">
                    <td>${user.user_name}</td>
                    <td py:if="authByLdapEnabled" class="server-user-grey">${user.serveruser}</td>
                    <td py:if="not authByLdapEnabled">${user.serveruser}</td>
                    <td>${ ", ".join( [g.group_name for g in user.groups] ) }</td>
                    <td><div py:replace="actionsMenu( options[ user ], rowID=user.user_name )"/></td>
                </tr>
            </tbody>
        </table>
    </div>

	<h3>NOTE</h3>
	<ul>
		<li>The <b>Username</b> field refers to the login name for the Web
		Console account.</li>

		<li>The <b>Server User</b> field refers to the UNIX user associated with
		this Web Console account (i.e. for running the server, querying logs etc).</li>

	</ul>

</div>
</body>

</html>

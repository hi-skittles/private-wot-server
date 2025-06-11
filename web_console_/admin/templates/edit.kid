<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">

<?python
  layout_params[ "page_specific_css"] = [ "/static/third_party/jquery-chosen/chosen.css"
                                        ]
?>

<html xmlns="http://www.w3.org/1999/xhtml"
      xmlns:py="http://purl.org/kid/ns#"
      py:layout="'../../common/templates/layout_css.kid'"
      py:extends="'../../common/templates/common.kid'">

<div py:def="moduleContent()" class="content">

	<link href="static/css/user-admin.css" rel="stylesheet" type="text/css" />
    <style type="text/css">
    </style>

    <form action="" method="post" name="user_details">

        <div class="alert-notification-container"></div>

        <div class="bordered table-container">
            <h2 class="heading" py:if="tg.request.params[ 'action' ] == 'add'">Add A New User</h2>
            <h2 class="heading" py:if="tg.request.params[ 'action' ] == 'edit'">Edit User Details</h2>
            <table class="layout-only">
                <tr>
                    <td class="colheader">Username</td>
                    <td>
                        <input py:if="not user" class="user-name" name="username" type="text" />
                        <input py:if="user" class="user-name" name="username" value="${user.user_name}" type="text" />
                    </td>
                </tr>

                <tr py:if="not authByLdapEnabled or ( user and user.isDefaultAdmin() )">
                    <td class="colheader">Password</td>
                    <td><input type="password" name="pass1"/></td>
                </tr>

                <tr py:if="not authByLdapEnabled or ( user and user.isDefaultAdmin() )">
                    <td class="colheader">Confirm Password</td>
                    <td><input type="password" name="pass2"/></td>
                </tr>

                <tr py:if="not authByLdapEnabled and ( not user or not user.isAdmin() )">
                    <td class="colheader">Server User</td>
                    <td>
                        <input py:if="not user" name="serveruser" type="text" />
                        <input py:if="user" name="serveruser" value="${user.serveruser}" type="text" />
                    </td>
                </tr>

                <tr py:if="authByLdapEnabled and ( not user or not user.isDefaultAdmin() )">
                    <td class="colheader">Server User</td>
                    <td class="server-user-container">
						<span py:if="not user" class="server-user-name"></span>
						<span py:if="user" class="server-user-name">${user.serveruser}</span>
						<span class="query-indicator"><img class="progress-spinner" src="/static/images/throbber.gif" /></span>
                    </td>
                </tr>

                <tr py:if="groups and not user or not user.isDefaultAdmin()">
                    <td class="colheader">Group</td>
                    <td>
                        <select py:if="not user" name="group" data-placeholder="Select group..." class="search-field-disabled">
                            <option selected="true" py:if="tg.config( 'web_console.authorisation.default_group' )" >${ tg.config( 'web_console.authorisation.default_group' ) }</option>
                            <option py:for="g in groups" py:if="g.group_name != tg.config( 'web_console.authorisation.default_group' )">${ g.group_name }</option>
                        </select>
                        <select py:if="user" name="group" data-placeholder="Select group..." class="search-field-disabled">
                            <?python
                                remainingGroups = []
                                for g in groups:
                                    if g not in user.groups:
                                        remainingGroups.append( g )
                            ?>
                            <option py:for="g in user.groups" selected="true">${ g.group_name }</option>
                            <option py:for="g in remainingGroups" >${ g.group_name }</option>
                        </select>
                    </td>
                </tr>

                <tr>
                    <td colspan="2">
                        <input py:if="user" type="hidden" name="id" value="${user.id}"/>
                        <input py:if="user and user.isAdmin()" type="hidden" name="serveruser" value="${user.serveruser}"/>
                        <input py:if="not user" type="submit" value="Add User" class="button commit-add" />
                        <input py:if="user" type="submit" value="Commit Changes" class="button commit-edit" />
                    </td>
                </tr>

            </table>
        </div>
    </form>

    <h3>NOTE</h3>

    <ul>
        <li>The <b>Username</b> field refers to the login name for the Web
        Console account.</li>

        <li py:if="authByLdapEnabled and ( not user or not user.isDefaultAdmin() )">
        Authentication by LDAP has been enabled. The <b>Username</b> field
        should be linked a valid LDAP account.</li>


        <li py:if="not authByLdapEnabled and ( not user or not user.isAdmin() )">The <b>Server User</b> field refers to the UNIX user associated with
        this Web Console account (i.e. for running the server, querying logs etc).</li>

    </ul>

    <script src="/static/third_party/jquery-chosen/chosen.jquery.js" type="text/javascript"></script>
    <script src="static/js/user-admin.js" type="text/javascript"></script>  
    <script type="text/javascript">//<![CDATA[

        var action = "${tg.request.params[ 'action' ].capitalize()}" || 'Edit';
        document.title = action + " User Account - WebConsole";

        // form select replacement
        jQuery( 'select' ).chosen();

        // Set the focus to the first field
        document.forms.user_details.username.focus();
        
        var authByLdapEnabled = "${authByLdapEnabled}";
		var isDefaultAdmin = "${user and user.isDefaultAdmin()}";

        if (isDefaultAdmin != "True" && authByLdapEnabled == "True")
        {
            jQuery( document ).ready( initAddUser() );
        }
	// ]]>
    </script>

<!-- div py:def="moduleContent()" -->
</div>
</html>

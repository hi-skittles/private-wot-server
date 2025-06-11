<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<!--!
    kid language spec: http://werc.engr.uaf.edu/~ken/doc/python-kid/html/language.html
    kid user's guide: http://werc.engr.uaf.edu/~ken/doc/python-kid/html/guide.html
-->
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#">
<head>
	<link rel="stylesheet" type="text/css" href="/static/css/font-awesome.css"/>
	<link rel="stylesheet" type="text/css" href="/static/css/top.css"/>
	<link rel="stylesheet" type="text/css" href="/static/css/navmenu.css"/>
	<link rel="stylesheet" type="text/css" href="/static/css/content.css"/>
	<link rel="stylesheet" type="text/css" href="/static/css/alert.css"/>
	<link rel="stylesheet" type="text/css" href="/static/css/web_console.css"/>
	<link rel="stylesheet" type="text/css" href="/static/third_party/jquery-plugin-dataTables/css/jquery.dataTables.css"/>
	<link rel="stylesheet" type="text/css" href="/static/css/dynamic_table.css"/>
	<link rel="stylesheet" type="text/css" href="/static/third_party/jquery-ui/css/jquery-ui.css"/>
	<link rel="shortcut icon" type="image/x-icon" href="/static/images/favicon.ico"/>

	<title>WebConsole</title>

	<script type="text/javascript" src="/static/js/jquery-1.7.2.js"></script>
	<script type="text/javascript" src="/static/third_party/jquery-ui/jquery-ui.js"></script>
	<script type="text/javascript" src="/static/third_party/jquery-plugin-dataTables/js/jquery.dataTables.js"></script>
	<script type="text/javascript" src="/static/third_party/jquery-cookie/jquery.cookie.js"></script>
	<script type="text/javascript" src="/static/js/standard_shims.js"></script>
	<script type="text/javascript" src="/static/js/alert.js"></script>
	<script type="text/javascript" src="/static/js/bw.js"></script>

	<!-- Note: this isn't the IE method of controlling cache -->
	<meta http-equiv="cache-control" content="no-cache"/>

	<!-- Make IE not turn on compatibility mode which screws up JS -->
	<meta http-equiv="X-UA-Compatible" content="IE=9"/>

	<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
	<meta name="format-detection" content="telephone=no" />

	<link py:for="file in value_of( 'page_specific_css', [] )" href="${file}" type="text/css" rel="stylesheet" />
</head>
<body>
<?python

from web_console.common import util, module
import web_console.root.controllers

username = util.getSessionUsername()
actingServeruser = util.getServerUsername()
try:
    user = tg.identity.user
    actualServeruser = user.serveruser
except:
    user = None
    actualServeruser = None
?>

<div py:if="username and user and user.hasOtherPermissions( 'view' )" class="switch-user-dialog">
	<span class="close-button">&#10005;</span>
    <h3>Access Other Server User</h3>
    <p>
        You are currently acting as server user ${ actingServeruser }.<br/>
        Enter a username to access or select one from the dropdown menu.
    </p>
	<div class="input-div">
		<div class="username-accept"></div>
		<div class="dropdown-button"><span>&#x25bc;</span></div>
		<input id="users-input"/>
		<button class="disabled" disabled="disabled" id="access-user-btn">Access User</button>
		<ul class="recent-users-list ui-autocomplete ui-front ui-menu ui-widget ui-widget-content"></ul>
	</div>
	<div class="all-users-header">
		<div id="header-icon" class="icon-plus-sign"></div>
		<span>Show all users</span>
		<hr/>
	</div>
    <div class="all-users-list">
		<a class="button refresh-users-button"><img src="/static/images/throbber_16_o.gif"/></a>
		<table id="all-users-table" class="all-users-table">
			<thead>
				<tr>
					<th>Username</th>
					<th>UID</th>
					<th>Activity</th>
				</tr>
			</thead>
			<tbody id="all-users-tbody">
			<tr>
				<td colspan="3">Waiting for server...</td>
			</tr>
			</tbody>
		</table>
		<div class="checkbox-div">
			<input type="checkbox" id="alwaysShowUsersCheckbox"/><label for="alwaysShowUsersCheckbox">Always show all users</label>
		</div>
	</div>
    <p style="display:none;" py:if="username and (actualServeruser != actingServeruser)"><a href="javascript:BW.user.switchServerUser( '${ actualServeruser }' )">Revert to own server user</a></p>
</div>


<div class="user-feedback-dialog" id="user-feedback-dialog">

	<div id="user-feedback-disabled-message">
		<h3 class="heading">WebConsole User Feedback</h3>
		<div>
			<p class="error-message"></p>
		</div>
		<div class="feedback-actions-bar">
			<button id="user-feedback-disabled-OK" class="button">
				<text>OK</text></button>
		</div>
	</div>

	<form id="user-feedback-form">
		<h3 class="heading">WebConsole User Feedback</h3>

		<table class="layout-only" id="user-feedback-table">
			<tr>
				<td>
					<label>Subject:</label>
				</td>
				<td>
					<input type="text" id="user-feedback-subject"/>
				</td>
			</tr>
			<tr id="user-feedback-email-row">
				<td>
					<label>Return Email:</label>
				</td>
				<td>
					<input type="email" id="user-feedback-address"
						placeholder="(optional)"/>
				</td>
			</tr>
			<tr id="user-feedback-comments-row">
				<td>
					<label>Comments:</label>
				</td>
				<td>
					<textarea id="user-feedback-comments"></textarea>
				</td>
			</tr>
			<tr id="user-feedback-info-row">
				<td>
					<label>User/Page Info:</label>
				</td>
				<td>
					<textarea id="user-feedback-attached"
						disabled="disabled"></textarea>
				</td>
			</tr>
		</table>

		<div class="actions-bar-right" id="user-feedback-actions-bar">
			<button type="button" id="user-feedback-button-send" class="button">
				<text>Send</text></button>
			<button type="button" id="user-feedback-button-cancel" class="button">
				<text>Cancel</text></button>
		</div>

		<div id="user-feedback-sent">
			<div class="result-text">
				<p>Your feedback was sent.</p>
			</div>
			<div class="actions-bar-right">
				<button type="button" id="user-feedback-sent-OK" class="button">
					<text>OK</text></button>
			</div>
		</div>
	</form>
</div>

<div class="logoheader">
	<div py:if="username and user" id="show-info-dialog" class="version-info"
		onclick="BW.page.showVersionInfo()" />

    <div class="logo_image">
        <img src="/static/images/bigworld.png" alt="BigWorld Web Console"/>
    </div>

    <!-- user menu -->
    <div py:if="username" class="user-profile">
        <div class="profile-summary">
            <label class="display-name" title="Your WebConsole user name">${ username }</label>
            <label class="acting-serveruser" title="Your current BigWorld server user">${ actingServeruser }</label>
        </div>
        <div class="show-profile button"></div>
        <div class="profile-detail dropdown-menu-container">
            <ul class="dropdown-menu contains-links pull-right">
                <li class="switch-serveruser"><a href="javascript:BW.user.switchServerUserDialog()">Access other server user</a></li>
                <li class="revert-serveruser"><a href="javascript:BW.user.revertServerUser()">Revert to own server user</a></li>
                <hr/>
                <li class="user-feedback"><a class="user-feedback-button" href="javascript:BW.user.showFeedbackDialog()">User feedback</a></li>
                <li><a href="/logout">Logout</a></li>
            </ul>
        </div>
    </div>

    <!-- login form -->
    <div py:if="not username" class="login">
        <script type="text/javascript">
            document.title = 'Login - WebConsole';
        </script>

        <form action="/login" method="post" id="loginForm">
        <div>
            <span id="loginbox">
                <label>Username:</label>
                <input name="${ tg.config( 'identity.form.user_name' ) }" id="username" size="13" class="text"/>
                <label>Password:</label>
                <input name="${ tg.config( 'identity.form.password' ) }" type="password" size="13" class="text"/>
                <input type="submit" name="${ tg.config( 'identity.form.submit' ) }" value="Log In" class="login-button"/>
                <!-- Hidden field required to trigger turbogears AJAX login -->
                <input type="hidden" name="${ tg.config( 'identity.form.submit' ) }"/>
            </span>
        </div>
        </form>
    </div>

    <!-- show/hide control -->
    <div py:if="username and user" id="menu_collapser" class="menu_collapser animated resizable"
        title="Show/Hide the navigation menu">
	<link rel="stylesheet" type="text/css" href="/auth/permissions.css" />

    <script type="text/javascript" src="/static/js/bw_user.js"></script>
    <script type="text/javascript" src="/static/js/bw_constants.js"></script>
    <script type="text/javascript">//<![CDATA[

        BW.require( "BW.User" );

        // instantiate BW.user, the currently authenticated WebConsole user
        BW.user = new BW.User({
            name: "${ tg.identity.user.user_name }",
            serverUser: "${ actualServeruser }",
            effectiveServerUser: "${ actingServeruser }",
            ownerRights: ${ repr( list( tg.identity.user.getOwnerPermissions() ) ) },
            otherRights: ${ repr( list( tg.identity.user.getOtherPermissions() ) ) },
        });
	
        // Initialise user list in change server user dialog
        if (!BW.user.isAdmin())
        {
            BW.user.getUsersListForDialog();
        }

        // apply permissions CSS classes to current document
        BW.User.initPermissions();

        // load permissions object
        BW.User.loadPermissions();

    // ]]>
    </script>
    </div>

</div><!-- /.logoheader -->

<!-- navigation -->
<div id="navmenu_cell" class="spaced resizable" py:if="username or tg.request.path == '/login'">
    <div id="navigation" class="navmenu">
        <ul class="level-one">
            <li py:for="mod in module.Module.all()"
                py:if="mod.auth()"
                py:attrs="mod.attrs()">
                <a href="/${mod.path}"><img src="${mod.icon}" alt=""/>${mod.name}<div class="arrow"></div><div class="arrow"></div></a>
                <ul py:if="mod.isCurrent()" class="level-two">
                    <li py:for="page in mod.pages"
                        py:attrs="page.attrs()">
                        <a href="${page.url()}">${page.name}</a>
                    </li>
                </ul>
            </li>
			<li py:if="username" class="top-level feedback-list-item">
				<a class="user-feedback-button" href="Javascript:BW.user.showFeedbackDialog()">
					<img src="/static/images/feedback.png" alt=""/><div class="arrow"></div><div class="arrow"></div><span>Feedback</span>
				</a>
			</li>
        </ul>
    </div><!-- /#navigation -->
</div>

<!-- main content -->
<div id="main" class="resizable">
    <div class="content" py:content="moduleContent()" />
    <div class="content mask" />
</div><!-- /#main -->


<script py:if="defined( 'page_specific_js' )" type="text/javascript">
    console.warn('using page_specific_js to include JS files is deprecated, please inline');
</script>
<script py:for="file in value_of( 'page_specific_js', [] )" type="text/javascript" src="${file}"></script>

</body>
</html>

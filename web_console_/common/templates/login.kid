<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<html xmlns="http://www.w3.org/1999/xhtml"
	  xmlns:py="http://purl.org/kid/ns#"
	  py:layout="'../../common/templates/layout_css.kid'"
	  py:extends="'../../common/templates/common.kid'">

<body>
<div py:def="moduleContent()" class="content">

    <style type="text/css">
    #main {
        left: 12px;
        transition: none;
    }
    </style>

    <?python
        try:
            loginErrors
        except:
            loginErrors = None
    ?>
    <p py:if="loginErrors" class="login-incorrect">${ loginErrors }</p>

	<!-- Introductory text -->
	<div id="login_intro">

        <h1 class="heading">BigWorld WebConsole<div class="arrow"></div><div class="arrow"></div></h1>

        <p>Welcome to the BigWorld WebConsole: the web-based interface to
        BigWorld cluster management. </p>

        <h2>User Quickstart</h2>
        <p>If you do not already have an account, ask the system administrator to
        set one up for you; this must be done by the <b>admin</b> user.</p>

        <p>If you already have a user account, login through the <a href="#"
            onClick="return false"
            onMouseOver="var loginBox = document.getElementById( 'loginbox' );
                loginBox.style.border = '3px solid #FAA61A';
                loginBox.style.backgroundColor = '#104D8C';
                loginBox.style.padding = '2em';
                "
            onMouseOut="var loginBox = document.getElementById( 'loginbox' );
                loginBox.style.border = 'none';
                loginBox.style.background = 'transparent';
                loginBox.style.padding = '0';">login box</a> in the
        top-right corner of the screen.</p>

        <p>Once you are logged in, you will see the <i>Cluster</i> module by
        default. This module allows you to view the state of the cluster, and start
        and stop BigWorld server processes.  </p>

        <p>The navigation menu on the left will allow you to move between modules.
        Online help is available: look for the <i>Help</i> links in the navigation
        menu.</p>

        <?python
            #TODO: make this sysadmin quickstart section only appear if no other users
            #other than admin exist
        ?>
        <h2>System Administration Quickstart</h2>

        <p> If you are the system administrator and WebConsole has only just been
        installed, you will need to set up user accounts through the <b>admin</b>
        account. The default password for the admin account is
        '<code>admin</code>'. After logging in, make sure you change the
        administrator password. </p>

        <p>Create user accounts for BigWorld users to administrate their BigWorld
        server processes. </p>

        <p>For more details, refer to the <i>Server Tools Installation
        Guide</i>.</p>

	</div><!-- / login_intro -->

</div><!-- / Login page contents -->
</body>
</html>

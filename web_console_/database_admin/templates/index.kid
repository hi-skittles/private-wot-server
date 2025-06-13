<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://
www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns:py="http://purl.org/kid/ns#"
      xmlns="http://www.w3.org/1999/xhtml"
      py:layout="'../../common/templates/layout_css.kid'"
      py:extends="'../../common/templates/common.kid'">

<!-- main content -->
<div id="main" class="resizable">
    <div class="content" py:def="moduleContent()">
        <h2>Database Overview <span class="">(${username})</span></h2>
        <br/>
        <p>
            There are <strong>${total}</strong> players in the database.
        </p>
    </div>
</div>
<!-- /#main -->

</html>
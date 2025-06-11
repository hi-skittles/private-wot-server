<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<?python
  layout_params[ "pageHeader" ] = "Starting"
?>

<html xmlns="http://www.w3.org/1999/xhtml"
	  xmlns:py="http://purl.org/kid/ns#"
      py:layout="'../../common/templates/layout_css.kid'"
      py:extends="'../../common/templates/common.kid'">

<div py:def="moduleContent()">

	<?python
	  from turbojson import jsonify
	  if action == "start":
	    header = "Starting"
	  elif action == "stop":
	    header = "Stopping"
	  elif action == "restart":
	    header = "Restarting"
	?>

	<script type="text/javascript">
		document.title = "${header} Server - WebConsole";
	</script>

	<div class="bordered table-container">
        <h2 class="heading">${header} The Server</h2>
        <table>
            <thead>
                <tr>
                    <th>Component</th>
                    <th style="color: red">Dead</th>
                    <th style="color: orange">Running</th>
                    <th style="color: green">Registered</th>
                    <th style="color: blue">Details</th>
                </tr>
            </thead>
            <tbody>
                <tr py:for="pname in pnames">
                    <td py:content="pname" id="${pname}_header"/>
                    <td id="${pname}_dead"/>
                    <td id="${pname}_running"/>
                    <td id="${pname}_registered"/>
                    <td id="${pname}_details"/>
                </tr>
            </tbody>
        </table>
    </div>

	<div id="toggle_errors" class="alert"/>

	<script src="${tg.tg_js}/MochiKit.js" type="text/javascript"></script>
	<script src="/static/js/ajax.js" type="text/javascript"></script>
	<script src="/static/js/async_task.js" type="text/javascript"></script>
	<script type="text/javascript" src="static/js/toggle.js"/>
	<script type="text/javascript">
		Toggle.layout = ${jsonify.encode( layout )};
		Toggle.id = ${id};
		Toggle.pnames = ${jsonify.encode( pnames )};
		Toggle.user = "${user}";
		Toggle.action = "${action}";
		Toggle.display();
		Toggle.follow();
	</script>

</div>

</html>

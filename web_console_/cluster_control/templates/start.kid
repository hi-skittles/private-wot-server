<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<?python
  layout_params[ "pageHeader" ] = "Start The Server"
?>

<html xmlns="http://www.w3.org/1999/xhtml"
	  xmlns:py="http://purl.org/kid/ns#"
      py:layout="'../../common/templates/layout_css.kid'"
      py:extends="'../../common/templates/common.kid'">

<body>
	<!-- Macro definitions -->
	<select py:def="selectList( name, options, selected )"
			name="${name}" onchange="onSelectMachines( this )">
			<loop py:for="o in options">
				<option py:if="o == selected"
						selected="selected">${o}</option>

				<option py:if="o != selected">${o}</option>
			</loop>
	</select>

	<!-- Document body -->
	<div py:def="moduleContent()">

	<script type="text/javascript">
		document.title = 'Start Server - WebConsole';
	</script>

	<style type="text/css">
        .table-container {
            /*margin-right: 1em;*/
            margin-bottom: 1em;
            float: left;
            clear: both;
        }
	</style>

	<?python
	  groups = c.getGroups().keys()
	  groups.append( "(use all machines)" )

	  machines = c.getMachines()
	  machines.sort()
	?>

	<form action="${tg.url( 'doStart' )}" name="startForm">
        <div class="bordered table-container">
            <h2 class="heading">Server Environment</h2>
            <table class="layout-only">
                <tr>
                    <th>User</th>
                    <td>${user.name}</td>
                </tr>
                <tr>
                    <th>UID</th>
                    <td>${user.uid}</td>
                </tr>
                <tr>
                    <th>MF_ROOT</th>
                    <td><code id="ccStartMFRoot"> </code></td>
                </tr>
                <tr>
                    <th>BW_RES_PATH</th>
                    <td><code id="ccStartBWResPath"> </code></td>
                </tr>
                <tr py:if="user.coredumps">
                    <th class="alert">Core Dumps</th>
                    <td><a href="${tg.url( 'coredumps', user=user.name )}">${len( user.coredumps )}</a></td>
                </tr>
            </table>
        </div>

        <div class="bordered table-container">
            <h2 class="heading">Start</h2>
            <table class="layout-only">
                <tr>
                    <td>
                        <input type="radio" name="mode" value="single"
                               id="ccStartMachineMode" checked="checked"
                               onchange="onSelectMachines( this.form.machine )"/>
                    </td>
                    <td>
                        On a single machine:
                    </td>
                    <td>
                        <select py:replace="selectList( 'machine',
                            [m.name for m in machines], prefs.last_machine )"/>
                    </td>
                </tr>
                <tr>
                    <td>
                        <input type="radio" name="mode" value="layout"
                               id="ccStartLayoutMode"
                               onchange="onSelectMachines( this.form.layout )"/>
                    </td>
                    <td>
                        From a saved layout:
                    </td>
                    <td>
                        <select py:replace="selectList( 'layout',
                                            savedLayouts, prefs.last_layout )"/>
                    </td>
                </tr>
                <tr>
                    <td>
                        <input type="radio" name="mode" value="group"
                               id="ccStartGroupMode"
                               onchange="onSelectMachines( this.form.group )"/>
                    </td>
                    <td>
                        On a group of machines:
                    </td>
                    <td>
                        <select py:replace="selectList( 'group',
                                            groups, prefs.last_group )"/>
                    </td>
                </tr>
                <tr>
                    <td/>
                    <td>
                        <label>Restrict components by tags:</label>
                    </td>
                    <td>
                        <input type="checkbox" name="restrict" value="true"
                               id="ccRestrictFlag" checked="checked" disabled="true"/>
                    </td>
                </tr>
                <tr>
                    <td/>
                    <td colspan="2">
                        <input type="submit" id="ccStartSubmit" value="Go!"/>
                    </td>
                </tr>
            </table>
		</div>
	</form>

	<!-- JavaScript stuff -->
	<script type="text/javascript" src="static/js/start.js"/>
	<script type="text/javascript">
		var username = "${user.name}";

		// Disable modes that don't make sense
		if (${len( groups )} == 0)
		{
			$( "ccStartGroupMode" ).disabled = true;
			document.startForm.group.disabled = true;
		}

		if (${len( savedLayouts )} == 0)
		{
			$( "ccStartLayoutMode" ).disabled = true;
			document.startForm.layout.disabled = true;
		}

		if ("${prefs.last_mode}" == "single")
		{
			$( "input:radio[name=mode]" )[0].checked = true;
		}
		else if ("${prefs.last_mode}" == "group" &amp;&amp; !$( "ccStartGroupMode" ).disabled)
		{
			$( "input:radio[name=mode]" )[2].checked = true;
		}
		else if (!$( "ccStartLayoutMode" ).disabled)
		{
			$( "input:radio[name=mode]" )[1].checked = true;
		}

		onSelectMachines( null );
	</script>

</div></body>
</html>

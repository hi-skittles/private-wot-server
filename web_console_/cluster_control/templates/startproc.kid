<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<?python
  layout_params[ "pageHeader" ] = "Start Processes"
?>

<html xmlns="http://www.w3.org/1999/xhtml"
	  xmlns:py="http://purl.org/kid/ns#"
      py:layout="'../../common/templates/layout_css.kid'"
      py:extends="'../../common/templates/common.kid'">

<div py:def="moduleContent()">

	<script type="text/javascript">
		document.title = 'Start Processes - WebConsole';
	</script>

	<select py:def="selectList( name, options, selected, jsFunc )"
			name="${name}" style="width: 100%"
			onChange="${jsFunc}( this.value );">

			<loop py:for="o in options">
				<option py:if="o[0] == selected"
						selected="selected" value="${o[0]}">${o[1]}</option>

				<option py:if="o[0] != selected" value="${o[0]}">${o[1]}</option>
			</loop>
	</select>

	<table class="bordered layout-only">
		<tr py:replace="tableHeader( 'Starting as' )"/>
		<tr><td>User</td><td>${user.name}</td></tr>
		<tr><td>UID</td><td>${user.uid}</td></tr>
	</table>

	<p/>

	<form action="${tg.url( 'startproc' )}" name="startProcForm">
		<table class="bordered layout-only">
			<tr py:replace="tableHeader( 'Start' )"/>
			<tr>
				<td>
					Server component:
				</td>
				<td py:content="selectList( 'pname',
					proclist, prefs[ 'proc' ],
					'enableInputIfNotSingleton' )"/>
			</tr>
			<tr>
				<td>
					Machine:
				</td>
				<td py:content="selectList( 'machine',
					machines, prefs[ 'machine' ],
					'nullFunc' )"/>
			</tr>

			<tr>
				<td>
					<label>Number of processes:</label>
				</td>
				<td>
					<input type="text" name="count" autocomplete="off" value="${prefs[ 'count' ]}"/>
				</td>
			</tr>

			<tr>
				<td/>
				<td colspan="2">
					<input type="submit" value="Go!"/>
				</td>
			</tr>
		</table>
	</form>

	<!-- JavaScript stuff -->
	<script src="static/js/startproc.js" type="text/javascript"></script>

</div>
</html>

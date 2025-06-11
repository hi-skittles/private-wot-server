<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<?python
  layout_params[ "pageHeader" ] = "Watchers"
  layout_params[ "page_specific_css"] = [ '../static/css/watchers.css' ]
?>

<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
	  py:layout="'../../common/templates/layout_css.kid'"
	  py:extends="'../../common/templates/common.kid'">

<div py:def="moduleContent()" class="content">

	<script type="text/javascript">
		document.title = 'Watchers for ${process.label()} - WebConsole';
	</script>

	<?python
	  import os
	  from web_console.common.util import alterParams

	  pathSplit = watcherData.path.split( "/" )
	?>


	<div class="bordered watcher-list-container">
	<h2 class="heading">Watcher Values for
	    <span class="watcher-path">
            <span py:if="not watcherData.path" py:content="process.label()" py:strip="True"/>
            <span py:if="watcherData.path" py:strip="True">
                <a href="${alterParams( path = '', error=None )}">${process.label()}</a>
                <span py:for="i in xrange( len( pathSplit ) - 1 )" py:strip="True">/
                    <a href="${alterParams( path = '/'.join( pathSplit[:i+1] ), error=None )}">${pathSplit[i]}</a>
                </span>
                / ${pathSplit[-1]}
            </span>
		</span>
	</h2>

	<?python
	  colspan = 4
	?>

	<script type="text/javascript" src="../static/js/collections.js"/>
	<script type="text/javascript" src="../static/js/tree.js"/>

	<script type="text/javascript" src="/static/js/action_table.js"/>
	<script type="text/javascript" src="/static/js/ajax.js"/>
	<script type="text/javascript" src="/static/js/util.js"/>

	<form name="menuForm">
		<table class="watcher">
			<tr>
				<td colspan="${colspan}">
				<a py:if="watcherData.path" href="${alterParams( path = os.path.dirname( watcherData.path ), error=None )}">..</a>
				<a py:if="not watcherData.path" href="${tg.url( '/watchers/tree' )}">..</a>
				</td>
			</tr>

			<tr py:for="dir in subDirs" class="watcherrow">
				<td colspan="${colspan}">
					<a href="${alterParams( path = dir.path, error=None )}">
						${os.path.basename( dir.path )}
					</a>
				</td>
			</tr>
			<tr py:for="(w, menu) in watchers" class="watcherrow">
				<td>${os.path.basename( w.path )} </td>

				<!-- Check if the watcher is a function or not -->
				<td py:if="w.isCallable()">Callable function</td>
				<td py:if="not w.isCallable()">
					<div py:if="w.isReadOnly()" class="read-only-value">${w.valueAsStr()}</div>
					<div py:if="not w.isReadOnly()">${w.valueAsStr()}</div>
				</td>

				<!-- The advanced mode options -->
				<td class="advancedMenu" style="display: none">
					<select name="actionMenu"
						py:replace="actionsMenu( menu, rowID = w.path, help = 'Add the menu now' )"/>
				</td>
			</tr>
		</table>
	</form>
	</div><!-- /watcher-list-container -->

	<!-- Checkbox to toggle display of custom watcher menu -->
	<form name="pageOptions" py:if="len( watcherData.getChildren() or [] ) > 0">
		<input id="advanced" onclick="toggleAdvancedOptions()" type="checkbox" name="showAdvanced"/> <label for="advanced">Advanced Options</label>
	</form>

	<script py:if="error" type="text/javascript">
		Util.error( "Error occured", [ ${error} ] );
	</script>

</div><!-- /moduleContent -->

</html>

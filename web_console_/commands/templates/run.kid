<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<?python
  layout_params['page_specific_css'] = [ "/commands/static/css/runscript.css", "/static/css/dynamic_selectors.css" ]
?>

<html xmlns="http://www.w3.org/1999/xhtml"
	  xmlns:py="http://purl.org/kid/ns#"
	  py:layout="'../../common/templates/layout_css.kid'"
	  py:extends="'../../common/templates/common.kid'">

<div py:def="moduleContent()">

	<script type="text/javascript">
		document.title = 'Commands Library - WebConsole';
	</script>

<div py:if="serverRunning" class="content">

        <h2 class="heading">Command Library</h2>
        <table class="selection_library layout-only">
        <!--<tr py:replace="tableHeader( 'Command Library' )"/>-->
        <!-- Main command area contents -->
        <tbody>
        <tr>
            <td>
                <select size="12" id="scriptSelect" class="primary_select"/>

                <div class="floating_info_pane">
                    <!-- right aligned script information -->
                    <div id="scriptTitlePane"/><br/>
                    <div id="scriptParamPane"/><br/>
                    <form name="executeForm"
                            action="javascript:RunScript.executeScriptFromForm()">
                        <div id="scriptExecutePane"/>
                    </form>
                </div>
            </td>
        </tr>
        </tbody>
        </table>

        <div id="outputContainer" class="pyscript">
            <h3>Return Value</h3>
            <div id="resultPane"/>

            <h3>Console Output</h3>
            <div id="outputPane"/>
        </div>

	<script type="text/javascript" src="${tg.tg_js}/MochiKit.js"/>
	<script type="text/javascript" src="/commands/static/js/runscript.js" />
	<script type="text/javascript" src="/commands/static/js/argtypes.js" />
	<script type="text/javascript">
		<p py:if="runNow" py:strip="True">
			MochiKit.DOM.addLoadEvent( MochiKit.Base.bind( RunScript.executeScript, RunScript, ${runNow.id} ) );
		</p>

		<?python import simplejson ?>
		RunScript.initCategories( ${simplejson.dumps( categories )} );

		function initLoad()
		{
			RunScript.switchCategory( "watcher", "" );
		}
		MochiKit.DOM.addLoadEvent( initLoad );
	</script>

</div> <!-- py:if="serverRunning" -->

<div py:if="not serverRunning">
	No server running.
</div> <!-- py:if="not serverRunning" -->

</div>

</html>

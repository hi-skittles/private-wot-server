<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<?python
  layout_params[ "moduleHeader" ] = "StatGrapher"
  layout_params[ "page_specific_css"] = [ "/statg/static/css/stat_grapher.css"]
?>

<html xmlns="http://www.w3.org/1999/xhtml"
	  xmlns:py="http://purl.org/kid/ns#"
	  py:layout="'../../common/templates/layout_css.kid'"
	  py:extends="'../../common/templates/common.kid'">

<body>
<div py:def="moduleContent()" class="content">

		<script type="text/javascript">
		//<![CDATA[
			document.title = 'Graphs - Web Console';
		//]]>
		</script>

		<script type="text/javascript" src="${tg.tg_js}/MochiKit.js"></script>
		<script type="text/javascript" src="/statg/static/js/exception.js"></script>
		<script type="text/javascript" src="/statg/static/js/flashtag.js"></script>
		<script type="text/javascript" src="/statg/static/js/flashserializer.js"></script>
		<script type="text/javascript" src="/statg/static/js/flashproxy.js"></script>
		<script type="text/javascript" src="/statg/static/js/legend.js"></script>
		<script type="text/vbscript" src="/statg/static/js/vbcallback.vbs"></script>
		<script type="text/javascript" src="/statg/static/js/swfobject.js"></script>

		<table  id="graphtable" class="layout-only">
		<tr>
			<td id="flashCell" >
				<div id="flashDiv">
				Flash Player 9 or higher required. Go
				<a href="http://www.adobe.com/go/getflashplayer">here</a>
				to get it!

				<script type="text/javascript">
					jQuery( 'html' ).addClass( 'contains-flash' );
					
					var flashId = new Date().getTime();
					var flashProxy = new FlashProxy( flashId, "graphDisplay",
							'/statg/static/swf/javascriptflashgateway.swf' );
					var so = new SWFObject("/statg/static/swf/graph.swf","graphDisplay",
							'100%', '100%', "9", "#FFFFFF" );
					so.addVariable( 'flashId', flashId );
					so.addVariable( 'logName', "$log" );
					so.addVariable( 'user', "$user" );
					so.addVariable( 'profile', '$profile' );
					so.addVariable( 'serviceURL', "$serviceURL" );
					so.addVariable( 'bwdebug', "${debug and 'true' or 'false'}" );
					so.addVariable( 'desiredPointsPerView', "$desiredPointsPerView" );
					so.addVariable( 'minGraphWidth', "$minGraphWidth" );
					so.addVariable( 'minGraphHeight', "$minGraphHeight" );
					so.addParam( 'scale', 'noscale' );
					so.addParam( 'salign', 'tl' );
					so.addParam( 'align', 'middle' );
					so.addParam( 'width', '100%' );
					so.addParam( 'height', '100%' );
					so.addParam( 'id', 'graphDisplay' );
					//so.useExpressInstall('/statg/static/swf/expressinstall.swf');
					so.write("flashDiv");
				</script>
				</div>
				<div class="preferencesInfoDialog" id="stat_pref_edit_dialog" style="display: none;">
					<div id="stat_pref_edit_contents" class="stat_pref_edit"/>
				</div>
			</td>

			<td id="legendCell" class="legend" >
				<div id="legendDiv"></div>
			</td>
		</tr>
		</table>
		<div py:if="debug">
			<textarea cols="80" rows="24" id="flashDebugOutput" editable="no"></textarea><br/>
			<button onClick="document.getElementById( 'flashDebugOutput' ).value = ''; return true;">clear</button>
		</div>

<!-- colour picker palette -->
<table py:replace="staticColourPickerPalette()" />

</div><!-- /moduleContent -->

</body>

</html>

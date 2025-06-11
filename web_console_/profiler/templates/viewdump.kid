<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<?python
  layout_params[ "page_specific_css" ] = [ "/static/third_party/trace-viewer/trace-viewer.css" 
                                         , "static/css/profiler.css" 
                                        ]
?>

<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#" xmlns:bw="http://bigworldtech.com.au"
      py:layout="'../../common/templates/layout_css.kid'"
      py:extends="'../../common/templates/common.kid'">


<div py:def="moduleContent()" class="content">
<script type="text/javascript" src="/static/third_party/trace-viewer/trace-viewer.js"></script>
<script type="text/javascript" src="static/js/view-dump.js"></script>
<script type="text/javascript">//<![CDATA[
    var fileName = "${fileName}"; // populated by python
	var userName = "${userName}"; // populated by python
    document.title = fileName + ' - WebConsole';
// ]]>
</script>

<div id="trace-viewer-container">
    <h2 class="heading">${ 'Profiler Dump: %s' % fileName }</h2>
    <div class="trace-viewer-panel">
    </div>
</div>

</div>

</html>

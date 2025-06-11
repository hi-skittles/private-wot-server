<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<?python
  layout_params[ "page_specific_css"] = [ "/static/third_party/jquery-plugin-dataTables/css/jquery.dataTables.css"
                                        , "/static/css/dynamic_table.css"
                                        , "static/css/spaceviewer.css"
                                        , "static/css/show_spaces.css"
                                        ]
?>

<html xmlns="http://www.w3.org/1999/xhtml"
      xmlns:py="http://purl.org/kid/ns#"
      py:layout="'../../common/templates/layout_css.kid'"
      py:extends="'../../common/templates/common.kid'">

<div py:def="moduleContent()">

<script type="text/javascript">
    document.title = 'Spaces - WebConsole';
</script>
<script type="text/javascript" src="/static/js/jquery.mousewheel-3.0.6.js"></script>
<script type="text/javascript" src="/static/third_party/jquery-plugin-dataTables/js/jquery.dataTables.js"></script>
<script type="text/javascript" src="/static/third_party/jquery-plugin-dataTables-colReorder/js/ColReorderWithResize.js"></script>
<script type="text/javascript" src="/static/js/dynamic_table.js"></script>
<script type="text/javascript" src="/static/js/chainloader.js"></script>
<script type="text/javascript" src="static/js/animation.js"></script>
<script type="text/javascript" src="static/js/spaceviewer_canvas.js"></script>
<script type="text/javascript" src="static/js/spaceviewer_tiling.js"></script>
<script type="text/javascript" src="static/js/spaces_widget.js"></script>
<script type="text/javascript" src="static/js/show_spaces.js"></script>

<!-- table of current spaces -->
<div id="dynamic-spacelist"></div>

<!-- server notifications -->
<div class="alert-notification-container"></div>

<!-- embedded spaceviewer preview template section -->
<div id="embedded-spaceviewer-template" style="display: none">
    <div class="sv-container">
        <canvas class="sv-canvas">
            <p>
                SpaceViewer requires a browser that supports the
                <code>canvas</code> element - yours doesn't.
                Please consider upgrading to a supported browser.
            </p>
        </canvas>
        <div class="sv-zoom-control sv-fade-animation">
            <a onclick="getSpaceviewer( this ).zoomIn()" title="Zoom in (+)"><i class="icon-plus"></i></a>
            <a onclick="getSpaceviewer( this ).zoomOut()" title="Zoom out (-)"><i class="icon-minus"></i></a>
            <a onclick="getSpaceviewer( this ).zoomToSpaceBounds()" title="Zoom to space bounds ([space])"><i class="icon-resize-full"></i></a>
        </div>
    </div><!-- /sv-container -->

    <div class="space-detail-info-pane">
        <h2><!-- space name --></h2>
    </div>
</div>

<!-- forward ref to FontAwesome to force loading prior to use in Alert -->
<div style="font-family: FontAwesome; visibility: hidden">dummy text</div>

</div>
</html>


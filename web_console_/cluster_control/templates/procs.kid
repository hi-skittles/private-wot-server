<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<?python
  layout_params[ "page_specific_css"] = [ "/static/third_party/jquery-plugin-dataTables/css/jquery.dataTables.css"
                                        , "/static/third_party/jquery-plugin-dataTables-colReorder/css/ColReorder.css"
                                        , "/static/css/dynamic_table.css"
                                        , "static/css/control_cluster.css"
                                        ]
?>

<html xmlns="http://www.w3.org/1999/xhtml"
      xmlns:py="http://purl.org/kid/ns#"
      py:layout="'../../common/templates/layout_css.kid'"
      py:extends="'../../common/templates/common.kid'">

<div py:def="moduleContent()">

    <script src="/static/third_party/jquery-plugin-dataTables/js/jquery.dataTables.js"></script>
    <script src="/static/third_party/jquery-plugin-dataTables-colReorder/js/ColReorderWithResize.js"></script>
    <script src="/static/js/dynamic_table.js"></script>
    <script src="/cc/static/js/cluster_control_widget.js"></script>

    <!-- process list table -->
    <div id="dynamic-processlist"></div>

    <div class="alert-notification-container"></div>

    <script type="text/javascript">
    //<![CDATA[

    document.title = 'Cluster Processes - WebConsole';

    var processTable;
    jQuery( document ).ready( function()
    {
        processTable = new ControlClusterWidget( '#dynamic-processlist', {
            title: "Processes"
        });

        // Start automatic polling
        // processTable.connectModel();
        processTable.updatePauseUpdatesButtonConnectionStatus();

        jQuery( document ).one( 'keypress', function() {
            processTable.dom.container.find( 'input[type="text"]' ).focus();
        });
    });

    // ]]>
    </script>

</div>


</html>

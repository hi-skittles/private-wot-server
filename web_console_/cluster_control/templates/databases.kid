<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<?python
  layout_params[ "page_specific_css"] = [ "/static/css/dynamic_table.css"
                                        , "/static/third_party/jquery-chosen/chosen.css"
                                        , "static/css/control_cluster.css"
                                        , "static/css/cluster_databases_widget.css"
                                        ]
?>

<html xmlns="http://www.w3.org/1999/xhtml"
      xmlns:py="http://purl.org/kid/ns#"
      py:layout="'../../common/templates/layout_css.kid'"
      py:extends="'../../common/templates/common.kid'">

<div py:def="moduleContent()">

    <style type="text/css">
    .table-container {
        display: block;
        word-wrap: break-word;
    }

    .chzn-container-single {
        min-width: 150px;
    }
    </style>

    <div class="alert-notification-container"></div>

    <div class="bordered animated table-container cluster-databases-widget">
        <h2>Databases</h2>
        <div class="dynamic-table-header cluster-control-actions">
            <button action="consolidate_dbs">Consolidate Secondary Databases</button>
            <button action="clear_dbs">Clear Secondary Databases</button>
            <button action="clear_autoload">Clear Autoloaded Entities</button>
            <button action="sync_db">Synchronise Entity Definitions</button>
            <button action="cancel">Cancel</button>
        </div>
        <form class="select-machine animated">
            Select machine from which to run command:
            <select name="machine" data-placeholder="any machine">
                <option></option>
                <option py:for="m in machines">${ m.name }</option>
            </select>
        </form>
        <div class="output"></div>
    </div>

    <!-- JS -->
    <script src="/static/third_party/jquery.deserialize.js" type="text/javascript"></script>
    <script src="/static/js/ajax.js" type="text/javascript"></script>
    <script src="/static/js/async_task.js" type="text/javascript"></script>
    <script src="/log/static/js/log_viewer.js"></script>
    <script src="/static/third_party/jquery-chosen/chosen.jquery.js" type="text/javascript"></script>
    <script src="/cc/static/js/process_control.js"></script>
    <script src="/cc/static/js/cluster_databases_widget.js"></script>
    <script type="text/javascript">
    //<![CDATA[

        document.title = "Databases - WebConsole";

        jQuery( 'select' ).chosen( { allow_single_deselect: true } );

        LogViewer.Query.Defaults.debug = 2;

        var widget;
        jQuery( document ).ready( function() {
            widget = new BigWorld.DatabaseWidget( '.cluster-databases-widget' );
        });

    // ]]>
    </script>

</div>
</html>

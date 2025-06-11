<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<?python
  layout_params[ "pageHeader" ] = "Machines"
  layout_params[ "page_specific_css"] = [ "/static/third_party/jquery-plugin-dataTables/css/jquery.dataTables.css"
                                        , "/static/third_party/jquery-plugin-dataTables-colReorder/css/ColReorder.css"
                                        , "/static/css/dynamic_table.css"
                                        , "static/css/control_cluster.css"
										, "/static/third_party/jquery-ui/css/jquery-ui.css"
                                        ]
?>

<html xmlns="http://www.w3.org/1999/xhtml"
      xmlns:py="http://purl.org/kid/ns#"
      py:layout="'../../common/templates/layout_css.kid'"
      py:extends="'../../common/templates/common.kid'">

<div py:def="moduleContent()">

    <script src="/static/third_party/jquery-plugin-dataTables/js/jquery.dataTables.js"></script>
    <script src="/static/third_party/jquery-plugin-dataTables-colReorder/js/ColReorderWithResize.js"></script>
	<script src="/static/third_party/jquery-plugin-sparkline/jquery.sparkline.js"></script>
	<script src="/static/third_party/jquery-ui/jquery-ui.js"></script>
	<script src="/static/js/browser_detect.js" type="text/javascript"/>
    <script src="/static/js/dynamic_table.js"></script>
    <script src="static/js/cluster_machines_widget.js"></script>

    <!-- machine list -->
    <div class="machine-list"></div>

    <!-- alerts -->
    <div class="alert-notification-container"></div>

    <style>
    .low {}
    .med { color: darkorange; }
    .high { color: red; }
	.max-arrow { color: red; }
	.min-arrow { color: blue; }
	
    .group { float: left; color: #aaa; }
    .group:first-child { clear: left; }
	.cpu-load-data { display: inline-block; margin-left: 5px; width: 45px; }
	.avg { display: inline-block; vertical-align: top; margin-top: 6px; width: 33px; }
	.cpu-load-data .minmax { display: inline-block; }
	.cpu-load-data span { font-size: smaller; }
	.cpu-load-sparkline canvas { background-color: #e6e6e6; } 
	
	td.cpu-load { background-image: url('../static/images/tool_tip.png'); background-position: right top; background-repeat: no-repeat; padding: 1px 10px !important; }
	td.num-procs { background-image: url('../static/images/tool_tip.png'); background-position: right top; background-repeat: no-repeat; }

	.mem:after { content: '%'; margin-left: 3px; }

    .proc-list:empty:after { content: 'none'; font-style: italic; color: #aaa; }

    .proc { padding: 2px 5px; }
    .proc:after { content: '(' attr( count ) ')'; margin-left: 3px; }
    .proc[count="0"] { color: #ccc; }
    .proc[count="0"]:after { content: none; }
    .proc[count="1"]:after { content: none; }

    .cpus { white-space: nowrap; }

    .dataTable tbody td.platform:empty:after {
        content: '(unknown)';
        font-style: italic;
        color: #aaa;
    }

	.hostname a, .hostname a:active, .hostname a:visited { color: #105293 !important; text-decoration: underline !important; } 
	.hostname a:hover { color: #FF8000 !important; }

    .net { float: left; min-width: 85px; padding: 2px; }
    .net:before { content: attr( if ) ': '; width: 45px; }

    .hostname { white-space: nowrap; }
	.platform { min-width: 65px; }
	.cpu-load { min-width: 230px; }
	.num-procs { min-width: 70px; }

	.machined { white-space: nowrap; min-width: 120px; }
    .machined .not-latest-version { color: red; font-weight: bold; }
	
	.ui-tooltip { background: rgba(51,51,51,0.8); border: white solid; border-width: 1px !important; color: white; border-radius: 0 !important; }
	.ui-tooltip .high { color: #ff7a7a; }
	.ui-tooltip .med { color: #ffc277; }
	.jqsfield { color: white; font: 10pt arial, san serif; text-align: left; }
	
	.dataTables_wrapper { display: inline-block; }
    </style>

    <script type="text/javascript">
    //<![CDATA[

    document.title = 'Cluster Machines - WebConsole';

    var machinesTable;
    jQuery( document ).ready( function()
    {
        machinesTable = new ClusterMachinesWidget( '.machine-list' );
        machinesTable.connectModel();

        jQuery( document ).one( 'keypress', function() {
            machinesTable.dom.container.find( 'input[type="text"]' ).focus();
        });
    });

    // ]]>
    </script>

</div>
</html>

<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<?python
  layout_params[ "page_specific_css"] = [ "static/css/spaceviewer.css" ]
?>

<html xmlns="http://www.w3.org/1999/xhtml"
	  xmlns:py="http://purl.org/kid/ns#"
	  py:layout="'../../common/templates/layout_css.kid'"
	  py:extends="'../../common/templates/common.kid'">

<div py:def="moduleContent()" class="content">

<script type="text/javascript" src="/static/js/jquery.mousewheel-3.0.6.js"></script>
<script type="text/javascript" src="/static/third_party/jquery.hammer.js"></script>
<script type="text/javascript" src="static/js/animation.js"></script>
<script type="text/javascript" src="/static/js/chainloader.js"></script>
<script type="text/javascript" src="static/js/spaceviewer_canvas.js"></script>
<script type="text/javascript" src="static/js/spaceviewer_minimap.js"></script>
<script type="text/javascript" src="static/js/spaceviewer_tiling.js"></script>
<script type="text/javascript" src="static/js/spaceviewer_detail_page.js"></script>

<style type="text/css">
    /*
    *   Have to special-case left menu hiding for spaceviewer because of the
    *   need to pan the canvas to maintain the user's world perspective. the below
    *   CSS sets the "menu-collapsed" state to be (more or less) the same as the
    *   uncollapsed state, so that spaceviewer page script can handle the hiding
    *   and panning.
    */

    /* override */ #main.menu-collapsed {
        left: 130px;
    }
    /* override */ #navmenu_cell.menu-collapsed {
        left: 0px;
        display: none;
    }
    /* override */ .resizable {
        -webkit-transition-property: background-image;
        -moz-transition-property: background-image;
        -ms-transition-property: background-image;
        -o-transition-property: background-image;
        transition-property: background-image;
	}
</style>

<script type="text/javascript">//<![CDATA[
    var spaceId = ${spaceId}; // populated by python
    var numInitialServiceApps = ${serviceapps}; // populated by python
    document.title = 'Space ' + spaceId + ' - WebConsole';
// ]]>
</script>

<!--~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ spaceviewer ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~-->
<div class="sv-container-container">
<div class="sv-container">

    <div class="heading sv-header">
    <div class="sv-space-title">Space ${spaceId}</div>
        <div class="sv-button-container">
            <button style="display: none" class="sv-resume-button" onclick="sv.connectModel(); jQuery(this).fadeOut();">Resume</button>
            <button onclick="toggleLoadBalancePanel( this )" class="load-balance-button">Load Balancing</button>
            <button onclick="toggleSettings( this )" class="setting-button">Settings</button>
        </div>
    </div>
    <canvas class="sv-canvas" id="space_viewer">
        <p>
            SpaceViewer requires a browser that supports the
            <code>canvas</code> element - yours doesn't.
            Please consider upgrading to a supported browser.
        </p>
    </canvas>
    <div class="sv-status-info sv-fade-animation">
        <div class="sv-coords"><span class="x_pos">(x)</span>,&nbsp;<span class="y_pos">(y)</span></div>
        <div class="sv-bounds">(left,bottom to right,top)</div>
        <div class="sv-cell-stats">(count) of (total) cellapps,</div>
        <div class="sv-entity-stats">(count) real entities, (count) ghost entities</div>
    </div>
    <div class="sv-zoom-control sv-fade-animation">
        <a onclick="sv.zoomIn()" title="Zoom in (+)"><i class="icon-plus"></i></a>
        <a onclick="sv.zoomOut()" title="Zoom out (-)"><i class="icon-minus"></i></a>
        <a onclick="sv.zoomToSpaceBounds()" title="Zoom to space bounds ([space])"><i class="icon-resize-full"></i></a>
    </div>
    <div class="alert-notification-container"></div>
    <div class="sv-minimap sv-fade-animation">
        <div class="sv-minimap-container">
            <canvas id="minimap" class="sv-fade-animation"></canvas>
        </div>
    </div>
    <div class="sv-debug sv-fade-animation" style="display: none">
        <div id="sv-perfgraph"></div>
        <div class="tiling"></div>
    </div>
    <div class="sv-popup-menu sv-event-ignore">
        <ul class="contains-link dropdown-menu sv-popup-menu-list">
            <li class="popup-menu-title"></li>
            <li class="retire-cell"><a href="#"/>Retire this cell</li>
            <li class="cancel-retire"><a href="#"/>Cancel retiring this cell</li>
            <li class="split-cell"><a href="#"/>Split this cell</li>
            <li class="non-splittable-tip">(not enough cellapps)</li>
        </ul>
    </div>
</div><!-- /sv-container -->

<!--~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ colour picker ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~-->
<div id="sv-config-panel" class="bordered touch-moveable">
    <table class="legendTable legend">

        <tbody id="sv-config-space">
        <tr><th colspan="3">Space</th></tr>
        <tr>
            <td><input id="chkbox_spaceBackgroundImage" type="checkbox" onchange="UI.spaceBackgroundImage.enabled = !UI.spaceBackgroundImage.enabled; sv.draw()"/></td>
            <td></td>
            <td><abbr title="Toggle space background images">Space background image</abbr></td>
        </tr>
        <tr>
            <td><input id="chkbox_animation" type="checkbox" onchange="UI.animation.enabled = !UI.animation.enabled;"/></td>
            <td></td>
            <td><abbr title="Toggle animations">Animations</abbr></td>
        </tr>
        <tr>
        <td><input id="chkbox_interpolation" type="checkbox" onchange="toggleInterpolation()"/></td>
            <td></td>
            <td><abbr title="Toggle interpolation of entity and partition position between data ticks">Interpolation</abbr></td>
        </tr>
        <tr>
        <td><input id="chkbox_minimap" type="checkbox" onchange="toggleMinimap()"/></td>
            <td></td>
            <td><abbr title="Toggle minimap">Minimap</abbr></td>
        </tr>
        <!--
        <tr>
        <td><input id="chkbox_spaceBackgroundTileLayer" type="checkbox" onchange="UI.spaceBackgroundTileLayer.enabled = !UI.spaceBackgroundTileLayer.enabled; sv.draw()"/></td>
            <td></td>
            <td><abbr title="Toggle high-resolution background tile layer">High-resolution backgrounds</abbr></td>
        </tr>
        -->
        </tbody>

        <tbody id="sv-config-partitions">
        <tr><th colspan="3">Partitions</th></tr>
        <tr>
            <td style="border-bottom: none; border-right: none"><input id="chkbox_partitionLine" type="checkbox" onchange="UI.partitionLine.enabled = !UI.partitionLine.enabled; sv.draw()"/></td>
            <td><div id="colour_partitionLine" class="sv-config-colour-selector sv-partition-line"></div></td>
            <td><abbr title="Show/Hide partitions (p)">Partition line</abbr></td>
        </tr>
        <tr>
            <td style="border-bottom: none; border-top: none; border-right: none"></td>
            <td style="border-top: none; border-left: none; border-bottom: none;"><input id="chkbox_partitionLabel_load" type="checkbox" onchange="UI.partitionLabel_load.enabled = !UI.partitionLabel_load.enabled; sv.draw()"/></td>
            <td><abbr title="Show/Hide partition load label">Partition load</abbr></td>
        </tr>
        <tr>
            <td style="border-bottom: none; border-top: none; border-right: none;"></td>
            <td style="border-left: none; border-top: none;"><input id="chkbox_partitionLabel_aggression" type="checkbox" onchange="UI.partitionLabel_aggression.enabled = !UI.partitionLabel_aggression.enabled; sv.draw()"/></td>
            <td><abbr title="Show/Hide partition aggression label">Partition aggression</abbr></td>
        </tr>
        </tbody>

        <tbody id="sv-config-cells">
        <tr><th colspan="3">Cells</th></tr>
        <tr>
            <td><input id="chkbox_chunkBounds" type="checkbox" onchange="UI.chunkBounds.enabled = !UI.chunkBounds.enabled; sv.draw()"/></td>
            <td><div id="colour_chunkBounds" class="sv-config-colour-selector sv-chunk-bounds"></div></td>
            <td><abbr title="Show/Hide loaded chunk grid (k)">Chunk grid</abbr></td>
        </tr>
        <tr>
            <td><input id="chkbox_entityBounds" type="checkbox" onchange="UI.entityBounds.enabled = !UI.entityBounds.enabled; sv.draw()"/></td>
            <td><div id="colour_entityBounds" class="sv-config-colour-selector sv-entity-bounds"></div></td>
            <td><abbr title="Show/Hide entity bound level rects (b)">Entity bound levels</abbr></td>
        </tr>
        <tr>
            <td style="border-bottom: none; border-right: none;"><input id="chkbox_cellLabel" type="checkbox" onchange="UI.cellLabel.enabled = !UI.cellLabel.enabled; sv.draw()"/></td>
            <td><div id="colour_cellLabel" class="sv-config-colour-selector sv-cell-label"></div></td>
            <td><abbr title="Show/Hide cell labels (c)">Cell labels</abbr></td>
        </tr>
        <tr>
            <td style="border-top: none; border-bottom: none; border-right: none;"></td>
            <td style="border-top: none; border-bottom: none; border-left: none;"><input id="chkbox_cellLabel_cellId" type="checkbox" onchange="UI.cellLabel_cellId.enabled = !UI.cellLabel_cellId.enabled; sv.draw()"/></td>
            <td><abbr title="Show/Hide cell ID in cell label">Cell ID</abbr></td>
        </tr>
        <tr>
            <td style="border-top: none; border-bottom: none; border-right: none;"></td>
            <td style="border-top: none; border-bottom: none; border-left: none;"><input id="chkbox_cellLabel_ipAddress" type="checkbox" onchange="UI.cellLabel_ipAddress.enabled = !UI.cellLabel_ipAddress.enabled; sv.draw()"/></td>
            <td><abbr title="Show/Hide IP address in cell label">IP address</abbr></td>
        </tr>
        <tr>
            <td style="border-top: none; border-right: none;"></td>
            <td style="border-top: none; border-left: none;"><input id="chkbox_cellLabel_load" type="checkbox" onchange="UI.cellLabel_load.enabled = !UI.cellLabel_load.enabled; sv.draw()"/></td>
            <td><abbr title="Show/Hide relative cell load in cell label">Cell load</abbr></td>
        </tr>
        <tr>
            <td><input id="chkbox_cellLoad" type="checkbox" onchange="UI.cellLoad.enabled = !UI.cellLoad.enabled; sv.draw()"/></td>
            <td></td>
            <td><abbr title="Show/Hide cell load as background tint">Cell load tint</abbr></td>
        </tr>
        <tr>
            <td></td>
            <td><input id="chkbox_cellLoad_useRelativeLoad" type="checkbox" onchange="UI.cellLoad_useRelativeLoad.enabled = !UI.cellLoad_useRelativeLoad.enabled; sv.draw()"/></td>
            <td><abbr title="Toggle displaying relative (l) or absolute (shift-l) cell load">Relative load</abbr></td>
        </tr>
        </tbody>

        <tbody id="sv-config-entities">
        <tr><th colspan="3">Entities</th></tr>
        <tr>
            <td><input id="chkbox_entity" type="checkbox" onchange="UI.entity.enabled = !UI.entity.enabled; sv.draw()"/></td>
            <td></td>
            <td><abbr title="Show/Hide real entities for the currently selected cell (e)">Real entities</abbr></td>
        </tr>
        <tr>
            <td><input id="chkbox_ghostEntity" type="checkbox" onchange="UI.ghostEntity.enabled = !UI.ghostEntity.enabled; sv.draw()"/></td>
            <td></td>
            <td><abbr title="Show/Hide ghosted entities for the currently selected cell (g)">Ghost entities</abbr></td>
        </tr>
        <tr>
            <td><input id="chkbox_entityIcons" type="checkbox" onchange="UI.entityIcons.enabled = !UI.entityIcons.enabled; 	updateEntityIcons(); sv.draw()"/></td>
            <td></td>
            <td><abbr title="Toggle between drawing entities as icons or circles (i)">Entities as icons</abbr></td>
        </tr>
        </tbody>

    </table>
</div><!-- /sv-config-panel -->

<div id="load-balance-panel" class="bordered touch-moveable">
    <div class="load-balance-title">
        Load Balancing
    </div>
    <div class="load-balance-settings server-load-balance">
        <div class="setting-title">
            Server Load Balancing
        </div>
        <div class="radio-buttons">
            <div class="disable-button">
                <input type="radio" name="server_load_balancing" value="disabled"/>
                <label>Disabled</label>
            </div>
            <div class="enable-button">
                <input type="radio" name="server_load_balancing" value="enabled"/>
                <label>Enabled</label>
            </div>
        </div>
    </div>
    <div class="load-balance-settings meta-load-balance">
        <div class="setting-title">
            Server Cell Creation/Retiring
        </div>
        <div class="radio-buttons">
            <div class="disable-button">
                <input type="radio" name="meta_load_balancing" value="disabled"/>
                <label>Disabled</label>
            </div>
            <div class="enable-button">
                <input type="radio" name="meta_load_balancing" value="enabled"/>
                <label>Enabled</label>
            </div>
        </div>
    </div>
    <div class="load-balance-settings manual-load-balance">
        <div class="setting-title">
           Manual Load Balancing 
        </div>
        <div class="radio-buttons">
            <div class="disable-button">
                <input type="radio" name="manual_load_balancing" value="disabled"/>
                <label>Disabled</label>
            </div>
            <div class="enable-button">
                <input type="radio" name="manual_load_balancing" value="enabled"/>
                <label>Enabled</label>
            </div>
        </div>
    </div>
</div><!-- /load-balance-panel -->

</div><!-- /sv-container-container -->


<!-- colour picker palette -->
<table py:replace="staticColourPickerPalette()" />


</div><!-- /moduleContent -->

</html>

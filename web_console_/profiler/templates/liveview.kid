<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">


<?python
layout_params[ "page_specific_css"] = [ "static/css/profiler.css"
                                      , "/static/third_party/jquery-chosen/chosen.css"
                                      ]
?>

<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
      py:layout="'../../common/templates/layout_css.kid'"
      py:extends="'../../common/templates/common.kid'">

 

<div py:def="moduleContent()" class="live-view flexboxed">
    <div class="alert-notification-container"></div>

    <div class="bordered profile-form-container">
        <h2 class="heading">Live View of ${processName}(${pid}) on ${machine}</h2>

        <div class="profile-options-controls">
            <div class="profile-options">
                <select name="sort-mode" class="sort-mode search-field-disabled">
                    <option value="SORT_BY_TIME">Sort by Time</option>
                    <option value="SORT_BY_NAME">Sort by Name</option>
                    <option value="SORT_BY_NUMCALLS">Sort by Number of Calls</option>
                    <option value="HIERARCHICAL">Hierarchical</option>
                </select> 
                <select name="exclusive-mode" class="exclusive-mode search-field-disabled">
                    <option value="false">Inclusive</option>
                    <option value="true">Exclusive</option>
                </select> 
                <select name="categories" class="categories search-field-disabled"/>
            </div>

           <div class="profile-controls">
                <button class="prev-entry">Previous Entry</button>
                <button class="next-entry">Next Entry</button>
                <button class="toggle-entry">Toggle Entry</button>
            </div>
         </div>
        
        <div class="profile-record-container">
            <div class="profile-record-pane">
                <div class='profile-actions'>
                    <button class="start-profile">Start</button>
                    <button class="stop-profile">Stop</button>
                    <button class="start-record">Record</button>
                    <button class="cancel-record">Stop Recording</button>
                </div>

                <div class="record-settings">
                    <label>Enter the number of ticks to be recorded: </label>
                    <input type="text" class="record-ticks" value="15" size="5" />
                    <button class="do-record">Go</button>
					<span id="recording-estimation"></span>
                </div>

                <div class="record-status">
                    <p class="record-status-text"></p>
                    <img class="record-spinner" src="/static/images/throbber.gif" />
                </div>

                <div class="record-result">
                    <p class="record-result-text">Recording finished.</p>
                    <a class="view-recording" href="#">Click to View</a>
                </div>
            </div><!-- profile-record-pane -->
        </div><!-- /profile-record-container -->
    </div><!--/profile-form-container-->

    <div class="stat-output-header">
        <h2>Statistics</h2>
        <div class="stat-output-status">
            <div class="status-indicator">Profile is stopped</div>
            <img class="decrease-font-size" title="Decrease font size" src="/static/images/font_small.png" />
            <img class="increase-font-size" title="Increase font size" src="/static/images/font_large.png" />
            <img class="idle-spinner" src="/static/images/throbber.png" />
            <img class="progress-spinner" src="/static/images/throbber.gif" />
        </div>
    </div><!--/stat-output-header-->
    
    <div class="stat-output-container">
            <div class="stat-output-pane"></div>
    </div><!--/stat-output-container-->

	<script src="/static/js/browser_detect.js" type="text/javascript"/>
    <script src="static/js/live-view.js" type="text/javascript"></script>  
    <script src="/static/third_party/jquery-chosen/chosen.jquery.js" type="text/javascript"></script>
    <script type="text/javascript">
        document.title = 'Live View - WebConsole';
        jQuery( document ).ready( initLiveView( ".live-view", "${machine}", 
                                       "${pid}" ) ); 
        window.onbeforeunload = beforeUnload;
    </script>

</div>:w


</html>

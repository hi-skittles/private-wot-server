<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<?python
  layout_params[ "page_specific_css"] = [ 'static/css/profiler.css' ]
?>

<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
      py:layout="'../../common/templates/layout_css.kid'"
      py:extends="'../../common/templates/common.kid'">


<div py:def="moduleContent()" class="content">
    <div class="alert-notification-container"></div>

    <div class="bordered table-container" id="json-files-table">
        <h2 class="heading">Profiler JSON Dumps</h2>
        <table class="sortable">
            <thead>
                <tr class="sortrow">
                    <th>File Name</th>
                    <th>Size</th>
                    <th>Upload Time</th>
                    <th>Action</th>
                </tr>
            </thead>
            <tbody>
                <tr py:if="dumps" py:for="file in dumps">
                    <td py:content="file.fileName"/>
                    <td py:content="file.size"/>
                    <td py:content="file.timestamp"/>
                    <td><div class="recording-file-actions">
                            <a href="${tg.url( 'view',
                                fileName=file.fileName )}">View</a>
                            <a href="${tg.url( 'delete',
                                    fileName=file.fileName )}">&nbsp;Delete</a>
                        </div>
                        <div class="recording-hint-text">Incompatible browser</div>
                    </td>
                </tr>
                <tr py:if="not dumps">
                    <td colspan="4" style="text-align: center">No profiler dumps</td>
                </tr>
           </tbody>
        </table>
    </div>
    <div class="upload-file">
        <form class="upload-form" action="upload" method="POST" enctype="multipart/form-data">
            <input type="file" id="uploadFile" name="uploadFile"/>
            <input type="submit" class="submit-upload" value="Upload"/>
            <img id="spinner" style="display:none" src="/static/images/throbber.gif" />
        </form>
    </div>

    <script type="text/javascript" src="/static/js/table.js"/>
    <script type="text/javascript" src="/static/js/browser_detect.js"/>
    <script type="text/javascript">
    //<![CDATA[
        document.title = 'Profiler Dumps- WebConsole';
        jQuery( document ).ready( function() { 
            var browserSupported = true;
            if (BrowserDetect.browser != "Chrome" || !(BrowserDetect.version >= 25) )
            {
                browserSupported = false;    
            }

            Table.init();

            if (browserSupported && BW.user.isCurrentPageOwner)
            {
                jQuery('.upload-file').show();
            }

            if (!browserSupported)
            {
                jQuery( '#json-files-table' ).addClass( 'incompatible-browser' );
                new Alert.Error( 'Viewing Profiler dumps is disabled as your browser is not currently supported.  Only Chrome of version 25 or later is supported.' );
            }
        } );
        
        jQuery( '.upload-form' ).submit( function( event )
        {
            if( jQuery( '#uploadFile' ).val() === "" )
            {
                new Alert.Warning( 'No file is specified.' + 
                    ' Please choose a file and try again' );
                return false;
            }
            else
            {
                jQuery( '.submit-upload' ).attr("disabled", "disabled");
                jQuery( '#spinner' ).show( 100 );
            }

            return true;
        } );
    // ]]>
    </script>

</div>

</html>

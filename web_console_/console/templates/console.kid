<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<?python
layout_params['page_specific_css'] = [ "/console/static/css/interpreter.css" ]
?>

<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
	  py:layout="'../../common/templates/layout_css.kid'"
	  py:extends="'../../common/templates/common.kid'">

<div py:def="moduleContent()">

    <!--
    this page doesn't actually require all these scripts; defer rationalising
    these until the port to jquery for expediency.
    -->
	<script type="text/javascript" src="${tg.tg_js}/MochiKit.js"/>
	<script type="text/javascript" src="/static/js/util.js"/>
	<script type="text/javascript" src="/static/js/ajax.js"/>
	<script type="text/javascript" src="/static/js/async_task.js"/>
	<script type="text/javascript" src="/console/static/js/interpreter.js"/>
	<script type="text/javascript">
	    document.title = 'Python Console on ${process_label} - WebConsole';
	</script>

	<script type="text/javascript">
	function insert_header()
	{
		interpreterManager.banner("${banner}");
	}

	addLoadEvent( insert_header );
	</script>

    <div id="main_content">
        <h1 class="console">${process_label}</h1>
        <form id="interpreter_form" action="" style="width:100%">
            <!-- PyConsole connection info -->
            <input type="hidden" value="${hostname}"
                    name="component_host" id="component_host"/>
            <input type="hidden" value="${port}"
                    name="component_port" id="component_port"/>

            <!-- Main console display -->
            <div id="interpreter_area">
                <div id="interpreter_output"></div>
            </div>
            <p />

        <div id="console_input">
            <div id="console_input_line">
            <!-- Single line input field -->
            <input id="interpreter_text" name="input_text"
                    type="text" class="console_textbox" title="Press Ctrl+Enter to execute" style="width:97%"/>
            </div>

            <!-- Multiline input field -->
            <div id="console_input_block" class="invisible">
            <textarea style="width:97%;height:170px"
                    name="interpreter_block_text"
                    id="interpreter_block_text"
                    class="console_textbox"
                    title="Press Ctrl+Enter to execute"></textarea>
            </div>

            <!-- Input style selection and execution elements -->
            <p/>
            <input type="button" name="exec" id="exec" value="Execute" />
            <input onClick="console_input_toggle();" type="checkbox"
                name="isMultiline" id="isMultiline">Multiline input field</input>
        </div>
        </form>
    </div>

    <script type="text/javascript">
        addLoadEvent( function(){ $("interpreter_form").input_text.focus() } );
    </script>

</div>

</html>

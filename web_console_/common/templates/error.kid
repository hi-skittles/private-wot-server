<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<html xmlns="http://www.w3.org/1999/xhtml"
	  xmlns:py="http://purl.org/kid/ns#"
	  py:layout="'../../common/templates/layout_css.kid'"
	  py:extends="'../../common/templates/common.kid'">

<div py:def="moduleContent()">
    <script py:if="traceback" src="${tg.tg_js}/MochiKit.js" ></script>
    <script py:if="traceback" type="text/javascript" src="/static/js/util.js"></script>
	<h1>${error}</h1>
	<h3 py:if="traceback">${timestamp}</h3>
	<code id="exceptionName">${message}</code>
	<br/><br/>
	<div py:if="traceback" id="notrace">
		<a class="user-feedback-button button" href='Javascript:BW.user.showFeedbackDialog("${timestamp}")'>Report exception</a>
		<a href="#" class="button" onClick="Util.toggleVisibility('notrace','stacktrace');">View stack trace</a>
	</div>

	<div py:if="traceback" id="stacktrace" class="hidden" style="display: none">
		<a class="user-feedback-button button" href='Javascript:BW.user.showFeedbackDialog("${timestamp}")'>Report exception</a>
		<a href="#" class="button" onClick="Util.toggleVisibility('notrace','stacktrace');">Hide stack trace</a>
		<font size="-1">
			<pre>${traceback}</pre>
		</font>
	</div>
	<script>
		jQuery( document ).ready( function () 
		{
			// Ensure all feedback links will use exception data if they're
			// clicked while on this page.
			jQuery( '.user-feedback-button' ).attr( 'href', "Javascript:BW.user.showFeedbackDialog( \"${timestamp}\" )" );
		});
	</script>
</div>
</html>

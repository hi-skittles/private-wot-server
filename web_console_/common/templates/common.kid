<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<?python import sitetemplate ?>
<html xmlns="http://www.w3.org/1999/xhtml"
	  xmlns:py="http://purl.org/kid/ns#"
	  py:extends="sitetemplate">

<head>
	<title> Library Functions </title>
	<!--
        useful kid template reference:
        http://werc.engr.uaf.edu/~ken/doc/python-kid/html/language.html
	-->
</head>

<body>

	<!--
		Hidden form element for passing current page and params for doing
		redirects later on.
	-->
	<div py:def="hiddenRedirect()">
		<?python
		  import cherrypy
		?>
		<input type="hidden" name="redirectTo"
			   value="${tg.url( cherrypy.request.path, **cherrypy.request.params )}"/>
	</div>

	<!--
		Insert a header row into a table
	-->
	<table>
		<tr py:def="tableHeader( text )">
			<th colspan="100" class="heading">${text}</th>
		</tr>
	</table>

	<!--
		Insert column headers into a table
	-->
	<table>
		<tr py:def="colHeaders( hdrs )" class="sortrow">
			<td py:for="h in hdrs" py:content="h" class="colheader"/>
		</tr>
	</table>


	<!--
		A GMail-style actions menu with support for option groups.  Please see
		actionMenuAppend() and clearChildren() in dom.js for ways of
		dynamically modifying these menus at runtime.

		You must pass an instance of web_console.common.util.ActionMenuOptions
		as the first argument to this template.  Please see that module for more
		info about constructing the option list.
	-->
	<form action=""><p>

		<select py:def="actionsMenu( options, rowID='', help = '' )"
				title='${help}'
				style="width: 100%"
				onchange="var o = this.options[this.selectedIndex];
				          if ( o.onclick != null ) { o.onclick(); return true; }
				          performAction( '${rowID}', this );">

			<div py:for="g in options.groupOrder" py:strip="True">

				<option py:if="g == options.groupOrder[0]"
						style="color: #666">
					${g.name}
				</option>

				<option py:if="g != options.groupOrder[0]"
						style="color: #666" disabled="disabled">
					${g.name}
				</option>

				<optgroup label="" id="${g.id}">

					<option py:for="label, script, help in g.options"
							title="${help}">

						<script type="text/javascript">
								addAction( "${rowID}", "${label}", "${script}" );
						</script>

						${label}
					</option>

				</optgroup>

			</div>

		</select>

	</p></form>

<table py:def="staticColourPickerPalette()" id="colourpicker">
<tbody><tr>
<td style="background-color: rgb(255, 255, 255); "></td>
<td style="background-color: rgb(255, 204, 204); "></td>
<td style="background-color: rgb(255, 204, 153); "></td>
<td style="background-color: rgb(255, 255, 153); "></td>
<td style="background-color: rgb(255, 255, 204); "></td>
<td style="background-color: rgb(153, 255, 153); "></td>
<td style="background-color: rgb(153, 255, 255); "></td>
<td style="background-color: rgb(204, 255, 255); "></td>
<td style="background-color: rgb(204, 204, 255); "></td>
<td style="background-color: rgb(255, 204, 255); "></td>
</tr>
<tr>
<td style="background-color: rgb(204, 204, 204); "></td>
<td style="background-color: rgb(255, 102, 102); "></td>
<td style="background-color: rgb(255, 153, 102); "></td>
<td style="background-color: rgb(255, 255, 102); "></td>
<td style="background-color: rgb(255, 255, 51); "></td>
<td style="background-color: rgb(102, 255, 153); "></td>
<td style="background-color: rgb(51, 255, 255); "></td>
<td style="background-color: rgb(102, 255, 255); "></td>
<td style="background-color: rgb(153, 153, 255); "></td>
<td style="background-color: rgb(255, 153, 255); "></td>
</tr>
<tr>
<td style="background-color: rgb(192, 192, 192); "></td>
<td style="background-color: rgb(255, 0, 0); "></td>
<td style="background-color: rgb(255, 153, 0); "></td>
<td style="background-color: rgb(255, 204, 102); "></td>
<td style="background-color: rgb(255, 255, 0); "></td>
<td style="background-color: rgb(51, 255, 51); "></td>
<td style="background-color: rgb(102, 204, 204); "></td>
<td style="background-color: rgb(51, 204, 255); "></td>
<td style="background-color: rgb(102, 102, 204); "></td>
<td style="background-color: rgb(204, 102, 204); "></td>
</tr>
<tr>
<td style="background-color: rgb(153, 153, 153); "></td>
<td style="background-color: rgb(204, 0, 0); "></td>
<td style="background-color: rgb(255, 102, 0); "></td>
<td style="background-color: rgb(255, 204, 51); "></td>
<td style="background-color: rgb(255, 204, 0); "></td>
<td style="background-color: rgb(51, 204, 0); "></td>
<td style="background-color: rgb(0, 204, 204); "></td>
<td style="background-color: rgb(51, 102, 255); "></td>
<td style="background-color: rgb(102, 51, 255); "></td>
<td style="background-color: rgb(204, 51, 204); "></td>
</tr>
<tr>
<td style="background-color: rgb(102, 102, 102); "></td>
<td style="background-color: rgb(153, 0, 0); "></td>
<td style="background-color: rgb(204, 102, 0); "></td>
<td style="background-color: rgb(204, 153, 51); "></td>
<td style="background-color: rgb(153, 153, 0); "></td>
<td style="background-color: rgb(0, 153, 0); "></td>
<td style="background-color: rgb(51, 153, 153); "></td>
<td style="background-color: rgb(51, 51, 255); "></td>
<td style="background-color: rgb(102, 0, 204); "></td>
<td style="background-color: rgb(153, 51, 153); "></td>
</tr>
<tr>
<td style="background-color: rgb(51, 51, 51); "></td>
<td style="background-color: rgb(102, 0, 0); "></td>
<td style="background-color: rgb(153, 51, 0); "></td>
<td style="background-color: rgb(153, 102, 51); "></td>
<td style="background-color: rgb(102, 102, 0); "></td>
<td style="background-color: rgb(0, 102, 0); "></td>
<td style="background-color: rgb(51, 102, 102); "></td>
<td style="background-color: rgb(0, 0, 153); "></td>
<td style="background-color: rgb(51, 51, 153); "></td>
<td style="background-color: rgb(102, 51, 102); "></td>
</tr>
<tr>
<td style="background-color: rgb(0, 0, 0); "></td>
<td style="background-color: rgb(51, 0, 0); "></td>
<td style="background-color: rgb(102, 51, 0); "></td>
<td style="background-color: rgb(102, 51, 51); "></td>
<td style="background-color: rgb(51, 51, 0); "></td>
<td style="background-color: rgb(0, 51, 0); "></td>
<td style="background-color: rgb(0, 51, 51); "></td>
<td style="background-color: rgb(0, 0, 102); "></td>
<td style="background-color: rgb(51, 0, 153); "></td>
<td style="background-color: rgb(51, 0, 51); "></td></tr></tbody>
</table>

</body>
</html>

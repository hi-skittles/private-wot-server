<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<?python
	import time
	layout_params['moduleHeader'] = "StatGrapher"
?>

<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
	  py:layout="'../../common/templates/layout_css.kid'"
	  py:extends="'../../common/templates/common.kid'">

<body py:def="moduleContent()" py:strip="True" class="content">

	<script type="text/javascript" src="/static/js/table.js"/>
	<script type="text/javascript">
		document.title = 'StatLogger Users - Web Console';
		jQuery( document ).ready( function() { Table.init(); } );
	</script>

	<div class="bordered table-container">
        <h2 class="heading">Users available in ${log}</h2>
        <table class="sortable">
            <thead>
                <tr class="sortrow">
                    <th>User name</th>
                    <th>User ID</th>
                </tr>
            </thead>
            <tbody>
                <tr py:for="row in outputList">
                    <td><a href="../../${action}/${log}/${row[0]}">${row[1]}</a></td>
                    <td>${row[0]}</td>
                </tr>
            </tbody>
        </table>
	</div>

	</body>
</html>

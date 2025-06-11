<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<?python
  layout_params[ "pageHeader" ] = "Watcher Collection"
  layout_params[ "page_specific_css"] = [ '../static/css/watchers.css' ]
?>

<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
	  py:layout="'../../common/templates/layout_css.kid'"
	  py:extends="'../../common/templates/common.kid'">

<body>

<!-- Document body -->
<div py:def="moduleContent()" class="content">

	<script type="text/javascript" src="/static/js/ajax.js"/>
	<script type="text/javascript" src="/static/js/util.js"/>
	<script type="text/javascript" src="../static/js/collections.js"/>
	<script type="text/javascript">
		document.title = 'Watcher Collection "${name}" - WebConsole';
	</script>

	<style>
	.table-container {
	    float: left;
	    clear: both;
	    margin-bottom: 1em;
	}

	.content > h2 {
	    margin-bottom: 1em;
	}
	</style>

	<h2>Watcher Collection: ${name}</h2>

	<div py:for="comp in results" class="bordered table-container">
        <h2 class="heading">${comp}</h2>
        <table>
            <thead>
                <tr>
                    <th style="background-color: #DDD"></th>
                    <th py:for="watcher in results[ comp ][0]">
                        ${"/".join( watcher.split('/')[-2:] )}
                        <a href="#" onClick="deleteFromCollection('${name}','${comp}','${watcher}');"
                           title="Delete watcher '${watcher}' from this collection">
                            [x]
                        </a>
                    </th>
                </tr>
            </thead>
            <tbody>
                <tr py:for="proc in results[ comp ][1]">
                    <th align="right">${proc}</th>
                    <td py:for="value in results[ comp ][1][ proc ]" align="left">${value}</td>
                </tr>
            </tbody>
        </table>
	</div>

</div>
</body>
</html>

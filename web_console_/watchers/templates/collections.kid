<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<?python
  layout_params[ "pageHeader" ] = "Watcher Collections"
?>

<html xmlns="http://www.w3.org/1999/xhtml"
	  xmlns:py="http://purl.org/kid/ns#"
      py:layout="'../../common/templates/layout_css.kid'"
      py:extends="'../../common/templates/common.kid'">

<body>
<div py:def="moduleContent()" class="content">

	<script type="text/javascript">
		document.title = 'Watcher Collections - WebConsole';
	</script>

	<script type="text/javascript" src="/static/js/action_table.js"/>
	<script type="text/javascript" src="/static/js/ajax.js"/>

	<div class="bordered table-container" py:if="collections">
        <h2 class="heading">Watcher Collections</h2>
        <table>
            <thead>
                <tr>
                    <th>Collection Name</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                <tr py:for="(collection, menu, count) in collections">
                    <td>
                    <div py:if="count!=0">
                    <a href="${tg.url( 'view', name=collection.pageName )}">
                        ${collection.pageName}
                    </a>
                    </div>
                    <div py:if="count==0"> ${collection.pageName} </div>
                    </td>
                    <td align="center">
                            <select py:replace="actionsMenu( menu, rowID=collection.pageName )"/>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>

	<div py:if="not collections">
		No watcher collections defined!
	</div>

	<script type="text/javascript" src="../static/js/collections.js"/>
	<p>
		<a href="#" onclick="createCollection()">
			New watcher collection
		</a>
	</p>

</div>
</body>
</html>

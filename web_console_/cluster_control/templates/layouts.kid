
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<?python
	from pycommon import cluster

  layout_params[ "pageHeader" ] = "Layouts"
  layout_params[ "page_specific_css"] = [ "/static/third_party/jquery-plugin-dataTables/css/jquery.dataTables.css"
                                        , "/static/third_party/jquery-plugin-dataTables-colReorder/css/ColReorder.css"
                                        , "/static/css/dynamic_table.css"
                                        ]
?>

<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
	py:layout="'../../common/templates/layout_css.kid'"
	py:extends="'../../common/templates/common.kid'">

<div py:def="moduleContent()">
    <script src="/static/third_party/jquery-plugin-dataTables/js/jquery.dataTables.js"></script>
    <script src="/static/third_party/jquery-plugin-dataTables-colReorder/js/ColReorderWithResize.js"></script>
    <script src="/static/js/dynamic_table.js"></script>

	<div py:if="layouts" id="layouts">
		<table>
		<thead>
			<tr>
				<th> Name </th>
				<th> Server User </th>
				<th py:for="pname in pnames">
					${cluster.Process.getPlural( pname )}
				</th>
				<th>Actions</th>
			</tr>
		</thead>
		<tbody>
			<tr py:for="i in xrange( len( layouts ) )">
				<td py:content="recs[i].name" />
				<td py:content="recs[i].serveruser"/>
				<td py:for="pname in pnames" py:content="layouts[i][ pname ]" class="numeric"/>
				<td>
					<a href="${tg.url( 'deleteLayout', name = recs[i].name )}">delete</a>
				</td>
			</tr>
		</tbody>
		</table>

		<script type="text/javascript">
		//<![CDATA[

		var layoutTable;
		jQuery( document ).ready( function()
		{
			this.title = 'Saved Layouts - WebConsole';

			layoutTable = new DynamicTable( '#layouts table', {
				title: 'Saved Layouts',
			});
		});

		jQuery( document ).one( 'keypress', function() {
			layoutTable.dom.container.find( 'input[type="text"]' ).focus();
		});
		// ]]>
		</script>
	</div>

	<div py:if="not layouts">
	No saved layouts!
	</div>

</div>

</html>

<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<?python
  layout_params[ "pageHeader" ] = "Machine Info"
?>

<html xmlns="http://www.w3.org/1999/xhtml"
	  xmlns:py="http://purl.org/kid/ns#"
      py:layout="'../../common/templates/layout_css.kid'"
      py:extends="'../../common/templates/common.kid'">

<div py:def="moduleContent()">

	<?python
	  import time
	?>

	<script type="text/javascript">
		document.title = 'Coredumps - WebConsole';
	</script>

	<div class="bordered table-container">
        <h2 class="heading">${ 'Coredumps for %s' % user.name }</h2>
        <table class="sortable">
            <thead>
                <tr>
                    <th>Filename</th>
                    <th>Time</th>
                    <th>Assertion</th>
                </tr>
            </thead>
            <tbody>
            <tr py:if="coredumps" py:for="fname, assrt, t in coredumps">

                <td valign="top">
                    <pre class="thinpre" py:content="fname"/>
                </td>

                <td valign="top">
                    <pre class="thinpre" py:content="time.ctime( t )"/>
                </td>

                <td valign="top">
                    <pre class="thinpre" py:content="assrt or '(none)'"/>
                </td>
            </tr>
            <tr py:if="not coredumps">
                <td colspan="3"><em>No coredumps to display</em></td>
            </tr>
            </tbody>
        </table>
	</div>
</div>

</html>

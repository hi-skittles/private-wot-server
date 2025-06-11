<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<?python
  layout_params[ "pageHeader" ] = "Watchers"
?>

<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
	  py:layout="'../../common/templates/layout_css.kid'"
	  py:extends="'../../common/templates/common.kid'">

<div py:def="moduleContent()" class="content">

	<script type="text/javascript">
		document.title = 'Edit Watchers - WebConsole';
	</script>

	<?python
	  pathSplit = watcherData.path.split( "/" )
	?>

	<form action="/watchers/tree/edit" method="get">
	<div class="bordered table-container">
        <h2 class="heading">Watcher Values for
            <span py:if="not watcherData.path" py:content="process.label()" py:strip="True"/>
            <span py:if="watcherData.path" py:strip="True">
                <a href="${tg.url( '/watchers/tree/show', dict(
                            machine=machine.name,
                            pid = process.pid, path = '' ))}">${process.label()}</a>
                <span py:for="i in xrange( len( pathSplit ) - 1 )" py:strip="True">/
                    <a href="${tg.url( '/watchers/tree/show', dict(
                            machine = machine.name,pid = process.pid,
                             path='/'.join( pathSplit[:i+1] ) ))}">${pathSplit[i]}</a>
                </span>
                / ${pathSplit[-1]}
            </span>
        </h2>

        <table>
            <tr><th class="heading" colspan="2">${watcherData.name}</th></tr>
            <tr>
                <td class="colheader">Existing Value</td>
                <td>
                    <div py:if="propagate == False">${watcherData.value}</div>
                    <div py:if="propagate == True">
                        <table width="100%" height="100%">
                            <tr py:for="(proc, value) in values" class="watcherrow">
                                <td>${proc}</td>
                                <td>${value}</td>
                            </tr>
                        </table>
                    </div>
                </td>
            </tr>
            <tr>
                <td class="colheader">New Value</td>
                <td>
                    <input type="hidden" name="machine" value="${machine.name}"/>
                    <input type="hidden" name="pid" value="${process.pid}"/>
                    <input type="hidden" name="path" value="${watcherData.path}"/>
                    <input type="hidden" name="dataType" value="${watcherData.type}"/>
                    <input py:if="propagate" type="hidden" name="propagate" value="True"/>
                    <!-- If it's a boolean, show a dropdown selection -->
                    <div py:if="watcherData.type == 4">
                        <select name="newval">
                            <option value="true">True</option>
                            <option value="false">False</option>
                        </select>
                    </div>
                    <div py:if="watcherData.type != 4">
                        <input name="newval" value="${watcherData.value}" type="text"/>
                    </div>
                </td>
            </tr>
            <tr>
                <td colspan="2" style="text-align:right;">
                    <input type="submit" value="Modify"/>
                </td>
            </tr>
        </table>

    </div><!-- /table-container -->
    </form>

</div>

</html>

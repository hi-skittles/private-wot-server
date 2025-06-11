<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml"
	  xmlns:py="http://purl.org/kid/ns#"
	  py:layout="'../../common/templates/layout_css.kid'"
	  py:extends="'../../common/templates/common.kid'">

<div py:def="moduleContent()" class="content">

	<script type="text/javascript">
		window.title = 'WebConsole - Flush User Mappings';
	</script>

	<div>

		<p>
			The bwmachined processes cache a mapping from Username to User ID
			for all available users.  If a new Unix user is added, these
			caches may need updating.  After the flush operation, new UNIX
			users with ~/.bwmachined.conf can be used in the "Server User"
			field when creating a new Web Console account.
		</p>

		<p>
			The duration of the flush operation will depend on the number of
			bwmachined processes in the network.
		</p>


		Are you sure you want to flush user mappings of all bwmachined
		processes in the network?

		<form action="" method="post"><p>

			<input type="submit" value="Yes"/>
			<input type="hidden" name="confirmed" value="true"/>
			<input type="button" value = "No"
				   onclick="window.history.back()"/>

		</p></form>

	</div>

</div>

</html>

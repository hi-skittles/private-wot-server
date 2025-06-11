var BASE_PATH = "/watchers/collections/";

function createCollection()
{
	var params = {};
	params.name = window.prompt( "New watcher collection name:" );

	// Reload the page when we've successfully added the new watcher
	// page so that the list of watcher collection pages is updated.
	function onSuccess()
	{
		window.location = BASE_PATH + "list";
	}

	if (params.name)
	{
		Ajax.call( BASE_PATH + "createCollection", params, onSuccess );
	}
}



function addToCollection( collection, component, watcher )
{
	var params = new Object();
	params.collection = collection;
	params.component = component;
	params.watcher = watcher;


	// TODO: Might be worth adding an onSuccess() to this ajax call
	//       to refresh the page similar to createCollection()
	//       above. Would involve passing in the page that called
	//       us.

	Ajax.call( BASE_PATH + "addToCollection", params );
}


function deleteCollection( collection )
{
	var params = new Object();
	params.collection = collection;

	// Reload the page when we've successfully added the new watcher
	// page so that the list of collections is updated.
	function onSuccess( )
	{
		window.location = BASE_PATH + "list";
	}

	if (confirm( "About to delete watcher collection " + collection))
	{
		Ajax.call( BASE_PATH + "deleteCollection", params, onSuccess );
	}
}


function deleteFromCollection( collection, component, watcherPath )
{
	var params = new Object();
	params.collection = collection;
	params.component = component;
	params.watcherPath = watcherPath;

	// Remove the '#' put on by the onClick call so we reload the page
	var tmploc = new String( window.location );
	tmploc = tmploc.substring(0, tmploc.length)

	// Reload the page when we've successfully delete the watcher path
	// so that we are displaying an up to date list of items.
	function onSuccess( )
	{
		window.location = tmploc;
	}

	if (confirm("Delete watcher path " + watcherPath + "?"))
	{
		Ajax.call( BASE_PATH + "deleteFromCollection",
				params, onSuccess );
	}
}

// collections.js

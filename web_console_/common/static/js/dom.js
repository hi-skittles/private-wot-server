/* namespace */ var DOM =
{
	// Delete all child nodes of an element
	clearChildren: function( elt )
	{
		for (var i = elt.childNodes.length - 1; i >= 0; i--)
			elt.removeChild( elt.childNodes[i] );
	},

	// Returns a list of the selected elements in a multiple selection list
	getSelected: function( input )
	{
		var selected = new Array();
		for (var i in input.options)
			if (input.options[i].selected)
				selected.push( input.options[i].value );
		return selected;
	},

	// Select specific elements in a multiple selection list
	setSelected: function( input, selected )
	{
		for (var i=0; i < input.options.length; i++)
		{
			input.options[i].selected =
			selected.indexOf( input.options[i].value ) >= 0;
		}
	},

	// Append an option to an optiongroup created with actionsMenu() from
	// common.kid
	actionMenuAppend: function( optgroup, label, script )
	{
		var option = createDOM(
			"option",
			{"onclick": script + "; this.parentNode.parentNode.selectedIndex = 0"},
			label );
		optgroup.appendChild( option );
	}
};

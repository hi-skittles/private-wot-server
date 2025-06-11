/*
 *
 * Sortable Tables:
 * The top level <table> element needs a class="sortable" attribute defined.
 * For every row heading that should be clickable to sort, define an attribute
 * class="sortrow".
 *
 * Example:
 * <table class="sortable>
 *  <tr class="sortrow">
 *   <th>Birthday</th>
 *   <th>First Name</th>
 *   <th>Last Name</th>
 *  </tr>
 *
 *  <tr>
 *   <td>12/01/1967</td>
 *   <td>Peter</td>
 *   <td>Smith</td>
 *  </tr>
 * </table>
 */

/* namespace */ var Table =
{
	// Dictionary of table objects already mapped
	s_tables: {},

	// Images for hiders
	images: ["/static/images/arrow_up.png", "/static/images/arrow_down.png"],

	init: function()
	{
		// Make hideable-classed tables hideable
		var tables = document.getElementsByTagName( "table" );
		var patt = /hideable\.(\d+)\.(\d+)\.(\d+)\.(\d+)/;
		for (var i=0; i < tables.length; i++)
		{

			// Is the table hideable?
			var m = patt.exec( tables[i].getAttribute( "class" ) );
			if (m)
			{
				Table.makeHideable(
					tables[i], new Number( m[1] ), new Number( m[2] ),
					new Number( m[3] ),	new Number( m[4] ) );
			}

			// Is the table sortable?
	        if (((' '+tables[i].className+' ').indexOf("sortable") != -1)) {
				if (!tables[i].id)
					tables[i].id = "a" + Math.random();
	            Table.makeSortable( tables[i] );
	        }
		}
	},

	// Make a table hideable, by inserting a hider element in cell (hr, hc) and
	// making a metaobject for it tagged with head and tail.
	makeHideable: function( table, hr, hc, head, tail )
	{
		var metaObj = Table.get( table.id, {head: head, tail: tail} );
		if (metaObj.hideable)
			return;

		var oldText = table.rows[ hr ].cells[ hc ].innerHTML;
		var newText =
		'<div>' +
		'<span style="float: left">' + oldText + '</span>' +
		'<span style="float: right">' +
		'<a href="javascript:Table.get( \'' + table.id + '\' ).toggleHide()"/>' +
		'<img src="/static/images/arrow_up.png" class="hider">' +
		'</a>' +
		'</span>' +
		'</div>';

		table.rows[ hr ].cells[ hc ].innerHTML = newText;
		metaObj.hideable = true;

		// Set the hider field of the table
		var images = table.getElementsByTagName( "img" );
		var hider = null;
		for (var i=0; i < images.length; i++)
		{
			if (images[i].getAttribute( "class" ) == "hider")
			{
				hider = images[i];
				break;
			}
		}

		metaObj.setHider( hider );
	},



	makeSortable: function( table )
	{
		// Search for any rows tagged as sortrows and make all their
		// contents clickable to sort.
		for (var i=0; i<table.rows.length; i++)
		{
			row = table.rows[i];
			if (row.getAttribute( "class" ) == "sortrow")
			{
				// Make the contents of this row clickable links
				for (var j=0; j<row.cells.length; j++)
				{
					var cell = row.cells[j];
					var txt = Table.getInnerText(cell);
					cell.innerHTML = '<a href="#" class="sortheader" ' +
					'title="Click to sort by this column" ' +
					'onclick="Table.resortTable(this, '+j+', '+(i+1)+');return false;">' +
					txt+'<span class="sortarrow"></span></a>';
				}
			}
		}
	},


	getInnerText: function( el )
	{
		if (typeof el == "string") return el;
		if (typeof el == "undefined") { return el };
		if (el.innerText) return el.innerText;	//Not needed but it is faster
		var str = "";

		var cs = el.childNodes;
		var l = cs.length;
		for (var i = 0; i < l; i++) {
			switch (cs[i].nodeType) {
				case 1: //ELEMENT_NODE
					str += Table.getInnerText(cs[i]);
					break;
				case 3:	//TEXT_NODE
					str += cs[i].nodeValue;
					break;
			}
		}
		return str;
	},


	resortTable: function( lnk, clid, rowid )
	{
		// get the span
		var span;
		for (var ci=0;ci<lnk.childNodes.length;ci++) {
			if (lnk.childNodes[ci].tagName &&
				lnk.childNodes[ci].tagName.toLowerCase() == 'span')
			{
				span = lnk.childNodes[ci];
			}
		}
		var spantext = Table.getInnerText( span );
		var td = lnk.parentNode;
		var column = clid || td.cellIndex;
		var table = Table.getParent(td, 'TABLE');

		// Work out a type for the column
		if (table.rows.length <= 1)
		{
			return;
		}

		var itm = Table.getInnerText( table.rows[ rowid ].cells[ column ] );
		sortfn = Table.sortCaseinsensitive;
		if (itm.match(/^\d\d[\/-]\d\d[\/-]\d\d\d\d$/)) sortfn = Table.sortDate;
		if (itm.match(/^\d\d[\/-]\d\d[\/-]\d\d$/)) sortfn = Table.sortDate;
		if (itm.match(/^[£$]/)) sortfn = Table.sortCurrency;
		if (itm.match(/^[\d\.%]+$/)) sortfn = Table.sortNumeric;
		if (itm.match(/^\d+\.\d+\.\d+\.\d+$/)) sortfn = Table.sortIpaddress;
		SORT_COLUMN_INDEX = column;
		var newRows = new Array();
		for (j=rowid;j<table.rows.length;j++) { newRows.push( table.rows[j] ); }

		newRows.sort(sortfn);

		if (span.getAttribute("sortdir") == 'down')
		{
			ARROW = '&uarr;';
			newRows.reverse();
			span.setAttribute('sortdir','up');
		}
		else
		{
			ARROW = '&darr;';
			span.setAttribute('sortdir','down');
		}

		// We appendChild rows that already exist to the tbody, so it moves
		// them rather than creating new ones

		// dont do sortbottom rows
		for (i=0;i<newRows.length;i++)
		{
			if (!newRows[i].className || (newRows[i].className &&
				(newRows[i].className.indexOf('sortbottom') == -1)))
			{
				table.tBodies[0].appendChild(newRows[i]);
			}
		}

		// do sortbottom rows only
		for (i=0;i<newRows.length;i++)
		{
			if (newRows[i].className &&
				(newRows[i].className.indexOf('sortbottom') != -1))
			{
				table.tBodies[0].appendChild(newRows[i]);
			}
		}

		// Delete any other arrows there may be showing
		var allspans = document.getElementsByTagName("span");
		for (var ci=0;ci<allspans.length;ci++)
		{
			if (allspans[ci].className == 'sortarrow')
			{
				if (Table.getParent(allspans[ci],"table") == Table.getParent(lnk,"table"))
				{
					// in the same table as us?
	                allspans[ci].innerHTML = '';
				}
			}
		}

		span.innerHTML = ARROW;
	},


	getParent: function( el, pTagName )
	{
		if (el == null)
			return null;
		else if (el.nodeType == 1 &&
				el.tagName.toLowerCase() == pTagName.toLowerCase())
			// Gecko bug, supposed to be uppercase
			return el;
		else
			return Table.getParent(el.parentNode, pTagName);
	},


	sortDate: function(a,b)
	{
		// y2k notes: two digit years less than 50 are treated as 20XX,
		// greater than 50 are treated as 19XX
		aa = Table.getInnerText(a.cells[SORT_COLUMN_INDEX]);
		bb = Table.getInnerText(b.cells[SORT_COLUMN_INDEX]);
		if (aa.length == 10) {
			dt1 = aa.substr(6,4)+aa.substr(3,2)+aa.substr(0,2);
		} else {
			yr = aa.substr(6,2);
			if (parseInt(yr) < 50) { yr = '20'+yr; } else { yr = '19'+yr; }
			dt1 = yr+aa.substr(3,2)+aa.substr(0,2);
		}
		if (bb.length == 10) {
			dt2 = bb.substr(6,4)+bb.substr(3,2)+bb.substr(0,2);
		} else {
			yr = bb.substr(6,2);
			if (parseInt(yr) < 50) { yr = '20'+yr; } else { yr = '19'+yr; }
			dt2 = yr+bb.substr(3,2)+bb.substr(0,2);
		}
		if (dt1==dt2) return 0;
		if (dt1<dt2) return -1;
		return 1;
	},

	sortCurrency: function(a,b)
	{
		aa = Table.getInnerText(a.cells[SORT_COLUMN_INDEX]).replace(/[^0-9.]/g,'');
		bb = Table.getInnerText(b.cells[SORT_COLUMN_INDEX]).replace(/[^0-9.]/g,'');
		return parseFloat(aa) - parseFloat(bb);
	},

	sortNumeric: function(a,b)
	{
		aa = parseFloat(Table.getInnerText(a.cells[SORT_COLUMN_INDEX]));
		if (isNaN(aa)) aa = 0;
		bb = parseFloat(Table.getInnerText(b.cells[SORT_COLUMN_INDEX]));
		if (isNaN(bb)) bb = 0;
		return aa-bb;
	},

	sortCaseinsensitive: function(a,b)
	{
		aa = Table.getInnerText(a.cells[SORT_COLUMN_INDEX]).toLowerCase();
		bb = Table.getInnerText(b.cells[SORT_COLUMN_INDEX]).toLowerCase();
		if (aa==bb) return 0;
		if (aa<bb) return -1;
		return 1;
	},

	sortDefault: function(a,b) {
		aa = Table.getInnerText(a.cells[SORT_COLUMN_INDEX]);
		bb = Table.getInnerText(b.cells[SORT_COLUMN_INDEX]);
		if (aa==bb) return 0;
		if (aa<bb) return -1;
		return 1;
	},

	sortIpaddress: function(a,b) {
		aa = Table.getInnerText(a.cells[SORT_COLUMN_INDEX]).split( "." );
		bb = Table.getInnerText(b.cells[SORT_COLUMN_INDEX]).split( "." );

		for (var i=0; i < aa.length; i++)
		{
			aaa = parseInt( aa[i] );
			bbb = parseInt( bb[i] );
			if (aaa != bbb)
				return aaa - bbb;
		}

		return 0;
	},


	// Get a metaobject associated with a real HTML table.  Implemented as a
	// factory because we need to preserve additional fields in different
	// contexts.
	get: function( id, params )
	{
		if (Table.s_tables[ id ])
		{
			return Table.s_tables[ id ];
		}

		var elt = $(id);

		// Class definition
		var table =
		{
			// Fields
			elt: elt,
			hider: null,
			head: ((params) ? (params.head || 1) : 1),
			tail: ((params) ? (params.tail || 0) : 0),
			hidden: false,
			hideable: false,
			onResize: ((params) ? (params.onResize || null) : null),

			setHider: function( hider )
			{
				this.hider = hider;
			},

			setHidden: function( hidden )
			{
				if (this.hidden == hidden)
					return;
				else
					this.hidden = hidden;

				if (this.hider)
					this.hider.blur();

				if (this.hidden)
				{
					var dims = elementDimensions( this.elt );
					for (var i = this.head;
						 i < this.elt.rows.length - this.tail; i++)
					{
						this.elt.rows[i].style.display = "none";
					}
					this.elt.style.width = dims.w + "px";
				}
				else
				{
					for (var i=0; i < this.elt.rows.length; i++)
						this.elt.rows[i].style.display = "table-row";
					this.elt.style.width = "auto";
				}

				if (this.hider)
					this.hider.src = Table.images[ new Number( this.hidden ) ];

				if (this.onResize)
					this.onResize();
			},

			hide: function()
			{
				this.setHidden( true );
			},

			show: function()
			{
				this.setHidden( false );
			},

			toggleHide: function()
			{
				this.setHidden( !this.hidden );
			}
		};

		Table.s_tables[ id ] = table;
		return table;
	}
};

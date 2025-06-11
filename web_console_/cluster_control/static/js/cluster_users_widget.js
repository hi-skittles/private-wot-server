"use strict";


var ClusterUsersWidget = function( /*string or jquery*/ domTarget, /*Map*/ options )
{
	var opts = jQuery.extend( true, {}, ClusterUsersWidget.DEFAULTS, options );
	DynamicTable.call( this, domTarget, opts );
};


/* class ClusterUsersWidget extends DynamicTable */
ClusterUsersWidget.prototype = new DynamicTable;
ClusterUsersWidget.prototype.constructor = ClusterUsersWidget;


// Anything in hungarian notation is from Datatables;
// see http://www.datatables.net/ref for API reference.
ClusterUsersWidget.DEFAULTS =
{
	//debug: 1,
	title: 'Server Users',
	baseurl: '/cc/api/users',
	showInactive: true,

	sAjaxDataProp: 'users',
	aaSorting: [ [1, 'asc'], [0, 'asc'] ],

	aoColumns:
	[
		{
			sTitle: 'Username',
			mData: 'name',
			mRender: function( username, reason, user )
			{
				if (reason === 'sort' || reason === 'type')
					return username;

				return username;
			},
		},
		{
			bVisible: false,
			bSearchable: false, // do not apply filtering to contents of this column
			sTitle: 'Activity',
			mData: 'isActive',
			aDataSort: [ 1, 0 ],
			mRender: function( isActive, reason, user )
			{
				if (reason === 'sort' || reason === 'type')
					return user.procs.length > 0 ? 1 : 2;

				return isActive ? 'active' : 'inactive';
			},
		},
		{
			sTitle: 'UID',
			mData: 'uid',
		},
		{
			sTitle: 'Activity',
			bSearchable: false, // do not apply filtering to contents of this column
			mData: 'procs',
			sClass: 'activity',
			sDefaultContent: 'N/A',
			asSorting: [ 'desc', 'asc' ],
			mRender: function( procs, reason, user )
			{
				if (reason === 'sort' || reason === 'type')
					return procs.length;

				var numProcs = procs.length;
				if (!numProcs)
					return '';

				var count = {};
				for (var i in procs)
				{
					var m = procs[i].machine;
					count[ m.name ] = (count[ m.name ] || 0) + 1;
				}
				var numMachines = Object.keys( count ).length;

				// if (!numMachines || !numProcs)
				// 	return '';

				return numProcs +
					((numProcs === 1) ? ' process' : ' processes') +
					' on ' +
					numMachines +
					((numMachines === 1) ? ' machine' : ' machines');
			},
		},
		{
			bVisible: false,
			bSearchable: false, // do not apply filtering to contents of this column
			sTitle: 'BW root',
			mData: 'mfroot',
			sDefaultContent: 'N/A',
		},
	],

	sAjaxSource: 'dummy', // non-null value to make "sLoadingRecords" appear

	oLanguage: {
		sInfo: "Showing _START_ to _END_ of _TOTAL_ users",
		sInfoEmpty: "",
		sEmptyTable: "No users",
		sZeroRecords: "No matching users",
		sLoadingRecords: "Waiting for Server...",
	},

	fnCreatedRow: function( tableRow, columnData, rowIndex )
	{
		var rowId = columnData.username;
		var $tr = jQuery( tableRow );
		$tr.attr( 'row-id', rowId );
		if (columnData.isActive)
		{
			$tr.addClass( 'active-user' );
		}
		else
		{
			$tr.addClass( 'inactive-user' );
		}
	},
};

ClusterUsersWidget.prototype.getModelUpdateUrl = function()
{
	if (this.options.showInactive)
	{
		return this.options.baseurl + '?inactive=1';
	}
	else
	{
		return this.options.baseurl;
	}
};


/* cluster_users_widget.js */

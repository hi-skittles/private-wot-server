"use strict";


var ClusterMachinesWidget =
function( /*string or jquery*/ domTarget, /*Map*/ options )
{
	var opts = jQuery.extend( true, {}, 
		ClusterMachinesWidget.DEFAULTS, options );
	DynamicTable.call( this, domTarget, opts );

	jQuery( this ).one( 'updateModel.dt', function()
	{
		var machine_list = this.data[ this.options.sAjaxDataProp ];
		var machinedVersions = machine_list.map(
			function( m ) { return m.machinedVersion; } );

		var d = ClusterMachinesWidget.DEFAULTS;
		d.maxMachinedVersion = Math.max.apply( Math, machinedVersions );
		d.minMachinedVersion = Math.min.apply( Math, machinedVersions );

		if (d.maxMachinedVersion > d.minMachinedVersion)
		{
			new Alert.Warning(
				"Not all machines are running the same bwmachined versions",
				{ id: 'multiple-machined-versions' }
			);
		}
	});
};


/* class ClusterMachinesWidget extends DynamicTable */
ClusterMachinesWidget.prototype = new DynamicTable;
ClusterMachinesWidget.prototype.constructor = ClusterMachinesWidget;

// Store CPU load historical data for sparkline graph
ClusterMachinesWidget.HistoricalLoadData = {};

// Anything in hungarian notation is from Datatables;
// see http://www.datatables.net/ref for API reference.
ClusterMachinesWidget.DEFAULTS =
{
	//debug: 1,
	title: 'Active Machines',
	baseurl: '/cc/api/machines',
	pollInterval: 3500,

	// machine "tag" info; see controller and pycommon/machine.py
	tags: {},

	// the latest machined version (int); normally retrieved from live server
	maxMachinedVersion: 0,

	sAjaxDataProp: 'ms',
	aoColumns: /* column configuration */
	[
		{
			sTitle: 'Hostname',
			mData: 'name',
			sClass: 'hostname',
			mRender: function( hostname, reason, machine )
			{
				if (reason === 'sort' || reason === 'type')
					return hostname;

				var machine_name = '<a href="machine?machine=' +
					hostname + '">' + hostname + '</a>';

				var groups = ClusterMachinesWidget.DEFAULTS.tags.Groups;
				if (groups && groups[hostname])
				{
					for (var i in groups[hostname])
					{
						machine_name += '<div class="group">' +
							groups[hostname][i] + '</div>';
					}
				}

				return machine_name;
			},
		},
		{
			sTitle: 'IP',
			mData: 'ip',
			sClass: 'ip'
		},
		{
			sTitle: 'Platform',
			mData: 'platformInfo',
			sClass: 'platform'
		},
		{
			sTitle: 'CPUs',
			mData: 'loads.length',
			sClass: 'cpus',
			mRender: function( numCpus, reason, machine )
			{
				if (reason === 'sort' || reason === 'type')
				{
					return numCpus * machine.processor;
				}

				return numCpus + ' x '
					+ ( machine.processor / 1000 ).toFixed( 1 ) + ' GHz';
			},
		},
		{
			sTitle: 'CPU Load (Avg/Max/Min)',
			mData: 'loads',
			sClass: 'cpu-load',
			sDefaultContent: 'N/A',
			mRender: function( loads, reason, machine )
			{
				// if sorting or discovering col type, return average of loads
				if (reason === 'sort' || reason === 'type')
					return loads.reduce( function( a, b ) { return a + b; } )
						/ loads.length;

				// else if display return formatted html
				if (reason === 'display')
				{
					var calculateLoadCat = function( value )
					{
						return value > 75 ? 'high' : value > 50 ? 'med' : 'low';
					};

					var avgLoad = ( loads.reduce( function( a, b )
						{ return a + b; } ) / loads.length ) * 100;
					var minLoad = Math.min.apply( null, loads ) * 100;
					var maxLoad = Math.max.apply( null, loads ) * 100;
					
					var currentLoadData = 
						ClusterMachinesWidget.HistoricalLoadData[machine.name];
					
					if (currentLoadData == undefined) 
					{
						//initialise history data
						currentLoadData = 
						{
							minLoads: [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
							avgLoads: [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
							maxLoads: [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
						};
					}
					
					//out with the old, in with the new
					currentLoadData.minLoads.shift();
					currentLoadData.avgLoads.shift();
					currentLoadData.maxLoads.shift();
					currentLoadData.minLoads.push( minLoad.toFixed( 0 ) );
					currentLoadData.avgLoads.push( avgLoad.toFixed( 0 ) );
					currentLoadData.maxLoads.push( maxLoad.toFixed( 0 ) );
					
					ClusterMachinesWidget.HistoricalLoadData[machine.name] = 
						currentLoadData;
					
					var html = '<div class="avg ' + 
						calculateLoadCat( avgLoad.toFixed( 0 ) ) + '">' + 
						avgLoad.toFixed( 0 ) + '%</div>';
					
					html += '<div class="cpu-load-data"><div class="minmax">' 
						+ '<span class="max-arrow">&#x25b2;</span><span class="'
						+ calculateLoadCat( maxLoad.toFixed( 0 ) ) + '">'
						+ maxLoad.toFixed( 0 ) + '%</span><br/>' 
						+ '<span class="min-arrow">&#x25bc;</span><span class="'
						+ calculateLoadCat( minLoad.toFixed( 0 ) ) + '">' 
						+ minLoad.toFixed( 0 ) + '%</span></div></div>';

					html += '<span class="cpu-load-sparkline" ' 
						+ 'minValues="' + currentLoadData.minLoads + '" '
						+ 'avgValues="' + currentLoadData.avgLoads + '" ' 
						+ 'maxValues="' + currentLoadData.maxLoads + '">'
						+ '</span>';
					
					
					return html;
				}
			},
		},
		{
			sTitle: 'Mem',
			mData: 'mem',
			sClass: 'memory',
			sDefaultContent: 'N/A',
			mRender: function( mem, reason, machine )
			{
				if (reason === 'sort' || reason === 'type')
					return mem;

				mem *= 100;
				var memCat = mem > 75 ? 'high' : mem > 50 ? 'med' : 'low';
				return '<div class="mem ' + memCat + '">'
					+ mem.toFixed( 1 )
					+ '</div>'
				;
			},
		},
// display of network stats not used at the moment; may be added in near future?
/*
		{
			sTitle: 'Network (in)',
			mData: 'interfaces',
			sClass: 'network',
			mRender: function( net, reason, machine )
			{
				if (reason === 'sort' || reason === 'type')
				{
					return ( Object.keys( net )
						.map( function( k ) { return net[k].bitsIn; } )
						.reduce( function( bits1, bits2 ) 
							{ return bits1 + bits2 } )
					);
				}

				return ( Object.keys( net ).sort().map(
					function( k )
					{
						// if (!net[k].bitsIn) return '';

						return ( '<div class="net" if="' + k + '">'
							+ net[k].bitsIn
							+ '</div>'
						);
					}).join( '' )
				);
			},
		},
		{
			sTitle: 'Network (out)',
			mData: 'interfaces',
			sClass: 'network',
			mRender: function( net, reason, machine )
			{
				if (reason === 'sort' || reason === 'type')
				{
					return ( Object.keys( net )
						.map( function( k ) { return net[k].bitsOut; } )
						.reduce( function( bits1, bits2 ) 
							{ return bits1 + bits2 } )
					);
				}

				return ( Object.keys( net ).sort().map(
					function( k )
					{
						// if (!net[k].bitsOut) return '';

						return ( '<div class="net" if="' + k + '">'
							+ net[k].bitsOut
							+ '</div>'
						);
					}).join( '' )
				);
			},
		},
*/
		{
			sTitle: 'Processes',
			mData: 'processes.length',
			sClass: 'num-procs',
		},
		{
			sTitle: 'Machined Version',
			mData: 'machinedVersion',
			sClass: 'machined',
			mRender: function( machinedVersion, reason, machine )
			{
				if (reason === 'sort' || reason === 'type')
				{
					return machinedVersion;
				}

				var max = 
					ClusterMachinesWidget.DEFAULTS.maxMachinedVersion || 0;
				if (machinedVersion < max)
				{
					return '<span class="not-latest-version">' + 
						machinedVersion + '</span';
				}
				else
				{
					return '<span>' + machinedVersion + '</span';
				}
			},
		},
	],

	sAjaxSource: 'dummy', // non-null value to make "sLoadingRecords" appear

	oLanguage: {
		sInfo: "Showing _START_ to _END_ of _TOTAL_ machines",
		sInfoEmpty: "",
		sEmptyTable: "No machines",
		sZeroRecords: "No matching machines",
		sLoadingRecords: "Waiting for Server...",
	},
	
	fnCreatedRow: function( nRow, aData )
	{
		var calculateLoadCat = function( value )
		{
			return value > 75 ? 'high' : value > 50 ? 'med' : 'low';
		};

		// Add tooltip to CPU Loads cell
		var loadsPercent = [];
		var load;
		for (var i in aData.loads)
		{
			load = aData.loads[i] * 100;
			loadsPercent.push( '<span class="' + calculateLoadCat( load ) + '">'
				+ load.toFixed( 0 ) + '%</span>' );
		}

		// Disable table cell tooltip while mouse is over graph
		jQuery( '.cpu-load .cpu-load-sparkline', nRow ).hover(
			function( e ) { jQuery( '.cpu-load', nRow ).tooltip( 'disable' ); } 
		);
		jQuery( '.cpu-load .cpu-load-sparkline', nRow ).mouseout(
			function( e ) { jQuery( '.cpu-load', nRow ).tooltip( 'enable' ); } 
		);

		// Add components tooltip to cell in Processes column
		var count = {};
		var machinesTableOptions = ClusterMachinesWidget.DEFAULTS;

		if (machinesTableOptions.tags[ aData.name ])
		{
			var allowed_procs = 
				machinesTableOptions.tags[ aData.name ].Components;
			for (var i in allowed_procs)
			{
				count[ allowed_procs[i] ] = 0;
			}
		}

		for (var i in aData.processes)
		{
			if (count[ aData.processes[i] ] === undefined)
			{
				count[ aData.processes[i] ] = 0;
			}
			count[ aData.processes[i] ]++;
		}

		var procs = Object.keys( count ).sort();

		for (i in procs)
		{
			procs[i] = '<span class="proc" count="'
					+ count[ procs[i] ]
					+ '">'
					+ procs[i]
					+ '</span>';
		}
		
		// Add tooltips as normal
		jQuery( '.cpu-load', nRow ).tooltip(
		{
			content: function () { return '<b>Core Loads:</b><br/>'
				+ loadsPercent.join( '<br/>' ) },
			items: 'td, div, span',
			track: true,
			show: 0,
			hide: 0
		});
		
		jQuery( '.num-procs', nRow ).tooltip(
		{
			content: function () {
				// if no default components, show "( any )"
				if (procs.length == 0) {
					return '<b>Components:</b><br/>'
						+ '<span class="proc" count="0">( any )</span><br/>';
				}
				else {
					return '<b>Components:</b><br/>' + procs.join('<br/>');
				}
			},
			items: 'td, div, span',
			track: true,
			show: 0,
			hide: 0
		});
		
		// Workarounds for Chrome. If more than one tooltip is visible when the
		// mouse moves across the cell, remove the old one.
		jQuery( '.cpu-load', nRow ).on( 'mousemove', function() {
			if (jQuery( '.ui-tooltip' ).length > 1) {
				jQuery( '.ui-tooltip' ).first().remove();
			}
		});

		jQuery( '.num-procs', nRow ).on( 'mousemove', function() {
			if(jQuery( '.ui-tooltip' ).length > 1) {
				jQuery( '.ui-tooltip' ).first().remove();
			}
		});

		/* 	For showing what processes are running for each user.
			Not currently used but useful to have for later. */
		/*for (var user in aData.processesByUser) 
		{
			for (var n in aData.processesByUser[user])
			{
				var procName = aData.processesByUser[user][n];
				if(procList[user] == undefined) 
				{
					procList[user] = [];
				}
				if (procList[user].indexOf(procName) == -1)
				{
					procList[user].push(procName);
				}
				
				if(procCounts[user] == undefined) 
				{
					procCounts[user] = [];
				}
				if(procCounts[user][procName] == undefined)
				{
					procCounts[user][procName] = 0;
				}
				procCounts[user][procName]++;
			}
		}
		
		var tooltipHtml = '<b>Components:</b><br/>';

		if (jQuery.isEmptyObject( aData.processesByUser ))
		{
			tooltipHtml += 'none';
		}
		else 
		{
			for (user in procList)
			{
				tooltipHtml += user + ':<br/>&nbsp;&nbsp;';
				for (n in procList[user]) 
				{
					var procName = aData.processesByUser[user][n];
					if (procCounts[user][procName] != 1) 
					{
						procList[user][n] += ' (' 
							+ procCounts[user][procName] + ')';
					}
				}
				tooltipHtml += procList[user].join( '<br/>&nbsp;&nbsp;' ) 
					+ '<br/>';
			}
		}*/
	},

	fnDrawCallback: function()
	{
		// Draw sparklines in CPU Load column
		var commonOptions = 
		{ 
			height: '28px', 
			width: '150px', 
			tooltipSuffix: '%', 
			chartRangeMin: '0', 
			chartRangeMax: '100',
			tooltipClassname: 'ui-tooltip jqstooltip'
		};
		
		jQuery( '.cpu-load-sparkline' ).sparkline( 'html', jQuery.extend( { }, 
			commonOptions, 
			{ 
				type: 'bar',
				barWidth: '6px',
				tooltipPrefix: 'Max: ',
				tagValuesAttribute: 'maxValues',
				zeroAxis: false,
				barColor: 'rgba(150,20,20,0.3)'
			}
		));
		jQuery( '.cpu-load-sparkline' ).sparkline( 'html', jQuery.extend( { },
			commonOptions, 
			{ 
				type: 'bar',
				barWidth: '6px', 
				tooltipPrefix: 'Min: ', 
				tagValuesAttribute: 'minValues', 
				zeroAxis: false, 
				barColor: 'rgba(230,20,20,0.3)', 
				colorMap: {'0:50':'rgba(20,20,230,0.2)',
					'51:100':'rgba(230,20,20,0.2)'}, 
				composite: true
			}
		));
		jQuery( '.cpu-load-sparkline' ).sparkline( 'html', jQuery.extend( { },
			commonOptions, 
			{ 
				type: 'line',
				tagValuesAttribute: 'avgValues', 
				tooltipPrefix: 'Avg: ', 
				fillColor: '', 
				lineColor: 'black', 
				spotColor: '', 
				minSpotColor: '', 
				maxSpotColor: '', 
				composite: true
			}
		));
	}
};


/** Returns ajax update URL. */
ClusterMachinesWidget.prototype.getModelUpdateUrl = function()
{
	var hasLoadedTags =
		Object.keys( ClusterMachinesWidget.DEFAULTS.tags ).length > 0;
	if (hasLoadedTags)
	{
		return this.options.baseurl;
	}
	else
	{
		return this.options.baseurl + '?tags=1';
	}
};


/**
*	Update machine info.
*
*   Looking up machine "tag" info is expensive, so we assume here it's
*   done infrequently enough to be worth setting it in the  static config
*   singleton so it can be shared between instances and update ticks.
*/
ClusterMachinesWidget.prototype.updateModel = function( /*Object*/ data )
{
	// If present, extract machine tag info into machinesTableOptions.tags,
	// key = machine name, value = array of allowed process names
	var machine_list = data[ this.options.sAjaxDataProp ];
	var opts = ClusterMachinesWidget.DEFAULTS;

	for (var i in machine_list)
	{
		var machine = machine_list[i];
		if (!machine.tags || !machine.tags.Components)
		{
			// no tag info provided
			continue;
		}

        opts.tags[ machine.name ] = machine.tags;

        // components are mixed-case; everything else is lower-case
        var components = opts.tags[ machine.name ].Components || [];
        for (var j in components)
        {
            components[j] = components[j].toLowerCase();
        }
    }
	
	if(BrowserDetect.browser == "Firefox") 
	{
		// Destroy the tooltip in Firefox. The new one will appear immediately
		jQuery( 'td.cpu-load' ).tooltip( 'destroy' );
		jQuery( 'td.num-procs' ).tooltip( 'destroy' );
	}
	
	// For all browsers, remove all data and events from the cell. In Chrome 
	// this will make the tooltip stick, but the mousemove event listener
	// added in fnCreatedRow above will remove it as soon as the mouse moves.
	jQuery( 'td.cpu-load' ).removeData();
	jQuery( 'td.cpu-load' ).off();
	jQuery( 'td.num-procs' ).removeData();
	jQuery( 'td.num-procs' ).off();
	
	// Remove all events and data from sparklines. Prevents memory leak.
	jQuery( '.cpu-load *' ).off();
	jQuery( '.cpu-load *' ).each( function() { jQuery( this ).removeData(); });
	
	DynamicTable.prototype.updateModel.call( this, data );
};


/* cluster_machines_widget.js */

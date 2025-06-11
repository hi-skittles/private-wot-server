"use strict";

if (!window.jQuery) throw new Error( "jquery lib not loaded" );
if (!window.jQuery.fn.dataTable) throw new Error( "jquery-dataTable plugin lib not loaded" );
if (!window.DynamicTable) throw new Error( "DynamicTable lib not loaded" );



/**
*   Synopsis:
*
*		new SpacesWidget( '#your-spaces-list-div' );
*		new SpacesWidget( '#your-spaces-list-div', options );
*/
var SpacesWidget = function( /*string or jquery*/ domTarget, /*Map*/ options )
{
	var opts = jQuery.extend( {}, SpacesWidget.DEFAULTS, options );
	DynamicTable.call( this, domTarget, opts );
};


/* class SpacesWidget extends DynamicTable */
SpacesWidget.prototype = new DynamicTable;
SpacesWidget.prototype.constructor = SpacesWidget;


SpacesWidget._roundPercent = function( value )
{
	if (value >= 0)
	{
		return (Math.round( value * 1000 ) / 10 ) + '%';
	}
};


SpacesWidget.DEFAULTS = {

	title: 'Spaces',
	poll: 2500, // msecs
	baseurl: '/sv/api/spaces?',
	previewSpace: false,
	bServerSide: true,

	/* datatable opts */

	// json path to the data for rows returned by 'baseurl'
	sAjaxDataProp: 'spaceList',

	aoColumns: [
		{
			sTitle: 'ID',
			mData: 'id'
		},
		{
			sTitle: 'Name',
			mData: 'name',
			bSortable: false,
		},
		{
			sTitle: 'Cells',
			mData: 'numCells',
			sDefaultContent: '<abbr style="color: #aaa;" ' +
				'title="Not available in this version of BigWorld">N/A</abbr>',
			bSortable: false,
		},
		{
			sTitle: 'Avg Load',
			mData: 'loadAvg',
			mRender: SpacesWidget._roundPercent,
			sDefaultContent: '<abbr style="color: #aaa;" ' +
				'title="Not available in this version of BigWorld">N/A</abbr>',
			bSortable: false,
		},
		{
			sTitle: 'Min Load',
			mData: 'loadMin',
			mRender: SpacesWidget._roundPercent,
			sDefaultContent: '<abbr style="color: #aaa;" ' +
				'title="Not available in this version of BigWorld">N/A</abbr>',
			bSortable: false,
		},
		{
			sTitle: 'Max Load',
			mData: 'loadMax',
			mRender: SpacesWidget._roundPercent,
			sDefaultContent: '<abbr style="color: #aaa;" ' +
				'title="Not available in this version of BigWorld">N/A</abbr>',
			bSortable: false,
		},
		{
			sTitle: '',
			mData: 'id',
			bSortable: false,
			bSearchable: false,
			mRender: function( spaceId )
			{
				return '<a href="/sv/space?spaceId=' + spaceId + '">View</a>';
			},
		},
	],

	sAjaxSource: 'dummy', // non-null value to make "sLoadingRecords" appear

	oLanguage: {
		sInfo: "Showing _START_ to _END_ of _TOTAL_ spaces",
		sInfoEmpty: "",
		sEmptyTable: "No spaces loaded",
		sZeroRecords: "No matching spaces",
		sLoadingRecords: "Waiting for Server...",
	},
};


SpacesWidget.prototype._initEvents = function()
{
	// call superclass method
	DynamicTable.prototype._initEvents.call( this );

	if (this.options.previewSpace)
	{
		// show/hide a spaceviewer for each row in the spaces table on click
		this.spaceViewers = {};

		this.datatable.on( 'click', 'tbody tr', function( event )
		{
			var tr = event.currentTarget;
			var spaceId = jQuery( tr ).attr( 'row-id' );
			if (!spaceId) throw new Error( 'no row-id' );

			if (this.datatable.fnIsOpen( tr ))
			{
				this.hideSpaceviewer( tr );
			}
			else
			{
				this.showSpaceviewer( tr );
			}
		}
		.bind( this ));

		jQuery( window ).resize( function()
		{
			for (var spaceId in this.spaceViewers)
			{
				this.spaceViewers[ spaceId ].resizeWindow();
			}
		}
		.bind( this ));
	}
	else
	{
		this.datatable.on( 'click', 'tbody tr', function( event )
		{
			var tr = event.currentTarget;
			var spaceId = jQuery( tr ).attr( 'row-id' );
			if (!spaceId) throw new Error( 'no row-id' );

			this.disconnectModel();
			window.document.location = 'space?spaceId=' + spaceId;
		}
		.bind( this ));
	}
};


SpacesWidget.prototype.showSpaceviewer = function( tableRow )
{
	var spaceId = jQuery( tableRow ).attr( 'row-id' );
	if (!spaceId) throw new Error( 'no row-id' );

	console.log( "creating spaceviewer %s", spaceId );

	// copy the DOM for a detailed space info panel
	var detailedSpaceSection = jQuery( '#embedded-spaceviewer-template' ).clone();
	detailedSpaceSection.prop( 'id', 'sv-space-' + Date.now() );
	detailedSpaceSection.attr( 'space-id', spaceId );

	// create a info row below the clicked row & attach info panel;
	// creates a new <tr/> element and appends passed div
	var tr = this.datatable.fnOpen( tableRow, detailedSpaceSection, 'sv-space-detail' );

	var svs = new SV.SpaceViewSurface( spaceId, {
		div: detailedSpaceSection,
	});
	this.spaceViewers[ spaceId ] = svs;
	svs.dom.title = jQuery( 'h2', svs.dom.container.parent() );

	jQuery( svs ).one( 'updateModel.sv', function()
	{
		this.rescaleWindow();
		this.zoomToSpaceBounds( false );
	});


	jQuery( svs ).on( 'updateModel.sv', function()
	{
		var div = this.dom.container.parent().find( '.space-detail-info-pane' );
		var sb = this.getSpaceBounds();

		div.empty();
		div.append( '<h2>Space '
			      + this.spaceId
			      + ': '
			      + this.spaceName
			      + '</h2>'
			      + '<p>Space bounds: '
			      + sb.minX
			      + ', '
			      + sb.minY
			      + ' to '
			      + sb.maxX
			      + ', '
			      + sb.maxY
			      + '</p>'
		);
	});


	detailedSpaceSection.hide().fadeIn();
	svs.connectModel();
};


SpacesWidget.prototype.hideSpaceviewer = function( tableRow )
{
	var tr = jQuery( tableRow );
	var spaceId = tr.attr( 'row-id' );
	if (!spaceId) throw new Error( 'no row-id' );
	var spacesWidget = this;

	jQuery( '[space-id=' + spaceId + ']' ).fadeOut( function()
	{
		console.log( "disposing spaceviewer %s", spaceId );

		// dispose of SV instance
		var svs = spacesWidget.spaceViewers[ spaceId ];
		svs.disconnectModel();
		jQuery( svs ).remove();
		delete spacesWidget.spaceViewers[ spaceId ];

		// clean up DOM
		jQuery( this ).remove();
		spacesWidget.datatable.fnClose( tableRow );
	});
};


// spaces_widget.js

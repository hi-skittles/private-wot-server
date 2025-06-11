var CreateScript = {
	/*------------------------------------------
	 * Variables
	 *------------------------------------------*/
	 numArgs: 0,
	 argList: [],
	 argTypes: [],

	 argDiv: null,
	 addArgButton: null,
	 removeArgButton: null,



	/*------------------------------------------
	 * Functions
	 *------------------------------------------*/
	init: function()
	{
		this.argDiv = $("args");	
		this.addArgButton = $("addArg");
		this.removeArgButton = $("removeArg");

		this.constructArgList();

		MochiKit.Signal.connect( this.addArgButton, 'onclick', this, 
				this.addArg );
		MochiKit.Signal.connect( this.removeArgButton, 'onclick', this, 
				this.removeArg );
	},

	getNextID: function()
	{
		var id = this.numArgs;
		this.numArgs += 1;
		return id;
	},

	setArgList: function( argList )
	{
		this.argList = argList;
	},

	constructArgList: function()
	{
		if (this.argList == undefined)
		{
			return;
		}
		for (var i = 0; i < this.argList.length; i++)
		{
			var name = this.argList[i][0];
			var type = this.argList[i][1];
			this.addArg( null, name, type );
		}
	},

	addArg: function( evt, name, type )
	{
		var optMaker = function( dataType )
		{
			var attr = {value:dataType[1]};
			if (dataType[1] == type)
			{
				attr["selected"] = true;
			}
			return OPTION( attr, dataType[0] );
		}

		var id = this.getNextID();

		if (name == undefined)
		{
			name = "";
		}

		if (type == undefined)
		{
			type = "";
		}

		var div = DIV({id:"arg"+id},
			id + ": ",
			INPUT({type:"text", name:"args", value:name}), 
			SELECT({name:"argTypes"}, 
				MochiKit.Iter.imap( optMaker, ArgTypes.types ) )
		);
		MochiKit.DOM.appendChildNodes( this.argDiv, div );
		this.updateButtons();
	},

	removeArg: function( evt, id )
	{
		if (this.numArgs == 0)
		{
			return;
		}

		if (id == undefined)
		{
			id = this.numArgs - 1;
		}
		MochiKit.DOM.removeElement( "arg"+id );
		this.numArgs -= 1;
	},

	updateButtons: function()
	{
		if (this.numArgs == 0)
		{
			// disable removeArg button
			this.removeArgButton.disabled = true;
		}
		else
		{
			// enable addArg button
			this.removeArgButton.enabled = false;
		}
	},
};

MochiKit.DOM.addLoadEvent( MochiKit.Base.bind( CreateScript.init, CreateScript ) );

var ArgTypes = {
	/*------------------------------------------
	 * Variables
	 *------------------------------------------*/
	types: [ 
		["Int", 1],
		["Float", 3],
		["Bool", 4],
		["String", 5]
	],

	typeToLabel: {},
	labelToType: {},

	/*------------------------------------------
	 * Functions
	 *------------------------------------------*/
	init: function()
	{
		for (var i = 0; i < this.types.length; i++)
		{
			var label = this.types[i][0];
			var type = this.types[i][1];

			this.typeToLabel[type] = label;
			this.labelToType[label] = type;
		}
	},

	/**
	 * TODO: Implement this function so that it returns a DOM element node
	 * containing the appropriate input for the type. You'll need to modify
	 * this method to accept extra data needed, e.g. which argument item this
	 * is (the first, or second, third, etc.) so we can assign an appropriate
	 * ID to the HTML element. Not entirely sure how this'll work, good luck.
	 *
	 * @param type    The integer corresponding to the WatcherDataType enum 
	 *                type.
	 */
	generateInputField : function( type )
	{
		switch (this.typeToLabel( type ))
		{
			case "Int":
				logDebug( "Generating field for ", type );
			default:
				throw "Unknown type to generate field for...";
		};
	}
};

MochiKit.DOM.addLoadEvent( MochiKit.Base.bind( ArgTypes.init, ArgTypes ) );

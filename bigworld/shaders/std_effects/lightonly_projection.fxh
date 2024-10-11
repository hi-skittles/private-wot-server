#ifndef LIGHTONLY_PROJECTION_FXH
#define LIGHTONLY_PROJECTION_FXH

//--------------------------------------------------------------------------------------------------
float3 uTransform
<
	bool artistEditable = true;
	string UIName = "U Transform";
	string UIDesc = "The U-transform vector for the material";
	string UIWidget = "Spinner";
	float UIMax = 100;
	float UIMin = -100;
> = {1,0,0};

//--------------------------------------------------------------------------------------------------
float3 vTransform
<
	bool artistEditable = true;
	string UIName = "V Transform";
	string UIDesc = "The V-transform vector for the material";
	string UIWidget = "Spinner";
	float UIMax = 100;
	float UIMin = -100;
> = {0,1,0};

//--------------------------------------------------------------------------------------------------
BW_ARTIST_EDITABLE_ADDRESS_MODE(BW_WRAP)

// Project UVs for lightonly_projection shader, this must be included before 
// lightonly_2uv.fxh because it is used in the vs_main defined there.
//--------------------------------------------------------------------------------------------------#define CALCULATE_UVS( o, itc, worldPos, worldNormal )\
{\
	o.tc = itc;\
	float4 ut = float4(mul(world, uTransform).xyz, 2) * 0.25;\
	float4 vt = float4(mul(world, -vTransform).xyz, 2) * 0.25;\
	o.tc2.x = dot( ut, worldPos);\
	o.tc2.y = dot( vt, worldPos );\
}

DECLARE_OTHER_MAP( otherMap, otherSampler, "Other Map", "The other map for the material, which will be projected onto the model." )

#endif
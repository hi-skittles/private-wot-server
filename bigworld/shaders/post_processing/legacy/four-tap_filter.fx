#include "post_processing.fxh"

DECLARE_EDITABLE_TEXTURE( inputTexture, inputSampler, CLAMP, CLAMP, LINEAR, "Input texture/render target" )


float brightness
<
	bool artistEditable = true;
	float UIMin = 0;
	float UIMax = 2.0;
	int UIDigits = 2;
	string UIName = "Brightness";
	string UIDesc = "Brightness of the filter";
> = 1.0;


float4 ps_main( PS_INPUT v ) : COLOR
{
	float4 map0 = tex2D( inputSampler, v.tc0.xy );
	float4 map1 = tex2D( inputSampler, v.tc1.xy );
	float4 map2 = tex2D( inputSampler, v.tc2.xy );
	float4 map3 = tex2D( inputSampler, v.tc3.xy );

	float4 result0 = map1 * v.tc1.z * brightness;
	result0 = saturate( (v.tc0.z * brightness * map0) + result0 );

	float4 result1 = map3 * v.tc3.z * brightness;
	result1 = saturate( (v.tc2.z * brightness * map2) + result1 );

	float4 result = result0 + result1;	
	
	return result;
};

STANDARD_PP_TECHNIQUE( compile vs_2_0 vs_pp_default(), compile ps_2_0 ps_main() )

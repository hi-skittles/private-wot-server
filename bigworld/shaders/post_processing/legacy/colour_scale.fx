#include "post_processing.fxh"

DECLARE_EDITABLE_TEXTURE( inputTexture, inputSampler, CLAMP, CLAMP, LINEAR, "Input texture/render target" )

float blur <
	bool artistEditable = true;
	string UIDesc = "Blur amount";
> = 0.5;

float power
<
	float UIMin = 0;
	float UIMax = 32.0;
	int UIDigits = 1;
	bool artistEditable = true;
	string UIName = "Power";
	string UIDesc = "Mathematical Power of the filter";
> = 8.0;


float4 ps_main( PS_INPUT v ) : COLOR
{
	float4 map0 = tex2D( inputSampler, v.tc0.xy );
	float3 res = pow( map0.rgb, power );
	return float4( res, 1.0 - blur );
};


STANDARD_PP_TECHNIQUE( compile vs_2_0 vs_pp_default(), compile ps_2_0 ps_main() )

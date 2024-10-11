#include "post_processing.fxh"

DECLARE_EDITABLE_TEXTURE( inputTexture, inputSampler, CLAMP, CLAMP, LINEAR, "Input texture/render target" )
DECLARE_EDITABLE_TEXTURE( distortionTexture, distortionSampler, WRAP, WRAP, LINEAR, "Distortion normal map" )


float alpha
<
	bool artistEditable = true;
	float UIMin = 0;
	float UIMax = 1.0;
	int UIDigits = 2;
	string UIDesc = "Alpha value";
> = 1.0;


float scale
<
	bool artistEditable = true;
	float UIMin = 0;
	float UIMax = 1.0;
	int UIDigits = 2;
	string UIDesc = "Scale factor for the distortion texture";
> = 1.0;


float tile
<
	bool artistEditable = true;
	float UIMin = 1;
	float UIMax = 128.0;
	int UIDigits = 0;
	string UIDesc = "Tiling of the distortion texture";
> = 1.0;


float4 ps_main( PS_INPUT input ) : COLOR0
{
	float4 dist = tex2D( distortionSampler, input.tc1 * tile );
	dist.xy += float2( -0.5, -0.5 );
	float4 bb = tex2D( inputSampler, input.tc1 + dist * scale );
	bb.a = alpha;
	return bb;
}


STANDARD_PP_TECHNIQUE( compile vs_2_0 vs_pp_default(), compile ps_2_0 ps_main() )

#include "post_processing.fxh"

DECLARE_EDITABLE_TEXTURE( inputTexture, inputSampler, CLAMP, CLAMP, LINEAR, "Input texture/render target" )


float alpha
<
	bool artistEditable = true;
	float UIMin = 0;
	float UIMax = 1.0;
	int UIDigits = 2;
	string UIDesc = "Alpha value";
> = 1.0;


float4 ps_main( PS_INPUT input ) : COLOR0
{
	float4 bb = tex2D( inputSampler, input.tc2 );
	bb.rgb = luminance( bb.rgb );
	bb.a *= alpha;
	return bb;
}

STANDARD_PP_TECHNIQUE( compile vs_2_0 vs_pp_default(), compile ps_2_0 ps_main() )

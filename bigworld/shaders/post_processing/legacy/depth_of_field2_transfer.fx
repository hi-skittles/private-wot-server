#include "post_processing.fxh"

DECLARE_EDITABLE_TEXTURE( inputTexture, inputSampler, CLAMP, CLAMP, LINEAR, "Input texture/render target" )
DECLARE_EDITABLE_TEXTURE( depthBlurTexture, depthBlurSampler, CLAMP, CLAMP, LINEAR, "Depth blur texture (calculated by a Lens Simulation effect)" )


float factor
<
	bool artistEditable = true;
	float UIMin = 0;
	float UIMax = 100.0;
	int UIDigits = 1;
	string UIDesc = "Transfer amount factor";
> = 100.0;


float4 ps_main( PS_INPUT input ) : COLOR0
{
	float4 t1 = tex2D( inputSampler, input.tc1 );
	float4 db = tex2D( depthBlurSampler, input.tc1 );
	float4 blurredColour = t1 / t1.a;
	float blur = saturate(db.g * factor);
	blurredColour.a = blur;
	return blurredColour;
}

STANDARD_PP_TECHNIQUE( compile vs_2_0 vs_pp_default(), compile ps_2_0 ps_main() )

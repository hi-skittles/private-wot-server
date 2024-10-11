#include "post_processing.fxh"

DECLARE_EDITABLE_TEXTURE( inputTexture, inputSampler, CLAMP, CLAMP, LINEAR, "Input texture/render target" )

const float g_bloomThreshold
<
	bool artistEditable = true;
	float UIMin = 0.1;
	float UIMax = 1.0;
	int UIDigits = 2;
	string UIDesc = "ToDo:";
> = 0.6f;

//-------------------------------------------------------------------------------------------------
float4 ps_main(PS_INPUT input) : COLOR0
{
	float4 color = tex2D(inputSampler, input.tc0);

	//-- adjust it to keep only values brighter than the specified threshold.
	return saturate((color - g_bloomThreshold) / (1.0f - g_bloomThreshold)); 
}

STANDARD_PP_TECHNIQUE( compile vs_2_0 vs_pp_default(), compile ps_2_0 ps_main() )
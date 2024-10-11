#include "post_processing.fxh"

DECLARE_EDITABLE_TEXTURE( fullTexture, fullSampler, CLAMP, CLAMP, LINEAR, "The main scene color texture/render target" )

//-------------------------------------------------------------------------------------------------
float4 ps_main( PS_INPUT input ) : COLOR0
{
	return tex2D(fullSampler, input.tc0);
}

STANDARD_PP_TECHNIQUE( compile vs_2_0 vs_pp_default(), compile ps_2_0 ps_main() )

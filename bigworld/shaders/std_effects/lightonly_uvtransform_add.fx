#define ADDITIVE_EFFECT 1
#define UV_TRANSFORM_OTHER
#undef BW_DEFERRED_SHADING
#include "stdinclude.fxh"
BW_ARTIST_EDITABLE_ADDITIVE_BLEND

#include "unskinned_effect_include.fxh"

BW_ARTIST_EDITABLE_ADDRESS_MODE(BW_WRAP)
DECLARE_OTHER_MAP( otherMap, otherSampler, "Other Map", "The other map for the material, to which the uv transform will be applied." )

#include "lightonly_2uv.fxh"

//--------------------------------------------------------------------------------------------------
BW_COLOR_CHANNEL_TECHNIQUE("sorted", false, false)
{
	pass P0
	{		
		BW_BLENDING_ADD
		BW_CULL_DOUBLESIDED
		BW_FOG_ADD
		
		VertexShader = compile vs_2_0 vs_main_2_0();
		PixelShader  = compiled_ps_main_2_0[alphaTestEnable];
	}
}

#undef BW_DEFERRED_SHADING
#include "stdinclude.fxh"
BW_ARTIST_EDITABLE_ALPHA_BLEND

#include "skinned_effect_include.fxh"
#include "lightonly.fxh"

//--------------------------------------------------------------------------------------------------
BW_COLOR_CHANNEL_TECHNIQUE("sorted", false, true)
{
	pass P0
	{		
		BW_BLENDING_ALPHA
		BW_CULL_DOUBLESIDED
		BW_FOG
		
		VertexShader = compile vs_2_0 vs_main_2_0();
		PixelShader  = compiled_ps_main_2_0[alphaTestEnable];
	}
}

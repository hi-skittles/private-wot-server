#undef BW_DEFERRED_SHADING
#define ADDITIVE_EFFECT 1
#include "stdinclude.fxh"
BW_ARTIST_EDITABLE_ADDITIVE_BLEND

#include "unskinned_effect_include.fxh"
#include "lightonly.fxh"

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
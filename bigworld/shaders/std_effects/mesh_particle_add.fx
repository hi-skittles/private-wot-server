#undef BW_DEFERRED_SHADING
#define ADDITIVE_EFFECT 1
#include "stdinclude.fxh"
#include "mesh_particle_include.fxh"

BW_ARTIST_EDITABLE_ADDITIVE_BLEND

//--------------------------------------------------------------------------------------------------
BW_COLOR_CHANNEL_TECHNIQUE("sorted", false, true)
{
	pass P0
	{
		BW_BLENDING_ADD
		BW_FOG_ADD
		SRCBLEND = SRCALPHA;
		DESTBLEND = ONE;
		BW_CULL_DOUBLESIDED
		
		VertexShader = compile vs_2_0 vs_main_2_0();
		PixelShader  = compile ps_2_0 ps_main_2_0();
	}
}

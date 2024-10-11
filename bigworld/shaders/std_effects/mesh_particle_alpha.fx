#undef BW_DEFERRED_SHADING
#include "stdinclude.fxh"
#include "mesh_particle_include.fxh"

BW_ARTIST_EDITABLE_ALPHA_BLEND

//--------------------------------------------------------------------------------------------------
BW_COLOR_CHANNEL_TECHNIQUE("internalSorted", false, true)
{
	pass P0
	{
		BW_BLENDING_ALPHA
		BW_FOG		
		BW_CULL_DOUBLESIDED
		
		VertexShader = compile vs_2_0 vs_main_2_0();
		PixelShader  = compile ps_2_0 ps_main_2_0();
	}
}

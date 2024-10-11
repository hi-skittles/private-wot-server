#include "stdinclude.fxh"
#include "unskinned_effect_include.fxh"
#define BW_DEFERRED_SHADING_OLD BW_DEFERRED_SHADING
#define BW_DEFERRED_SHADING 0
#include "lightonly.fxh"
#define BW_DEFERRED_SHADING BW_DEFERRED_SHADING_OLD

//--------------------------------------------------------------------------------------------------
BW_COLOR_CHANNEL_TECHNIQUE("sorted", false, false)
{
	pass P0
	{		
		BW_BLENDING_SOLID
		BW_CULL_DOUBLESIDED
		BW_FOG
		
		VertexShader = compile vs_2_0 vs_main_2_0();
		PixelShader  = compiled_ps_main_2_0[alphaTestEnable];
	}
}

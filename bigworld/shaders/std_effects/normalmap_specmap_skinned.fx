#include "stdinclude.fxh"

#include "normalmap_specmap.fxh"
#include "skinned_effect_include.fxh"
#include "normalmap_2_0.fxh"

//--------------------------------------------------------------------------------------------------
#if BW_DEFERRED_SHADING

//--------------------------------------------------------------------------------------------------
BW_COLOR_TECHNIQUE(true, true)
{
	pass P0
	{		
		BW_BLENDING_SOLID
		BW_CULL_DOUBLESIDED
		
		VertexShader = compile vs_3_0 vs_deferred_3_0();
		PixelShader  = compiled_ps_deferred_3_0[alphaTestEnable];
	}
}

//--------------------------------------------------------------------------------------------------
BW_REFLECTION_TECHNIQUE(true, true)
{
	pass P0
	{		
		BW_BLENDING_SOLID
		BW_CULL_DOUBLESIDED
		
		VertexShader = compile vs_3_0 vs_reflection_3_0();
		PixelShader  = compiled_ps_reflection_3_0[alphaTestEnable];
	}
}

//--------------------------------------------------------------------------------------------------
BW_SHADOW_TECHNIQUE(true)
{
	pass P0
	{		
		BW_BLENDING_SOLID
		BW_SHADOW_CULL_MODE
		
		VertexShader = compile vs_3_0 vs_shadows_3_0();
		PixelShader  = compiled_ps_shadows_3_0[alphaTestEnable];
	}
}

#else //-- BW_DEFERRED_SHADING

//--------------------------------------------------------------------------------------------------
BW_COLOR_TECHNIQUE(true, true)
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

#endif //-- BW_DEFERRED_SHADING
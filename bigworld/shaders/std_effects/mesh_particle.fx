#include "stdinclude.fxh"
#include "mesh_particle_include.fxh"

//--------------------------------------------------------------------------------------------------
#if BW_DEFERRED_SHADING

//--------------------------------------------------------------------------------------------------
BW_COLOR_TECHNIQUE(false, true)
{
	pass P0
	{		
		BW_BLENDING_SOLID
		BW_CULL_DOUBLESIDED
		
		VertexShader = compile vs_3_0 vs_deferred_3_0();
		PixelShader  = compile ps_3_0 ps_deferred_3_0();
	}
}

//--------------------------------------------------------------------------------------------------
BW_REFLECTION_TECHNIQUE(false, true)
{
	pass P0
	{		
		BW_BLENDING_SOLID
		BW_CULL_DOUBLESIDED
		
		VertexShader = compile vs_3_0 vs_reflection_3_0();
		PixelShader  = compile ps_3_0 ps_reflection_3_0();
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
		PixelShader  = compile ps_3_0 ps_shadows_3_0();
	}
}

#else //-- BW_DEFERRED_SHADING

//--------------------------------------------------------------------------------------------------
BW_COLOR_TECHNIQUE(false, true)
{
	pass P0
	{
		BW_BLENDING_SOLID
		BW_CULL_DOUBLESIDED
		BW_FOG
		
		VertexShader = compile vs_2_0 vs_main_2_0();
		PixelShader  = compile ps_2_0 ps_main_2_0();
	}
}

#endif //-- BW_DEFERRED_SHADING
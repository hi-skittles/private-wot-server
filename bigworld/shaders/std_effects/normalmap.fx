#include "stdinclude.fxh"

#include "normalmap.fxh"
#include "unskinned_effect_include.fxh"
#include "normalmap_2_0.fxh"

//--------------------------------------------------------------------------------------------------
#if BW_DEFERRED_SHADING

//--------------------------------------------------------------------------------------------------
BW_COLOR_TECHNIQUE(true, false)
{
	pass P0
	{		
		BW_BLENDING_SOLID
		BW_CULL_DOUBLESIDED
		ALPHATESTENABLE = FALSE;
		
		VertexShader = compile vs_3_0 vs_deferred_3_0();
		PixelShader  = compiled_ps_deferred_3_0[alphaTestEnable];
	}
}

//--------------------------------------------------------------------------------------------------
BW_COLOR_INSTANCED_TECHNIQUE(true, false)
{
	pass P0
	{		
		BW_BLENDING_SOLID
		BW_CULL_DOUBLESIDED
		ALPHATESTENABLE = FALSE;
		
		VertexShader = compile vs_3_0 vs_instanced_deferred_3_0();
		PixelShader  = compiled_ps_deferred_3_0[alphaTestEnable];
	}
}

//--------------------------------------------------------------------------------------------------
BW_REFLECTION_TECHNIQUE(true, false)
{
	pass P0
	{		
		BW_BLENDING_SOLID
		BW_CULL_DOUBLESIDED
		ALPHATESTENABLE = FALSE;
		
		VertexShader = compile vs_3_0 vs_reflection_3_0();
		PixelShader  = compiled_ps_reflection_3_0[alphaTestEnable];
	}
}

//--------------------------------------------------------------------------------------------------
BW_REFLECTION_INSTANCED_TECHNIQUE(true, false)
{
	pass P0
	{
		BW_BLENDING_SOLID
		BW_CULL_DOUBLESIDED
		ALPHATESTENABLE = FALSE;
		
		VertexShader = compile vs_3_0 vs_instanced_reflection_3_0();
		PixelShader  = compiled_ps_reflection_3_0[alphaTestEnable];
	}
}

//--------------------------------------------------------------------------------------------------
BW_SHADOW_TECHNIQUE(false)
{
	pass P0
	{		
		BW_BLENDING_SOLID
		BW_SHADOW_CULL_MODE
		
		VertexShader = compile vs_3_0 vs_shadows_3_0();
		PixelShader  = compiled_ps_shadows_3_0[alphaTestEnable];
	}
}

//--------------------------------------------------------------------------------------------------
BW_SHADOW_INSTANCED_TECHNIQUE(false)
{
	pass P0
	{		
		BW_BLENDING_SOLID
		BW_SHADOW_CULL_MODE
		
		VertexShader = compile vs_3_0 vs_instanced_shadows_3_0();
		PixelShader  = compiled_ps_shadows_3_0[alphaTestEnable];
	}
}

//--------------------------------------------------------------------------------------------------

#else //-- BW_DEFERRED_SHADING

//--------------------------------------------------------------------------------------------------
BW_COLOR_TECHNIQUE(true, false)
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
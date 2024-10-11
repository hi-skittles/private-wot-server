#include "stdinclude.fxh"
#include "read_g_buffer.fxh"

// Шейдер для заполнения уменьшенного буффера глубины. 
// На данный момент является неоконченной экспериментальной реализацией и не работает в финальной технологии.

//--------------------------------------------------------------------------------------------------

BW_DS_LIGHT_PASS_VS2PS VS(BW_DS_LIGHT_PASS_VS i)
{
	BW_DS_LIGHT_PASS_VS2PS o = (BW_DS_LIGHT_PASS_VS2PS) 0;
	o.pos = i.pos;
	o.tc  = i.tc;
	return o;
}

//--------------------------------------------------------------------------------------------------

float4 PS(BW_DS_LIGHT_PASS_VS2PS i) : COLOR
{
	return g_buffer_readLinearZ(i.tc);
}

//--------------------------------------------------------------------------------------------------

technique DEFAULT
{
	pass Pass_0
	{
		ALPHATESTENABLE = FALSE;
		ZENABLE = FALSE;
		ZWRITEENABLE = FALSE;
		ALPHABLENDENABLE = FALSE;
		FOGENABLE = FALSE;
		POINTSPRITEENABLE = FALSE; // ???
		STENCILENABLE = FALSE;
		CULLMODE = CW;

		VertexShader = compile vs_3_0 VS();
		PixelShader  = compile ps_3_0 PS();
	}
};

//--------------------------------------------------------------------------------------------------
//-- End

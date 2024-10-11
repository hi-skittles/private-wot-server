#include "stdinclude.fxh"
#include "read_g_buffer.fxh"

// Реализация эффекта блюра специализированная для размазывания SSAO resolve-буфера.
// Работает в два прохода (VERTICAL и HORIZONTAL). Использует свойства сепарабельных фильтров.
// Записывает в пиксель среднее арифметическое всех его соседей находящихся в квадрате 4x4.
//
// Из-за того, что в квадрате 4x4 нет центрального пикселя, маска фильтра немного смещена:
//
// X X X X
// X O X X
// X X X X
// X X X X
//

//--------------------------------------------------------------------------------------------------

texture g_srcMap;
bool g_useStencilOptimization = true;

//--------------------------------------------------------------------------------------------------

sampler g_srcMapSampler = sampler_state
{		
	Texture = <g_srcMap>;
	MIPFILTER = POINT;
	MAGFILTER = POINT;
	MINFILTER = POINT;
	ADDRESSU = WRAP;
	ADDRESSV = WRAP;
};

//--------------------------------------------------------------------------------------------------

static const float offsets[4] = // in pixels
{
	- 1.f, 
	  0.f,
	  1.f,
	  2.f
};

//--------------------------------------------------------------------------------------------------

BW_DS_LIGHT_PASS_VS2PS VS(BW_DS_LIGHT_PASS_VS i)
{
	BW_DS_LIGHT_PASS_VS2PS o = (BW_DS_LIGHT_PASS_VS2PS) 0;
	o.pos = i.pos;
	o.tc  = i.tc;
	return o;
}

//--------------------------------------------------------------------------------------------------

float4 PS(BW_DS_LIGHT_PASS_VS2PS i, uniform bool isVertical) : COLOR
{
	float res = 0.f;
	[unroll]
	for(int index = 0; index < 4; ++index)
	{
		float2 vertOff = float2(0.f, offsets[index]);
		float2 horzOff = float2(offsets[index], 0.f);

		float2 off = isVertical ? vertOff : horzOff;

		res += tex2D(g_srcMapSampler, i.tc + g_invScreen.zw * off).x;
	}
	res /= 4.f;
	return res;
}

//--------------------------------------------------------------------------------------------------

technique VERTICAL_BLURE
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

		//-- use stencil to mark only valid g-buffer pixels (i.e. not sky and flora pixels)
		STENCILENABLE = <g_useStencilOptimization>;
		STENCILFUNC = NOTEQUAL;
		STENCILWRITEMASK = 0x00;
		STENCILMASK = G_STENCIL_USAGE_ALL_OPAQUE;
		STENCILREF = 0;

		VertexShader = compile vs_3_0 VS();
		PixelShader  = compile ps_3_0 PS(true);
	}
};

technique HORIZONTAL_BLURE
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

		//-- use stencil to mark only valid g-buffer pixels (i.e. not sky and flora pixels)
		STENCILENABLE = <g_useStencilOptimization>;
		STENCILFUNC = NOTEQUAL;
		STENCILWRITEMASK = 0x00;
		STENCILMASK = G_STENCIL_USAGE_ALL_OPAQUE;
		STENCILREF = 0;

		VertexShader = compile vs_3_0 VS();
		PixelShader  = compile ps_3_0 PS(false);
	}
};

//--------------------------------------------------------------------------------------------------
//-- End

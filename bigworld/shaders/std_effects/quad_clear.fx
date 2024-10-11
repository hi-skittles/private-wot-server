#include "stdinclude.fxh"

//--------------------------------------------------------------------------------------------------
struct VS_INPUT
{
	float4 pos : POSITION;
	float2 tc  : TEXCOORD;
};

//--------------------------------------------------------------------------------------------------
struct VS_OUTPUT
{
	float4 pos : POSITION;
	float2 tc  : TEXCOORD0;
};

//-- vertex shader.
//--------------------------------------------------------------------------------------------------
VS_OUTPUT VS( VS_INPUT i )
{
	VS_OUTPUT o = (VS_OUTPUT)0;
	o.pos = i.pos;
	o.tc  = i.tc;
	return o;
}

float4 g_color;

//-- pixel shader.
//--------------------------------------------------------------------------------------------------
float4 PS( VS_OUTPUT i ) : COLOR
{
	return g_color;
}

//--------------------------------------------------------------------------------------------------
technique clear_channel
{
	pass Pass_0
	{
		ALPHATESTENABLE  = FALSE;
		ALPHABLENDENABLE = FALSE;
		ZENABLE          = FALSE;
		ZWRITEENABLE     = FALSE;
		FOGENABLE        = FALSE;

		// POINTSPRITEENABLE = FALSE;
		// STENCILENABLE = FALSE;
		CULLMODE = CW;

		VertexShader = compile vs_2_0 VS();
		PixelShader  = compile ps_2_0 PS();
	}
}

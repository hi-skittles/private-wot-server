#include "stdinclude.fxh"

//--------------------------------------------------------------------------------------------------
texture g_srcMap;
float4  g_offsetMask;
float4  g_visibilityMask;

//--------------------------------------------------------------------------------------------------
sampler g_srcMapSampler = sampler_state
{
	Texture 		= (g_srcMap);
	ADDRESSU 		= CLAMP;
	ADDRESSV 		= CLAMP;
	ADDRESSW 		= CLAMP;
	MAGFILTER 		= LINEAR;
	MINFILTER 		= LINEAR;
	MIPFILTER 		= LINEAR;
	MAXMIPLEVEL 	= 0;
	MIPMAPLODBIAS 	= 0;
};

//--------------------------------------------------------------------------------------------------
struct VertexXYZUV
{
   float4 pos: 	POSITION;
   float2 tc:	TEXCOORD0;
};

//-------------------------------------------------------------------------------------------------
struct VertexOut
{
	float4 pos:	POSITION;
	float2 tc: 	TEXCOORD0;
};

//-------------------------------------------------------------------------------------------------
VertexOut VS(const VertexXYZUV i)
{
	VertexOut o = (VertexOut)0;
	o.pos = i.pos;
	o.tc  = i.tc;
	
	return o;
}

//--------------------------------------------------------------------------------------------------
float4 PS(const VertexOut i) : COLOR
{
	float4 src = tex2D(g_srcMapSampler, i.tc);

	float4 o = float4(0,0,0,0);
	for (int i = 0; i < 4; ++i)
	{
		o[i] = src[g_offsetMask[i]] * g_visibilityMask[i];
	}

	return o;
}

//-------------------------------------------------------------------------------------------------
technique TRANSFER
{
	pass Pass_0
	{
		ALPHABLENDENABLE = FALSE;
		ALPHATESTENABLE = FALSE;
		ZENABLE = FALSE;
		ZWRITEENABLE = FALSE;
		ZFUNC = ALWAYS;
		CULLMODE = NONE;
		FOGENABLE = FALSE;
		STENCILENABLE = FALSE;
		
		VertexShader = compile vs_2_0 VS();
		PixelShader  = compile ps_2_0 PS();
	}
}
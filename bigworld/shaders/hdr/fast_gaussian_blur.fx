#include "stdinclude.fxh"

//-- Notice: This shader implements gaussian blur with 5x5 kernel but uses only 5 sample instructions
//--		 instead of 9 because texture sampler has LINEAR filtration and we manually adjust
//--		 offsets and weight to reuse hardware accelerated filtration power.
//--		 Totally we need only 10 sample instruction to perform gaussian blur with 5x5 kernel.
//--		 Broadforce approach takes 9x9 = 81 sample instruction to do almost the same.

//-- params.
texture		 g_srcMap;
const float4 g_srcSize;

//-------------------------------------------------------------------------------------------------
sampler g_srcMapLinearSampler = sampler_state
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

//-------------------------------------------------------------------------------------------------
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
VertexOut VS(VertexXYZUV i)
{
	VertexOut o = (VertexOut)0;
	o.pos = i.pos;
	o.tc  = i.tc;
	
	return o;
}

//-------------------------------------------------------------------------------------------------
static const float3 g_offsets = float3(0.0, 1.3846153846, 3.2307692308);
static const float3 g_weights = float3(0.2270270270, 0.3162162162, 0.0702702703);

//-------------------------------------------------------------------------------------------------
float4 PS_horizontal_blur(const VertexOut i) : COLOR0
{
	half4 color = tex2D(g_srcMapLinearSampler, i.tc) * g_weights[0];

	[unroll]
	for (int j = 1; j < 3; ++j)
	{
		color += tex2D(g_srcMapLinearSampler, i.tc + float2(g_offsets[j], 0.0) * g_srcSize.z) * g_weights[j];
		color += tex2D(g_srcMapLinearSampler, i.tc - float2(g_offsets[j], 0.0) * g_srcSize.z) * g_weights[j];
	}

	return color;
}

//-------------------------------------------------------------------------------------------------
float4 PS_vertical_blur(const VertexOut i) : COLOR0
{
	half4 color = tex2D(g_srcMapLinearSampler, i.tc) * g_weights[0];

	[unroll]
	for (int j = 1; j < 3; ++j)
	{
		color += tex2D(g_srcMapLinearSampler, i.tc + float2(0.0, g_offsets[j]) * g_srcSize.w) * g_weights[j];
		color += tex2D(g_srcMapLinearSampler, i.tc - float2(0.0, g_offsets[j]) * g_srcSize.w) * g_weights[j];
	}

	return color;
}

//-------------------------------------------------------------------------------------------------
technique HORIZONTAL_PASS
{
	pass Pass_0
	{
		ALPHABLENDENABLE = FALSE;
		ALPHATESTENABLE = FALSE;
		ZENABLE = FALSE;
		ZWRITEENABLE = FALSE;
		FOGENABLE = FALSE;
		CULLMODE = CW;
		
		VertexShader = compile vs_2_0 VS();
		PixelShader  = compile ps_2_0 PS_horizontal_blur();
	}
}

//-------------------------------------------------------------------------------------------------
technique VERTICAL_PASS
{
	pass Pass_0
	{
		ALPHABLENDENABLE = FALSE;
		ALPHATESTENABLE = FALSE;
		ZENABLE = FALSE;
		ZWRITEENABLE = FALSE;
		FOGENABLE = FALSE;
		CULLMODE = CW;
		
		VertexShader = compile vs_2_0 VS();
		PixelShader  = compile ps_2_0 PS_vertical_blur();
	}
}
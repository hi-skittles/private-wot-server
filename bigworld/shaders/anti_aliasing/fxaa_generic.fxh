//-- include FXAA realization file.
#define FXAA_HLSL_3 1
#include "fxaa.fxh"

//-- params.
const float4  g_invScreen : InvScreen;
texture       g_bbCopyMap;

//-------------------------------------------------------------------------------------------------
sampler g_bbCopyMapSampler = sampler_state
{
	Texture 		= (g_bbCopyMap);
	ADDRESSU 		= CLAMP;
	ADDRESSV 		= CLAMP;
	ADDRESSW 		= CLAMP;
	MAGFILTER 		= LINEAR;
	MINFILTER 		= LINEAR;
	MIPFILTER 		= LINEAR;
	MAXANISOTROPY 	= 1;
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
float4 PS(VertexOut i) : COLOR0
{
	float  alpha = tex2D(g_bbCopyMapSampler, i.tc).a;
	float3 rgb   = FxaaPixelShader(i.tc, g_bbCopyMapSampler, g_invScreen.zw);
	
	return float4(rgb, 1.0f); 
}

//-------------------------------------------------------------------------------------------------
technique fxaa
{
	pass Pass_0
	{
		ALPHABLENDENABLE = FALSE;
		ALPHATESTENABLE = FALSE;
		FOGENABLE = FALSE;
		POINTSPRITEENABLE = FALSE;
		STENCILENABLE = FALSE;
		ZENABLE = FALSE;
		ZWRITEENABLE = FALSE;
		CULLMODE = CW;
		
		VertexShader = compile vs_3_0 VS();
		PixelShader  = compile ps_3_0 PS();
	}
}
#include "stdinclude.fxh"

#ifdef BW_SKINNED
#include "skinned_effect_include.fxh"
#else
#include "unskinned_effect_include.fxh"
#endif

//-------------------------------------------------------------------------------------------------
// Uniform constants
//-------------------------------------------------------------------------------------------------

float4x4 g_lightViewProj;
float4x4 g_mainViewProj;
float4x4 g_mainView;

// Split planes in main view space
// x -- near
// y -- far
float2 g_splitPlanes;

//-------------------------------------------------------------------------------------------------

struct VertexXYZ
{
	float4 pos		: POSITION;
#ifdef BW_SKINNED
	float3 indices	: BLENDINDICES;
	float2 weights	: BLENDWEIGHT;	
#endif
};

struct Output
{
	float4 pos				: POSITION;
	float4 mainViewPos		: TEXCOORD1;
	float4 mainViewProjPos	: TEXCOORD2;
};

//-------------------------------------------------------------------------------------------------
// Vertex shader
//-------------------------------------------------------------------------------------------------

Output vs_main(VertexXYZ i)
{
	Output o = (Output) 0;

#ifndef BW_SKINNED
	float4 worldPos = mul(i.pos, g_world);
#else
	int indices[3];
    calculateSkinningIndices(i.indices, indices);
    float weights[3] = { i.weights.x, i.weights.y, 1 - i.weights.y - i.weights.x };
	float4 worldPos = transformPos(g_world, i.pos, weights, indices);
#endif

	o.pos = mul(worldPos, g_lightViewProj);
	o.mainViewPos = mul(worldPos, g_mainView);
	o.mainViewProjPos = mul(worldPos, g_mainViewProj);

	return o;
}

//-------------------------------------------------------------------------------------------------
// Pixel shader
//-------------------------------------------------------------------------------------------------

float4 ps_main( Output i ) : COLOR
{
	if(i.mainViewPos.z < g_splitPlanes.x || i.mainViewPos.z > g_splitPlanes.y)
	{
		discard;
	}

	float3 mvpp = i.mainViewProjPos.xyz / i.mainViewProjPos.w;

	if(any(mvpp.xy < -1.f) || any(mvpp.xy > 1.f) || mvpp.z > 1.f || mvpp.z < 0.f)
	{
		discard;
	}
	
#ifdef BW_SKINNED
	return float4(0.f, 1.f, 0.f, 1.0f);
#else
	return float4(1.f, 0.f, 0.f, 1.0f);
#endif
}

//-------------------------------------------------------------------------------------------------
// Technique 
//-------------------------------------------------------------------------------------------------

technique standard
<
	bool skinned = true;
	string label = "SHADER_MODEL_2";
>
{
	pass Pass_0
	{
		ALPHATESTENABLE = FALSE;
		ALPHABLENDENABLE = FALSE;

		ZENABLE = TRUE;
		ZWRITEENABLE = TRUE;
		ZFUNC = LESSEQUAL;

		CULLMODE = NONE;

		VertexShader = compile vs_2_0 vs_main();
		PixelShader = compile ps_2_0 ps_main();
	}
}
BW_NULL_TECHNIQUE

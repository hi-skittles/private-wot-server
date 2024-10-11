#include "stdinclude.fxh"
#include "skinned_effect_include.fxh"

const float3 g_colorMask;

struct VertexXYZIIIWW
{
	float4 pos: 	POSITION;
	float3 indices:	BLENDINDICES;
	float2 weights:	BLENDWEIGHT;
};

struct Output
{
	float4 pos:  POSITION;
};

//-------------------------------------------------------------------------
Output VS(VertexXYZIIIWW i)
{
	Output o = (Output)0;

	int indices[3];
    calculateSkinningIndices( i.indices, indices );
	
    float weights[3] = { i.weights.x, i.weights.y, 1 - i.weights.y - i.weights.x };
	float4 worldPos = transformPos(g_world, i.pos, weights, indices );
	o.pos = mul(worldPos, g_viewProjMat);

	return o;
}

//-------------------------------------------------------------------------
float4 PS(Output i) : COLOR0
{
	return float4(g_colorMask, 0);
}

//--------------------------------------------------------------//
// Technique Section for standard
//--------------------------------------------------------------//
technique standard
<
	bool skinned = true;
	string label = "SHADER_MODEL_2";
>
{
	pass Pass_0
	{
		ZENABLE = TRUE;
		ZWRITEENABLE = FALSE;
		ALPHATESTENABLE = FALSE;
		ALPHABLENDENABLE = FALSE;
		FOGENABLE = FALSE;
		CULLMODE = CCW;
		VertexShader = compile vs_2_0 VS();
		PixelShader = compile ps_2_0 PS();
	}
}
BW_NULL_TECHNIQUE

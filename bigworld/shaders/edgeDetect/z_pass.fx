#include "stdinclude.fxh"

const float4x4 g_MVPMat : WorldViewProjection;
const float3   g_colorMask;

struct VertexXYZ
{
	float4 pos : POSITION;
};

struct Output
{
	float4 pos  : POSITION;
};

//-------------------------------------------------------------------------
Output VS(VertexXYZ i)
{
	Output o = (Output)0;

	o.pos = mul(i.pos, g_MVPMat);

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

#include "stdinclude.fxh"

//-- params.
const float4  g_edgeColors[3];
texture       g_edgeDetectedMap;

//-------------------------------------------------------------------------------------------------
sampler g_edgeSampler = sampler_state
{
	Texture 		= (g_edgeDetectedMap);
	ADDRESSU 		= WRAP;
	ADDRESSV 		= WRAP;
	ADDRESSW 		= WRAP;
	MAGFILTER 		= POINT;
	MINFILTER 		= POINT;
	MIPFILTER 		= POINT;
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


//-- Does the simplest edge detect filter. I.e. looks at the four directions
//-- up - down, left - right and if the final sum is great then zero, this means that currect
//-- pixel situates on the edge.
//-------------------------------------------------------------------------------------------------
half4 detectEdge(in float2 tc)
{
	const float2 d10 = float2(g_invScreen.z, 0.0f);
	const float2 d01 = float2(0.0f, g_invScreen.w);
	
	half4 c1 = tex2D(g_edgeSampler, tc + d01);
	half4 c2 = tex2D(g_edgeSampler, tc - d01);
	half4 c3 = tex2D(g_edgeSampler, tc + d10);
	half4 c4 = tex2D(g_edgeSampler, tc - d10);
	
	return saturate(abs(c1 - c2) + abs(c3 - c4));
}

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
	half4 o    = half4(0,0,0,0);
	half4 edge = detectEdge(i.tc);
	
	o += edge.r * g_edgeColors[0];
	o += edge.g * g_edgeColors[1];
	o += edge.b * g_edgeColors[2];
	
	return o;
}

//-------------------------------------------------------------------------------------------------
technique shaderTransfer
{
	pass Pass_0
	{
		ALPHABLENDENABLE = TRUE;
		ALPHATESTENABLE = FALSE;
		CULLMODE = CW;
		SRCBLEND = SRCALPHA;
		DESTBLEND = INVSRCALPHA;
		BlendOp = ADD;
		
		ZENABLE = TRUE;
		ZWRITEENABLE = FALSE;
		ZFUNC = ALWAYS;
		FOGENABLE = FALSE;
		
		VertexShader = compile vs_2_0 VS();
		PixelShader  = compile ps_2_0 PS();
	}
}
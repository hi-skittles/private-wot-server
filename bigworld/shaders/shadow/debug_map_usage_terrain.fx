#include "terrain_common.fxh"

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

struct TerrainVertexOutput
{
	float4 position			: POSITION;
	float4 mainViewPos		: TEXCOORD1;
	float4 mainViewProjPos	: TEXCOORD2;
};

//-------------------------------------------------------------------------------------------------
// Vertex shader
//-------------------------------------------------------------------------------------------------

void vs30_terrain( in TerrainVertex vertex, inout TerrainVertexOutput oVertex )
{	
	// Calculate the position of the vertex
	float4 worldPos = terrainVertexPosition(vertex);
	oVertex.position = mul(worldPos, g_lightViewProj);
	oVertex.mainViewPos = mul(worldPos, g_mainView);
	oVertex.mainViewProjPos = mul(worldPos, g_mainViewProj);
}

//-------------------------------------------------------------------------------------------------
// Pixel shader
//-------------------------------------------------------------------------------------------------

float4 ps30_terrain( const TerrainVertexOutput i ) : COLOR
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
	
	return float4(0.f, 0.f, 1.f, 1.0f);
};

//-------------------------------------------------------------------------------------------------
// Technique 
//-------------------------------------------------------------------------------------------------

technique four_layer_shader_3_0
<
	string label = "SHADER_MODEL_3";
>
{
	pass lighting_only_pass
	{
        ALPHABLENDENABLE = FALSE;
        ALPHATESTENABLE = FALSE;

		ZENABLE = TRUE;
        ZWRITEENABLE = TRUE;
        ZFUNC = LESSEQUAL;

		CULLMODE = NONE;
        
        VertexShader = compile vs_3_0 vs30_terrain();
		PixelShader = compile ps_3_0 ps30_terrain();
	}
}

//-------------------------------------------------------------------------------------------------
// End
//-------------------------------------------------------------------------------------------------
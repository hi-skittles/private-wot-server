#include "terrain_common.fxh"

//--------------------------------------------------------------------------------------------------
float g_esmK;

//--------------------------------------------------------------------------------------------------
struct VS_CASTER_OUTPUT
{
	float4 pos	 : POSITION;
	float2 depth : TEXCOORD0;
};

//--------------------------------------------------------------------------------------------------
VS_CASTER_OUTPUT vs_main(const TerrainVertex vertex)
{
	VS_CASTER_OUTPUT o = (VS_CASTER_OUTPUT) 0;
	float4 worldPos = terrainVertexPosition(vertex);
	o.pos = mul(worldPos, g_viewProjMat);
	o.depth = o.pos.zw;
	return o;
};

//--------------------------------------------------------------------------------------------------
float4 ps_main(VS_CASTER_OUTPUT i) : COLOR
{
    float depth = i.depth.x / i.depth.y;
	float d = exp( - g_esmK * depth);
    return float4(d, d, d, d);
}

//--------------------------------------------------------------------------------------------------
technique standard
{
	pass Pass_0
	{
		ALPHATESTENABLE = FALSE;
		ALPHABLENDENABLE = FALSE;

		ZENABLE = TRUE;									
		ZWRITEENABLE = TRUE;
		ZFUNC = LESSEQUAL;
								
		FOGENABLE = FALSE;
		CULLMODE = CCW; 
				
		VertexShader = compile vs_3_0 vs_main();
		PixelShader  = compile ps_3_0 ps_main();
	}
}
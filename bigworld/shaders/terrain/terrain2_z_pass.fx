#include "terrain_common.fxh"

USE_TERRAIN_HOLES_MAP

//--------------------------------------------------------------------------------------------------
struct TerrainVertexOutput
{
	float4 position	: POSITION;
    float2 holesUV	: TEXCOORD0;
};

//--------------------------------------------------------------------------------------------------
TerrainVertexOutput vs_main_2_0(const TerrainVertex i)
{
	TerrainVertexOutput o  = (TerrainVertexOutput)0;
	
	o.position = mul(terrainVertexPosition(i), g_viewProjMat);
    o.holesUV  = i.xz * (holesSize / holesMapSize);

	return o;
};

//--------------------------------------------------------------------------------------------------
float4 ps_main_2_0(const TerrainVertexOutput i, uniform bool hasHoles) : COLOR0
{
    if (hasHoles)
    {
        //-- do the holes.
        clip(-tex2D(holesMapSampler, i.holesUV).x);
    }
    
	return float4(0,0,0,1);
};

//--------------------------------------------------------------------------------------------------
PixelShader PS[2] =
{
    compile ps_2_0 ps_main_2_0(0),
    compile ps_2_0 ps_main_2_0(1)
};

//--------------------------------------------------------------------------------------------------
technique Z_PASS
{
	pass Pass_0
	{
        ALPHATESTENABLE		= FALSE;
        ALPHABLENDENABLE	= FALSE;
        ZENABLE				= TRUE;
        ZWRITEENABLE		= TRUE;
        ZFUNC				= LESSEQUAL;
		CULLMODE			= BW_CULL_CCW;
        
		VertexShader = compile vs_2_0 vs_main_2_0();
		PixelShader  = PS[int(holesSize > 0)];
	}
}
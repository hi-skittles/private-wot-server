#include "shared_constants.fxh"

//--------------------------------------------------------------------------------------------------
float4 dummyVS(in float4 pos : POSITION) : POSITION
{
	return pos;
}

//--------------------------------------------------------------------------------------------------
float4 dummyPS(in float4 pos : POSITION) : COLOR0
{
	return float4(1,1,1,1);
}

//--------------------------------------------------------------------------------------------------
technique DummyTechnique
{									
	pass DummyPass					
	{		
		VertexShader = compile vs_2_0 dummyVS();
		PixelShader  = compile ps_2_0 dummyPS();
	}
}
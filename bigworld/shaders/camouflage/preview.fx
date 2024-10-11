float4 vColor0;
float4 vColor1;
float4 vColor2;
float4 vColor3;
float4 vWeights;
float4 vBGColor;


texture texMask;

sampler smpMask = sampler_state
{
	texture = < texMask >;
	MinFilter = Linear;
	MagFilter = Linear;
	MipFilter = Linear;
};

struct InVertex
{
	float3	vPosition : POSITION;
	float2	vTexCoord : TEXCOORD0;
};

struct OutVertex
{
	float4	vPosition : POSITION;
	float2	vTexCoord : TEXCOORD0;
};

OutVertex VS_Cam( InVertex input )
{
	OutVertex result;
	result.vPosition = float4( input.vPosition, 1 );
	result.vTexCoord = input.vTexCoord;
	return result;
}

float4 PS_Cam( OutVertex input ): COLOR
{
	float4 vMask = tex2D( smpMask, input.vTexCoord );
	vMask *= vWeights;

	float3 rgb = vBGColor.rgb;
	rgb = lerp( rgb, vColor0.rgb, vMask.r );
	rgb = lerp( rgb, vColor1.rgb, vMask.g );
	rgb = lerp( rgb, vColor2.rgb, vMask.b );
	rgb = lerp( rgb, vColor3.rgb, vMask.a );

	return float4( rgb, 1 );
}

technique techCam
{
	pass p0
	{
		VertexShader = compile vs_2_0 VS_Cam();
		PixelShader = compile ps_2_0 PS_Cam();

		ZEnable = false;
		StencilEnable = false;
		FogEnable = false;
		AlphaBlendEnable = False;
		AlphaTestEnable = False;
		CullMode = None;
	}	
}

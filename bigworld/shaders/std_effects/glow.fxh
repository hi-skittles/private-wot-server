#ifndef GLOW_FXH
#define GLOW_FXH

BW_ARTIST_EDITABLE_DIFFUSE_MAP
BW_ARTIST_EDITABLE_DOUBLE_SIDED
BW_ARTIST_EDITABLE_ALPHA_TEST
BW_ARTIST_EDITABLE_MOD2X
BW_ARTIST_EDITABLE_ADDRESS_MODE(BW_WRAP)

sampler diffuseSampler = BW_SAMPLER(diffuseMap, BW_TEX_ADDRESS_MODE)

//--------------------------------------------------------------------------------------------------
struct VS2PS
{
	float4 pos		:	POSITION;
	float2 tc		:	TEXCOORD0;
	float4 worldPos	:	TEXCOORD1;
	float3 normal	:	TEXCOORD2;
	float  fog		:	FOG;
};

//--------------------------------------------------------------------------------------------------
VS2PS vs_main_2_0(VERTEX_FORMAT i)
{
	VS2PS o = (VS2PS)0;

	BW_PROJECT_POSITION(o)
	BW_CALCULATE_UVS(o)
	BW_VERTEX_FOG(o)

	return o;
}

//--------------------------------------------------------------------------------------------------
float4 ps_main_2_0(VS2PS i, uniform bool alphaTest) : COLOR0
{
	half4 diffuse = gamma2linear(tex2D(diffuseSampler, i.tc));

	//-- compile-time branching.
	if (alphaTest)
	{
		clip(diffuse.a - alphaReference / 255.0h);
	}

	return diffuse;
}

//--
PixelShader compiled_ps_main_2_0[] = {
	compile ps_2_0 ps_main_2_0(false),
	compile ps_2_0 ps_main_2_0(true)
};

#endif //-- GLOW_FXH
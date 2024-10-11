#include "stdinclude.fxh"
#include "read_g_buffer.fxh"

//-- TODO(a_cherkes): думаю, что возможна оптимизация путем учета
//--                  visibilityDistance теней. Ресолвить нужно только
//--                  ту часть мира, которая находится перед ней.

static const int MaxNumSplits = 4;

const int g_shadowQuality = 0;

// x - blend start
// y - blend distance
float2 g_blend;

//-- splits
float		g_dynamicShadowMapResolution;
float4x4	g_textureMatrices[MaxNumSplits];
float		g_splitPlanesArray[MaxNumSplits];
texture		g_shadowMapAtlas;
texture		g_noiseMapShadow;
float		g_splitCount;

//-- terrain
//float		g_esmK;
//float4x4	g_textureMatrixTerrain;
//texture	g_shadowMapTerrain;

#define DEFINE_SHADOW_MAP_SAMPLER( N )						\
sampler shadowSampler##N = sampler_state					\
{															\
	Texture = <g_shadowMap##N>;								\
	MIPFILTER = POINT;										\
	MAGFILTER = POINT;										\
	MINFILTER = POINT;										\
	ADDRESSU = BORDER;										\
	ADDRESSV = BORDER;										\
	BORDERCOLOR = float4(1.0f, 1.0f, 1.0f, 1.0f);			\
};

//-- noise map sampler.
sampler noiseMapSampler = sampler_state
{		
	Texture = <g_noiseMapShadow>;
	MIPFILTER = LINEAR;
	MAGFILTER = POINT;
	MINFILTER = POINT;
	ADDRESSU = WRAP;
	ADDRESSV = WRAP;
};

DEFINE_SHADOW_MAP_SAMPLER(Atlas)

//--------------------------------------------------------------------------------------------------
struct VS_INPUT
{
	float4 pos : POSITION;
	float2 tc  : TEXCOORD;
};

//--------------------------------------------------------------------------------------------------
struct VS_OUTPUT
{
	float4 pos : POSITION;
	float2 tc  : TEXCOORD0;
};

//-- generated poisson points on a disk, max radius = 1
const static float2 poissonDisk[] = {
    float2(-0.2613868f, -0.005345194f),
    float2(0.1172257f, 0.7124456f),
    float2(0.4299957f, -0.1240174f),
    float2(-0.6207129f, 0.6525496f),
    float2(-0.7165685f, -0.5897592f),
    float2(0.04813414f, -0.8662012f),
    float2(-0.9632512f, 0.02041215f),
    float2(0.8428857f, 0.1896802f),
    float2(0.4971309f, -0.681029f),
    float2(0.9297811f, -0.3064848f),
    float2(0.6275305f, 0.6259851f)
};

//-- do PCF filter based on poisson disk with 11 samples.
//-------------------------------------------------------------------------------------------------
float PCF_filter(sampler s, float2 shadowUV, float zReceiver, float filterRadiusUV, const int samplesCount) 
{ 
	float2 g_invRes = 1.0f / (2.0f * g_dynamicShadowMapResolution);
	float  sum	    = 0.0f; 
	float2 adjust   = g_invRes * filterRadiusUV;

	[unroll]
	for (int i = 0; i < samplesCount; ++i) 
	{ 
		sum += (zReceiver > tex2D(s, shadowUV + poissonDisk[i] * adjust).x);
	} 
	return sum / samplesCount; 
}

//-- do PCF filter based on randomly rotated poisson disk with 11 samples.
//-------------------------------------------------------------------------------------------------
float rotated_PCF_filter(sampler s, in float2 screenUV, float2 shadowUV, float zReceiver, float splitBlurFactor, const int samplesCount) 
{ 
    half  sum	  = 0.0f; 
	half2 adjust = 1 / (2 * g_dynamicShadowMapResolution);

	//-- use screen space noise texture coordinates or world space.
	float2 noiseUV = screenUV * (g_screen.xy / float2(256,256));

	//-- read noise angle in radians.
	half2 noise = tex2D( noiseMapSampler, noiseUV ).rg;
	
	//-- calculate 2D rotation poisson disk matrix.
	half2x2 rotMat = {
		+noise.r, -noise.g,
		+noise.g, +noise.r
	};

	//-- fade blur radius depending on the current shadow spit.
	half blurFactor = lerp(2.0f, 1.0f, splitBlurFactor);
	
	//-- do PCF filter with poisson disk.
#if 0
	//-- Non optimized version.
	[unroll]
    for (int i = 0; i < samplesCount; ++i) 
	{ 
		float2 coords = mul(poissonDisk[i], rotMat);
		sum += (zReceiver > tex2D(s, shadowUV + coords * adjust * blurFactor).x);
    }
#else
	//-- Optimized version.
	const half adjustBlurFactor = adjust * blurFactor;

	[unroll]
	for (int i = 0; i < samplesCount; i += 4) 
	{ 
		half4 coords01;
		half4 coords23;

		coords01.xy = mul(poissonDisk[i + 0], rotMat);
		coords01.zw = mul(poissonDisk[i + 1], rotMat);
		coords23.xy = mul(poissonDisk[i + 2], rotMat);
		coords23.zw = mul(poissonDisk[i + 3], rotMat);

		coords01 *= adjustBlurFactor;
		coords23 *= adjustBlurFactor;

		float4 depths;
		depths[0] = tex2D(s, shadowUV + coords01.xy).x;
		depths[1] = tex2D(s, shadowUV + coords01.zw).x;
		depths[2] = tex2D(s, shadowUV + coords23.xy).x;
		depths[3] = tex2D(s, shadowUV + coords23.zw).x;
	
		half4 res = (zReceiver.xxxx > depths) ? 1.0f : 0.0f;
		sum += dot(res, 1);
    } 
#endif

	//-- find the average coverage shadow value.
    return (sum / samplesCount);
}


//-- Sampling appropriate split. We can use here some more advanced sampling techniques to add our
//-- shadows some more softed look.
//--------------------------------------------------------------------------------------------------
float sampleShadowSplit(sampler s, float2 uv, float z)
{
	return (z > tex2D(s, uv).r);
}

//-- vertex shader.
//--------------------------------------------------------------------------------------------------
VS_OUTPUT VS(VS_INPUT i)
{
	VS_OUTPUT o = (VS_OUTPUT)0;
	o.pos = i.pos;
	o.tc  = i.tc;
	return o;
}

//-- debug visualization
static const float4 g_colors[] = {
	float4(1,0,0,1),
	float4(0,1,0,1),
	float4(0,0,1,1),
	float4(1,0,1,1)
};

//-- pixel shader.
//--------------------------------------------------------------------------------------------------
//--------------------------------------------------------------------------------------------------
float4 PS(VS_OUTPUT i, const uniform int samplesCount) : COLOR
{
	//-- read world space position.
	float3 wPos = g_buffer_readWorldPos(i.tc, g_nvStereoParams.w);

	//-- find view space z value.
	float viewZ	= g_buffer_readLinearZ(i.tc) * g_farPlane.x;
	float coverage = 0.0f;

	//--
	int split = MaxNumSplits + 1;

	for ( int idx = 0; idx < g_splitCount && idx < MaxNumSplits; ++idx )
	{
		if (viewZ < g_splitPlanesArray[idx])
		{
			split = idx;
			break;
		}
	}

	//--
	clip( g_splitCount - split );

	float4 sp   = mul( float4( wPos, 1 ), g_textureMatrices[split] );
	float3 smTC = sp.xyz / sp.w;

	float dynamicShadowCoverage = rotated_PCF_filter(
		shadowSamplerAtlas,
		i.tc, 
		smTC.xy,
		smTC.z,
		split / g_splitCount,
		samplesCount
	);

	//-- result coverage
	coverage = saturate( dynamicShadowCoverage );

	return coverage;
}

//--------------------------------------------------------------------------------------------------
PixelShader g_pixelShaders[3] = 
{
	//-- dynamic shadows OFF
	compile ps_3_0 PS(8),
	compile ps_3_0 PS(4),
	compile ps_3_0 PS(1)
};

//--------------------------------------------------------------------------------------------------
technique fill_deffered_all
{
	pass Pass_0
	{
		COLORWRITEENABLE = RED;
		ALPHATESTENABLE = FALSE;
		ALPHABLENDENABLE = FALSE;
		ZENABLE = FALSE;
		ZWRITEENABLE = FALSE;
		FOGENABLE = FALSE;
		CULLMODE =  CW;

		//-- use stencil to mark only valid g-buffer pixels (i.e. not sky pixels)
		STENCILENABLE = TRUE;
		STENCILFUNC = NOTEQUAL;
		STENCILWRITEMASK = 0x00;
		STENCILMASK = G_STENCIL_USAGE_ALL_OPAQUE;
		STENCILREF = 0;

		VertexShader = compile vs_3_0 VS();
		PixelShader  = g_pixelShaders[g_shadowQuality];
	}
}

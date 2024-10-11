#include "stdinclude.fxh"

//-- params.
texture		 g_avgLumMap;
texture		 g_srcMap;
texture		 g_prevMipMap;
const float4 g_srcSize;
const float4 g_params;

//-------------------------------------------------------------------------------------------------
sampler g_avgLumMapSampler = sampler_state
{
	Texture 		= (g_avgLumMap);
	ADDRESSU 		= CLAMP;
	ADDRESSV 		= CLAMP;
	ADDRESSW 		= CLAMP;
	MAGFILTER 		= POINT;
	MINFILTER 		= POINT;
	MIPFILTER 		= POINT;
	MAXMIPLEVEL 	= 0;
	MIPMAPLODBIAS 	= 0;
};

//-------------------------------------------------------------------------------------------------
sampler g_srcMapLinearSampler = sampler_state
{
	Texture 		= (g_srcMap);
	ADDRESSU 		= CLAMP;
	ADDRESSV 		= CLAMP;
	ADDRESSW 		= CLAMP;
	MAGFILTER 		= LINEAR;
	MINFILTER 		= LINEAR;
	MIPFILTER 		= LINEAR;
	MAXMIPLEVEL 	= 0;
	MIPMAPLODBIAS 	= 0;
};

//-------------------------------------------------------------------------------------------------
sampler g_srcMapPointSampler = sampler_state
{
	Texture 		= (g_srcMap);
	ADDRESSU 		= CLAMP;
	ADDRESSV 		= CLAMP;
	ADDRESSW 		= CLAMP;
	MAGFILTER 		= POINT;
	MINFILTER 		= POINT;
	MIPFILTER 		= POINT;
	MAXMIPLEVEL 	= 0;
	MIPMAPLODBIAS 	= 0;
};

//-------------------------------------------------------------------------------------------------
sampler g_prevMipMapLinearSampler = sampler_state
{
	Texture 		= (g_prevMipMap);
	ADDRESSU 		= CLAMP;
	ADDRESSV 		= CLAMP;
	ADDRESSW 		= CLAMP;
	MAGFILTER 		= LINEAR;
	MINFILTER 		= LINEAR;
	MIPFILTER 		= LINEAR;
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

//-------------------------------------------------------------------------------------------------
VertexOut VS(VertexXYZUV i)
{
	VertexOut o = (VertexOut)0;
	o.pos = i.pos;
	o.tc  = i.tc;
	
	return o;
}

//-------------------------------------------------------------------------------------------------
float4 PS_bright_pass(const VertexOut i) : COLOR0
{
	half3 color = tex2D(g_srcMapLinearSampler, i.tc).rgb;

	const half g_brightThreshold = g_params.x;
	const half g_brightOffset	 = g_params.y;
	const half g_middleGray		 = g_params.z;
	const half g_avgLum			 = tex2D(g_avgLumMapSampler, float2(0,0));
	
	//-- map HDR color to the final color.
	color *= g_middleGray / (g_avgLum + 0.0001f);

	//-- determine bright regions.
	color = max(0.0h, color - g_brightThreshold);

	//-- now map color to the range [0,1)
	color /= (g_brightOffset + color);

	//-- scale range to keep some precision in darks (gets rescaled down to original value
	//-- during final tone map scene).
	return float4(color * 8.0f, 0.0f);
}

//-------------------------------------------------------------------------------------------------
float4 PS_down_sample_bloom_map(const VertexOut i) : COLOR0
{
	return tex2D(g_srcMapLinearSampler, i.tc);
}

//-------------------------------------------------------------------------------------------------
float4 PS_accumulate_bloom_map(const VertexOut i) : COLOR0
{
	float4 curMip  = tex2D(g_srcMapPointSampler, i.tc);
	float4 prevMip = tex2D(g_prevMipMapLinearSampler, i.tc);

	return max(curMip, prevMip);
}

//-------------------------------------------------------------------------------------------------
technique BRIGHT_PASS
{
	pass Pass_0
	{
		ALPHABLENDENABLE = FALSE;
		ALPHATESTENABLE = FALSE;
		ZENABLE = FALSE;
		ZWRITEENABLE = FALSE;
		FOGENABLE = FALSE;
		CULLMODE = CW;
		
		VertexShader = compile vs_3_0 VS();
		PixelShader  = compile ps_3_0 PS_bright_pass();
	}
}

//-------------------------------------------------------------------------------------------------
technique DOWN_SAMPLE_BLOOM_MAP
{
	pass Pass_0
	{
		ALPHABLENDENABLE = FALSE;
		ALPHATESTENABLE = FALSE;
		ZENABLE = FALSE;
		ZWRITEENABLE = FALSE;
		FOGENABLE = FALSE;
		CULLMODE = CW;
		
		VertexShader = compile vs_3_0 VS();
		PixelShader  = compile ps_3_0 PS_down_sample_bloom_map();
	}
}

//-------------------------------------------------------------------------------------------------
technique ACCUMULATE_BLOOM_MAP
{
	pass Pass_0
	{
		ALPHABLENDENABLE = FALSE;
		ALPHATESTENABLE = FALSE;
		ZENABLE = FALSE;
		ZWRITEENABLE = FALSE;
		FOGENABLE = FALSE;
		CULLMODE = CW;
		
		VertexShader = compile vs_3_0 VS();
		PixelShader  = compile ps_3_0 PS_accumulate_bloom_map();
	}
}
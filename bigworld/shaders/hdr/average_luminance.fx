#include "stdinclude.fxh"

//-- params.
texture		 g_previousMipMap;
const float4 g_previousMipMapSize;

//-------------------------------------------------------------------------------------------------
const float4 g_params; //-- x - eye dark limit, y - eye light limit, z - cur time, w - accomodation speed.
texture		 g_avgLumMap1;
texture		 g_avgLumMap2;

//-------------------------------------------------------------------------------------------------
sampler g_avgLumMap1Sampler = sampler_state
{
	Texture 		= (g_avgLumMap1);
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
sampler g_avgLumMap2Sampler = sampler_state
{
	Texture 		= (g_avgLumMap2);
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
sampler g_previousMipMapPointSampler = sampler_state
{
	Texture 		= (g_previousMipMap);
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
sampler g_previousMipMapLinearSampler = sampler_state
{
	Texture 		= (g_previousMipMap);
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
float4 PS_average_log_lum(VertexOut i) : COLOR0
{
	half lum0 = log(luminance(tex2D(g_previousMipMapPointSampler, i.tc - half2(+g_previousMipMapSize.z, 0.0h)).rgb) + 0.0001f);
	half lum1 = log(luminance(tex2D(g_previousMipMapPointSampler, i.tc - half2(0.0h, +g_previousMipMapSize.w)).rgb) + 0.0001f);
	half lum2 = log(luminance(tex2D(g_previousMipMapPointSampler, i.tc - half2(-g_previousMipMapSize.z, 0.0h)).rgb) + 0.0001f);
	half lum3 = log(luminance(tex2D(g_previousMipMapPointSampler, i.tc - half2(0.0h, -g_previousMipMapSize.w)).rgb) + 0.0001f);

	return (lum0 + lum1 + lum2 + lum3) * 0.25h;
}

//-------------------------------------------------------------------------------------------------
float4 PS_average_lum(VertexOut i) : COLOR0
{
	half lum0 = luminance(tex2D(g_previousMipMapPointSampler, i.tc - half2(+g_previousMipMapSize.z, 0.0h)).rgb);
	half lum1 = luminance(tex2D(g_previousMipMapPointSampler, i.tc - half2(0.0h, +g_previousMipMapSize.w)).rgb);
	half lum2 = luminance(tex2D(g_previousMipMapPointSampler, i.tc - half2(-g_previousMipMapSize.z, 0.0h)).rgb);
	half lum3 = luminance(tex2D(g_previousMipMapPointSampler, i.tc - half2(0.0h, -g_previousMipMapSize.w)).rgb);

	return (lum0 + lum1 + lum2 + lum3) * 0.25h;
}

//-------------------------------------------------------------------------------------------------
float4 PS_down_sample_color(VertexOut i) : COLOR0
{
	return tex2D(g_previousMipMapLinearSampler, i.tc);
}

//-------------------------------------------------------------------------------------------------
float4 PS_down_sample_lum(VertexOut i) : COLOR0
{
	return tex2D(g_previousMipMapLinearSampler, i.tc);
}

//-------------------------------------------------------------------------------------------------
float4 PS_final_average_lum(VertexOut i) : COLOR0
{
	//-- read average luminance from previous and current frame and do clamping of these values in
	//-- eye limits range.
	float avgLum1 = clamp(tex2D(g_avgLumMap1Sampler, float2(0,0)), g_params.x, g_params.y);
	float avgLum2 = clamp(tex2D(g_avgLumMap2Sampler, float2(0,0)), g_params.x, g_params.y);

	//-- calculate lerp delta for finding final average luminance.
	float delta   = 1.0f - pow(0.98f, g_params.w * g_params.z);

	//-- find final averga luminance.
	float finalAvgLum = lerp(avgLum1, avgLum2, delta);

	return finalAvgLum;
}

//-------------------------------------------------------------------------------------------------
float4 PS_final_average_log_lum(VertexOut i) : COLOR0
{
	//-- read average luminance from previous and current frame and do clamping of these values in
	//-- eye limits range.
	//-- Note: we use exp only on the second map because the first one already did it.
	float avgLum1 = clamp(tex2D(g_avgLumMap1Sampler, float2(0,0)).x, g_params.x, g_params.y);
	float avgLum2 = clamp(exp(tex2D(g_avgLumMap2Sampler, float2(0,0)).x), g_params.x, g_params.y);

	//-- calculate lerp delta for finding final average luminance.
	float delta   = 1.0f - pow(0.98f, g_params.w * g_params.z);

	//-- find final averga luminance.
	float finalAvgLum = lerp(avgLum1, avgLum2, delta);

	return finalAvgLum;
}

//-------------------------------------------------------------------------------------------------
technique DOWN_SAMPLE_COLOR
{
	pass Pass_0
	{
		ALPHABLENDENABLE = FALSE;
		ALPHATESTENABLE = FALSE;
		ZENABLE = FALSE;
		ZWRITEENABLE = FALSE;
		FOGENABLE = FALSE;
		CULLMODE = CW;
		
		VertexShader = compile vs_2_0 VS();
		PixelShader  = compile ps_2_0 PS_down_sample_color();
	}
}

//-------------------------------------------------------------------------------------------------
technique DOWN_SAMPLE_LUM
{
	pass Pass_0
	{
		ALPHABLENDENABLE = FALSE;
		ALPHATESTENABLE = FALSE;
		ZENABLE = FALSE;
		ZWRITEENABLE = FALSE;
		FOGENABLE = FALSE;
		CULLMODE = CW;
		
		VertexShader = compile vs_2_0 VS();
		PixelShader  = compile ps_2_0 PS_down_sample_lum();
	}
}

//-------------------------------------------------------------------------------------------------
technique AVERAGE_LUM
{
	pass Pass_0
	{
		ALPHABLENDENABLE = FALSE;
		ALPHATESTENABLE = FALSE;
		ZENABLE = FALSE;
		ZWRITEENABLE = FALSE;
		FOGENABLE = FALSE;
		CULLMODE = CW;
		
		VertexShader = compile vs_2_0 VS();
		PixelShader  = compile ps_2_0 PS_average_lum();
	}
}

//-------------------------------------------------------------------------------------------------
technique LOG_AVERAGE_LUM
{
	pass Pass_0
	{
		ALPHABLENDENABLE = FALSE;
		ALPHATESTENABLE = FALSE;
		ZENABLE = FALSE;
		ZWRITEENABLE = FALSE;
		FOGENABLE = FALSE;
		CULLMODE = CW;
		
		VertexShader = compile vs_2_0 VS();
		PixelShader  = compile ps_2_0 PS_average_log_lum();
	}
}

//-------------------------------------------------------------------------------------------------
technique FINAL_AVERAGE_LUM
{
	pass Pass_0
	{
		ALPHABLENDENABLE = FALSE;
		ALPHATESTENABLE = FALSE;
		ZENABLE = FALSE;
		ZWRITEENABLE = FALSE;
		FOGENABLE = FALSE;
		CULLMODE = CW;
		STENCILENABLE = FALSE;
		
		VertexShader = compile vs_2_0 VS();
		PixelShader  = compile ps_2_0 PS_final_average_lum();
	}
}

//-------------------------------------------------------------------------------------------------
technique FINAL_AVERAGE_LOG_LUM
{
	pass Pass_0
	{
		ALPHABLENDENABLE = FALSE;
		ALPHATESTENABLE = FALSE;
		ZENABLE = FALSE;
		ZWRITEENABLE = FALSE;
		FOGENABLE = FALSE;
		CULLMODE = CW;
		
		VertexShader = compile vs_2_0 VS();
		PixelShader  = compile ps_2_0 PS_final_average_log_lum();
	}
}
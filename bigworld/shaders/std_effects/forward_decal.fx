#undef BW_DEFERRED_SHADING
#define ADDITIVE_EFFECT 1
#include "stdinclude.fxh"
BW_ARTIST_EDITABLE_ADDITIVE_BLEND

#include "unskinned_effect_include.fxh"
#include "lightonly.fxh"
//--------------------------------------------------------------------------------------------------
texture g_atlasMap;
sampler g_atlasMapSml = sampler_state	
{									
	Texture = (g_atlasMap);
	ADDRESSU = BORDER;
	ADDRESSV = BORDER;
	ADDRESSW = BORDER;
	MAGFILTER = LINEAR;
	MINFILTER = (minMagFilter);
	MIPFILTER = (mipFilter);
	MAXANISOTROPY = (maxAnisotropy);
	MAXMIPLEVEL = 0;
	MIPMAPLODBIAS = 0;
	BORDERCOLOR = float4(0,0,0,0);
};

//--------------------------------------------------------------------------------------------------
const float4 g_atlasSize;
float4x4 worldSticker;
float4 g_uv;
float alpha;

//-- unpack texture coordinates offset and scale in the texture atlas map1.
//--------------------------------------------------------------------------------------------------

struct VSOutput
{
	float4 pos		:	POSITION;
	float2 tc		:	TEXCOORD0;
	float3 normal	:	TEXCOORD1;
	float4 worldPos	:	TEXCOORD2;
	float  fog		:	FOG;
};

VSOutput vs_main(VertexXYZNUV i)
{
	VSOutput o = (VSOutput)0;
	
	o.worldPos = mul(i.pos, worldSticker);
	o.normal = transformNormaliseVector( worldSticker, BW_UNPACK_VECTOR(i.normal) );
	o.pos = mul(o.worldPos, g_viewProjMat);

	BW_CALCULATE_UVS(o)
	o.tc = o.tc * g_uv.xy + g_uv.zw;
	BW_VERTEX_FOG(o)

	return o;
}

float4 ps_main_forward(VSOutput i) : COLOR0
{
	float4 diffuse = tex2D(g_atlasMapSml, i.tc);

	//-- ToDo: optimize.
	if (alphaTestEnable && (diffuse.a < (alphaReference / 255.0f)))
	{
		discard;
	}

    float3 color   = diffuse.rgb * (sunAmbientTerm().rgb + sunDiffuseTerm(normalize(i.normal)).rgb);

	return float4(color, diffuse.a*alpha);
}

float4 ps_main_deferred(VSOutput i) : COLOR0
{
	float4 diffuse = tex2D(g_atlasMapSml, i.tc);

	return float4(diffuse.rgb, diffuse.a*alpha);
}

//--------------------------------------------------------------------------------------------------
technique FORWARD
{
	pass Pass_0
	{		

		ALPHATESTENABLE = FALSE;
		ALPHABLENDENABLE = TRUE;
		COLORWRITEENABLE = RED | GREEN | BLUE;
		SRCBLEND = SRCALPHA;
		DESTBLEND = INVSRCALPHA;
		ZENABLE = TRUE;
		ZWRITEENABLE = FALSE;
		ZFUNC = LESSEQUAL;

		BW_FOG_ADD

		BW_TEXTURESTAGE_DIFFUSEONLY(0, diffuseMap)
		BW_TEXTURESTAGE_TERMINATE(1)
		
		VertexShader = compile vs_2_0 vs_main();
		PixelShader  = compile ps_2_0 ps_main_forward();
	}
}

technique DEFERRED
{
	pass Pass_0
	{		

		ALPHATESTENABLE = FALSE;
		ALPHABLENDENABLE = TRUE;
		COLORWRITEENABLE = RED | GREEN | BLUE;
		COLORWRITEENABLE1 = 0x00;
		SRCBLEND = SRCALPHA;
		DESTBLEND = INVSRCALPHA;
		ZENABLE = TRUE;
		ZWRITEENABLE = FALSE;
		ZFUNC = LESSEQUAL;
		
		VertexShader = compile vs_2_0 vs_main();
		PixelShader  = compile ps_2_0 ps_main_deferred();
	}
}

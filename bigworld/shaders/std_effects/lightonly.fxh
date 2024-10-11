#ifndef LIGHTONLY_FXH
#define LIGHTONLY_FXH

BW_ARTIST_EDITABLE_DIFFUSE_MAP
BW_ARTIST_EDITABLE_DOUBLE_SIDED
BW_ARTIST_EDITABLE_ALPHA_TEST
BW_ARTIST_EDITABLE_MOD2X
BW_ARTIST_EDITABLE_ADDRESS_MODE(BW_WRAP)

sampler diffuseSampler = BW_SAMPLER(diffuseMap, BW_TEX_ADDRESS_MODE)

#if DUAL_UV
	BW_ARTIST_EDITABLE_DIFFUSE_MAP2
	sampler diffuseSampler2 = BW_SAMPLER(diffuseMap2, BW_TEX_ADDRESS_MODE)
#endif

//-- colorise.
#ifdef COLOURISE_DIFFUSE_TEXTURE
	#include "colourise_diffuse_texture.fxh"
#endif

//-- spec map.
#ifdef USES_SPEC_MAP
	#include "specmap.fxh"
#endif

//-- common part of pixel shader.
//--------------------------------------------------------------------------------------------------
#if DUAL_UV
	#define BW_DIFFUSE_COLOR	diffuseColor(i.tc, i.tc2);
#else
	#define BW_DIFFUSE_COLOR	diffuseColor(i.tc, float2(0,0));
#endif

//--------------------------------------------------------------------------------------------------
half4 blendDiffuse(half4 diffuseMap1, half4 diffuseMap2)
{
#ifdef BLEND_ALTERNATIVE
	return half4(diffuseMap1.rgb*(1-diffuseMap2.a) + diffuseMap2.rgb*(diffuseMap2.a), diffuseMap1.a );
#else
	return half4(diffuseMap1.rgb * diffuseMap2.rgb, diffuseMap1.a * diffuseMap2.a);
#endif
}

//--------------------------------------------------------------------------------------------------
half4 diffuseColor(float2 tc, float2 tc2)
{
#if DUAL_UV
	half4 diffuseMap1 = gamma2linear(tex2D(diffuseSampler, tc.xy));
	half4 diffuseMap2 = gamma2linear(tex2D(diffuseSampler2, tc2.xy));
	half4 diffuseMap  = blendDiffuse(diffuseMap1, diffuseMap2);
#else
	half4 diffuseMap  = gamma2linear(tex2D(diffuseSampler, tc.xy));
#endif

#ifdef COLOURISE_DIFFUSE_TEXTURE
	diffuseMap = colouriseDiffuseTex(diffuseMap, tc.xy);
#endif

	return diffuseMap;
}

//--------------------------------------------------------------------------------------------------
#if BW_DEFERRED_SHADING

#include "write_g_buffer.fxh"

//--------------------------------------------------------------------------------------------------
BW_DS_VS_DIFFUSE_OUT vs_deferred_3_0(VERTEX_FORMAT i)
{
	BW_DS_VS_DIFFUSE_OUT o = (BW_DS_VS_DIFFUSE_OUT)0;

	BW_DS_PROJECT_POSITION(o)
	BW_DS_CALCULATE_UVS(o)

	return o;
}

//--------------------------------------------------------------------------------------------------
BW_DS_VS_DIFFUSE_OUT vs_instanced_deferred_3_0(VERTEX_FORMAT i, InstancingStream instance)
{
	BW_DS_VS_DIFFUSE_OUT o = (BW_DS_VS_DIFFUSE_OUT)0;

	BW_DS_INSTANCING_PROJECT_POSITION(o)
	BW_DS_INSTANCING_CALCULATE_UVS(o)

	return o;
}

//--------------------------------------------------------------------------------------------------
G_BUFFER_LAYOUT ps_deferred_3_0(BW_DS_VS_DIFFUSE_OUT i, uniform bool alphaTest)
{
	G_BUFFER_LAYOUT o = (G_BUFFER_LAYOUT)0;

	half4 color = BW_DIFFUSE_COLOR;

	//-- compile-time branching.
	if (alphaTest)
	{
		clip(color.a - alphaReference / 255.0h);
	}

	g_buffer_writeAlbedo(o, color.rgb);

#ifdef USES_SPEC_MAP
	half specular = luminance(tex2D(specularSampler, i.tc.xy).rgb);
	g_buffer_writeSpecAmount(o, specular);
#endif

	g_buffer_writeDepth(o, i.linerZ);
	g_buffer_writeNormal(o, i.normal);
	g_buffer_writeObjectKind(o, g_objectID ? G_OBJECT_KIND_DYNAMIC : G_OBJECT_KIND_STATIC);

	return o;
}

//--------------------------------------------------------------------------------------------------
struct OutputDiffuseLighting
{
	float4 pos		:	POSITION;
	float2 tc		:	TEXCOORD0;
#if DUAL_UV
	float2 tc2		:	TEXCOORD1;
#endif
	float3 normal	:	TEXCOORD2;
	float4 worldPos	:	TEXCOORD3;
	float  fog		:	TEXCOORD4;
};

//--------------------------------------------------------------------------------------------------
OutputDiffuseLighting vs_reflection_3_0(VERTEX_FORMAT i)
{
	OutputDiffuseLighting o = (OutputDiffuseLighting)0;

	BW_PROJECT_POSITION(o)
	BW_CALCULATE_UVS(o)
	BW_VERTEX_FOG(o)

	return o;
}

//--------------------------------------------------------------------------------------------------
OutputDiffuseLighting vs_instanced_reflection_3_0(VERTEX_FORMAT i, InstancingStream instance)
{
	OutputDiffuseLighting o = (OutputDiffuseLighting)0;

	BW_INSTANCING_PROJECT_POSITION(o)
	BW_INSTANCING_CALCULATE_UVS(o)
	BW_VERTEX_FOG(o)

	return o;
}

//--------------------------------------------------------------------------------------------------
float4 ps_reflection_3_0(OutputDiffuseLighting i, uniform bool alphaTest) : COLOR0
{
	//-- lambert equation.
	half4 diffuse = BW_DIFFUSE_COLOR;

	//-- compile-time branching.
	if (alphaTest)
	{
		clip(diffuse.a - alphaReference / 255.0h);
	}

	//--
	half3 normal = normalize(i.normal);
    half3 color  = diffuse.rgb * (sunAmbientTerm().rgb + sunDiffuseTerm(normal).rgb);

#ifdef USES_SPEC_MAP
	half specular = g_specularParams.x * luminance(tex2D(specularSampler, i.tc.xy).rgb);
	color		 += specular * sunSpecTerm(normal, normalize(g_cameraPos - i.worldPos), g_specularParams.y).rgb;
#endif

	//-- fog.
	color = applyFogTo(color, i.fog);
	
	return float4(color, 0);
}

//--------------------------------------------------------------------------------------------------
VS_CASTER_OUTPUT_ALPHA_TESTED vs_shadows_3_0(VERTEX_FORMAT i)
{
	VS_CASTER_OUTPUT_ALPHA_TESTED o = (VS_CASTER_OUTPUT_ALPHA_TESTED) 0;
	BW_SHADOW_CAST_PROJECT_POSITION(o);
	BW_SHADOWS_CALCULATE_UVS(o)

	o.depth = o.pos.zw;
	return o;
}

//--------------------------------------------------------------------------------------------------
VS_CASTER_OUTPUT_ALPHA_TESTED vs_instanced_shadows_3_0(VERTEX_FORMAT i, InstancingStream instance)
{
	VS_CASTER_OUTPUT_ALPHA_TESTED o = (VS_CASTER_OUTPUT_ALPHA_TESTED) 0;
	BW_INSTANCING_SHADOW_CAST_PROJECT_POSITION(o);
	BW_SHADOWS_INSTANCING_CALCULATE_UVS(o)

	o.depth = o.pos.zw;
	return o;
}

//--------------------------------------------------------------------------------------------------
float4 ps_shadows_3_0(VS_CASTER_OUTPUT_ALPHA_TESTED i, uniform bool alphaTest) : COLOR0
{
	//-- compile-time branching.
	if (alphaTest)
	{
#if DUAL_UV
		half alpha1 = tex2D(diffuseSampler, i.tc.xy).w;
		half alpha2 = tex2D(diffuseSampler2, i.tc2.xy).w;
		half alpha  = alpha1 * alpha2;
#else
		half alpha  = tex2D(diffuseSampler, i.tc.xy).w;
#endif
		//--
		clip(alpha - alphaReference / 255.0h);
	}

    return i.depth.x / i.depth.y;
}

//--
PixelShader compiled_ps_deferred_3_0[] = {
	compile ps_3_0 ps_deferred_3_0(false),
	compile ps_3_0 ps_deferred_3_0(true)
};

//--
PixelShader compiled_ps_reflection_3_0[] = {
	compile ps_3_0 ps_reflection_3_0(false),
	compile ps_3_0 ps_reflection_3_0(true)
};

//--
PixelShader compiled_ps_shadows_3_0[] = {
	compile ps_3_0 ps_shadows_3_0(false),
	compile ps_3_0 ps_shadows_3_0(true)
};

//--------------------------------------------------------------------------------------------------
#else //-- BW_DEFERRED_SHADING

//--------------------------------------------------------------------------------------------------
struct OutputDiffuseLighting
{
	float4 pos		:	POSITION;
	float2 tc		:	TEXCOORD0;
#if DUAL_UV
	float2 tc2		:	TEXCOORD1;
#endif
	float3 normal	:	TEXCOORD2;
	float4 worldPos	:	TEXCOORD3;
	float  fog		:	FOG;
};

//--------------------------------------------------------------------------------------------------
OutputDiffuseLighting vs_main_2_0(VERTEX_FORMAT i)
{
	OutputDiffuseLighting o = (OutputDiffuseLighting)0;

	BW_PROJECT_POSITION(o)
	BW_CALCULATE_UVS(o)
	BW_VERTEX_FOG(o)

	return o;
}

//--------------------------------------------------------------------------------------------------
float4 ps_main_2_0(OutputDiffuseLighting i, uniform bool alphaTest) : COLOR0
{
	half4 diffuse = BW_DIFFUSE_COLOR;

	//-- compile-time branching.
	if (alphaTest)
	{
		clip(diffuse.a - alphaReference / 255.0h);
	}

	//--
	half3 normal = normalize(i.normal);
	half3 color  = diffuse.rgb * (sunAmbientTerm().rgb + sunDiffuseTerm(normal).rgb);

#ifdef USES_SPEC_MAP
	half specular = g_specularParams.x * luminance(tex2D(specularSampler, i.tc.xy));
	color.rgb     += specular * sunSpecTerm(normal, normalize(g_cameraPos - i.worldPos), g_specularParams.y).rgb;
#endif

	return float4(color, diffuse.a);
}

//--
PixelShader compiled_ps_main_2_0[] = {
	compile ps_2_0 ps_main_2_0(false),
	compile ps_2_0 ps_main_2_0(true)
};

#endif //-- BW_DEFERRED_SHADING

#endif //-- LIGHTONLY_FXH

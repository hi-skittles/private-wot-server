#ifndef NORMALMAP_2_0_FXH
#define NORMALMAP_2_0_FXH

#ifdef COLOURISE_DIFFUSE_TEXTURE
#include "colourise_diffuse_texture.fxh"
#endif

//-- common part of pixel shader.
//--------------------------------------------------------------------------------------------------
#if DUAL_UV
	#define BW_DIFFUSE_COLOR	diffuseColor(i.tc, i.tc2);
#else
	#define BW_DIFFUSE_COLOR	diffuseColor(i.tc, float2(0,0));
#endif

//--------------------------------------------------------------------------------------------------
half4 diffuseColor(float2 tc, float2 tc2)
{
#if DUAL_UV
	half4 diffuseMap1 = gamma2linear(tex2D(diffuseSampler, tc.xy));
	half4 diffuseMap2 = gamma2linear(tex2D(diffuseSampler2, tc2.xy));
	half4 diffuseMap  = half4(diffuseMap1.rgb * diffuseMap2.rgb, diffuseMap1.a * diffuseMap2.a);
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
BW_DS_VS_BUMP_OUT vs_deferred_3_0(BUMPED_VERTEX_FORMAT i)
{
	BW_DS_VS_BUMP_OUT o = (BW_DS_VS_BUMP_OUT)0;

	BW_DS_PROJECT_POSITION(o)
	BW_DS_CALCULATE_UVS(o)
	BW_DS_CALCULATE_TS_MATRIX(o)

	return o;
}

//--------------------------------------------------------------------------------------------------
BW_DS_VS_BUMP_OUT vs_instanced_deferred_3_0(BUMPED_VERTEX_FORMAT i, InstancingStream instance)
{
	BW_DS_VS_BUMP_OUT o = (BW_DS_VS_BUMP_OUT)0;

	BW_DS_INSTANCING_PROJECT_POSITION(o)
	BW_DS_INSTANCING_CALCULATE_UVS(o)
	BW_DS_INSTANCING_CALCULATE_TS_MATRIX(o)

	return o;
}

//--------------------------------------------------------------------------------------------------
G_BUFFER_LAYOUT ps_deferred_3_0(BW_DS_VS_BUMP_OUT i, uniform bool alphaTest)
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
#endif //-- USES_SPEC_MAP
	
	//-- calculate world space normal.
	half3    nn   = tex2D(normalSampler, i.tc.xy).xyz * 2 - 1;
	half3x3 TBN   = half3x3(i.tangent, i.binormal, i.normal);
	half3  normal = mul(nn.xyz, TBN);

	g_buffer_writeDepth(o, i.linerZ);
	g_buffer_writeNormal(o, normal);
	g_buffer_writeObjectKind(o, g_objectID ? G_OBJECT_KIND_DYNAMIC : G_OBJECT_KIND_STATIC);

	return o;
}

//--------------------------------------------------------------------------------------------------
struct OutputNormalMap
{
	float4 pos		:	POSITION;
	float4 tc		:	TEXCOORD0;
#if DUAL_UV
	float2 tc2		:	TEXCOORD1;
#endif
	float3 normal	:	TEXCOORD2;
	float3 tangent	:	TEXCOORD3;
	float3 binormal	:	TEXCOORD4;
	float4 worldPos	:	TEXCOORD5;
	float  fog		:	TEXCOORD6;
};

//--------------------------------------------------------------------------------------------------
OutputNormalMap vs_reflection_3_0(BUMPED_VERTEX_FORMAT i)
{
	OutputNormalMap o = (OutputNormalMap)0;

	BW_PROJECT_POSITION(o)
	BW_CALCULATE_UVS(o)
	BW_CALCULATE_TS_MATRIX(o)
	BW_VERTEX_FOG(o)

	return o;
}

//--------------------------------------------------------------------------------------------------
OutputNormalMap vs_instanced_reflection_3_0(BUMPED_VERTEX_FORMAT i, InstancingStream instance)
{
	OutputNormalMap o = (OutputNormalMap)0;

	BW_INSTANCING_PROJECT_POSITION(o)
	BW_INSTANCING_CALCULATE_UVS(o)
	BW_INSTANCING_CALCULATE_TS_MATRIX(o)
	BW_VERTEX_FOG(o)

	return o;
}

//--------------------------------------------------------------------------------------------------
float4 ps_reflection_3_0(OutputNormalMap i, uniform bool alphaTest) : COLOR
{
	//--  output constant color:
	half4 diffuse = BW_DIFFUSE_COLOR;

	//-- compile time-branching.
	if (alphaTest)
	{
		clip(diffuse.a - alphaReference / 255.0h);
	}

	half3 nn	  = tex2D(normalSampler, i.tc.xy) * 2 - 1;
	half3x3 TBN   = half3x3(i.tangent, i.binormal, i.normal);
	half3  normal = normalize(mul(nn.xyz, TBN));

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
	if (alphaTest)
	{
	#if DUAL_UV
		half alpha1 = tex2D(diffuseSampler, i.tc.xy).w;
		half alpha2 = tex2D(diffuseSampler2, i.tc2.xy).w;
		half alpha  = alpha1 * alpha2;
	#else
		half alpha  = tex2D(diffuseSampler, i.tc.xy).w;
	#endif	

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
#else

//--------------------------------------------------------------------------------------------------
struct OutputNormalMap
{
	float4 pos		:	POSITION;
	float4 tc		:	TEXCOORD0;
#if DUAL_UV
	float2 tc2		:	TEXCOORD1;
#endif
	float3 normal	:	TEXCOORD2;
	float3 tangent	:	TEXCOORD3;
	float3 binormal	:	TEXCOORD4;
	float4 worldPos	:	TEXCOORD5;
	float fog		:	FOG;
};

//--------------------------------------------------------------------------------------------------
OutputNormalMap vs_main_2_0(BUMPED_VERTEX_FORMAT i)
{
	OutputNormalMap o = (OutputNormalMap)0;

	BW_PROJECT_POSITION(o)
	BW_VERTEX_FOG(o)
	BW_CALCULATE_UVS(o)
	BW_CALCULATE_TS_MATRIX(o)

	return o;
}

//--------------------------------------------------------------------------------------------------
float4 ps_main_2_0(OutputNormalMap i, uniform bool alphaTest) : COLOR
{
	//--  output constant color:
	half4 diffuse = BW_DIFFUSE_COLOR;

	//-- compile-time branching.
	if (alphaTest)
	{
		clip(diffuse.a - alphaReference / 255.0h);
	}

	half3 nn	  = tex2D(normalSampler, i.tc.xy) * 2 - 1;
	half3x3 TBN   = half3x3(i.tangent, i.binormal, i.normal);
	half3  normal = normalize(mul(nn.xyz, TBN));

	half4 color = half4(0,0,0,0);
	color.rgb = diffuse.rgb * (sunAmbientTerm() + sunDiffuseTerm(normal));
	color.a	  = diffuse.a;

#ifdef USES_SPEC_MAP
	half specular = g_specularParams.x * luminance(tex2D(specularSampler, i.tc.xy).rgb);
	color.rgb    += specular * sunSpecTerm(normal, normalize(g_cameraPos.xyz - i.worldPos), g_specularParams.y);
#endif //-- USES_SPEC_MAP

	return color;
}

//--
PixelShader compiled_ps_main_2_0[] = {
	compile ps_2_0 ps_main_2_0(false),
	compile ps_2_0 ps_main_2_0(true)
};

#endif //-- BW_DEFERRED_SHADING

#endif //-- NORMALMAP_2_0_FXH

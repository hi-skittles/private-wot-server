#ifndef LIGHTONLY_2UV_FXH
#define LIGHTONLY_2UV_FXH

BW_ARTIST_EDITABLE_DIFFUSE_MAP
BW_ARTIST_EDITABLE_DOUBLE_SIDED
BW_ARTIST_EDITABLE_ALPHA_TEST
BW_ARTIST_EDITABLE_MOD2X
BW_ARTIST_EDITABLE_TEXTURE_OP

sampler diffuseSampler = BW_SAMPLER(diffuseMap, BW_TEX_ADDRESS_MODE)

//-- colorise.
#ifdef COLOURISE_DIFFUSE_TEXTURE
	#include "colourise_diffuse_texture.fxh"
#endif

//-- spec map.
#ifdef USES_SPEC_MAP
	#include "specmap.fxh"
#endif

//--------------------------------------------------------------------------------------------------
#if BW_DEFERRED_SHADING

#include "write_g_buffer.fxh"

//--------------------------------------------------------------------------------------------------
BW_DS_VS_DIFFUSE2_OUT vs_deferred_3_0(VERTEX_FORMAT i)
{
	BW_DS_VS_DIFFUSE2_OUT o = (BW_DS_VS_DIFFUSE2_OUT)0;

	BW_DS_PROJECT_POSITION(o)
	BW_DS_CALCULATE_UVS(o)

	return o;
}

//--------------------------------------------------------------------------------------------------
BW_DS_VS_DIFFUSE2_OUT vs_instanced_deferred_3_0(VERTEX_FORMAT i, InstancingStream instance)
{
	BW_DS_VS_DIFFUSE2_OUT o = (BW_DS_VS_DIFFUSE2_OUT)0;

	BW_DS_INSTANCING_PROJECT_POSITION(o)
	BW_DS_INSTANCING_CALCULATE_UVS(o)

	return o;
}

//--------------------------------------------------------------------------------------------------
G_BUFFER_LAYOUT ps_deferred_3_0(BW_DS_VS_DIFFUSE2_OUT i, uniform bool alphaTest)
{
	G_BUFFER_LAYOUT o = (G_BUFFER_LAYOUT)0;

	half4 diffuseMap = gamma2linear(tex2D(diffuseSampler, i.tc.xy));

	//-- compile-time branching.
	if (alphaTest)
	{
		clip(diffuseMap.a - alphaReference / 255.0h);
	}

	half4 otherMap = gamma2linear(tex2D(otherSampler, i.tc2.xy));
	half3 color	   = bwTextureOp((textureOperation), diffuseMap.rgb, diffuseMap.w, diffuseMap, otherMap);

	g_buffer_writeAlbedo(o, color.xyz);

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
struct OutputDiffuseLighting2
{
	float4 pos		:	POSITION;
	float2 tc		:	TEXCOORD0;
	float2 tc2		:	TEXCOORD1;
	float3 normal	:	TEXCOORD2;
	float4 worldPos	:	TEXCOORD3;
	float  fog		:	TEXCOORD4;
};

//--------------------------------------------------------------------------------------------------
OutputDiffuseLighting2 vs_reflection_3_0(VERTEX_FORMAT i)
{
	OutputDiffuseLighting2 o = (OutputDiffuseLighting2)0;

	BW_PROJECT_POSITION(o)
	BW_CALCULATE_UVS(o)
	BW_VERTEX_FOG(o)

	return o;
}

//--------------------------------------------------------------------------------------------------
OutputDiffuseLighting2 vs_instanced_reflection_3_0(VERTEX_FORMAT i, InstancingStream instance)
{
	OutputDiffuseLighting2 o = (OutputDiffuseLighting2)0;

	BW_INSTANCING_PROJECT_POSITION(o)
	BW_INSTANCING_CALCULATE_UVS(o)
	BW_VERTEX_FOG(o)

	return o;
}

//--------------------------------------------------------------------------------------------------
float4 ps_reflection_3_0(OutputDiffuseLighting2 i, uniform bool alphaTest) : COLOR0
{
	half4 diffuseMap = gamma2linear(tex2D(diffuseSampler, i.tc.xy));

	//-- compile-time branching.
	if (alphaTest)
	{
		clip(diffuseMap.a - alphaReference / 255.0h);
	}

	half4 otherMap = gamma2linear(tex2D(otherSampler, i.tc2.xy));
	half3 color    = bwTextureOp((textureOperation), diffuseMap.rgb, diffuseMap.a, diffuseMap, otherMap);

	//--
	half3 normal = normalize(i.normal);

    color = diffuseMap.rgb * (sunAmbientTerm() + sunDiffuseTerm(normal));

#ifdef USES_SPEC_MAP
	half specular = g_specularParams.x * luminance(tex2D(specularSampler, i.tc.xy).rgb);
	color		 += specular * sunSpecTerm(normal, normalize(g_cameraPos - i.worldPos), g_specularParams.y);
#endif

	//-- fog
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
		half alpha = tex2D(diffuseSampler, i.tc.xy).a;
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
struct OutputDiffuseLighting2
{
	float4 pos		:	POSITION;
	float2 tc		:	TEXCOORD0;
	float2 tc2		:	TEXCOORD1;
	float3 normal	:	TEXCOORD2;
	float4 worldPos	:	TEXCOORD3;
	float  fog		:	FOG;
};


//--------------------------------------------------------------------------------------------------
OutputDiffuseLighting2 vs_main_2_0(VERTEX_FORMAT i) 
{
	OutputDiffuseLighting2 o = (OutputDiffuseLighting2)0;

	BW_PROJECT_POSITION(o)
	BW_CALCULATE_UVS(o)
	BW_VERTEX_FOG(o)

	return o;
}

//--------------------------------------------------------------------------------------------------
float4 ps_main_2_0(OutputDiffuseLighting2 i, uniform bool alphaTest) : COLOR0
{
	half4 diffuseMap = gamma2linear(tex2D(diffuseSampler, i.tc.xy));

	//-- compile-time branching.
	if (alphaTest)
	{
		clip(diffuseMap.a - alphaReference / 255.0h);
	}

	half4 otherMap = gamma2linear(tex2D(otherSampler, i.tc2.xy));
	half3 color    = bwTextureOp((textureOperation), diffuseMap.rgb, diffuseMap.a, diffuseMap, otherMap);

	//--
	half3 normal = normalize(i.normal);

	half3 o = color * (sunAmbientTerm() + sunDiffuseTerm(normal));

#ifdef USES_SPEC_MAP
	half specular = g_specularParams.x * luminance(tex2D(specularSampler, i.tc.xy));
	o += specular * sunSpecTerm(normal, normalize(g_cameraPos - i.worldPos), g_specularParams.y);
#endif		

	return float4(o, diffuseMap.a);
}

//--
PixelShader compiled_ps_main_2_0[] = {
	compile ps_2_0 ps_main_2_0(false),
	compile ps_2_0 ps_main_2_0(true)
};

#endif //-- BW_DEFERRED_SHADING

#endif //-- LIGHTONLY_2UV_FXH
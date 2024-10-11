#ifndef MESH_PARTICLE_INCLUDE_FXH
#define MESH_PARTICLE_INCLUDE_FXH

//--------------------------------------------------------------------------------------------------
BW_ARTIST_EDITABLE_ALPHA_TEST
BW_ARTIST_EDITABLE_DIFFUSE_MAP
BW_ARTIST_EDITABLE_DOUBLE_SIDED
BW_ARTIST_EDITABLE_ADDRESS_MODE(BW_WRAP)

sampler diffuseSampler = BW_SAMPLER(diffuseMap, BW_TEX_ADDRESS_MODE)

//--------------------------------------------------------------------------------------------------
float4 g_world[45] : WorldPalette;	//-- 15 is MAX_MESHES, and matrices are 3 float4s
float4 g_tint[15]  : TintPalette;


//-- normal -> world normal and 1-bone skinning
//--------------------------------------------------------------------------------------------------
float3 transformNormal(float4 world[45], float3 v, int index)
{
	float3 ret;
	ret.x = dot(world[index + 0].xyz, v);
	ret.y = dot(world[index + 1].xyz, v);
	ret.z = dot(world[index + 2].xyz, v);
	return normalize(ret);
}

//-- pos -> world pos and 1-bone skinning
//--------------------------------------------------------------------------------------------------
float3 transformPos(float4 world[45], float4 pos, int index)
{
	float3 ret;
	ret.x = dot(world[index + 0], pos);
	ret.y = dot(world[index + 1], pos);
	ret.z = dot(world[index + 2], pos);
	return ret;
}

//--------------------------------------------------------------------------------------------------
#if BW_DEFERRED_SHADING

#include "write_g_buffer.fxh"

//--------------------------------------------------------------------------------------------------
struct ColorVS2PS
{
	float4 pos			:	POSITION;
	float3 tcLinearZ	:	TEXCOORD0;
	float3 normal		:	TEXCOORD1;
	float4 tint			:	TEXCOORD2;
};

//--------------------------------------------------------------------------------------------------
ColorVS2PS vs_deferred_3_0(VertexXYZNUVI i)
{
	ColorVS2PS o = (ColorVS2PS)0;

	float3 wPos	= transformPos(g_world, i.pos, i.index);
	o.normal	= transformNormal(g_world, BW_UNPACK_VECTOR(i.normal), i.index);
	o.pos		= mul(float4(wPos, 1), g_viewProjMat);
	o.tcLinearZ	= float3(BW_UNPACK_TEXCOORD(i.tc), o.pos.w);
	o.tint		= g_tint[i.index / 3];

	return o;
}

//--------------------------------------------------------------------------------------------------
G_BUFFER_LAYOUT ps_deferred_3_0(ColorVS2PS i)
{
	G_BUFFER_LAYOUT o = (G_BUFFER_LAYOUT)0;

	half4 color = tex2D(diffuseSampler, i.tcLinearZ.xy) * (half4)i.tint;

	//--
	clip(color.a - 0.25h);

	g_buffer_writeAlbedo(o, color.rgb);
	g_buffer_writeDepth(o, i.tcLinearZ.z);
	g_buffer_writeNormal(o, i.normal);
	g_buffer_writeObjectKind(o, G_OBJECT_KIND_DYNAMIC);

	return o;
}

//--------------------------------------------------------------------------------------------------
struct ShadowsVS2PS
{
	float4 pos		:	POSITION;
	float4 tcDepth	:	TEXCOORD0;
	float4 tint		:	TEXCOORD2;
};

//--------------------------------------------------------------------------------------------------
ShadowsVS2PS vs_shadows_3_0(VertexXYZNUVI i)
{
	ShadowsVS2PS o = (ShadowsVS2PS)0;

	float3 wPos	= transformPos(g_world, i.pos, i.index);
	o.pos		= mul(float4(wPos, 1), g_viewProjMat);
	o.tcDepth	= float4(BW_UNPACK_TEXCOORD(i.tc), o.pos.zw);
	o.tint		= g_tint[i.index / 3];

	return o;
}

//--------------------------------------------------------------------------------------------------
float4 ps_shadows_3_0(ShadowsVS2PS i) : COLOR0
{
	half alpha = tex2D(diffuseSampler, i.tcDepth.xy).a * (half)i.tint.a;

	//--
	clip(alpha - 0.25h);

	return i.tcDepth.z / i.tcDepth.w;
}

//--------------------------------------------------------------------------------------------------
struct ReflectionVS2PS
{
	float4 pos		:	POSITION;
	float3 tcFog	:	TEXCOORD0;
	float3 normal	:	TEXCOORD2;
	float4 tint		:	TEXCOORD4;
};

//--------------------------------------------------------------------------------------------------
ReflectionVS2PS vs_reflection_3_0(VertexXYZNUVI i)
{
	ReflectionVS2PS o = (ReflectionVS2PS)0;

	float3 wPos	= transformPos(g_world, i.pos, i.index);
	o.normal	= transformNormal(g_world, BW_UNPACK_VECTOR(i.normal), i.index);
	o.pos		= mul(float4(wPos, 1), g_viewProjMat);
	o.tcFog.xy	= BW_UNPACK_TEXCOORD(i.tc);
	o.tcFog.z	= bw_vertexFog(float4(wPos, 1), o.pos.w);
	o.tint		= g_tint[i.index / 3];

	return o;
}

//--------------------------------------------------------------------------------------------------
float4 ps_reflection_3_0(ReflectionVS2PS i) : COLOR0
{
	half4 diffuseMap = tex2D(diffuseSampler, i.tcFog.xy) * (half4)i.tint;
	half3 o		     = diffuseMap.rgb * (sunAmbientTerm() + sunDiffuseTerm(normalize(i.normal)));
	o				 = applyFogTo(o, i.tcFog.z);

	return float4(o, diffuseMap.a);
}

#else

//--------------------------------------------------------------------------------------------------
struct VS2PS
{
	float4 pos		:	POSITION;
	float2 tc		:	TEXCOORD0;
	float3 normal	:	TEXCOORD2;
	float4 worldPos	:	TEXCOORD3;
	float4 tint		:	TEXCOORD4;
	float  fog		:	FOG;
};

//--------------------------------------------------------------------------------------------------
VS2PS vs_main_2_0(VertexXYZNUVI i)
{
	VS2PS o = (VS2PS)0;

	float3 wPos	= transformPos(g_world, i.pos, i.index);
	o.normal	= transformNormal(g_world, BW_UNPACK_VECTOR(i.normal), i.index);
	o.pos		= mul(float4(wPos, 1), g_viewProjMat);
	o.tc		= BW_UNPACK_TEXCOORD(i.tc);
	o.tint		= g_tint[i.index / 3];
	o.fog		= bw_vertexFog(float4(wPos, 1), o.pos.w);

	return o;
}

//--------------------------------------------------------------------------------------------------
float4 ps_main_2_0(VS2PS i) : COLOR
{
	half4 diffuseMap = tex2D(diffuseSampler, i.tc) * (half4)i.tint;
	half3 o		     = diffuseMap.rgb * (sunAmbientTerm() + sunDiffuseTerm(normalize(i.normal)));
	return float4(o, diffuseMap.a);
}

#endif //-- BW_DEFERRED_SHADING
#endif //-- MESH_PARTICLE_INCLUDE_FXH
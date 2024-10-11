#ifndef UNSKINNED_PROJECTION_HELPERS_FXH
#define UNSKINNED_PROJECTION_HELPERS_FXH

#include "uv.fxh"

//--------------------------------------------------------------------------------------------------
float4x4 g_world	: World;
float	 g_objectID	: ObjectID;

//--------------------------------------------------------------------------------------------------
float3 transformPos( float4x4 world, float4 pos )
{
	float3 ret = {	dot( world[0], pos ), dot( world[1], pos ), dot( world[2], pos )	};
	return ret;
}

//--------------------------------------------------------------------------------------------------
float3 transformNormaliseVector( float4x4 world, float3 v )
{
	float3 ret;
	ret = mul( v, (float3x3)world );	
	return normalize( ret );
}

//--------------------------------------------------------------------------------------------------
float3x3 worldSpaceTSMatrix( in float4x4 world, in float3 tangent, in float3 binormal, in float3 worldNormal )
{	
	float3 worldTangent  = transformNormaliseVector(world, BW_UNPACK_VECTOR(tangent ));
	float3 worldBinormal = transformNormaliseVector(world, BW_UNPACK_VECTOR(binormal));
	
	float3x3 tsMatrix = { worldTangent, worldBinormal, worldNormal };
	return tsMatrix;
}

//--------------------------------------------------------------------------------------------------
float4 unskinnedTransform( in float4 pos, in float3 normal, in float4x4 world, in float4x4 viewProj, out float4 worldPos, out float3 worldNormal )
{	
	worldPos = mul(pos, world);
	worldNormal = transformNormaliseVector( world, BW_UNPACK_VECTOR(normal) );
	
	float4 projPos = mul(worldPos, viewProj);
	return projPos;
}

//-- Deferred shading.
//--------------------------------------------------------------------------------------------------

//--------------------------------------------------------------------------------------------------
#define BW_DS_PROJECT_POSITION(o)																\
	float4 worldPos;																			\
	o.pos = unskinnedTransform(i.pos, i.normal, g_world, g_viewProjMat, worldPos, o.normal);	\
	o.linerZ = o.pos.w;

//--------------------------------------------------------------------------------------------------
#define BW_DS_CALCULATE_TS_MATRIX(o)	BW_CALCULATE_TS_MATRIX(o)

//--------------------------------------------------------------------------------------------------
#define BW_DS_INSTANCING_PROJECT_POSITION(o)													\
	float4   worldPos;																			\
	float4x4 worldMat = {instance.v0, instance.v1, instance.v2, instance.v3};					\
	o.pos = unskinnedTransform(i.pos, i.normal, worldMat, g_viewProjMat, worldPos, o.normal);	\
	o.linerZ = o.pos.w;

//--------------------------------------------------------------------------------------------------
#define BW_DS_INSTANCING_CALCULATE_TS_MATRIX(o)													\
	float3x3 tsMatrix = worldSpaceTSMatrix(worldMat, i.tangent, i.binormal, o.normal);			\
	o.tangent  = tsMatrix[0];																	\
	o.binormal = tsMatrix[1];																	\
	o.normal   = tsMatrix[2];

//-- Shadows.
//--------------------------------------------------------------------------------------------------

//--------------------------------------------------------------------------------------------------

//--------------------------------------------------------------------------------------------------
#define BW_SHADOW_CAST_PROJECT_POSITION(o)														\
	float4 worldPos;																			\
	float3 worldNormal;																			\
	o.pos = unskinnedTransform(i.pos, i.normal, g_world, g_viewProjMat, worldPos, worldNormal);

//--------------------------------------------------------------------------------------------------
#define BW_INSTANCING_SHADOW_CAST_PROJECT_POSITION(o)											\
	float4 worldPos;																			\
	float3 worldNormal;																			\
	float4x4 worldMat = {instance.v0, instance.v1, instance.v2, instance.v3};					\
	o.pos = unskinnedTransform(i.pos, i.normal, worldMat, g_viewProjMat, worldPos, worldNormal);

//-- Forward shading.
//--------------------------------------------------------------------------------------------------

//--------------------------------------------------------------------------------------------------
#define BW_PROJECT_POSITION(o)																	\
	o.pos = unskinnedTransform(i.pos, i.normal, g_world, g_viewProjMat, o.worldPos, o.normal);

//--------------------------------------------------------------------------------------------------
#define BW_CALCULATE_TS_MATRIX(o)																\
	float3x3 tsMatrix = worldSpaceTSMatrix(g_world, i.tangent, i.binormal, o.normal);			\
	o.tangent  = tsMatrix[0];																	\
	o.binormal = tsMatrix[1];																	\
	o.normal   = tsMatrix[2];

//--------------------------------------------------------------------------------------------------
#define BW_INSTANCING_PROJECT_POSITION(o)														\
	float4x4 worldMat = {instance.v0, instance.v1, instance.v2, instance.v3};					\
	o.pos = unskinnedTransform(i.pos, i.normal, worldMat, g_viewProjMat, o.worldPos, o.normal);

//--------------------------------------------------------------------------------------------------
#define BW_INSTANCING_CALCULATE_TS_MATRIX(o)													\
	float3x3 tsMatrix = worldSpaceTSMatrix(worldMat, i.tangent, i.binormal, o.normal);			\
	o.tangent  = tsMatrix[0];																	\
	o.binormal = tsMatrix[1];																	\
	o.normal   = tsMatrix[2];

//--------------------------------------------------------------------------------------------------
#if DUAL_UV
#	define VERTEX_FORMAT		VertexXYZNUV2
#	define BUMPED_VERTEX_FORMAT	VertexXYZNUV2TB
#elif VERTEX_COLOURS
#	define VERTEX_FORMAT		VertexXYZNDUV
#	define BUMPED_VERTEX_FORMAT	VertexXYZNDUVTB
#else
#	define VERTEX_FORMAT		VertexXYZNUV
#	define BUMPED_VERTEX_FORMAT	VertexXYZNUVTB
#endif

#endif //-- UNSKINNED_PROJECTION_HELPERS_FXH

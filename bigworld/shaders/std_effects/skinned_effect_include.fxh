#ifndef SKINNED_PROJECTION_HELPERS_FXH
#define SKINNED_PROJECTION_HELPERS_FXH

#include "uv.fxh"

//--------------------------------------------------------------------------------------------------
float4	g_world[51] : WorldPalette;
float	g_objectID	: ObjectID;

// This value is the scale factor for indices passed in through the color semantic.
// This value is defined as 256.5 so that 8-series nvidia cards will scale up the values
// correctly as well as it appears the 8-series nvidia cards use 256 as the divisor for
// the colour values in shader model 1 whereas most other cards use 255. Having the value
// defined as 256.05 gives us enough precision to have ~ 56 matrices in the palette.
//--------------------------------------------------------------------------------------------------
const float INDEX_SCALE_FACTOR = 256.5;

//--------------------------------------------------------------------------------------------------
float3 transformPos( float4 world[51], float4 pos, int index )
{
	float3 ret = {	dot( world[index], pos ),
					dot( world[index + 1], pos ),
					dot( world[index + 2], pos ) };
	return ret;
}

//--------------------------------------------------------------------------------------------------
float4 transformPos( float4 world[51], float4 pos, float weights[3], int indices[3] )
{
	float4 ret = float4( 0, 0, 0, 1 );
	ret.xyz = transformPos( world, pos, indices[0] ) * weights[0];
	ret.xyz += transformPos( world, pos, indices[1] ) * weights[1];
	ret.xyz += transformPos( world, pos, indices[2] ) * weights[2];
	return ret;
}

//--------------------------------------------------------------------------------------------------
float3 transformNormaliseVector( float4 world[51], float3 v, int index )
{
	float3 ret;
	ret.x = dot( world[index + 0].xyz, v  );
	ret.y = dot( world[index + 1].xyz, v );
	ret.z = dot( world[index + 2].xyz, v );
	return normalize( ret );
}

//--------------------------------------------------------------------------------------------------
float3x3 worldSpaceTSMatrix( in float4 world[51], in int idx, in float3 tangent, in float3 binormal, in float3 worldNormal )
{	
	float3 worldTangent  = transformNormaliseVector(world, BW_UNPACK_VECTOR(tangent) , idx);
	float3 worldBinormal = transformNormaliseVector(world, BW_UNPACK_VECTOR(binormal), idx);
	
	float3x3 tsMatrix = { worldTangent, worldBinormal, worldNormal };
	return tsMatrix;
}

//--------------------------------------------------------------------------------------------------
void calculateSkinningIndices( in float3 idcs, out int indices[3] )
{
	indices[0] = idcs.x * INDEX_SCALE_FACTOR;
	indices[1] = idcs.y * INDEX_SCALE_FACTOR;
	indices[2] = idcs.z * INDEX_SCALE_FACTOR;
}

//--------------------------------------------------------------------------------------------------
float4 skinnedTransform( in float4 pos, in float3 normal, in float3 idcs, in float2 wts, float4 world[51], float4x4 viewProj, out int indices[3], out float4 worldPos, out float3 worldNormal )
{
    calculateSkinningIndices( idcs, indices );
	
	float weights[3] = {wts.x, wts.y, 1 - wts.y - wts.x };
	
	worldPos = transformPos( world, pos, weights, indices );	
	worldNormal = transformNormaliseVector( world, BW_UNPACK_VECTOR(normal), indices[0] );
	
	float4 projPos = mul(worldPos, viewProj);
	return projPos;	
}

//-- Deferred shading.
//--------------------------------------------------------------------------------------------------

//--------------------------------------------------------------------------------------------------
#define BW_DS_PROJECT_POSITION(o)																	\
	int indices[3];																					\
	float4 worldPos;																				\
	o.pos = skinnedTransform(i.pos, i.normal, i.indices, i.weights, g_world, g_viewProjMat, indices, worldPos, o.normal);\
	o.linerZ = o.pos.w;

//--------------------------------------------------------------------------------------------------
#define BW_DS_CALCULATE_TS_MATRIX(o)	BW_CALCULATE_TS_MATRIX(o)

//--------------------------------------------------------------------------------------------------
#define	BW_DS_INSTANCING_PROJECT_POSITION(o)
#define BW_DS_INSTANCING_CALCULATE_TS_MATRIX(o)
#define	BW_DS_INSTANCING_CALCULATE_UVS(o)

//-- Shadows.
//--------------------------------------------------------------------------------------------------

//--------------------------------------------------------------------------------------------------
#define BW_SHADOW_CAST_PROJECT_POSITION(o)														\
	int indices[3];																				\
	float4 worldPos;																			\
	float3 worldNormal;																			\
	o.pos = skinnedTransform(i.pos, i.normal, i.indices, i.weights, g_world, g_viewProjMat, indices, worldPos, worldNormal);

//--------------------------------------------------------------------------------------------------
#define BW_INSTANCING_SHADOW_CAST_PROJECT_POSITION(o)

//-- Forward shading.
//--------------------------------------------------------------------------------------------------

//--------------------------------------------------------------------------------------------------
#define BW_PROJECT_POSITION(o)																		\
	int indices[3];																					\
	o.pos = skinnedTransform(i.pos, i.normal, i.indices, i.weights, g_world, g_viewProjMat, indices, o.worldPos, o.normal);

//--------------------------------------------------------------------------------------------------
#define BW_CALCULATE_TS_MATRIX(o)																	\
	float3x3 tsMatrix = worldSpaceTSMatrix(g_world, indices[0], i.tangent, i.binormal, o.normal);	\
	o.tangent  = tsMatrix[0];																		\
	o.binormal = tsMatrix[1];																		\
	o.normal   = tsMatrix[2];

//--------------------------------------------------------------------------------------------------
#define	BW_INSTANCING_PROJECT_POSITION(o)
#define BW_INSTANCING_CALCULATE_TS_MATRIX(o)
#define	BW_INSTANCING_CALCULATE_UVS(o)

//--------------------------------------------------------------------------------------------------
#if DUAL_UV
#	define VERTEX_FORMAT		VertexXYZNUV2IIIWW
#	define BUMPED_VERTEX_FORMAT	VertexXYZNUV2IIIWWTB
#elif VERTEX_COLOURS
#	define VERTEX_FORMAT		VertexXYZNDUVIIIWW
#	define BUMPED_VERTEX_FORMAT	VertexXYZNDUVIIIWWTB
#else
#	define VERTEX_FORMAT		VertexXYZNUVIIIWW
#	define BUMPED_VERTEX_FORMAT	VertexXYZNUVIIIWWTB
#endif

#endif //-- SKINNED_PROJECTION_HELPERS_FXH

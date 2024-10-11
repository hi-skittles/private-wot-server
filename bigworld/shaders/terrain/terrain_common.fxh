#include "stdinclude.fxh"

// Terrain vertex format
// -------------------------------------------------------------------------------------------------
struct TerrainVertex
{
	// The height is stored in two values 
	// one for the current lod level and 
	// one for the next one down
	float2	height	: POSITION;

	// the xz coordinate stores the gradient 
	// along the x and z axis of the terrain 
	// block, these values are used to calculate
	// the position of the vertex and projecting 
	// textures on the terrain block
	float2	xz		: TEXCOORD0;
};

//--------------------------------------------------------------------------------------------------
struct SpecularInfo
{
	float power;
	float multiplier;
	float fresnelExp;
	float fresnelConstant;
};

// -----------------------------------------------------------------------------
// Constants needed to transform the vertices
// -----------------------------------------------------------------------------

// The world transform of the terrain block
matrix world;
matrix viewProj;

// The x/z scale of the terrain block
float terrainScale;

// The lod values for this terrain block
float lodStart = 9999.f;
float lodEnd = 10000.f;

// Zero and one so we can saturate without saturate().
// See bug 22135
float zero = 0.0;
float one = 1.0;

// The specular blend value
float specularBlend = 0.5;

// Other specular values.
SpecularInfo terrain2Specular =
{ 
	60.0,  	// power
	1.04, 	// multiplier
	4.5,	// fresnelExp
	0.05	// fresnelConstant
};

// -----------------------------------------------------------------------------
// Texture definition helpers
// -----------------------------------------------------------------------------
#define USE_TERRAIN_NORMAL_MAP \
float normalMapSize = 256.f;\
texture normalMap;\
sampler normalMapSampler = sampler_state\
{\
	Texture = (normalMap);\
	ADDRESSU = CLAMP;\
	ADDRESSV = CLAMP;\
	MAGFILTER = LINEAR;\
	MINFILTER = LINEAR;\
	MIPFILTER = NONE;\
};

#define USE_TERRAIN_AO_MAP\
float aoMapSize = 256.f;\
texture aoMap;\
sampler aoMapSampler = sampler_state\
{\
	Texture = (aoMap);\
	ADDRESSU = CLAMP;\
	ADDRESSV = CLAMP;\
	MAGFILTER = LINEAR;\
	MINFILTER = LINEAR;\
	MIPFILTER = NONE;\
};

#define USE_TERRAIN_HOLES_MAP \
float holesMapSize = 128.f;\
float holesSize = 100.f;\
texture holesMap;\
sampler holesMapSampler = sampler_state\
{\
	Texture = (holesMap);\
	ADDRESSU = CLAMP;\
	ADDRESSV = CLAMP;\
	MAGFILTER = POINT;\
	MINFILTER = POINT;\
	MIPFILTER = NONE;\
};

#define USE_TERRAIN_HORIZON_MAP 
float4 rcpPenumbra : PenumbraSize = {0.1,0.1,0.1,0.1};\
float4 sunAngle : SunAngle = {0.5,0.5,0.5,0.5};\
float2 horizonShadowsBlendDistances : ShadowsBlendDistances = {0.0, 0.0}; \
float horizonMapSize = 256.f;\
texture horizonMap;\
sampler horizonMapSampler = sampler_state\
{\
	Texture = (horizonMap);\
	ADDRESSU = CLAMP;\
	ADDRESSV = CLAMP;\
	MAGFILTER = LINEAR;\
	MINFILTER = LINEAR;\
	MIPFILTER = NONE;\
};

#define USE_TERRAIN_BLEND_TEXTURE\
float blendMapSize = 256.f;\
texture blendMap;\
sampler blendMapSampler = sampler_state\
{\
	Texture = (blendMap);\
	ADDRESSU = CLAMP;\
	ADDRESSV = CLAMP;\
	MAGFILTER = LINEAR;\
	MINFILTER = (minMagFilter);\
	MIPFILTER = (mipFilter);\
	MAXANISOTROPY = (maxAnisotropy);\
};

#define TERRAIN_TEXTURE( name )\
float4 name##UProjection;\
float4 name##VProjection;\
texture name;\
sampler name##Sampler = sampler_state\
{\
	Texture = (name);\
	ADDRESSU = WRAP;\
	ADDRESSV = WRAP;\
	MAGFILTER = LINEAR;\
	MINFILTER = (minMagFilter);\
	MIPFILTER = (mipFilter);\
	MAXANISOTROPY = (maxAnisotropy);\
};\
texture name##Bump;\
sampler name##Bump##Sampler = sampler_state\
{\
	Texture = (name##Bump);\
	ADDRESSU = WRAP;\
	ADDRESSV = WRAP;\
	MAGFILTER = LINEAR;\
	MINFILTER = (minMagFilter);\
	MIPFILTER = (mipFilter);\
	MAXANISOTROPY = (maxAnisotropy);\
};

// -----------------------------------------------------------------------------
// Helper methods
// -----------------------------------------------------------------------------

// This method calculates the position of this terrain vertex in world space
// It uses the lod start and end values to calculate the geo morphing
// @param vertex the terrain vertex
// @return position in world space
float4 terrainVertexPosition( const TerrainVertex vertex )
{
	// Get the position on the xz plane
	float4 position = mul( float4( vertex.xz.x * terrainScale, 0, vertex.xz.y * terrainScale, 1 ), world );
	
	// Calculate the distance from the camera on the xz plane
	float distance = length(position.xz - g_lodCameraPos.xz) * g_lodCameraPos.w;
	
	// Calculate the lod value, we linearly interpolate between the two lod distances
	// Avoid using saturate as this generates broken code in shader model 3 (bug 22135)
//	float lod = saturate( (distance - lodStart) / (lodEnd - lodStart) );
	float lod = ( (distance - lodStart) / (lodEnd - lodStart) );
	lod = max( zero, lod );
	lod = min( one, lod );

	// Calculate the new height
	float height = lerp( vertex.height.x, vertex.height.y, lod );
	
	// transform the height and add it to the position
	position.xyz += mul( float3( 0.f, height, 0.f ), world );
	
	return position;
}

// This method calculates the inclusive texture coordinate for the input dimensions
// based on the current xz coordinate. This makes sure the texture coordinates
// go from the centre of the first texel to the centre of the last texel
// @param vertex the terrain vertex
// @param dimensions the integer dimensions of the texture
// @return the uv coordinates
float2 inclusiveTextureCoordinate( const float2 vertexXZ, const float2 dimensions )
{
	// calculate the scale factor for recalculating the uvs
	float2 scale = float2( float(dimensions.x -1 ) / float( dimensions.x ) , float(dimensions.y -1 ) / float( dimensions.y ) );
	
	// calculate the offset to the middle of the first texel
	float2 offset = float2( 0.5f / float( dimensions.x ), 0.5f / float( dimensions.y ) );
	
	return vertexXZ.xy * scale + offset;
}

// This method gets the normal from the compressed normal map
half3 terrainNormal(sampler normalMapSampler, float2 normalUV)
{
    // Use swizzled normal map : Load X from alpha, Z from Green, and generate Y
    // This assumes input normal is unit length.
    half3 normal;
    normal.xy = tex2D(normalMapSampler, normalUV).ag * 2 - 1;
    normal.z  = sqrt(1 - normal.x * normal.x - normal.y * normal.y);

    // Compiler doesn't like initializing normal.xz, so we swap Y and Z
    return normal.xzy;
}

//-- gets the ambient occlusion factor.
half terrainAO(sampler aoMapSampler, float2 aoUV)
{
	return tex2D(aoMapSampler, aoUV).r;
}
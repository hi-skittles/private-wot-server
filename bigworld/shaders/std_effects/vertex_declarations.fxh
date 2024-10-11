//-- This include file has all of the vertex declarations that are passed between vertex and pixel shader.

//--------------------------------------------------------------------------------------------------

//-------------------------------------------------------------------------
// Normals packing
#if BW_GPU_VERTEX_PACKING_USE_VEC3_NORMAL_UBYTE4_8_8_8
   float3 unpackNormal(float3 src)
   {
      return (src - 127.0f) / 127.0f;
   }

   #define BW_VEC3 float3
   #define BW_UNPACK_VECTOR(packed) unpackNormal(packed)

#elif BW_GPU_VERTEX_PACKING_USE_VEC3_NORMAL_FLOAT16_X4
   #define BW_VEC3 half4
   #define BW_UNPACK_VECTOR(packed) packed.xyz

#else  //-- Default packing
   #define BW_VEC3 float3
   #define BW_UNPACK_VECTOR(packed) packed

#endif //-- Normals packing

//-------------------------------------------------------------------------
// Texcoords packing
#if BW_GPU_VERTEX_PACKING_USE_VEC2_TEXCOORD_INT16_X2
   float2 unpackTexCoord(float2 src)
   {
      return src / 2047.0f;
   }

   #define BW_VEC2 float2
   #define BW_UNPACK_TEXCOORD(packed) unpackTexCoord(packed)
   
#elif BW_GPU_VERTEX_PACKING_USE_VEC2_TEXCOORD_FLOAT16_X2
      #define BW_VEC2 half2
      #define BW_UNPACK_TEXCOORD(packed) packed

#else  //-- Default packing
      #define BW_VEC2 float2
      #define BW_UNPACK_TEXCOORD(packed) packed

#endif //-- Texcoords packing

//--------------------------------------------------------------------------------------------------
struct InstancingStream
{
	float4 v0	:	TEXCOORD4;
	float4 v1	:	TEXCOORD5;
	float4 v2	:	TEXCOORD6;
	float4 v3	:	TEXCOORD7;
};

//--------------------------------------------------------------------------------------------------
struct VertexXYZNUVIIIWWTB
{
   float4  pos:			POSITION;
   float3  indices:		BLENDINDICES;
   float2  weights:		BLENDWEIGHT;
   BW_VEC3 normal:		NORMAL;
   BW_VEC3 binormal:	BINORMAL;
   BW_VEC3 tangent:		TANGENT;
   BW_VEC2 tc:			TEXCOORD0;
};

//--------------------------------------------------------------------------------------------------
struct VertexXYZNUVIIIWW
{
   float4  pos:		POSITION;
   float3  indices:	BLENDINDICES;
   float2  weights:	BLENDWEIGHT;
   BW_VEC3 normal:	NORMAL;
   BW_VEC2 tc:		TEXCOORD0;
};

//--------------------------------------------------------------------------------------------------
struct VertexXYZNUV2IIIWW
{
   float4  pos:		POSITION;
   float3  indices:	BLENDINDICES;
   float2  weights:	BLENDWEIGHT;
   BW_VEC3 normal:	NORMAL;
   BW_VEC2 tc:		TEXCOORD0;
   BW_VEC2 tc2:		TEXCOORD1;
};

//--------------------------------------------------------------------------------------------------
struct VertexXYZNDUVIIIWW
{
   float4 pos:		POSITION;
   float3 indices:	BLENDINDICES;
   float2 weights:	BLENDWEIGHT;
   float3 normal:	NORMAL;
   float4 colour:	COLOR;
   float2 tc:		TEXCOORD0;
};

//--------------------------------------------------------------------------------------------------
struct VertexXYZNUVITB
{
   float4  pos:			POSITION;
   float   index:		BLENDINDICES;
   BW_VEC3 normal:		NORMAL;
   BW_VEC3 binormal:	BINORMAL;
   BW_VEC3 tangent:		TANGENT;
   BW_VEC2 tc:			TEXCOORD0;
};

//--------------------------------------------------------------------------------------------------
struct VertexXYZNUVI
{
   float4  pos:		POSITION;
   float   index:	BLENDINDICES;
   BW_VEC3 normal:	NORMAL;
   BW_VEC2 tc:		TEXCOORD0;
};

//--------------------------------------------------------------------------------------------------
struct VertexXYZNUVTB
{
   float4  pos:			POSITION;
   BW_VEC3 normal:		NORMAL;
   BW_VEC3 binormal:	BINORMAL;
   BW_VEC3 tangent:		TANGENT;
   BW_VEC2 tc:			TEXCOORD0;
};

//--------------------------------------------------------------------------------------------------
struct VertexXYZNUV2TB
{
   float4 pos:			POSITION;
   BW_VEC3 normal:		NORMAL;
   BW_VEC3 binormal:	BINORMAL;
   BW_VEC3 tangent:		TANGENT;
   BW_VEC2 tc:			TEXCOORD0;
   BW_VEC2 tc2:			TEXCOORD1;
};

//--------------------------------------------------------------------------------------------------
struct VertexXYZNUV
{
   float4  pos:		POSITION;
   BW_VEC3 normal:	NORMAL;
   BW_VEC2 tc:		TEXCOORD0;
};

//--------------------------------------------------------------------------------------------------
struct VertexXYZNUV2
{
   float4  pos:		POSITION;
   BW_VEC3 normal:	NORMAL;
   BW_VEC2 tc:		TEXCOORD0;
   BW_VEC2 tc2:		TEXCOORD1;
};

//--------------------------------------------------------------------------------------------------
struct VertexXYZNDUV
{
   float4 pos:		POSITION;
   float3 normal:	NORMAL;
   float4 colour:	COLOR;
   float2 tc:		TEXCOORD0;
};

//--------------------------------------------------------------------------------------------------
struct VertexXYZNDUV2
{
   float4 pos:		POSITION;
   float3 normal:	NORMAL;
   float4 colour:	COLOR;
   float2 tc:		TEXCOORD0;
   float2 tc2:		TEXCOORD1;
};

//--------------------------------------------------------------------------------------------------
struct VertexXYZL
{
   float4 pos:		POSITION;
   float4 diffuse:	COLOR;
};

//--------------------------------------------------------------------------------------------------
struct VertexXYZDUV
{
   float4 pos:		POSITION;
   float4 diffuse:	COLOR;
   float2 tc:		TEXCOORD0;
};
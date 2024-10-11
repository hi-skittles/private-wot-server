#ifndef _BW_DEFERRED_SHADING_FXH_
#define _BW_DEFERRED_SHADING_FXH_

#include "stdinclude.fxh"

//--------------------------------------------------------------------------------------------------
struct BW_DS_VS_DIFFUSE2_OUT
{
	float4 pos		: POSITION;
	float  linerZ	: TEXCOORD0;
	float2 tc		: TEXCOORD1;
	float2 tc2		: TEXCOORD2;
	float3 normal	: TEXCOORD3;
};

//--------------------------------------------------------------------------------------------------
struct BW_DS_VS_DIFFUSE_OUT
{
	float4 pos		: POSITION;
	float  linerZ	: TEXCOORD0;
	float2 tc		: TEXCOORD1;
#if DUAL_UV
	float2 tc2		: TEXCOORD2;
#endif //-- DUAL_UV
	float3 normal	: TEXCOORD3;
};

//--------------------------------------------------------------------------------------------------
struct BW_DS_VS_BUMP_OUT
{
	float4 pos		: POSITION;
	float  linerZ	: TEXCOORD0;
	float2 tc		: TEXCOORD1;
#if DUAL_UV
	float2 tc2		: TEXCOORD2;
#endif //-- DUAL_UV
	float3 normal	: TEXCOORD3;
	float3 tangent	: TEXCOORD4;
	float3 binormal	: TEXCOORD5;
};

//--------------------------------------------------------------------------------------------------
struct VS_CASTER_OUTPUT
{
	float4 pos	 : POSITION;
	float2 depth : TEXCOORD0;
};

//--------------------------------------------------------------------------------------------------
struct VS_CASTER_OUTPUT_ALPHA_TESTED
{
	float4 pos	 : POSITION;
	float2 tc	 : TEXCOORD0;
#if DUAL_UV || (defined UV_TRANSFORM_OTHER)
	float2 tc2	 : TEXCOORD1;
#endif
	float2 depth : TEXCOORD2;
};

//-- vertex layout for deferred shading's lighting pass.
//--------------------------------------------------------------------------------------------------
struct BW_DS_LIGHT_PASS_VS
{
	float4 pos	:	POSITION;
	float2 tc	:	TEXCOORD0;
};

//-- from VS to PS for deferred shading's lighting pass.
//--------------------------------------------------------------------------------------------------
struct BW_DS_LIGHT_PASS_VS2PS
{
	float4 pos	:	POSITION;
	float2 tc	:	TEXCOORD0;
};

//-- convert screen space position to texture space.
//-- I.e. from XY[screen width, screen height] -> UV[0, 1]
//--------------------------------------------------------------------------------------------------
float2 SC2TC(float2 vPos)
{
	return (vPos + float2(+0.5f, +0.5f)) * g_invScreen.zw;
}

//-- converts clip space position to texture space. I.e. from XY[-1, +1] -> UV[0, 1]
//--------------------------------------------------------------------------------------------------
float2 CS2TS(in float2 cs)
{
	return cs * float2(+0.5f, -0.5f) + float2(+0.5f, +0.5f);
}

//-- converts texture coordinates to clip space position. I.e. UV[0,1] -> XY[-1, +1]
//--------------------------------------------------------------------------------------------------
float2 TS2CS(in float2 ts)
{
	return ts * float2(-2.0f, +2.0f) + float2(+1.0f, -1.0f);
}

//--------------------------------------------------------------------------------------------------
sampler g_atan2LUTMapSml = sampler_state
{
	Texture   = <g_atan2LUTMap>;
	ADDRESSU  = CLAMP;
	ADDRESSV  = CLAMP;
	MinFilter = POINT;
	MagFilter = POINT;
};

//--------------------------------------------------------------------------------------------------
half lookup_atan2(half y, half x)
{
	return tex2Dlod(g_atan2LUTMapSml, half4(y, x, 0, 0)).x;
}

//-- from ShaderX5 "2.6 Normal Mapping without Pre-Computed Tangents".
//--------------------------------------------------------------------------------------------------
float3x3 computeTangentFrame(float3 N, float3 p, float2 uv)
{
    //-- get edge vectors of the pixel triangle
    float3 dp1  = ddx(p);
    float3 dp2  = ddy(p);
    float2 duv1 = ddx(uv);
    float2 duv2 = ddy(uv);

    //-- solve the linear system
    float3x3 M = float3x3(dp1, dp2, cross(dp1, dp2));
    float2x3 inversetransposeM = float2x3(cross(M[1], M[2]), cross(M[2], M[0]));
    float3   T = mul(float2(duv1.x, duv2.x), inversetransposeM);
    float3   B = mul(float2(duv1.y, duv2.y), inversetransposeM);

    //-- construct tangent frame 
    return float3x3(normalize(T), normalize(B), N);
}

//-- compute desired LOD for sampling based on the incoming UV coordinate and texture dimension.
//--------------------------------------------------------------------------------------------------
float computeTextureLOD(in float2 uv, in float2 texDim)
{
	uv *= texDim;
	
	float2 ddx_ = ddx(uv);
	float2 ddy_ = ddy(uv);
	float2 mag  = abs(ddx_) + abs(ddy_);
	float  lod = log2(max(mag.x, mag.y));

	return lod;
}

//-- encode a float value into 3 bytes (input value should be in the range of [0, 1])
//--------------------------------------------------------------------------------------------------
float3 packFloatToVec3(const float value)
{
	static const float  invByte  = 1.0f / 255.0f;
	static const float  max24int = 256*256*256-1;
	static const float3 bitSh    = float3(max24int/(256*256), max24int/256, max24int);
	static const float3 bitMsk   = float3(0.0, 256.0, 256.0);

	float3 decomp = floor(value * bitSh) * invByte;
	decomp -= decomp.xxy * bitMsk;
	return decomp;
}

//--------------------------------------------------------------------------------------------------
float unpackFloatFromVec3(const float3 value)
{
	static const float3 bitSh = float3(255.0/256, 255.0/(256*256), 255.0/(256*256*256));

	return dot(value, bitSh);
}

//-- converts a normalized cartesian direction vector to spherical coordinates.
//--------------------------------------------------------------------------------------------------
half2 cartesianToSpherical(in half3 cartesian)
{
#if 0
	static const half invPi = 1.0h / 3.14159h;
	half2 spherical;
	spherical.x = atan2(cartesian.y, cartesian.x) * invPi;
	spherical.y = cartesian.z;
	return spherical * 0.5h + 0.5h;
#else
	half3 packed = cartesian * 0.5h + 0.5h;
	half2 spherical;
	spherical.x = lookup_atan2(packed.y, packed.x);
	spherical.y = packed.z;
	return spherical;
#endif
}

//-- Converts a spherical coordinate to a normalized cartesian direction vector.
//--------------------------------------------------------------------------------------------------
half3 sphericalToCartesian(half2 spherical)
{
  half2 sinCosTheta, sinCosPhi;

  spherical = spherical * 2 - 1;
  sincos(spherical.x * 3.14159h, sinCosTheta.x, sinCosTheta.y);
  sinCosPhi = half2(sqrt(1 - spherical.y * spherical.y), spherical.y);

  return half3(sinCosTheta.y * sinCosPhi.x, sinCosTheta.x * sinCosPhi.x, sinCosPhi.y);    
}

//--------------------------------------------------------------------------------------------------
float almostZero(float f, float epsilon = 0.0004f)
{
	return f < epsilon && f > -epsilon;
}

#endif //-- _BW_DEFERRED_SHADING_FXH_
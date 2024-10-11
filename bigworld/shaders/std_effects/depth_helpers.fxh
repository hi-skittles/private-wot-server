#ifndef DEPTH_HELPERS_FXH
#define DEPTH_HELPERS_FXH

// experiments with motion blur:
//#define USE_MOTION_BLUR

float4 farPlane : FarPlane;

/**
 *	This file contains all the helpers for depth related stuff
 */

// Packing / Unpacking floats
float4 floatToColour4( float value )
{
	const float max24int = 256*256*256-1;
	const float4 bitSh = float4( max24int/(256*256), max24int/256, max24int, max24int*256 );
	const float4 bitMsk = float4( 0.0, 256.0, 256.0, 256.0 );
	float4 decomp = floor( value * bitSh ) / 255.0;
	decomp -= decomp.xxyz * bitMsk;
	return decomp;
}

float colour4ToFloat(const float4 value)
{
	const float4 bitSh = float4( 255.0/256, 255.0/(256*256), 255.0/(256*256*256), (255.0/256)/(256*256*256) );
	return(dot(value, bitSh));
}

float4 floatToColour4WithAlpha( float value, float alpha )
{
	const float max24int = 256*256*256-1;
	const float3 bitSh = float3( max24int/(256*256), max24int/256, max24int );
	const float3 bitMsk = float3( 0.0, 256.0, 256.0 );
	float3 decomp = floor( value * bitSh ) / 255.0;
	decomp -= decomp.xxy * bitMsk;
	return float4(decomp.xyz, alpha);
}

float colour4ToFloatWithAlpha(const float4 value)
{
	const float3 bitSh = float3( 255.0/256, 255.0/(256*256), 255.0/(256*256*256) );
	return(dot(value.xyz, bitSh));
}


float decodeDepth( sampler depthTex, float2 tc )
{
	float4 dSample = tex2D( depthTex, tc );
	return (colour4ToFloatWithAlpha(dSample)*farPlane.x);
}

float decodeDepthWithAlpha( sampler depthTex, float2 tc, out float alpha )
{
	float4 dSample = tex2D( depthTex, tc );
	alpha = dSample.a;
	return (colour4ToFloatWithAlpha(dSample)*farPlane.x);
}

struct PS_OutputMRT
{
	float4 col0	:		COLOR0;
	float4 col1	:		COLOR1;
};

struct PS_Output
{
	float4 col0	:		COLOR0;
};

float g_objectID : ObjectID;
#if USE_MRT_DEPTH
#define BW_COLOUR_OUT PS_OutputMRT

//TODO: common depth output technique
//#define BW_OUTPUT_DEPTH( out )							\
//	out.depthInfo.x = (out.pos.z);							\
//	/*out.depthInfo.x = out.pos.z * out.pos.w / farPlane;*/	\
//	/*o.depthInfo = o.pos.w * farPlane;*/

#define BW_FINAL_COLOUR( depth, colour )					\
	BW_COLOUR_OUT o = (BW_COLOUR_OUT)0;						\
	o.col0 = colour;										\
	o.col1 = floatToColour4WithAlpha( depth, g_objectID );	\
	return o;

#ifdef USE_MOTION_BLUR
#define BW_FINAL_COLOUR2( depth, colour, velocity )			\
	BW_COLOUR_OUT o = (BW_COLOUR_OUT)0;						\
	o.col0 = colour;										\
	velocity = (velocity + 1.0) * 0.5;	/*apply bias*/		\
	o.col1 = float4(depth, velocity.x, velocity.y, 0.5f);	\
	return o;
#else
#define BW_FINAL_COLOUR2( depth, colour, velocity ) BW_FINAL_COLOUR(depth,colour)
#endif //USE_MOTION_BLUR

#define BW_DEPTH(out, depth) out = depth * farPlane.y;

#else

#define BW_COLOUR_OUT PS_Output

//#define BW_OUTPUT_DEPTH( out )
#define BW_FINAL_COLOUR( depth, colour )					\
	BW_COLOUR_OUT o = (BW_COLOUR_OUT)0;						\
	o.col0 = colour;										\
	return o;

#define BW_FINAL_COLOUR2( depth, colour, velocity ) BW_FINAL_COLOUR(depth,colour)

#define BW_DEPTH(out, depth) 

#endif //USE_MRT_DEPTH

#ifdef USE_MOTION_BLUR
float4x4 lastWVP : LastWorldViewProjection;
float4x4 WVP : WorldViewProjection;
float4 calcVelocity( float4 inPos, float4 currentPos )
{
	float4 lastPos = mul( inPos, lastWVP );
	// do divide by W -> NDC coordinates
	currentPos.xyz = currentPos.xyz / currentPos.w;
	lastPos.xyz = lastPos.xyz / lastPos.w;
	float3 dP = (currentPos.xyz - lastPos.xyz);
	dP *= 0.5;
	return float4(dP.xyz, 1);
}
#endif //USE_MOTION_BLUR

#endif //DEPTH_HELPERS_FXH
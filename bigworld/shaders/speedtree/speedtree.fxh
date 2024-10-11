#include "stdinclude.fxh"
#include "quaternion_helpers.fxh"

//-- debug.
#define SHOW_OVERDRAW 0

//--------------------------------------------------------------------------------------------------
#if BW_DEFERRED_SHADING
	#include "write_g_buffer.fxh"
#endif

//--
static const int G_NUM_WIND_MATRICES = 6;

//-- 64 bytes structure describes each individual speedtree instance.
//--------------------------------------------------------------------------------------------------
struct SpeedTreeInstance
{
	float4	 m_rotationQuat;
	float3   m_translation;
	float	 m_uniformScale;
	float3   m_scale;
	float	 m_materialID;
	float	 m_windMatOffset;
	float    m_blendFactor;
	float	 m_alphaRef;	
	float	 m_padding;
};

SpeedTreeInstance g_instance;

//-- 40 bytes packed structure. See vertex declaration in speedtree_instancing.xml
//--------------------------------------------------------------------------------------------------
struct SpeedTreeInstancingStream
{
	float4 m_row0	:	TEXCOORD3;
	float4 m_row1	:	TEXCOORD4;
	float4 m_row2	:	TEXCOORD5;    
	float4 m_row3	:	TEXCOORD6;
};

//-- unpack specialy packed instancin stream data.
//-- See speedtree_tree_type.hpp file Instance::packForInstancing() function.
//--------------------------------------------------------------------------------------------------
SpeedTreeInstance unpackInstancingStream(in SpeedTreeInstancingStream stream)
{
	/*
	SpeedTreeInstance o = (SpeedTreeInstance)0;
	o.m_rotationQuat   = stream.m_row0;
	o.m_translation    = stream.m_row1.xyz;
	o.m_uniformScale   = stream.m_row1.w;
	o.m_scale		   = stream.m_row2.xyz;
	o.m_materialID	   = stream.m_row2.w;
	o.m_windMatOffset  = stream.m_row3.x;
	o.m_blendFactor	   = stream.m_row3.y;
	o.m_alphaRef	   = stream.m_row3.z;
	o.m_padding		   = stream.m_row3.w;
	*/

	SpeedTreeInstance o = (SpeedTreeInstance)stream;

	//--
	o.m_scale.xyz	/= 511.0f;
	o.m_alphaRef	/= 255.0f;
	o.m_blendFactor /= 255.0f;
	o.m_uniformScale = dot(o.m_scale.xyz, 1) * 0.333f;

	return o;
}

//-- quality option.
bool	 g_useHighQuality = true;
bool	 g_useZPrePass = false;
bool	 g_useNormalMap = true;
bool     g_texturedTrees = true;

texture  g_diffuseMap;
texture  g_normalMap;

//--
float4   g_material[2];  //-- [0] - diffuse, [1] - ambient multipliers for each individual tree part.
float	 g_leafLightAdj; //-- 
bool	 alphaTestEnable = true;

//-- per tree type properties.
float    g_leafRockFar;
float4x4 g_windMatrices[G_NUM_WIND_MATRICES];
float4   g_leafAngles[64];
float4   g_leafAngleScalars;
float4   g_leafUnitSquare[5] =
{
	 float4(+0.5f, +0.5f, 0.0f, 0.0f), 
	 float4(-0.5f, +0.5f, 0.0f, 0.0f), 
	 float4(-0.5f, -0.5f, 0.0f, 0.0f), 
	 float4(+0.5f, -0.5f, 0.0f, 0.0f),
	 float4( 0.0f,  0.0f, 0.0f, 0.0f)
};

//-- specular fade-out distance.
static const float g_specularFadeoutDist = 1.0f / 500.0f;

//--
sampler  speedTreeDiffuseSampler = BW_SAMPLER(g_diffuseMap, WRAP)

sampler bbNormalSampler = sampler_state
{
	Texture       = (g_normalMap);
	ADDRESSU      = WRAP;
	ADDRESSV      = WRAP;
	ADDRESSW      = WRAP;
	MAGFILTER     = LINEAR;
	MINFILTER     = LINEAR;
	MIPFILTER     = POINT;
	MAXMIPLEVEL   = 0;
	MIPMAPLODBIAS = 0;
};

sampler speedTreeNormalSampler = BW_SAMPLER(g_normalMap, WRAP)

//--  WindEffect
//--
//--  New with 4.0 is a two-weight wind system that allows the tree model
//--  to bend at more than one branch level.
//--
//--  In order to keep the vertex size small, the wind parameters have been
//--  compressed as detailed here:
//--
//--      vWindInfo.x = (wind_matrix_index1 * 10.0) / G_NUM_WIND_MATRICES  + wind_weight1
//--      vWindInfo.y = (wind_matrix_index2 * 10.0) / G_NUM_WIND_MATRICES  + wind_weight2
//--
//--  * Note: G_NUM_WIND_MATRICES cannot be larger than 10 in this case
//--
//--  * Caution: Negative wind weights will not work with this scheme.  We rely on the
//--             fact that the SpeedTreeRT library clamps wind weights to [0.0, 1.0]
//--------------------------------------------------------------------------------------------------
float3 applyWind(float3 vPosition, float2 vWindInfo, float windMatrixOffset)
{
	// decode both wind weights and matrix indices at the same time in order to save
	// vertex instructions
	vWindInfo.xy += windMatrixOffset.xx;
	float2 vWeights = frac( vWindInfo.xy );
	float2 vIndices = (vWindInfo - vWeights) * 0.05f * G_NUM_WIND_MATRICES;

	// first-level wind effect - interpolate between static position and fully-blown
	// wind position by the wind weight value
	float3 vWindEffect = lerp(vPosition.xyz, mul(vPosition, (float3x3)g_windMatrices[int(vIndices.x)]), vWeights.x);

	// second-level wind effect - interpolate between first-level wind position and 
	// the fully-blown wind position by the second wind weight value
	return lerp(vWindEffect, mul(vWindEffect, (float3x3)g_windMatrices[int(vIndices.y)]), vWeights.y);
}

//--------------------------------------------------------------------------------------------------
struct VS_INPUT_BRANCHES
{
	float4 pos			: POSITION;
	float3 normal		: NORMAL;
	float4 tcWindInfo	: TEXCOORD0;
	float3 tangent		: TANGENT;
};

//--------------------------------------------------------------------------------------------------
float4 branchesOutputPosition(const VS_INPUT_BRANCHES i, SpeedTreeInstance inst, bool enableWind = true)
{
	float3 wPos = i.pos.xyz;

	//-- 1. scale vertex before rotation and translation.
	wPos  = wPos * inst.m_scale;

	//-- 2. rotate vertex in world space.
	wPos  = qrot(wPos, inst.m_rotationQuat);

	//-- 3. (optional) apply wind effect on the vertex.
	if (enableWind)
	{
		wPos  = applyWind(wPos, i.tcWindInfo.zw, inst.m_windMatOffset);
	}

	//-- 4. translate vertex in the world space.
	wPos += inst.m_translation;

	//-- 5. and finally convert vertex position to the clip space.
	return mul(float4(wPos, 1.0f), g_viewProjMat);
};

//--
//-- Leaves
//--------------------------------------------------------------------------------------------------

//--------------------------------------------------------------------------------------------------
struct VS_INPUT_LEAF
{
	float4 pos			: POSITION;
	float3 normal		: NORMAL;
	float4 tcWindInfo	: TEXCOORD0;
	float4 rotGeomInfo	: TEXCOORD1;
	float3 extraInfo	: TEXCOORD2;
	float3 tangent		: TANGENT;
	float2 pivotInfo	: BINORMAL;
};

//-- Includes 2 leaf influences and better rock/rustle.
//--------------------------------------------------------------------------------------------------
float4 calcLeafVertex2(const VS_INPUT_LEAF i, SpeedTreeInstance inst, bool enableWind = true, bool enableRockAndRustle = true)
{
	float3 centerPoint = i.pos.xyz;

	//-- scale vertex before rotation and translation.
	centerPoint.xyz *= inst.m_scale.xyz;

	//-- rotate center point.
	centerPoint      = qrot(centerPoint, inst.m_rotationQuat);

	//-- (optional) enable wind.
	if (enableWind)
	{
		centerPoint = applyWind(centerPoint, i.tcWindInfo.zw, inst.m_windMatOffset);
	}

	centerPoint     += inst.m_translation;

	float3 corner    = g_leafUnitSquare[i.extraInfo.y].xyz;
	corner.xy	    += i.pivotInfo.xy;
	corner.xyz	    *= inst.m_uniformScale * saturate(g_cameraPos.w * 7.0f);

	//-- adjust by pivot point so rotation occurs around the correct point
	corner.xyz	    *= i.rotGeomInfo.zwz;

	//--
	if (enableRockAndRustle)
	{
		//-- rock & rustling on the card corner
		float fRotAngleX = i.rotGeomInfo.x;  // angle offset for leaf rocking (helps make it distinct)
		float fRotAngleY = i.rotGeomInfo.y;  // angle offset for leaf rustling (helps make it distinct)

		//-- quaternion rotation sequence.
		float2 leafRockAndRustle = g_leafAngleScalars.xy * g_leafAngles[i.extraInfo.x].xy;
		float4 combQuat	= quat(fRotAngleY, float3(1,0,0));
		combQuat		= qmul(combQuat, quat(fRotAngleX - leafRockAndRustle.y, float3(0,1,0)));
		combQuat		= qmul(combQuat, quat(leafRockAndRustle.x, float3(0,0,1)));
		corner			= qrot(corner, combQuat);
	}

	centerPoint  = mul(float4(centerPoint, 1.0f), g_viewMat).xyz;
	centerPoint += corner;

	return float4(centerPoint, 1.0f);
}

//--------------------------------------------------------------------------------------------------
struct VS_INPUT_BB
{
    float4 pos			: POSITION;
    float3 lightNormal	: NORMAL;
    float3 alphaNormal	: TEXCOORD0;
    float2 tc			: TEXCOORD1;
	float3 binormal		: BINORMAL;
	float3 tangent		: TANGENT;
};

//-- Blend imposters based on the imposter normal and camera direction.
//--------------------------------------------------------------------------------------------------
half calculateAlpha(in half3 aphaWorldNormal, in half3 camDir, in half alphaRef)
{
	half3 alphaNormal = normalize(aphaWorldNormal);
	half  cameraDim   = abs(dot(alphaNormal, camDir));

	return (1 - ((1 - alphaRef) * cameraDim));
}
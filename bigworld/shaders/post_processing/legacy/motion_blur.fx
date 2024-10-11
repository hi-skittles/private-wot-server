#include "post_processing.fxh"

DECLARE_EDITABLE_TEXTURE( inputTexture, inputSampler, CLAMP, CLAMP, LINEAR, "Input texture/render target" )
USES_DEPTH_TEXTURE

//-- Note: Some pre defined settings.
#define DEBUG_VERSION		0
#define NUM_SAMPLES			8
#define VELOCITY_THRESHOLD	5

const float g_blurAmount
<
	bool artistEditable = true;
	float UIMin = 0.0;
	float UIMax = 1.0;
	int UIDigits = 2;
	string UIDesc = "Amount of the blur.";
> = 1.0f;

const float g_useMasking
<
	bool artistEditable = true;
	float UIMin = 0.0;
	float UIMax = 1.0;
	int UIDigits = 0;
	string UIDesc = "The object won't interact with motion blur.";
> = 1.0f;

//const float4x4 g_invViewProjMat  : InvViewProjection;
//const float4x4 g_lastViewProjMat : LastViewProjection;
const float4   g_farNearPlanes   : FarNearPlanes;
//const float4   g_invScreen		 : InvScreen;

#if DEBUG_VERSION

	const float g_debug
	<
		bool artistEditable = true;
		float UIMin = 0;
		float UIMax = 4;
		int UIDigits = 0;
		string UIDesc = "0 - nothing, 1 - debug velocity vector, 2 - debug depth";
	> = 0;

#endif //-- DEBUG_VERSION

//-- This function returns the true world space positon of the screen pixel as the function output
//-------------------------------------------------------------------------------------------------
float4 restoreWorldPos(in float2 texCoord, out float mask, out float4 clipPos, out float depth)
{
	//-- 1. restore scene depth in the screen space:

	//-- a. depth = (worldPos * viewProjMat).z
	depth = decodeDepthWithAlpha(depthSampler, texCoord, mask);
	//-- b. restore (worldPos * viewProjMat).w
	float w = depth * (g_farNearPlanes.x - g_farNearPlanes.z) * g_farNearPlanes.y + g_farNearPlanes.z;
	//-- c. make perspective division.
	depth /= w;

	//-- 2. make blur mask depended on alpha chanel of the mrt depth buffer.
	mask = 1.0f - saturate(mask) * g_useMasking;

	//-- 3. make position of the pixel on the screen.
	clipPos.x = +(2.0 * texCoord.x - 1.0f);
	clipPos.y = -(2.0 * texCoord.y - 1.0f);
	clipPos.z = depth;
	clipPos.w = 1.0f;

	//-- 4. calculate world position of desired pixel in the current frames.
	float4 curWorldPos = mul(clipPos, g_invViewProjMat);
	curWorldPos /= curWorldPos.w;

	return curWorldPos;
}

//-------------------------------------------------------------------------------------------------
float4 ps_main( PS_INPUT input ) : COLOR0
{
	//-- save texture coordinates.
	float2 texCoord = input.tc0;
	float  mask		= 0.0f;
	float  depth	= 0.0f;
	float4 clipPos  = float4(0,0,0,0);

	//-- 1. restore scene depth in the screen space.
	float4 curWorldPos = restoreWorldPos(texCoord, mask, clipPos, depth);

	//-- 2. now calculate screen position in the previous frame.
	float4 lastClipPos = mul(curWorldPos, g_lastViewProjMat);
	lastClipPos /= lastClipPos.w;

	//-- 3. calculate the velocity in the range of steps.
	float2 velocity = float2(0,0);
	{
		//-- a. calculate the velocity in the world space.
		velocity = (clipPos - lastClipPos) * 0.5f;

		//-- b. clam velocity vector to threshold.
		float2 vt = float2(VELOCITY_THRESHOLD, VELOCITY_THRESHOLD) * g_invScreen.zw;
		velocity = clamp(velocity, -vt, +vt);

		//-- c. apply the custom blur amount.
		velocity *= (g_blurAmount * 0.01f);

		//-- d. use masking, i.e. we blur only the environment, but not the entities.
		velocity *= mask;
	}
	
	//-- 4. retrieve initial color sample.
	float4 oColor = tex2D(inputSampler, texCoord);

	//-- 5. change texture coordinates along the motion vector.
	texCoord += velocity;

	//-- 6. make a numerous samples along the velocity vector.
	for (int i = 1; i < NUM_SAMPLES; ++i, texCoord += velocity)
	{
		//-- retrieve sample.
		float4 color = tex2D(inputSampler, texCoord);

		//-- add it to the output color.
		oColor += color;
	}

	//-- 7. average all of the samples.
	oColor /= NUM_SAMPLES;

#if DEBUG_VERSION

	if		(g_debug == 1)	return float4(velocity * 0.5f + 0.5f, 0, 1);
	else if (g_debug == 2)	return float4(depth, 0, 0, 1);
	else					return oColor;

#else

	return oColor;

#endif //-- DEBUG_VERSION
}

STANDARD_PP_TECHNIQUE( compile vs_2_0 vs_pp_default(), compile ps_2_0 ps_main() )

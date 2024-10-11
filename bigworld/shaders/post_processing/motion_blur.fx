#include "post_processing.fxh"
#include "read_g_buffer.fxh"

DECLARE_EDITABLE_TEXTURE( inputTexture, inputSampler, CLAMP, CLAMP, LINEAR, "Input texture/render target" )

//-- Note: Some pre defined settings.
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

float2 calcVelocity(float4 clipPos, float4 lastClipPos)
{
	float2 velocity = float2(0,0);

	//-- a. calculate the velocity in the clip space.
	velocity = (clipPos - lastClipPos).xy * 0.5f;

	//-- b. clamp velocity vector to threshold.
	float2 vt = float2(VELOCITY_THRESHOLD, VELOCITY_THRESHOLD) * g_invScreen.zw;
	velocity = clamp(velocity, -vt, +vt);

	//-- c. apply the custom blur amount.
	velocity *= g_blurAmount;

	return velocity;
}

float4 ps_main( PS_INPUT input ) : COLOR0
{
	//-- name aliases
	float2 texCoord = input.tc0.xy;

	//-- current world pos
	float4 curWorldPos = float4(g_buffer_readWorldPos(texCoord), 1.f);

	//-- current clip pos
	float4 clipPos = mul(curWorldPos, g_viewProjMat);
	clipPos /= clipPos.w;

	//-- prev clip pos
	float4 lastClipPos = mul(curWorldPos, g_lastViewProjMat);
	lastClipPos /= lastClipPos.w;

	//-- velocity
	float2 velocity = calcVelocity(clipPos, lastClipPos);

	//-- color
	float4 oColor = 0.f;
	for (int i = 0; i < NUM_SAMPLES; ++i, texCoord += velocity)
	{		
		float4 color = tex2D(inputSampler, texCoord);
		oColor += color;
	}
	oColor /= NUM_SAMPLES;

	//-- return
	return oColor;
}

STANDARD_PP_TECHNIQUE_STENCILMASK( 
	compile vs_2_0 vs_pp_default(), 
	compile ps_2_0 ps_main(), 
	G_STENCIL_USAGE_ALL_OPAQUE )

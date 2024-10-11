#include "stdinclude.fxh"
//--------------------------------------------------------------------------------------------------

BW_ARTIST_EDITABLE_ALPHA_BLEND
BW_ARTIST_EDITABLE_ALPHA_TEST

BW_ARTIST_EDITABLE_DIFFUSE_MAP
BW_ARTIST_EDITABLE_ADDRESS_MODE(BW_WRAP)

sampler diffuseSampler = BW_SAMPLER( diffuseMap, BW_TEX_ADDRESS_MODE )

float4x4 proj : Projection;
float4x4 invview : InvView;


// -- Near fade
float nearFadeCutoff = 1;			// [0,nearFadeStart] distance at which to discard fragments
float nearFadeStart = 1.5;		// [nearFadeCutoff, n] distance at which fading is full opacity
float nearFadeFalloffPower = 1;		// [1,n] falloff/fading curve factor

// -- Softness
float softDepthRange = 1;	// [0,n] modifies range of depth difference to which softness is applied
float softFalloffPower = 1;	// [1,10] falloff/fading curve factor
float softDepthOffset = 0;	// [-1,1] shifts the softening by relative depth difference, relative to extent.

static const float minAlphaCutoff = 0.01;	// [0,1] min fragment alpha to consider. lower than this get discarded

bool fogToFogColour = true;
//--------------------------------------------------------------------------------------------------
#if BW_DEFERRED_SHADING
	// Soft particles params enabled from client side only when deferred pipeline.
	// Reading scene depth is required for soft particle effect.
	#include "read_g_buffer.fxh"
#endif //-- BW_DEFERRED_SHADING
//--------------------------------------------------------------------------------------------------

// -- Declarations
struct PS_INPUT
{
	float4 pos : POSITION;
	float3 tc : TEXCOORD0;// z = fogDensity 1 - no fog, 0 - full fog.

	// Can't read POSITION in pixel shader
	// So output pos to a TEXCOORD as well
	float4 pos2 : TEXCOORD1;
	float4 diffuse : TEXCOORD2;
};

//--------------------------------------------------------------------------------------------------

/**
 * This function maps the input (depth difference in [0,1]) to an output value in [0,1] 
 * using a piecewise symmetric contrast curve that can be tweaked via the power parameter.
 * Reference: http://developer.download.nvidia.com/whitepapers/2007/SDK10/SoftParticles_hi.pdf
 */
float nvidiaContrast( const in float input, const float contrastPower )
{
	float invInput = (input > 0.5) ? 1-input : input;
	float output = 0.5 * pow( saturate( 2 * invInput ), contrastPower );
	return (input > 0.5) ? 1-output : output;
}

#if BW_DEFERRED_SHADING
/**
 * This function calculates the "soft particle" opacity by comparing with scene depth
 * The return value is the opacity multiplier that alpha will be multiplied with.
 */
float depthSoftnessOpacity ( const in float4 pos2  )
{
	// -- Particle depth
	float particleDepth = pos2.w;

	// Scene depth from screen space depth texture (g buffer)
	float2 clipPos = pos2.xy / particleDepth;
	float2 screenCoords = ( clipPos.xy + 1 ) * 0.5;
	screenCoords.y = 1 - screenCoords.y;	// Texture y is from top left corner
	float sceneDepthNorm = g_buffer_readLinearZ(screenCoords); // [0,1]

	// Depth difference
	float zdiff = (sceneDepthNorm * g_farPlane.x) - particleDepth;

	// Particle is in front of scene - blend
	if (sceneDepthNorm != 1 && zdiff >= 0)
	{
		float scaledZDiff = (zdiff / softDepthRange) + softDepthOffset;
		return nvidiaContrast( scaledZDiff, softFalloffPower );
	}

	// return full opacity for max depth and negative diff (due to sky far plane)
	return 1;
}
#endif // BW_DEFERRED_SHADING

/**
 * Starts fading the particle from nearFadeStart as it comes closer to 
 * the nearFadeCutoff, at which point it is completely discarded.
 * This is to prevent visual popping and clipping against camera near plane.
 */
float nearFadeOpacity( const in float particleDepth )
{
	// opacity based on fade range position clamped to [0,1]
	float range = nearFadeStart - nearFadeCutoff;
	float opacity = saturate( (particleDepth - nearFadeCutoff) / range );

	// Apply falloff factor
	return pow(opacity, nearFadeFalloffPower);
}
//--------------------------------------------------------------------------------------------------

PS_INPUT vs_main_3_0( VertexXYZDUV input )
{

	PS_INPUT output = (PS_INPUT)0;
	output.pos = mul( input.pos, proj );
	output.pos2 = output.pos;
	output.tc.xy = input.tc;
	output.diffuse = input.diffuse;

	// -- Fog density
	float4 wPos = float4( mul( input.pos, invview ).xyz, 1 );
	float distToCam = length( g_cameraPos.xyz - wPos );
	output.tc.z = bw_vertexFog( wPos, distToCam );

	return output;
}
//--------------------------------------------------------------------------------------------------


float4 ps_main_3_0( PS_INPUT input ) : COLOR0
{
	// -- Input texture
	float4 diffuseMapColour = tex2D( diffuseSampler, input.tc.xy );

	// -- Calculate output colour
	float4 colour = diffuseMapColour;
	colour = colour * input.diffuse;

#if BW_DEFERRED_SHADING
	// In front of something - blend based on depth
	float opacity = depthSoftnessOpacity( input.pos2 );
	colour.w *= saturate( opacity );
#endif // BW_DEFERRED_SHADING

	// -- Calculate near plane fade out
	colour.w = min( colour.w, nearFadeOpacity( input.pos2.w ) );

	if (colour.w < minAlphaCutoff)
	{
		discard;
	}
	
	if (fogToFogColour)
	{
		colour.xyz = applyFogTo( colour.xyz, input.tc.z ); 
	}
	else
	{	// -- Fog to black.
		colour = colour * input.tc.z;
	}
	return colour;
}
//--------------------------------------------------------------------------------------------------

//--------------------------------------------------------------//
// Technique Section for shader 3
//--------------------------------------------------------------//

technique SpriteParticles
{
	pass Pass_0
	{

		BW_BLENDING_ALPHA
		CULLMODE = BW_CULL_NONE;

		VertexShader = compile vs_3_0 vs_main_3_0();
		PixelShader = compile ps_3_0 ps_main_3_0();
	}
}




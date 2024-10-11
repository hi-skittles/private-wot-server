#include "post_processing.fxh"
#include "lighting_helpers.fxh"

//This shader calculates a sun occlusion map based on the sun position
//and the depth buffer
USES_DEPTH_TEXTURE
float3 eyePos : CameraPos;
float4x4 viewProj : ViewProjection;


float2 sunScreenPos()
{
	float3 sunWorldPos = eyePos - g_sunLight.m_dir * farPlane.x;
	float4 projPos = mul(float4(sunWorldPos,1.0), viewProj);
	projPos.xyz /= projPos.w;
	projPos.x = projPos.x * 0.5 + 0.5;
	projPos.y = projPos.y * 0.5 + 0.5;
	projPos.y = 1.0 - projPos.y;
	return projPos.xy;
}


float4 sunColour( float2 sunPos, PS_INPUT input ) : COLOR0
{
	float2 deltaTexCoord = (input.tc2 - sunPos.xy);
	float len = 1.0 - saturate(distance(sunPos, input.tc2));
	return float4( len, len, len, 1.0 ) * g_sunLight.m_color;
}


float4 ps_main( PS_INPUT input ) : COLOR0
{
	//clip all pixels looking away from the sun
	clip( dot(input.worldNormal, -g_sunLight.m_dir) );

	float2 screenLightPos = sunScreenPos();
	float4 color = sunColour( screenLightPos, input );
	float sceneDepth = decodeDepth( depthSampler, input.tc0 );
	clip( sceneDepth - 0.999 );
	return sunColour( screenLightPos, input );
}

STANDARD_PP_TECHNIQUE( compile vs_3_0 vs_pp_default(), compile ps_3_0 ps_main() )

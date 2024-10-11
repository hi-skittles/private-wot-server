#include "post_processing.fxh"

DECLARE_EDITABLE_TEXTURE( inputTexture, inputSampler, CLAMP, CLAMP, LINEAR, "Input texture/render target" )
DECLARE_EDITABLE_TEXTURE( lookupTexture, lookupSampler, CLAMP, CLAMP, LINEAR, "Lee diagram lookup texture" )


float dropSize
<
	bool artistEditable = true;
	float UIMin = 0;
	float UIMax = 1.0;
	int UIDigits = 2;
	string UIDesc = "Rain drop size";
> = 0.7;


float rainbowAmount
<
	bool artistEditable = true;
	float UIMin = 0;
	float UIMax = 1.0;
	int UIDigits = 2;
	string UIDesc = "Rainbow effect amount";
> = 0.5;


float nearPlane : NearPlane;

USES_DEPTH_TEXTURE

float4 ps_main( PS_INPUT input ) : COLOR0
{
	float3 normalisedWN = normalize(input.worldNormal);	
	float dp = saturate( dot( normalisedWN, g_sunLight.m_dir) );	
	float2 tc = float2( dropSize, dp );
		
	float sceneDepth = decodeDepth( depthSampler, input.tc2 );	
	
	float4 leeMap = tex2D( lookupSampler, tc );
	return leeMap * rainbowAmount * sceneDepth;
}


//--------------------------------------------------------------//
// Technique Section
//--------------------------------------------------------------//
STANDARD_PP_TECHNIQUE( compile vs_2_0 vs_pp_default(), compile ps_2_0 ps_main() )

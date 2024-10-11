#include "post_processing.fxh"


DECLARE_ENVIRONMENT_CUBE_MAP( envMap, envMapSampler )
USES_DEPTH_TEXTURE


float z
<
	bool artistEditable = true;
	float UIMin = 0.01;
	float UIMax = 1.00;
	int UIDigits = 2;
	string UIDesc = "Starting percent distance to the far plane";
> = 1.0;


float falloffPower
<
	bool artistEditable = true;
	float UIMin = 0.5;
	float UIMax = 32.0;
	int UIDigits = 2;
	string UIDesc = "Falloff power";
> = 1.0;


float4 ps_main( PS_INPUT input ) : COLOR0
{
	float4 envMap = texCUBE(envMapSampler, input.worldNormal);
	float depthAdjust = 1.0 / normalize(input.viewNormal).z;
	float sceneDepth = decodeDepth(depthSampler, input.tc2) * depthAdjust;
	float4 colour;
	colour = envMap;
	colour.w = saturate( sceneDepth - z ) * (1.0/z);
	colour.w = pow( colour.w, falloffPower );
	return colour;	
}

STANDARD_PP_TECHNIQUE( compile vs_2_0 vs_pp_default(), compile ps_2_0 ps_main() )

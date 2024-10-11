#include "post_processing.fxh"
#include "lighting_helpers.fxh"

//This shader calculates an occlusion map based on the light position
//and the depth buffer
USES_DEPTH_TEXTURE
float3 eyePos : CameraPos;
float4x4 viewProj : ViewProjection;


struct PS_IN
{
   float4 pos:			POSITION; 
   float3 tc0:			TEXCOORD0;
   float4 lightPos:			TEXCOORD1;
};

float4 lightPos
<
	bool artistEditable = true;
	string UIDesc = "World Light Position";
> = {0,0,0,0};

float worldLightRadius
<
	bool artistEditable = true;
	float UIMin = 0;
	float UIMax = 100.0;
	int UIDigits = 2;
	string UIDesc = "World Light Radius";
> = 10.0;

float falloffPower
<
	bool artistEditable = true;
	float UIMin = 0;
	float UIMax = 100.0;
	int UIDigits = 2;
	string UIDesc = "World Light Falloff Power";
> = 10.0;

float4 projectLightPos()
{
	lightPos.w = 1.0;
	return mul(lightPos, viewProj);
}

float4 lightColour
<
	bool artistEditable = true;
	string UIWidget = "Color";
	float UIMin = 0;
	float UIMax = 2;
	int UIDigits = 1;
	string UIDesc = "Light Colour";
> = {1,1,1,1};


float2 screenToUV( float2 lightPos )
{
	float2 uv;
	uv.x = lightPos.x * 0.5 + 0.5;
	uv.y = lightPos.y * 0.5 + 0.5;
	uv.y = 1.0 - uv.y;
	return uv;
}

float4 lightCol( PS_IN input ) : COLOR0
{
	float2 currUVPos = screenToUV(input.lightPos);	
	float len = 1.0 - saturate(distance(currUVPos, input.tc0));
	len = pow(len, falloffPower);
	return float4( len, len, len, 1.0 ) * lightColour;
}

PS_IN vs_main( VS_INPUT input )
{
	PS_IN o = (PS_IN)0;
	
	o.pos = input.pos.xyww;
	o.tc0 = input.tc0;
	o.lightPos = projectLightPos();
	
	return o;
}

float4 ps_main( PS_IN input ) : COLOR0
{
	//projected coordinate now in input.tc1
	input.lightPos.xy /= input.lightPos.w;
	float zDist = input.lightPos.z;
	zDist /= farPlane.x;

	// float4 dSample = tex2D( depthSampler, input.tc0 );
	// float sceneDepth = colour4ToFloat(dSample);
	float sceneDepth = decodeDepth(depthSampler, input.tc0);

	float dist = sceneDepth - zDist;
	clip( dist );
	return lightCol( input );
}

STANDARD_PP_TECHNIQUE( compile vs_3_0 vs_main(), compile ps_3_0 ps_main() )

#include "post_processing.fxh"
#include "lighting_helpers.fxh"

DECLARE_EDITABLE_TEXTURE( inputTexture, inputSampler, CLAMP, CLAMP, LINEAR, "Input texture/render target" )

float3 eyePos : CameraPos;
float4x4 viewProj : ViewProjection;

int numSamples
<
	bool artistEditable = true;
	int UIMin = 1;
	int UIMax = 128;
	string UIDesc = "NUM_SAMPLES";
> = 16;

float density
<
	bool artistEditable = true;
	float UIMin = 0;
	float UIMax = 5.0;
	int UIDigits = 2;
	string UIDesc = "Sample density";
> = 1.0;

float weight
<
	bool artistEditable = true;
	float UIMin = 0;
	float UIMax = 2.0;
	int UIDigits = 3;
	string UIDesc = "Weight";
> = 1.0;

float decay
<
	bool artistEditable = true;
	float UIMin = 0;
	float UIMax = 5.0;
	int UIDigits = 2;
	string UIDesc = "Decay";
> = 1.0;

float exposure
<
	bool artistEditable = true;
	float UIMin = 0;
	float UIMax = 5.0;
	int UIDigits = 2;
	string UIDesc = "Exposure";
> = 1.0;

float4 lightPos
<
	bool artistEditable = true;
	float UIMin = 0;
	float UIMax = 5.0;
	int UIDigits = 2;
	string UIDesc = "World Light Position";
> = {0,0,0,0};


float2 lightScreenPos()
{
	lightPos.w = 1.0;
	float4 projPos = mul(lightPos, viewProj);
	projPos.xyz /= projPos.w;
	projPos.x = projPos.x * 0.5 + 0.5;
	projPos.y = projPos.y * 0.5 + 0.5;
	projPos.y = 1.0 - projPos.y;
	return projPos.xy;
}


float4 ps_main( PS_INPUT input ) : COLOR0
{
	float2 lsPos = lightScreenPos();
	float2 texCoord = input.tc0;
	half2 deltaTexCoord = (input.tc2 - lsPos.xy);
	deltaTexCoord *= 1.0f / numSamples * density;
	half3 color = tex2D(inputSampler, texCoord);
	
	// Early out if the source pixel is black
	clip ( color.r + color.g + color.b );
	
	// Set up illumination decay factor.
	half illuminationDecay = 1.0f;

	// Evaluate summation from Equation 3 numSamples iterations.
	for (int i = 0; i < numSamples; i++)
	{
		texCoord -= deltaTexCoord;
		half3 sample = tex2D(inputSampler, texCoord);
		sample *= illuminationDecay * weight;
		color += sample;
		illuminationDecay *= decay;
	}
	// Output final color with a further scale control factor.
	return float4( color * exposure, 1);
}

STANDARD_PP_TECHNIQUE( compile vs_3_0 vs_pp_default(), compile ps_3_0 ps_main() )

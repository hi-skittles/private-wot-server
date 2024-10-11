#include "post_processing.fxh"

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


float4 ps_main( PS_INPUT input ) : COLOR0
{
	float2 screenLightPos = sunScreenPos();
	float2 texCoord = input.tc0;	
	half2 deltaTexCoord = (input.tc2 - screenLightPos.xy);	
	deltaTexCoord *= 1.0f / numSamples * density;
	half3 color = tex2D(inputSampler, texCoord);

	// Early out if the source pixel is black
	clip ( color.r + color.g + color.b );

	half illuminationDecay = 1.0f;
	for (int i = 0; i < numSamples; i++)
	{		
		texCoord -= deltaTexCoord;		
		half3 sample = tex2D(inputSampler, texCoord);		
		sample *= illuminationDecay * weight;		
		color += sample;		
		illuminationDecay *= decay;
	}
	
	return float4( color * exposure, 1);
}

STANDARD_PP_TECHNIQUE( compile vs_3_0 vs_pp_default(), compile ps_3_0 ps_main() )

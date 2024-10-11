#include "post_processing.fxh"

DECLARE_EDITABLE_TEXTURE( inputTexture, inputSampler, CLAMP, CLAMP, LINEAR, "Input texture/render target" )

const float innerRadius
<
	bool artistEditable = true;
	float UIMin = 0;
	float UIMax = 1.0;
	int UIDigits = 2;
	string UIDesc = "Inner distortion radius";
> = 0.5;

const float outerRadius
<
	bool artistEditable = true;
	float UIMin = 0;
	float UIMax = 1.0;
	int UIDigits = 2;
	string UIDesc = "Outer distortion radius";
> = 1.0;

const float distortionCoeff
<
	bool artistEditable = true;
	float UIMin = -1.0;
	float UIMax =  1.0;
	int UIDigits = 2;
	string UIDesc = "Distortion coeffitient";
> = 0.1f;

//-------------------------------------------------------------------------------------------------
float smoothFunc(in float x)
{
	//return x;
	return x*x;
	//return smoothstep(0, 1, x);
}

//-------------------------------------------------------------------------------------------------
float2 lens(in float2 tc)
{
	//-- 1. screen space position.
	float2 scp  = 2.0f * tc - 1.0f;

	//-- 2. squared length from the center of the screen to the current point.
	float radius = length(scp);

	//-- 3. direction from the center of the screen to the desired texture coordinates.
	float2 dir  = float2(scp.x, scp.y);
	dir = normalize(dir);
	
	//-- 4. calculate coefficient.
	float coeff = saturate((radius - innerRadius) / (outerRadius - innerRadius));
	//float coeff = max(0.0f, (radius - innerRadius) / (outerRadius - innerRadius));

	//-- 5. some texture coordinates perturbation.
	tc -= dir * smoothFunc(coeff) * distortionCoeff;

	return tc;
}

//-------------------------------------------------------------------------------------------------
float4 ps_main( PS_INPUT input ) : COLOR0
{
	return tex2D(inputSampler, lens(input.tc2));
}

STANDARD_PP_TECHNIQUE( compile vs_2_0 vs_pp_default(), compile ps_2_0 ps_main() )

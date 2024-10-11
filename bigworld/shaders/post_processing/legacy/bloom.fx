#include "post_processing.fxh"

DECLARE_EDITABLE_TEXTURE( baseTexture, baseSampler, CLAMP, CLAMP, POINT,  "The main scene color texture/render target" )
DECLARE_EDITABLE_TEXTURE( blurTexture, blurSampler, CLAMP, CLAMP, LINEAR, "The blurred version of the scene color texture/render target" )

//const float4 g_invScreen : InvScreen;

const float g_bloomSaturation
<
	bool artistEditable = true;
	float UIMin = 0.0;
	float UIMax = 1.0;
	int UIDigits = 2;
	string UIDesc = "ToDo:";
> = 1.0f;

const float g_bloomIntensity
<
	bool artistEditable = true;
	float UIMin = 0.0;
	float UIMax = 2.0;
	int UIDigits = 2;
	string UIDesc = "ToDo:";
> = 0.5f;

const float g_baseSaturation
<
	bool artistEditable = true;
	float UIMin = 0.0;
	float UIMax = 1.0;
	int UIDigits = 2;
	string UIDesc = "ToDo:";
> = 1.0f;

const float g_baseIntensity
<
	bool artistEditable = true;
	float UIMin = 0.0;
	float UIMax = 2.0;
	int UIDigits = 2;
	string UIDesc = "ToDo:";
> = 0.6f;

const float g_blurPower
<
	bool artistEditable = true;
	float UIMin = 0.0;
	float UIMax = 5.0;
	int UIDigits = 2;
	string UIDesc = "ToDo:";
> = 1.0f;

//-- preudo poisson disk.
const static float2 g_poissonDisk[12] =
{ 
	-0.326212, -0.405805,
	-0.840144, -0.073580, 
	-0.695914,  0.457137, 
	-0.203345,  0.620716, 
	 0.962340, -0.194983, 
	 0.473434, -0.480026, 
	 0.519456,  0.767022, 
	 0.185461, -0.893124, 
	 0.507431,  0.064425, 
	 0.896420,  0.412458, 
	-0.321940, -0.932615, 
	-0.791559, -0.597705, 
}; 

//-------------------------------------------------------------------------------------------------
float3 adjustSaturation(in float3 color, in float saturation)
{ 
  //-- the constants 0.3, 0.59, and 0.11 are chosen because the 
  //-- human eye is more sensitive to green light, and less to blue. 
  return lerp(luminance(color), color, saturation); 
} 

//-------------------------------------------------------------------------------------------------
float4 ps_main( PS_INPUT input ) : COLOR0
{
	// -- get base color.
	float4 original = tex2D(baseSampler, input.tc0); 
  
	//-- compute bloom color after gaussian filtering.
	float4 bloom = tex2D(blurSampler, input.tc0); 

	for (int i = 0; i < 12; ++i)
	{ 
		bloom += tex2D(blurSampler, input.tc0 + g_blurPower * g_poissonDisk[i] * g_invScreen.zw); 
	}

	bloom /= 13; 
  
	//-- adjust intensity and saturation 
	original.rgb = adjustSaturation(original.rgb, g_baseSaturation ) * g_baseIntensity; 
	bloom.rgb	 = adjustSaturation(bloom.rgb,    g_bloomSaturation) * g_bloomIntensity;
	
	return float4(original.rgb + bloom.rgb, original.a + bloom.a);
}

STANDARD_PP_TECHNIQUE( compile vs_2_0 vs_pp_default(), compile ps_2_0 ps_main() )

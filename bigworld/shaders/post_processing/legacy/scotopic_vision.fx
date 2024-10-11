#include "post_processing.fxh"
DECLARE_EDITABLE_TEXTURE( inputTexture, inputSampler, CLAMP, CLAMP, LINEAR, "Input texture/render target" )
DECLARE_EDITABLE_TEXTURE( noiseTexture, inputSampler2, WRAP, WRAP, LINEAR, "Noise texture" )
DECLARE_EDITABLE_TEXTURE( colouredTexture, inputSampler3, CLAMP, CLAMP, LINEAR, "Colour-corrected scene render target" )

float alpha
<
	bool artistEditable = true;
	float UIMin = 0;
	float UIMax = 1.0;
	int UIDigits = 2;
	string UIDesc = "Main alpha value";
> = 1.0;


float additionalAlpha
<
	bool artistEditable = true;
	float UIMin = 0;
	float UIMax = 1.0;
	int UIDigits = 2;
	string UIDesc = "Additional alpha value, which gets added to the main alpha";
> = 0.0;


float noiseThreshold
<
	bool artistEditable = true;
	float UIMin = 0;
	float UIMax = 1.0;
	int UIDigits = 2;
	string UIDesc = "Noise threshold";
> = 0.7;


float noiseLevel
<
	bool artistEditable = true;
	float UIMin = 0;
	float UIMax = 20.0;
	int UIDigits = 2;
	string UIDesc = "Noise level";
> = 10.0;


float noiseScale
<
	bool artistEditable = true;
	float UIMin = 0.1;
	float UIMax = 15.0;
	int UIDigits = 2;
	string UIDesc = "Noise scale factor";
> = 10.0;


float4 ps_main( PS_INPUT input ) : COLOR0
{
	float4 image = tex2D( inputSampler, input.tc1 );
	float4 noise = tex2D( inputSampler2, input.tc1 * noiseScale );
	float4 colouredImage = tex2D( inputSampler3, input.tc1 );
	
	float lum = saturate( 1.0-luminance( image.rgb ) );	
	lum = saturate(lum - noiseThreshold) * 1.0 / noiseThreshold;
	
	image = (lum * colouredImage) + (1-lum) * image;
	
	float4 bb = image + lum * noiseLevel * noise;
	bb.a *= alpha;
	bb.a += additionalAlpha;
	return bb;
}

STANDARD_PP_TECHNIQUE( compile vs_2_0 vs_pp_default(), compile ps_2_0 ps_main() )

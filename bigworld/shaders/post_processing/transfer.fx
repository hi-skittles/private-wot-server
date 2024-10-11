#include "post_processing.fxh"

DECLARE_EDITABLE_TEXTURE( inputTexture, inputSampler, CLAMP, CLAMP, LINEAR, "Input texture/render target" )

float alphaOverdrive
<
	bool artistEditable = true;
	float UIMin = 0;
	float UIMax = 1.0;
	int UIDigits = 2;
	string UIDesc = "Input alpha multiplier";
> = 1.0;


float alpha
<
	bool artistEditable = true;
	float UIMin = 0;
	float UIMax = 1.0;
	int UIDigits = 2;
	string UIDesc = "Main alpha value, multiplied with input alpha.";
> = 1.0;


float additionalAlpha
<
	bool artistEditable = true;
	float UIMin = 0;
	float UIMax = 1.0;
	int UIDigits = 2;
	string UIDesc = "Additional alpha value, which gets added to the main alpha";
> = 0.0;


float4 colourise
<
	bool artistEditable = true;
	string UIWidget = "Color";
	string UIName = "Colour";
	string UIDesc = "RGB colour tint, multiplied with input colour.";
> = {1.0,1.0,1.0,1.0};


float4 ps_main( PS_INPUT input ) : COLOR0
{
	float4 bb = tex2D( inputSampler, input.tc1 );
	bb.a = saturate( bb.a * alphaOverdrive );
	bb *= float4(colourise.r,colourise.g,colourise.b,alpha);
	bb.a += additionalAlpha;
	return bb;
}

STANDARD_PP_TECHNIQUE( compile vs_2_0 vs_pp_default(), compile ps_2_0 ps_main() )

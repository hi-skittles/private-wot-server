#include "post_processing.fxh"

DECLARE_EDITABLE_TEXTURE( lookupTexture, lookupSampler, CLAMP, CLAMP, LINEAR, "Colour correction lookup table texture" )
DECLARE_EDITABLE_TEXTURE( inputTexture, inputSampler, CLAMP, CLAMP, LINEAR, "Input texture/render target" )

float alpha 
<
	bool artistEditable = true;
	float UIMin = 0;
	float UIMax = 1.0;
	int UIDigits = 2;
	string UIDesc = "Alpha value";
> = 1.0;

half3 colourCorrect( half3 origColor )
{	
	half3 newColor;
	newColor.r = tex1D(lookupSampler,origColor.r).r;
	newColor.g = tex1D(lookupSampler,origColor.g).g;
	newColor.b = tex1D(lookupSampler,origColor.b).b;
	return newColor;
};

half3 colourCorrectLerpAlpha( half3 origColor, float alphaKey )
{	
	half4 newColor;
	newColor.r = tex1D(lookupSampler,origColor.r).r;
	newColor.g = tex1D(lookupSampler,origColor.g).g;
	newColor.b = tex1D(lookupSampler,origColor.b).b;
	float amt = tex1D(lookupSampler,alphaKey).a;	
	return lerp(origColor,newColor,amt);
};

float4 ps_main( PS_INPUT input ) : COLOR0
{
	float4 bb = tex2D( inputSampler, input.tc2 );	
	float4 colour;
	colour.xyz = colourCorrect( bb );
	colour.a = (alpha);
	return colour;
}

STANDARD_PP_TECHNIQUE( compile vs_2_0 vs_pp_default(), compile ps_2_0 ps_main() )

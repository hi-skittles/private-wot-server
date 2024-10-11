#include "post_processing.fxh"

DECLARE_EDITABLE_TEXTURE( texture1, baseSampler1, CLAMP, CLAMP, POINT,  "The main scene color texture/render target" )
DECLARE_EDITABLE_TEXTURE( texture2, baseSampler2, CLAMP, CLAMP, LINEAR, "The blurred version of the scene color texture/render target" )

//const float4 g_invScreen : InvScreen;

const float Saturation2
<
	bool artistEditable = true;
	float UIMin = 0.0;
	float UIMax = 1.0;
	int UIDigits = 2;
	string UIDesc = "ToDo:";
> = 1.0f;

const float Intensity2
<
	bool artistEditable = true;
	float UIMin = 0.0;
	float UIMax = 2.0;
	int UIDigits = 2;
	string UIDesc = "ToDo:";
> = 0.5f;

const float Saturation1
<
	bool artistEditable = true;
	float UIMin = 0.0;
	float UIMax = 1.0;
	int UIDigits = 2;
	string UIDesc = "ToDo:";
> = 1.0f;

const float Intensity1
<
	bool artistEditable = true;
	float UIMin = 0.0;
	float UIMax = 2.0;
	int UIDigits = 2;
	string UIDesc = "ToDo:";
> = 0.6f;


//-------------------------------------------------------------------------------------------------
float3 adjustSaturation(in float3 color, in float saturation)
{ 
  //-- the constants 0.3, 0.59, and 0.11 are chosen because the 
  //-- human eye is more sensitive to green light, and less to blue. 
  return lerp(luminance(color), color, saturation); 
} 

float4 ps_main( PS_INPUT input ) : COLOR0
{
	// -- get base color.
	float4 original1 = tex2D(baseSampler1, input.tc0); 
	// -- get base color.
	float4 original2 = tex2D(baseSampler2, input.tc0); 
  
	//-- adjust intensity and saturation 
	original1.rgb = adjustSaturation(original1.rgb, Saturation1 ) * Intensity1; 
	original2.rgb	 = adjustSaturation(original2.rgb,    Saturation2) * Intensity2;
	
	return float4(original1.rgb + original2.rgb, 0.0f);//min(original1.a, original2.a));
}

//STANDARD_PP_TECHNIQUE_NO_ALPHA( compile vs_2_0 vs_pp_default(), compile ps_2_0 ps_main() )
technique PP_TECHNIQUE
{
   pass Pass_0
   {
      ALPHATESTENABLE = <alphaTestEnable>;
      ALPHAREF = <alphaReference>;
      SRCBLEND = <srcBlend>;
      DESTBLEND = <destBlend>;
      ZENABLE = FALSE;
      FOGENABLE = FALSE;
      ALPHABLENDENABLE = TRUE;
      POINTSPRITEENABLE = FALSE;
      STENCILENABLE = FALSE;
	  COLORWRITEENABLE = RED|GREEN|BLUE;
      VertexShader = compile vs_2_0 vs_pp_default();
      PixelShader = compile ps_2_0 ps_main();
   }
}
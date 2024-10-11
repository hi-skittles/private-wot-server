#include "post_processing.fxh"

DECLARE_EDITABLE_TEXTURE( inputTexture, inputSampler, CLAMP, CLAMP, LINEAR, "Input texture/render target" )
DECLARE_EDITABLE_TEXTURE( hatchTexture, hatchSampler, WRAP, WRAP, LINEAR, "Hatch pattern texture (see the Content Creation Manual)" )
DECLARE_EDITABLE_TEXTURE( offsetTexture, offsetSampler, WRAP, WRAP, POINT, "Offset punchcard texture (see the Content Creation Manual)" )


float alpha
<
	bool artistEditable = true;
	float UIMin = 0;
	float UIMax = 1.0;
	int UIDigits = 2;
	string UIDesc = "Alpha value";
> = 1.0;


float tile
<
	bool artistEditable = true;
	float UIMin = 0;
	float UIMax = 128.0;
	int UIDigits = 1;
	string UIDesc = "Hatching pattern tiling";
> = 5.0;


float4 tint <
	bool artistEditable = true;
	string UIWidget = "Color";
	string UIDesc = "Hatching pattern tint colour";
> = {0.94, 0.94, 0.78, 1.0};


float scale
<
	bool artistEditable = true;
	float UIMin = 0;
	float UIMax = 15.0;
	int UIDigits = 1;
	string UIDesc = "Scale the brightness of the input render target";
> = 0.3;	//adjusts for brightness of input scene


float speed
<
	bool artistEditable = true;
	float UIMin = 0;
	float UIMax = 10.0;
	int UIDigits = 1;
	string UIDesc = "Hatching pattern offset change speed";
> = 2.7;	//pencil stroke variation speed - 12 fps (32texels / 12.0)
float time : Time;


float power
<
	bool artistEditable = true;
	float UIMin = 0.1;
	float UIMax = 32.0;
	int UIDigits = 1;
	string UIName = "Power";
	string UIDesc = "Mathematical Power of the filter";
> = 3.0;


float4 ps_main( PS_INPUT v ) : COLOR
{
	float4 map0 = tex2D( inputSampler, v.tc0.xy ) * scale;
	float2 hatchOffset = float2(0.05,time/speed);			//just sample the left-most pixel
	float4 offset = tex2D(offsetSampler, hatchOffset);
	float4 map1 = tex2D( hatchSampler, v.tc0.xy * tile + offset.rg );
	float3 bbx4 = saturate(map0.rgb * power);
	float4 r0;
	r0.rgb = (1-bbx4.rgb) * (1-map1.rgb);
	float4 r1;
	r1.a = saturate(dot(r0.rgb,float3(1,0,0)));
	r1.rgb = saturate(dot(r0,float3(0,0,1)));
	r1 = (1-r1) * (1-r1.a);
	r1 = 2 * (r1-0.5);
	r0.rgb = bbx4;
	r0.rgb = r1.rgb * r0.rgb;
	r0.rgb = r0.rgb * tint * 2;
	r0.a = alpha;
	return r0;
};

STANDARD_PP_TECHNIQUE( compile vs_2_0 vs_pp_default(), compile ps_2_0 ps_main() )

#include "post_processing.fxh"

DECLARE_EDITABLE_TEXTURE( inputTexture, inputSampler, CLAMP, CLAMP, LINEAR, "Input texture/render target" )


float threshold
<
	bool artistEditable = true;
	float UIMin = 0;
	float UIMax = 1.0;
	int UIDigits = 2;
	string UIName = "Dilation threshold";
	string UIDesc = "Dilation threshold.  A higher threshold filters more of the result";
> = 0.4;


//screenDimensions is (w,h,halfw,halfh)
float4 screenDimensions : Screen;

//uoffset, voffset, weight, unused
float4 tap1	<
	bool artistEditable = true;
	string UIDesc = "Filter tap 1 (uoffset, voffset, weight, unused)";
> = ( 0.0, 0.0, 0.0, 0.0 );

float4 tap2	<
	bool artistEditable = true;
	string UIDesc = "Filter tap 2 (uoffset, voffset, weight, unused)";
> = { 0.0, 0.0, 0.0, 0.0 };

float4 tap3	<
	bool artistEditable = true;
	string UIDesc = "Filter tap 3 (uoffset, voffset, weight, unused)";
> = { 0.0, 0.0, 0.0, 0.0 };

float4 tap4	<
	bool artistEditable = true;
	string UIDesc = "Filter tap 4 (uoffset, voffset, weight, unused)";
> = { 0.0, 0.0, 0.0, 0.0 };

float4 tap5	<
	bool artistEditable = true;
	string UIDesc = "Filter tap 5 (uoffset, voffset, weight, unused)";
> = ( 0.0, 0.0, 0.0, 0.0 );


struct DILATE_PS_INPUT
{
	float4 pos		: POSITION;
	float3 tc0		: TEXCOORD0;
	float2 invS		: TEXCOORD1;
};

DILATE_PS_INPUT vs_main( VS_INPUT input )
{
	DILATE_PS_INPUT o = (DILATE_PS_INPUT)0;
	o.pos = input.pos.xyww;
	o.tc0 = input.tc0;
	o.invS.x = 1.0 / screenDimensions.x;
	o.invS.y = 1.0 / screenDimensions.y;
	return o;
};

float4 ps_main( DILATE_PS_INPUT v ) : COLOR
{
	int i =0;
	float4 map[5];
	
	map[0] = tex2D( inputSampler, v.tc0.xy + tap1.xy * v.invS ) * tap1.z;
	map[1] = tex2D( inputSampler, v.tc0.xy + tap2.xy * v.invS ) * tap2.z;
	map[2] = tex2D( inputSampler, v.tc0.xy + tap3.xy * v.invS ) * tap3.z;
	map[3] = tex2D( inputSampler, v.tc0.xy + tap4.xy * v.invS ) * tap4.z;
	map[4] = tex2D( inputSampler, v.tc0.xy + tap5.xy * v.invS ) * tap5.z;
	
	float4 total = map[0] + map[1] + map[2] + map[3] + map[4];
	
	//threshold
	total = saturate( (total - threshold) * (0.5/threshold) );
	
	//and greyscale and invert
	total.rgb = 1 - luminance(total);
	
	return total;
};


STANDARD_PP_TECHNIQUE( compile vs_2_0 vs_main(), compile ps_2_0 ps_main() )

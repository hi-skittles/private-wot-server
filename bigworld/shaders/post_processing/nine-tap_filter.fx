#include "post_processing.fxh"

DECLARE_EDITABLE_TEXTURE( inputTexture, inputSampler, CLAMP, CLAMP, LINEAR, "Input texture/render target" )


float alpha
<
	bool artistEditable = true;
	float UIMin = 0;
	float UIMax = 1.0;
	int UIDigits = 2;
	string UIDesc = "Alpha value";
> = 1.0;

float brightness
<
	bool artistEditable = true;
	float UIMin = -1.0;
	float UIMax = 1.0;
	int UIDigits = 2;
	string UIName = "Brightness";
	string UIDesc = "Brightness of the filter";
> = 1.0;

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

float4 tap6	<
	bool artistEditable = true;
	string UIDesc = "Filter tap 6 (uoffset, voffset, weight, unused)";
> = { 0.0, 0.0, 0.0, 0.0 };

float4 tap7	<
	bool artistEditable = true;
	string UIDesc = "Filter tap 7 (uoffset, voffset, weight, unused)";
> = { 0.0, 0.0, 0.0, 0.0 };

float4 tap8	<
	bool artistEditable = true;
	string UIDesc = "Filter tap 8 (uoffset, voffset, weight, unused)";
> = { 0.0, 0.0, 0.0, 0.0 };

float4 tap9	<
	bool artistEditable = true;
	string UIDesc = "Filter tap 9 (uoffset, voffset, weight, unused)";
> = { 0.0, 0.0, 0.0, 0.0 };


struct NTF_PS_INPUT
{
	float4 pos		: POSITION;
	float3 tc0		: TEXCOORD0;
	float2 invS		: TEXCOORD1;
};


NTF_PS_INPUT vs_main( VS_INPUT input )
{
	NTF_PS_INPUT o = (NTF_PS_INPUT)0;
	o.pos = input.pos.xyww;
	o.tc0 = input.tc0;
	o.invS.x = 1.0 / g_screen.x;
	o.invS.y = 1.0 / g_screen.y;
	return o;
};


float4 ps_main( NTF_PS_INPUT v ) : COLOR
{
	float4 map0 = tex2D( inputSampler, v.tc0.xy + tap1.xy * v.invS ) * tap1.z;
	float4 map1 = tex2D( inputSampler, v.tc0.xy + tap2.xy * v.invS ) * tap2.z;
	float4 map2 = tex2D( inputSampler, v.tc0.xy + tap3.xy * v.invS ) * tap3.z;
	float4 map3 = tex2D( inputSampler, v.tc0.xy + tap4.xy * v.invS ) * tap4.z;
	float4 map4 = tex2D( inputSampler, v.tc0.xy + tap5.xy * v.invS ) * tap5.z;
	float4 map5 = tex2D( inputSampler, v.tc0.xy + tap6.xy * v.invS ) * tap6.z;
	float4 map6 = tex2D( inputSampler, v.tc0.xy + tap7.xy * v.invS ) * tap7.z;
	float4 map7 = tex2D( inputSampler, v.tc0.xy + tap8.xy * v.invS ) * tap8.z;
	float4 map8 = tex2D( inputSampler, v.tc0.xy + tap9.xy * v.invS ) * tap9.z;
	
	float4 result = map0 + map1 + map2 + map3 + map4 + map5 + map6 + map7 + map8;
	result.a = (alpha);
	return result;
};


STANDARD_PP_TECHNIQUE( compile vs_2_0 vs_main(), compile ps_2_0 ps_main() )

#include "post_processing.fxh"

DECLARE_EDITABLE_TEXTURE( inputTexture, inputSampler, CLAMP, CLAMP, LINEAR, "Input texture/render target" )

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


struct OUTPUT_VERTEX
{
	float4 pos		: POSITION;
	float3 tc0		: TEXCOORD0;
	float2 invS		: TEXCOORD1;
};

OUTPUT_VERTEX vs_main( VS_INPUT input )
{
	OUTPUT_VERTEX o = (OUTPUT_VERTEX)0;
	o.pos = input.pos.xyww;
	o.tc0 = input.tc0;
	o.invS.x = 1.0 / screenDimensions.x;
	o.invS.y = 1.0 / screenDimensions.y;
	return o;
};

float4 ps_main( OUTPUT_VERTEX v ) : COLOR
{
	int i=0;
	float4 map[9];
	map[0] = tex2D( inputSampler, v.tc0.xy + tap1.xy * v.invS );
	map[1] = tex2D( inputSampler, v.tc0.xy + tap2.xy * v.invS );
	map[2] = tex2D( inputSampler, v.tc0.xy + tap3.xy * v.invS );
	map[3] = tex2D( inputSampler, v.tc0.xy + tap4.xy * v.invS );
	map[4] = tex2D( inputSampler, v.tc0.xy + tap5.xy * v.invS );
	map[5] = tex2D( inputSampler, v.tc0.xy + tap6.xy * v.invS );
	map[6] = tex2D( inputSampler, v.tc0.xy + tap7.xy * v.invS );
	map[7] = tex2D( inputSampler, v.tc0.xy + tap8.xy * v.invS );
	map[8] = tex2D( inputSampler, v.tc0.xy + tap9.xw * v.invS );
	
	float4 mean = float4(0,0,0,0);
	for (i=0; i < 9; i++)
	{
		mean += map[i];
	}
	mean /= 9.0;
	
	float4 total = float4(0,0,0,0);
	for (i=0; i < 9; i++)
	{
		total += (mean - map[i]) * (mean - map[i]);
	}
	//float variance = dot( total, 1.0/9.0 );
	float variance = total;
	float4 result;
	result.xyz = mean;
	result.a = variance;
	return result;
};

STANDARD_PP_TECHNIQUE( compile vs_2_0 vs_main(), compile ps_2_0 ps_main() )

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


struct VERTEX_OUTPUT
{
	float4 pos		: POSITION;
	float3 tc0		: TEXCOORD0;
	float2 invS		: TEXCOORD1;
};

VERTEX_OUTPUT vs_main( VS_INPUT input )
{
	VERTEX_OUTPUT o = (VERTEX_OUTPUT)0;
	o.pos = input.pos.xyww;
	o.tc0 = input.tc0;
	o.invS.x = 1.0 / screenDimensions.x;
	o.invS.y = 1.0 / screenDimensions.y;
	return o;
};

float4 ps_main( VERTEX_OUTPUT v ) : COLOR
{
	int i =0;
	float4 sample[4], s0, s1, s2, s3, lowestVariance, l2;
	float s0a, s1a, s2a, s3a, la, l2a;
	float4 c1,c2;
	
	sample[0] = tex2D( inputSampler, v.tc0.xy + tap1.xy * v.invS );
	sample[1] = tex2D( inputSampler, v.tc0.xy + tap2.xy * v.invS );
	sample[2] = tex2D( inputSampler, v.tc0.xy + tap3.xy * v.invS );
	sample[3] = tex2D( inputSampler, v.tc0.xy + tap4.xy * v.invS );
	
	s0a = sample[0].a;
	s1a = sample[1].a;
	s2a = sample[2].a;
	s3a = sample[3].a;
	
	if( s0a < s1a )
	{
		la = s0a;
		c1 = sample[0];
	}
	else
	{
		la = s1a;
		c1 = sample[1];
	}
	
	if( s2a < s3a )
	{
		l2a = s2a;
		c2 = sample[2];
	}
	else
	{
		l2a = s3a;
		c2 = sample[3];
	}
	
	if( l2a < la )
	{
		return c2;
	}
	else
	{
		return c1;
	}	
	
	return lowestVariance;
};

STANDARD_PP_TECHNIQUE( compile vs_2_0 vs_main(), compile ps_2_0 ps_main() )
#include "post_processing.fxh"


DECLARE_EDITABLE_TEXTURE( punchcard, punchcardSampler, CLAMP, WRAP, POINT, "Offset punchcard texture (see the Content Creation Manual)" )
DECLARE_EDITABLE_TEXTURE( inputTexture0, input0Sampler, CLAMP, WRAP, LINEAR, "Film scratches/lines map 1" )
DECLARE_EDITABLE_TEXTURE( inputTexture1, input1Sampler, CLAMP, WRAP, LINEAR, "Film scratches/lines map 2" )
DECLARE_EDITABLE_TEXTURE( inputTexture2, input2Sampler, CLAMP, CLAMP, LINEAR, "Film grain/dust map 1" )
DECLARE_EDITABLE_TEXTURE( inputTexture3, input3Sampler, CLAMP, CLAMP, LINEAR, "Film grain/dust map 2" )
DECLARE_EDITABLE_TEXTURE( inputTexture4, input4Sampler, CLAMP, CLAMP, LINEAR, "Film grain/dust map 3" )
DECLARE_EDITABLE_TEXTURE( inputTexture5, input5Sampler, CLAMP, CLAMP, LINEAR, "Film grain/dust map 4" )


float alpha
<
	bool artistEditable = true;
	float UIMin = 0;
	float UIMax = 5.0;
	int UIDigits = 2;
	string UIDesc = "Alpha value";
> = 0.5;


float speed
<
	bool artistEditable = true;
	float UIMin = 0.01;
	float UIMax = 0.5;
	int UIDigits = 2;
	string UIDesc = "Speed for cycling through the punchcard texture";
> = 0.1;


float scale
<
	bool artistEditable = true;
	float UIMin = 1.0;
	float UIMax = 50.0;
	int UIDigits = 1;
	string UIDesc = "Scale factor for the dust and scratches";
> = 50.0;


float punchcardOffset
<
	bool artistEditable = true;
	float UIMin = 0;
	float UIMax = 5.0;
	int UIDigits = 2;
	string UIDesc = "Initial punchcard offset";
> = 0.0;


float time : Time;


float4 ps_main( PS_INPUT input ) : COLOR0
{
	float2 tc1;
	float t = (time+punchcardOffset) * speed;
	float columnToUV = 1.0/6.0;

	float4 punchcard1 = tex2D( punchcardSampler, float2(columnToUV * 0.5, t) );
	float4 punchcard2 = tex2D( punchcardSampler, float2(columnToUV * 1.5, t) );
	
	float4 punchcard3 = tex2D( punchcardSampler, float2(columnToUV * 2.5, t) );
	float4 punchcard4 = tex2D( punchcardSampler, float2(columnToUV * 3.5, t) );
	float4 punchcard5 = tex2D( punchcardSampler, float2(columnToUV * 4.5, t) );
	float4 punchcard6 = tex2D( punchcardSampler, float2(columnToUV * 5.5, t) );
	
	punchcard1.xy += float2(-0.5,-0.5);
	punchcard1.xy *= scale;
	
	punchcard2.xy += float2(-0.5,-0.5);
	punchcard2.xy *= scale;
	
	punchcard3.xy += float2(-0.5,-0.5);
	punchcard3.xy *= scale;
	
	punchcard4.xy += float2(-0.5,-0.5);
	punchcard4.xy *= scale;
	
	punchcard5.xy += float2(-0.5,-0.5);
	punchcard5.xy *= scale;
	
	punchcard6.xy += float2(-0.5,-0.5);
	punchcard6.xy *= scale;
	
	float2 tc0;
	tc0 = input.tc0;
	tc0 += float2(-0.5,-0.5);
	tc0 *= scale;
	tc0 -= float2(-0.5,-0.5);

	float4 t0 = tex2D( input0Sampler, tc0 + punchcard1.xy );
	float4 t1 = tex2D( input1Sampler, tc0 + punchcard2.xy );
	float4 t2 = tex2D( input2Sampler, tc0 + punchcard3.xy );
	float4 t3 = tex2D( input3Sampler, tc0 + punchcard4.xy );
	float4 t4 = tex2D( input4Sampler, tc0 + punchcard5.xy );
	float4 t5 = tex2D( input5Sampler, tc0 + punchcard6.xy );
	
	float a = t0.a * punchcard1.b + t1.a * punchcard2.b + t2.a + t3.a + t4.a + t5.a;
	float3 colour = t0.rgb * t0.aaa * 10.0 + t1.rgb * t1.aaa * 10.0 + t2.rgb + t3.rgb + t4.rgb + t5.rgb;
	float4 bb = float4( colour.r, colour.g, colour.b, a * alpha );
	return bb;
}

STANDARD_PP_TECHNIQUE( compile vs_2_0 vs_pp_default(), compile ps_2_0 ps_main() )

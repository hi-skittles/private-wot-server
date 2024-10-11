#include "post_processing.fxh"

//Depth of Field (variable CoC)

DECLARE_EDITABLE_TEXTURE( inputTexture, inputSampler, CLAMP, CLAMP, LINEAR, "Input texture/render target" )
DECLARE_EDITABLE_TEXTURE( depthBlurTexture, depthBlurSampler, CLAMP, CLAMP, LINEAR, "Depth blur texture (calculated by a Lens Simulation effect)" )

float maxCoC
<
	bool artistEditable = true;
	float UIMin = 0;
	float UIMax = 64.0;
	int UIDigits = 1;
	string UIDesc = "Maximum circle of confusion (pixels)";
> = 10.0 ;


//screenDimensions is (w,h,halfw,halfh)
float4 screenDimensions : Screen;


//uoffset, voffset, weight, unused
float4 tap0	<
	bool artistEditable = true;
	string UIDesc = "Filter tap 0 (uoffset, voffset, weight, unused)";
> = ( 0.0, 0.0, 0.0, 0.0 );

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

float4 tap10	<
	bool artistEditable = true;
	string UIDesc = "Filter tap 10 (uoffset, voffset, weight, unused)";
> = { 0.0, 0.0, 0.0, 0.0 };

float4 tap11	<
	bool artistEditable = true;
	string UIDesc = "Filter tap 11 (uoffset, voffset, weight, unused)";
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
	o.invS.x = 1.0 / screenDimensions.x;
	o.invS.y = 1.0 / screenDimensions.y;
	return o;
};


#define sumTap( tapOffset )\
tapCoord = v.tc0 + tapOffset * width;\
tapColour = tex2D( inputSampler, tapCoord );\
tapDepthBlur = tex2D( depthBlurSampler, tapCoord );\
tapContribution = (tapDepthBlur.x > centerDepthBlur.x) ? 1.0 : tapDepthBlur.y;\
colourSum += tapColour * tapContribution;\
totalContribution += tapContribution;


float4 ps_main( NTF_PS_INPUT v ) : COLOR
{
	//calculate depth of pixel, and circle of confusion radius
	float4 colourSum = tex2D( inputSampler, v.tc0 );
	float totalContribution = 1.0;
	float2 centerDepthBlur = tex2D( depthBlurSampler, v.tc0 );
		
	float sizeCoC = abs(centerDepthBlur.y) * maxCoC;
	
	float width =  v.invS * sizeCoC;

	float2 tapCoord;
	float4 tapColour;
	float2 tapDepthBlur;
	float tapContribution;
	
	sumTap( tap0 )
	sumTap( tap1 )
	sumTap( tap2 )
	sumTap( tap3 )
	sumTap( tap4 )
	sumTap( tap5 )
	sumTap( tap6 )
	sumTap( tap7 )
	sumTap( tap8 )
	sumTap( tap9 )
	sumTap( tap10 )
	sumTap( tap11 )
	
	float4 finalColour = colourSum / totalContribution;
	return finalColour;
};


STANDARD_PP_TECHNIQUE( compile vs_3_0 vs_main(), compile ps_3_0 ps_main() )

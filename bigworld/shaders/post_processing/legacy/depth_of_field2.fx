#include "post_processing.fxh"

DECLARE_EDITABLE_TEXTURE( inputTexture, inputSampler, CLAMP, CLAMP, LINEAR, "Input texture/render target" )
DECLARE_EDITABLE_TEXTURE( depthBlurTexture, depthBlurSampler, CLAMP, CLAMP, LINEAR, "Depth blur texture (calculated by a Lens Simulation effect)" )
DECLARE_EDITABLE_TEXTURE( bokehTexture, bokehSampler, CLAMP, CLAMP, LINEAR, "Shape of the blur" )


float maxCoC
<
	bool artistEditable = true;
	float UIMin = 0;
	float UIMax = 64.0;
	int UIDigits = 1;
	string UIDesc = "Maximum circle of confusion (pixels)";
> = 4.0 ;


float bokehAmount
<
	bool artistEditable = true;
	float UIMin = 0;
	float UIMax = 4.0;
	int UIDigits = 2;
	string UIDesc = "Usually 1.0, but can be used to adjust the bokeh brightness";
> = 1.0;


//screenDimensions is (w,h,halfw,halfh)
float4 screenDimensions : Screen;

struct DOF2_VS_INPUT
{
	float4 pos:			POSITION;
	float2 tc0:			TEXCOORD0;
};

struct DOF2_PS_INPUT
{
	float4 pos		: POSITION;
	float2 tc0		: TEXCOORD0;
	float3 col		: COLOR;
	float ptSize	: PSIZE0;
};


DOF2_PS_INPUT vs_main( VS_INPUT input )
{
	DOF2_PS_INPUT o = (DOF2_PS_INPUT)0;	
	float4 depthBlur = tex2Dlod( depthBlurSampler, float4( input.tc0.xy, 0, 0.0 ) );
	float4 colourBuffer = tex2Dlod( inputSampler, float4( input.tc0.xy, 0, 0.0 ) );
	float pSize = abs(depthBlur.g) * maxCoC;
	
	o.pos = input.pos.xyww;
	o.tc0 = input.tc0;
	o.col = colourBuffer * bokehAmount;
	o.ptSize = pSize;

	return o;
};


//This pixel shader is drawing point sprites and accumulates
//all point sprites into a colour buffer.  The alpha is written
//out, and is subsequently used for blending with the frame buffer.
float4 ps_main( DOF2_PS_INPUT v ) : COLOR
{
	float4 bokeh = tex2D( bokehSampler, v.tc0 );	//this tc0 comes from point sprite interpolator, not our vertex shader.
	bokeh.rgb = bokeh.rgb * v.col.rgb * bokeh.a;
	return bokeh;
};


technique PP_TECHNIQUE
{
   pass Pass_0
   {
      ALPHATESTENABLE = TRUE;
      ALPHAREF = 1;
      SRCBLEND = <srcBlend>;
      DESTBLEND = <destBlend>;
      ZENABLE = FALSE;
      FOGENABLE = FALSE;
      ALPHABLENDENABLE = TRUE;
      POINTSPRITEENABLE = TRUE;
      STENCILENABLE = FALSE;
      VertexShader = compile vs_3_0 vs_main();
      PixelShader = compile ps_3_0 ps_main();
   }
}

#include "post_processing.fxh"

//Thin Lens Simulation

DECLARE_EDITABLE_TEXTURE( inputTexture, inputSampler, CLAMP, CLAMP, LINEAR, "Input texture/render target" )

USES_DEPTH_TEXTURE

float focalLen
<
	bool artistEditable = true;
	float UIMin = 0.0;
	float UIMax = 0.5;
	int UIDigits = 3;
	string UIDesc = "Focal length (metres)";
> = 0.1;			//fLen = 100mm


float aperture
<
	bool artistEditable = true;
	float UIMin = 0.001;
	float UIMax = 0.5;
	int UIDigits = 3;
	string UIDesc = "Lens Apperture (metres)";
> = 0.05;		//aperture = f/2


float focalDistance
<
	bool artistEditable = true;
	float UIMin = 0.1;
	float UIMax = 100.0;
	int UIDigits = 3;
	string UIDesc = "Focal distance";
> = 2.5;


float imagePlaneDistance
<
	bool artistEditable = true;
	float UIMin = 0.005;
	float UIMax = 0.05;
	int UIDigits = 3;
	string UIDesc = "Image plane distance (in addition to the focal length)";
> = 0.01;


float maxCoC
<
	bool artistEditable = true;
	float UIMin = 0;
	float UIMax = 64.0;
	int UIDigits = 1;
	string UIDesc = "Maximum circle of confusion (pixels)";
> = 10.0 ;


float scale
<
	bool artistEditable = true;
	float UIMin = 0;
	float UIMax = 5000.0;
	int UIDigits = 0;
	string UIDesc = "Scaling factor for this effect";
> = 2000.0;			//this just scales the overall dof effect


struct NTF_PS_INPUT
{
	float4 pos		: POSITION;
	float3 tc0		: TEXCOORD0;
};


NTF_PS_INPUT vs_main( VS_INPUT input )
{
	NTF_PS_INPUT o = (NTF_PS_INPUT)0;
	o.pos = input.pos.xyww;
	o.tc0 = input.tc0;
	return o;
};


float4 ps_main( NTF_PS_INPUT v ) : COLOR
{
	//calculate depth of pixel, and circle of confusion radius
	float sceneDepth = decodeDepth( depthSampler, v.tc0 );
	float sceneDepthWorld = sceneDepth * farPlane.x + (focalLen);	//add the lens focal length to the depth values, since depth=0 is an object sitting directly on the end of the camera lens;
	float zFocus = focalDistance + (focalLen + imagePlaneDistance);
	float pixCoC = aperture * focalLen * (zFocus - sceneDepthWorld) / (zFocus * (sceneDepthWorld - focalLen));
	float blurAmount = -pixCoC * scale / maxCoC;
	float4 result = float4( sceneDepth, blurAmount, 0, 0);
	return result;
};


float4 ps_preview( NTF_PS_INPUT v ) : COLOR
{
	//calculate depth of pixel, and circle of confusion radius
	float sceneDepthWorld = decodeDepth( depthSampler, v.tc0 ) + (focalLen);	//add the lens focal length to the depth values, since depth=0 is an object sitting directly on the end of the camera lens;
	float zFocus = focalDistance + (focalLen + imagePlaneDistance);
	float pixCoC = aperture * focalLen * (zFocus - sceneDepthWorld) / (zFocus * (sceneDepthWorld - focalLen));
	float blurAmount = -pixCoC * scale / maxCoC;
	float4 result = float4( -blurAmount, blurAmount, 0, 1);
	return result;
};


STANDARD_PP_TECHNIQUE( compile vs_3_0 vs_main(), compile ps_3_0 ps_main() )
STANDARD_PREVIEW_TECHNIQUE( compile vs_3_0 vs_main(), compile ps_3_0 ps_preview() )

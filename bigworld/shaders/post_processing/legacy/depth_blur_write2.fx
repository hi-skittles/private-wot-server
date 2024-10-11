#include "post_processing.fxh"

DECLARE_EDITABLE_TEXTURE( inputTexture, inputSampler, CLAMP, CLAMP, POINT, "Input texture/render target" )
USES_DEPTH_TEXTURE

const float falloff
<
	bool artistEditable = true;
	float UIMin = 0;
	float UIMax = 10.0;
	int UIDigits = 1;
	string UIDesc = "How quickly it becomes out of focus";
> = 2.0;

const float zNear
<
	bool artistEditable = true;
	float UIMin = 0;
	float UIMax = 1.0;
	int UIDigits = 2;
	string UIDesc = "Near focal distance";
> = 0.0;

const float zFar
<
	bool artistEditable = true;
	float UIMin = 0;
	float UIMax = 1.0;
	int UIDigits = 2;
	string UIDesc = "Far focal distance";
> = 0.5;

const float g_blurRadius
<
	bool artistEditable = true;
	float UIMin = 0;
	float UIMax = 1.0;
	int UIDigits = 2;
	string UIDesc = "blur radius on the focal plane";
> = 0.6;

const float g_blurRadiusSpeed
<
	bool artistEditable = true;
	float UIMin = 0;
	float UIMax = 1.0;
	int UIDigits = 2;
	string UIDesc = "blur speed on the radius on the focal plane";
> = 0.6;

//-------------------------------------------------------------------------------------------------
float calcBlurCoeff(in float radius, in float2 texCoord)
{
	//-- screen space position.
	float2 scp  = 2.0f * texCoord - 1.0f;

	//-- squared length from the center of the screen to the current point.
	float  qlen = (scp.x * scp.x + scp.y * scp.y);

	//return lerp(0, 1, qlen / (radius * radius)) * blurRadiusSpeed;
	return smoothstep(0, radius, qlen / (radius * radius)) * g_blurRadiusSpeed;
};

//-------------------------------------------------------------------------------------------------
float4 ps_main( PS_INPUT i ) : COLOR
{
	//-- 1. find the post perspective z value.
	float depth = decodeDepth(depthSampler, i.tc0.xy);

	//-- 2. calulate down- and up-slopes.
	float downSlope = saturate((zNear - depth) * falloff);
	float upSlope   = saturate((depth - zFar ) * falloff);
	
	//-- 3. calculate the main and radius blur amount.
	float mainblurAmount   = max(downSlope, upSlope);
	float radiusBlurAmount = falloff * calcBlurCoeff(g_blurRadius, i.tc0.xy);
	
	//-- 4. calculate the final blur amount.
	float blurAmount = max(mainblurAmount, radiusBlurAmount);

	//-- 5. return ...
	return float4(depth, blurAmount, 0, 0);
	
};

STANDARD_PP_TECHNIQUE( compile vs_2_0 vs_pp_default(), compile ps_2_0 ps_main() )

#include "post_processing.fxh"

texture dirtTexture
< 
	bool artistEditable = true; 
	string UIName = "Lens dirt texture";
	string UIDesc = "The main lens dirt texture map ";
>;

texture alphaTexture
< 
	bool artistEditable = true; 
	string UIName = "Lens alpha texture";
	string UIDesc = "The lens alpha texture map which rotates depending on the sun-camera angle ";
>;

texture sunLightTexture1
< 
	bool artistEditable = true; 
	string UIName = "Sun texture 1";
	string UIDesc = "The sun lights texture map which rotates depending on the sun-camera angle ";
>;

texture sunLightTexture2
< 
	bool artistEditable = true; 
	string UIName = "Sun texture 2";
	string UIDesc = "The sun lights texture map which rotates depending on the sun-camera angle ";
>;

const float dirtBrightness
<
	bool artistEditable = true;
	float UIMin = 0.1;
	float UIMax = 30.0;
	int UIDigits = 2;
	string UIName = "Dirt brightness";
	string UIDesc = "Dirt brightness";
> = 1.0f;

const float sunBrightness
<
	bool artistEditable = true;
	float UIMin = 0.1;
	float UIMax = 10.0;
	int UIDigits = 2;
	string UIDesc = "Sun brightness";
	string UIName = "Sun brightness";
> = 1.0f;

const float sunSize
<
	bool artistEditable = true;
	float UIMin = 0.01;
	float UIMax = 0.9;
	int UIDigits = 2;
	string UIDesc = "Sun size";
	string UIName = "Sun size";
> = 0.3f;

sampler dirtSampler			= BW_SAMPLER(dirtTexture, CLAMP)
sampler alphaSampler		= BW_SAMPLER(alphaTexture, CLAMP)
sampler sunSampler1			= BW_SAMPLER(sunLightTexture1, CLAMP)
sampler sunSampler2			= BW_SAMPLER(sunLightTexture2, CLAMP)


// Vertex Formats
struct OUTPUT
{
	float4 pos:					POSITION;
	float2 tc:					TEXCOORD0;	
	float4 offset:				TEXCOORD1; // cos1 sin1 cos2 sin2 - for rotation os sun textures
	float shininess:			TEXCOORD3; // brightness of sun and dirt depending on camera-sun angle
	float2 sunTC:				TEXCOORD4; // sun screen coords
};

//-------------------------------------------------------------------------------------------------

float2 sunScreenPos()
{
	float3 sunWorldPos = g_cameraPos - g_sunLight.m_dir * g_farPlane.x;
	float4 projPos = mul(float4(sunWorldPos,1.0), g_viewProjMat);
	projPos.xyz /= projPos.w;
	projPos.x = projPos.x * 0.5 + 0.5f;
	projPos.y = projPos.y * 0.5 - 0.5f;
	projPos.y = -projPos.y;
	return projPos.xy;
}


OUTPUT vs_main( VS_INPUT i )
{
	OUTPUT o = (OUTPUT)0;
	o.pos = i.pos;
	o.tc  = i.tc0;
	
	float2 angle = mul(g_sunLight.m_dir, g_viewProjMat).xy;
	o.offset = float4(cos(angle.x), sin(angle.x), cos(angle.y), sin(angle.y));

	o.shininess = pow(saturate(-dot(g_cameraDir, g_sunLight.m_dir)), 0.5f);
	o.sunTC = sunScreenPos();
	
	return o;
}


float4 ps_main( OUTPUT i ) : COLOR
{
	float sunVisibility = saturate(0.2f + g_sunVisibility);
	float2x2 rotationMatrix = float2x2(i.offset.x, -i.offset.y, i.offset.y, i.offset.x);
	float2 tc = mul(i.tc - 0.5f, rotationMatrix) * 0.7f + 0.5f;
	float4 diffuseMap = tex2D( dirtSampler, i.tc );
	float4 alphaMap = tex2D( alphaSampler, tc);

	float2 sunTC1 = mul((i.tc - i.sunTC) / (sunSize * 2.7f * sunVisibility), rotationMatrix) * 0.707106f + float2(0.5f, 0.5f);
	float4 sunMap1 = tex2D( sunSampler1, sunTC1);
	rotationMatrix = float2x2(i.offset.z, -i.offset.w, i.offset.w, i.offset.z);
	float2 sunTC2 = mul((i.tc - i.sunTC) / (sunSize * 5.0f * sunVisibility), rotationMatrix) * 0.707106f + float2(0.5f, 0.5f);
	float4 sunMap2 = tex2D( sunSampler2, sunTC2);
	
	float4 colour = 0;
	colour.xyz = (	diffuseMap.xyz * alphaMap.x * dirtBrightness * i.shininess * sunVisibility * 3.0f+ 
							sunMap1.xyz * sunBrightness * i.shininess * g_sunVisibility * 0.8f + 
							sunMap2.xyz * sunBrightness * i.shininess * g_sunVisibility * 0.5f);	
	colour.w = 1.0f;

	return colour;
}


STANDARD_PP_TECHNIQUE(compile vs_2_0 vs_main(), compile ps_2_0 ps_main());


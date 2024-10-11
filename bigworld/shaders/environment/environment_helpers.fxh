#include "stdinclude.fxh"
#include "deferred_shading.fxh"

#define BW_ARTIST_EDITABLE_CLOUD_MAP( varName, uiName )\
texture varName\
< \
	bool artistEditable = true;\
	string UIName = uiName;\
	string UIDesc = "The texture map for the cloud layer.  Alpha represents cloud density.";\
>;

#define BW_ARTIST_EDITABLE_FOG_MAP( varName, uiName )\
texture varName\
< \
	bool artistEditable = true;\
	string UIName = uiName;\
	string UIDesc = "The map that defines how much and where fogging is applied to the cloud layer";\
>;

#define BW_ARTIST_EDITABLE_RIM_DETECT_WIDTH( varName, uiName )\
float varName\
<\
	bool artistEditable = true;\
	string UIName = uiName;\
	string UIDesc = "The width of the detected cloud rim";\
	float UIMin = 0;\
	float UIMax = 1;\
	int UIDigits = 2;\
> = 0.3;

#define BW_ARTIST_EDITABLE_RIM_DETECT_POWER( varName, uiName )\
float varName\
<\
	bool artistEditable = true;\
	string UIName = uiName;\
	string UIDesc = "The sharpness of the detected cloud rim";\
	float UIMin = 0;\
	float UIMax = 32;\
	int UIDigits = 2;\
> = 5.0;

#define BW_ARTIST_EDITABLE_RIM_POWER( varName, uiName )\
float varName\
<\
	bool artistEditable = true;\
	string UIName = uiName;\
	string UIDesc = "The overall sharpness of the rim lighting effect";\
	float UIMin = 0;\
	float UIMax = 32;\
	int UIDigits = 2;\
> = 5.0;

#define BW_ARTIST_EDITABLE_RIM_STRENGTH( varName, uiName )\
float varName\
<\
	bool artistEditable = true;\
	string UIName = uiName;\
	string UIDesc = "The overall strength of the rim lighting effect";\
	float UIMin = 0;\
	float UIMax = 5;\
	int UIDigits = 2;\
> = 1.5;

#define BW_ARTIST_EDITABLE_SCATTERING_POWER( varName, uiName )\
float varName\
<\
	bool artistEditable = true;\
	string UIName = uiName;\
	string UIDesc = "The overall sharpness of the mie (forward) scattering";\
	float UIMin = 0;\
	float UIMax = 32;\
	int UIDigits = 2;\
> = 5.0;

#define BW_ARTIST_EDITABLE_SCATTERING_STRENGTH( varName, uiName )\
float varName\
<\
	bool artistEditable = true;\
	string UIName = uiName;\
	string UIDesc = "The overall strength of mie (forward) scattering";\
	float UIMin = 0;\
	float UIMax = 5;\
	int UIDigits = 2;\
> = 1.0;

#define BW_ARTIST_EDITABLE_WIND_SPEED( varName, uiName )\
float varName\
<\
	bool artistEditable = true;\
	string UIName = uiName;\
	string UIDesc = "How much the cloud layer responds to wind in the game.";\
	string UIWidget = "Spinner";\
	float UIMax = 1;\
	float UIMin = 0;\
	int UIDigits = 3;\
> = 0;

#define BW_ARTIST_EDITABLE_TEXTURE_TILE( varName, uiName )\
float2 varName\
<\
	bool artistEditable = true;\
	string UIName = uiName;\
	string UIDesc = "The texture tiling amount for the cloud layer";\
	string UIWidget = "Spinner";\
	float UIMax = 10;\
	float UIMin = -10;\
	int UIDigits = 3;\
> = {1,1};

#define BW_ARTIST_EDITABLE_SUN_FLARE_OCCLUSION( varName, uiName )\
float varName\
<\
	bool artistEditable = true;\
	string UIName = uiName;\
	string UIDesc = "The texture factor used when testing sun flare occlusion";	\
	float UIMax = 255;\
	float UIMin = 0;\
	int UIDigits = 0;\
> = 128.0;

#define BW_ARTIST_EDITABLE_YPARALLAX( yVarName, yUIName )\
float yVarName\
<\
	bool artistEditable = true;\
	string UIName = yUIName;\
	string UIDesc = "How much the cloud layer moves up and down with the camera";\
	float UIMax = 0.1;\
	float UIMin = 0.0;\
	int UIDigits = 3;\
> = 0.01;

#define BW_ARTIST_EDITABLE_PARALLAX( yVarName, yUIName, xzVarName, xzUIName )\
float yVarName\
<\
	bool artistEditable = true;\
	string UIName = yUIName;\
	string UIDesc = "How much the cloud layer moves up and down with the camera";\
	float UIMax = 0.1;\
	float UIMin = 0.0;\
	int UIDigits = 3;\
> = 0.01;\
\
float xzVarName\
<\
	bool artistEditable = true;\
	string UIName = xzUIName;\
	string UIDesc = "How much the cloud layer moves around with camera. Must be 1.0 for shadow casters. Should be 0 for ring geometry.";\
	float UIMax = 1.0;\
	float UIMin = 0.0;\
	int UIDigits = 3;\
> = 0.0;

#define BW_ARTIST_EDITABLE_SHADOW_CONTRAST( varName, uiName )\
float varName\
<\
	bool artistEditable = true;\
	string UIName = uiName;\
	string UIDesc = "Contrast for shadow casting";\
	string UIWidget = "Spinner";\
	float UIMax = 1;\
	float UIMin = 0;\
	int UIDigits = 3;\
> = 0.0;

#define BW_ARTIST_EDITABLE_SUNLIGHT_AMOUNT( varName, uiName )\
float varName\
<\
	bool artistEditable = true;\
	string UIName = uiName;\
	string UIDesc = "Amount the skybox repsonds to the sunlight.";\
	string UIWidget = "Spinner";\
	float UIMax = 1;\
	float UIMin = 0;\
	int UIDigits = 2;\
> = 1.0;

#define BW_ARTIST_EDITABLE_FOG_RESPONSE( varName, uiName )\
float varName\
<\
	bool artistEditable = true;\
	string UIName = uiName;\
	string UIDesc = "Amount the skybox repsonds to any extra fogging in the scene.";\
	string UIWidget = "Spinner";\
	float UIMax = 1;\
	float UIMin = 0;\
	int UIDigits = 2;\
> = 0.5;


#define BW_CLOUD_MAP_SAMPLER( varName, mapName, wrapMode )\
sampler varName = sampler_state\
{\
	Texture = (mapName);\
	ADDRESSU = wrapMode;\
	ADDRESSV = wrapMode;\
	ADDRESSW = CLAMP;\
	MAGFILTER = LINEAR;\
	MINFILTER = LINEAR;\
	MIPFILTER = LINEAR;\
	MAXMIPLEVEL = 0;\
	MIPMAPLODBIAS = 0;\
};


#define BW_FOG_MAP_SAMPLER( varName, mapName )\
sampler varName = sampler_state\
{\
	Texture = (mapName);\
	ADDRESSU = CLAMP;\
	ADDRESSV = CLAMP;\
	ADDRESSW = CLAMP;\
	MAGFILTER = LINEAR;\
	MINFILTER = LINEAR;\
	MIPFILTER = LINEAR;\
	MAXMIPLEVEL = 0;\
	MIPMAPLODBIAS = 0;\
};

int		occlusionTest : EnvironmentOcclusionTest;
int		occlusionAlphaRef : EnvironmentOcclusionAlphaRef;
int		shadowDraw : EnvironmentShadowDraw;

//this value scales from a world wind animation position, to tex coord adjustments.
//it is further modified per-cloud-map by an artist editing the wind speed parameter.
float2 windScale = { -0.0019, 0.0019 };

//return the pixel shader index for the technique, based on whether
//we are occlusion testing or drawing the shadow map.
int pixelShaderIndex()
{
	if (occlusionTest)
		return 1;
	else if (shadowDraw)
		return 2;
	else return 0;
}

//return the pixel shader index for the technique, based on whether
//we are occlusion testing or drawing the shadow map.
int vertexShaderIndex()
{
	if (shadowDraw)
		return 1;	
	else return 0;
}

//return the alpha reference for the technique.
int alphaReference()
{
	if (!occlusionTest)
		return 0;
	else
		return (occlusionAlphaRef);
};

//return z-enable for the technique, based on whether
//we are occlusion testing or drawing the shadow map.
int enableZ()
{
	return (occlusionTest == 0) && (shadowDraw == 0);
}

//return alpha test for the technique, based on whether
//we are occlusion testing or drawing the shadow map.
int enableAlphaTest()
{
	return (occlusionTest == 1) && (shadowDraw == 0);
}


float2 cloudLayerTexCoords( in float2 itc, in float2 textureTile, in float windSpeed )
{
	float4 tc = float4(itc, 1, 1);
	float2 otc;	
	otc.x = tc.x * textureTile.x + windSpeed * g_windAnimation.x * windScale.x;
	otc.y = tc.y * textureTile.y + windSpeed * g_windAnimation.y * windScale.y;
	return otc;
}


//adjust skybox xz verts to put them in world coordinates.
float2 worldVertexPosition( in float2 xz, in float meshSize )
{
	float skyFarPlane = g_farPlane.z;	
	float2 opos = xz * (skyFarPlane / meshSize);
	return opos;
}


//transform camera world movemements into skybox local space texture coords.
float2 adjustTexCoords(in float2 tc, in float parallax, in float cameraPosX, in float cameraPosZ)
{
	float2 otc;			
	
	float invSkyFarPlane = g_farPlane.w;
	otc.x = tc.x + (0.5 * cameraPosX * invSkyFarPlane * parallax);
	otc.y = tc.y - (0.5 * cameraPosZ * invSkyFarPlane * parallax);
		
	return otc;
}

//--------------------------------------------------------------------------------------------------
float4 cloudLighting(
	in float3 light,
	in float4 diffuse,
	in float4 diffuseMap,	
	in float rimDetectWidth,
	in float rimDetectPower,
	in float rimPower,
	in float rimStrength,
	in float scatteringPower,
	in float scatteringStrength,
	in float4 fogColour,
	in float4 fogAmount )
{	
	float density = diffuseMap.w;	
	float3 scattering = pow( light, scatteringPower );
	float rimDetect = pow((1.0 - saturate(density - rimDetectWidth)), rimDetectPower);	
	float rimScattering = pow( light, rimPower );
	float litRim = rimDetect * rimScattering;
	
	//darken diffuse map based on sunlight / ambient lighting amount.
	float4 colour = diffuse * diffuseMap;	
	
	//add all the scattering stuff
	colour.xyz += g_sunLight.m_color * scattering * scatteringStrength + litRim * rimStrength;
	colour.w = diffuseMap.w;
	
	//and blend to fog colour
	colour.xyz = lerp(colour.xyz, fogColour.xyz, fogAmount);
	return colour;
}


float4 staticSkyBoxLighting( in float howMuch )
{
	float3 color = g_sunLight.m_color;

	float lum = (0.3f * color.r + 0.59f * color.g + 0.11f * color.b);
	lum = lum * howMuch + (1-howMuch);
	return float4(lum,lum,lum,1.0);
}

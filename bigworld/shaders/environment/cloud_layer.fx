#include "environment_helpers.fxh"
#include "stdinclude.fxh"

// This constant is read by the tools to know if it should setup a rendering
// environment that is appropriate for a skybox.
bool isBWSkyBox = true;

float4x4 envShadowTransform : EnvironmentShadowTransform;
//control - (fogDensity, windMultiplier, occludes, fade in/out)
float4 control : SkyBoxController = {1,1,1,1};

struct OutputNormalMap
{
	float4 pos:     POSITION;
	float2 tc:      TEXCOORD0;
	float2 ntc:     TEXCOORD1;
	float3 dLight1: TEXCOORD2;
	float3 normal:	TEXCOORD3;
	float4 worldPos: TEXCOORD4;
	float4 diffuse: COLOR0;	
};

//NOTE - this is set to true because currently ME hard-disables fogging
//bool fogEnabled : FogEnabled = true;
bool fogEnabled = true;

BW_ARTIST_EDITABLE_CLOUD_MAP( diffuseMap, "Diffuse Map" )
BW_ARTIST_EDITABLE_FOG_MAP( fogMap, "Fog Map" )
BW_ARTIST_EDITABLE_RIM_DETECT_WIDTH( rimDetectWidth, "Rim Detect Width" )
BW_ARTIST_EDITABLE_RIM_DETECT_POWER( rimDetectPower, "Rim Detect Power" )
BW_ARTIST_EDITABLE_RIM_POWER( rimPower, "Rim Power" )
BW_ARTIST_EDITABLE_RIM_STRENGTH( rimStrength, "Rim Strength" )
BW_ARTIST_EDITABLE_SCATTERING_POWER( scatteringPower, "Scattering Power" )
BW_ARTIST_EDITABLE_SCATTERING_STRENGTH( scatteringStrength, "Scattering Strength" )
BW_ARTIST_EDITABLE_WIND_SPEED( windSpeed, "Wind Speed" )
BW_ARTIST_EDITABLE_TEXTURE_TILE( textureTile, "Texture Tile" )
BW_ARTIST_EDITABLE_SUN_FLARE_OCCLUSION( sunFlareOcclusion, "Sun Flare Occlusion" )
BW_ARTIST_EDITABLE_PARALLAX( parallax, "Vertical Parallax", xzParallax, "Horizontal Parallax" )
BW_ARTIST_EDITABLE_SHADOW_CONTRAST( shadowContrast, "Shadow Contrast" )

/*float yPoint
<
	bool artistEditable = true;
	string UIName = "Curvature";
	string UIDesc = "Curvature of sky layer";
	string UIWidget = "Spinner";
	float UIMax = 100;
	float UIMin = 0;
	int UIDigits = 2;
> = 0.0;*/

//This should be set to the max bounds of the object
float meshSize = 50.f;

//Note - yPoint used to created hacked normals,
//remove when normal modifier in max can be used instead
float yPoint = 0.0;

#include "unskinned_effect_include.fxh"

BW_CLOUD_MAP_SAMPLER( diffuseSampler, diffuseMap, WRAP )
BW_FOG_MAP_SAMPLER( fogSampler, fogMap )


OutputNormalMap vs_main( VertexXYZNUV i )
{
	OutputNormalMap o = (OutputNormalMap)0;
	
	o.normal = float3(0,0,1);//-directionalLights[0].direction;
	
	//adjust input y for parallax
	i.pos.xyz *= 25.0f;
	i.pos.y -= g_cameraPos.y * parallax;
	
	//this is just so we get the world space TS matrix
	BW_PROJECT_POSITION(o)
	            
	o.pos  = mul(i.pos, g_environmentMat).xyww;
	o.dLight1 = float3(0,0,0);//directionalLight( -o.normal, directionalLights[0] );
	
	float4 tc = float4(BW_UNPACK_TEXCOORD(i.tc), 1, 1);
	o.tc = adjustTexCoords( BW_UNPACK_TEXCOORD(i.tc), xzParallax, g_cameraPos.x, g_cameraPos.z );
	o.tc = cloudLayerTexCoords( o.tc, textureTile, windSpeed );
	o.ntc = tc;	
	
	//o.diffuse = directionalLights[0].colour + ambientColour;	
	//o.diffuse = fogColour;
	
	//calculate current luminance of sun (move to effect constant, not per-vertex)
	o.diffuse = dot( float3(0.3,0.59,0.11), g_sunLight.m_color.r ) + float4(sunAmbientTerm(), 0);
	
	return o;
}


OutputNormalMap vs_shadows( VertexXYZNUV i )
{
	OutputNormalMap o = (OutputNormalMap)0;
		
	o.normal = (0,-1,0);	
	i.pos.xz = worldVertexPosition( i.pos.xz, meshSize );
	
	//this is just so we get the world space TS matrix
	BW_PROJECT_POSITION(o)
	
	o.pos = mul(i.pos, envShadowTransform);
	o.pos.z = o.pos.w;		
	o.tc = adjustTexCoords( BW_UNPACK_TEXCOORD(i.tc), xzParallax, g_cameraPos.x, g_cameraPos.z );
	o.tc = cloudLayerTexCoords( o.tc, textureTile, windSpeed );
	o.ntc = BW_UNPACK_TEXCOORD(i.tc);	
	o.diffuse = (1,1,1,1);
	o.dLight1 = (0,0,0,0);
	
	return o;
}


float4 ps_main( OutputNormalMap i ) : COLOR0
{	
	half4 diffuseMap = tex2D( diffuseSampler, i.tc );
	half4 fogAmount;
	if (fogEnabled)
		fogAmount = tex2D( fogSampler, i.ntc );
	else
		fogAmount = half4(0,0,0,0);
	half3 normal = i.normal;	
	
	fogAmount = saturate( fogAmount + control.xxxx );			
			
	half3 light = half3(1,1,1);//saturate( dot( normalize(i.dLight1.xyz), normal ) );	
	half4 colour = cloudLighting(
							light,
							i.diffuse,
							diffuseMap,
							rimDetectWidth,
							rimDetectPower,
							scatteringPower,
							scatteringStrength,
							rimPower,
							rimStrength,
							g_fogParams.m_color,
							fogAmount );								
	colour.w *= control.w;

	colour.xyz *= 1 + colour.a * g_HDRParams.x;

	return colour;
}


float4 ps_simple( OutputNormalMap i ) : COLOR0
{
	float4 diffuseMap = tex2D( diffuseSampler, i.tc );
	float4 fogAmount = tex2D( fogSampler, i.ntc );
	float4 colour = i.diffuse * diffuseMap;
	colour.w = diffuseMap.w;
	colour.xyz = lerp(colour.xyz, g_fogParams.m_color.xyz, fogAmount);
	colour.w *= control.w;
	return colour;
}


float4 ps_occlusion( OutputNormalMap i ) : COLOR0
{
	float4 diffuseMap = tex2D( diffuseSampler, i.tc );
	diffuseMap.xyz = 1.0;
	diffuseMap.w *= control.w;
	return diffuseMap;
}


float4 ps_shadowDraw( OutputNormalMap i ) : COLOR0
{
	float4 diffuseMap = tex2D( diffuseSampler, i.tc );
	diffuseMap.xyz = 0.0;
	diffuseMap.w *= diffuseMap.w;
	diffuseMap.w *= shadowContrast;
	diffuseMap.w *= control.w;	
	return diffuseMap;
}


BW_COLOR_TECHNIQUE(false, false)
{
   pass P0
   {
      ALPHATESTENABLE = enableAlphaTest();
      ALPHAREF = (sunFlareOcclusion);
      ZENABLE = enableZ();
      SRCBLEND = SRCALPHA;
      DESTBLEND = INVSRCALPHA;
      ZWRITEENABLE = FALSE;
      ZFUNC = LESSEQUAL;
      FOGENABLE = FALSE;
      ALPHABLENDENABLE = TRUE;      
      POINTSPRITEENABLE = FALSE;
      STENCILENABLE = FALSE;
      CULLMODE = NONE;
      
      TexCoordIndex[0] = 0;
      TexCoordIndex[1] = 1;
      TexCoordIndex[2] = 2;
      TexCoordIndex[3] = 3;

      VertexShader = compile vs_2_0 vs_main();
      PixelShader = compile ps_2_0 ps_main();
   }
}

BW_SHADOW_TECHNIQUE( false )
{
   pass P0
   {
      ALPHATESTENABLE = enableAlphaTest();
      ALPHAREF = 0;
      ZENABLE = FALSE;
      SRCBLEND = SRCALPHA;
      DESTBLEND = INVSRCALPHA;
      ZWRITEENABLE = FALSE;
      ZFUNC = LESSEQUAL;
      FOGENABLE = FALSE;
      ALPHABLENDENABLE = TRUE;      
      POINTSPRITEENABLE = FALSE;
      STENCILENABLE = FALSE;
      CULLMODE = NONE;
      
      TexCoordIndex[0] = 0;
      TexCoordIndex[1] = 1;
      TexCoordIndex[2] = 2;
      TexCoordIndex[3] = 3;

      VertexShader = compile vs_2_0 vs_main();
      PixelShader = compile ps_2_0 ps_shadowDraw();
   }
}


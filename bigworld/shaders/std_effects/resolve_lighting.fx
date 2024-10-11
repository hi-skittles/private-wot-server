#include "stdinclude.fxh"
#include "deferred_shading.fxh"
#include "read_g_buffer.fxh"
#include "shadow_helpers.fxh"


//--------------------------------------------------------------------------------------------------
//-- SSAO constants

bool g_enableSSAO;
texture g_texSSAO;
sampler g_texSSAOSml
{
	Texture = (g_texSSAO);
	ADDRESSU = CLAMP;
	ADDRESSV = CLAMP;
	ADDRESSW = CLAMP;
	MAGFILTER = POINT;
	MINFILTER = POINT;
	MIPFILTER = POINT;
	MAXANISOTROPY = 1;
	MAXMIPLEVEL = 0;
	MIPMAPLODBIAS = 0;
};

//--------------------------------------------------------------------------------------------------
sampler g_speedTreeMaterialsMapSml = sampler_state
{
	Texture = <g_speedTreeMaterialsMap>;
	MipFilter = POINT;
	MinFilter = POINT;
	MagFilter = POINT;
};

//--------------------------------------------------------------------------------------------------
half4 get_speedtree_diffuse(in half materialID)
{
	static const half2 g_invSize = half2(1, 1 / 127.0);
	return tex2D(g_speedTreeMaterialsMapSml, half2(0, materialID) * g_invSize).rgba;
}

//--------------------------------------------------------------------------------------------------
half3 get_speedtree_ambient(in half materialID)
{
	static const half2 g_invSize = half2(1, 1 / 127.0);
	return tex2D(g_speedTreeMaterialsMapSml, half2(0.5, materialID) * g_invSize).rgb;
}

//--------------------------------------------------------------------------------------------------
struct DS_LIGHT_DIR_VS
{
	float3 pos			:	POSITION;
	float2 tc			:	TEXCOORD0;
};

//--------------------------------------------------------------------------------------------------
struct DS_LIGHT_OMNI_VS_INSTANCED
{
	float3 pos	  :	POSITION;
	float2 tc	  :	TEXCOORD0;
	float3 normal :	NORMAL;

	//-- instance data.
	InstancingStream instance;
};

//--------------------------------------------------------------------------------------------------
struct DS_LIGHT_OMNI_VS2PS_INSTANCED
{
	float4 pos			:	POSITION;

	//-- omni light data.
	float3 wPos			:	TEXCOORD1;
	float4 color		:	TEXCOORD2;
	float2 attenuation	:	TEXCOORD3;
};

//--------------------------------------------------------------------------------------------------
struct DS_LIGHT_OMNI_VS
{
	float3 pos	  :	POSITION;
	float2 tc	  :	TEXCOORD0;
	float3 normal :	NORMAL;
};

//--------------------------------------------------------------------------------------------------
struct DS_LIGHT_OMNI_VS2PS
{
	float4 pos	:	POSITION;
};

//--------------------------------------------------------------------------------------------------
struct DS_LIGHT_SPOT_VS
{
	float3 pos	  :	POSITION;
	float2 tc	  :	TEXCOORD0;
	float3 normal :	NORMAL;
};


//-- constants.
const float			g_omniLightLODRadiusError;
const PointLight	g_omniLight;
const SpotLight		g_spotLight;

/*
sampler g_ssShadowMapSml = sampler_state	
{									
	Texture = (g_ssShadowMap);
	ADDRESSU = CLAMP;	
	ADDRESSV = CLAMP;
	ADDRESSW = CLAMP;
	MAGFILTER = POINT;
	MINFILTER = POINT;
	MIPFILTER = POINT;
	MAXANISOTROPY = 1;
	MAXMIPLEVEL   = 0;
	MIPMAPLODBIAS = 0;
};

//--------------------------------------------------------------------------------------------------
half calcShadow( float2 tc, in half backedShadow, in half viewZ, bool enableShadows )
{
	if ( enableShadows )
	{
		// Channels: r - dynamic; g - semi terrain; b - semi object
		half3 shadows = tex2D( g_ssShadowMapSml, tc ).rgb;
		half  semi    = saturate( shadows.b + shadows.g );
		float t       = saturate( ( viewZ - g_shadowBlendParams.x ) / g_shadowBlendParams.y + 1.f );
		float s       = saturate( shadows.r + ( shadows.b * g_shadowBlendParams.z ) + shadows.g );

		return min( 1.0h - lerp( s, semi, t ), backedShadow );
	}

	return backedShadow;
}
*/

//-- returns SSAO coefficients for ambient (.x) and diffuse + specular (.y) terms.
//--------------------------------------------------------------------------------------------------
half2 calcSSAO(in float2 tc, in float2 amount, bool enableSSAO)
{
	half2 o = half2(1.0h, 1.0h);

	if (enableSSAO)
	{
		//-- combine screen space and backed ambient occlusion factors.
		half ssao = tex2D(g_texSSAOSml, tc).x;

		//-- apply ao differently on ambient and lighting components.
		half ambient  = lerp(1.0h, ssao, amount.x);
		half lighting = lerp(1.0h, ssao, amount.y);

		//--
		o = half2(ambient, lighting);
	}

	return o;
}

//-- returns terrain SSAO coefficients for ambient (.x) and diffuse + specular (.y) terms.
//--------------------------------------------------------------------------------------------------
half2 calcTerrainSSAO(in float2 tc, in float2 amount, in half backedAO, bool enableSSAO)
{
	half2 o = half2(1.0h, 1.0h);

	if (enableSSAO)
	{
		//-- combine screen space and backed ambient occlusion factors.
		half ssao = tex2D(g_texSSAOSml, tc).x;
		ssao = lerp(0.0h, backedAO * 2.0h, ssao);

		//-- apply ao differently on ambient and lighting components.
		half ambient  = lerp(1.0h, ssao, amount.x);
		half lighting = lerp(1.0h, ssao, amount.y);

		//--
		o = half2(ambient, lighting);
	}

	return o;
}

//--------------------------------------------------------------------------------------------------
BW_DS_LIGHT_PASS_VS2PS VS_DIR(DS_LIGHT_DIR_VS i)
{
	BW_DS_LIGHT_PASS_VS2PS o = (BW_DS_LIGHT_PASS_VS2PS)0;

	o.pos = float4(i.pos, 1);
	o.tc  = i.tc;

	return o;
}

//--------------------------------------------------------------------------------------------------
float4 PS_DIR(BW_DS_LIGHT_PASS_VS2PS i, uniform bool enableShadows, uniform bool enableSSAO) : COLOR0
{
	//-- read g-buffer properties.
	float3 wPos        = g_buffer_readWorldPos(i.tc, g_nvStereoParams.w);
	half3  wNormal     = g_buffer_readWorldNormal(i.tc);
	half3  albedo      = g_buffer_readAlbedo(i.tc);
	float  linearZ	   = g_buffer_readLinearZ(i.tc) * g_farPlane.x;
	half   specAmount  = g_buffer_readSpecAmount(i.tc);

	//--
	half2  ssao	 = calcSSAO(i.tc, g_SSAOParams[2].xy, enableSSAO);
	half   shadow = calcShadow(i.tc, 1.0h, linearZ, enableShadows);

	//--
	float3 vecToCam  = g_cameraPos.xyz - wPos;
	float  distToCam = length(vecToCam);

	//--
	half3 ambient  = albedo * sunAmbientTerm();
	half3 diffTerm = albedo * sunDiffuseTerm(wNormal);
	half3 specTerm = g_specularParams.x * specAmount * sunSpecTerm(wNormal, vecToCam / distToCam, g_specularParams.y);

	//-- lighting equation.
	half3 result = ssao.x * ambient + ssao.y * shadow * (diffTerm + specTerm);

	//-- fog.
	result = applyFogTo(result, bw_vertexFog(float4(wPos, 1), distToCam));

	return float4(result, 0);
}

//--------------------------------------------------------------------------------------------------
float4 PS_DIR_SPEEDTREE(BW_DS_LIGHT_PASS_VS2PS i, uniform bool enableDynamicShadows, uniform bool enableSSAO) : COLOR0
{
	//-- read g-buffer properties.
	float3 wPos        = g_buffer_readWorldPos(i.tc, g_nvStereoParams.w);
	half3  wNormal     = g_buffer_readWorldNormal(i.tc);
	half3  albedo      = g_buffer_readAlbedo(i.tc);
	float  linearZ	   = g_buffer_readLinearZ(i.tc) * g_farPlane.x;
	half   specAmount  = g_buffer_readSpecAmount(i.tc);
	half   materialID  = g_buffer_readUserData1(i.tc);

	//--
	half2  ssao	  = calcSSAO(i.tc, g_SSAOParams[0].xy, enableSSAO);
	half   shadow = calcShadow(i.tc, 1.0h, linearZ, enableDynamicShadows);

	//--
	float3 vecToCam  = g_cameraPos.xyz - wPos;
	float  distToCam = length(vecToCam);

	//-- specific for the speedtree lighting formula.
	half3 speedtree_ambient		= get_speedtree_ambient(materialID);
	half4 speedtree_diffuse		= get_speedtree_diffuse(materialID);
	half  speedtree_lightAdjust = speedtree_diffuse.w;

	//--
	half3 ambient  = albedo * sunAmbientTerm() * speedtree_ambient;
	half3 diffTerm = albedo * sunDiffuseTerm(wNormal, speedtree_lightAdjust) * speedtree_diffuse.xyz;
	half3 specTerm = specAmount * sunSpecTerm(wNormal, vecToCam / distToCam);

	//-- lighting equation.
	half3 result = ssao.x * ambient + ssao.y * shadow * (diffTerm + specTerm);

	//-- fog.
	result = applyFogTo(result, bw_vertexFog(float4(wPos, 1), distToCam));

	return float4(result, 0);
}

//--------------------------------------------------------------------------------------------------
float4 PS_DIR_TERRAIN(BW_DS_LIGHT_PASS_VS2PS i, uniform bool enableDynamicShadows, uniform bool enableSSAO) : COLOR0
{
	//-- read g-buffer properties.
	float3 wPos          = g_buffer_readWorldPos(i.tc, g_nvStereoParams.w);
	half3  wNormal       = g_buffer_readWorldNormal(i.tc);
	half3  albedo        = g_buffer_readAlbedo(i.tc);
	float  linearZ	     = g_buffer_readLinearZ(i.tc) * g_farPlane.x;
	half   specAmount    = g_buffer_readSpecAmount(i.tc);
	half   backedShadow  = 1.0h - g_buffer_readUserData1(i.tc, false);
	half   backedAO		 = g_buffer_readUserData2(i.tc, false);

	//--
	half2  ssao   = calcTerrainSSAO(i.tc, g_SSAOParams[1].xy, backedAO, enableSSAO);
	half   shadow = calcShadow(i.tc, backedShadow, linearZ, enableDynamicShadows);

	//--
	float3 vecToCam  = g_cameraPos.xyz - wPos;
	float  distToCam = length(vecToCam);

	//--
	half3 ambient  = albedo * sunAmbientTerm();
	half3 diffTerm = albedo * sunDiffuseTerm(wNormal);
	half3 specTerm = specAmount * sunSpecTerm(wNormal, vecToCam / distToCam);

	//-- lighting equation.
	half3 result = ssao.x * ambient + ssao.y * shadow * (diffTerm + specTerm);

	//-- fog.
	result = applyFogTo(result, bw_vertexFog(float4(wPos, 1), distToCam));

	return float4(result, 0);
}

//--------------------------------------------------------------------------------------------------
DS_LIGHT_OMNI_VS2PS_INSTANCED VS_OMNI_INSTANCED(DS_LIGHT_OMNI_VS_INSTANCED i)
{
	DS_LIGHT_OMNI_VS2PS_INSTANCED o = (DS_LIGHT_OMNI_VS2PS_INSTANCED)0;

	//-- Note: additional scale LOD radius error needed beacuse to minimize overhead on VS size we
	//--	   use very low poly spheres (about 150-200 faces).
	float  scale = (i.instance.v2.x + g_omniLightLODRadiusError) * 100.0f;
	float3 pos   = i.instance.v0.xyz;

	float4x4 world = float4x4(
		float4(scale, 0, 0, 0),
		float4(0, scale, 0, 0),
		float4(0, 0, scale, 0),
		float4(pos, 1)
		);

	float4 wPos = mul(float4(i.pos, 1), world);
	o.pos       = mul(wPos, g_viewProjMat);

	//-- omni light data.
	o.wPos			= pos;
	o.color			= i.instance.v1;
	o.attenuation	= i.instance.v2.xy;

	return o;
}

//--------------------------------------------------------------------------------------------------
DS_LIGHT_OMNI_VS2PS VS_OMNI(DS_LIGHT_OMNI_VS i)
{
	DS_LIGHT_OMNI_VS2PS o = (DS_LIGHT_OMNI_VS2PS)0;

	//-- Note: additional scale LOD radius error needed beacuse to minimize overhead on VS size we
	//--	   use very low poly spheres (about 150-200 faces).
	float  scale = (g_omniLight.attenuation.x + g_omniLightLODRadiusError) * 100.0f;
	float3 pos   = g_omniLight.position.xyz;

	float4x4 world = float4x4(
		float4(scale, 0, 0, 0),
		float4(0, scale, 0, 0),
		float4(0, 0, scale, 0),
		float4(pos, 1)
		);

	float4 wPos = mul(float4(i.pos, 1), world);
	o.pos       = mul(wPos, g_viewProjMat);

	return o;
}

//--------------------------------------------------------------------------------------------------
float4 PS_OMNI_STENCIL_PASS(DS_LIGHT_OMNI_VS2PS_INSTANCED i) : COLOR0
{
	//-- is not important what we send to the buffer, because writing to the color buffer disabled
	//-- by the render state.
	return float4(0,0,0,0);
}

//--------------------------------------------------------------------------------------------------
float4 PS_OMNI_MAIN_PASS(DS_LIGHT_OMNI_VS2PS_INSTANCED i, in float2 vPos : VPOS) : COLOR0
{
	float2 screenXY = SC2TC(vPos);

	//-- resore omni light.
	PointLight light = (PointLight)0;
	light.position    = float4(i.wPos, 0.0f);
	light.colour      = i.color * 2.0f;
	light.attenuation = float4(i.attenuation, 0.0f, 0.0f);

	//-- read g-buffer properties.
	float3 wPos       = g_buffer_readWorldPos(screenXY, g_nvStereoParams.w);
	half3  wNormal    = g_buffer_readWorldNormal(screenXY);
	half3  albedo     = g_buffer_readAlbedo(screenXY);
	half   specAmount = g_buffer_readSpecAmount(screenXY);

	//-- do lighting equation.
	half3 diffTerm = albedo * pointLight(wPos, wNormal, light);
	half3 specTerm = g_specularParams.x * specAmount * pointSpecLight(wPos, wNormal, normalize(g_cameraPos.xyz - wPos), light, g_specularParams.y);

	return float4(diffTerm + specTerm, 0);
	//return float4(albedo, 0);
	//return float4(0.1f,0,0,0);
}

//--------------------------------------------------------------------------------------------------
float4 PS_OMNI_FALLBACK_PASS(DS_LIGHT_OMNI_VS2PS i, in float2 vPos : VPOS) : COLOR0
{
	float2 screenXY = SC2TC(vPos);

	//-- read g-buffer properties.
	float3 wPos       = g_buffer_readWorldPos(screenXY, g_nvStereoParams.w);
	half3  wNormal    = g_buffer_readWorldNormal(screenXY);
	half3  albedo     = g_buffer_readAlbedo(screenXY);
	half   specAmount = g_buffer_readSpecAmount(screenXY);

	PointLight light = g_omniLight;
	light.colour *= 2.0f;

	//-- do lighting equation.
	half3 diffTerm = albedo * pointLight(wPos, wNormal, light);
	half3 specTerm = g_specularParams.x * specAmount * pointSpecLight(wPos, wNormal, normalize(g_cameraPos.xyz - wPos), light, g_specularParams.y);

	return float4(diffTerm + specTerm, 0);
	//return float4(albedo, 0);
	//return float4(0.1f,0,0,0);
}

//--------------------------------------------------------------------------------------------------
BW_DS_LIGHT_PASS_VS2PS VS_SPOT(DS_LIGHT_DIR_VS i)
{
	BW_DS_LIGHT_PASS_VS2PS o = (BW_DS_LIGHT_PASS_VS2PS)0;

	o.pos = float4(i.pos, 1);

	return o;
}

//--------------------------------------------------------------------------------------------------
float4 PS_SPOT(BW_DS_LIGHT_PASS_VS2PS i, in float2 vPos : VPOS) : COLOR0
{
	float2 screenXY = SC2TC(vPos);

	//-- read g-buffer properties.
	float3 wPos       = g_buffer_readWorldPos(screenXY, g_nvStereoParams.w);
	half3  wNormal    = g_buffer_readWorldNormal(screenXY);
	half3  albedo     = g_buffer_readAlbedo(screenXY);
	half   specAmount = g_buffer_readSpecAmount(screenXY);

	//-- do lighting equation.
	half3 spec = half3(0,0,0);
	half3 diff = half3(0,0,0);
	spotSpecLight(wPos, wNormal, normalize(g_cameraPos.xyz - wPos), g_spotLight, diff, spec);

	half3 diffTerm = albedo * diff * 2;
	half3 specTerm = specAmount * spec;

	return float4(diffTerm + specTerm, 0);
}

//--------------------------------------------------------------------------------------------------
PixelShader g_sunPixelShaders[12] = 
{
	//-- dynamic shadows OFF
	compile ps_3_0 PS_DIR(false, true),
	compile ps_3_0 PS_DIR(false, false),
	compile ps_3_0 PS_DIR_SPEEDTREE(false, true),
	compile ps_3_0 PS_DIR_SPEEDTREE(false, false),
	compile ps_3_0 PS_DIR_TERRAIN(false, true),
	compile ps_3_0 PS_DIR_TERRAIN(false, false),

	//-- dynamic shadows ON
	compile ps_3_0 PS_DIR(true, true),
	compile ps_3_0 PS_DIR(true, false),
	compile ps_3_0 PS_DIR_SPEEDTREE(true, true),
	compile ps_3_0 PS_DIR_SPEEDTREE(true, false),
	compile ps_3_0 PS_DIR_TERRAIN(true, true),
	compile ps_3_0 PS_DIR_TERRAIN(true, false)
};

//-- 
//--------------------------------------------------------------------------------------------------
technique SUN							
{	
	pass SPEEDTREE
	{
		ZENABLE = TRUE;
		ZFUNC = ALWAYS;
		ZWRITEENABLE = FALSE;
		FOGENABLE = FALSE;		
		ALPHABLENDENABLE = FALSE;
		ALPHATESTENABLE = FALSE;
		CULLMODE = CW;
		COLORWRITEENABLE = 0xFF;

		//-- use stencil to mark only valid g-buffer pixels (i.e. only speedtree pixels.)
		STENCILENABLE = TRUE;
		STENCILFUNC = NOTEQUAL;
		STENCILWRITEMASK = 0x00;
		STENCILMASK = G_STENCIL_USAGE_SPEEDTREE;
		STENCILREF = 0;

		VertexShader = compile vs_3_0 VS_DIR();
		PixelShader  = g_sunPixelShaders[6 * g_enableShadows + (g_enableSSAO ? 2 : 3)];
	}

	pass TERRAIN
	{
		//-- use stencil to mark only valid g-buffer pixels (i.e. only terrain pixels.)
		STENCILMASK = G_STENCIL_USAGE_TERRAIN;

		VertexShader = compile vs_3_0 VS_DIR();
		PixelShader  = g_sunPixelShaders[6 * g_enableShadows + (g_enableSSAO ? 4 : 5)];
	}

	pass OTHER_OPAQUE
	{
		//-- use stencil to mark only valid g-buffer pixels (i.e. not sky pixels)
		STENCILMASK = G_STENCIL_USAGE_FLORA | G_STENCIL_USAGE_OTHER_OPAQUE;

		VertexShader = compile vs_3_0 VS_DIR();
		PixelShader  = g_sunPixelShaders[6 * g_enableShadows + (g_enableSSAO ? 0 : 1)];
	}
}

//-- ToDo: reconsider state bucket. I feel that we can gretly improve this.
//--------------------------------------------------------------------------------------------------
technique OMNI_COMMON
{	
	pass CLEAR_STENCIL_PASS
	{
		ALPHATESTENABLE = FALSE;
		CULLMODE = NONE;
		ZENABLE = TRUE;
		ZFUNC = ALWAYS;
		ZWRITEENABLE = FALSE;
		FOGENABLE = FALSE;		
		ALPHABLENDENABLE = FALSE;
		POINTSPRITEENABLE = FALSE;
		COLORWRITEENABLE = 0x00;

		STENCILENABLE = TRUE;
		STENCILWRITEMASK = G_STENCIL_CUMSTOM_WRITE_MASK;
		STENCILMASK = G_STENCIL_CUMSTOM_WRITE_MASK;
		STENCILREF = 0;
		STENCILFUNC = ALWAYS;
		STENCILPASS = REPLACE;
		STENCILFAIL = REPLACE;
		STENCILZFAIL = REPLACE;
										
		VertexShader = compile vs_3_0 VS_OMNI_INSTANCED();
		PixelShader  = compile ps_3_0 PS_OMNI_STENCIL_PASS();
	}

	pass STENCIL_PASS							
	{		
		CULLMODE = CW;
		ZFUNC = GREATEREQUAL;

		STENCILENABLE = TRUE;
		STENCILFUNC = ALWAYS;
		STENCILPASS = INCR;
		STENCILFAIL = KEEP;
		STENCILZFAIL = KEEP;
										
		VertexShader = compile vs_3_0 VS_OMNI_INSTANCED();
		PixelShader  = compile ps_3_0 PS_OMNI_STENCIL_PASS();
	}

	pass MAIN_PASS
	{
		CULLMODE = CCW;
		ZFUNC = LESSEQUAL;
		ZWRITEENABLE = FALSE;
		ALPHABLENDENABLE = TRUE;
		SRCBLEND = ONE;				
		DESTBLEND = ONE;
		BLENDOP = ADD;	
		COLORWRITEENABLE = 0xFF;

		STENCILENABLE = TRUE;
		STENCILFUNC = LESS;
		STENCILPASS = KEEP;
		STENCILZFAIL = DECRSAT;
		STENCILFAIL = KEEP;
		STENCILREF = 0;
										
		VertexShader = compile vs_3_0 VS_OMNI_INSTANCED();
		PixelShader  = compile ps_3_0 PS_OMNI_MAIN_PASS();
	}
}

//--------------------------------------------------------------------------------------------------
technique OMNI_FALLBACK
{			
	pass Pass_0
	{
		ALPHATESTENABLE = FALSE;
		CULLMODE = CW;
		ZENABLE = TRUE;
		ZFUNC = GREATEREQUAL;
		ZWRITEENABLE = FALSE;
		FOGENABLE = FALSE;
		ALPHABLENDENABLE = TRUE;
		SRCBLEND = ONE;		
		DESTBLEND = ONE;
		BLENDOP = ADD;
		POINTSPRITEENABLE = FALSE;
		COLORWRITEENABLE = 0xFF;
		STENCILENABLE = FALSE;
	
		VertexShader = compile vs_3_0 VS_OMNI();
		PixelShader  = compile ps_3_0 PS_OMNI_FALLBACK_PASS();
	}
}

//-- ToDo: reconsider state bucket. I fell that we can gretly improve this.
//--------------------------------------------------------------------------------------------------
technique SPOT_FALLBACK							
{									
	pass Pass_0							
	{		
		ALPHATESTENABLE = FALSE;
		ZENABLE = FALSE;			
		FOGENABLE = FALSE;		
		ZWRITEENABLE = FALSE;
		ALPHABLENDENABLE = TRUE;
		SRCBLEND = ONE;				
		DESTBLEND = ONE;
		BLENDOP = ADD;	
		POINTSPRITEENABLE = FALSE;
		STENCILENABLE = FALSE;
		CULLMODE = NONE;

		//-- use stencil to mark only valid g-buffer pixels (i.e. only speedtree pixels.)
		STENCILENABLE = TRUE;
		STENCILFUNC = NOTEQUAL;
		STENCILWRITEMASK = 0x00;
		STENCILMASK = G_STENCIL_USAGE_ALL_OPAQUE;
		STENCILREF = 0;

		VertexShader = compile vs_3_0 VS_SPOT();
		PixelShader  = compile ps_3_0 PS_SPOT();
	}
}

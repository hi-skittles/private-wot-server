// ----------------------------------------------------------------------------
// Water shaders
// ----------------------------------------------------------------------------

#include "stdinclude.fxh"
#include "water_common.fxh"
#include "read_g_buffer.fxh"
#include "shadow_helpers.fxh"

#define WATER_REFLECTION_FADE_ENABLED 1

float4		scale					= {0.08,0.08,0.08,0.08};
float4		simulationTransformX	= {1,0,0,0};
float4		simulationTransformY	= {0,1,0,0};
float4		bumpTexCoordTransformX	= {1,0,0,0};
float4		bumpTexCoordTransformY	= {0,1,0,0};
float4		bumpTexCoordTransformX2 = {1,0,0,0};
float4		bumpTexCoordTransformY2 = {0,1,0,0};
float4		reflectionTint			= {1,1,1,1};
float4		refractionTint			= {0.1,0.9,1.0,1};
float4		foamColour				= {0.8, 0.8, 0.8, 1.0};

float		simpleReflection		= 0.0;

float4		deepColour				= {0, 0.21, 0.35, 1.0};

float4		screenOffset			= { 0,0,0,0 };

float		simulationTiling		= 1.f; //used to artificially increase the sim resolution for the rain
float		sunPower				= 32.0;
float		sunScale				= 1.0;
float		smoothness				= 0.0;

float		texScale				= 0.0;
float		freqX					= 1.7;
float		freqZ					= 2.2;
float		maxDepth				= 100.f;
float		fadeDepth				= 10.f;
float		waveHeight				= 0.5f;
float		simulationPower			= 1.0f;

float		animationInterpolator   = 0.0f;

float		cellSizeHalfY			= 5.0f;
float		cellSizeHalfX			= 5.0f;
float		textureTesselation      = 5.0f;
float		foamTiling				= 1.0;

bool		useRefraction			= true;
bool		enableWaterShadows		= false;

float4x4	world;

BW_FRESNEL
BW_NON_EDITABLE_ALPHA_TEST
BW_NON_EDITABLE_ALPHA_BLEND

// ----------------------------------------------------------------------------
// Section: Textures
// ----------------------------------------------------------------------------

texture		reflectionMap;
texture		screenFadeMap;
texture		normalMap1;
texture		normalMap2;
texture		reflectionCubeMap;

// ----------------------------------------------------------------------------
// Section: Samplers
// ----------------------------------------------------------------------------
sampler screenFadeSampler			= BW_SAMPLER(screenFadeMap, WRAP)
sampler reflectionSampler			= BW_SAMPLER(reflectionMap, CLAMP)
sampler normalSampler1				= BW_SAMPLER(normalMap1, WRAP)
sampler normalSampler2				= BW_SAMPLER(normalMap2, WRAP)
samplerCUBE reflectionCubeSampler	= BW_SAMPLER( reflectionCubeMap, CLAMP )


// ----------------------------------------------------------------------------
// Section: Vertex formats
// ----------------------------------------------------------------------------

struct VS_INPUT
{
   float4 pos:				POSITION;
   float3 bankDirDist:		NORMAL;
   float4 diffuse:			COLOR0;
   float2 tc:				TEXCOORD0;
};

// ----------------------------------------------------------------------------
// Section: Pixel shader input
// ----------------------------------------------------------------------------

struct PS_INPUT_RT
{
	float4 pos:				POSITION;
	float4 tc:				TEXCOORD0;
	float4 worldPos:		TEXCOORD1;
	float4 reflect_refract:	TEXCOORD2;
	float4 W_sim:			TEXCOORD3;
	float4 foam0:			TEXCOORD4;
	float3 bankDirDist:		TEXCOORD5;
	float4 alpha:			COLOR0;
	float fog:				FOG;	
};

// standard water technique
#define WATER_TECHNIQUE(name, vs, ps, alphaBlendEnabled)\
technique name\
{\
	pass Pass_0\
	{\
		ALPHATESTENABLE = <alphaTestEnable>;\
		ALPHAREF = <alphaReference>;\
		ALPHAFUNC = GREATER;\
		ALPHABLENDENABLE = alphaBlendEnabled;\
		SRCBLEND = <srcBlend>;\
		DESTBLEND = <destBlend>;\
		ZENABLE = TRUE;\
		ZWRITEENABLE = <useRefraction>;\
		ZFUNC = LESSEQUAL;		\
		CULLMODE = NONE;\
		VertexShader = vs;\
		PixelShader  = ps;\
		FOGENABLE = FALSE;\
	}\
}



#define cHalf	0.5f

float AnimationHeight(float3 pos, float2 bankDir, float _alpha)
{
	float2 cPos = float2(pos.x*bankDir.x + pos.z*bankDir.y, -pos.x*bankDir.y + pos.z*bankDir.x);
	float anim = pos.y + sin(g_time*freqX+cPos.x) * sin(1.5707f * cos(g_time*freqZ+cPos.y)) * 0.9015f * _alpha * waveHeight;
	return anim;
}

// ----------------------------------------------------------------------------
// Section: Vertex Shaders
// ----------------------------------------------------------------------------

PS_INPUT_RT vs_main ( VS_INPUT i, uniform bool modifyEdge, uniform bool stereo )
{
	PS_INPUT_RT o = (PS_INPUT_RT)0;
	
	if (modifyEdge)
		i.pos.y = AnimationHeight(i.pos, i.bankDirDist.xy, i.diffuse.w);
		
	float4 projPos = mul( i.pos, mul(world, g_viewProjMat) );
	o.pos = projPos;

	// Transform bump coordinates
	o.tc.x = dot( float4(i.tc.xy, 0,1), bumpTexCoordTransformX );
	o.tc.y = dot( float4(i.tc.xy,0,1), bumpTexCoordTransformY );

	o.tc.z = dot( float4(i.tc.xy,0,1), bumpTexCoordTransformX2 );
	o.tc.w = dot( float4(i.tc.xy,0,1), bumpTexCoordTransformY2 );

	o.W_sim.x = (i.tc.x + simulationTransformX.w)*simulationTransformX.x + cHalf;
	o.W_sim.y = (i.tc.y + simulationTransformY.w)*simulationTransformY.y + cHalf;

	o.bankDirDist = i.bankDirDist;

	//-- Compile time branching.
	if (stereo)//-- set here some default values, the real values will be calculated later in pixel shader.
		o.reflect_refract = float4(0,0,0,0);
	else
	{
		//-- Map projected position to the reflection and refraction texture
		float2 reflect_refractPos = (projPos.xy + projPos.w) * cHalf;
		// Reflection transform
		o.reflect_refract = float4( reflect_refractPos.x, -reflect_refractPos.y, 
									-reflect_refractPos.y, reflect_refractPos.x );
	}

    o.worldPos.xyz = mul(float4(i.pos.xyz, 1.0f), world);
	o.worldPos.w = o.pos.w;
    o.alpha = i.diffuse;
	
	// calc fog
	o.fog = bw_vertexFog(o.worldPos, o.pos.w);
	
	//TODO: use the far plane here ....
	o.W_sim.w = projPos.z;
	o.W_sim.z = projPos.w;
	// foam tex coords
	float foamAnim = frac( bumpTexCoordTransformX.x  );
	o.foam0.xy = i.pos.xz * float2( 0.02, 0.02 ) * 0.333f * 16 * 3;
	//o.foam0.wz = i.pos.zx * float2( 0.02, 0.02 ) * 0.333f * 20 * 2.1f + foamAnim;

	o.foam0 *= foamTiling;
	return o;
};

half3 getSunLight( half3 eye, half3 normal )
{
	half3 halfAngle = normalize(-g_sunLight.m_dir + eye);
	half specular = sunScale * pow( saturate( dot( halfAngle, normal ) ), sunPower );
	return (specular * g_sunLight.m_color * g_HDRParams.y);
}

half4 computeDependentCoords(float4 reflect_refract, half3 normal, float w, float zScale,
							 out half2 oScreenCoords)
{
	// Perform division by W only once
	half ooW = 1.0f / w;
	// Vectorize the dependent UV calculations (reflect = .xy, refract = .wz)
	half4 vN = normal.xyxy;	
	half4 screenCoords = (reflect_refract * ooW) + screenOffset;

	oScreenCoords = screenCoords.wz;
	// Fade out the distortion offset at the screen borders to avoid artifacts.
	half3 screenFade = tex2D( screenFadeSampler, screenCoords.xy  );	
	half4 dependentTexCoords = vN * scale * screenFade.xxxx;

	return (dependentTexCoords + screenCoords);
}

half3 generateSurfaceNormal( float2 tc, half3 simNormal )
{
	//setting two crossing normal samplers to simulate realistic waves
   	// Load normal and expand range
	half3 vNormal1 = tex2D( normalSampler1, tc ) * 2.0f - 1.0f;
	half3 vNormal2 = tex2D( normalSampler2, tc ) * 2.0f - 1.0f;
	half3 vNormal = lerp(vNormal1, vNormal2, animationInterpolator);

	vNormal = normalize( vNormal );
	vNormal = lerp( vNormal, half3(0,0,1), smoothness);		
	vNormal.x += simulationPower * simNormal.x;
	vNormal.y += simulationPower * simNormal.y;
	vNormal.z += simulationPower * simNormal.z;
	vNormal = normalize( vNormal );
	return vNormal;
}

//////////////////////////////////////////////////////////////////////////////////////////////
#if BW_DEFERRED_SHADING 

//configurable foam params
float waterContrast = 0.5;	//power of contrast fn
float foamIntersectionFactor = 0.25;
float softIntersectionFactor = 50.0f;
float foamMultiplier = 0.75; // яркость прибоя
float foamFreq = 0.3f; // частота прибоя
float foamAmplitude = 0.3f; // амплитуда прибоя в метрах
float foamWidth = 10.0f; // ширина прибоя
bool bypassDepth = true;		//for SM 3.0 water
float causticsPower = 8.0f;
bool		useSimulation			= true;
bool		combineSimulation		= false;
bool		useCaustics				= true;

texture		foamMap;
texture		simulationMap;
texture		rainSimulationMap;
texture		bbCopy;

sampler simulationSampler			= BW_SAMPLER(simulationMap, CLAMP)
sampler rainSimulationSampler		= BW_SAMPLER(rainSimulationMap, WRAP)
sampler bbCopySampler				= BW_SAMPLER(bbCopy, CLAMP)

sampler2D foamSampler = sampler_state
{
  Texture = (foamMap);
  MinFilter = LINEAR;
  MagFilter = LINEAR;
  MipFilter = LINEAR;
  AddressU = Wrap;
  AddressV = Wrap;
};

float3 calcFinalReflection(half4 dependentTexCoords, half3 normal)
{
	float3 reflectionColour = tex2D( reflectionSampler, dependentTexCoords.xy );
	reflectionColour *= reflectionTint;

#if WATER_REFLECTION_FADE_ENABLED
	// At water reflection scene cull distance, the reflection is no longer  
	// updated. Fade to refraction tint colour (colour of water). 
	reflectionColour = lerp(reflectionColour, refractionTint, simpleReflection); 
#endif	//WATER_REFLECTION_FADE_ENABLED

	return reflectionColour;
}


float Contrast(float Input, float ContrastPower)
{
    float Output = pow(saturate(Input / 5.0f), ContrastPower); 
    return Output;
}

#define EPSILONZ 0.0001f
#define PI 3.14f

float2 calculateSimTex( float2 inputCoord )
{
	const float val = 1 - (2*SIM_BORDER_SIZE*c_pixelSize);
	float2 simTex = inputCoord;
	simTex = ((simTex - 0.5) * val) + 0.5;
	return simTex;
}

float CalculateCaustics(half3 simNormal, half3 pos, half waterHeight)
{
	// вычисляем точку на поверхности воды вдоль направления света
	half a = (waterHeight - pos.y) / (-g_sunLight.m_dir.y); 
	half3 waterPos = pos - g_sunLight.m_dir * a; 
	// текстурные к-ты карты нормалей
	half2 tc = (waterPos.xz + half2(cellSizeHalfX, cellSizeHalfY)) / textureTesselation; 
	// смещение текстурных к-т для движущейся воды
	tc = half2(	dot( float4(tc, 0, 1), bumpTexCoordTransformX	), 
				dot( float4(tc, 0, 1), bumpTexCoordTransformY	));
	// нормаль каустики
	half3 caustic_normal = generateSurfaceNormal(tc, simNormal * 0.1f); 

	float fScale = ( 1.0 - pow(caustic_normal.z, causticsPower) );
	half result = 1.0f - 1.6 * g_sunLight.m_dir.y * fScale * min((waterHeight - pos.y), 1.0);
	return result;
}

half3 getFoam(half amplPos, half2 tc, half2 bankDir, half glow)
{
	//half2 bd = half2(bankDir.y, -bankDir.x);
	half3 cFoam  =	tex2D(foamSampler,  (tc + bankDir * amplPos*foamAmplitude)).xyz * 2.0f;/* * (-amplPos + 1.0f)*/
	half fFoamLuminance = saturate( dot( cFoam, 0.333f) - 1.0f);
	half foam = (1.0f - saturate(foamIntersectionFactor * (0.2f / fFoamLuminance)));
	foam *= smoothstep(0.2f, 0.7f, foam );
	half3 cFinalFoam = foam * fFoamLuminance * foamMultiplier;
	return cFinalFoam * glow;
}

// The high quality water shader. (Shader Model 3)
float4 ps_main_3_0( PS_INPUT_RT i, in float2 vPos : VPOS,
					uniform bool bUseSim,
					uniform bool bUseCausticsAndChromaticAberration,
					uniform bool bEnableShadows) : COLOR0
{
	//-- recalculate reflect and refract texture coordinates in respect to the nVidia 3D Vision.
	//-- Note: We have to do the same recalculation with the SM2 shader, but because of the VPOS
	//--	   shader's semantic was designed only for SM3 and above, we can't do this.
	//----------------------------------------------------------------------------------------------
	float  projPosW = 0.5f * i.W_sim.z;
	float2 screenUV = SC2TC(vPos);

	//-- Map projected position to the reflection and refraction texture
	half2 reflect_refractPos = half2(2.0f * screenUV.x, -2.0f * screenUV.y + 2.0f) * projPosW;

	//-- Reflection transform
	i.reflect_refract = half4(reflect_refractPos.x, -reflect_refractPos.y, -reflect_refractPos.y, reflect_refractPos.x);
	//----------------------------------------------------------------------------------------------

	half3 simNormal = half3(0,0,1); // normal to the simulation wave
	float height = 0.f;

	if (bUseSim)
	{
		if (simulationTiling == 1.0)
		{
			half4 simSample = tex2D(simulationSampler, calculateSimTex(i.W_sim.xy));
			simNormal = simSample.xzy;
			height = simSample.a;
		}
		else if (combineSimulation) // sim and rain
		{
			half4 simSample = tex2D(simulationSampler, calculateSimTex(i.W_sim.xy));
			half3 rainSample = tex2D(rainSimulationSampler, calculateSimTex(i.W_sim.xy * simulationTiling));
			simSample.xyz = (simSample.xyz + rainSample.xyz) * 0.5;
			simNormal = simSample.xzy;
			height = simSample.a;
		}
		else // just rain
		{
			half4 simSample = tex2D(rainSimulationSampler, calculateSimTex(i.W_sim.xy * simulationTiling));
			simNormal = simSample.xzy;
		}
	}

	half3 vNormal = generateSurfaceNormal( i.tc.xy, simNormal);
	vNormal *= pow(generateSurfaceNormal( i.tc.zw * 0.514f, simNormal), 0.6f);
	vNormal = normalize(vNormal);

	/////////////////////////////////////////////////////////////
	/* Compute coordinates for sampling Reflection/Refraction*/
	half2 screenCoords;
	half4 dependentTexCoords = computeDependentCoords(i.reflect_refract, vNormal, i.W_sim.z, i.W_sim.w, screenCoords);
	float contrast_ = 1.0f;/* water transparency factor */
	float depth = 0.0f;/* distance between underwater surface and water */
	float softIntersect = 1.0f;
	float3 underWaterPos = g_buffer_readWorldPos(screenUV);
	if ( !bypassDepth )
	{
		depth = distance( underWaterPos , i.worldPos ) * 0.07f;
		contrast_ = Contrast(depth, waterContrast);
		if( (depth * contrast_) <= EPSILONZ )
		{
			discard;
			return float4(0,0,0,0);
		}
		softIntersect = saturate( softIntersectionFactor * depth);
	}
	/////////////////////////////////////////////////////////////
	float3 eye = normalize(g_cameraPos.xyz - i.worldPos.xyz);
	float3 reflectionColour = calcFinalReflection(dependentTexCoords, vNormal.xzy);

	//-- foam --///////////////////////////////////
	float bankDist = i.bankDirDist.z - 2.0f;
	float2 bankDir = i.bankDirDist.xy;
	float distKoef = 1.0f - saturate((bankDist) / foamWidth);
	float3 finalFoamColor = 0;
	float bankGlow = 1.0f;
	if(bankDist < foamWidth*2)
	{
		float amplPos1 = sin(foamFreq * (g_time + (i.worldPos.x + i.worldPos.z)*0.1f )); // first foam wave
		float glow1 = pow(sin(foamFreq * g_time * 0.5f), 4); // first glow wave
		glow1 = saturate(cos(PI * (bankDist - foamWidth*(1.0f + 0.25f*amplPos1))/foamWidth))/**saturate( glow1 + 0.2f)*/;
		float amplPos2 = sin(foamFreq * g_time + 3.14f); // second foam wave
		float glow2 = pow(sin((foamFreq * g_time + 3.14f) * 0.5f), 4); // second glow wave
		glow2 = saturate(cos(PI * (bankDist - foamWidth*(1.0f + 0.25f*amplPos2))/foamWidth))*saturate( glow2 + 0.2f);

		bankGlow = max(glow1, glow2);

		half3 cFoamFinal1 = getFoam(amplPos1, i.foam0.xy + vNormal.xy * 0.075f + half2(0.25f, 0.17f), bankDir, glow1);
		half3 cFoamFinal2 = getFoam(amplPos2, i.foam0.xy + vNormal.xy * 0.075f, bankDir, glow2);

		finalFoamColor = (cFoamFinal1 + cFoamFinal2) * 0.6666f;
	}
	//////////////////////////////////////////////
	//--sim foaming:
	float4 foam = foamColour * (vNormal.y*vNormal.y);
	float foamAmount = clamp(abs(height), 0.0f, 0.4f) * 0.5f;

	//--deepening effect
	float deepening = saturate((fadeDepth - depth) / (fadeDepth + EPSILONZ));	
	half3 waterColour = lerp(deepColour.rgb * (1.0f - deepening), foam, foamAmount);

	//-- get back buffer copy sampler and distort it depending on depth ( to prevent big distorsion near the bank )
	float refractionCoefficient = softIntersect * contrast_;
	float3 finalRefraction = tex2D( bbCopySampler, lerp( screenCoords, dependentTexCoords, 0.9f * refractionCoefficient ) );

	//-- caustics and chromatic aberration
	if(bUseCausticsAndChromaticAberration)
	{
		half3 specular = 0;
		specular.r = CalculateCaustics(simNormal, underWaterPos, i.worldPos.y) * saturate(1.1f - contrast_);
		specular.g = CalculateCaustics(simNormal, underWaterPos + half3(0.11f, 0.1f, 0.0f), i.worldPos.y) * saturate(1.1f - contrast_);
		specular.b = CalculateCaustics(simNormal, underWaterPos + half3(0.2f, 0.15f, 0.0f), i.worldPos.y) * saturate(1.1f - contrast_);
		finalRefraction *= specular;
	}

	//--Combine refraction / deepening color
	finalRefraction = lerp(finalRefraction, waterColour, (1.0f - deepening));
		
	//--distKoef for soft coast line
	distKoef = saturate(1.0f - distKoef);
	//--Fresnel effect coef. to set realistic reflection amount
	half fresnel_ = fresnel( eye, vNormal.xzy, fresnelExp, fresnelConstant ); 
	float softReflectionKoef = saturate(depth*10.0f);
	finalRefraction *= lerp(half3(1,1,1), refractionTint, softReflectionKoef);

	// Shadow
	// float2 correctedUV = vPos * g_invScreen.zw;
	float linearZ = g_buffer_readLinearZ( screenUV ) * g_farPlane.x;
	half  shadow  = calcShadow( screenUV, 1.f, linearZ, bEnableShadows );

	float3 finalColour = lerp( finalRefraction, reflectionColour, softReflectionKoef * fresnel_ );
	//--foam 
	finalColour += finalFoamColor * distKoef;
	//--Specular light
	finalColour += shadow * getSunLight( eye, vNormal.xzy ) * softReflectionKoef;
	//--fog
	finalColour.xyz = lerp(finalColour.xyz, g_fogParams.m_color.rgb * g_HDRParams.w, (1.0f - i.fog) * g_fogParams.m_enabled * softReflectionKoef);
	
	// finalColour.xyz = applyFogTo( finalColour.xyz, i.fog );
	return float4(finalColour, 1.0f );
};


PixelShader rt_pshaders[] = 
{
	// (bUseSim, bUseCaustics, bEnableShadows)
	compile ps_3_0 ps_main_3_0( true, true, false),
	compile ps_3_0 ps_main_3_0( false, true, false),
	compile ps_3_0 ps_main_3_0( false, false, false),

	compile ps_3_0 ps_main_3_0( true, true, true),
	compile ps_3_0 ps_main_3_0( false, true, true),
	compile ps_3_0 ps_main_3_0( false, false, true)
};


int psIndex()
{
	int index = 0;
	if (!useCaustics)
		index = 2;
	else if (!useSimulation)
		index = 1;

	if (enableWaterShadows)
		index += 3;

	return index;
}

// Standard water render technique:
WATER_TECHNIQUE(water_rt, (compile vs_3_0 vs_main(true, true)), (rt_pshaders[psIndex()]), FALSE)

//// A special case to draw the water in the project view thumbnails.
float4 ps_main_proj_view( PS_INPUT_RT i ) : COLOR0
{
	half3 vNormal = generateSurfaceNormal( i.tc, half3(0,0,1) );
	half edging = i.alpha.w;
	
	half2 screenCoords;
	// Compute coordinates for sampling Reflection/Refraction
	half4 dependentTexCoords = computeDependentCoords(i.reflect_refract, vNormal, i.W_sim.z, i.W_sim.w, screenCoords);
			
	half3 eye = half3(0,1,0);
	half2 screenTexCoord = dependentTexCoords.xy;

	// Sample reflection and use alpha for transparency
	half4 reflectionColour = tex2D( reflectionSampler, screenTexCoord ) * reflectionTint;	
	half fresnelCoeff = fresnel( eye, vNormal.xzy, fresnelExp, fresnelConstant );
	half4 finalColour = reflectionColour * fresnelCoeff + refractionTint * (1.0f - fresnelCoeff);
	
	return float4( finalColour.xyz, fresnelCoeff*edging );
};

// Project view technique:
WATER_TECHNIQUE(water_proj, (compile vs_3_0 vs_main(false, false)), (compile ps_3_0 ps_main_proj_view()), FALSE)

#else //#if BW_DEFERRED_SHADING

// ----------------------------------------------------------------------------
// Section: General Functions
// ----------------------------------------------------------------------------
struct PS_FF_INPUT_RT
{
	float4 pos:				POSITION;
	float4 tc:				TEXCOORD0;
	float4 alpha:			COLOR0;
	float fog:				FOG;	
};


PS_FF_INPUT_RT vs_ff( VS_INPUT i )
{
	PS_FF_INPUT_RT o = (PS_FF_INPUT_RT)0;
	o.alpha = i.diffuse;
	
	float4 projPos = mul( i.pos, mul(world, g_viewProjMat) );
	o.pos = projPos;
	o.fog = 0;

	// Reflection transform.  Perspective divide done by FF hardware state,
	// so we need to multiply the following u,v coordinates by w
	o.tc.x = 0.5 * projPos.x + 0.5 * projPos.w;
	o.tc.y = 0.5 * -projPos.y + 0.5 * projPos.w;
	o.tc.z = projPos.w;
	o.tc.w = projPos.w;

	return o;
};


// ----------------------------------------------------------------------------
// Section: Pixel Shaders
// ----------------------------------------------------------------------------

half3 calcCubeReflections( half3 eye, half3 normal )
{
	float3 cubeNormal = float3(0,1-scale.x,0) + normal*scale.x;
	float3 reflVec = reflect(eye, cubeNormal);
	reflVec = float3(reflVec.z, -reflVec.y, -reflVec.x);
	return texCUBE(reflectionCubeSampler, reflVec).rgb;
}

half4 calcFinalColour(half3 normal, half3 worldPos, half2 tc, float refrCoef)
{
	half3 eye = normalize(g_cameraPos.xyz - worldPos);

	//half3 refraction = tex2D( bbCopySampler, tc );
	//refraction *= lerp(half3(1,1,1), refractionTint, refrCoef);

	half3 reflection = calcCubeReflections(eye, normal);
	reflection *= reflectionTint;

	half fresnelCoeff = fresnel( eye, normal, fresnelExp, fresnelConstant*saturate(refrCoef*2.0f) ); 
	half4 finalColour = half4(reflection, fresnelCoeff);

	finalColour.xyz += getSunLight( eye, normal );

	return finalColour;
}

#define WATER_NORMAL(tc, simNormal) \
	half3 vNormal = generateSurfaceNormal( tc, simNormal );\
	half edging = i.alpha.w;

// A special case to draw the water in the project view thumbnails.
float4 ps_main_proj_view( PS_INPUT_RT i ) : COLOR0
{
	WATER_NORMAL(i.tc, half3(0,0,1))
	
	half2 screenCoords;
	// Compute coordinates for sampling Reflection/Refraction
	half4 dependentTexCoords = computeDependentCoords(i.reflect_refract, vNormal, i.W_sim.z, i.W_sim.w, screenCoords);
			
	half3 eye = half3(0,1,0);
	half2 screenTexCoord = dependentTexCoords.xy;

	// Sample reflection and use alpha for transparency
	half4 reflectionColour = tex2D( reflectionSampler, screenTexCoord ) * reflectionTint;	
	half fresnelCoeff = fresnel( eye, vNormal.xzy, fresnelExp, fresnelConstant );
	half4 finalColour = reflectionColour * fresnelCoeff + refractionTint * (1.0f - fresnelCoeff);
	
	return float4( finalColour.xyz, fresnelCoeff*edging );
};

// The medium quality water shader. (Shader Model 2)
float4 ps_main_2_0( PS_INPUT_RT i) : COLOR0
{
	half3 simNormal = half3(0,0,0);
	float height = 0.f;

	WATER_NORMAL(i.tc.xy, simNormal)

	/* Compute coordinates for sampling Reflection/Refraction*/
	half2 screenCoords;
	half4 dependentTexCoords = computeDependentCoords(i.reflect_refract, vNormal, i.W_sim.z, i.W_sim.w, screenCoords);
	float refrCoef = saturate((i.bankDirDist.z-10.f) / 40.0f);
	half4 finalColour = calcFinalColour( vNormal.xzy, i.worldPos.xyz, lerp( screenCoords, dependentTexCoords.xy, 0.05f ), refrCoef);
	return float4( finalColour );
}

//--------------------------------------------------------------
// Technique Section
//--------------------------------------------------------------

// Standard water render technique:
WATER_TECHNIQUE(water_rt, (compile vs_2_0 vs_main(false, false)), (compile ps_2_0 ps_main_2_0()), TRUE)

// Project view technique:
WATER_TECHNIQUE(water_proj, (compile vs_2_0 vs_main(false, false)), (compile ps_2_0 ps_main_proj_view()), FALSE)

technique water_SM1
{
	pass Pass_0
	{
		SPECULARENABLE = FALSE;
		TEXTUREFACTOR = (float4(0.5, 0.8, 1.0, 0.4));
		BW_FOG
		COLOROP[0] = ( 4 );
		COLORARG1[0] = TEXTURE;
		COLORARG2[0] = TFACTOR;
		ALPHAOP[0] = SELECTARG2;
		ALPHAARG1[0] = TEXTURE;
		ALPHAARG2[0] = TFACTOR;
		Texture[0] = (reflectionMap);
		ADDRESSU[0] = WRAP;
		ADDRESSV[0] = WRAP;
		ADDRESSW[0] = WRAP;
		MAGFILTER[0] = LINEAR;
		MINFILTER[0] = LINEAR;
		MIPFILTER[0] = LINEAR;
		MAXMIPLEVEL[0] = 0;
		MIPMAPLODBIAS[0] = 0;
		TexCoordIndex[0] = 0;
		TEXTURETRANSFORMFLAGS[0] = 0;

		BW_TEXTURESTAGE_TERMINATE(1)
		CULLMODE = NONE;

		ALPHATESTENABLE = FALSE;
		ALPHABLENDENABLE = TRUE;
		SRCBLEND = <srcBlend>;
		DESTBLEND = <destBlend>;
		ZENABLE = TRUE;
		ZWRITEENABLE = FALSE;
		ZFUNC = LESSEQUAL;		

		VertexShader = compile vs_1_1 vs_ff();
		PixelShader = NULL;
	}
}

technique water_SM0
{
	pass Pass_0
	{
		SPECULARENABLE = FALSE;
		TEXTUREFACTOR = (float4(0.5, 0.8, 1.0, 0.4));
		BW_FOG
		COLOROP[0] = ( 4 );
		COLORARG1[0] = TEXTURE;
		COLORARG2[0] = TFACTOR;
		ALPHAOP[0] = SELECTARG2;
		ALPHAARG1[0] = TEXTURE;
		ALPHAARG2[0] = TFACTOR;
		Texture[0] = (reflectionMap);
		ADDRESSU[0] = WRAP;
		ADDRESSV[0] = WRAP;
		ADDRESSW[0] = WRAP;
		MAGFILTER[0] = LINEAR;
		MINFILTER[0] = LINEAR;
		MIPFILTER[0] = LINEAR;
		MAXMIPLEVEL[0] = 0;
		MIPMAPLODBIAS[0] = 0;
		TexCoordIndex[0] = 0;
		TEXTURETRANSFORMFLAGS[0] = 0;

		BW_TEXTURESTAGE_TERMINATE(1)
		CULLMODE = NONE;

		ALPHATESTENABLE = FALSE;
		ALPHABLENDENABLE = TRUE;
		SRCBLEND = <srcBlend>;
		DESTBLEND = <destBlend>;
		ZENABLE = TRUE;
		ZWRITEENABLE = FALSE;
		ZFUNC = LESSEQUAL;		

		VertexShader = compile vs_1_1 vs_ff();
		PixelShader = NULL;
	}
}

#endif//BW_DEFERRED_SHADING
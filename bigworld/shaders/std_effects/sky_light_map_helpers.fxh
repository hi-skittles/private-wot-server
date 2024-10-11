/**
 *	This include file contains all you need to implement sky light mapping.
 */
 
 // don't allow cloud shadows on additive effects
#if SKY_LIGHT_MAP_ENABLE
	#ifdef ADDITIVE_EFFECT
		#undef SKY_LIGHT_MAP_ENABLE
		#define REENABLE_SKY_LIGHT_MAP 1
	#endif
#endif

// helper function
float2 generateSkyMapCoords(in float3 inputWPos, in float3 cameraWPos, 
							in float4 transform0, in float4 transform1 )
{
	float4 skyLightMap;
	skyLightMap.xyz = inputWPos - cameraWPos;
	skyLightMap.w = 1.0;

	float2 output;
	output.x = dot( skyLightMap, transform0 );
	output.y = dot( skyLightMap, transform1 );
	
	return output;
}

#if SKY_LIGHT_MAP_ENABLE

#define BW_SKY_LIGHT_MAP\
float4 skyLightMapTransform[2] : SkyLightMapTransform;\
texture skyLightMap : SkyLightMap;\

#define BW_SKY_MAP_COORDS(output,inputWPos)\
output = generateSkyMapCoords( inputWPos, wsCameraPos, skyLightMapTransform[0], skyLightMapTransform[1] );\

#define BW_SKY_LIGHT_MAP_SAMPLER\
sampler skyLightMapSampler = sampler_state\
{\
	Texture = (skyLightMap);\
	ADDRESSU = CLAMP;\
	ADDRESSV = WRAP;\
	ADDRESSW = CLAMP;\
	MAGFILTER = LINEAR;\
	MINFILTER = LINEAR;\
	MIPFILTER = LINEAR;\
	MAXMIPLEVEL = 0;\
	MIPMAPLODBIAS = 0;\
};\


#define BW_SAMPLE_SKY_MAP( input )\
1.0 - tex2D( skyLightMapSampler, input ).w;\


#define BW_TEXTURESTAGE_CLOUDMAP(stage)\
COLOROP[stage] = MODULATE;\
COLORARG1[stage] = TEXTURE|ALPHAREPLICATE|COMPLEMENT;\
COLORARG2[stage] = CURRENT;\
ALPHAOP[stage] = SELECTARG1;\
ALPHAARG1[stage] = CURRENT;\
ALPHAARG2[stage] = CURRENT;\
Texture[stage] = (skyLightMap);\
ADDRESSU[stage] = WRAP;\
ADDRESSV[stage] = CLAMP;\
ADDRESSW[stage] = WRAP;\
MAGFILTER[stage] = LINEAR;\
MINFILTER[stage] = LINEAR;\
MIPFILTER[stage] = LINEAR;\
MAXMIPLEVEL[stage] = 0;\
MIPMAPLODBIAS[stage] = 0;\
TexCoordIndex[stage] = stage;


#define BW_TEXTURESTAGE_CLOUDMAP_MULALPHA(stage)\
COLOROP[stage] = MODULATE;\
COLORARG1[stage] = TEXTURE|ALPHAREPLICATE|COMPLEMENT;\
COLORARG2[stage] = CURRENT;\
ALPHAOP[stage] = MODULATE;\
ALPHAARG1[stage] = CURRENT;\
ALPHAARG2[stage] = DIFFUSE;\
Texture[stage] = (skyLightMap);\
ADDRESSU[stage] = WRAP;\
ADDRESSV[stage] = CLAMP;\
ADDRESSW[stage] = WRAP;\
MAGFILTER[stage] = LINEAR;\
MINFILTER[stage] = LINEAR;\
MIPFILTER[stage] = LINEAR;\
MAXMIPLEVEL[stage] = 0;\
MIPMAPLODBIAS[stage] = 0;\
TexCoordIndex[stage] = stage;


#define CLOUDMAP_STAGE 1
#define CLOUDMAP_STAGE_PLUS1 2
#define CLOUDMAP_STAGE_PLUS2 3
#define CLOUDMAP_STAGE_PLUS3 4

#else	// i.e. if not def SKY_LIGHTMAP_ENABLE

#define BW_SKY_LIGHT_MAP
#define BW_SKY_MAP_COORDS(output,inputWPos)
#define BW_SKY_LIGHT_MAP_SAMPLER
#define BW_SAMPLE_SKY_MAP( input ) 1.0;
#define BW_TEXTURESTAGE_CLOUDMAP(stage)
#define BW_TEXTURESTAGE_CLOUDMAP_MULALPHA(stage)
#define CLOUDMAP_STAGE 0
#define CLOUDMAP_STAGE_PLUS1 1
#define CLOUDMAP_STAGE_PLUS2 2
#define CLOUDMAP_STAGE_PLUS3 3

#endif	// ifdef SKY_LIGHT_MAP_ENABLE

#ifdef REENABLE_SKY_LIGHT_MAP
#define SKY_LIGHT_MAP_ENABLE 1
#undef REENABLE_SKY_LIGHT_MAP
#endif
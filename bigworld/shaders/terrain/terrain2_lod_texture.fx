#include "terrain_common.fxh"

//--------------------------------------------------------------------------------------------------
USE_TERRAIN_AO_MAP
USE_TERRAIN_NORMAL_MAP
USE_TERRAIN_HORIZON_MAP
USE_TERRAIN_BLEND_TEXTURE

//--------------------------------------------------------------------------------------------------
bool	useMultipassBlending	= false;
bool	hasHoles				= false;
bool	hasAO					= false;
float	lodTextureStart 		= 200;	// this is where we start blending in lod texture
float	lodTextureDistance		= 100; 	// this is where lod texture is 100%

//--------------------------------------------------------------------------------------------------
#if BW_DEFERRED_SHADING

#include "write_g_buffer.fxh"

//--------------------------------------------------------------------------------------------------
struct ColorVS2PS
{
	float4 pos					: POSITION;	
	float4 normalBlendUV		: TEXCOORD0; //-- normal and blend UV coordinates.
    float4 shadowUVLinearZAlpha	: TEXCOORD1; //-- shadow UV, linearZ, blendFactor
	float2 aoUV					: TEXCOORD2; //-- ao UV
};

//--------------------------------------------------------------------------------------------------
ColorVS2PS vs_deferred_3_0(in TerrainVertex v)
{
	ColorVS2PS o = (ColorVS2PS)0;
	
	// Calculate the position of the vertex
	float3 wPos = terrainVertexPosition(v);
	o.pos		= mul(float4(wPos, 1.0f), g_viewProjMat);

	//-- write linear z.
	o.shadowUVLinearZAlpha.z = o.pos.w;
	
	//-- calculate the texture coordinate for the normal map.
	o.normalBlendUV.xy = inclusiveTextureCoordinate(v.xz, float2(normalMapSize, normalMapSize));

	//-- calculate the texture coordinate for the horizon map.
	o.shadowUVLinearZAlpha.xy = inclusiveTextureCoordinate(v.xz, float2(horizonMapSize, horizonMapSize));
	
	//-- calculate the texture coordinate for the blend map.
	o.normalBlendUV.zw = v.xz; 
	o.normalBlendUV.w  = 1.0f - o.normalBlendUV.w;

	//--
	o.aoUV = inclusiveTextureCoordinate(v.xz, float2(aoMapSize, aoMapSize));
	
	//-- calculate blend alpha in over a distance.
	//-- ToDo (b_sviglo): optimize use squared length instead and avoid using division.
	float len = length(wPos.xz - g_lodCameraPos.xz) * g_lodCameraPos.w;
	len 	  = clamp(len, lodTextureStart, lodTextureStart + lodTextureDistance);

	o.shadowUVLinearZAlpha.w = abs(len - lodTextureStart) / lodTextureDistance;

	return o;
}

//--------------------------------------------------------------------------------------------------
G_BUFFER_LAYOUT ps_deferred_3_0(const ColorVS2PS i, uniform bool compile_time_enableBlending)
{
	G_BUFFER_LAYOUT o = (G_BUFFER_LAYOUT)0;

	//-- get the diffuse colour.
	half4 diffuseColor = gamma2linear(tex2D(blendMapSampler, i.normalBlendUV.zw));
	
	//-- get the normal from the terrain normal map.
	half3 normal = terrainNormal(normalMapSampler, i.normalBlendUV.xy);
	
	//-- calculate the horizon shadows.
    half shadowCoverage = 1 - tex2D(horizonMapSampler, i.shadowUVLinearZAlpha.xy).y;

	//
	half ao = 0.5f;
	if (hasAO)
	{
		ao = terrainAO(aoMapSampler, i.aoUV).x;
	}

	//-- fill GBuffer.
	g_buffer_writeDepth(o, i.shadowUVLinearZAlpha.z);
	g_buffer_writeObjectKind(o, G_OBJECT_KIND_TERRAIN);
	g_buffer_writeNormal(o, normal);
	g_buffer_writeAlbedo(o, diffuseColor.rgb);
	g_buffer_writeSpecAmount(o, diffuseColor.a);
	g_buffer_writeUserData1(o, shadowCoverage, false);
	g_buffer_writeUserData2(o, ao, false);

	//-- in case if we have to do blending.
	if (compile_time_enableBlending)
	{
		o.color0.a = i.shadowUVLinearZAlpha.w;
		o.color1.a = i.shadowUVLinearZAlpha.w;
		o.color2.a = i.shadowUVLinearZAlpha.w;
	}

	return o;
};

//--------------------------------------------------------------------------------------------------
struct ReflectionVS2PS
{
	float4 pos				: POSITION;	
	float4 normalBlendUV	: TEXCOORD0; //-- normal and blend UV coordinates.
    float4 shadowUVAlphaFog	: TEXCOORD1; //-- shadow UV, blendFactor, fog
};

//--------------------------------------------------------------------------------------------------
ReflectionVS2PS vs_reflection_3_0(const TerrainVertex i)
{
	ReflectionVS2PS o = (ReflectionVS2PS)0;

	//-- calculate the position of the vertex.
	float4 wPos = terrainVertexPosition(i);
	o.pos		= mul(wPos, g_viewProjMat);
	
	//-- calculate the texture coordinate for the normal map.
	o.normalBlendUV.xy = inclusiveTextureCoordinate(i.xz, float2(normalMapSize, normalMapSize));

	//-- calculate the texture coordinate for the backed shadows.
	o.shadowUVAlphaFog.xy = inclusiveTextureCoordinate(i.xz, float2(horizonMapSize, horizonMapSize));
	
	//-- calculate the texture coordinate for the blend map.
	o.normalBlendUV.zw = i.xz; 
	o.normalBlendUV.w  = 1.0f - o.normalBlendUV.w;
	
	//-- calculate blend alpha in over a distance.
	//-- ToDo (b_sviglo): optimize use squared length instead and avoid using division.
	float len   = length(wPos.xz - g_lodCameraPos.xz) * g_lodCameraPos.w;
	len 	    = clamp(len, lodTextureStart, lodTextureStart + lodTextureDistance);
	float alpha  = abs(len - lodTextureStart) / lodTextureDistance;

	o.shadowUVAlphaFog.z = alpha;
	o.shadowUVAlphaFog.w = bw_vertexFog(wPos, o.pos.w);
	
	return o;
}

//--------------------------------------------------------------------------------------------------
float4 ps_reflection_3_0(const ReflectionVS2PS i) : COLOR0
{
	//-- get the diffuse color.
	half4 diffuseColor = gamma2linear(tex2D(blendMapSampler, i.normalBlendUV.zw));
	
	//-- get the normal from the terrain normal map.
	half3 normal = terrainNormal(normalMapSampler, i.normalBlendUV.xy);
	
	//-- calculate the horizon shadows.
    half shadow = tex2D(horizonMapSampler, i.shadowUVAlphaFog.xy).x;

	//-- calculate sun influence.
	half4 o;
	o.rgb = diffuseColor.rgb * (sunAmbientTerm() + sunDiffuseTerm(normal));
	o.a   = i.shadowUVAlphaFog.z;

	//-- fog.
	o.rgb = applyFogTo(o.rgb, i.shadowUVAlphaFog.w);

	return o;
}


//--------------------------------------------------------------------------------------------------
PixelShader colorPS[2] = {
	compile ps_3_0 ps_deferred_3_0(1),
	compile ps_3_0 ps_deferred_3_0(0)
};

//--------------------------------------------------------------------------------------------------
technique MAIN
{
	pass Pass_0
	{
		ALPHATESTENABLE		= FALSE;
		ALPHABLENDENABLE	= (useMultipassBlending ? 1 : 0);
        SRCBLEND			= SRCALPHA;
        DESTBLEND			= INVSRCALPHA;
        ZWRITEENABLE		= (hasHoles ? 0 : 1);
        ZFUNC				= (hasHoles ? BW_CMP_EQUAL : BW_CMP_LESSEQUAL);
        ZENABLE				= TRUE;
		CULLMODE			= BW_CULL_CCW;

		//-- render target mask.
		//-- Note: these mask should be in sync with the g-buffer layout.
		COLORWRITEENABLE  = (useMultipassBlending ? 0x00 : 0xFF);
		COLORWRITEENABLE1 = (useMultipassBlending ? 0x07 : 0xFF);
		COLORWRITEENABLE2 = (useMultipassBlending ? 0x07 : 0xFF);
		
		VertexShader = compile vs_3_0 vs_deferred_3_0();
		PixelShader  = colorPS[useMultipassBlending ? 0 : 1];
	}
}

//--------------------------------------------------------------------------------------------------
technique REFLECTION
{
	pass Pass_0
	{
		ALPHATESTENABLE		= FALSE;
		ALPHABLENDENABLE	= (useMultipassBlending ? 1 : 0);
        SRCBLEND			= SRCALPHA;
        DESTBLEND			= INVSRCALPHA;
        ZWRITEENABLE		= (hasHoles ? 0 : 1);
        ZFUNC				= (hasHoles ? BW_CMP_EQUAL : BW_CMP_LESSEQUAL);
        ZENABLE				= TRUE;
		CULLMODE			= BW_CULL_CCW;

		VertexShader = compile vs_3_0 vs_reflection_3_0();
		PixelShader  = compile ps_3_0 ps_reflection_3_0();
	}
}

//--------------------------------------------------------------------------------------------------
#else

// The output from the vertex shader
//--------------------------------------------------------------------------------------------------
struct TerrainVS2PS
{
	float4 pos				: POSITION;
	float4 normalBlendUV	: TEXCOORD0; //-- normal and blend UV coordinates.
    float3 shadowUVAlpha	: TEXCOORD1; //-- shadow UV, blendFactor
	float  fog				: FOG;
};

//--------------------------------------------------------------------------------------------------
TerrainVS2PS vs_main_2_0(in TerrainVertex i)
{
	TerrainVS2PS o = (TerrainVS2PS)0;
	
	//-- calculate the position of the vertex.
	float4 wPos = terrainVertexPosition(i);
	o.pos = mul(wPos, g_viewProjMat);
	
	//-- calculate the texture coordinate for the normal map.
	o.normalBlendUV.xy = inclusiveTextureCoordinate(i.xz, float2(normalMapSize, normalMapSize));

	//-- calculate the texture coordinate for the backed shadows.
	o.shadowUVAlpha.xy = inclusiveTextureCoordinate(i.xz, float2(horizonMapSize, horizonMapSize));
	
	//-- calculate the texture coordinate for the blend map.
	o.normalBlendUV.zw = i.xz; 
	o.normalBlendUV.w  = 1.0f - o.normalBlendUV.w;
	
	//-- blend alpha in over a distance.
	//-- ToDo (b_sviglo): optimize use squared length instead and avoid using division.
	float len = length(wPos.xz - g_lodCameraPos.xz) * g_lodCameraPos.w;
	len 	  = clamp(len, lodTextureStart, lodTextureStart + lodTextureDistance);
	float a	  = abs(len - lodTextureStart) / lodTextureDistance;
	o.shadowUVAlpha.z = a;

	//-- fog.
	o.fog = bw_vertexFog(wPos, o.pos.w);

	return o;
}

//--------------------------------------------------------------------------------------------------
float4 ps_main_2_0(const TerrainVS2PS i) : COLOR
{
	//-- get the diffuse color.
	half4 diffuseColor = tex2D(blendMapSampler, i.normalBlendUV.zw);
	
	//-- get the normal from the terrain normal map.
	half3 normal = terrainNormal(normalMapSampler, i.normalBlendUV.xy);
	
	//-- calculate the horizon shadows.
    half shadow = tex2D(horizonMapSampler, i.shadowUVAlpha.xy).x;

	//-- calculate sun influence.
	half4 o;
	o.rgb = diffuseColor.rgb * (sunAmbientTerm() + shadow * sunDiffuseTerm(normal));
	o.a   = i.shadowUVAlpha.z;

	return o;
};

//--------------------------------------------------------------------------------------------------
technique MAIN
{
	pass Pass_0
	{
		ALPHATESTENABLE		= FALSE;
		ALPHABLENDENABLE	= (useMultipassBlending ? 1 : 0);
        SRCBLEND			= SRCALPHA;
        DESTBLEND			= INVSRCALPHA;
        ZWRITEENABLE		= (hasHoles ? 0 : 1);
        ZFUNC				= (hasHoles ? BW_CMP_EQUAL : BW_CMP_LESSEQUAL);
        ZENABLE				= TRUE;
		CULLMODE			= BW_CULL_CCW;
		BW_FOG
        
        VertexShader = compile vs_2_0 vs_main_2_0();
		PixelShader  = compile ps_2_0 ps_main_2_0();
	}
}

//--------------------------------------------------------------------------------------------------
technique REFLECTION
{
	pass Pass_0
	{
		ALPHATESTENABLE		= FALSE;
		ALPHABLENDENABLE	= (useMultipassBlending ? 1 : 0);
        SRCBLEND			= SRCALPHA;
        DESTBLEND			= INVSRCALPHA;
        ZWRITEENABLE		= (hasHoles ? 0 : 1);
        ZFUNC				= (hasHoles ? BW_CMP_EQUAL : BW_CMP_LESSEQUAL);
        ZENABLE				= TRUE;
		CULLMODE			= BW_CULL_CCW;
		BW_FOG
        
        VertexShader = compile vs_2_0 vs_main_2_0();
		PixelShader  = compile ps_2_0 ps_main_2_0();
	}
}

#endif //-- BW_DEFERRED_SHADING

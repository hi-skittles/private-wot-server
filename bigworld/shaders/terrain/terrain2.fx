#include "terrain_common.fxh"

USE_TERRAIN_NORMAL_MAP
USE_TERRAIN_HORIZON_MAP
USE_TERRAIN_AO_MAP

// Textures
USE_TERRAIN_BLEND_TEXTURE
TERRAIN_TEXTURE( layer0 )
TERRAIN_TEXTURE( layer1 )
TERRAIN_TEXTURE( layer2 )
TERRAIN_TEXTURE( layer3 )

//--------------------------------------------------------------------------------------------------
bool	hasHoles				= false;
bool	hasAO					= false;
bool	useMultipassBlending	= false;
int		bumpShaderMask			= 0;
float4	bumpFading				= float4(1,1,0,0); // x - start fading, y - fading distance.
float4	layerMask				= float4(1,1,1,1); //-- the mask used to set which layers are in use.

// Need this for blending setup
BW_NON_EDITABLE_ALPHA_TEST
BW_FRESNEL

//-- returns blend mask of 4 textures layers.
//--------------------------------------------------------------------------------------------------
half4 getBlendMask(const float2 uv)
{
	return tex2D(blendMapSampler, uv) * layerMask;
}

//--------------------------------------------------------------------------------------------------
half getAO(const float2 uv)
{
	half ao =  0.5f;
	if (hasAO)
	{
		ao = terrainAO(aoMapSampler, uv);
	}
	
	return ao;
}

//--------------------------------------------------------------------------------------------------
#if BW_DEFERRED_SHADING

#include "write_g_buffer.fxh"

//--------------------------------------------------------------------------------------------------
struct ColorVS2PS
{
	float4 pos					: POSITION;
	float4 normalBlendUV		: TEXCOORD0;	//-- normal.uv = xy, blend.uv = zw
	float4 layer01UV			: TEXCOORD1;	//-- layer0.uv = xy, layer1.uv = zw
	float4 layer23UV			: TEXCOORD2;	//-- layer2.uv = xy, layer3.uv = zw
	float4 wPosLinearZ			: TEXCOORD3;	//-- worldPos and linearZ
	float3 backedShadowsAlpha	: TEXCOORD4;	//-- backed shadows uv, bump alpha
	float2 aoUV					: TEXCOORD5;	//-- ao UV
};

//--------------------------------------------------------------------------------------------------
half getBackedShadows(const ColorVS2PS i)
{
	return 1 - tex2D(horizonMapSampler, i.backedShadowsAlpha.xy).y;
}

//-- returns blended color of the terrain pixel.
//--------------------------------------------------------------------------------------------------
half4 getTerrainColor(const ColorVS2PS i, const half4 blendMask)
{
	half4 diffuseColor = half4(0,0,0,0);

	diffuseColor += tex2D(layer0Sampler, i.layer01UV.xy) * blendMask.x;
	diffuseColor += tex2D(layer1Sampler, i.layer01UV.zw) * blendMask.y;
	diffuseColor += tex2D(layer2Sampler, i.layer23UV.xy) * blendMask.z;
	diffuseColor += tex2D(layer3Sampler, i.layer23UV.zw) * blendMask.w;

	return diffuseColor;
}

//-- from ShaderX5 "2.6 Normal Mapping without Pre-Computed Tangents".
//--------------------------------------------------------------------------------------------------
half2x3 computeTangentFrameCommonPart(float3 p)
{
    //-- get edge vectors of the pixel triangle
    half3 dp1  = ddx(p);
    half3 dp2  = ddy(p);

    //-- solve the linear system
    half3x3 M = half3x3(dp1, dp2, cross(dp1, dp2));
    half2x3 inversetransposeM = half2x3(cross(M[1], M[2]), cross(M[2], M[0]));

    //-- 
    return inversetransposeM;
}

//-- from ShaderX5 "2.6 Normal Mapping without Pre-Computed Tangents".
//--------------------------------------------------------------------------------------------------
half3x3 computeTangentFrameFromCommonPart(half2x3 invTranspM, half3 N, half2 uv)
{
    //-- get edge vectors of the pixel triangle
    half2 duv1 = ddx(uv);
    half2 duv2 = ddy(uv);

    //-- solve the linear system
    half3 T = mul(half2(duv1.x, duv2.x), invTranspM);
    half3 B = mul(half2(duv1.y, duv2.y), invTranspM);

    //-- construct tangent frame 
    return half3x3(normalize(T), normalize(B), N);
}

//-- Note: This is much more expensive version but fully correct. We'll use it because it always
//--	   gives correct results and eliminate unnacessary code parts at compile time. So if we'll
//--	   use relatively small count of bump maps it's pretty fast.
//--	   
//--	   Some measurements:
//--	   |  61  |  101  |  124  |  140 | - pixel shader instruction count
//--	   |  0	  |    1  |    2  |    3 | - number of bump-maps.

//-- Terrain 2.0 supports feature of multi-pass blending. Means terrain 2.0 renderer can perform
//-- only 4 layer at a time, so if we have more than 4 layers we have to draw desired chunk of terrain
//-- multiple times. To support ability correct blending bump-maps for different layers in different
//-- batches (BigWorld names it "combinedLayer" means batch of 4 layers) we have to do some additional
//-- work which is incapsulated here.
//--------------------------------------------------------------------------------------------------
half4 getBumpedNormal(const ColorVS2PS i, const half4 blend, const int4 compile_time_bumpMask)
{
	//-- 1. find blend sum of the current combined layer.
	const half combinedLayerBlendSum = dot(blend, 1);

	//-- 2. based on compile time mask "bumpMask" find out the resulting bumped normal for current
	//--	combined layer.
	half  blendSumOfBumpedLayers	= dot(blend, compile_time_bumpMask.wzyx);
	half3 worldBumpNormal			= half3(0,0,0);

	//-- 3. retrieve original world space normal for this pixel.
	half3 orgNormal = terrainNormal(normalMapSampler, i.normalBlendUV.xy);

	//-- 4. compute common part of the tangent frame.
	half2x3 invTransM = computeTangentFrameCommonPart(i.wPosLinearZ.xyz);

	//-- 5. compute world space bumped normal.
	//--	Note: For eliminating unused code we use compile time branching.
	if (compile_time_bumpMask[3])
	{
		const half3 bumpNormal = (tex2D(layer0BumpSampler, i.layer01UV.xy).xyz * 2 - 1) * blend.x;
		
		const half3x3 TBN = computeTangentFrameFromCommonPart(invTransM, orgNormal, i.layer01UV.xy);
		worldBumpNormal += mul(bumpNormal, TBN);
	}
	if (compile_time_bumpMask[2])
	{
		const half3 bumpNormal = (tex2D(layer1BumpSampler, i.layer01UV.zw).xyz * 2 - 1) * blend.y;
		
		const half3x3 TBN = computeTangentFrameFromCommonPart(invTransM, orgNormal, i.layer01UV.zw);
		worldBumpNormal += mul(bumpNormal, TBN);
	}
	if (compile_time_bumpMask[1])
	{
		const half3 bumpNormal = (tex2D(layer2BumpSampler, i.layer23UV.xy).xyz * 2 - 1) * blend.z;
		
		const half3x3 TBN = computeTangentFrameFromCommonPart(invTransM, orgNormal, i.layer23UV.xy);
		worldBumpNormal += mul(bumpNormal, TBN);
	}
	if (compile_time_bumpMask[0])
	{
		const half3 bumpNormal = (tex2D(layer3BumpSampler, i.layer23UV.zw).xyz * 2 - 1) * blend.w;
		
		const half3x3 TBN = computeTangentFrameFromCommonPart(invTransM, orgNormal, i.layer23UV.zw);
		worldBumpNormal += mul(bumpNormal, TBN);
	}

	//-- 6. find blend factor for blending together bumped normal and original normal.
	const half blendFactor = (blendSumOfBumpedLayers / combinedLayerBlendSum) * i.backedShadowsAlpha.z;

	//-- 7. and finally blend it with the original normal.
	orgNormal = lerp(orgNormal, normalize(worldBumpNormal), blendFactor);

	//-- 8. return final normal in world space and normal blend factor to do correct blending with
	//--	the sequential combined layers if they are available.
	//--	Note: If we have only one combined layer. combinedLayerBlendSum shold be 1.0f
	return half4(orgNormal, combinedLayerBlendSum);
}

//--------------------------------------------------------------------------------------------------
half4 getOriginalNormal(const ColorVS2PS i, const half4 blend)
{
	//-- 1. find blend sum of the current combined layer.
	const half combinedLayerBlendSum = dot(blend, 1);

	//-- 2. get the normal from the terrain normal map.
	half3 orgNormal = terrainNormal(normalMapSampler, i.normalBlendUV.xy);

	return half4(orgNormal, combinedLayerBlendSum);
}

//--------------------------------------------------------------------------------------------------
ColorVS2PS vs_deferred_3_0(const TerrainVertex i, uniform bool compile_time_bumped)
{
	ColorVS2PS o = (ColorVS2PS) 0;

	//-- calculate the position of the vertex.
	o.wPosLinearZ.xyz = terrainVertexPosition(i);
	o.pos			  = mul(float4(o.wPosLinearZ.xyz, 1.0f), g_viewProjMat);
	o.wPosLinearZ.w   = o.pos.w;
	
	//-- calculate the texture coordinate for the normal map.
	o.normalBlendUV.xy = inclusiveTextureCoordinate(i.xz, float2(normalMapSize, normalMapSize));
	
	//-- calculate the texture coordinate for the blend map.
	o.normalBlendUV.zw = inclusiveTextureCoordinate(i.xz, float2(blendMapSize, blendMapSize));
	
	//-- calculate the texture coordinates for our texture layers
	const float3 wPos = o.wPosLinearZ.xyz;
	o.layer01UV.xy = float2(dot(layer0UProjection, wPos), dot(layer0VProjection, wPos));
	o.layer01UV.zw = float2(dot(layer1UProjection, wPos), dot(layer1VProjection, wPos));
	o.layer23UV.xy = float2(dot(layer2UProjection, wPos), dot(layer2VProjection, wPos));
	o.layer23UV.zw = float2(dot(layer3UProjection, wPos), dot(layer3VProjection, wPos));

	o.layer01UV = o.layer01UV * float4(+1,-1,+1,-1) + 0.5f;
	o.layer23UV = o.layer23UV * float4(+1,-1,+1,-1) + 0.5f;

	//-- calculate the texture coordinate for the backed shadows.
	o.backedShadowsAlpha.xy = inclusiveTextureCoordinate(i.xz, float2(horizonMapSize, horizonMapSize));

	//-- 
	o.aoUV = inclusiveTextureCoordinate(i.xz, float2(aoMapSize, aoMapSize));

	//-- calculate blend alpha in over a distance.
	//-- ToDo (b_sviglo): optimize use squared length instead and avoid using division.
	if (compile_time_bumped)
	{
		float len = length(o.wPosLinearZ.xz - g_lodCameraPos.xz) * g_lodCameraPos.w;
		len 	  = clamp(len, bumpFading.x, bumpFading.x + bumpFading.y);
		float a	  = abs(len - bumpFading.x) / bumpFading.y;

		o.backedShadowsAlpha.z = 1.0f - a;
	}

	return o;
}

//--------------------------------------------------------------------------------------------------
G_BUFFER_LAYOUT ps_deferred_3_0(ColorVS2PS i, uniform bool compile_time_bumped, uniform int4 compile_time_bumpMask)
{
	G_BUFFER_LAYOUT o = (G_BUFFER_LAYOUT)0;

	//-- calculate blend mask of 4 layers.
	half4 blendMask = getBlendMask(i.normalBlendUV.zw);

    //-- get the diffuse color.
	half4 diffColor = gamma2linear(getTerrainColor(i, blendMask));

	//-- get the normal.
	half4 normal = half4(0,0,0,0);
	if (compile_time_bumped)
	{
		normal = getBumpedNormal(i, blendMask, compile_time_bumpMask);
	}
	else
	{
		normal = getOriginalNormal(i, blendMask);
	}

	//-- fill GBuffer.
	g_buffer_writeNormal(o, normal);
	g_buffer_writeAlbedo(o, diffColor.xyz);
	g_buffer_writeSpecAmount(o, diffColor.w);

	//-- if we are in multipass blending state disable expensive g-buffer filling with some unused
	//-- paramters.
	if (!useMultipassBlending)
	{
		g_buffer_writeDepth(o, i.wPosLinearZ.w);
		g_buffer_writeObjectKind(o, G_OBJECT_KIND_TERRAIN);
		g_buffer_writeUserData1(o, getBackedShadows(i), false);
		g_buffer_writeUserData2(o, getAO(i.aoUV), false);
	}

	//-- special blending of normals in case if we are using multi-pass rendering.
	{
		//-- multiply normal by blend factor. If we doesn't use multi-pass blending the blend factor
		//-- is 1.0f.
		o.color1.rg *= normal.w;
	}

	return o;
}

//--------------------------------------------------------------------------------------------------
struct ReflectionVS2PS
{
	float4 pos					: POSITION;
	float4 normalBlendUV		: TEXCOORD0;	//-- normal.uv = xy, blend.uv = zw
	float4 layer01UV			: TEXCOORD1;	//-- layer0.uv = xy, layer1.uv = zw
	float4 layer23UV			: TEXCOORD2;	//-- layer2.uv = xy, layer3.uv = zw
	float3 backedShadowsUVFog	: TEXCOORD3;	//-- backed shadows uv, fog
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
	
	//-- calculate the texture coordinate for the blend map.
	o.normalBlendUV.zw = inclusiveTextureCoordinate(i.xz, float2(blendMapSize, blendMapSize));
	
	//-- calculate the texture coordinates for our texture layers
	o.layer01UV.xy = float2(dot(layer0UProjection, wPos), dot(layer0VProjection, wPos));
	o.layer01UV.zw = float2(dot(layer1UProjection, wPos), dot(layer1VProjection, wPos));
	o.layer23UV.xy = float2(dot(layer2UProjection, wPos), dot(layer2VProjection, wPos));
	o.layer23UV.zw = float2(dot(layer3UProjection, wPos), dot(layer3VProjection, wPos));

	o.layer01UV = o.layer01UV * float4(+1,-1,+1,-1) + 0.5f;
	o.layer23UV = o.layer23UV * float4(+1,-1,+1,-1) + 0.5f;

	//-- calculate the texture coordinate for the backed shadows.
	o.backedShadowsUVFog.xy = inclusiveTextureCoordinate(i.xz, float2(horizonMapSize, horizonMapSize));

	//-- fog
	o.backedShadowsUVFog.z = bw_vertexFog(wPos, o.pos.w);
	
	return o;
}

//--------------------------------------------------------------------------------------------------
float4 ps_reflection_3_0(const ReflectionVS2PS i) : COLOR0
{
	//-- calculate blend mask of 4 layers.
	half4 blendMask = getBlendMask(i.normalBlendUV.zw);

    //-- get the diffuse color.
	half4 diffuseColor = half4(0,0,0,0);
	diffuseColor += tex2D(layer0Sampler, i.layer01UV.xy) * blendMask.x;
	diffuseColor += tex2D(layer1Sampler, i.layer01UV.zw) * blendMask.y;
	diffuseColor += tex2D(layer2Sampler, i.layer23UV.xy) * blendMask.z;
	diffuseColor += tex2D(layer3Sampler, i.layer23UV.zw) * blendMask.w;

	diffuseColor = gamma2linear(diffuseColor);

	//-- retrieve normal.
	half3 normal = terrainNormal(normalMapSampler, i.normalBlendUV.xy);
	
	//-- calculate sun influence.
	half3 o = diffuseColor.rgb * (sunAmbientTerm() + sunDiffuseTerm(normal));

	//-- fog.
	// Purely distance based fogging, same as in terrain pass in lighting 
	// resolve, which does not use a blendSum either. blendSum < 1 on
	// close pixels can result in incorrectly strong fog on close terrain.

	//const half blendSum = dot(blendMask, 1);
	//o = applyFogTo(o, i.backedShadowsUVFog.z * blendSum);

	o = applyFogTo(o, i.backedShadowsUVFog.z);

	return float4(o, 1);
}

//--------------------------------------------------------------------------------------------------
VertexShader deferredVS[] = {
	compile vs_3_0 vs_deferred_3_0(0),
	compile vs_3_0 vs_deferred_3_0(1)
};

//-- generate full combinations set of bump-mapped pixel shaders.
//--------------------------------------------------------------------------------------------------
PixelShader deferredPS[16] = {
	compile ps_3_0 ps_deferred_3_0(0, int4(0,0,0,0)),
	compile ps_3_0 ps_deferred_3_0(1, int4(0,0,0,1)),
	compile ps_3_0 ps_deferred_3_0(1, int4(0,0,1,0)),
	compile ps_3_0 ps_deferred_3_0(1, int4(0,0,1,1)),
	compile ps_3_0 ps_deferred_3_0(1, int4(0,1,0,0)),
	compile ps_3_0 ps_deferred_3_0(1, int4(0,1,0,1)),
	compile ps_3_0 ps_deferred_3_0(1, int4(0,1,1,0)),
	compile ps_3_0 ps_deferred_3_0(1, int4(0,1,1,1)),
	compile ps_3_0 ps_deferred_3_0(1, int4(1,0,0,0)),
	compile ps_3_0 ps_deferred_3_0(1, int4(1,0,0,1)),
	compile ps_3_0 ps_deferred_3_0(1, int4(1,0,1,0)),
	compile ps_3_0 ps_deferred_3_0(1, int4(1,0,1,1)),
	compile ps_3_0 ps_deferred_3_0(1, int4(1,1,0,0)),
	compile ps_3_0 ps_deferred_3_0(1, int4(1,1,0,1)),
	compile ps_3_0 ps_deferred_3_0(1, int4(1,1,1,0)),
	compile ps_3_0 ps_deferred_3_0(1, int4(1,1,1,1)),
};

//--------------------------------------------------------------------------------------------------
technique MAIN
{
	pass Pass_0
	{
        //-- Turn on alpha blend and set dest blend to 1 if using multiple passes.
		ALPHATESTENABLE		= FALSE;
        ALPHABLENDENABLE	= (useMultipassBlending ? 1 : 0);
        SRCBLEND			= ONE;
        DESTBLEND			= (useMultipassBlending ? BW_BLEND_ONE : BW_BLEND_ZERO);
        ZWRITEENABLE		= (hasHoles || useMultipassBlending ? 0 : 1);
        ZFUNC				= (hasHoles || useMultipassBlending ? BW_CMP_EQUAL : BW_CMP_LESSEQUAL);
        ZENABLE				= TRUE;
		CULLMODE			= BW_CULL_CCW;

		//-- render target mask.
		//-- Note: these mask should be in sync with the g-buffer layout.
		COLORWRITEENABLE	= (useMultipassBlending ? 0x00 : 0xFF);
		COLORWRITEENABLE1	= (useMultipassBlending ? 0x07 : 0xFF);
		COLORWRITEENABLE2	= (useMultipassBlending ? 0x07 : 0xFF);
		
		VertexShader = deferredVS[bumpShaderMask > 0 ? 1 : 0];
		PixelShader  = deferredPS[bumpShaderMask];
	}
}

//--------------------------------------------------------------------------------------------------
technique REFLECTION
{
	pass Pass_0
	{
		//-- Turn on alpha blend and set dest blend to 1 if using multiple passes.
		ALPHATESTENABLE		= FALSE;
        ALPHABLENDENABLE	= (useMultipassBlending ? 1 : 0);
        SRCBLEND			= ONE;
        DESTBLEND			= (useMultipassBlending ? BW_BLEND_ONE : BW_BLEND_ZERO);
        ZWRITEENABLE		= (hasHoles || useMultipassBlending ? 0 : 1);
        ZFUNC				= (hasHoles || useMultipassBlending ? BW_CMP_EQUAL : BW_CMP_LESSEQUAL);
        ZENABLE				= TRUE;
		CULLMODE			= BW_CULL_CCW;

		VertexShader = compile vs_3_0 vs_reflection_3_0();
		PixelShader  = compile ps_3_0 ps_reflection_3_0();
	}
}

//--------------------------------------------------------------------------------------------------
#else

//--------------------------------------------------------------------------------------------------
struct TerrainVS2PS
{
	float4 pos				: POSITION;
	float4 normalBlendUV	: TEXCOORD0;	//-- normal.uv = xy, blend.uv = zw
    float3 horizonUVFog		: TEXCOORD1;	//-- horizon.uv = xy,fog = z
	float4 layer01UV		: TEXCOORD2;	//-- layer0.uv = xy, layer1.uv = zw
	float4 layer23UV		: TEXCOORD3;	//-- layer2.uv = xy, layer3.uv = zw
};

//--------------------------------------------------------------------------------------------------
half4 getDiffuseColor(const TerrainVS2PS i, const half4 blenMask)
{
	half4 diffuseColor = half4(0,0,0,0);
	diffuseColor += tex2D(layer0Sampler, half2(i.layer01UV.x, i.layer01UV.y)) * blenMask.x;
	diffuseColor += tex2D(layer1Sampler, half2(i.layer01UV.z, i.layer01UV.w)) * blenMask.y;
	diffuseColor += tex2D(layer2Sampler, half2(i.layer23UV.x, i.layer23UV.y)) * blenMask.z;
	diffuseColor += tex2D(layer3Sampler, half2(i.layer23UV.z, i.layer23UV.w)) * blenMask.w;
	return diffuseColor;
}

//--------------------------------------------------------------------------------------------------
TerrainVS2PS vs_main_2_0(in TerrainVertex i)
{
	TerrainVS2PS o = (TerrainVS2PS)0;
	
	//-- calculate the position of the vertex.
	float4 wPos = terrainVertexPosition(i);
	o.pos = mul(wPos, g_viewProjMat);
	
	//-- calculate the texture coordinate for the normal map.
	o.normalBlendUV.xy = inclusiveTextureCoordinate(i.xz, float2(normalMapSize, normalMapSize));
	
	//-- calculate the texture coordinate for the blend map.
	o.normalBlendUV.zw = inclusiveTextureCoordinate(i.xz, float2(blendMapSize, blendMapSize));
	
	//-- calculate the texture coordinates for our texture layers
	o.layer01UV.xy = float2(dot(layer0UProjection, wPos), dot(layer0VProjection, wPos));
	o.layer01UV.zw = float2(dot(layer1UProjection, wPos), dot(layer1VProjection, wPos));
	o.layer23UV.xy = float2(dot(layer2UProjection, wPos), dot(layer2VProjection, wPos));
	o.layer23UV.zw = float2(dot(layer3UProjection, wPos), dot(layer3VProjection, wPos));

	o.layer01UV = o.layer01UV * float4(+1,-1,+1,-1) + 0.5f;
	o.layer23UV = o.layer23UV * float4(+1,-1,+1,-1) + 0.5f;
	
	//-- calculate the texture coordinate for the horizon map.
	o.horizonUVFog.xy = inclusiveTextureCoordinate(i.xz, float2(horizonMapSize, horizonMapSize));

	//-- fog.
	o.horizonUVFog.z = bw_vertexFog(wPos, o.pos.w);

	return o;
}

//--------------------------------------------------------------------------------------------------
float4 ps_main_2_0(const TerrainVS2PS i) : COLOR0
{
	//-- calculate blend mask of 4 layers.
	half4 blendMask = getBlendMask(i.normalBlendUV.zw);

	//-- get the blended diffuse color.
	half4 diffuseColor = getDiffuseColor(i, blendMask);

	//-- get the normal from the terrain normal map.
	half3 normal = terrainNormal(normalMapSampler, i.normalBlendUV.xy);
	
	//-- horizon shadow.
    half shadow = tex2D(horizonMapSampler, i.horizonUVFog.xy).x;
	
	//-- calculate sun influence.
	half3 o = diffuseColor * (sunAmbientTerm() + shadow * sunDiffuseTerm(normal));
	
	//-- fog.
	const half blendSum = dot(blendMask, 1);
	o = applyFogTo(o, g_fogParams.m_color.rgb * blendSum, i.horizonUVFog.z);

	return float4(o, 1);
};

//--------------------------------------------------------------------------------------------------
technique MAIN
{
	pass Pass_0
	{
        //-- Turn on alpha blend and set dest blend to 1 if using multiple passes.
		ALPHATESTENABLE		= FALSE;
        ALPHABLENDENABLE	= (useMultipassBlending ? 1 : 0);
        SRCBLEND			= ONE;
        DESTBLEND			= (useMultipassBlending ? BW_BLEND_ONE : BW_BLEND_ZERO);
        ZWRITEENABLE		= (hasHoles || useMultipassBlending ? 0 : 1);
        ZFUNC				= (hasHoles || useMultipassBlending ? BW_CMP_EQUAL : BW_CMP_LESSEQUAL);
        ZENABLE				= TRUE;
		CULLMODE			= BW_CULL_CCW;
		FOGENABLE			= FALSE;
		
        VertexShader = compile vs_2_0 vs_main_2_0();
		PixelShader  = compile ps_2_0 ps_main_2_0();
	}
}

//--------------------------------------------------------------------------------------------------
technique REFLECTION
{
	pass Pass_0
	{
        //-- Turn on alpha blend and set dest blend to 1 if using multiple passes.
		ALPHATESTENABLE		= FALSE;
        ALPHABLENDENABLE	= (useMultipassBlending ? 1 : 0);
        SRCBLEND			= ONE;
        DESTBLEND			= (useMultipassBlending ? BW_BLEND_ONE : BW_BLEND_ZERO);
        ZWRITEENABLE		= (hasHoles || useMultipassBlending ? 0 : 1);
        ZFUNC				= (hasHoles || useMultipassBlending ? BW_CMP_EQUAL : BW_CMP_LESSEQUAL);
        ZENABLE				= TRUE;
		CULLMODE			= BW_CULL_CCW;
        FOGENABLE			= FALSE;
		
        VertexShader = compile vs_2_0 vs_main_2_0();
		PixelShader  = compile ps_2_0 ps_main_2_0();
	}
}

#endif //-- BW_DEFERRED_SHADING

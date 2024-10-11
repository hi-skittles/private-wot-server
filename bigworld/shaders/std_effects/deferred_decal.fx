#include "stdinclude.fxh"
#include "read_g_buffer.fxh"

//--------------------------------------------------------------------------------------------------
sampler g_bitwiseLUTMapSml = sampler_state
{
	Texture = <g_bitwiseLUTMap>;
	MipFilter = POINT;
	MinFilter = POINT;
	MagFilter = POINT;
};

//--------------------------------------------------------------------------------------------------
texture g_atlasMap;
sampler g_atlasMapSml = sampler_state	
{									
	Texture = (g_atlasMap);
	ADDRESSU = BORDER;
	ADDRESSV = BORDER;
	ADDRESSW = BORDER;
	MAGFILTER = LINEAR;
	MINFILTER = (minMagFilter);
	MIPFILTER = (mipFilter);
	MAXANISOTROPY = (maxAnisotropy);
	MAXMIPLEVEL = 0;
	MIPMAPLODBIAS = 0;
	BORDERCOLOR = float4(0,0,0,0);
};

//--------------------------------------------------------------------------------------------------
const float4 g_atlasSize;

//-- unpacked decal data.
//--------------------------------------------------------------------------------------------------
struct DecalData
{
	float3 m_pos;
	float3 m_scale;
	float3 m_axisX;
	float3 m_axisY;
	float3 m_axisZ;
	float  m_surface;
};

//--------------------------------------------------------------------------------------------------
DecalData unpackDecal(const InstancingStream i)
{
	DecalData o = (DecalData)0;

	o.m_pos	  = i.v1.xyz;
	o.m_scale = i.v3.xyz;
	o.m_axisZ = normalize(i.v0.xyz);
	o.m_axisY = normalize(i.v2.xyz);
	o.m_axisX = cross(o.m_axisY, o.m_axisZ);

	return o;
}

//-- unpack texture coordinates offset and scale in the texture atlas map1.
//--------------------------------------------------------------------------------------------------
float4 unpackTexMap1(const InstancingStream i)
{
	float4 o;
	o.zw  = floor(float2(i.v0.w, i.v1.w));
	o.xy  = float2(i.v0.w, i.v1.w) - o.zw;
	o.zw *= g_atlasSize.zw;
	return o;
}

//-- unpack texture coordinates offset and scale in the texture atlas map2.
//--------------------------------------------------------------------------------------------------
float4 unpackTexMap2(const InstancingStream i)
{
	float4 o;
	o.zw  = floor(float2(i.v2.w, i.v3.w));
	o.xy  = float2(i.v2.w, i.v3.w) - o.zw;
	o.zw *= g_atlasSize.zw;
	return o;
}

//-- clamp texture coordinates of decals inside its own texture atlas sub-image bounds to prevent
//-- sampling from adjaset sub-images.
//--------------------------------------------------------------------------------------------------
float clampToBorder(in float2 tc, in float4 mapTC)
{
	float2 clampedAtlasUV = clamp(tc, mapTC.xy, mapTC.xy + mapTC.zw);
	return 1.0f - (float)any(clampedAtlasUV - tc);
}

//-- Returns 1.0f if desired bit (testBit) is set to 1 in the bits set (bitSet) else 0.0f
//--------------------------------------------------------------------------------------------------
float influenceMask(in float bitSet, in float testBit)
{
	static const float2 g_invBits = 1.0f / float2(255.0f, 7.0f);
	return tex2Dlod(g_bitwiseLUTMapSml, float4(float2(bitSet, testBit) * g_invBits, 0, 0)).x;
}

//--------------------------------------------------------------------------q------------------------
struct DecalVertex
{
	float3 pos	  :	POSITION;
	float2 tc	  :	TEXCOORD0;
	float3 normal :	NORMAL;

	//-- instance data.
	InstancingStream instance;
};

//-- pixel shader output in case of bumped decal.
//--------------------------------------------------------------------------------------------------
struct DECAL_PS_OUT_ONE_RT
{
	float4 color0 : COLOR0;
};

struct DECAL_PS_OUT_TWO_RT
{
	float4 color0 : COLOR0;
	float4 color1 : COLOR1;
};

//--------------------------------------------------------------------------------------------------
struct DECAL_VS2PS_STENCIL
{
	float4 pos : POSITION;
};

//-- ToDo: Think about using so named no_iterpolation flag for matrices are passed from vs shader.
//--	   Maybe on the new hardware it gives us additional performace boost, because rasterizer
//--	   will not do unneccessary perspective interpolation of the input parameters.
//--------------------------------------------------------------------------------------------------
struct DECAL_VS2PS
{
	float4 pos		 : POSITION;

	//-- decal's VP matrix.
	float4 row0		 : TEXCOORD0;
	float4 row1		 : TEXCOORD1;
	float4 row2		 : TEXCOORD2;
	float4 row3		 : TEXCOORD3;

	float2 blendSurf : TEXCOORD4;
	float4 map1TC	 : TEXCOORD5;

};

//-- ToDo: Think about using so named no_iterpolation flag for matrices are passed from vs shader.
//--	   Maybe on the new hardware it gives us additional performace boost, because rasterizer
//--	   will not do unneccessary perspective interpolation of the input parameters.
//--------------------------------------------------------------------------------------------------
struct DECAL_VS2PS_EXT
{
	float4 pos		: POSITION;

	//-- decal's VP matrix.
	float4 row0		: TEXCOORD0;
	float4 row1		: TEXCOORD1;
	float4 row2		: TEXCOORD2;
	float4 row3		: TEXCOORD3;

	float4 map1TC	: TEXCOORD4;
	float4 map2TC	: TEXCOORD5;

	//-- tbn basis.
	float4 tbn0		: TEXCOORD6; //-- tbn and blendFactor
	float4 tbn1		: TEXCOORD7; //-- tbn and surface type.
	float3 tbn2		: COLOR0;    //-- Note: to prevent clamping value in range [0,1] we manually normalize vector.
};

//--------------------------------------------------------------------------------------------------
static const float g_parallaxScale    = 0.01f;
static const float g_parallaxMinSteps = 5;
static const float g_parallaxMaxSteps = 25;

//-- calculate texture coordinates after parallax effect apllied to them.
//--------------------------------------------------------------------------------------------------
half2 getParallaxedTC(in half3 eyeInTS, in half2 tc)
{
	//-- select steps number based on the eye position in tangent space. If it's far away from
	//-- the surface we can minimize step count, but if we near the surface we have to do more
	//-- precise calculation to remove noticable layering in the image.
	half numSteps = lerp(g_parallaxMaxSteps, g_parallaxMinSteps, eyeInTS.z);

	//-- calculate step value.
	half step = 1.0f / numSteps;

	//-- adjustment for one layer.
	half2 dtex = eyeInTS.xy * g_parallaxScale * step / eyeInTS.z;

	//-- height of the layer.
	half height = 1.0f;

	//-- initial guess.
	half2 tex = tc;

	//-- get height
	half h = tex2D(g_atlasMapSml, tex).a;

	float LOD = computeTextureLOD(tex, g_atlasSize.xy);

	while (h < height)
	{
		height -= step;
		tex    += dtex;
		h       = tex2Dlod(g_atlasMapSml, half4(tex, 0, LOD)).a;
	}

	//-- now find point via linear interpolation previous point.
	half2 prev   = tex - dtex;				
	half  hPrev  = tex2D(g_atlasMapSml, prev).a - (height + step); //-- < 0
	half  hCur   = h - height;	//-- > 0
	half  weight = hCur / (hCur - hPrev);
	
	tex = lerp(tex, prev, weight);

	return tex;
}

//--------------------------------------------------------------------------------------------------
float4x4 calcDecalWorldMat(const DecalData i)
{
	//-- compute world matrix.
	//-- world = scale * rotateTranslate.

	float4x4 worldMat = 
	{
		{i.m_axisX * i.m_scale.x, 0},
		{i.m_axisY * i.m_scale.y, 0},
		{i.m_axisZ * i.m_scale.z, 0},
		{i.m_pos,   1}
	};

	//-- final world matrix.
	return worldMat;
}

//-- ToDo: optimize.
//--------------------------------------------------------------------------------------------------
float4x4 calcDecalViewProjMat(const DecalData i)
{
	//-- 1. compute data for the decal view matrix.
	//--
	//-- zaxis = normal(dir)
	//-- xaxis = normal(cross(Up, zaxis))
	//-- yaxis = cross(zaxis, xaxis)
	//--
	//-- xaxis.x           yaxis.x           zaxis.x          0
	//-- xaxis.y           yaxis.y           zaxis.y          0
	//-- xaxis.z           yaxis.z           zaxis.z          0
	//-- -dot(xaxis, pos)  -dot(yaxis, pos)  -dot(zaxis, pos) l
	//--
	float4x4 lookAtMat = 
	{
		{i.m_axisX.x,				i.m_axisY.x,				i.m_axisZ.x,				0},
		{i.m_axisX.y,				i.m_axisY.y,				i.m_axisZ.y,				0},
		{i.m_axisX.z,				i.m_axisY.z,				i.m_axisZ.z,				0},
		{-dot(i.m_axisX, i.m_pos),  -dot(i.m_axisY, i.m_pos),	-dot(i.m_axisZ, i.m_pos),	1}
	};
	
	//-- 2. compute data for the decal proj matrix.
	//--
	//-- 2/w   0        0       0
	//-- 0     2/h      0       0
	//-- 0     0    1/(zf-zn)   0
	//-- 0     0    -zn/(zf-zn) l
	//--
	// zn = -0.5f * scale.z;
	// zf = +0.5f * scale.z;
	//--
	float4x4 projMat = 
	{
		{2.0f / i.m_scale.x,	0,						0,					0},
		{0,				 		2.0f / i.m_scale.y,		0,					0},
		{0,				 		0,						1.0f / i.m_scale.z,	0},
		{0,  			 		0,						0.5f,				1}
	};
	
	//-- 3. caclulate final view-projection decal matrix.
	return mul(lookAtMat, projMat);
}

//-- ToDo: optimize.
//--------------------------------------------------------------------------------------------------
float3x3 calcDecalTBNBasis(const DecalData i)
{
	float3x3 tbn = { +i.m_axisX, -i.m_axisY, -i.m_axisZ };
	return tbn;
}

//--------------------------------------------------------------------------------------------------
DECAL_VS2PS_STENCIL VS_STENCIL(const DecalVertex i)
{
	DECAL_VS2PS_STENCIL o = (DECAL_VS2PS_STENCIL)0;

	//-- 1. unpack decal data.
	DecalData decal = unpackDecal(i.instance);
	
	//-- 2. calculate decal world matrix.
	float4x4 worldMat = calcDecalWorldMat(decal);

	//-- 3. Now do regular vertex shader with usage of the previous calculated data.
	float4 wPos	= mul(float4(i.pos, 1.0f), worldMat);

	//-- 4.
	o.pos = mul(wPos, g_viewProjMat);

	return o;
}

//--------------------------------------------------------------------------------------------------
DECAL_VS2PS VS(const DecalVertex i)
{
	DECAL_VS2PS o = (DECAL_VS2PS)0;

	//-- 1. retrieve instance data.
	DecalData decal = unpackDecal(i.instance);
	
	//-- 2. calculate decal matrices.
	float4x4 viewProjMat = calcDecalViewProjMat(decal);
	float4x4 worldMat	 = calcDecalWorldMat(decal);

	//-- 3. Now do regular vertex shader with usage of the previous calculated data.
	float4 wPos	= mul(float4(i.pos, 1.0f), worldMat);

	//-- 4. write decal view-proj matrix.
	o.pos  = mul(wPos, g_viewProjMat);
	o.row0 = viewProjMat[0];
	o.row1 = viewProjMat[1];
	o.row2 = viewProjMat[2];
	o.row3 = viewProjMat[3];

	//-- 5. unpack texture coordinates offset and scale in the texture atlas.
	o.map1TC = unpackTexMap1(i.instance);

	//-- 6. write blend factor and material kind.
	o.blendSurf.x = length(i.instance.v0.xyz) - 0.5f;
	o.blendSurf.y = length(i.instance.v2.xyz) - 0.5f;

	return o;
}

//--------------------------------------------------------------------------------------------------
DECAL_VS2PS_EXT VS_EXT(const DecalVertex i)
{
	DECAL_VS2PS_EXT o = (DECAL_VS2PS_EXT)0;

	//-- 1. retrieve instance data.
	DecalData decal = unpackDecal(i.instance);

	//-- 2. calculate decal matrices.
	float4x4 viewProjMat = calcDecalViewProjMat(decal);
	float4x4 worldMat	 = calcDecalWorldMat(decal);
	float3x3 TBN		 = calcDecalTBNBasis(decal);

	//-- 3. Now do regular vertex shader with usage of the previous calculated data.
	float4 wPos	= mul(float4(i.pos, 1.0f), worldMat);

	//-- 4. write decal view-proj matrix.
	o.pos  = mul(wPos, g_viewProjMat);
	o.row0 = viewProjMat[0];
	o.row1 = viewProjMat[1];
	o.row2 = viewProjMat[2];
	o.row3 = viewProjMat[3];

	//-- 5. write decal tbn basis.
	o.tbn0.xyz = TBN[0];
	o.tbn1.xyz = TBN[1];
	o.tbn2     = TBN[2] * 0.5f + 0.5f;

	//-- 6. write blend factor and material kind.
	o.tbn0.w = length(i.instance.v0.xyz) - 0.5f;
	o.tbn1.w = length(i.instance.v2.xyz) - 0.5f;
	
	//-- 7. unpack texture coordinates offset and scale in the texture atlas.
	o.map1TC = unpackTexMap1(i.instance);
	o.map2TC = unpackTexMap2(i.instance);

	return o;
}

//--------------------------------------------------------------------------------------------------
float4 PS_STENCIL(DECAL_VS2PS_STENCIL i) : COLOR0
{
	//-- is not important what we send to the buffer, because writing to the color buffer disabled
	//-- by the render state.
	return float4(0,0,0,0);
}

//--------------------------------------------------------------------------------------------------
DECAL_PS_OUT_ONE_RT PS_DIFFUSE(const DECAL_VS2PS i, in float2 vPos : VPOS)
{
	DECAL_PS_OUT_ONE_RT o = (DECAL_PS_OUT_ONE_RT)0;

	float2 screenXY = SC2TC(vPos);

	//-- read GBuffer properties.
	float3 wPos    = g_buffer_readWorldPos(screenXY, g_nvStereoParams.w);
	float  objKind = g_buffer_readObjectKind(screenXY);

	//-- reconstruct decal projection matrix.
	float4x4 decalViewProjMat = { i.row0, i.row1, i.row2, i.row3 };

	//-- calculate texture coordinates for projection texture.
	float4 cPos = mul(float4(wPos, 1.0f), decalViewProjMat);
	cPos.xyz /= cPos.w;

	//-- calculate texture coordinates in the atlas for diffuse and bump TC.
	float2 atlasUV = i.map1TC.xy + CS2TS(cPos.xy) * i.map1TC.zw;

	//-- retreive diffuse decal's color.
	float4 oColor = gamma2linear(tex2D(g_atlasMapSml, atlasUV));
	
	//-- alpha value for blending.
	float alpha = oColor.w;
	//-- clam to border.
	alpha *= clampToBorder(atlasUV, i.map1TC);
	//-- apply distance fader.
	alpha *= 1.0f - abs(cPos.z * 2.0f - 1.0f);
	//-- apply manual alpha fader.
	alpha *= i.blendSurf.x;
	//-- apply influence type
	alpha *= influenceMask(i.blendSurf.y, objKind);

	//-- write output.	
	//-- Note: we doesn't write alpha into any of the final buffers. Alpha used only for doing correct
	//--	   alpha blending operations.
	o.color0 = float4(oColor.xyz, alpha);

	return o;
}

//--------------------------------------------------------------------------------------------------
DECAL_PS_OUT_ONE_RT PS_OVERDRAW(const DECAL_VS2PS i, in float2 vPos : VPOS)
{
	DECAL_PS_OUT_ONE_RT o = (DECAL_PS_OUT_ONE_RT)0;

	o.color0 = float4(1.0f, 0.0f, 0.0f, 0.1f);

	return o;
}

//--------------------------------------------------------------------------------------------------
DECAL_PS_OUT_TWO_RT PS_BUMP(const DECAL_VS2PS_EXT i, in float2 vPos : VPOS)
{
	DECAL_PS_OUT_TWO_RT o = (DECAL_PS_OUT_TWO_RT)0;

	float2 screenXY = SC2TC(vPos);

	//-- read GBuffer properties.
	float3 wPos	   = g_buffer_readWorldPos(screenXY, g_nvStereoParams.w);
	float  objKind = g_buffer_readObjectKind(screenXY);

	//-- reconstruct decal projection matrix.
	float4x4 decalViewProjMat = { i.row0, i.row1, i.row2, i.row3 };

	//-- calculate texture coordinates for projection texture.
	float4 cPos = mul(float4(wPos, 1.0f), decalViewProjMat);
	cPos.xyz /= cPos.w;

	//-- calculate texture coordinates in the atlas for diffuse and bump TC.
	float2 baseUV	= CS2TS(cPos.xy);
	float2 atlas1UV = i.map1TC.xy + baseUV * i.map1TC.zw;
	float2 atlas2UV = i.map2TC.xy + baseUV * i.map2TC.zw;

	//-- retreive diffuse decal's color.
	float4 oColor = gamma2linear(tex2D(g_atlasMapSml, atlas1UV));
	
	//-- compute TBN basis.
	float3x3 TBN = {i.tbn0.xyz, i.tbn1.xyz, i.tbn2 * 2.0f - 1.0f};

	//-- calculate world normal.
	float4 map2Src = tex2D(g_atlasMapSml, atlas2UV);
	float3 nn	   = map2Src.xyz * 2.0f - 1.0f;
	float3 oNormal = float3(cartesianToSpherical(normalize(mul(nn, TBN))), map2Src.w);

	//-- alpha value for blending.
	float alpha = oColor.w;
	//-- clam to border.
	alpha *= clampToBorder(atlas1UV, i.map1TC);
	//-- apply distance fader.
	alpha *= cPos.z * 2.0f;
	//-- apply manual alpha fader.
	alpha *= i.tbn0.w;
	//-- apply influence type
	alpha *= influenceMask(i.tbn1.w, objKind);

	//-- write output.	
	//-- Note: we doesn't write alpha into any of the final buffers. Alpha used only for doing correct
	//--	   alpha blending operations.
	o.color0 = float4(oColor.xyz, alpha);
	o.color1 = float4(oNormal, alpha);

	return o;
}

//--------------------------------------------------------------------------------------------------
DECAL_PS_OUT_TWO_RT PS_PARALLAX(const DECAL_VS2PS_EXT i, in float2 vPos : VPOS)
{
	DECAL_PS_OUT_TWO_RT o = (DECAL_PS_OUT_TWO_RT)0;

	float2 screenXY = SC2TC(vPos);

	//-- read GBuffer properties.
	float3 wPos    = g_buffer_readWorldPos(screenXY, g_nvStereoParams.w);
	float  objKind = g_buffer_readObjectKind(screenXY);

	//-- reconstruct decal projection matrix.
	float4x4 decalViewProjMat = { i.row0, i.row1, i.row2, i.row3 };

	//-- calculate texture coordinates for projection texture.
	float4 cPos = mul(float4(wPos, 1.0f), decalViewProjMat);
	cPos.xyz /= cPos.w;

	//-- calculate texture coordinates in the atlas for diffuse and bump TC.
	float2 baseUV	= CS2TS(cPos.xy);
	float2 atlas1UV = i.map1TC.xy + baseUV * i.map1TC.zw;
	float2 atlas2UV = i.map2TC.xy + baseUV * i.map2TC.zw;

	//-- compute TBN basis.
	float3x3 TBN = {i.tbn0.xyz, i.tbn1.xyz, i.tbn2 * 2.0f - 1.0f};

	//-- find eye direction in the tangent space.
	half3 eyeDir  = normalize(g_cameraPos.xyz - wPos);
	half3 eyeInTS = normalize(mul(TBN, eyeDir));

	//-- find parallaxed texture coordinates.
	half2 newAtlas2UV = getParallaxedTC(eyeInTS, atlas2UV);
	half2 newAtlas1UV = newAtlas2UV;//atlas1UV;// + (atlas2UV - newAtlas2UV);

	//-- retreive diffuse decal's color.
	float4 oColor = gamma2linear(tex2D(g_atlasMapSml, newAtlas1UV));

	//-- calculate world normal.
	float3 nn	   = (tex2D(g_atlasMapSml, newAtlas2UV).xyz * 2.0f) - 1.0f;
	float3 oNormal = float3(cartesianToSpherical(normalize(mul(nn, TBN))), 0);

	//-- alpha value for blending.
	float alpha = oColor.w;
	//-- clam to border.
	alpha *= clampToBorder(newAtlas1UV, i.map1TC);
	//-- apply distance fader.
	alpha *= cPos.z * 2.0f;
	//-- apply manual alpha fader.
	alpha *= i.tbn0.w;
	//-- apply influence type
	alpha *= influenceMask(i.tbn1.w, objKind);

	//-- write output.	
	//-- Note: we doesn't write alpha into any of the final buffers. Alpha used only for doing correct
	//--	   alpha blending operations.
	o.color0 = float4(oColor.xyz, alpha);
	o.color1 = float4(oNormal, alpha);

	return o;
}

//--------------------------------------------------------------------------------------------------
DECAL_PS_OUT_TWO_RT PS_ENV_MAPPING(const DECAL_VS2PS_EXT i, in float2 vPos : VPOS)
{
	DECAL_PS_OUT_TWO_RT o = (DECAL_PS_OUT_TWO_RT)0;

	//-- ToDo: implement.

	float2 screenXY = SC2TC(vPos);

	//-- read GBuffer properties.
	float objKind = g_buffer_readObjectKind(screenXY);

	/*
	static float3 g_matKinds[] = {
		float3(0,0,0),
		float3(1,0,0),
		float3(0,1,0),
		float3(0,0,1),
		float3(1,1,1)
	};

	o.color0 = float4(g_matKinds[(int)matKind], 1);
	*/

	o.color0 = float4(1,0,0, influenceMask(i.tbn1.w, objKind));

	return o;
}

//-- ToDo: reconsider state bucket. I feel that we can greatly improve this.
//--------------------------------------------------------------------------------------------------
technique STENCIL
{
	//-- clear stencil.
	pass Pass_0
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
		COLORWRITEENABLE1 = 0x00;

		STENCILENABLE = TRUE;
		STENCILWRITEMASK = G_STENCIL_CUMSTOM_WRITE_MASK;
		STENCILMASK = G_STENCIL_CUMSTOM_WRITE_MASK;
		STENCILFUNC = ALWAYS;
		STENCILPASS = REPLACE;
		STENCILFAIL = REPLACE;
		STENCILZFAIL = REPLACE;
		STENCILREF = 0x00;
										
		VertexShader = compile vs_3_0 VS_STENCIL();
		PixelShader  = compile ps_3_0 PS_STENCIL();
	}

	//-- fill stencil.
	pass Pass_1
	{
		CULLMODE = CW;
		ZENABLE = TRUE;
		ZFUNC = GREATEREQUAL;

		STENCILENABLE = TRUE;
		STENCILWRITEMASK = G_STENCIL_CUMSTOM_WRITE_MASK;
		STENCILMASK = G_STENCIL_CUMSTOM_WRITE_MASK;
		STENCILFUNC = ALWAYS;
		STENCILPASS = INCR;
		STENCILFAIL = KEEP;
		STENCILZFAIL = KEEP;
										
		VertexShader = compile vs_3_0 VS_STENCIL();
		PixelShader  = compile ps_3_0 PS_STENCIL();
	}
}

//--------------------------------------------------------------------------------------------------
technique DIFFUSE
{
	pass Pass_0
	{
		ALPHATESTENABLE = FALSE;
		CULLMODE = CCW;
		ZENABLE = TRUE;
		ZFUNC = LESSEQUAL;
		ZWRITEENABLE = FALSE;
		FOGENABLE = FALSE;		
		ALPHABLENDENABLE = TRUE;
		SRCBLEND = SRCALPHA;				
		DESTBLEND = INVSRCALPHA;
		BLENDOP = ADD;	
		POINTSPRITEENABLE = FALSE;
		COLORWRITEENABLE  = 0x07; //-- write all except alpha.
		COLORWRITEENABLE1 = 0x00;

		STENCILENABLE = TRUE;
		STENCILFUNC = LESS;
		STENCILWRITEMASK = G_STENCIL_CUMSTOM_WRITE_MASK;
		STENCILMASK = G_STENCIL_CUMSTOM_WRITE_MASK;
		STENCILPASS = KEEP;
		STENCILZFAIL = DECRSAT;
		STENCILFAIL = KEEP;
		STENCILREF = 0;
										
		VertexShader = compile vs_3_0 VS();
		PixelShader  = compile ps_3_0 PS_DIFFUSE();
	}
}

//--------------------------------------------------------------------------------------------------
technique BUMP
{					
	pass Pass_0
	{
		ALPHATESTENABLE = FALSE;
		CULLMODE = CCW;
		ZENABLE = TRUE;
		ZFUNC = LESSEQUAL;
		ZWRITEENABLE = FALSE;
		FOGENABLE = FALSE;		
		ALPHABLENDENABLE = TRUE;
		SRCBLEND = SRCALPHA;				
		DESTBLEND = INVSRCALPHA;
		BLENDOP = ADD;	
		POINTSPRITEENABLE = FALSE;
		COLORWRITEENABLE  = 0x07; //-- write all except alpha.
		COLORWRITEENABLE1 = 0x07;

		STENCILENABLE = TRUE;
		STENCILFUNC = LESS;
		STENCILWRITEMASK = G_STENCIL_CUMSTOM_WRITE_MASK;
		STENCILMASK = G_STENCIL_CUMSTOM_WRITE_MASK;
		STENCILPASS = KEEP;
		STENCILZFAIL = DECRSAT;
		STENCILFAIL = KEEP;
		STENCILREF = 0;
										
		VertexShader = compile vs_3_0 VS_EXT();
		PixelShader  = compile ps_3_0 PS_BUMP();
	}
}

//--------------------------------------------------------------------------------------------------
technique PARALLAX
{									
	pass Pass_0							
	{		
		ALPHATESTENABLE = FALSE;
		CULLMODE = CCW;
		ZENABLE = TRUE;
		ZFUNC = LESSEQUAL;
		ZWRITEENABLE = FALSE;
		FOGENABLE = FALSE;		
		ALPHABLENDENABLE = TRUE;
		SRCBLEND = SRCALPHA;				
		DESTBLEND = INVSRCALPHA;
		BLENDOP = ADD;	
		POINTSPRITEENABLE = FALSE;
		COLORWRITEENABLE  = 0x07; //-- write all except alpha.
		COLORWRITEENABLE1 = 0x07;

		STENCILENABLE = TRUE;
		STENCILFUNC = LESS;
		STENCILWRITEMASK = G_STENCIL_CUMSTOM_WRITE_MASK;
		STENCILMASK = G_STENCIL_CUMSTOM_WRITE_MASK;
		STENCILPASS = KEEP;
		STENCILZFAIL = DECRSAT;
		STENCILFAIL = KEEP;
		STENCILREF = 0;
										
		VertexShader = compile vs_3_0 VS_EXT();
		PixelShader  = compile ps_3_0 PS_PARALLAX();
	}
}

//--------------------------------------------------------------------------------------------------
technique ENV_MAPPING
{									
	pass Pass_0							
	{		
		ALPHATESTENABLE = FALSE;
		CULLMODE = CCW;
		ZENABLE = TRUE;
		ZFUNC = LESSEQUAL;
		ZWRITEENABLE = FALSE;
		FOGENABLE = FALSE;		
		ALPHABLENDENABLE = TRUE;
		SRCBLEND = SRCALPHA;				
		DESTBLEND = INVSRCALPHA;
		BLENDOP = ADD;	
		POINTSPRITEENABLE = FALSE;
		COLORWRITEENABLE  = 0x07; //-- write all except alpha.
		COLORWRITEENABLE1 = 0x07;

		STENCILENABLE = TRUE;
		STENCILFUNC = LESS;
		STENCILWRITEMASK = G_STENCIL_CUMSTOM_WRITE_MASK;
		STENCILMASK = G_STENCIL_CUMSTOM_WRITE_MASK;
		STENCILPASS = KEEP;
		STENCILZFAIL = DECRSAT;
		STENCILFAIL = KEEP;
		STENCILREF = 0;
										
		VertexShader = compile vs_3_0 VS_EXT();
		PixelShader  = compile ps_3_0 PS_ENV_MAPPING();
	}
}

//--------------------------------------------------------------------------------------------------
technique DEBUG_OVERDRAW
{
	pass Pass_0
	{
		ALPHATESTENABLE = FALSE;
		CULLMODE = CCW;
		ZENABLE = TRUE;
		ZFUNC = LESSEQUAL;
		ZWRITEENABLE = FALSE;
		FOGENABLE = FALSE;		
		ALPHABLENDENABLE = TRUE;
		SRCBLEND = SRCALPHA;				
		DESTBLEND = INVSRCALPHA;
		BLENDOP = ADD;	
		POINTSPRITEENABLE = FALSE;
		COLORWRITEENABLE  = 0xFF; //-- write all except alpha.
		COLORWRITEENABLE1 = 0x00;

		STENCILENABLE = TRUE;
		STENCILFUNC = LESS;
		STENCILWRITEMASK = G_STENCIL_CUMSTOM_WRITE_MASK;
		STENCILMASK = G_STENCIL_CUMSTOM_WRITE_MASK;
		STENCILPASS = KEEP;
		STENCILZFAIL = DECRSAT;
		STENCILFAIL = KEEP;
		STENCILREF = 0;
										
		VertexShader = compile vs_3_0 VS();
		PixelShader  = compile ps_3_0 PS_OVERDRAW();
	}
}

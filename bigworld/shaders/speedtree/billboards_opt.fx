#include "speedtree.fxh"

//--------------------------------------------------------------------------------------------------
float4   g_bbAlphaRefs[64];
//float4   g_bbAlphaRefs[196];

#define g_bbAlphaRefs64 g_bbAlphaRefs
#define g_bbAlphaRefs196 g_bbAlphaRefs

//TODO: extend the maximum instance count...
//float4   g_bbAlphaRefs64[64];
//float4   g_bbAlphaRefs196[196];

//--------------------------------------------------------------------------------------------------
float2   g_UVScale;
float    g_bias = 0.0;

//--------------------------------------------------------------------------------------------------
sampler speedTreeDiffuseSamplerBiased = sampler_state
{
	Texture = (g_diffuseMap);
	ADDRESSU = WRAP;
	ADDRESSV = WRAP;
	ADDRESSW = WRAP;
	MAGFILTER = LINEAR;
	MINFILTER = (minMagFilter);
	MIPFILTER = (mipFilter);
	MAXANISOTROPY = (maxAnisotropy);

	MAXMIPLEVEL = 0;
	MIPMAPLODBIAS = (g_bias);
};

//--------------------------------------------------------------------------------------------------
sampler bbNormalSamplerBiased = sampler_state
{
	Texture       = (g_normalMap);
	ADDRESSU      = WRAP;
	ADDRESSV      = WRAP;
	ADDRESSW      = WRAP;
	MAGFILTER     = POINT;
	MINFILTER     = POINT;
	MIPFILTER     = POINT;

	MAXMIPLEVEL   = 0;
	MIPMAPLODBIAS = (g_bias);
};

//--------------------------------------------------------------------------------------------------
struct VS_INPUT_BB_OPT
{
    float4 pos            : POSITION;
    float3 lightNormal    : NORMAL;
    float3 alphaNormal    : TEXCOORD0;
    float3 texCoordsMatID : TEXCOORD1; //-- xy - texture coordinates, z - material kind.
    float  alphaIndex     : TEXCOORD2;
    float4 alphaMask      : TEXCOORD3;
	float3 binormal       : TEXCOORD4;
	float3 tangent        : TEXCOORD5;
	float4 diffuseNAdjust : TEXCOORD6;
	float3 ambient        : TEXCOORD7;
};

#if BW_DEFERRED_SHADING

//--------------------------------------------------------------------------------------------------
struct ColorVS2PS
{
	float4 pos					: POSITION;
	float4 tcLinearZBlendAlpha	: TEXCOORD0;
	float3 tangent				: TEXCOORD1;
	float3 binormal				: TEXCOORD2;
	float4 normalMatID			: TEXCOORD3; //-- xyz - normal, w - material ID.
};

//--------------------------------------------------------------------------------------------------
ColorVS2PS vs_color_3_0(VS_INPUT_BB_OPT i)
{
	ColorVS2PS o = (ColorVS2PS)0;

	//-- calculate view space position with respect to the wind animation.
	o.pos					 = mul(i.pos, g_viewProjMat);
	o.tcLinearZBlendAlpha.xy = i.texCoordsMatID.xy * g_UVScale.xy;
	o.tcLinearZBlendAlpha.z	 = o.pos.w;

	//-- calculate TBN basis matrix.
	o.tangent			= i.tangent;
	o.binormal			= i.binormal;
	o.normalMatID.xyz   = normalize(cross(o.tangent, o.binormal));

	//-- material ID.
	o.normalMatID.w = i.texCoordsMatID.z;

	//-- world space alpha normal for imposters blending.
	float bbAlphaRef		= dot(g_bbAlphaRefs196[i.alphaIndex], i.alphaMask);
	o.tcLinearZBlendAlpha.w = calculateAlpha(i.alphaNormal, g_cameraDir.xyz, bbAlphaRef);
	
	return o;
}

//--------------------------------------------------------------------------------------------------
G_BUFFER_LAYOUT ps_color_3_0(ColorVS2PS i, uniform bool useAlphaTest)
{
	G_BUFFER_LAYOUT o = (G_BUFFER_LAYOUT)0;
	
	half4 diffuseMap = gamma2linear(tex2D(speedTreeDiffuseSamplerBiased, i.tcLinearZBlendAlpha.xy));

	//-- compile-time branching.
	if (useAlphaTest)
	{
		clip(diffuseMap.w - i.tcLinearZBlendAlpha.w);
	}

	//-- calculate world normal.
	half4   nSample = tex2D(bbNormalSamplerBiased, i.tcLinearZBlendAlpha.xy);
	half3   nn      = nSample.xyz * 2 - 1;
	//-- Note: TBN matrix calculation. In C++ tangent is binormal and visa versa.
	half3x3 TBN		= half3x3(i.binormal, i.tangent, i.normalMatID.xyz);
	half3   normal  = mul(nn.xyz, TBN);

	//-- fill g-buffer.
	g_buffer_writeDepth(o, i.tcLinearZBlendAlpha.z);
	g_buffer_writeAlbedo(o, diffuseMap.xyz);
	g_buffer_writeNormal(o, normal);
	g_buffer_writeSpecAmount(o, nSample.w);
	g_buffer_writeObjectKind(o, G_OBJECT_KIND_SPEEDTREE);
	g_buffer_writeUserData1(o, i.normalMatID.w);

	return o;
}

//--------------------------------------------------------------------------------------------------
struct ShadowsVS2PS
{
	float4 pos			: POSITION;
	float3 tcAlphaRef	: TEXCOORD0;
	float2 clipPos		: TEXCOORD1;
};

//--------------------------------------------------------------------------------------------------
ShadowsVS2PS vs_shadows_3_0(VS_INPUT_BB_OPT i)
{
	ShadowsVS2PS o = (ShadowsVS2PS)0;

	//-- calculate view space position with respect to the wind animation.
	o.pos		    = mul(i.pos, g_viewProjMat);
	o.tcAlphaRef.xy = i.texCoordsMatID.xy * g_UVScale;
	o.clipPos		= o.pos.zw;

	//-- world space alpha normal for imposters blending.
	float bbAlphaRef = dot(g_bbAlphaRefs196[i.alphaIndex], i.alphaMask);
	o.tcAlphaRef.z   = calculateAlpha(i.alphaNormal, g_cameraDir.xyz, bbAlphaRef);
	
	return o;
}

//--------------------------------------------------------------------------------------------------
float4 ps_shadows_3_0(ShadowsVS2PS i) : COLOR0
{
	half alpha = tex2D(speedTreeDiffuseSampler, i.tcAlphaRef.xy).a;

	//-- alpha test.
	clip(alpha - i.tcAlphaRef.z);

	return i.clipPos.x / i.clipPos.y;
}

//--------------------------------------------------------------------------------------------------
struct DepthVS2PS
{
	float4 pos			: POSITION;
	float3 tcAlphaRef	: TEXCOORD0;
};

//--------------------------------------------------------------------------------------------------
DepthVS2PS vs_depth_3_0(VS_INPUT_BB_OPT i)
{
	DepthVS2PS o = (DepthVS2PS)0;

	//-- calculate view space position with respect to the wind animation.
	o.pos		    = mul(i.pos, g_viewProjMat);
	o.tcAlphaRef.xy = i.texCoordsMatID.xy * g_UVScale;

	//-- world space alpha normal for imposters blending.
	float bbAlphaRef = dot(g_bbAlphaRefs196[i.alphaIndex], i.alphaMask);
	o.tcAlphaRef.z   = calculateAlpha(i.alphaNormal, g_cameraDir.xyz, bbAlphaRef);
	
	return o;
}

//--------------------------------------------------------------------------------------------------
float4 ps_depth_3_0(DepthVS2PS i) : COLOR0
{
	half alpha = tex2D(speedTreeDiffuseSampler, i.tcAlphaRef.xy).a;

	//-- alpha test.
	clip(alpha - i.tcAlphaRef.z);

	return float4(0,0,0,0);
}

//--------------------------------------------------------------------------------------------------
struct ReflectionVS2PS
{
	float4 pos			:	POSITION;
	float3 tcAlphaRef	:	TEXCOORD0;
	float4 normalFog	:	TEXCOORD1;
	float4 material0	:	TEXCOORD2;
	float4 material1	:	TEXCOORD3;
};

//--------------------------------------------------------------------------------------------------
ReflectionVS2PS vs_reflection_3_0(const VS_INPUT_BB_OPT i)
{
	ReflectionVS2PS o = (ReflectionVS2PS) 0;

	o.pos				 = mul(i.pos, g_viewProjMat);
	o.tcAlphaRef.xy		 = i.texCoordsMatID.xy * g_UVScale.xy;

	// view angle alpha
	float bbAlphaRef	 = dot(g_bbAlphaRefs196[i.alphaIndex], i.alphaMask);
	o.tcAlphaRef.z		 = calculateAlpha(i.alphaNormal, g_cameraDir.xyz, bbAlphaRef);

	o.material0			 = i.diffuseNAdjust;
	o.material1.xyz		 = i.ambient;
	
	// normal mapping data
	o.normalFog.xyz		 = normalize(cross(i.tangent, i.binormal));
	o.normalFog.w		 = vertexFog(i.pos, o.pos.w);
	
	return o;
};

//--------------------------------------------------------------------------------------------------
float4 ps_reflection_3_0(const ReflectionVS2PS i) : COLOR
{
    half4 diffuseMap = gamma2linear(tex2D(speedTreeDiffuseSamplerBiased, i.tcAlphaRef.xy));

	//-- alpha test.
	clip(diffuseMap.w - i.tcAlphaRef.z);

	//-- lighting equation.
	half3 ambient = (half3)i.material1.rgb * sunAmbientTerm();
	half3 diffuse = (half3)i.material0.rgb * sunDiffuseTerm(normalize(i.normalFog.xyz), i.material0.w);
	half3 color   = diffuseMap.rgb * (ambient + diffuse);

	//-- fog.
	color = applyFogTo(color, i.normalFog.w);

	return float4(color, 1.0f);
}

//--------------------------------------------------------------------------------------------------
PixelShader colorPS[] = {
	compile ps_3_0 ps_color_3_0(true),
	compile ps_3_0 ps_color_3_0(false)
};

//--------------------------------------------------------------------------------------------------
BW_COLOR_TECHNIQUE(false, false)
{
	pass Pass_0
	{
		ZENABLE				= TRUE;
		ZWRITEENABLE		= g_useZPrePass ? 0 : 1;
		ZFUNC				= g_useZPrePass ? BW_CMP_EQUAL : BW_CMP_LESSEQUAL;
		STENCILENABLE		= g_useZPrePass ? 0 : 1;
		ALPHABLENDENABLE	= FALSE;
		ALPHATESTENABLE		= FALSE;
		CULLMODE			= CW;

		VertexShader = compile vs_3_0 vs_color_3_0();
		PixelShader  = colorPS[g_useZPrePass ? 1 : 0];
	}
}

//--------------------------------------------------------------------------------------------------
BW_SHADOW_TECHNIQUE(false)
{
	pass Pass_0
	{
		ZENABLE				= TRUE;
		ZWRITEENABLE		= TRUE;
		ZFUNC				= LESSEQUAL;
		ALPHABLENDENABLE	= FALSE;
		ALPHATESTENABLE		= FALSE;
		CULLMODE			= CW;

		VertexShader = compile vs_3_0 vs_shadows_3_0();
		PixelShader  = compile ps_3_0 ps_shadows_3_0();
	}
}

//--------------------------------------------------------------------------------------------------
BW_REFLECTION_TECHNIQUE(false, false)
{
	pass Pass_0
	{
		ZENABLE				= TRUE;
		ZWRITEENABLE		= TRUE;
		ZFUNC				= LESSEQUAL;
		ALPHABLENDENABLE	= FALSE;
		ALPHATESTENABLE		= FALSE;
		CULLMODE			= CW;

		VertexShader = compile vs_3_0 vs_reflection_3_0();
		PixelShader  = compile ps_3_0 ps_reflection_3_0();
	}
}

//--------------------------------------------------------------------------------------------------
BW_DEPTH_TECHNIQUE(false)
{
	pass Pass_0
	{
		ZENABLE				= TRUE;
		ZWRITEENABLE		= TRUE;
		ZFUNC				= LESSEQUAL;
		ALPHABLENDENABLE	= FALSE;
		ALPHATESTENABLE		= FALSE;
		CULLMODE			= CW;

		VertexShader = compile vs_3_0 vs_depth_3_0();
		PixelShader  = compile ps_3_0 ps_depth_3_0();
	}
}

#else //-- BW_DEFERRED_SHADING

//--------------------------------------------------------------------------------------------------
struct ColorVS2PS
{
	float4 pos			:	POSITION;
	float3 tcAlphaRef	:	TEXCOORD0;
	float3 normal		:	TEXCOORD1;
	float3 tangent		:	TEXCOORD2;
	float3 binormal		:	TEXCOORD3;
	float4 material0	:	TEXCOORD4;
	float4 material1	:	TEXCOORD5;
	float  fog			:	FOG;
};

//--------------------------------------------------------------------------------------------------
ColorVS2PS vs_color_2_0(const VS_INPUT_BB_OPT i)
{
	ColorVS2PS o = (ColorVS2PS) 0;

	o.pos			 = mul(i.pos, g_viewProjMat);
	o.tcAlphaRef.xy	 = i.texCoordsMatID.xy * g_UVScale.xy;

	// view angle alpha
	float bbAlphaRef = dot(g_bbAlphaRefs196[i.alphaIndex], i.alphaMask);
	o.tcAlphaRef.z	 = calculateAlpha(i.alphaNormal, g_cameraDir.xyz, bbAlphaRef);

	o.material0		= i.diffuseNAdjust;
	o.material1.xyz = i.ambient;

	// normal mapping data
	o.binormal = i.binormal;
	o.tangent  = i.tangent;
	o.normal   = normalize(cross(o.tangent, o.binormal));

	//-- fog
	o.fog = bw_vertexFog(float4(i.pos.xyz, 1.0f), o.pos.w);
	
	return o;
}

//--------------------------------------------------------------------------------------------------
float4 ps_color_2_0(const ColorVS2PS i, uniform bool useAlphaTest) : COLOR
{
    half4 diffuseMap = tex2D(speedTreeDiffuseSamplerBiased, i.tcAlphaRef.xy);

	//-- compile-time branching.
	if (useAlphaTest)
	{
		clip(diffuseMap.w - i.tcAlphaRef.z);
	}

	//-- calculate world normal.
	half4   nSample = tex2D(bbNormalSamplerBiased, i.tcAlphaRef.xy);
	half3   nn      = nSample.xyz * 2 - 1;
	//-- Note: TBN matrix calculation. In C++ tangent is binormal and visa versa.
	half3x3 TBN		= half3x3(i.binormal, i.tangent, i.normal);
	half3   normal  = mul(nn.xyz, TBN);

	//-- lighting equation.
	half3 ambient = (half3)i.material1.rgb * sunAmbientTerm();
	half3 diffuse = (half3)i.material0.rgb * sunDiffuseTerm(normalize(normal), i.material0.w);
	half3 color   = diffuseMap.rgb * (ambient + diffuse);

#if SHOW_OVERDRAW
	return float4(0,0,1,0.1f);
#else
	return float4(color, 1.0f);
#endif
}

//--------------------------------------------------------------------------------------------------
struct DepthVS2PS
{
	float4 pos			: POSITION;
	float3 tcAlphaRef	: TEXCOORD0;
};

//--------------------------------------------------------------------------------------------------
DepthVS2PS vs_depth_2_0(VS_INPUT_BB_OPT i)
{
	DepthVS2PS o = (DepthVS2PS)0;

	//-- calculate view space position with respect to the wind animation.
	o.pos		    = mul(i.pos, g_viewProjMat);
	o.tcAlphaRef.xy = i.texCoordsMatID.xy * g_UVScale;

	//-- world space alpha normal for imposters blending.
	float bbAlphaRef = dot(g_bbAlphaRefs196[i.alphaIndex], i.alphaMask);
	o.tcAlphaRef.z   = calculateAlpha(i.alphaNormal, g_cameraDir.xyz, bbAlphaRef);
	
	return o;
}

//--------------------------------------------------------------------------------------------------
float4 ps_depth_2_0(DepthVS2PS i) : COLOR0
{
	half alpha = tex2D(speedTreeDiffuseSampler, i.tcAlphaRef.xy).a;

	//-- alpha test.
	clip(alpha - i.tcAlphaRef.z);

	return float4(0,0,0,0);
}

//--------------------------------------------------------------------------------------------------
PixelShader colorPS[] = {
	compile ps_2_0 ps_color_2_0(true),
	compile ps_2_0 ps_color_2_0(false)
};

//--------------------------------------------------------------------------------------------------
BW_COLOR_TECHNIQUE(false, false)
{
	pass Pass_0
	{
		BW_FOG
		ZENABLE				= TRUE;
		ZWRITEENABLE		= g_useZPrePass ? 0 : 1;
		ZFUNC				= g_useZPrePass ? BW_CMP_EQUAL : BW_CMP_LESSEQUAL;
		STENCILENABLE		= g_useZPrePass ? 0 : 1;
		ALPHATESTENABLE		= FALSE;
		CULLMODE			= CW;

#if SHOW_OVERDRAW
		ALPHABLENDENABLE	= TRUE;
		SRCBLEND			= SRCALPHA;
        DESTBLEND			= INVSRCALPHA;
#else
		ALPHATESTENABLE		= FALSE;
#endif
			
		VertexShader = compile vs_2_0 vs_color_2_0();
		PixelShader  = colorPS[g_useZPrePass ? 1 : 0];
	}
}

//--------------------------------------------------------------------------------------------------
BW_DEPTH_TECHNIQUE(false)
{
	pass Pass_0
	{
		ZENABLE				= TRUE;
		ZWRITEENABLE		= TRUE;
		ZFUNC				= LESSEQUAL;
		ALPHABLENDENABLE	= FALSE;
		ALPHATESTENABLE		= FALSE;
		CULLMODE			= CW;
			
		VertexShader = compile vs_2_0 vs_depth_2_0();
		PixelShader  = compile ps_2_0 ps_depth_2_0();
	}
}

#endif //-- BW_DEFERRED_SHADING
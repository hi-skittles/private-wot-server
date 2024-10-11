#include "speedtree.fxh"

//--------------------------------------------------------------------------------------------------
#if BW_DEFERRED_SHADING

//--------------------------------------------------------------------------------------------------
struct ColorVS2PS
{
	float4 pos			: POSITION;
	float2 linearZMatID	: TEXCOORD0; //-- x - linear Z, y - material ID.
	float4 tcExtra		: TEXCOORD1; //-- xy - uv coords, z - extra data, w - alpha reference.
	float3 tangent		: TEXCOORD2;
	float3 binormal		: TEXCOORD3;
	float3 normal		: TEXCOORD4;
};

//--------------------------------------------------------------------------------------------------
ColorVS2PS vs_color_generic_3_0(in const VS_INPUT_LEAF i, in const SpeedTreeInstance inst, bool highQuality)
{
	ColorVS2PS o = (ColorVS2PS)0;

	//-- calculate view space position with respect to the wind animation.
	float4 outPos = calcLeafVertex2(i, inst, true, highQuality);

	o.pos			 = mul(outPos, g_projMat);
	o.tcExtra		 = float4(i.tcWindInfo.xy, i.extraInfo.z, inst.m_alphaRef);
	o.linearZMatID.x = o.pos.w;
	o.linearZMatID.y = inst.m_materialID;

	//-- calculate TBN basis matrix.
	if (highQuality)
	{
		o.normal   = qrot(i.normal, inst.m_rotationQuat);
		o.tangent  = qrot(i.tangent, inst.m_rotationQuat);
		o.binormal = normalize(cross(o.normal, o.tangent));
	}
	else
	{
		o.normal.xy = qrot(i.normal, inst.m_rotationQuat);
	}
	
	return o;
}

//--------------------------------------------------------------------------------------------------
ColorVS2PS vs_color_3_0(const VS_INPUT_LEAF i, uniform bool highQuality)
{
	return vs_color_generic_3_0(i, g_instance, highQuality);
}

//--------------------------------------------------------------------------------------------------
ColorVS2PS vs_color_instanced_3_0(const VS_INPUT_LEAF i, const SpeedTreeInstancingStream stream, uniform bool highQuality)
{
	return vs_color_generic_3_0(i, unpackInstancingStream(stream), highQuality);
}

//--------------------------------------------------------------------------------------------------
G_BUFFER_LAYOUT ps_color_3_0(ColorVS2PS i, uniform bool highQuality, uniform bool useAlphaTest)
{
	G_BUFFER_LAYOUT o = (G_BUFFER_LAYOUT)0;
	
	//-- read albedo.
	half  leafDimming = i.tcExtra.z;
	half4 diffuseMap  = gamma2linear(tex2D(speedTreeDiffuseSampler, i.tcExtra.xy));
	diffuseMap.xyz    *= leafDimming;

	//-- compile-time branching.
	if (useAlphaTest)
	{
		clip(diffuseMap.a - i.tcExtra.w);
	}

	if (highQuality)
	{
		//-- calculate world space normal.
		half4   nSample = tex2D(speedTreeNormalSampler, i.tcExtra.xy);
		half3	nn      = nSample.xyz * 2 - 1;

		half3x3 TBN     = half3x3(i.tangent, i.binormal, i.normal);
		half3   normal  = mul(nn.xyz, TBN);

		g_buffer_writeNormal(o, normal);

		//-- fade out the specular with distance from the camera.
		nSample.w *= (1 - saturate(i.linearZMatID.x * g_specularFadeoutDist));

		g_buffer_writeSpecAmount(o, nSample.w);
	}
	else
	{
		g_buffer_writeNormal(o, i.normal);
		g_buffer_writeSpecAmount(o, 0);
	}

	//-- fill g-buffer.
	g_buffer_writeAlbedo(o, diffuseMap.xyz);
	g_buffer_writeDepth(o, i.linearZMatID.x);
	g_buffer_writeObjectKind(o, G_OBJECT_KIND_SPEEDTREE);
	g_buffer_writeUserData1(o, i.linearZMatID.y);

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
ShadowsVS2PS vs_shadows_generic_3_0(const VS_INPUT_LEAF i, const SpeedTreeInstance inst, uniform bool highQuality)
{
	ShadowsVS2PS o = (ShadowsVS2PS) 0;

	//-- calculate view space position with respect to the wind animation.
	float4 outPos = calcLeafVertex2(i, inst, true, highQuality);

	o.pos		  = mul(outPos, g_projMat);
	o.tcAlphaRef  = float3(i.tcWindInfo.xy, inst.m_alphaRef);
	o.clipPos	  = o.pos.zw;

	return o;
}

//--------------------------------------------------------------------------------------------------
ShadowsVS2PS vs_shadows_3_0(const VS_INPUT_LEAF i, uniform bool highQuality)
{
	return vs_shadows_generic_3_0(i, g_instance, highQuality);
}

//--------------------------------------------------------------------------------------------------
ShadowsVS2PS vs_shadows_instanced_3_0(const VS_INPUT_LEAF i, const SpeedTreeInstancingStream stream, uniform bool highQuality)
{
	return vs_shadows_generic_3_0(i, unpackInstancingStream(stream), highQuality);
}

//--------------------------------------------------------------------------------------------------
float4 ps_shadows_3_0(ShadowsVS2PS i) : COLOR
{
	half alpha = tex2D(speedTreeDiffuseSampler, i.tcAlphaRef.xy).a;

	//-- alpha test.
	clip(alpha - i.tcAlphaRef.z);

	//-- To prevent self shadowing on leaves.
	const float biasing = 0.001f;

	return (i.clipPos.x / i.clipPos.y) + biasing;
}

//--------------------------------------------------------------------------------------------------
struct DepthVS2PS
{
	float4 pos			:	POSITION;
	float3 tcAlphaRef	:	TEXCOORD0;
};

//--------------------------------------------------------------------------------------------------
DepthVS2PS vs_depth_generic_3_0(const VS_INPUT_LEAF i, const SpeedTreeInstance inst, uniform bool highQuality)
{
	DepthVS2PS o = (DepthVS2PS) 0;

	//-- calculate view space position with respect to the wind animation.
	float4 outPos = calcLeafVertex2(i, inst, true, highQuality);

	o.pos		  = mul(outPos, g_projMat);
	o.tcAlphaRef  = float3(i.tcWindInfo.xy, inst.m_alphaRef);

	return o;
}

//--------------------------------------------------------------------------------------------------
DepthVS2PS vs_depth_3_0(const VS_INPUT_LEAF i, uniform bool highQuality)
{
	return vs_depth_generic_3_0(i, g_instance, highQuality);
}

//--------------------------------------------------------------------------------------------------
DepthVS2PS vs_depth_instanced_3_0(const VS_INPUT_LEAF i, const SpeedTreeInstancingStream stream, uniform bool highQuality)
{
	return vs_depth_generic_3_0(i, unpackInstancingStream(stream), highQuality);
}

//--------------------------------------------------------------------------------------------------
float4 ps_depth_3_0(DepthVS2PS i) : COLOR
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
	float4 tcExtra		:	TEXCOORD0;
	float4 normalFog	:	TEXCOORD1;
};

//--------------------------------------------------------------------------------------------------
ReflectionVS2PS vs_reflection_generic_3_0(const VS_INPUT_LEAF i, const SpeedTreeInstance inst, uniform bool highQuality)
{
	ReflectionVS2PS o = (ReflectionVS2PS)0;

	float4 outPos	= calcLeafVertex2(i, inst, true, highQuality);
	o.pos			= mul(outPos, g_projMat);
	o.tcExtra		= float4(i.tcWindInfo.xy, i.extraInfo.z, inst.m_alphaRef);
	o.normalFog.xyz = qrot(i.normal, inst.m_rotationQuat);
	o.normalFog.w	= bw_vertexFog(mul(outPos, g_invViewMat), o.pos.w);
	
	return o;
}

//--------------------------------------------------------------------------------------------------
ReflectionVS2PS vs_reflection_3_0(const VS_INPUT_LEAF i, uniform bool highQuality)
{
	return vs_reflection_generic_3_0(i, g_instance, highQuality);
}

//--------------------------------------------------------------------------------------------------
ReflectionVS2PS vs_reflection_instanced_3_0(const VS_INPUT_LEAF i, const SpeedTreeInstancingStream stream, uniform bool highQuality)
{
	return vs_reflection_generic_3_0(i, unpackInstancingStream(stream), highQuality);
}

//--------------------------------------------------------------------------------------------------
float4 ps_reflection_3_0(const ReflectionVS2PS i) : COLOR
{
	half4 diffuseMap = gamma2linear(tex2D(speedTreeDiffuseSampler, i.tcExtra.xy));

	//-- alpha test.
	clip(diffuseMap.a - i.tcExtra.w);

	//-- apply leaf dimming
	diffuseMap.xyz *= i.tcExtra.z;

	//-- lighting equation.
	half3 ambient = (half3)g_material[1].rgb * sunAmbientTerm();
	half3 diffuse = (half3)g_material[0].rgb * sunDiffuseTerm(normalize(i.normalFog.xyz), g_leafLightAdj);
	half3 color   = diffuseMap.rgb * (ambient + diffuse);

	//-- fog.
	color = applyFogTo(color, i.normalFog.w);

	return float4(color, 1.0f);
}

//--------------------------------------------------------------------------------------------------
PixelShader colorPS[] = {
	compile ps_3_0 ps_color_3_0(true,  true ),
	compile ps_3_0 ps_color_3_0(false, true ),
	compile ps_3_0 ps_color_3_0(true,  false),
	compile ps_3_0 ps_color_3_0(false, false)
};

//--------------------------------------------------------------------------------------------------
#undef	COMPILE_VS 
#define COMPILE_VS(pass)						\
	VertexShader pass##VS[] =					\
	{											\
		compile vs_3_0 vs_##pass##_3_0(true),	\
		compile vs_3_0 vs_##pass##_3_0(false)	\
	};

COMPILE_VS(color);
COMPILE_VS(color_instanced);
COMPILE_VS(reflection);
COMPILE_VS(reflection_instanced);
COMPILE_VS(shadows);
COMPILE_VS(shadows_instanced);
COMPILE_VS(depth);
COMPILE_VS(depth_instanced);

#undef COMPILE_VS

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
		CULLMODE			= NONE;

		VertexShader = colorVS[g_useHighQuality ? 0 : 1];
		PixelShader  = colorPS[(g_useHighQuality ? 0 : 1) + (g_useZPrePass ? 2 : 0)];
	}
}

//--------------------------------------------------------------------------------------------------
BW_COLOR_INSTANCED_TECHNIQUE(false, false)
{
	pass Pass_0
	{
		ZENABLE				= TRUE;
		ZWRITEENABLE		= g_useZPrePass ? 0 : 1;
		ZFUNC				= g_useZPrePass ? BW_CMP_EQUAL : BW_CMP_LESSEQUAL;
		STENCILENABLE		= g_useZPrePass ? 0 : 1;
		ALPHABLENDENABLE	= FALSE;
		ALPHATESTENABLE		= FALSE;
		CULLMODE			= NONE;

		VertexShader = color_instancedVS[g_useHighQuality ? 0 : 1];
		PixelShader  = colorPS[(g_useHighQuality ? 0 : 1) + (g_useZPrePass ? 2 : 0)];
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
		CULLMODE			= NONE;

		VertexShader = shadowsVS[g_useHighQuality ? 0 : 1];
		PixelShader  = compile ps_3_0 ps_shadows_3_0();
	}
}

//--------------------------------------------------------------------------------------------------
BW_SHADOW_INSTANCED_TECHNIQUE(false)
{
	pass Pass_0
	{
		ZENABLE				= TRUE;
		ZWRITEENABLE		= TRUE;
		ZFUNC				= LESSEQUAL;
		ALPHABLENDENABLE	= FALSE;
		ALPHATESTENABLE		= FALSE;
		CULLMODE			= NONE;

		VertexShader = shadows_instancedVS[g_useHighQuality ? 0 : 1];
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
		CULLMODE			= NONE;

		VertexShader = reflectionVS[g_useHighQuality ? 0 : 1];
		PixelShader  = compile ps_3_0 ps_reflection_3_0();
	}
}

//--------------------------------------------------------------------------------------------------
BW_REFLECTION_INSTANCED_TECHNIQUE(false, false)
{
	pass Pass_0
	{
		ZENABLE				= TRUE;
		ZWRITEENABLE		= TRUE;
		ZFUNC				= LESSEQUAL;
		ALPHABLENDENABLE	= FALSE;
		ALPHATESTENABLE		= FALSE;
		CULLMODE			= NONE;

		VertexShader = reflection_instancedVS[g_useHighQuality ? 0 : 1];
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
		CULLMODE			= NONE;

		VertexShader = depthVS[g_useHighQuality ? 0 : 1];
		PixelShader  = compile ps_3_0 ps_depth_3_0();
	}
}

//--------------------------------------------------------------------------------------------------
BW_DEPTH_INSTANCED_TECHNIQUE(false)
{
	pass Pass_0
	{
		ZENABLE				= TRUE;
		ZWRITEENABLE		= TRUE;
		ZFUNC				= LESSEQUAL;
		ALPHABLENDENABLE	= FALSE;
		ALPHATESTENABLE		= FALSE;
		CULLMODE			= NONE;

		VertexShader = shadows_instancedVS[g_useHighQuality ? 0 : 1];
		PixelShader  = compile ps_3_0 ps_depth_3_0();
	}
}

#else //-- BW_DEFERRED_SHADING

//--------------------------------------------------------------------------------------------------
struct ColorVS2PS
{
	float4 pos		:	POSITION;
	float4 tcExtra	:	TEXCOORD0;
	float3 normal	:	TEXCOORD1;
	float fog		:	FOG;
};

//--------------------------------------------------------------------------------------------------
ColorVS2PS vs_color_2_0(const VS_INPUT_LEAF i)
{
	ColorVS2PS o = (ColorVS2PS)0;
	
	float4 outPos = calcLeafVertex2(i, g_instance, false, false);
	o.pos		  = mul(outPos, g_projMat);
	o.tcExtra     = float4(i.tcWindInfo.xy, i.extraInfo.z, g_instance.m_alphaRef);
	o.normal	  = qrot(i.normal, g_instance.m_rotationQuat);

	//-- fog
	float4 wPos = mul(o.pos, g_invViewProjMat);
	o.fog = bw_vertexFog(wPos, o.pos.w);
	
	return o;
}

//--------------------------------------------------------------------------------------------------
float4 ps_color_2_0(const ColorVS2PS i, uniform bool useAlphaTest) : COLOR
{
	//-- read albedo.
	half4 diffuseMap = tex2D(speedTreeDiffuseSampler, i.tcExtra.xy);

	//-- compile-time branching.
	if (useAlphaTest)
	{
		clip(diffuseMap.a - i.tcExtra.w);
	}

	//-- apply leaf dimming
	diffuseMap.xyz *= i.tcExtra.z;

	//-- lighting equation.
	half3 ambient = (half3)g_material[1].rgb * sunAmbientTerm();
	half3 diffuse = (half3)g_material[0].rgb * sunDiffuseTerm(normalize(i.normal), g_leafLightAdj);
	half3 color   = diffuseMap.rgb * (ambient + diffuse);

#if SHOW_OVERDRAW
	return float4(1,0,0,0.1f);
#else
	return float4(color, 1.0f);
#endif
}

//--------------------------------------------------------------------------------------------------
struct DepthVS2PS
{
	float4 pos			:	POSITION;
	float3 tcAlphaRef	:	TEXCOORD0;
};

//--------------------------------------------------------------------------------------------------
DepthVS2PS vs_depth_2_0(const VS_INPUT_LEAF i)
{
	DepthVS2PS o = (DepthVS2PS) 0;

	//-- calculate view space position with respect to the wind animation.
	float4 outPos = calcLeafVertex2(i, g_instance, false, false);

	o.pos		  = mul(outPos, g_projMat);
	o.tcAlphaRef  = float3(i.tcWindInfo.xy, g_instance.m_alphaRef);

	return o;
}

//--------------------------------------------------------------------------------------------------
float4 ps_depth_2_0(DepthVS2PS i) : COLOR
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
		CULLMODE			= NONE;

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
		CULLMODE			= NONE;

		VertexShader = compile vs_2_0 vs_depth_2_0();
		PixelShader  = compile ps_2_0 ps_depth_2_0();
	}
}

#endif //-- BW_DEFERRED_SHADING

#include "speedtree.fxh"

//--------------------------------------------------------------------------------------------------
#if BW_DEFERRED_SHADING

//--------------------------------------------------------------------------------------------------
struct ColorVS2PS
{
	float4 pos			: POSITION;
	float2 linearZMatID	: TEXCOORD0;
	float3 tcAlphaRef	: TEXCOORD1;
	float3 tangent		: TEXCOORD2;
	float3 binormal		: TEXCOORD3;
	float3 normal		: TEXCOORD4;
};

//--------------------------------------------------------------------------------------------------
ColorVS2PS vs_color_generic_3_0(const VS_INPUT_BB i, const SpeedTreeInstance inst)
{
	ColorVS2PS o = (ColorVS2PS)0;

	//-- calculate view space position with respect to the wind animation.
	float3 wPos	 = i.pos;
	wPos.xyz	*= inst.m_scale;
	wPos		 = qrot(wPos, inst.m_rotationQuat);
	wPos.xyz	+= inst.m_translation;

	o.pos	         = mul(float4(wPos, 1.0f), g_viewProjMat);
	o.linearZMatID.x = o.pos.w;
	o.linearZMatID.y = inst.m_materialID;
	o.tcAlphaRef.xy	 = i.tc.xy;

	//-- calculate TBN basis matrix.
	o.binormal = qrot(i.binormal, inst.m_rotationQuat);
	o.tangent  = qrot(i.tangent, inst.m_rotationQuat);
	o.normal   = normalize(cross(o.tangent, o.binormal));

	//-- world space alpha normal for imposters blending.
	float3 wAlphaNormal = qrot(i.alphaNormal, inst.m_rotationQuat);
	o.tcAlphaRef.z = calculateAlpha(wAlphaNormal, g_cameraDir, inst.m_alphaRef);
	
	return o;
}

//--------------------------------------------------------------------------------------------------
ColorVS2PS vs_color_3_0(const VS_INPUT_BB i)
{
	return vs_color_generic_3_0(i, g_instance);
}

//--------------------------------------------------------------------------------------------------
ColorVS2PS vs_color_instanced_3_0(const VS_INPUT_BB i, const SpeedTreeInstancingStream stream)
{
	return vs_color_generic_3_0(i, unpackInstancingStream(stream));
}

//--------------------------------------------------------------------------------------------------
G_BUFFER_LAYOUT ps_color_3_0(ColorVS2PS i, uniform bool useAlphaTest)
{
	G_BUFFER_LAYOUT o = (G_BUFFER_LAYOUT)0;
	
    half4 diffuseMap = gamma2linear(tex2D(speedTreeDiffuseSampler, i.tcAlphaRef.xy));

	//-- compile-time branching.
	if (useAlphaTest)
	{
		clip(diffuseMap.w - i.tcAlphaRef.z);
	}

	//-- calculate world normal.
	half4   nSample = tex2D(bbNormalSampler, i.tcAlphaRef.xy);
	half3   nn      = nSample.xyz * 2 - 1;
	//-- Note: TBN matrix calculation. In C++ tangent is binormal and visa versa.
	half3x3 TBN	    = half3x3(i.binormal, i.tangent, i.normal);
	half3   normal  = mul(nn.xyz, TBN);

	//-- fade out the specular with distance from the camera.
	nSample.w *= (1 - saturate(i.linearZMatID.x * g_specularFadeoutDist));

	//-- fill g-buffer.
	g_buffer_writeAlbedo(o, diffuseMap.xyz);
	g_buffer_writeDepth(o, i.linearZMatID.x);
	g_buffer_writeNormal(o, normal);
	g_buffer_writeSpecAmount(o, nSample.w);
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
ShadowsVS2PS vs_shadows_generic_3_0(const VS_INPUT_BB i, const SpeedTreeInstance inst)
{
	ShadowsVS2PS o = (ShadowsVS2PS)0;

	//-- calculate view space position with respect to the wind animation.
	float3 wPos	 = i.pos;
	wPos		*= inst.m_scale;
	wPos		 = qrot(wPos, inst.m_rotationQuat);
	wPos		+= inst.m_translation;

	//-- world space alpha normal for imposters blending.
	float3 wAlphaNormal = qrot(i.alphaNormal, inst.m_rotationQuat);
	float alphaRef = calculateAlpha(wAlphaNormal, g_cameraDir, inst.m_alphaRef);

	o.pos		 = mul(float4(wPos, 1.0f), g_viewProjMat);
	o.tcAlphaRef = float3(i.tc, alphaRef);
	o.clipPos	 = o.pos.zw;

	return o;
}

//--------------------------------------------------------------------------------------------------
ShadowsVS2PS vs_shadows_3_0(const VS_INPUT_BB i)
{
	return vs_shadows_generic_3_0(i, g_instance);
}

//--------------------------------------------------------------------------------------------------
ShadowsVS2PS vs_shadows_instanced_3_0(const VS_INPUT_BB i, const SpeedTreeInstancingStream stream)
{
	return vs_shadows_generic_3_0(i, unpackInstancingStream(stream));
}

//--------------------------------------------------------------------------------------------------
float4 ps_shadows_3_0(ShadowsVS2PS i) : COLOR0
{
	half alpha = tex2D(speedTreeDiffuseSampler, i.tcAlphaRef.xy).a;

	//-- alpha test.
	clip(alpha - i.tcAlphaRef.z);

	//-- To prevent self shadowing on billboards.
	const float biasing = 0.0001f;

	return i.clipPos.x / i.clipPos.y + biasing;
}

//--------------------------------------------------------------------------------------------------
struct DepthVS2PS
{
	float4 pos			: POSITION;
	float3 tcAlphaRef	: TEXCOORD0;
};

//--------------------------------------------------------------------------------------------------
DepthVS2PS vs_depth_generic_3_0(const VS_INPUT_BB i, const SpeedTreeInstance inst)
{
	DepthVS2PS o = (DepthVS2PS)0;

	//-- calculate view space position with respect to the wind animation.
	float3 wPos	 = i.pos;
	wPos		*= inst.m_scale;
	wPos		 = qrot(wPos, inst.m_rotationQuat);
	wPos		+= inst.m_translation;

	//-- world space alpha normal for imposters blending.
	float3 wAlphaNormal = qrot(i.alphaNormal, inst.m_rotationQuat);
	float alphaRef = calculateAlpha(wAlphaNormal, g_cameraDir, inst.m_alphaRef);

	o.pos		 = mul(float4(wPos, 1.0f), g_viewProjMat);
	o.tcAlphaRef = float3(i.tc, alphaRef);

	return o;
}

//--------------------------------------------------------------------------------------------------
DepthVS2PS vs_depth_3_0(const VS_INPUT_BB i)
{
	return vs_depth_generic_3_0(i, g_instance);
}

//--------------------------------------------------------------------------------------------------
DepthVS2PS vs_depth_instanced_3_0(const VS_INPUT_BB i, const SpeedTreeInstancingStream stream)
{
	return vs_depth_generic_3_0(i, unpackInstancingStream(stream));
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
};

//--------------------------------------------------------------------------------------------------
ReflectionVS2PS vs_reflection_generic_3_0(const VS_INPUT_BB i, const SpeedTreeInstance inst)
{
	ReflectionVS2PS o = (ReflectionVS2PS) 0;

	float3 wPos	 = i.pos;
	wPos.xyz	*= inst.m_scale;
	wPos.xyz	 = qrot(wPos, inst.m_rotationQuat);
	wPos.xyz	+= inst.m_translation;

	//-- world space alpha normal for imposters blending.
	float3 wAlphaNormal = qrot(i.alphaNormal, inst.m_rotationQuat);
	float  alphaRef = calculateAlpha(wAlphaNormal, g_cameraDir, inst.m_alphaRef);

	o.pos		 = mul(float4(wPos, 1.0f), g_viewProjMat);
	o.tcAlphaRef = float3(i.tc, alphaRef);

	//-- calculate world space normal.
	float3 normal   = normalize(cross(i.tangent, i.binormal));
	o.normalFog.xyz	= qrot(normal, inst.m_rotationQuat);

	//-- fog
	o.normalFog.w	= vertexFog(float4(wPos, 1), o.pos.w);
		
	return o;
}

//--------------------------------------------------------------------------------------------------
ReflectionVS2PS vs_reflection_3_0(const VS_INPUT_BB i)
{
	return vs_reflection_generic_3_0(i, g_instance);
}

//--------------------------------------------------------------------------------------------------
ReflectionVS2PS vs_reflection_instanced_3_0(const VS_INPUT_BB i, const SpeedTreeInstancingStream stream)
{
	return vs_reflection_generic_3_0(i, unpackInstancingStream(stream));
}

//--------------------------------------------------------------------------------------------------
float4 ps_reflection_3_0(const ReflectionVS2PS i) : COLOR
{
    half4 diffuseMap = gamma2linear(tex2D(speedTreeDiffuseSampler, i.tcAlphaRef.xy));

	//-- alpha test.
	clip(diffuseMap.a - i.tcAlphaRef.z);

	//-- lighting equation.
	half3 ambient = (half3)g_material[1].rgb * sunAmbientTerm();
	half3 diffuse = (half3)g_material[0].rgb * sunDiffuseTerm(normalize(i.normalFog.xyz), g_leafLightAdj);
	half3 color   = diffuseMap.rgb * (ambient + diffuse);

	//-- fog.
	color = applyFogTo(color, i.normalFog.w);

	return float4(color, 1.0f);
};

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
		CULLMODE			= CW;

		VertexShader = compile vs_3_0 vs_color_instanced_3_0();
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
BW_SHADOW_INSTANCED_TECHNIQUE(false)
{
	pass Pass_0
	{
		ZENABLE				= TRUE;
		ZWRITEENABLE		= TRUE;
		ZFUNC				= LESSEQUAL;
		ALPHABLENDENABLE	= FALSE;
		ALPHATESTENABLE		= FALSE;
		CULLMODE			= CW;

		VertexShader = compile vs_3_0 vs_shadows_instanced_3_0();
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
BW_REFLECTION_INSTANCED_TECHNIQUE(false, false)
{
	pass Pass_0
	{
		ZENABLE				= TRUE;
		ZWRITEENABLE		= TRUE;
		ZFUNC				= LESSEQUAL;
		ALPHABLENDENABLE	= FALSE;
		ALPHATESTENABLE		= FALSE;
		CULLMODE			= CW;

		VertexShader = compile vs_3_0 vs_reflection_instanced_3_0();
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
		CULLMODE			= CW;

		VertexShader = compile vs_3_0 vs_depth_instanced_3_0();
		PixelShader  = compile ps_3_0 ps_depth_3_0();
	}
}

#else //-- BW_DEFERRED_SHADING

//--------------------------------------------------------------------------------------------------
struct ColorVS2PS
{
	float4 pos			: POSITION;
	float3 tcAlphaRef	: TEXCOORD0;
	float3 normal		: TEXCOORD1;
	float3 tangent		: TEXCOORD2;
	float3 binormal		: TEXCOORD3;
	float  fog			: FOG;
};

//--------------------------------------------------------------------------------------------------
ColorVS2PS vs_color_2_0(const VS_INPUT_BB i)
{
	ColorVS2PS o = (ColorVS2PS) 0;

	float3 wPos	 = i.pos.xyz;
	wPos		*= g_instance.m_scale;
	wPos		 = qrot(wPos, g_instance.m_rotationQuat);
	wPos		+= g_instance.m_translation;

	//-- world space alpha normal for imposters blending.
	float3 wAlphaNormal = qrot(i.alphaNormal, g_instance.m_rotationQuat);
	float  alphaRef = calculateAlpha(wAlphaNormal, g_cameraDir, g_instance.m_alphaRef);

	o.pos		 = mul(float4(wPos, 1.0f), g_viewProjMat);
	o.tcAlphaRef = float3(i.tc, alphaRef);

	//-- calculate TBN basis matrix.
	o.binormal = qrot(i.binormal, g_instance.m_rotationQuat);
	o.tangent  = qrot(i.tangent, g_instance.m_rotationQuat);
	o.normal   = normalize(cross(o.tangent, o.binormal));

	//--fog.
	o.fog = bw_vertexFog(float4(wPos, 1.0f), o.pos.w);
		
	return o;
}

//--------------------------------------------------------------------------------------------------
float4 ps_color_2_0(const ColorVS2PS i, uniform bool useAlphaTest) : COLOR
{
    half4 diffuseMap = tex2D(speedTreeDiffuseSampler, i.tcAlphaRef.xy);

	//-- compile-time branching.
	if (useAlphaTest)
	{
		clip(diffuseMap.a - i.tcAlphaRef.z);
	}

	//-- calculate world normal.
	half4   nSample = tex2D(bbNormalSampler, i.tcAlphaRef.xy);
	half3   nn      = nSample.xyz * 2 - 1;
	//-- Note: TBN matrix calculation. In C++ tangent is binormal and visa versa.
	half3x3 TBN		= half3x3(i.binormal, i.tangent, i.normal.xyz);
	half3   normal  = mul(nn.xyz, TBN);

	//-- lighting equation.
	half3 ambient = (half3)g_material[1].rgb * sunAmbientTerm();
	half3 diffuse = (half3)g_material[0].rgb * sunDiffuseTerm(normalize(normal), g_leafLightAdj);
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
DepthVS2PS vs_depth_2_0(const VS_INPUT_BB i)
{
	DepthVS2PS o = (DepthVS2PS)0;

	//-- calculate view space position with respect to the wind animation.
	float3 wPos	 = i.pos;
	wPos		*= g_instance.m_scale;
	wPos		 = qrot(wPos, g_instance.m_rotationQuat);
	wPos		+= g_instance.m_translation;

	//-- world space alpha normal for imposters blending.
	float3 wAlphaNormal = qrot(i.alphaNormal, g_instance.m_rotationQuat);
	float alphaRef = calculateAlpha(wAlphaNormal, g_cameraDir, g_instance.m_alphaRef);

	o.pos		 = mul(float4(wPos, 1.0f), g_viewProjMat);
	o.tcAlphaRef = float3(i.tc, alphaRef);

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
		ALPHABLENDENABLE	= FALSE;
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
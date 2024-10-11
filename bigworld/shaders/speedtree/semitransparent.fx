#include "speedtree.fxh"

//--------------------------------------------------------------------------------------------------
struct ZPassOutput
{
	float4 pos			: POSITION;
	float3 tcAlphaRef	: TEXCOORD0;
};

//--------------------------------------------------------------------------------------------------
ZPassOutput vs_branch_z_pass(const VS_INPUT_BRANCHES i, uniform bool useWindEffect = true)
{
	ZPassOutput o = (ZPassOutput)0;
	
	o.pos		 = branchesOutputPosition(i, g_instance, useWindEffect);
	o.tcAlphaRef = float3(i.tcWindInfo.xy, g_instance.m_alphaRef);

	return o;
}

//--------------------------------------------------------------------------------------------------
float4 ps_branch_z_pass(const ZPassOutput i) : COLOR0
{
	//-- read alpha.
	half alpha = tex2D(speedTreeDiffuseSampler, i.tcAlphaRef.xy).a;

	//-- alpha test.
	clip(alpha - i.tcAlphaRef.z);

	return float4(0,0,0,0);
}

//--------------------------------------------------------------------------------------------------
ZPassOutput vs_leaf_z_pass(const VS_INPUT_LEAF i, uniform bool useWindEffect = true, uniform bool highQuality = true)
{
	ZPassOutput o = (ZPassOutput)0;
	
	float4 outPos = calcLeafVertex2(i, g_instance, useWindEffect, highQuality);
	o.pos		  = mul(outPos, g_projMat);
	o.tcAlphaRef  = float3(i.tcWindInfo.xy, g_instance.m_alphaRef);

	return o;
}

//--------------------------------------------------------------------------------------------------
float4 ps_leaf_z_pass(const ZPassOutput i) : COLOR0
{
	//-- read alpha.
	half alpha = tex2D(speedTreeDiffuseSampler, i.tcAlphaRef.xy).a;

	//-- alpha test.
	clip(alpha - i.tcAlphaRef.z);

	return float4(0,0,0,0);
}

//--------------------------------------------------------------------------------------------------
ZPassOutput vs_billboard_z_pass(const VS_INPUT_BB i)
{
	ZPassOutput o = (ZPassOutput)0;

	float3 wPos	 = i.pos;
	wPos		*= g_instance.m_scale;
	wPos		 = qrot(wPos, g_instance.m_rotationQuat);
	wPos		+= g_instance.m_translation;

	//-- world space alpha normal for imposters blending.
	float3 wAlphaNormal = qrot(i.alphaNormal, g_instance.m_rotationQuat);
	float  alphaRef = calculateAlpha(wAlphaNormal, g_cameraDir, g_instance.m_alphaRef);

	o.pos		 = mul(float4(wPos, 1.0f), g_viewProjMat);
	o.tcAlphaRef = float3(i.tc, alphaRef);

	return o;
}

//--------------------------------------------------------------------------------------------------
float4 ps_billboard_z_pass(const ZPassOutput i) : COLOR0
{
	//-- read alpha.
	half alpha = tex2D(speedTreeDiffuseSampler, i.tcAlphaRef.xy).a;

	//-- alpha test.
	clip(alpha - i.tcAlphaRef.z);

	return float4(0,0,0,0);
}

//--------------------------------------------------------------------------------------------------
#if BW_DEFERRED_SHADING

#include "read_g_buffer.fxh"

//--------------------------------------------------------------------------------------------------
bool g_useAlpha = false;

//--------------------------------------------------------------------------------------------------
struct VS_INPUT
{
	float4 pos : POSITION;
	float2 tc  : TEXCOORD;
};

//--------------------------------------------------------------------------------------------------
struct VS_OUTPUT
{
	float4 pos : POSITION;
	float2 tc  : TEXCOORD0;
};

//--------------------------------------------------------------------------------------------------
VS_OUTPUT vs_fs_quad( VS_INPUT i )
{
	VS_OUTPUT o = (VS_OUTPUT)0;
	o.pos = i.pos;
	o.tc  = i.tc;
	return o;
}

//--------------------------------------------------------------------------------------------------
float4 ps_down_sample_depth(VS_OUTPUT i) : COLOR
{
	float depth = 0.0f;
	depth += g_buffer_readLinearZ(i.tc + float2(+g_invScreen.z, +g_invScreen.w));
	depth += g_buffer_readLinearZ(i.tc + float2(+g_invScreen.z, -g_invScreen.w));
	depth += g_buffer_readLinearZ(i.tc + float2(-g_invScreen.z, +g_invScreen.w));
	depth += g_buffer_readLinearZ(i.tc + float2(-g_invScreen.z, -g_invScreen.w));
	return depth / 4;
}

//--------------------------------------------------------------------------------------------------
texture g_srcMap;
sampler g_srcMapSampler = sampler_state
{		
	Texture = <g_srcMap>;
	MIPFILTER = LINEAR;
	MAGFILTER = LINEAR;
	MINFILTER = LINEAR;
	ADDRESSU  = WRAP;
	ADDRESSV  = WRAP;
};

//--------------------------------------------------------------------------------------------------
float4 ps_up_sample_rt(VS_OUTPUT i) : COLOR
{
#if 0
	half4 color = half4(0,0,0,0);

	color += tex2D(g_srcMapSampler, i.tc.xy + float2(+g_invScreen.z, +g_invScreen.w) * float2(0.25f, 0.25f));
	color += tex2D(g_srcMapSampler, i.tc.xy + float2(+g_invScreen.z, -g_invScreen.w) * float2(0.25f, 0.25f));
	color += tex2D(g_srcMapSampler, i.tc.xy + float2(-g_invScreen.z, +g_invScreen.w) * float2(0.25f, 0.25f));
	color += tex2D(g_srcMapSampler, i.tc.xy + float2(-g_invScreen.z, -g_invScreen.w) * float2(0.25f, 0.25f));

	return color / 4;
#else
	return tex2D(g_srcMapSampler, i.tc.xy);
#endif
}

//--------------------------------------------------------------------------------------------------
technique DOWN_SAMPLE_DEPTH
{	
	pass Pass_0
	{
		ZENABLE = FALSE;
		ZWRITEENABLE = FALSE;
		COLORWRITEENABLE = 0xFF;
		ZFUNC = ALWAYS;
		ALPHATESTENABLE = FALSE;
		ALPHABLENDENABLE = FALSE;
		STENCILENABLE = FALSE;
		CULLMODE = CW;

		VertexShader = compile vs_3_0 vs_fs_quad();
		PixelShader  = compile ps_3_0 ps_down_sample_depth();
	}
}

//--------------------------------------------------------------------------------------------------
technique UPSAMPLE_RT
{	
	pass Pass_0
	{
		ZENABLE = FALSE;
		ZWRITEENABLE = FALSE;
		COLORWRITEENABLE = 0x07;
		ZFUNC = ALWAYS;
		ALPHATESTENABLE = FALSE;
		STENCILENABLE = FALSE;
		CULLMODE = CW;
		ALPHABLENDENABLE = TRUE;
		BLENDOP = ADD;
		SRCBLEND = ONE;
		DESTBLEND = INVSRCALPHA;

		VertexShader = compile vs_3_0 vs_fs_quad();
		PixelShader  = compile ps_3_0 ps_up_sample_rt();
	}
}

//--------------------------------------------------------------------------------------------------
struct LeafVS2PS
{
	float4 pos			: POSITION;
	float2 linearZMatID	: TEXCOORD0; //-- x - linear Z, y - material ID.
	float4 tcExtra		: TEXCOORD1; //-- xy - uv coords, z - extra data, w - alpha reference.
	float3 tangent		: TEXCOORD2;
	float3 binormal		: TEXCOORD3;
	float3 normal		: TEXCOORD4;
	float3 wPos			: TEXCOORD5;
};

//--------------------------------------------------------------------------------------------------
LeafVS2PS vs_leaf_3_0(in const VS_INPUT_LEAF i, uniform bool highQuality)
{
	LeafVS2PS o = (LeafVS2PS)0;

	//-- calculate view space position with respect to the wind animation.
	float4 outPos = calcLeafVertex2(i, g_instance, true, highQuality);

	o.pos			 = mul(outPos, g_projMat);
	o.tcExtra		 = float4(i.tcWindInfo.xy, i.extraInfo.z, g_instance.m_alphaRef);
	o.linearZMatID.x = o.pos.w;
	o.linearZMatID.y = g_instance.m_materialID;

	if (highQuality)
	{
		//-- calculate TBN basis matrix.
		o.normal	= qrot(i.normal, g_instance.m_rotationQuat);
		o.tangent	= qrot(i.tangent, g_instance.m_rotationQuat);
		o.binormal	= normalize(cross(o.normal, o.tangent));

		//-- calculate world pos.
		o.wPos		= mul(outPos, g_invViewMat);
	}
	else
	{
		o.normal = qrot(i.normal, g_instance.m_rotationQuat);
	}
	
	return o;
}

//--------------------------------------------------------------------------------------------------
float4 ps_leaf_3_0(LeafVS2PS i, uniform bool highQuality) : COLOR0
{
	//-- read albedo.
	half  leafDimming = i.tcExtra.z;
	half4 diffuseMap  = gamma2linear(tex2D(speedTreeDiffuseSampler, i.tcExtra.xy));
	diffuseMap.xyz    *= leafDimming;

	//--
	half3 wNormal = normalize(i.normal);
	half3 spec    = 0;

	if (highQuality)
	{
		//-- calculate world space normal.
		half4   nSample = tex2D(speedTreeNormalSampler, i.tcExtra.xy);
		half3   nn      = nSample.xyz * 2 - 1;
		half3x3 TBN     = half3x3(i.tangent, i.binormal, i.normal);

		wNormal	= normalize(mul(nn, TBN));
		spec	= g_specularParams.x * nSample.w * sunSpecTerm(wNormal, normalize(g_cameraPos.xyz - i.wPos), g_specularParams.y);
	}

	//-- lighting equation.
	half3 ambient = g_material[1].xyz * sunAmbientTerm().xyz;
	half3 diffuse = g_material[0].xyz * sunDiffuseTerm(wNormal).xyz;

	//--
	half3 color = diffuseMap.xyz * (ambient + diffuse) + spec;
	half  alpha = diffuseMap.a * max(g_instance.m_blendFactor, g_useAlpha * 0.5f);

	return float4(color, alpha);
}

//--------------------------------------------------------------------------------------------------
struct BranchVS2PS
{
	float4 pos			: POSITION;
	float2 linearZMatID	: TEXCOORD0; //-- x - linear Z, y - material ID.
	float3 tcAlphaRef	: TEXCOORD1; //-- xy - texture coordinates, z - alpha reference.
	float3 normal		: TEXCOORD2;
	float3 tangent		: TEXCOORD3;
	float3 binormal		: TEXCOORD4;
	float3 wPos			: TEXCOORD5;
};

//--------------------------------------------------------------------------------------------------
BranchVS2PS vs_branch_3_0(const VS_INPUT_BRANCHES i, uniform bool highQuality)
{
	BranchVS2PS o = (BranchVS2PS)0;

	//-- calculate clip space position with respect to the wind animation.
	o.pos			 = branchesOutputPosition(i, g_instance);
	o.tcAlphaRef	 = float3(i.tcWindInfo.xy, g_instance.m_alphaRef);
	o.linearZMatID.x = o.pos.w;
	o.linearZMatID.y = g_instance.m_materialID;

	if (highQuality)
	{
		//-- calculate TBN basis matrix.
		o.normal   = qrot(i.normal, g_instance.m_rotationQuat);
		o.tangent  = qrot(i.tangent, g_instance.m_rotationQuat);
		o.binormal = normalize(cross(o.normal, o.tangent));

		//-- calculate world pos.
		float4 wPos	= mul(o.pos, g_invViewProjMat);
		o.wPos = wPos.xyz / wPos.w;
	}
	else
	{
		o.normal = qrot(i.normal, g_instance.m_rotationQuat);
	}

	return o;
}

//--------------------------------------------------------------------------------------------------
float4 ps_branch_3_0(BranchVS2PS i, uniform bool highQuality) : COLOR0
{
	half4 diffuseMap = gamma2linear(tex2D(speedTreeDiffuseSampler, i.tcAlphaRef.xy));

	//--
	half3 wNormal = normalize(i.normal);
	half3 spec    = 0;

	if (highQuality)
	{
		//-- calculate world space normal.
		half4   nSample = tex2D(speedTreeNormalSampler, i.tcAlphaRef.xy);
		half3   nn      = nSample.xyz * 2 - 1;
		half3x3 TBN		= half3x3(i.tangent, i.binormal, i.normal);
		half3   normal  = mul(nn, TBN);

		wNormal = normalize(mul(nn, TBN));
		spec	= g_specularParams.x * nSample.w * sunSpecTerm(wNormal, normalize(g_cameraPos.xyz - i.wPos), g_specularParams.y);
	}

	//-- lighting equation.
	half3 ambient = g_material[1].xyz * sunAmbientTerm().xyz;
	half3 diffuse = g_material[0].xyz * sunDiffuseTerm(wNormal).xyz;

	//--
	half3 color = diffuseMap.xyz * (ambient + diffuse) + spec;
	half  alpha = diffuseMap.a * max(g_instance.m_blendFactor, g_useAlpha * 0.5f);

	return float4(color, alpha);
}

//--------------------------------------------------------------------------------------------------
struct BillboardVS2PS
{
	float4 pos			: POSITION;
	float2 linearZMatID	: TEXCOORD0; //-- x - linear Z, y - material ID.
	float3 tcAlphaRef	: TEXCOORD1;
	float3 tangent		: TEXCOORD2;
	float3 binormal		: TEXCOORD3;
	float3 normal		: TEXCOORD4;
	float3 wPos			: TEXCOORD5;
};

//--------------------------------------------------------------------------------------------------
BillboardVS2PS vs_billboard_3_0(const VS_INPUT_BB i)
{
	BillboardVS2PS o = (BillboardVS2PS)0;

	//-- calculate view space position with respect to the wind animation.
	o.wPos		 = i.pos;
	o.wPos.xyz	*= g_instance.m_scale;
	o.wPos		 = qrot(o.wPos, g_instance.m_rotationQuat);
	o.wPos.xyz	+= g_instance.m_translation;

	o.pos	         = mul(float4(o.wPos, 1.0f), g_viewProjMat);
	o.linearZMatID.x = o.pos.w;
	o.linearZMatID.y = g_instance.m_materialID;
	o.tcAlphaRef.xy	 = i.tc.xy;

	//-- calculate TBN basis matrix.
	o.binormal = qrot(i.binormal, g_instance.m_rotationQuat);
	o.tangent  = qrot(i.tangent, g_instance.m_rotationQuat);
	o.normal   = normalize(cross(o.tangent, o.binormal));

	//-- world space alpha normal for imposters blending.
	float3 wAlphaNormal = qrot(i.alphaNormal, g_instance.m_rotationQuat);
	o.tcAlphaRef.z = calculateAlpha(wAlphaNormal, g_cameraDir, g_instance.m_alphaRef);
	
	return o;
}

//--------------------------------------------------------------------------------------------------
float4 ps_billboard_3_0(BillboardVS2PS i) : COLOR0
{
    half4 diffuseMap = gamma2linear(tex2D(speedTreeDiffuseSampler, i.tcAlphaRef.xy));

	//-- alpha test.
	clip(diffuseMap.a - i.tcAlphaRef.z);

	//-- calculate world normal.
	half4   nSample = tex2D(bbNormalSampler, i.tcAlphaRef.xy);
    half3   nn      = nSample.xyz * 2.0f - 1.0f;
	//-- Note: TBN matrix calculation. In C++ tangent is binormal and visa versa.
	half3x3 TBN     = half3x3(i.binormal, i.tangent, i.normal);
	half3   wNormal = normalize(mul(nn.xyz, TBN));

	//-- lighting equation.
	half3 ambient = g_material[1].xyz * sunAmbientTerm().xyz;
	half3 diffuse = g_material[0].xyz * sunDiffuseTerm(wNormal).xyz;
	half3 spec	   = g_specularParams.x * nSample.w * sunSpecTerm(wNormal, normalize(g_cameraPos.xyz - i.wPos), g_specularParams.y);

	//--
	half3 color = diffuseMap.xyz * (ambient + diffuse) + spec;
	half  alpha = diffuseMap.a * max(g_instance.m_blendFactor, g_useAlpha * 0.5f);

	return float4(color, alpha);
}

//--------------------------------------------------------------------------------------------------
PixelShader leafPS[2] = {
	compile ps_3_0 ps_leaf_3_0(true),
	compile ps_3_0 ps_leaf_3_0(false)
};

//--------------------------------------------------------------------------------------------------
VertexShader leafVS[2] = {
	compile vs_3_0 vs_leaf_3_0(true),
	compile vs_3_0 vs_leaf_3_0(false)
};

//--------------------------------------------------------------------------------------------------
VertexShader leaf_z_pass_VS[2] = {
	compile vs_3_0 vs_leaf_z_pass(true, true),
	compile vs_3_0 vs_leaf_z_pass(true, false)
};

//--------------------------------------------------------------------------------------------------
technique LEAF_DEPTH
{	
	pass Pass_0
	{
		ZENABLE = TRUE;
		ZWRITEENABLE = TRUE;
		COLORWRITEENABLE = 0x00;
		ZFUNC = LESSEQUAL;
		ALPHATESTENABLE = FALSE;
		ALPHABLENDENABLE = FALSE;
		STENCILENABLE = FALSE;
		CULLMODE = BW_CULL_NONE;

		VertexShader = leaf_z_pass_VS[g_useHighQuality ? 0 : 1];
		PixelShader  = compile ps_3_0 ps_leaf_z_pass();
	}
}

//--------------------------------------------------------------------------------------------------
technique LEAF_ALPHA
{	
	pass Pass_0
	{
		BW_FOG
		ZENABLE = TRUE;
		ZWRITEENABLE = FALSE;
		ZFUNC = EQUAL;
		COLORWRITEENABLE = g_useAlpha ? 0x0F : 0x07;
		ALPHATESTENABLE = FALSE;
		CULLMODE  = BW_CULL_NONE;
		ALPHABLENDENABLE = TRUE;
		BLENDOP = ADD;
		SRCBLEND = SRCALPHA;
		DESTBLEND = INVSRCALPHA;
				
		VertexShader = leafVS[g_useHighQuality ? 0 : 1];
		PixelShader  = leafPS[g_useHighQuality ? 0 : 1];
	}
}

//--------------------------------------------------------------------------------------------------
PixelShader branchPS[2] = {
	compile ps_3_0 ps_branch_3_0(true),
	compile ps_3_0 ps_branch_3_0(false)
};

//--------------------------------------------------------------------------------------------------
VertexShader branchVS[2] = {
	compile vs_3_0 vs_branch_3_0(true),
	compile vs_3_0 vs_branch_3_0(false)
};

//--------------------------------------------------------------------------------------------------
technique BRANCH_DEPTH
{
	pass Pass_0
	{
		ZENABLE = TRUE;
		ZWRITEENABLE = TRUE;
		COLORWRITEENABLE = 0x00;
		ZFUNC = LESSEQUAL;
		ALPHATESTENABLE = FALSE;
		ALPHABLENDENABLE = FALSE;
		STENCILENABLE = FALSE;
		CULLMODE = BW_CULL_NONE;

		VertexShader = compile vs_3_0 vs_branch_z_pass();
		PixelShader  = compile ps_3_0 ps_branch_z_pass();
	}
}

//--------------------------------------------------------------------------------------------------
technique BRANCH_ALPHA
{
	pass Pass_0
	{
		BW_FOG
		ZENABLE = TRUE;
		ZWRITEENABLE = FALSE;
		ZFUNC = EQUAL;
		COLORWRITEENABLE = g_useAlpha ? 0x0F : 0x07;
		ALPHATESTENABLE = FALSE;
		CULLMODE  = BW_CULL_NONE;
		ALPHABLENDENABLE = TRUE;
		BLENDOP = ADD;
		SRCBLEND = SRCALPHA;
		DESTBLEND = INVSRCALPHA;
				
		VertexShader = branchVS[g_useHighQuality ? 0 : 1];
		PixelShader  = branchPS[g_useHighQuality ? 0 : 1];
	}
}

//--------------------------------------------------------------------------------------------------
technique FROND_DEPTH
{
	pass Pass_0
	{
		ZENABLE = TRUE;
		ZWRITEENABLE = TRUE;
		COLORWRITEENABLE = 0x00;
		ZFUNC = LESSEQUAL;
		ALPHATESTENABLE = FALSE;
		ALPHABLENDENABLE = FALSE;
		STENCILENABLE = FALSE;
		CULLMODE = BW_CULL_NONE;

		VertexShader = compile vs_3_0 vs_branch_z_pass();
		PixelShader  = compile ps_3_0 ps_branch_z_pass();
	}
}

//--------------------------------------------------------------------------------------------------
technique FROND_ALPHA
{
	pass Pass_0
	{
		BW_FOG
		ZENABLE = TRUE;
		ZWRITEENABLE = FALSE;
		ZFUNC = EQUAL;
		COLORWRITEENABLE = g_useAlpha ? 0x0F : 0x07;
		ALPHATESTENABLE = FALSE;
		CULLMODE  = BW_CULL_NONE;
		ALPHABLENDENABLE = TRUE;
		BLENDOP = ADD;
		SRCBLEND = SRCALPHA;
		DESTBLEND = INVSRCALPHA;
				
		VertexShader = branchVS[g_useHighQuality ? 0 : 1];
		PixelShader  = branchPS[g_useHighQuality ? 0 : 1];
	}
}

//--------------------------------------------------------------------------------------------------
technique BILLBOARD_DEPTH
{
	pass Pass_0
	{
		ZENABLE = TRUE;
		ZWRITEENABLE = TRUE;
		ZFUNC = LESSEQUAL;
		COLORWRITEENABLE = 0x00;
		ALPHATESTENABLE = FALSE;
		ALPHABLENDENABLE = FALSE;
		CULLMODE = CW;

		VertexShader = compile vs_3_0 vs_billboard_z_pass();		
		PixelShader  = compile ps_3_0 ps_billboard_z_pass();
	}
}

//--------------------------------------------------------------------------------------------------
technique BILLBOARD_ALPHA
{
	pass Pass_0
	{
		BW_FOG
		ZENABLE = TRUE;
		ZWRITEENABLE = FALSE;
		ZFUNC = EQUAL;
		COLORWRITEENABLE = 7;
		ALPHATESTENABLE = FALSE;
		CULLMODE = CW;
		ALPHABLENDENABLE = TRUE;
		BLENDOP = ADD;
		SRCBLEND = SRCALPHA;
		DESTBLEND = INVSRCALPHA;

		VertexShader = compile vs_3_0 vs_billboard_3_0();
		PixelShader  = compile ps_3_0 ps_billboard_3_0();
	}
}

#else

//--------------------------------------------------------------------------------------------------
struct BranchVS2PS
{
	float4 pos		   : POSITION;
	float3 tcAlphaRef  : TEXCOORD0;
	float3 normal	   : TEXCOORD1;
	float  fog		   : FOG;
};

//--------------------------------------------------------------------------------------------------
BranchVS2PS vs_branch_2_0(const VS_INPUT_BRANCHES i)
{
	BranchVS2PS o = (BranchVS2PS)0;
	
	o.pos		  = branchesOutputPosition(i, g_instance, false);
	o.tcAlphaRef  = float3(i.tcWindInfo.xy, g_instance.m_alphaRef);
	o.normal	  = qrot(i.normal, g_instance.m_rotationQuat);

	//-- fog
	float4 wPos = mul(o.pos, g_invViewProjMat);
	o.fog = bw_vertexFog(wPos, o.pos.w);

	return o;
}

//--------------------------------------------------------------------------------------------------
float4 ps_branch_2_0(const BranchVS2PS i) : COLOR0
{
	//-- read albedo.
	half4 diffuseMap = tex2D(speedTreeDiffuseSampler, i.tcAlphaRef.xy);

	//-- lighting equation.
	half3 ambient = (half3)g_material[1].rgb * sunAmbientTerm();
	half3 diffuse = (half3)g_material[0].rgb * sunDiffuseTerm(normalize(i.normal));
	half3 color   = diffuseMap.rgb * (ambient + diffuse);

	return float4(color, diffuseMap.a * g_instance.m_blendFactor);
}

//--------------------------------------------------------------------------------------------------
technique BRANCH_DEPTH
{
	pass Pass_0
	{
		ZENABLE = TRUE;
		ZWRITEENABLE = TRUE;
		COLORWRITEENABLE = 0x00;
		ZFUNC = LESSEQUAL;
		ALPHATESTENABLE = FALSE;
		ALPHABLENDENABLE = FALSE;
		CULLMODE = BW_CULL_NONE;

		VertexShader = compile vs_2_0 vs_branch_z_pass(false);
		PixelShader  = compile ps_2_0 ps_branch_z_pass();
	}
}

//--------------------------------------------------------------------------------------------------
technique BRANCH_ALPHA
{
	pass Pass_0
	{
		BW_FOG
		ZENABLE = TRUE;
		ZWRITEENABLE = FALSE;
		ZFUNC = EQUAL;
		COLORWRITEENABLE = 7;
		ALPHATESTENABLE = FALSE;
		CULLMODE  = BW_CULL_NONE;
		ALPHABLENDENABLE = TRUE;
		BLENDOP = ADD;
		SRCBLEND = SRCALPHA;
		DESTBLEND = INVSRCALPHA;
				
		VertexShader = compile vs_2_0 vs_branch_2_0();
		PixelShader  = compile ps_2_0 ps_branch_2_0();
	}
}

//--------------------------------------------------------------------------------------------------
technique FROND_DEPTH
{
	pass Pass_0
	{
		ZENABLE = TRUE;
		ZWRITEENABLE = TRUE;
		ZFUNC = LESSEQUAL;
		COLORWRITEENABLE = 0x00;
		ALPHATESTENABLE = FALSE;
		ALPHABLENDENABLE = FALSE;
		CULLMODE = BW_CULL_NONE;

		VertexShader = compile vs_2_0 vs_branch_z_pass(false);
		PixelShader  = compile ps_2_0 ps_branch_z_pass();
	}
}

//--------------------------------------------------------------------------------------------------
technique FROND_ALPHA
{
	pass Pass_0
	{
		BW_FOG
		ZENABLE = TRUE;
		ZWRITEENABLE = FALSE;
		ZFUNC = EQUAL;
		COLORWRITEENABLE = 7;
		ALPHATESTENABLE = FALSE;
		CULLMODE  = BW_CULL_NONE;
		ALPHABLENDENABLE = TRUE;
		BLENDOP = ADD;
		SRCBLEND = SRCALPHA;
		DESTBLEND = INVSRCALPHA;
				
		VertexShader = compile vs_2_0 vs_branch_2_0();
		PixelShader  = compile ps_2_0 ps_branch_2_0();
	}
}

//--------------------------------------------------------------------------------------------------
struct LeafVS2PS
{
	float4 pos			:	POSITION;
	float4 tcExtra		:	TEXCOORD0;
	float3 normal		:	TEXCOORD1;
	float fog			:	FOG;
};

//--------------------------------------------------------------------------------------------------
LeafVS2PS vs_leaf_2_0(const VS_INPUT_LEAF i)
{
	LeafVS2PS o = (LeafVS2PS)0;
	
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
float4 ps_leaf_2_0(const LeafVS2PS i) : COLOR
{
	//-- read albedo.
	half4 diffuseMap = tex2D(speedTreeDiffuseSampler, i.tcExtra.xy);

	//-- apply leaf dimming
	diffuseMap.xyz *= i.tcExtra.z;

	//-- lighting equation.
	half3 ambient = (half3)g_material[1].rgb * sunAmbientTerm();
	half3 diffuse = (half3)g_material[0].rgb * sunDiffuseTerm(normalize(i.normal), g_leafLightAdj);
	half3 color   = diffuseMap.rgb * (ambient + diffuse);

	return float4(color, diffuseMap.a * g_instance.m_blendFactor);
}

//--------------------------------------------------------------------------------------------------
technique LEAF_DEPTH
{
	pass Pass_0
	{
		ZENABLE = TRUE;
		ZWRITEENABLE = TRUE;
		ZFUNC = LESSEQUAL;
		COLORWRITEENABLE = 0x00;
		ALPHATESTENABLE = FALSE;
		ALPHABLENDENABLE = FALSE;
		CULLMODE = NONE;

		VertexShader = compile vs_2_0 vs_leaf_z_pass(false, false);
		PixelShader  = compile ps_2_0 ps_leaf_z_pass();
	}
}

//--------------------------------------------------------------------------------------------------
technique LEAF_ALPHA
{
	pass Pass_0
	{
		BW_FOG
		ZENABLE = TRUE;
		ZWRITEENABLE = FALSE;
		ZFUNC = EQUAL;
		COLORWRITEENABLE = 7;
		ALPHATESTENABLE = FALSE;
		CULLMODE = NONE;
		ALPHABLENDENABLE = TRUE;
		BLENDOP = ADD;
		SRCBLEND = SRCALPHA;
		DESTBLEND = INVSRCALPHA;

		VertexShader = compile vs_2_0 vs_leaf_2_0();
		PixelShader  = compile ps_2_0 ps_leaf_2_0();
	}
}

//--------------------------------------------------------------------------------------------------
struct BillboardVS2PS
{
	float4 pos			:	POSITION;
	float3 tcAlphaRef	:	TEXCOORD0;
	float3 normal		:	TEXCOORD1;
	float  fog			:	FOG;
};

//--------------------------------------------------------------------------------------------------
BillboardVS2PS vs_billboard_2_0(const VS_INPUT_BB i)
{
	BillboardVS2PS o = (BillboardVS2PS) 0;

	float3 wPos	 = i.pos;
	wPos		*= g_instance.m_scale;
	wPos		 = qrot(wPos, g_instance.m_rotationQuat);
	wPos		+= g_instance.m_translation;

	//-- world space alpha normal for imposters blending.
	float3 wAlphaNormal = qrot(i.alphaNormal, g_instance.m_rotationQuat);
	float  alphaRef = calculateAlpha(wAlphaNormal, g_cameraDir, g_instance.m_alphaRef);

	o.pos		 = mul(float4(wPos, 1.0f), g_viewProjMat);
	o.tcAlphaRef = float3(i.tc, alphaRef);

	//-- calculate TBN basis matrix.
	float3 normal = normalize(cross(i.tangent, i.binormal));
	o.normal	  = qrot(normal, g_instance.m_rotationQuat);

	//-- fog.
	o.fog = bw_vertexFog(float4(wPos, 1.0f), o.pos.w);
		
	return o;
};

//--------------------------------------------------------------------------------------------------
float4 ps_billboard_2_0(const BillboardVS2PS i) : COLOR
{
    half4 diffuseMap = tex2D(speedTreeDiffuseSampler, i.tcAlphaRef.xy);

	//-- alpha test.
	clip(diffuseMap.a - i.tcAlphaRef.z);

	//-- lighting equation.
	half3 ambient = (half3)g_material[1].rgb * sunAmbientTerm();
	half3 diffuse = (half3)g_material[0].rgb * sunDiffuseTerm(normalize(i.normal), g_leafLightAdj);
	half3 color   = diffuseMap.rgb * (ambient + diffuse);

	return float4(color, diffuseMap.a * g_instance.m_blendFactor);
};

//--------------------------------------------------------------------------------------------------
technique BILLBOARD_DEPTH
{
	pass Pass_0
	{
		ZENABLE = TRUE;
		ZWRITEENABLE = TRUE;
		ZFUNC = LESSEQUAL;
		COLORWRITEENABLE = 0x00;
		ALPHATESTENABLE = FALSE;
		ALPHABLENDENABLE = FALSE;
		CULLMODE = CW;
			
		VertexShader = compile vs_2_0 vs_billboard_z_pass();		
		PixelShader  = compile ps_2_0 ps_billboard_z_pass();
	}
}

//--------------------------------------------------------------------------------------------------
technique BILLBOARD_ALPHA
{
	pass Pass_0
	{
		BW_FOG
		ZENABLE = TRUE;
		ZWRITEENABLE = FALSE;
		ZFUNC = EQUAL;
		COLORWRITEENABLE = 7;
		ALPHATESTENABLE = FALSE;
		CULLMODE = CW;
		ALPHABLENDENABLE = TRUE;
		BLENDOP = ADD;
		SRCBLEND = SRCALPHA;
		DESTBLEND = INVSRCALPHA;
			
		VertexShader = compile vs_2_0 vs_billboard_2_0();		
		PixelShader  = compile ps_2_0 ps_billboard_2_0();
	}
}

#endif //-- BW_DEFERRED_SHADING
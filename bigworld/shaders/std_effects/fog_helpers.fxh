#ifndef FOG_HELPERS_FXH
#define FOG_HELPERS_FXH

// BigWorld's version of bw_vertexFog func.
//--------------------------------------------------------------------------------------------------
float vertexFog( in float wPos, in float fogStart, in float fogEnd )
{
	float2 fogging = float2((-1.0 / (fogEnd - fogStart)), (fogEnd / (fogEnd - fogStart)));
	return wPos * fogging.x + fogging.y;
}

//-- calculte vertex fog.
//--------------------------------------------------------------------------------------------------
float bw_vertexFog(in float4 wPos, in float linearZ)
{
	//-- fog enabled if spaceBB is not zero vector.
	float isBBFogEnabled = all(g_fogParams.m_outerBB);
	
	//-- calculate the camera's far plane fog. Make sure that is clamped between 0.0f and 1.0f.
	float outFog = saturate((g_fogParams.m_end - linearZ) / (g_fogParams.m_end - g_fogParams.m_start));
	
	//-- calculate space bounds fog. This an optimized vectors form. Make sure we can't try to divide by zero.
	float4 coeff = max(g_fogParams.m_density * ((wPos.xzxz - g_fogParams.m_innerBB) / ((g_fogParams.m_outerBB - g_fogParams.m_innerBB) + (1.0f - isBBFogEnabled))), 0.0f);
	float fogBB  = 1.0f - max(max(max(coeff.x, coeff.y), coeff.z), coeff.w);
		
	//-- Is spaceBB fog enabled?
	outFog = min(outFog, fogBB) * isBBFogEnabled + outFog * (1.0f - isBBFogEnabled);
		
	return outFog;
}

//--------------------------------------------------------------------------------------------------
#define BW_VERTEX_FOG(o)	o.fog = bw_vertexFog(o.worldPos, o.pos.w);

//-- fogDensity 1 - no fog, 0 - full fog.
//--------------------------------------------------------------------------------------------------
half3 applyFogTo(const in half3 color, const in half fogDensity)
{
	return lerp(color, (half3)g_fogParams.m_color.rgb * (half)g_HDRParams.w, (1 - fogDensity) * (half)g_fogParams.m_enabled);
}

//-- fogDensity 1 - no fog, 0 - full fog.
//--------------------------------------------------------------------------------------------------
half3 applyFogTo(const in half3 color, const in half3 fogColor, const in half fogDensity)
{
	return lerp(color, fogColor * (half)g_HDRParams.w, (1 - fogDensity) * (half)g_fogParams.m_enabled);
}

#endif //FOG_HELPERS_FXH
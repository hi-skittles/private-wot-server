#ifndef _BW_SHADOW_HELPER_FXH_
#define _BW_SHADOW_HELPER_FXH_

sampler g_ssShadowMapSml = sampler_state
{									
	Texture = (g_ssShadowMap);
	ADDRESSU = CLAMP;	
	ADDRESSV = CLAMP;
	ADDRESSW = CLAMP;
	MAGFILTER = POINT;
	MINFILTER = POINT;
	MIPFILTER = POINT;
	MAXANISOTROPY = 1;
	MAXMIPLEVEL   = 0;
	MIPMAPLODBIAS = 0;
};

//--------------------------------------------------------------------------------------------------
half calcShadow(float2 tc, in half backedShadow, in half viewZ, const bool enableShadows)
{
	if (enableShadows)
	{
		// Channels: r - dynamic; g - semi terrain; b - semi object
		half3 shadows = tex2D( g_ssShadowMapSml, tc ).rgb;
		half  semi    = saturate( shadows.b + shadows.g );
		half t        = saturate( ( viewZ - g_shadowBlendParams.x ) / g_shadowBlendParams.y + 1.f );
		half s        = saturate( shadows.r + ( shadows.b * g_shadowBlendParams.z ) + shadows.g );

		return min(1.0h - lerp( s, semi, t ), backedShadow);
	}

	return backedShadow;
}

#endif // _BW_SHADOW_HELPER_FXH_
#include "stdinclude.fxh"
#include "read_g_buffer.fxh"

//--------------------------------------------------------------------------------------------------

// x -- blend range begins from
// y -- blend range lendth
//      semi dynamic shadows has being drawing after blend range
float2 g_blend;

// x, y -- minimal corner of the coverage area (world space)
// z, w -- 1/width and 1/height of the coverage area (world space)
float4 g_worldToIndirectionTcTransform;

// x = 1.f / shadowMapRT.width()
// y = 1.f / shadowMapRT.height()
// z = x * 2.f
// w = y * 2.f
float4 g_shadowMapSizeInv;

// x - g_cropZn - from code 
// y - g_cropZf - from code
float2 g_cropDistances;

// sunViewMatrix
float4x4 g_sunViewMatrix;

// Chunks sizes.
float g_quality[2];

// 1.f / m_coverageAreaSizeInv
float g_coverAreaSizeInv;

//--------------------------------------------------------------------------------------------------

texture g_shadowMapLow;
sampler g_shadowMapSmlLow = sampler_state
{
	Texture 		= (g_shadowMapLow);
	ADDRESSU		= BORDER;
	ADDRESSV		= BORDER;
	ADDRESSW		= BORDER;
	MAGFILTER 		= POINT;
	MINFILTER 		= POINT;
	MIPFILTER 		= POINT;
	MAXMIPLEVEL 	= 0;
	MIPMAPLODBIAS 	= 0;
	MAXANISOTROPY   = 1;

	// TODO(a_cherkes): Reconsider. 
	//                  The border color has a some strange value
	//                  because of we want to have all pixels abroad 
	//                  shadow coverage area to be lited (shadows can
	//                  apear inside area only).
	BORDERCOLOR = float4( 0.f, 0.f, 0.f, 0.f );
};

texture g_shadowMapHeight;
sampler g_shadowMapSmlHeight = sampler_state
{
	Texture 		= (g_shadowMapHeight);
	ADDRESSU		= BORDER;
	ADDRESSV		= BORDER;
	ADDRESSW		= BORDER;
	MAGFILTER 		= POINT;
	MINFILTER 		= POINT;
	MIPFILTER 		= POINT;
	MAXMIPLEVEL 	= 0;
	MIPMAPLODBIAS 	= 0;
	MAXANISOTROPY   = 1;

	// TODO(a_cherkes): Reconsider. 
	//                  The border color has a some strange value
	//                  because of we want to have all pixels abroad 
	//                  shadow coverage area to be lited (shadows can
	//                  apear inside area only).
	BORDERCOLOR = float4( 0.f, 0.f, 0.f, 0.f );
};


// x, y -- projection center
// w, h -- projection 1.f / width and 1.f / height
texture g_indirectionMapProj;
sampler g_indirectionMapProjSml = sampler_state
{
	Texture 		= (g_indirectionMapProj);
	ADDRESSU		= BORDER;	
	ADDRESSV		= BORDER;
	ADDRESSW		= BORDER;
	MAGFILTER 		= POINT;
	MINFILTER 		= POINT;
	MIPFILTER 		= POINT;
	MAXMIPLEVEL 	= 0;
	MIPMAPLODBIAS 	= 0;
	BORDERCOLOR     = float4( 0, 0, 1, 1 );
	MAXANISOTROPY   = 1;
};

// x, y -- left up corner
// w, h -- width and height
texture g_indirectionMapTc;
sampler g_indirectionMapTcSml = sampler_state
{
	Texture 		= (g_indirectionMapTc);
	ADDRESSU		= CLAMP;
	ADDRESSV		= CLAMP;
	ADDRESSW		= CLAMP;
	MAGFILTER 		= POINT;
	MINFILTER 		= POINT;
	MIPFILTER 		= POINT;
	MAXMIPLEVEL 	= 0;
	MIPMAPLODBIAS 	= 0;
	BORDERCOLOR     = float4( 1, 1, 1, 1 );
	MAXANISOTROPY   = 1;
};

//--------------------------------------------------------------------------------------------------

BW_DS_LIGHT_PASS_VS2PS VS(BW_DS_LIGHT_PASS_VS i)
{
	BW_DS_LIGHT_PASS_VS2PS o = (BW_DS_LIGHT_PASS_VS2PS) 0;
	o.pos = i.pos;
	o.tc  = i.tc;
	return o;
}

// Sample shadow map without PCF.
// returns coverage value
// 0 -- light
// 1 -- shadow
float2 sampleShadowMapSimple(float2 tc, float z, int quality)
{
	// r - terrain, g - objects
	if ( quality == 1 )
		return z > tex2D( g_shadowMapSmlLow, tc ).rg;
	return z > tex2D( g_shadowMapSmlHeight, tc ).rg;
}

// Sample shadow map with simple PCF.
// Returns coverage value
// 0 -- light
// 1 -- shadow
float2 sampleShadowMapLinearPCF(float2 tc, float z, int quality)
{
	float dx = -g_shadowMapSizeInv.x;
	float dy = -g_shadowMapSizeInv.y;

	float2 t0; // = { 1.f, 1.f };
	float2 t1; // = t0;
	float2 t2; // = t0;
	float2 t3; // = t0;

#if 1

	if ( quality == 0 )
	{
		// r - terrain, g - objects

		t0 = z > tex2D( g_shadowMapSmlHeight, tc + float2( 0.f, 0.f )).rg;
		t1 = z > tex2D( g_shadowMapSmlHeight, tc + float2( dx,  0.f )).rg;
		t2 = z > tex2D( g_shadowMapSmlHeight, tc + float2( 0.f, dy  )).rg;
		t3 = z > tex2D( g_shadowMapSmlHeight, tc + float2( dx,  dy  )).rg;
	}
	else if ( quality == 1 )
	{
		// r - terrain, g - objects
		t0 = z > tex2D( g_shadowMapSmlLow, tc + float2( 0.f, 0.f )).rg;
		t1 = z > tex2D( g_shadowMapSmlLow, tc + float2( dx,  0.f )).rg;
		t2 = z > tex2D( g_shadowMapSmlLow, tc + float2( 0.f, dy  )).rg;
		t3 = z > tex2D( g_shadowMapSmlLow, tc + float2( dx,  dy  )).rg;
	}

	float2 shadowMapSize = 1.f / float2( dx, dy );
	float2 lerps = frac(shadowMapSize * tc.xy);
	return lerp( lerp( t0, t1, lerps.x ), lerp( t2, t3, lerps.x ), lerps.y );

#else 

	if ( quality < 1 )
	{
		// r - terrain, g - objects
		t0 = z > tex2D( g_shadowMapSmlHeight, tc + float2( 0.f, 0.f )).rg;
		t1 = z > tex2D( g_shadowMapSmlHeight, tc + float2( dx,  0.f )).rg;
		t2 = z > tex2D( g_shadowMapSmlHeight, tc + float2( 0.f, dy  )).rg;
		t3 = z > tex2D( g_shadowMapSmlHeight, tc + float2( dx,  dy  )).rg;

		float2 shadowMapSize = 1.f / float2( dx, dy );
		float2 lerps = frac(shadowMapSize * tc.xy);

		return lerp( lerp( t0, t1, lerps.x ), lerp( t2, t3, lerps.x ), lerps.y );
	}

	return sampleShadowMapSimple( tc, z, 1 );
#endif
}

//--------------------------------------------------------------------------------------------------
float2 calcCoord( int quality, int idx )
{
	float4 q = g_quality[quality];
	return float2( q.x + idx % q.z, q.y + ceil( idx / q.z ) );
}

//--------------------------------------------------------------------------------------------------
float4 PS(BW_DS_LIGHT_PASS_VS2PS i) : COLOR
{
	float3 worldPos = g_buffer_readWorldPos(i.tc, g_nvStereoParams.w);

	// Выисляем координаты с которой будем сэмплировать indirection-текстуру.
	float2 indirectionTc = worldPos.xz;
	indirectionTc -= g_worldToIndirectionTcTransform.xy;
	indirectionTc *= g_worldToIndirectionTcTransform.zw;

	clip( 1.0f - abs( indirectionTc ) - g_coverAreaSizeInv * 2.f );

	indirectionTc.xy = indirectionTc.xy * float2(0.5f, 0.5f) + float2(0.5f, 0.5f);
	indirectionTc -= g_coverAreaSizeInv;

	// Сэмплиреум indirection-текстуру.
	float4 indProj = tex2Dlod( g_indirectionMapProjSml, float4( indirectionTc, 0, 0 ) );
	float4 indTc   = tex2Dlod( g_indirectionMapTcSml, float4( indirectionTc, 0, 0 ) ).argb * 255.f;

	// Начинаем вычислять проекцию точки на карту теней.
	float4 shadowTc = mul( float4( worldPos, 1.f ), g_sunViewMatrix );

	// Эмулируем умножение shadowTc на crop-матрицу солнца данного чанка.
	shadowTc.x = 2.f * (shadowTc.x - indProj.x) * indProj.z;
	shadowTc.y = 2.f * (shadowTc.y - indProj.y) * indProj.w;
	shadowTc.z = (shadowTc.z - g_cropDistances.x) / (g_cropDistances.y - g_cropDistances.x);
	shadowTc /= shadowTc.w;

	// Сlip-space => texture coords space.
	shadowTc.xy = CS2TS( shadowTc.xy );

	// Now clip if texture coords are outside valid range (don't want to sample adjacent atlas slots)
	clip( float4(shadowTc.xy, 1.f - shadowTc.xy) );
	
	// Корректируем текстурные координаты под нужный квадрат на карте теней.
	// shadowTc.x = indTc.x + shadowTc.x * indTc.z;
	// shadowTc.y = indTc.y + shadowTc.y * indTc.w;

	int   quality = indTc.z;
	float size = g_quality[quality];

	// Корректируем текстурные координаты под нужный квадрат на карте теней.
#if 1
	// float4 inv   = { g_shadowMapSizeInv.x, g_shadowMapSizeInv.y, g_shadowMapSizeInv.x * 2.f, g_shadowMapSizeInv.y * 2.f };
	// float  invX  = g_shadowMapSizeInv.x; // * 2;
	// float  invY  = g_shadowMapSizeInv.y; // * 2;
	// float  inv2X = invX * 2.f;
	// float  inv2Y = invY * 2.f;

	shadowTc.x = ( indTc.x * size + g_shadowMapSizeInv.x ) + shadowTc.x * ( size - g_shadowMapSizeInv.z );
	shadowTc.y = ( indTc.y * size + g_shadowMapSizeInv.y ) + shadowTc.y * ( size - g_shadowMapSizeInv.w );
#else
	shadowTc.x = indTc.x * size + shadowTc.x * size;
	shadowTc.y = indTc.y * size + shadowTc.y * size;
#endif

	// Вычисляем тень (два способа: простой и с PCF).
#if 1
	float2 t = sampleShadowMapLinearPCF(shadowTc.xy, shadowTc.z, quality);
#else
	float2 t = sampleShadowMapSimple(shadowTc.xy, shadowTc.z, quality);	
#endif

	// Возврат Green | Blue.
	return float4(0, t, 0);
}

//--------------------------------------------------------------------------------------------------

technique RECEIVE
{
	pass Pass_0
	{
		COLORWRITEENABLE = GREEN | BLUE;
		ALPHATESTENABLE = FALSE;
		ZENABLE = FALSE;
		ZWRITEENABLE = FALSE;
		ALPHABLENDENABLE = FALSE;
		FOGENABLE = FALSE;
		POINTSPRITEENABLE = FALSE;
		CULLMODE = CW;

		//-- use stencil to mark only valid g-buffer pixels (i.e. not sky and flora pixels)
		STENCILENABLE = TRUE;
		STENCILFUNC = NOTEQUAL;
		STENCILWRITEMASK = 0x00;
		STENCILMASK = G_STENCIL_USAGE_ALL_OPAQUE;
		STENCILREF = 0;

		VertexShader = compile vs_3_0 VS();
		PixelShader  = compile ps_3_0 PS();
	}
};

//--------------------------------------------------------------------------------------------------
//-- End

#include "stdinclude.fxh"
#include "terrain_common.fxh"

// Auto variables
//matrix viewProj : ViewProjection; // already defined  in "terrain_common.fxh"
texture floraTexture : FloraTexture;
//typedef float4 AnimationArray[64];
//AnimationArray animationGrid : FloraAnimationGrid;
float2 localAnimations[64];
float2 globalAnimations[64];

// Manual variables
//float4x4 vertexToWorld;
float2 VISIBILITY;
float g_alphaRef;
matrix LIGHT_MAP_PROJECTION;
//float POS_MULTIPLIER = (200.0/32767.0,200.0/32767.0,200.0/32767.0,1.0);
//float POS_MULTIPLIER = (1.0,1.0,1.0,1.0);
float FLEX_MULTIPLIER = 1.0 / 255.0;
float2 UV_MULTIPLIER = (1.0/16383.0, 1.0/16383.0);
float4 ambient;
float3 g_windDirection; // normalized force

const float g_tintBegin;
const float g_tintEnd;
texture		g_tintMap;
float g_useRandomAlpha = 1;

texture g_texAlpha;

sampler g_tintMapSlr = sampler_state
{
	Texture = (g_tintMap);
	ADDRESSU = BORDER;	
	ADDRESSV = BORDER;
	ADDRESSW = BORDER;
	MAGFILTER = LINEAR;
	MINFILTER = LINEAR;
	MIPFILTER = LINEAR;
	BORDERCOLOR = float4(0,0,0,0);
};

sampler floraTextureSampler = sampler_state
{
	Texture = (floraTexture);
	ADDRESSU = CLAMP;
	ADDRESSV = CLAMP;
	MAGFILTER = LINEAR;
	MINFILTER = LINEAR;
	MIPFILTER = LINEAR;
};

sampler smpAlpha = sampler_state
{
	Texture = (g_texAlpha);
	ADDRESSU = Wrap;
	ADDRESSV = Wrap;
	MAGFILTER = LINEAR;
	MINFILTER = LINEAR;
	MIPFILTER = LINEAR;
};
//--------------------------------------------------------------------------------------------------
#if BW_DEFERRED_SHADING

#include "write_g_buffer.fxh"

//--------------------------------------------------------------------------------------------------
struct FloraVertex
{
	float4 pos			:	POSITION;   
	float2 tc			:	TEXCOORD0;
	float2 animation	:	BLENDWEIGHT;
	float4 tint			:	TEXCOORD1;
};

//--------------------------------------------------------------------------------------------------
struct OutputVertex
{
	float4 pos			:	POSITION0;
	float2 tc0			:	TEXCOORD0; //-- floraTexture (Diffuse)
	float4 tint			:	TEXCOORD1; //-- xyz - tint clipPos, w - tint factor.
	float  linearZ		:	TEXCOORD2;
	float3 normal		:	TEXCOORD3;
	float4 col			:	COLOR;
};

//--------------------------------------------------------------------------------------------------
OutputVertex vs_deferred_3_0(FloraVertex i)
{
	OutputVertex o = (OutputVertex)0;

	//-- animate vertex position	
	float4 animatedPos		= i.pos;

	int idxLocal			= i.animation.y;
	animatedPos.xz			+= i.animation.x * FLEX_MULTIPLIER * localAnimations[idxLocal];

	int idxGlobal = (int)dot( i.pos, g_windDirection ) % 64;
	animatedPos.xz			+= i.animation.x * FLEX_MULTIPLIER * globalAnimations[idxGlobal];
	float4 animatedWorldPos = animatedPos;

	o.pos = mul(animatedWorldPos, g_viewProjMat);
	o.tc0.xy = i.tc.xy * UV_MULTIPLIER;

	//-- fade out based on distance
	float dist = length(o.pos.xyz) * VISIBILITY.x + VISIBILITY.y;
	o.col.w = 1.0 - saturate(dist);

	//-- write clip position.
	o.linearZ = o.pos.w;

	//-- ToDo: reconsider. For now flora's normal looks up.
//	o.normal = mul(float4(0,1,0,0), vertexToWorld).xyz;
	o.normal = float4( 0, 1, 0, 0 );

	//-- calculate tint texture coordinates.
	{
		//-- transform local to chunk tint position to the world space.
		float4 worldTintPos = float4( i.tint.xyz, 1 ); //mul(float4(i.tint.xyz, 1.0f), vertexToWorld);

		//-- and now transform it to the clip space.
		float4 clipTintPos = mul(worldTintPos, g_viewProjMat);

		//-- now send to the pixel shader tint clip position and tint factor.
		o.tint.xyz = clipTintPos.xyw;
		o.tint.w   = i.tint.w;
	}

	return o;
}

float getAlpha( int2 vScreenSpace: VPOS, float k )
{
	float fAlpha = tex2Dlod( smpAlpha, float4( vScreenSpace.xy / 64.0, 0, 0 ) ).r;
	return ( fAlpha > k ? 0 : 1 );
//	return fAlpha;
}

//--------------------------------------------------------------------------------------------------
G_BUFFER_LAYOUT ps_deferred_3_0(OutputVertex i, int2 vScreenSpace	:	VPOS )
{
	G_BUFFER_LAYOUT o = (G_BUFFER_LAYOUT)0;

	//-- 1. write albedo.
	{
		float2 tintUV     = CS2TS(i.tint.xy / i.tint.z);
		float  tintFactor = i.tint.w;

		half4 diffuse     = gamma2linear(tex2D(floraTextureSampler, i.tc0));
		//-- Note: environment is already in linear space.
		half3 environment = tex2D(g_tintMapSlr, tintUV).xyz;
		
		//-- sets stepCoeff in 1 if environment color is zero vector i.e. (0,0,0). This zero vector
		//-- indicates that either we try to sample back-buffer copy outside its dimension (i.e. 
		//-- outside the view port) or we try to sample sky's color.
		//-- Sets 0 if environment color is not black.
		half stepCoeff = step(dot(environment, environment), 0.001f);
		
		//-- correct environment color based on stepCoeff.
		environment   = lerp(environment, diffuse.xyz, stepCoeff);

		//-- ToDo: tweak. Use another algo for example lerp.
		half tf	  = smoothstep(g_tintEnd, g_tintBegin, tintFactor);
//		tf = pow( tf, 4 );
		tf = saturate( tf + 1 - i.col.w );
		half3 albedo = lerp(diffuse.xyz, environment, tf);
		half  alpha  = i.col.a * diffuse.a;

//		if ( g_useRandomAlpha > 0 )
//			alpha = getAlpha( vScreenSpace, smoothstep( 0, 0.25, alpha ) );
/*
		if ( alpha < 0.25f ) albedo = float3( 0, 0, 1 );
		else if ( alpha < 0.5f ) albedo = float3( 0, 1, 0 );
		else if ( alpha < 0.75f ) albedo = float3( 1, 0, 0 );
		else albedo = float3( 1, 1, 0 );
*/

//		albedo = i.col.w;
//		albedo = alpha;
//		alpha = 1;

		clip( alpha - g_alphaRef );

		g_buffer_writeAlbedo(o, albedo);
	}

	//-- 2. write depth.
	g_buffer_writeDepth(o, i.linearZ);

	//-- 3. write normal.
	g_buffer_writeNormal(o, i.normal);

	//-- 4. write object kind
	g_buffer_writeObjectKind(o, G_OBJECT_KIND_FLORA);

	return o;
}

//--------------------------------------------------------------------------------------------------
technique DS
{
	pass Pass_0
	{
		ZENABLE = TRUE;
		CULLMODE = NONE;
		ZFUNC = LESSEQUAL;
		FOGENABLE = FALSE;
		LIGHTING = FALSE;
		ALPHABLENDENABLE = FALSE;
		ALPHATESTENABLE = FALSE;

		VertexShader = compile vs_3_0 vs_deferred_3_0();
		PixelShader  = compile ps_3_0 ps_deferred_3_0();      
	}
}

#else //-- BW_DEFERRED_SHADING

//--------------------------------------------------------------------------------------------------
float4 dummyVS(in float4 pos : POSITION) : POSITION
{
	return pos;
}

//--------------------------------------------------------------------------------------------------
float4 dummyPS(in float4 pos : POSITION) : COLOR0
{
	return float4(1,1,1,1);
}

//--------------------------------------------------------------------------------------------------
technique DummyTechnique
{									
	pass DummyPass					
	{		
		VertexShader = compile vs_2_0 dummyVS();
		PixelShader  = compile ps_2_0 dummyPS();
	}
}

#endif //-- BW_DEFERRED_SHADING
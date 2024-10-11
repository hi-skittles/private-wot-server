#include "stdinclude.fxh"
#include "fog_helpers.fxh"

// Exposed artist editable variables.
texture decalMap;
float g_lifeTime;

// shader constants.
float g_fadeTime 				= 2.5f;
float g_invFadeTime 			= 1.0f / 2.5f;

float4x4 identity = { 
				1,0,0,0,
				0,1,0,0,
				0,0,1,0,
				0,0,0,1 };
			

#define BW_TEXTURESTAGE_DECAL(stage, inTexture)\
COLOROP[stage] 			= SELECTARG1;\
COLORARG1[stage] 		= TEXTURE;\
COLORARG2[stage] 		= DIFFUSE;\
ALPHAOP[stage] 			= SELECTARG1;\
ALPHAARG1[stage] 		= TEXTURE;\
ALPHAARG2[stage]		= DIFFUSE;\
Texture[stage] 			= (inTexture);\
ADDRESSU[stage]	 		= WRAP;\
ADDRESSV[stage] 		= WRAP;\
ADDRESSW[stage] 		= WRAP;\
MAGFILTER[stage] 		= LINEAR;\
MINFILTER[stage] 		= LINEAR;\
MIPFILTER[stage] 		= LINEAR;\
MAXMIPLEVEL[stage] 		= 0;\
MIPMAPLODBIAS[stage] 	= 0;\
TexCoordIndex[stage] 	= stage;

sampler decalSampler = sampler_state
{
	Texture 		= (decalMap);
	ADDRESSU 		= WRAP;
	ADDRESSV 		= WRAP;
	ADDRESSW 		= WRAP;
	MAGFILTER 		= LINEAR;
	MINFILTER 		= LINEAR;
	MIPFILTER 		= LINEAR;
	MAXMIPLEVEL 	= 0;
	MIPMAPLODBIAS 	= 0;
};

struct VertexXYZUVP
{
   float4 pos:		POSITION;
   float4 tc:		TEXCOORD0; // xy for tex1, zw for tex2
   float2 time:		TEXCOORD1; // x is time, y is tex1->tex2 factor
};

struct DecalOut
{
	float4 pos:		POSITION;
	float4 tc: 		TEXCOORD0;
	float3 fog:		TEXCOORD1;
	float4 worldPos: TEXCOORD2;
	float2 alpha:	TEXCOORD3; // x is alpha, y is tex1->tex2 factor
};

DecalOut decalVS ( VertexXYZUVP i )
{
	DecalOut o = (DecalOut)0;
	o.pos = mul( i.pos, g_viewProjMat );
	o.worldPos = i.pos;
	BW_VERTEX_FOG(o)
	o.tc = i.tc;
	// calculate alpha attenuation.
	o.alpha.x = max((g_time - i.time.x) + g_fadeTime - g_lifeTime, 0.0f) * g_invFadeTime;
	o.alpha.y = i.time.y;
	return o;
};

float4 decalPS( DecalOut i ) : COLOR0
{
	float4 tex = tex2D( decalSampler, i.tc.xy );
	tex = lerp(tex, tex2D( decalSampler, i.tc.zw ), i.alpha.y);
	i.fog = saturate( i.fog );
	float alpha = max(0.0f, tex.w + i.alpha.x);
	return float4( (tex.xyz * i.fog + ((1.0f - i.fog) * g_fogParams.m_color.xyz)), alpha);
};


//--------------------------------------------------------------//
// Technique Section for standard
//--------------------------------------------------------------//
technique shaderDecal
{
	pass Pass_0
	{
		LIGHTING = FALSE;
		ALPHATESTENABLE = FALSE;
		ALPHABLENDENABLE = TRUE;
		SRCBLEND = INVSRCALPHA;
		DESTBLEND = SRCALPHA;
		ZENABLE = TRUE;
		ZWRITEENABLE = FALSE;
		ZFUNC = LESSEQUAL;
		CULLMODE = CCW;
		FOGENABLE = FALSE; //doing the fogging in the shader
		
		VertexShader = compile vs_2_0 decalVS();
		PixelShader = compile ps_2_0 decalPS();
	}
}

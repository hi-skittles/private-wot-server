#include "post_processing.fxh"

// The heat shimmer effect for PC
// This effect takes a full-screen mesh with vertices in clip space.
// Two sets of uvs are output, one being the standard uvs, the other
// begin heat-shimmer perturbed uvs ( done in this shader )

texture inputTexture<
	bool artistEditable = true;
	string UIDesc = "Input texture/render target (you can drag a texture or render target from the Asset Browser)";
>;

float4 sinVec = {1.f, -0.16161616f, 0.0083333f, -0.00019841f};

float speed <
	bool artistEditable = true;
	float UIMin = 0.1;
	float UIMax = 500.0;
	int UIDigits = 2;
	string UIDesc = "Shimmer effect animation speed";
> = 121.f;

float spreadX <
	bool artistEditable = true;
	float UIMin = 0.0;
	float UIMax = 2.0;
	int UIDigits = 2;
	string UIDesc = "Effect's horizontal spread";
> =  0.f;
	
float spreadY <
	bool artistEditable = true;
	float UIMin = 0.0;
	float UIMax = 2.0;
	int UIDigits = 2;
	string UIDesc = "Effect's vertical spread";
> =  0.4f;

float freqS <
	bool artistEditable = true;
	float UIMin = 0.0;
	float UIMax = 2.0;
	int UIDigits = 2;
	string UIDesc = "Effect's horizontal frequency";
> = 0.f;
	
float freqT <
	bool artistEditable = true;
	float UIMin = 0.0;
	float UIMax = 2.0;
	int UIDigits = 2;
	string UIDesc = "Effect's vertical frequency";
> = 0.7f;

float4 waveSpeed <
	bool artistEditable = true;
	string UIDesc = "Wave speed";
> = {0.2f, 0.15f, 0.4f, 0.4f};

float4 fixups = {1.02f, 0.003f, 0.f, 0.f};
float uFixup  = -0.025f;
float vFixup  = 2.f;

float fullscreenAlpha <
	bool artistEditable = true;
	float UIMin = 0;
	float UIMax = 1.0;
	int UIDigits = 2;
	string UIDesc = "Full-screen effect alpha";
> = 0.f;

float twoPi = 6.283185307179586476925286766559f;

//-------------------------------------------------------------------------------------------------
struct Output
{
	float4 pos: POSITION;
	float2 tc:  TEXCOORD0;
	float2 tc1: TEXCOORD1;	
	float4 diffuse: COLOR;
};

//-------------------------------------------------------------------------------------------------
Output vs_main( VertexXYZNUV input )
{
	Output o = (Output)0;
	float4 r0;
	float4 r1;
	float4 r2;
	float4 r3;
	float4 r5;
	float4 r7;
	float4 r9;	
	float4 r11;

	//-- shortcuts.
	float invWidth	= g_invScreen.z;
	float invHeight	= g_invScreen.w;
	float hw		= g_screen.z;
	float hh		= g_screen.w;
	
	// Transform vertex to render target (screen space)
	const float4 texel2texelMapping = float4(-invWidth, invHeight, 0.0f, 0.0f);

	o.pos  = float4(input.pos.xy, 0.0f, 1.0f);
	o.pos += texel2texelMapping;

	// Calculate some more stuff that used to be sent through from C++	
	float4 NOISE_FREQ_S = float4( freqS * 0.25f * hw, freqS * 0.f * hh, freqS * -0.7f * hw, freqS * -0.8f * hh );
	float4 NOISE_FREQ_T = float4( freqT * 0.f * hw, freqT * 0.015f * hh, freqT * -0.7f * hw, freqT * 0.1f * hh );
	float2 UVFIX = float2( uFixup * invWidth, vFixup * invHeight );

	float t = g_time * (speed/10.f);
	float4 ANIMATION = float4( spreadX * invWidth, spreadY * invHeight, t, twoPi );

	// Set UV 0 to be standard tex coordinates ( unperturbed )
	o.tc   = BW_UNPACK_TEXCOORD(input.tc);	
	r11.xy = o.tc;	

	// Output colour as passed in alpha
	// This is for full-screen effects ( like when you
	// are inside a shockwave )
	o.diffuse = fullscreenAlpha;

	// Animate the uv.
	r0 = (NOISE_FREQ_S * r11.x);	
	r0 = r0 + (NOISE_FREQ_T * r11.y);	

	r1 = ANIMATION.zzzz;	
	r0 = r0 + r1 * waveSpeed;	
	r0.xy = frac(r0);	
	r1.xy = frac(r0.zwzw);
	r0.zw = r1.xyxy;
	r0 = r0 * fixups.x;
	r0 = r0 - 0.5;
	r1 = r0 * twoPi;

	r2 = r1 * r1;
	r3 = r2 * r1;
	r5 = r3 * r2;
	r7 = r5 * r2;
	r9 = r7 * r2;

	r0 = r1 + r3 * sinVec.x;
	r0 = r0 + r5 * sinVec.y;
	r0 = r0 + r7 * sinVec.z;
	r0 = r0 + r9 * sinVec.w;

	// And output uv.  scale results by the spread of the effect.
	r11.xy = r11.xy + (ANIMATION.xy * r0.xy);
	o.tc1 = r11.xy + UVFIX.xy;

	return o;
}


//--------------------------------------------------------------//
// Technique Section for standard
//--------------------------------------------------------------//
technique standard
<
	string label = "SHADER_MODEL_0";
>
{
	pass Pass_0
	{
		ALPHATESTENABLE = <alphaTestEnable>;
		ALPHAREF = <alphaReference>;
		SRCBLEND = <srcBlend>;
		DESTBLEND = <destBlend>;
		ZENABLE = FALSE;
		ALPHABLENDENABLE = TRUE;
		CULLMODE = NONE;
		LIGHTING = FALSE;
		FOGENABLE = FALSE;
		SPECULARENABLE = FALSE;
		
		Texture[0] = <inputTexture>;
		COLOROP[0] = SELECTARG1;
		COLORARG1[0] = TEXTURE;
		ALPHAOP[0] = ADD;
		ALPHAARG1[0] = DIFFUSE;
		ALPHAARG2[0] = TEXTURE;
		TEXCOORDINDEX[0] = 0;
		MAXMIPLEVEL[0] = 0;
		MIPMAPLODBIAS[0] = 0;
		
		Texture[1] = <inputTexture>;
		COLOROP[1] = BLENDCURRENTALPHA;
		COLORARG1[1] = TEXTURE;
		COLORARG2[1] = CURRENT;
		ALPHAOP[1] = DISABLE;
		TEXCOORDINDEX[1] = 1;
		MAXMIPLEVEL[1] = 0;
		MIPMAPLODBIAS[1] = 0;
		
		COLOROP[2] = DISABLE;
		ALPHAOP[2] = DISABLE;
		
		MAGFILTER[0] = POINT;
		MIPFILTER[0] = POINT;
		MINFILTER[0] = POINT;		
		ADDRESSU[0] = CLAMP;
		ADDRESSV[0] = CLAMP;
		ADDRESSW[0] = CLAMP;
		MAGFILTER[1] = LINEAR;
		MIPFILTER[1] = LINEAR;
		MINFILTER[1] = LINEAR;
		ADDRESSU[1] = MIRROR;
		ADDRESSV[1] = MIRROR;
		ADDRESSW[1] = MIRROR;
				
		VertexShader = compile vs_2_0 vs_main();
		PixelShader = NULL;
	}
}


//--------------------------------------------------------------//
// Technique Section for debug
//--------------------------------------------------------------//
technique debug
{
	pass Pass_0
	{
		ALPHATESTENABLE = <alphaTestEnable>;
		ALPHAREF = <alphaReference>;
		SRCBLEND = <srcBlend>;
		DESTBLEND = <destBlend>;
		ZENABLE = FALSE;
		ALPHABLENDENABLE = TRUE;
		CULLMODE = NONE;
		LIGHTING = FALSE;
		FOGENABLE = FALSE;
		SPECULARENABLE = FALSE;
		TEXTUREFACTOR = 0xFFFFFFFF;
		
		TEXTURE[0] = <inputTexture>;
		COLOROP[0] = SELECTARG1;
		COLORARG1[0] = TFACTOR | COMPLEMENT;
		ALPHAOP[0] = ADD;
		ALPHAARG1[0] = DIFFUSE;
		ALPHAARG2[0] = TEXTURE;
		
		TEXTURE[1] = <inputTexture>;
		COLOROP[1] = BLENDCURRENTALPHA;
		COLORARG1[1] = TFACTOR;
		COLORARG2[1] = CURRENT;
		ALPHAOP[1] = DISABLE;
		COLOROP[2] = DISABLE;
		
		MAGFILTER[0] = POINT;
		MIPFILTER[0] = POINT;
		MINFILTER[0] = POINT;		
		ADDRESSU[0] = CLAMP;
		ADDRESSV[0] = CLAMP;
		ADDRESSW[0] = CLAMP;
		MAGFILTER[1] = POINT;
		MIPFILTER[1] = POINT;
		MINFILTER[1] = POINT;
		ADDRESSU[1] = CLAMP;
		ADDRESSV[1] = CLAMP;
		ADDRESSW[1] = CLAMP;
				
		VertexShader = compile vs_1_1 vs_main();
		PixelShader = NULL;
	}
}
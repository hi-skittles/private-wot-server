#include "stdinclude.fxh"

// Exposed artist editable variables.
texture diffuseMap
< 
bool artistEditable = true; 
string UIName = "Diffuse Map";
string UIDesc = "The texture map to use for the heavenly body";
>;

// This constant is read by the tools to know if it should setup a rendering
// environment that is appropriate for a skybox.
bool isBWSkyBox = true;

// Auto Variables
float4x4 environmentTransform : EnvironmentTransform;
float4x4 world;
float3   color;
float    dist;

// Vertex Formats
struct OUTPUT
{
	float4 pos: POSITION;
	float2 tc0: TEXCOORD0;	
};

BW_ARTIST_EDITABLE_ADDRESS_MODE(BW_CLAMP)


OUTPUT vs_main( VertexXYZNUV input )
{
	OUTPUT o = (OUTPUT)0;

	float4 worldPos = normalize(mul(input.pos, world)) * dist;
	o.pos = mul(float4(worldPos.xyz, 1.0f), environmentTransform).xyzw;
	o.tc0 = input.tc;
	
	return o;
}

sampler diffuseSampler = sampler_state
{
	Texture = (diffuseMap);
	ADDRESSU = CLAMP;
	ADDRESSV = CLAMP;
	ADDRESSW = CLAMP;
	MAGFILTER = LINEAR;
	MINFILTER = LINEAR;
	MIPFILTER = LINEAR;
	MAXMIPLEVEL = 0;
	MIPMAPLODBIAS = 0;
};


float4 ps_main( OUTPUT i ) : COLOR0
{
	float4 diffuseMap = tex2D( diffuseSampler, i.tc0 );
	
	//TODO : fog colour

	float4 colour;
	colour.xyz = diffuseMap.xyz * color;	
	colour.w = diffuseMap.w;

	colour.xyz *= 1.0f + g_HDRParams.x;

	return colour;
}

technique pixelShader2_0
{
   pass Pass_0
   {
      ALPHATESTENABLE = TRUE;
      ALPHAREF = 1;
      ZENABLE = TRUE;
      SRCBLEND = SRCALPHA;
      DESTBLEND = ONE;
      ZWRITEENABLE = FALSE;
      ZFUNC = LESSEQUAL;
      FOGENABLE = FALSE;
      ALPHABLENDENABLE = TRUE;
      POINTSPRITEENABLE = FALSE;
      STENCILENABLE = FALSE;
	  CULLMODE = NONE;

      VertexShader = compile vs_2_0 vs_main();
      PixelShader = compile ps_2_0 ps_main();
   }
}

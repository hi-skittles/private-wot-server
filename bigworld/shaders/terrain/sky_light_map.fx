#include "stdinclude.fxh"

// variables
texture Cloud;
bool alphaTestEnable = false;
int alphaReference = 0;
float shadowIntensity = 0.25;
matrix lightMapProjection;

BW_NON_EDITABLE_ADDITIVE_BLEND

struct VS_INPUT
{
    float4 pos		: POSITION;
    float3 normal	: NORMAL;
    float2 tc		: TEXCOORD0;    
};

struct VS_OUTPUT
{
    float4 pos		: POSITION;
    float2 t0		: TEXCOORD0;
    float4 diffuse	: COLOR0;     
};

//----------------------------------------------------------------------------
// Shader body 
//----------------------------------------------------------------------------

VS_OUTPUT vs_main(const VS_INPUT v)
{
	VS_OUTPUT o = (VS_OUTPUT) 0;
	
	o.pos = mul( v.pos, lightMapProjection );	
	o.t0 = v.tc;
	o.diffuse.xyz = (1,1,1,1);
	
	return o;
};

sampler layer0Sampler = sampler_state
{
	Texture = (Cloud);
	ADDRESSU = CLAMP;
	ADDRESSV = CLAMP;
	ADDRESSW = CLAMP;
	MAGFILTER = LINEAR;
	MINFILTER = LINEAR;
	MIPFILTER = LINEAR;
	MAXMIPLEVEL = 0;
	MIPMAPLODBIAS = 0;
};

/**
 * This pixel shader outputs :
 * RGB	- none
 * A	- cloud density
 *
 * The resultant texture map will be used to light the
 * environment by modulating diffuse lighting with the
 * cloud density per-pixel.
 */
float4 ps_main( const VS_OUTPUT input ) : COLOR0
{	
	float4 layer0Map = tex2D( layer0Sampler, input.t0 );	
	float4 colour;
	colour.xyz = (0.0,0.0,0.0);
	colour.a = shadowIntensity * layer0Map.a;
	return colour;	
};

//--------------------------------------------------------------//
// Technique Sections for shader hardware
//--------------------------------------------------------------//
technique shader_version_2_0
{
	pass Pass_0
	{
		BW_BLENDING_ADD
		FOGENABLE = FALSE;
		SPECULARENABLE = TRUE;
		CULLMODE = NONE;
		ZENABLE = FALSE;
		COLORWRITEENABLE = RED | GREEN | BLUE | ALPHA;
		
		VertexShader = compile vs_2_0 vs_main();
		PixelShader = compile ps_2_0 ps_main();
	}
}

technique fixed_function
{
	pass Pass_0
	{
		BW_BLENDING_ADD
		FOGENABLE = FALSE;
		SPECULARENABLE = TRUE;
		CULLMODE = NONE;
		ZENABLE = FALSE;
		COLORWRITEENABLE = RED | GREEN | BLUE | ALPHA;
		WORLDTRANSFORM[0] = <lightMapProjection>;
		
		VertexShader = NULL;
		PixelShader = NULL;
	}
}

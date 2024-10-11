#include "stdinclude.fxh"

// variables
texture dappleMap 
< 
	bool artistEditable = true; 
	string UIName = "Dapple Map";
	string UIDesc = "The map providing dappled colour and shadow";
>;

texture dappleMask 
< 
	bool artistEditable = true; 
	string UIName = "Dapple Mask";
	string UIDesc = "The map that masks areas of dappled colour and shadow";
>;

float tile
< 
	bool artistEditable = true;
	string UIName = "Tile";
	string UIDesc = "The tiling factor for the dapple map";
	float UIMin = 0;
	float UIMax = 100;
	int UIDigits = 1;
> = 32.0;

float4x4 worldViewProj : WorldViewProjection;
bool alphaTestEnable = false;
int alphaReference = 255;
float fade = 0.f;

BW_NON_EDITABLE_ADDITIVE_BLEND

struct VS_INPUT
{
    float4 pos		: POSITION;    
    float2 tc		: TEXCOORD0;
};

struct VS_OUTPUT
{
    float4 pos		: POSITION;
    float2 skyLightMap : TEXCOORD0;
    float2 mapUV	: TEXCOORD1;    
    float4 diffuse	: COLOR0;     
};

//----------------------------------------------------------------------------
// Shader body 
//----------------------------------------------------------------------------

VS_OUTPUT vs_main(const VS_INPUT v)
{
	VS_OUTPUT o = (VS_OUTPUT) 0;
	
	o.pos = mul(v.pos, worldViewProj);	
	
	//float3 uvPos = float3(v.tc[0], 0.f, v.tc[1]);
	//BW_SKY_MAP_COORDS( o.skyLightMap, uvPos );
	o.skyLightMap[0] = v.tc[0];
	o.skyLightMap[1] = v.tc[1];
	o.mapUV = o.skyLightMap * (tile,tile);	
	
	return o;
};

sampler mapSampler = sampler_state
{
	Texture = (dappleMap);
	ADDRESSU = WRAP;
	ADDRESSV = WRAP;
	ADDRESSW = WRAP;
	MAGFILTER = LINEAR;
	MINFILTER = LINEAR;
	MIPFILTER = LINEAR;
	MAXMIPLEVEL = 0;
	MIPMAPLODBIAS = 0;
};

sampler maskSampler = sampler_state
{
	Texture = (dappleMask);
	ADDRESSU = WRAP;
	ADDRESSV = WRAP;
	ADDRESSW = WRAP;
	MAGFILTER = LINEAR;
	MINFILTER = LINEAR;
	MIPFILTER = LINEAR;
	MAXMIPLEVEL = 0;
	MIPMAPLODBIAS = 0;
};

/**
 * This pixel shader outputs :
 * RGB	- light intensity
 * A	- shadow density
 *
 * The resultant texture map will be used to light the
 * environment by modulating diffuse lighting with the
 * cloud density per-pixel.
 */
float4 ps_main( const VS_OUTPUT input ) : COLOR0
{	
	float4 dappleMap = tex2D( mapSampler, input.mapUV );
	float4 dappleMask = tex2D( maskSampler, input.skyLightMap );	
	return (dappleMap * dappleMask) * (1.0 - fade);	
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

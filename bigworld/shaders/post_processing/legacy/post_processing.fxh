#include "stdinclude.fxh"

//Currently - force all post processing shaders
//to have artist editable src/dest blend.
BW_ARTIST_EDITABLE_ALPHA_BLEND
BW_ARTIST_EDITABLE_ALPHA_TEST


struct VS_INPUT
{
   float4 pos:			POSITION; 
   float3 tc0:			TEXCOORD0;
   float3 tc1:			TEXCOORD1;
   float3 tc2:			TEXCOORD2;
   float3 tc3:			TEXCOORD3;
   float3 worldNormal:	TEXCOORD4;
   float3 viewNormal:	TEXCOORD5;
};


struct PS_INPUT
{
   float4 pos:			POSITION; 
   float3 tc0:			TEXCOORD0;
   float3 tc1:			TEXCOORD1;
   float3 tc2:			TEXCOORD2;
   float3 tc3:			TEXCOORD3;
   float3 worldNormal:	TEXCOORD4;
   float3 viewNormal:	TEXCOORD5;
};


PS_INPUT vs_pp_default( VS_INPUT input )
{
	PS_INPUT o = (PS_INPUT)0;
	o.pos = input.pos.xyww;
	o.tc0 = input.tc0;
	o.tc1 = input.tc1;
	o.tc2 = input.tc2;
	o.tc3 = input.tc3;
	o.worldNormal = input.worldNormal;
	o.viewNormal = input.viewNormal;
	return o;
}


#define DECLARE_EDITABLE_TEXTURE( mapName, samplerName, addressTypeU, addressTypeV, filterMode, desc )\
texture mapName\
<\
	bool artistEditable = true;\
	string UIDesc = desc " (you can drag a texture or render target from the Asset Browser)";\
>;\
sampler samplerName = sampler_state\
{\
	Texture = (mapName);\
	ADDRESSU = addressTypeU;\
	ADDRESSV = addressTypeV;\
	ADDRESSW = CLAMP;\
	MAGFILTER = filterMode;\
	MINFILTER = filterMode;\
	MIPFILTER = filterMode;\
	MAXANISOTROPY = 1;\
	MAXMIPLEVEL = 0;\
	MIPMAPLODBIAS = 0;\
};


#define DECLARE_ENVIRONMENT_CUBE_MAP( mapName, samplerName )\
texture mapName : EnvironmentCubeMap;\
sampler samplerName = sampler_state\
{\
	Texture = (mapName);\
	ADDRESSU = CLAMP;\
	ADDRESSV = CLAMP;\
	ADDRESSW = CLAMP;\
	MAGFILTER = LINEAR;\
	MINFILTER = LINEAR;\
	MIPFILTER = LINEAR;\
	MAXMIPLEVEL = 0;\
	MIPMAPLODBIAS = 0;\
};


#define STANDARD_PP_TECHNIQUE( vs, ps )\
technique PP_TECHNIQUE\
{\
   pass Pass_0\
   {\
      ALPHATESTENABLE = <alphaTestEnable>;\
      ALPHAREF = <alphaReference>;\
      SRCBLEND = <srcBlend>;\
      DESTBLEND = <destBlend>;\
      ZENABLE = FALSE;\
      FOGENABLE = FALSE;\
      ALPHABLENDENABLE = TRUE;\
      POINTSPRITEENABLE = FALSE;\
      STENCILENABLE = FALSE;\
      VertexShader = vs;\
      PixelShader = ps;\
   }\
}

#define STANDARD_PREVIEW_TECHNIQUE( vs, ps )\
technique Preview\
{\
   pass Pass_0\
   {\
      ALPHATESTENABLE = <alphaTestEnable>;\
      ALPHAREF = <alphaReference>;\
      SRCBLEND = <srcBlend>;\
      DESTBLEND = <destBlend>;\
      ZENABLE = FALSE;\
      FOGENABLE = FALSE;\
      ALPHABLENDENABLE = TRUE;\
      POINTSPRITEENABLE = FALSE;\
      STENCILENABLE = FALSE;\
      VertexShader = vs;\
      PixelShader = ps;\
   }\
}\

#include "depth_helpers.fxh"

#define USES_DEPTH_TEXTURE\
texture depthTex : DepthTex;\
sampler depthSampler = sampler_state\
{\
	Texture = (depthTex);\
	ADDRESSU = CLAMP;\
	ADDRESSV = CLAMP;\
	ADDRESSW = CLAMP;\
	MAGFILTER = POINT;\
	MINFILTER = POINT;\
	MIPFILTER = POINT;\
	MAXANISOTROPY = 1;\
	MAXMIPLEVEL = 0;\
	MIPMAPLODBIAS = 0;\
};\


float3 luminance( float3 input )
{
	return dot( input, float3(0.3,0.59,0.11) );
};

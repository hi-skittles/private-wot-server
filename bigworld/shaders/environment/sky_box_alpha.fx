#include "environment_helpers.fxh"

// Exposed artist editable variables.
BW_ARTIST_EDITABLE_CLOUD_MAP( diffuseMap, "Cloud Map" )
BW_ARTIST_EDITABLE_FOG_MAP( fogMap, "Fog Mask" )
BW_ARTIST_EDITABLE_YPARALLAX( parallax, "Vertical Parallax" )
BW_ARTIST_EDITABLE_SUNLIGHT_AMOUNT( lightAmount, "Sunlight Response" )
BW_ARTIST_EDITABLE_FOG_RESPONSE( fogResponse, "Fog Response" )
BW_CLOUD_MAP_SAMPLER( diffuseSampler, diffuseMap, CLAMP )
BW_FOG_MAP_SAMPLER( fogMapSampler, fogMap )
float4 control : SkyBoxController = {1,1,1,1};

float4x4 g_world : World;

// This constant is read by the tools to know if it should setup a rendering
// environment that is appropriate for a skybox.
bool isBWSkyBox = true;

struct Output
{
	float4 pos: POSITION;
	float2 tc0: TEXCOORD0;
	float2 tc1: TEXCOORD1;
	float4 col: COLOR0;
};


Output vs_main( VertexXYZNUV input )
{
	Output o = (Output)0;
	
	//adjust input y for parallax
	input.pos.y -= g_cameraPos.y * parallax;

	//-- ToDo: To be precise this division in not necessary, but because our artist already made
	//--		  skyboxes with that dimensions we have to normalize it back to identity.
	input.pos.xyz /= 25.0f;
	input.pos.xyz *= g_farPlane.x;
	
	o.pos = mul(float4(input.pos.xyz, 1.0f), g_world);
	o.pos = mul(o.pos, g_environmentMat).xyww;

	//-- to prevent numerical errors during rasterization.
	o.pos.z -= 0.0001f;

	o.tc0 = BW_UNPACK_TEXCOORD(input.tc);
	o.tc1 = BW_UNPACK_TEXCOORD(input.tc);	
	o.col = staticSkyBoxLighting(lightAmount);
	
	return o;
}


//blend between the skybox map and the fog colour based on the fog gradient map
float4 ps_main( Output i ) : COLOR0
{
	half4 diffuseMap = gamma2linear(tex2D(diffuseSampler, i.tc0));

	half4 fogAmount;
	half  fogFactor = control.x * fogResponse;

	if (g_fogParams.m_enabled)
		fogAmount = saturate(tex2D(fogMapSampler, i.tc1) + fogFactor);
	else
		fogAmount = half4(0,0,0,0);

	half4 colour;
	colour	    = i.col * diffuseMap;
	colour.rgb *= 1 + colour.a * g_HDRParams.x;
	colour.rgb  = lerp(colour.rgb, g_fogParams.m_color.rgb * g_HDRParams.w, fogAmount.xyz);

	return float4(colour.rgb, 1);
}

//occlusion test shader
float4 ps_occlusion( Output i ) : COLOR0
{
	float4 diffuseMap = tex2D( diffuseSampler, i.tc0 );	
	return diffuseMap;
}


//Since sky_box.fx is pixel shader 1.1 or Fixed Function only,
//it does not support sky shadowing.
float4 ps_shadow( Output i ) : COLOR0
{
	float4 colour = (0,0,0,0);
	return colour;	
}


PixelShader pixelShaders[3] = 
{
	compile ps_2_0 ps_main(),
	compile ps_2_0 ps_occlusion(),
	compile ps_2_0 ps_shadow()
};


//The pixel shader version turns off fogging with the engine.
technique pixelShader1_1
{
   pass Pass_0
   {
      ALPHATESTENABLE = (occlusionTest);      
      ALPHAREF = alphaReference();      
      ZENABLE = enableZ();
      SRCBLEND = SRCALPHA;
      DESTBLEND = INVSRCALPHA;
      ZWRITEENABLE = FALSE;
      ZFUNC = LESSEQUAL;
      FOGENABLE = FALSE;
      ALPHABLENDENABLE = TRUE;      
      POINTSPRITEENABLE = FALSE;
      STENCILENABLE = FALSE;
	  CULLMODE = NONE;

      VertexShader = compile vs_2_0 vs_main();
      PixelShader = (pixelShaders[pixelShaderIndex()]);
   }
}

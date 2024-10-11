#include "post_processing.fxh"

//-- params.

DECLARE_EDITABLE_TEXTURE( baseTexture, baseSampler, CLAMP, CLAMP, LINEAR,  "The main scene color texture/render target" )

const int g_stencilFunc
<
	bool artistEditable = true;
	string UIDesc = "ToDo:";
> = 2;

const bool g_useAlphaChannel
<
	bool artistEditable = true;
	string UIDesc = "ToDo:";
> = true;

//-------------------------------------------------------------------------------------------------
struct VertexXYZUV
{
   float4 pos: 	POSITION;
   float2 tc:	TEXCOORD0;
};

//-------------------------------------------------------------------------------------------------
struct VertexOut
{
	float4 pos:	POSITION;
	float2 tc: 	TEXCOORD0;
};

//-------------------------------------------------------------------------------------------------
VertexOut VS(VertexXYZUV i)
{
	VertexOut o = (VertexOut)0;
	o.pos = i.pos;
	o.tc  = i.tc;
	
	return o;
}

//-------------------------------------------------------------------------------------------------
float4 PS(VertexOut input) : COLOR0
{
	float4 color = tex2D( baseSampler, input.tc );
	if(g_useAlphaChannel)
	{
		if(color[3]>0.0f)
		{
			color *= color.a;
			color.a = 0.0f;
		}
		else
			color = float4(0,0,0,0);
	}
	return color;
}

//-------------------------------------------------------------------------------------------------
technique shaderTransfer
{
	pass Pass_0
	{
		ALPHABLENDENABLE = FALSE;
		ZENABLE = FALSE;
		ZWRITEENABLE = FALSE;
		CULLMODE = NONE;
		ALPHATESTENABLE = FALSE;
		CULLMODE = NONE;
		FOGENABLE = FALSE;
		
		COLORWRITEENABLE = RED | GREEN | BLUE | ALPHA;
		
		STENCILENABLE = TRUE;
		STENCILREF = 0;
		STENCILMASK = 0xFF;
		STENCILWRITEMASK = 0xFF;
		STENCILFUNC = <g_stencilFunc>;			
		STENCILPASS = KEEP;
		STENCILFAIL = KEEP;
		STENCILZFAIL = KEEP;


		VertexShader = compile vs_2_0 VS();
		PixelShader  = compile ps_2_0 PS();
	}
}
//--------------------------------------------------------------
// Declarations
//--------------------------------------------------------------

#define SAMPLE_COUNT 15

float2 sampleOffsets[SAMPLE_COUNT];
float  sampleWeights[SAMPLE_COUNT];
texture tBluredTexture;

sampler bluredTextureSampler = sampler_state
{
	Texture = <tBluredTexture>;
	MIPFILTER = LINEAR;
	MAGFILTER = LINEAR;
	MINFILTER = LINEAR;
	ADDRESSU = CLAMP;
	ADDRESSV = CLAMP;
};

struct VS_INPUT
{
	float4 pos : POSITION;
	float2 tex : TEXCOORD;
};

struct VS_OUTPUT
{
	float4 pos : POSITION;
	float2 tex : TEXCOORD;
};

//--------------------------------------------------------------
// Shaders code
//--------------------------------------------------------------

VS_OUTPUT vs_main(VS_INPUT i)
{
	VS_OUTPUT o = (VS_OUTPUT) 0;
	o.pos = i.pos;
	o.tex = i.tex;
	return o;
}

float4 ps_main(VS_OUTPUT input) : COLOR
{
	float res = 0.0f;
	for(int i = 0; i < SAMPLE_COUNT; ++i) {
		res += sampleWeights[i] * tex2D(bluredTextureSampler, input.tex + sampleOffsets[i]).r;
	}
	return res;
}

//--------------------------------------------------------------
// Technique Section for standard
//--------------------------------------------------------------

technique blur
{
	pass Pass_0
	{
		ALPHATESTENABLE = FALSE;
		ALPHABLENDENABLE = FALSE;

		ZENABLE = FALSE;
		ZWRITEENABLE = FALSE;
		ZFUNC = ALWAYS;

		CULLMODE = NONE;

		VertexShader = compile vs_2_0 vs_main();
		PixelShader = compile ps_2_0 ps_main();
	}
}

//--------------------------------------------------------------
// End
//--------------------------------------------------------------

////--------------------------------------------------------------
//// Declarations
////--------------------------------------------------------------
//
//float g_blureRadius = .0f;
//int g_samplesCount = 3;
//
//float g_texelTextureSize = 1.0f / 1536.0f;
//
//texture g_bluredTexture;
//bool g_isVerticalBlure;
//
////--------------------------------------------------------------
//
//sampler bluredTextureSampler = sampler_state
//{
	//Texture = <g_bluredTexture>;
	//MIPFILTER = LINEAR;
	//MAGFILTER = LINEAR;
	//MINFILTER = LINEAR;
	//ADDRESSU = CLAMP;
	//ADDRESSV = CLAMP;
//};
//
//struct VS_INPUT
//{
	//float4 pos : POSITION;
	//float2 tex : TEXCOORD;
//};
//
//struct PS_INPUT
//{
	//float4 pos : POSITION;
	//float2 tex : TEXCOORD;
//};
//
////--------------------------------------------------------------
//// Shaders code
////--------------------------------------------------------------
//
//PS_INPUT vs_main(VS_INPUT i)
//{
	//PS_INPUT o = (PS_INPUT) 0;
	//o.pos = i.pos;
	//o.tex = i.tex;
	//return o;
//}
//
//float4 ps_main(PS_INPUT i, uniform bool isVerticalBlure, uniform int samplesCount) : COLOR
//{
	//float ret = 0;
	//if(isVerticalBlure)
	//{
		//ret += tex2D(bluredTextureSampler, i.tex + float2(+ g_texelTextureSize * 3, 0.0f));
		//ret += tex2D(bluredTextureSampler, i.tex + float2(+ g_texelTextureSize * 2, 0.0f));
		//ret += tex2D(bluredTextureSampler, i.tex + float2(+ g_texelTextureSize * 1, 0.0f));
		//ret += tex2D(bluredTextureSampler, i.tex + float2(  g_texelTextureSize * 0, 0.0f));
		//ret += tex2D(bluredTextureSampler, i.tex + float2(- g_texelTextureSize * 1, 0.0f));
		//ret += tex2D(bluredTextureSampler, i.tex + float2(- g_texelTextureSize * 2, 0.0f));
		//ret += tex2D(bluredTextureSampler, i.tex + float2(- g_texelTextureSize * 3, 0.0f));
	//}
	//else 
	//{
		//ret += tex2D(bluredTextureSampler, i.tex + float2(0.0f, + g_texelTextureSize * 3));
		//ret += tex2D(bluredTextureSampler, i.tex + float2(0.0f, + g_texelTextureSize * 2));
		//ret += tex2D(bluredTextureSampler, i.tex + float2(0.0f, + g_texelTextureSize * 1));
		//ret += tex2D(bluredTextureSampler, i.tex + float2(0.0f,   g_texelTextureSize * 0));
		//ret += tex2D(bluredTextureSampler, i.tex + float2(0.0f, - g_texelTextureSize * 1));
		//ret += tex2D(bluredTextureSampler, i.tex + float2(0.0f, - g_texelTextureSize * 2));
		//ret += tex2D(bluredTextureSampler, i.tex + float2(0.0f, - g_texelTextureSize * 3));	
	//}
	//
	//return ret / 7.0f;
//}
//
////--------------------------------------------------------------
//// Technique Section for standard
////--------------------------------------------------------------
//
//PixelShader ps[8] = 
//{
	//// horiaontal
	//compile ps_3_0 ps_main(false, 1),
	//compile ps_3_0 ps_main(false, 3),
	//compile ps_3_0 ps_main(false, 5),
	//compile ps_3_0 ps_main(false, 7),
//
	////vertical
	//compile ps_3_0 ps_main(true, 1),
	//compile ps_3_0 ps_main(true, 3),
	//compile ps_3_0 ps_main(true, 5),
	//compile ps_3_0 ps_main(true, 7)
//};
//
//int selectPixelShader(int samplesCount, bool isVertical)
//{
	//return 4 * isVertical;
//}
//
//technique blur
//{
	//pass Pass_0
	//{
		//ALPHATESTENABLE = FALSE;
		//ALPHABLENDENABLE = FALSE;
//
		//ZENABLE = FALSE;
		//ZWRITEENABLE = FALSE;
		//ZFUNC = ALWAYS;
//
		//CULLMODE = NONE;
//
		//VertexShader = compile vs_3_0 vs_main();
		//PixelShader = ps[selectPixelShader(g_samplesCount, g_isVerticalBlure)];
	//}
//}
//
////--------------------------------------------------------------
//// End
////--------------------------------------------------------------
//
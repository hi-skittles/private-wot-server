/**
 *	This include file has all the material setup related functions, such as device states, texture stage states
 */

//--------------------------------------------------------------------------------------------------
#ifdef IN_GAME
#	define BW_CULL_DOUBLESIDED		CULLMODE = (doubleSided ? BW_CULL_NONE : BW_CULL_CCW);
#	define BW_SHADOW_CULL_MODE		CULLMODE = (doubleSided ? BW_CULL_NONE : BW_CULL_CW);
#else
#	define BW_CULL_DOUBLESIDED		CULLMODE = (doubleSided ? BW_CULL_NONE : BW_CULL_CW);
#	define BW_SHADOW_CULL_MODE		CULLMODE = (doubleSided ? BW_CULL_NONE : BW_CULL_CCW);
#endif

//--------------------------------------------------------------------------------------------------
#define BW_BLENDING_SOLID				\
	ALPHATESTENABLE		= FALSE;		\
	ALPHABLENDENABLE	= FALSE;		\
	ZWRITEENABLE		= TRUE;			\
	ZENABLE				= TRUE;			\
	ZFUNC				= LESSEQUAL;

//--------------------------------------------------------------------------------------------------
#define BW_ARTIST_EDITABLE_DIFFUSE_MAP\
	texture diffuseMap\
	<\
		bool artistEditable = true;\
		string UIName = "Diffuse Map";\
		string UIDesc = "The diffuse map for the material";\
	>;

//--------------------------------------------------------------------------------------------------
#define BW_ARTIST_EDITABLE_NORMAL_MAP\
	texture normalMap\
	<\
		bool artistEditable = true; \
		string UIName = "Normal Map";\
		string UIDesc = "The normal map for the material";\
	>;

//--------------------------------------------------------------------------------------------------
#define DECLARE_OTHER_MAP( mapName, samplerName, uiName, uiDesc )\
	texture mapName\
	<\
		bool artistEditable = true;\
		string UIName = uiName;\
		string UIDesc = uiDesc;\
	>;\
	sampler samplerName = BW_SAMPLER(mapName, <texAddressMode>)

//--------------------------------------------------------------------------------------------------
#define BW_ARTIST_EDITABLE_DIFFUSE_MAP2\
	texture diffuseMap2\
	<\
		bool artistEditable = true;\
		string UIName = "Diffuse Map2";\
		string UIDesc = "The diffuse map2 for the material (alpha for blend)";\
	>;

//--------------------------------------------------------------------------------------------------
#define BW_ARTIST_EDITABLE_GLOW_MAP\
	texture glowMap \
	<\
		bool artistEditable = true;\
		string UIName = "Glow Map";\
		string UIDesc = "The glow map for the material";\
	>;\
	bool USES_GLOW_MAP = true;\

//--------------------------------------------------------------------------------------------------
#define BW_ARTIST_EDITABLE_GLOW_FACTOR\
	float glowFactor\
	< \
		bool artistEditable = true; \
		string UIName = "Glow Factor";\
		string UIDesc = "The scalar factor to scale the glow map by";\
		float UIMin = 0;\
		float UIMax = 2;\
		int UIDigits = 1;\
	> = 0;

//--------------------------------------------------------------------------------------------------
#define BW_ARTIST_EDITABLE_SPEC_MAP\
	texture specularMap \
	<\
		bool artistEditable = true;\
		string UIName = "Specular Map";\
		string UIDesc = "The specular map for the material";\
	>;

//--------------------------------------------------------------------------------------------------
#define BW_ARTIST_EDITABLE_REFLECTION_MAP\
	texture reflectionMap\
	<\
		bool artistEditable = true;\
		string UIWidget = "CubeMap";\
		string UIName = "Reflection Cube Map";\
		string UIDesc = "The reflection map for the material";\
		string type = "Cube";\
	>;

//--------------------------------------------------------------------------------------------------
#define BW_ARTIST_EDITABLE_REFLECTION_AMOUNT\
	float reflectionAmount\
	< \
		bool artistEditable = true;\
		string UIName = "Reflection Amount";\
		string UIDesc = "A scaling factor for the reflection";\
		float UIMin = 0;\
		float UIMax = 2.0;\
		int UIDigits = 2;\
	> = 1.0;

//--------------------------------------------------------------------------------------------------
#define BW_ARTIST_EDITABLE_MATERIAL_SPECULAR\
	float4 materialSpecular\
	< \
		bool artistEditable = true;\
		string UIWidget = "Color"; \
		string UIName = "Specular Colour";\
		string UIDesc = "The specular colour for the material";\
		float UIMin = 0;\
		float UIMax = 2;\
		int UIDigits = 1;\
	> = {1,1,1,1};


//--------------------------------------------------------------------------------------------------
#define BW_ARTIST_EDITABLE_DOUBLE_SIDED\
	bool doubleSided\
	<\
		bool artistEditable = true;\
		string UIName = "Double Sided";\
		string UIDesc = "Whether the material is draw on both sides";\
	> = false;

//--------------------------------------------------------------------------------------------------
#ifdef MOD2X
#define BW_ARTIST_EDITABLE_MOD2X\
	float diffuseLightExtraModulation \
	< \
		bool artistEditable = true;\
		string UIName = "Diffuse Light Extra Modulation";\
		string UIDesc = "The diffuse light extra modulation factor"; \
		float UIMin = 0;\
		float UIMax = 2;\
		int UIDigits = 1;\
	> = 1.0;
#else
#define BW_ARTIST_EDITABLE_MOD2X\
	float diffuseLightExtraModulation = 0.0;
#endif

//--------------------------------------------------------------------------------------------------
#define BW_ARTIST_EDITABLE_ALPHA_TEST\
	bool alphaTestEnable < bool artistEditable = true;  string UIName = "Alpha Test";  string UIDesc = "Whether an alpha test should be performed"; > = false;\
	int alphaReference < bool artistEditable = true;  string UIName = "Alpha Reference";  string UIDesc = "The alpha value cut-off value"; \
	int UIMax = 255; int UIMin = 0; > = 0;

//--------------------------------------------------------------------------------------------------
#define BW_NON_EDITABLE_ALPHA_TEST\
	bool alphaTestEnable  = false;\
	int alphaReference = 0;

//--------------------------------------------------------------------------------------------------
#define BW_ARTIST_EDITABLE_ADDITIVE_BLEND\
	int srcBlend\
	<\
		bool artistEditable = true;\
		string UIName = "Source Blend";\
		string UIDesc = "D3D Source blend factor for blending with backbuffer";\
		string EnumType = "SRCBLEND";\
		int UIMin = 1;\
		int UIMax = 15;\
		int UIDigits = 2;\
	> = BW_BLEND_ONE;

//--------------------------------------------------------------------------------------------------
#define BW_ARTIST_EDITABLE_ALPHA_BLEND\
	int srcBlend\
	<\
		bool artistEditable = true;\
		string UIName = "Source Blend";\
		string UIDesc = "D3D Source blend factor for blending with backbuffer";\
		string EnumType = "SRCBLEND";\
		int UIMin = 1;\
		int UIMax = 15;\
		int UIDigits = 2;\
	> = BW_BLEND_SRCALPHA;\
	int destBlend\
	<\
		bool artistEditable = true;\
		string UIName = "Destination Blend";\
		string UIDesc = "D3D Destination blend factor for blending with backbuffer";\
		string EnumType = "DESTBLEND";\
		int UIMin = 1;\
		int UIMax = 15;\
		int UIDigits = 2;\
	> = BW_BLEND_INVSRCALPHA;

//--------------------------------------------------------------------------------------------------
#define BW_ARTIST_EDITABLE_TEXTURE_OP\
	int textureOperation\
	<\
		bool artistEditable = true;\
		string UIName = "Texture Operation";\
		string UIDesc = "D3D Texture Stage operation to use for blending the layer";\
		string EnumType = "TEXTUREOP";\
		int UIMin = 1;\
		int UIMax = 27;\
		int UIDigits = 2;\
	> = 18;

//--------------------------------------------------------------------------------------------------
#define BW_ARTIST_EDITABLE_ADDRESS_MODE( defaultMode )\
	int texAddressMode \
	<\
		bool artistEditable = true;\
		string UIName = "Texture Address Mode";\
		string UIDesc = "D3D Texture Adress Mode";\
		string EnumType = "TEXTUREADDRESS";\
		int UIMin = 1;\
		int UIMax = 5;\
		int UIDigits = 1;\
	> = defaultMode;

//--------------------------------------------------------------------------------------------------
#define BW_NON_EDITABLE_ADDRESS_MODE( defaultMode )\
	int texAddressMode = defaultMode;

//--------------------------------------------------------------------------------------------------
#define BW_TEX_ADDRESS_MODE <texAddressMode>

//--------------------------------------------------------------------------------------------------
#define BW_NON_EDITABLE_ADDITIVE_BLEND\
	const int srcBlend=BW_BLEND_ONE;

//--------------------------------------------------------------------------------------------------
#define BW_NON_EDITABLE_ALPHA_BLEND\
	const int srcBlend=BW_BLEND_SRCALPHA;\
	const int destBlend=BW_BLEND_INVSRCALPHA;

//--------------------------------------------------------------------------------------------------
#ifndef FORCE_ZWRITE_ENABLE
	#define ZWRITE_DISABLE ZWRITEENABLE = FALSE;
#else
	#define ZWRITE_DISABLE ZWRITEENABLE = TRUE;
#endif

//--------------------------------------------------------------------------------------------------
#define BW_BLENDING_ADD\
	ALPHATESTENABLE = <alphaTestEnable>;\
	ALPHAREF = <alphaReference>;\
	ALPHAFUNC = GREATER;\
	ALPHABLENDENABLE = TRUE;\
	SRCBLEND = <srcBlend>;\
	DESTBLEND = ONE;\
	ZENABLE = TRUE;\
	ZWRITE_DISABLE\
	ZFUNC = LESSEQUAL;

//--------------------------------------------------------------------------------------------------
#define BW_BLENDING_ALPHA\
	ALPHATESTENABLE = <alphaTestEnable>;\
	ALPHAREF = <alphaReference>;\
	ALPHAFUNC = GREATER;\
	ALPHABLENDENABLE = TRUE;\
	SRCBLEND = <srcBlend>;\
	DESTBLEND = <destBlend>;\
	ZENABLE = TRUE;\
	ZWRITE_DISABLE\
	ZFUNC = LESSEQUAL;

//--------------------------------------------------------------------------------------------------
#define BW_FOG\
	FOGENABLE = <g_fogParams.m_enabled>;\
	FOGSTART = 1.0;\
	FOGEND = 0.0;\
	FOGCOLOR = <g_fogParams.m_color>;\
	FOGTABLEMODE = NONE;\
	FOGVERTEXMODE = LINEAR;

//--------------------------------------------------------------------------------------------------
#define BW_FOG_ADD\
	FOGENABLE = TRUE;\
	FOGSTART = 1.0;\
	FOGEND = 0.0;\
	FOGCOLOR = float4(0,0,0,0);\
	FOGTABLEMODE = NONE;\
	FOGVERTEXMODE = LINEAR;

//-- ToDo (b_sviglo): reconsider fixed function macroses. Try to eliminate them.
//--------------------------------------------------------------------------------------------------
#define BW_TEXTURESTAGE_DIFFUSEONLY_NOLIGHT(stage, inTexture)\
COLOROP[stage] = 2;\
COLORARG1[stage] = TEXTURE;\
COLORARG2[stage] = DIFFUSE;\
ALPHAOP[stage] = SELECTARG1;\
ALPHAARG1[stage] = TEXTURE;\
ALPHAARG2[stage] = DIFFUSE;\
Texture[stage] = (inTexture);\
ADDRESSU[stage] = <texAddressMode>;\
ADDRESSV[stage] = <texAddressMode>;\
ADDRESSW[stage] = <texAddressMode>;\
MAGFILTER[stage] = LINEAR;\
MINFILTER[stage] = LINEAR;\
MIPFILTER[stage] = LINEAR;\
MAXMIPLEVEL[stage] = 0;\
MIPMAPLODBIAS[stage] = 0;\
TexCoordIndex[stage] = stage;

#ifdef MOD2X
#define BW_TEXTURESTAGE_DIFFUSEONLY(stage, inTexture)\
COLOROP[stage] = 5;\
COLORARG1[stage] = TEXTURE;\
COLORARG2[stage] = DIFFUSE;\
ALPHAOP[stage] = SELECTARG1;\
ALPHAARG1[stage] = TEXTURE;\
ALPHAARG2[stage] = DIFFUSE;\
Texture[stage] = (inTexture);\
ADDRESSU[stage] = <texAddressMode>;\
ADDRESSV[stage] = <texAddressMode>;\
ADDRESSW[stage] = <texAddressMode>;\
MAGFILTER[stage] = LINEAR;\
MINFILTER[stage] = LINEAR;\
MIPFILTER[stage] = LINEAR;\
MAXMIPLEVEL[stage] = 0;\
MIPMAPLODBIAS[stage] = 0;\
TexCoordIndex[stage] = stage;
#else
#define BW_TEXTURESTAGE_DIFFUSEONLY(stage, inTexture)\
COLOROP[stage] = 4;\
COLORARG1[stage] = TEXTURE;\
COLORARG2[stage] = DIFFUSE;\
ALPHAOP[stage] = SELECTARG1;\
ALPHAARG1[stage] = TEXTURE;\
ALPHAARG2[stage] = DIFFUSE;\
Texture[stage] = (inTexture);\
ADDRESSU[stage] = <texAddressMode>;\
ADDRESSV[stage] = <texAddressMode>;\
ADDRESSW[stage] = <texAddressMode>;\
MAGFILTER[stage] = LINEAR;\
MINFILTER[stage] = LINEAR;\
MIPFILTER[stage] = LINEAR;\
MAXMIPLEVEL[stage] = 0;\
MIPMAPLODBIAS[stage] = 0;\
TexCoordIndex[stage] = stage;
#endif

#ifdef MOD2X
#define BW_TEXTURESTAGE_DIFFUSEONLY_ALPHA(stage, inTexture)\
COLOROP[stage] = 5;\
COLORARG1[stage] = TEXTURE;\
COLORARG2[stage] = DIFFUSE;\
ALPHAOP[stage] = MODULATE;\
ALPHAARG1[stage] = TEXTURE;\
ALPHAARG2[stage] = DIFFUSE;\
Texture[stage] = (inTexture);\
ADDRESSU[stage] = <texAddressMode>;\
ADDRESSV[stage] = <texAddressMode>;\
ADDRESSW[stage] = <texAddressMode>;\
MAGFILTER[stage] = LINEAR;\
MINFILTER[stage] = LINEAR;\
MIPFILTER[stage] = LINEAR;\
MAXMIPLEVEL[stage] = 0;\
MIPMAPLODBIAS[stage] = 0;\
TexCoordIndex[stage] = stage;
#else
#define BW_TEXTURESTAGE_DIFFUSEONLY_ALPHA(stage, inTexture)\
COLOROP[stage] = 4;\
COLORARG1[stage] = TEXTURE;\
COLORARG2[stage] = DIFFUSE;\
ALPHAOP[stage] = MODULATE;\
ALPHAARG1[stage] = TEXTURE;\
ALPHAARG2[stage] = DIFFUSE;\
Texture[stage] = (inTexture);\
ADDRESSU[stage] = <texAddressMode>;\
ADDRESSV[stage] = <texAddressMode>;\
ADDRESSW[stage] = <texAddressMode>;\
MAGFILTER[stage] = LINEAR;\
MINFILTER[stage] = LINEAR;\
MIPFILTER[stage] = LINEAR;\
MAXMIPLEVEL[stage] = 0;\
MIPMAPLODBIAS[stage] = 0;\
TexCoordIndex[stage] = stage;
#endif

#define BW_TEXTURESTAGE_ADDTEXTUREMULALPHA(stage, inTexture)\
COLOROP[stage] = MODULATEALPHA_ADDCOLOR;\
COLORARG1[stage] = CURRENT;\
COLORARG2[stage] = TEXTURE;\
ALPHAOP[stage] = SELECTARG1;\
ALPHAARG1[stage] = CURRENT;\
ALPHAARG2[stage] = CURRENT;\
Texture[stage] = (inTexture);\
ADDRESSU[stage] = <texAddressMode>;\
ADDRESSV[stage] = <texAddressMode>;\
ADDRESSW[stage] = <texAddressMode>;\
MAGFILTER[stage] = LINEAR;\
MINFILTER[stage] = LINEAR;\
MIPFILTER[stage] = LINEAR;\
MAXMIPLEVEL[stage] = 0;\
MIPMAPLODBIAS[stage] = 0;\
TexCoordIndex[stage] = stage;

#define BW_TEXTURESTAGE_TEXTUREOP(stage, inTexture)\
COLOROP[stage] = <textureOperation>;\
COLORARG1[stage] = CURRENT;\
COLORARG2[stage] = TEXTURE;\
ALPHAOP[stage] = SELECTARG1;\
ALPHAARG1[stage] = CURRENT;\
ALPHAARG2[stage] = CURRENT;\
Texture[stage] = (inTexture);\
ADDRESSU[stage] = <texAddressMode>;\
ADDRESSV[stage] = <texAddressMode>;\
ADDRESSW[stage] = <texAddressMode>;\
MAGFILTER[stage] = LINEAR;\
MINFILTER[stage] = LINEAR;\
MIPFILTER[stage] = LINEAR;\
MAXMIPLEVEL[stage] = 0;\
MIPMAPLODBIAS[stage] = 0;\
TexCoordIndex[stage] = stage;

#define BW_TEXTURESTAGE_ALPHAONLY(stage, inTexture)\
COLOROP[stage] = SELECTARG1;\
COLORARG1[stage] = CURRENT;\
COLORARG2[stage] = CURRENT;\
ALPHAOP[stage] = SELECTARG1;\
ALPHAARG1[stage] = TEXTURE;\
ALPHAARG2[stage] = CURRENT;\
Texture[stage] = (inTexture);\
ADDRESSU[stage] = <texAddressMode>;\
ADDRESSV[stage] = <texAddressMode>;\
ADDRESSW[stage] = <texAddressMode>;\
MAGFILTER[stage] = LINEAR;\
MINFILTER[stage] = LINEAR;\
MIPFILTER[stage] = LINEAR;\
MAXMIPLEVEL[stage] = 0;\
MIPMAPLODBIAS[stage] = 0;\
TexCoordIndex[stage] = stage;


#define BW_TEXTURESTAGE_ADD(stage, inTexture)\
COLOROP[stage] = ADD;\
COLORARG1[stage] = CURRENT;\
COLORARG2[stage] = TEXTURE;\
ALPHAOP[stage] = SELECTARG1;\
ALPHAARG1[stage] = CURRENT;\
ALPHAARG2[stage] = TEXTURE;\
Texture[stage] = (inTexture);\
ADDRESSU[stage] = <texAddressMode>;\
ADDRESSV[stage] = <texAddressMode>;\
ADDRESSW[stage] = <texAddressMode>;\
MAGFILTER[stage] = LINEAR;\
MINFILTER[stage] = LINEAR;\
MIPFILTER[stage] = LINEAR;\
MAXMIPLEVEL[stage] = 0;\
MIPMAPLODBIAS[stage] = 0;\
TexCoordIndex[stage] = stage;

#define BW_TEXTURESTAGE_TERMINATE(stage)\
COLOROP[stage] = DISABLE;\
ALPHAOP[stage] = DISABLE;


//--------------------------------------------------------------//
// This pixel shader function attempts to simulate the Fixed
// function texture stage colour operation.
//--------------------------------------------------------------//
half3 bwTextureOp(int textureOperation, half3 currentColour, half currentAlpha, half4 diffuseMap, half4 otherMap)
{
/*		DISABLE,			1
		SELECTARG1,			2
		SELECTARG2,			3
		MODULATE,			4
		MODULATE2X,			5
		MODULATE4X,			6
		ADD,				7
		ADDSIGNED,
		ADDSIGNED2X,
		SUBTRACT,
		ADDSMOOTH,
		BLENDDIFFUSEALPHA,
		BLENDTEXTUREALPHA,
		BLENDFACTORALPHA,
		BLENDTEXTUREALPHAPM,
		BLENDCURRENTALPHA,
		PREMODULATE,
		MODULATEALPHA_ADDCOLOR,	18
		MODULATECOLOR_ADDALPHA,
		MODULATEINVALPHA_ADDCOLOR,
		MODULATEINVCOLOR_ADDALPHA,
		BUMPENVMAP,
		BUMPENVMAPLUMINANCE,
		DOTPRODUCT3,
		MULTIPLYADD,
		LERP,
		LAST_COLOROP = 0xFFFFFFFF	*/
	
	if (textureOperation == 18)
	{
		//MODULATE_ALPHA_ADD_COLOUR
		return currentColour + (currentAlpha * otherMap.xyz);
	}
	else if (textureOperation == 7)
	{
		//ADD
		return currentColour + otherMap.xyz;
	}
	else if (textureOperation == 4)
	{
		//MODULATE
		return currentColour * otherMap.xyz;
	}
	else if (textureOperation == 20)
	{
		//MODULATEINVALPHA_ADDCOLOR
		return currentColour + ((1.0 - currentAlpha) * otherMap.xyz);
	}
	else if (textureOperation == 2)
	{
		//SELECTARG1
		return currentColour;
	}
	else if (textureOperation == 3)
	{
		//SELECTARG2
		return otherMap.xyz;
	}		
	else if (textureOperation == 5)
	{
		//MODULATE2X
		return currentColour * otherMap.xyz * 2.0;
	}
	else if (textureOperation == 6)
	{
		//MODULATE4X
		return currentColour * otherMap.xyz * 4.0;
	}
	else	
	{
		//default to ADD
		//if you want to support more FF texture operations in
		//the pixel shader, then add them here.
		return currentColour + otherMap.xyz;
	}	
}

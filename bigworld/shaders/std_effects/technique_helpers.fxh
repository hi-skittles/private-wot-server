#ifndef TECHNIQUE_HELPERS_FXH
#define TECHNIQUE_HELPERS_FXH

//-- represents rendering pass types.
static const int G_RENDERING_PASS_COLOR			= 0;
static const int G_RENDERING_PASS_REFLECTION	= 1;
static const int G_RENDERING_PASS_SHADOWS		= 2;
static const int G_RENDERING_PASS_DEPTH			= 3;

//-- A null technique to remove shader cap warnings when a shader is tightly
//-- controlled by the application (not part of the std_effects set)
#define BW_NULL_TECHNIQUE \
technique null\
{\
   pass Pass_0\
   {\
      VertexShader = NULL;\
      PixelShader = NULL;\
   }\
}

//--------------------------------------------------------------------------------------------------
#if	DUAL_UV
	static const bool g_isDual = true;
#else
	static const bool g_isDual = false;
#endif

//--------------------------------------------------------------------------------------------------
#define _BW_COMMON_TECHNIQUE_(name, type, channelName, isBumped, isSkinned, isInstanced)\
	technique name <\
		bool	dualUV		= g_isDual;\
		string  channel		= channelName;\
		bool	bumpMapped	= isBumped;\
		bool	skinned		= isSkinned;\
		bool	instanced	= isInstanced;\
		int		renderType	= type;\
	>

//--------------------------------------------------------------------------------------------------
#define BW_COLOR_CHANNEL_TECHNIQUE(channelName, isBumped, isSkinned)\
	_BW_COMMON_TECHNIQUE_(COLOR, G_RENDERING_PASS_COLOR, channelName, isBumped, isSkinned, false)

//--------------------------------------------------------------------------------------------------
#define BW_COLOR_TECHNIQUE(isBumped, isSkinned)\
	_BW_COMMON_TECHNIQUE_(COLOR, G_RENDERING_PASS_COLOR, "none", isBumped, isSkinned, false)

//--------------------------------------------------------------------------------------------------
#define BW_COLOR_INSTANCED_TECHNIQUE(isBumped, isSkinned)\
	_BW_COMMON_TECHNIQUE_(COLOR_INSTANCED, G_RENDERING_PASS_COLOR, "none", isBumped, isSkinned, true)

//--------------------------------------------------------------------------------------------------
#define BW_REFLECTION_TECHNIQUE(isBumped, isSkinned)\
	_BW_COMMON_TECHNIQUE_(REFLECTION, G_RENDERING_PASS_REFLECTION, "none", isBumped, isSkinned, false)

//--------------------------------------------------------------------------------------------------
#define BW_REFLECTION_INSTANCED_TECHNIQUE(isBumped, isSkinned)\
	_BW_COMMON_TECHNIQUE_(REFLECTION_INSTANCED, G_RENDERING_PASS_REFLECTION, "none", isBumped, isSkinned, true)

//--------------------------------------------------------------------------------------------------
#define BW_SHADOW_TECHNIQUE(isSkinned)\
	_BW_COMMON_TECHNIQUE_(SHADOW, G_RENDERING_PASS_SHADOWS, "none", false, isSkinned, false)

//--------------------------------------------------------------------------------------------------
#define BW_SHADOW_INSTANCED_TECHNIQUE(isSkinned)\
	_BW_COMMON_TECHNIQUE_(SHADOW_INSTANCED, G_RENDERING_PASS_SHADOWS, "none", false, isSkinned, true)

//--------------------------------------------------------------------------------------------------
#define BW_DEPTH_TECHNIQUE(isSkinned)\
	_BW_COMMON_TECHNIQUE_(DEPTH, G_RENDERING_PASS_DEPTH, "none", false, isSkinned, false)

//--------------------------------------------------------------------------------------------------
#define BW_DEPTH_INSTANCED_TECHNIQUE(isSkinned)\
	_BW_COMMON_TECHNIQUE_(DEPTH_INSTANCED, G_RENDERING_PASS_DEPTH, "none", false, isSkinned, true)

#endif //-- TECHNIQUE_HELPERS_FXH
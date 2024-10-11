#ifndef STDINCLUDE_FXH
#define STDINCLUDE_FXH

//-- standard include file for .fx files contains most common code used in .fx pipeline
//-- Warning: Should be included file in all shaders.

//-- There is some description about widely used macroses:
//-- DUAL_UV				- means that vertex has two texture coordinates sets.
//-- NORMALMAP_ALPHA		- ToDo:
//-- NORMALMAP_TRASH		- ToDo:
//-- COLOURISE_DIFFUSE_MAP	- ToDo:
//-- ToDo: complete the list.
//--------------------------------------------------------------------------------------------------

//-- set of debug flags.
//#define BW_ENABLE_INSTANCING_VISUALIZATION 1

//-------------------------------------------------------------------------
// preset vertex packing rule sets. See vertex_formats.hpp
#define BW_GPU_VERTEX_PACKING_SET 1

#if BW_GPU_VERTEX_PACKING_SET == 1
	#define BW_GPU_VERTEX_PACKING_USE_VEC3_NORMAL_UBYTE4_8_8_8		1
	#define BW_GPU_VERTEX_PACKING_USE_VEC2_TEXCOORD_INT16_X2		1

#elif BW_GPU_VERTEX_PACKING_SET == 2
	#define BW_GPU_VERTEX_PACKING_USE_VEC3_NORMAL_FLOAT16_X4		1
	#define BW_GPU_VERTEX_PACKING_USE_VEC2_TEXCOORD_FLOAT16_X2		1

#else
	#error Selected vertex packing set unsupported

#endif	//-- BW_GPU_VERTEX_PACKING_SET
//-------------------------------------------------------------------------

//-- include shader constants.
#define PER_FRAME
#define PER_SCREEN
#define PER_VIEW
#include "shared_constants.fxh"

#include "d3d_state_mirror.fxh"
#include "lighting_helpers.fxh"
#include "vertex_declarations.fxh"
#include "material_helpers.fxh"
#include "fresnel_helpers.fxh"
#include "fog_helpers.fxh"
#include "technique_helpers.fxh"

//-- Warning: Should be in sync with IRendererPipeline.
static const int G_STENCIL_SYSTEM_WRITE_MASK	= 0xF0;
static const int G_STENCIL_CUMSTOM_WRITE_MASK	= 0x0F;

//-- represents pixels which are marked in the stencil buffer for DS.
//-- Warning: Should be in sync with IRendererPipeline::EStencilUsage
static const int G_STENCIL_USAGE_TERRAIN		= 0x10;
static const int G_STENCIL_USAGE_SPEEDTREE		= 0x20;
static const int G_STENCIL_USAGE_FLORA			= 0x40;
static const int G_STENCIL_USAGE_OTHER_OPAQUE	= 0x80;
static const int G_STENCIL_USAGE_ALL_OPAQUE		= 0xF0;

//-- represents object kind of the pixel.
static const int G_OBJECT_KIND_TERRAIN			= 1;
static const int G_OBJECT_KIND_FLORA			= 2;
static const int G_OBJECT_KIND_SPEEDTREE		= 3;
static const int G_OBJECT_KIND_STATIC			= 4;
static const int G_OBJECT_KIND_DYNAMIC			= 5;

#define BW_SAMPLER(map, addressType)\
sampler_state\
{\
	Texture = (map);\
	ADDRESSU = addressType;\
	ADDRESSV = addressType;\
	ADDRESSW = addressType;\
	MAGFILTER = LINEAR;\
	MINFILTER = (minMagFilter);\
	MIPFILTER = (mipFilter);\
	MAXANISOTROPY = (maxAnisotropy);\
	MAXMIPLEVEL = 0;\
	MIPMAPLODBIAS = 0;\
};

#endif //-- STDINCLUDE_FXH
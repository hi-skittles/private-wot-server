#ifndef _SHARED_CONSTANTS_FXH_
#define _SHARED_CONSTANTS_FXH_

//-- This header file containts the common and shared constant among all shaders in the engine.
//-- The shared contants are set only once per view or frame update and greatly reduce redutant
//-- state changes. To make effect pool technique work you have to include this file in every new
//-- create .fx file wihout any modification. Moreover you don't have to declare these constans
//-- youself in your shader. These variable names and semantics are reserved.

//-- avaliable mutators to correct create effect pool for every constants group.
//-- PER_FRAME
//-- PER_SCREEN
//-- PER_VIEW

//-- add to the shared constants specific meta-info.
#undef  BW_SHARED
#define BW_SHARED <bool isShared = true;>

//--------------------------------------------------------------------------------------------------

#define BW_DEFINE_TEX_AND_SAMPLER(name, semantic)	\
	shared texture name##Tex : semantic BW_SHARED;	\
	sampler name##Sml = sampler_state				\
	{												\
		Texture = (name##Tex);						\
		ADDRESSU = CLAMP;							\
		ADDRESSV = CLAMP;							\
		ADDRESSW = CLAMP;							\
		MAGFILTER = POINT;							\
		MINFILTER = POINT;							\
		MIPFILTER = POINT;							\
		MAXANISOTROPY = 1;							\
		MAXMIPLEVEL = 0;							\
		MIPMAPLODBIAS = 0;							\
	};

//--------------------------------------------------------------------------------------------------
struct SunLight
{
	float3 m_dir;
	float4 m_color; 
	float4 m_ambient;
};

//--------------------------------------------------------------------------------------------------
struct FogParams
{
	float  m_enabled;
	float  m_density;
	float  m_start;
	float  m_end;
	float4 m_color;
	float4 m_outerBB; //-- outer BB for space bound fog.
	float4 m_innerBB; //-- inner BB for space bound fog.
};

//-- per-frame constants
#ifdef PER_FRAME
	shared float		g_time					:	Time					BW_SHARED;
	//-- (separation, eye separation, convergence, stereoEnabled)
	shared float4		g_nvStereoParams		:	NvStereoParams			BW_SHARED = float4(0,0,0,0);
	shared texture		g_nvStereoParamsMap		:	NvStereoParamsMap		BW_SHARED;
	shared float4		g_debugVisualizer		:	DebugVisualizer			BW_SHARED = float4(1,1,1,1);
	//-- (windAnimX, windAnimZ, currentWindAverageX, currentWindAverageZ)
	shared float4		g_windAnimation			:	WindAnimation			BW_SHARED;
	shared int			mipFilter				:	MipFilter				BW_SHARED = 2;
	shared int			minMagFilter			:	MinMagFilter			BW_SHARED = 2;
	shared int			maxAnisotropy			:	MaxAnisotropy			BW_SHARED = 1;
	shared texture		g_envCubeMap			:	EnvironmentCubeMap		BW_SHARED;
	shared texture		g_noiseMap				:	NoiseMap				BW_SHARED;
	shared texture		g_bitwiseLUTMap			:	BitwiseLUTMap			BW_SHARED;
	shared texture		g_atan2LUTMap			:	Atan2LUTMap				BW_SHARED;
	shared texture		g_speedTreeMaterialsMap	:	SpeedTreeMaterials		BW_SHARED;
	shared SunLight		g_sunLight				:	SunLight				BW_SHARED;
	shared FogParams	g_fogParams				:	FogParams				BW_SHARED;
	shared float		g_sunVisibility			:	SunVisibility			BW_SHARED;
	//-- Warning: should be in sync with G_OBJECT_KIND_* in stdinclude.fxh
	//--		  xy - (ambient, (diffuse + specular))
	shared float4x4		g_SSAOParams			:	SSAOParams				BW_SHARED;
	//-- (skyLumMultiplier, sunLumMultiplier, ambientLumMultiplier, fogLumMultiplier)
	shared float4		g_HDRParams				:	HDRParams				BW_SHARED = float4(0,1,1,1);
	//-- (gamma, 1/gamma, unused, unused)
	shared float4		g_gammaCorrection		:	GammaCorrection			BW_SHARED = float4(1,1,0,0);
	
	//-- Shadows constants
	shared float4       g_shadowBlendParams     :   ShadowBlendParams		BW_SHARED;
	shared texture      g_ssShadowMap           :   ShadowScreenSpaceMap	BW_SHARED;

	shared float4		g_specularParams		:	SpecularParams			BW_SHARED;
	shared bool			g_enableShadows			:	IsShadowsEnabled		BW_SHARED;

	//-- define accessors to the g-buffer channels.
	BW_DEFINE_TEX_AND_SAMPLER(g_GBufferChannel0, GBufferChannel0)
	BW_DEFINE_TEX_AND_SAMPLER(g_GBufferChannel1, GBufferChannel1)
	BW_DEFINE_TEX_AND_SAMPLER(g_GBufferChannel2, GBufferChannel2)
#endif

//-- per-screen constants.
#ifdef PER_SCREEN
	shared float4		g_screen				:	Screen					BW_SHARED;
	shared float4		g_invScreen				:	InvScreen				BW_SHARED;
#endif

//-- per-view constants.
#ifdef PER_VIEW
	shared float4x4		g_viewMat				:	View					BW_SHARED;
	shared float4x4		g_invViewMat			:	InvView					BW_SHARED;
	shared float4x4		g_projMat				:	Projection				BW_SHARED;
	shared float4x4		g_viewProjMat			:	ViewProjection			BW_SHARED;
	shared float4x4		g_invViewProjMat		:	InvViewProjection		BW_SHARED;
	shared float4x4		g_lastViewProjMat		:	LastViewProjection		BW_SHARED;
	shared float4x4		g_environmentMat		:	EnvironmentTransform	BW_SHARED; 
	shared float4x4		g_cameraDirs			:	CameraDirs				BW_SHARED;
	shared float4		g_cameraPos				:	CameraPos				BW_SHARED; //-- xyz - cameraPos, w - zoomFactor
	shared float4		g_lodCameraPos			:	LodCameraPos			BW_SHARED; //-- xyz - lodCameraPos, w - lodZoomFactor
	shared float3		g_cameraDir				:	CameraDir				BW_SHARED;
	shared float4		g_farNearPlane			:	FarNearPlane			BW_SHARED; //-- (fp, 1.f/fp,    np,    1.f/np)
	shared float4		g_farPlane				:	FarPlane				BW_SHARED; //-- (fp, 1.f/fp, skyfp, 1.f/skyfp)
#endif

#undef BW_SHARED
#undef BW_DEFINE_TEX_AND_SAMPLER

#endif //-- _SHARED_CONSTANTS_FXH_
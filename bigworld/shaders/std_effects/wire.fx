#include "stdinclude.fxh"

float3 vDiffuse;
float4 vWind;

const float c_fSpecularPower = 20.0f;

//--------------------------------------------------------------------------------------------------
struct vertexInput 
{
	float3	vPosition				: POSITION0;
	float3	vU_Size_Wind			: TEXCOORD0;
	float3	vTangent				: NORMAL0;
//	float2	vWindParams				: TEXCOORD1;
} InputVertexDeclaration;

//--------------------------------------------------------------------------------------------------
struct vertexOutput 
{
	float4	vPosition				: POSITION0;
	float3	vTexCoord_Depth			: TEXCOORD0;
	float3	vToCamera				: TEXCOORD1;
	float3	vBinormal				: TEXCOORD2;
	float3	vTangent				: TEXCOORD3;
	float3	vNormal					: TEXCOORD4;
	float		fFog				: FOG;
};

//--------------------------------------------------------------------------------------------------
texture texNormalMap				: NormalMapTexture;
sampler smpNormalMap = sampler_state 
{
	texture = < texNormalMap >;
	AddressU = Clamp;
	AddressV = Clamp;
	MipFilter = Linear;
	MagFilter = Linear;
	MinFilter = Linear;
};

//--------------------------------------------------------------------------------------------------
vertexOutput WireVS( vertexInput input )
{
	vertexOutput result = (vertexOutput)0;

/*
	float3 vWorldPos = input.vPosition;

//	float2 vWind1 = vWind.xy;
//	float2 vWind2 = vWind.zw;
//	float fWindK = input.vU_Size_Wind.z;
//	float fWindOffset = 0;
//	vWorldPos.xz += lerp( vWind1, vWind2, fWindOffset ) * fWindK;

	float3 vTangent = normalize( input.vTangent );
	float3 vToCamera = vCameraPosition - vWorldPos;
	float3 vBinormal = normalize( cross( vTangent, vToCamera ) );

	vWorldPos += vBinormal * input.vU_Size_Wind.y;


	vToCamera = normalize( vCameraPosition - vWorldPos );

	result.vPosition = mul( float4( vWorldPos, 1 ), mViewProjection );

	result.vToCamera = -vToCamera;
	result.vNormal = normalize( cross( vBinormal, vTangent ) );
	result.vBinormal = vBinormal;
	result.vTangent = vTangent;

	result.vTexCoord_Depth.xy = float2( input.vU_Size_Wind.x, 0 );

	result.vTexCoord_Depth.z = 0;
	BW_DEPTH( result.vTexCoord_Depth.z, result.vPosition.z )

	result.fFog = bw_vertexFog( float4( vWorldPos, 0 ), result.vPosition.w, BW_EXT_FOG_PARAMS );
*/

	return result;
}

//--------------------------------------------------------------------------------------------------
float4 WirePS( vertexOutput input ) : COLOR
{
/*
	float3x3 m = float3x3( input.vBinormal, input.vTangent, input.vNormal );
	float3 vNormal = ( tex2D( smpNormalMap, input.vTexCoord_Depth.xy ) - 0.5f ) * 2;
	vNormal = mul( m, vNormal );

	float3 vHalfAngle = normalize( -vLightDir + input.vToCamera );
   	float fSpecular = saturate( dot( vHalfAngle, vNormal ) );
	fSpecular = pow( fSpecular, c_fSpecularPower );	

	float4 vResult;
	vResult.rgb = fSpecular * vDiffuse;
	vResult.a = 1;

	BW_FINAL_COLOUR( input.vTexCoord_Depth.z, vResult )
*/

	return float4(0,0,0,0);
}

technique Wire
{
	pass P0
	{          
		VertexShader = compile vs_2_0 WireVS();
		PixelShader = compile ps_2_0 WirePS();

		FogEnable = True;
		CullMode = None;

		ZEnable = True;
		ZWriteEnable = True;

		AlphaBlendEnable = False;
		AlphaTestEnable = False;
	}
}

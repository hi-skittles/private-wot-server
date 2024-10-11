#ifndef _BW_READ_G_BUFFER_FXH_
#define _BW_READ_G_BUFFER_FXH_

#include "deferred_shading.fxh"
#include "nv_stereo.fxh"

//-- reconstruct world space position from the depths texture for desired screen space position.
//--------------------------------------------------------------------------------------------------
float3 g_buffer_readWorldPos(in float2 uv, bool stereoEnabled = false)
{
	//-- TODO: We can create special optimized version of this function for fxQuad rendering.
	//--       We have to pass the camera dirs as a params of fxQuad vertices.

#if 1

	// lt - 0  rt - 2
	// lb - 1  rb - 3
	
	float z = unpackFloatFromVec3(tex2D(g_GBufferChannel0Sml, uv).rgb) * g_farPlane.x;

	//-- correct uv coordinates for stereo.
	if (stereoEnabled)
	{
		uv = stereoToMonoUV(uv, z);
	}
	
	float3 dir_l = lerp(g_cameraDirs[0], g_cameraDirs[1], uv.y).xyz;
	float3 dir_r = lerp(g_cameraDirs[2], g_cameraDirs[3], uv.y).xyz;
	
	float3 dir = lerp(dir_l, dir_r, uv.x);
	
	return g_cameraPos.xyz + dir * z;

#else

	//-- TODO: Another way to restore world z using g_invViewProjMat.

	float z = unpackFloatFromVec3(tex2D(g_GBufferChannel0Sml, uv).rgb) * g_farPlane.x;

	float zf = g_farPlane.x;
	float zn = g_farNearPlane.z;

	float z_div_w = zf * (z - zn) / z * (zf - zn);

	float4 pos = float4(
		+2.0f * uv.x  - 1.0f,
		-2.0f * uv.y  + 1.0f,
		z_div_w,
		1.0f
	);

	pos = mul(pos, g_invViewProjMat);
	pos.xyz /= pos.w;

	return pos.xyz;

#endif
}

//-- read normalized liner z value from g-buffer.
//--     0.f - corresponds to the camera position point (not a near plane)
//--     1.f - corresponds to the far plane
//-- read liner z value from g-buffer.
//--------------------------------------------------------------------------------------------------
float g_buffer_readLinearZ(in float2 uv)
{
	return unpackFloatFromVec3(tex2D(g_GBufferChannel0Sml, uv).rgb);
}

//-- reconstruct world space normal from the normals texture for desired screen space position.
//--------------------------------------------------------------------------------------------------
half3 g_buffer_readWorldNormal(in float2 uv)
{
	half2 enc = tex2D(g_GBufferChannel1Sml, uv).rg;
    return sphericalToCartesian(enc);
}

//--------------------------------------------------------------------------------------------------
half3 g_buffer_readAlbedo(in float2 uv)
{
	return tex2D(g_GBufferChannel2Sml, uv).rgb;
}

//-- read material kind of the pixel. We have up to 256 different materials.
//--------------------------------------------------------------------------------------------------
half g_buffer_readObjectKind(in float2 uv)
{
	return tex2D(g_GBufferChannel0Sml, uv).a * 255;
}

//-- ToDo: reconsider. I hope compiler will be much enough smart to don't do additional texture sampling.
//--------------------------------------------------------------------------------------------------
half g_buffer_readSpecAmount(in float2 uv)
{
	return tex2D(g_GBufferChannel1Sml, uv).b;
}

//-- read material id #1. May be used differently for different sub-systems. See SpeedTree sub-system
//-- for example.
//--------------------------------------------------------------------------------------------------
half g_buffer_readUserData1(in float2 uv, uniform const bool isPacked = true)
{
	half ret = 0.f;

	//-- Note: compile-time branching.
	if (isPacked)
	{
		ret = tex2D(g_GBufferChannel2Sml, uv).a * 255;
	}
	else
	{
		ret = tex2D(g_GBufferChannel2Sml, uv).a;
	}
	return ret;
}

//-- read material id #2. May be used differently for different sub-systems. See SpeedTree sub-system
//-- for example.
//--------------------------------------------------------------------------------------------------
half g_buffer_readUserData2(in float2 uv, uniform const bool isPacked = true)
{
	half ret = 0.f;

	//-- Note: compile-time branching.
	if (isPacked)
	{
		ret = tex2D(g_GBufferChannel1Sml, uv).a * 255;
	}
	else
	{
		ret = tex2D(g_GBufferChannel1Sml, uv).a;
	}
	return ret;
}

#endif //-- _BW_READ_G_BUFFER_FXH_
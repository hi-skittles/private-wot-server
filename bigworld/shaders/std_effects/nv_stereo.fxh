#ifndef _BW_NV_STEREO_FXH_
#define _BW_NV_STEREO_FXH_

//--------------------------------------------------------------------------------------------------
sampler g_nvStereoParamsMapSpl = sampler_state
{
	Texture = <g_nvStereoParamsMap>;
	MipFilter = POINT;
	MinFilter = POINT;
	MagFilter = POINT;
};

//-- transform coordinates from stereo clip space to mono clip space.
//--------------------------------------------------------------------------------------------------
float4 stereoToMonoCPOS(float4 cposStereo)
{
    float2 stereoParam = float2(0,0);
	stereoParam.x = tex2Dlod(g_nvStereoParamsMapSpl, float4(0.000, 0, 0, 0)).x;
	stereoParam.y =	tex2Dlod(g_nvStereoParamsMapSpl, float4(0.125, 0, 0, 0)).x;

    float4 cposMono = cposStereo;
    cposMono.x = cposStereo.x + stereoParam.x * cposStereo.w + stereoParam.y;
    return cposMono;
}

//-- transform coordinates from mono clip space to stereo clip space.
//--------------------------------------------------------------------------------------------------
float4 monoToStereoCPOS(float4 cposMono)
{
	float2 stereoParam = float2(0,0);
	stereoParam.x = tex2Dlod(g_nvStereoParamsMapSpl, float4(0.000, 0, 0, 0)).x;
	stereoParam.y =	tex2Dlod(g_nvStereoParamsMapSpl, float4(0.125, 0, 0, 0)).x;

	float4 cposStereo = cposMono;
	cposStereo.x = cposMono.x - stereoParam.x * cposStereo.w - stereoParam.y;
	return cposStereo;
}

//-- same as stereoToMonoCPOS but stereo position is in the normalized clip space. I.e. after
//-- perspective division.
//--------------------------------------------------------------------------------------------------
float4 stereoToMonoNPOS(float4 nposStereo, float wClip)
{
	float2 stereoParam = float2(0,0);
	stereoParam.x = tex2Dlod(g_nvStereoParamsMapSpl, float4(0.000, 0, 0, 0)).x;
	stereoParam.y =	tex2Dlod(g_nvStereoParamsMapSpl, float4(0.125, 0, 0, 0)).x;

    float4 nposMono = nposStereo;
    nposMono.x = nposStereo.x + stereoParam.x + stereoParam.y / wClip;
    return nposMono;
}

//-- same as monoToStereoCPOS but mono position is in the normalized clip space. I.e. after
//-- perspective division.
//--------------------------------------------------------------------------------------------------
float4 monoToStereoNPOS(float4 nposMono, float wClip)
{
	float2 stereoParam = float2(0,0);
	stereoParam.x = tex2Dlod(g_nvStereoParamsMapSpl, float4(0.000, 0, 0, 0)).x;
	stereoParam.y =	tex2Dlod(g_nvStereoParamsMapSpl, float4(0.125, 0, 0, 0)).x;

    float4 nposStereo = nposMono;
    nposStereo.x = nposMono.x - stereoParam.x - stereoParam.y / wClip;
    return nposMono;
}

//-- transform uv coordinates (texture space) from stereo clip space to mono clip space.
//--------------------------------------------------------------------------------------------------
float2 stereoToMonoUV(float2 stereoUV, float wClip)
{
	//--
	float2 stereoParam = float2(0,0);
	stereoParam.x = tex2Dlod(g_nvStereoParamsMapSpl, float4(0.000, 0, 0, 0)).x;
	stereoParam.y =	tex2Dlod(g_nvStereoParamsMapSpl, float4(0.125, 0, 0, 0)).x;

	float2 monoUV		= stereoUV;
	float  stereoOffset = stereoParam.x + stereoParam.y / wClip;

	//-- stereoUV.x to clip space + stereo offset.
	monoUV.x = (2.0f * stereoUV.x - 1.0f) + stereoOffset;
	//-- monoUV back to texture space.
	monoUV.x = monoUV.x * 0.5f + 0.5f;

	return monoUV;
}

//-- Returns eye type as float value either -1 or +1.
//-- -1 - left eye
//-- +1 - right eye
//--  0 - stereo disabled.
//--------------------------------------------------------------------------------------------------
half stereoEye()
{
	return tex2Dlod(g_nvStereoParamsMapSpl, half4(0.250, 0, 0, 0)).x;
}

#endif //-- _BW_NV_STEREO_FXH_
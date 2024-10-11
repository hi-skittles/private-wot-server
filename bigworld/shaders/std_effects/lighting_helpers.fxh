#ifndef LIGHTING_HELPERS_FXH
#define LIGHTING_HELPERS_FXH

#pragma warning( disable : 3205 )

//--------------------------------------------------------------------------------------------------
struct DirectionalLight
{
	float3 direction;
	float4 colour;
};

//--------------------------------------------------------------------------------------------------
struct PointLight
{
	float4 position;	//-- xyz
	float4 colour;		//-- xyzw
	float4 attenuation;	//-- xy
	float4 padding;		//-- padding
};

//--------------------------------------------------------------------------------------------------
struct SpotLight
{
	float4 position;	//-- xyz
	float4 colour;		//-- xyzw
	float4 attenuation;	//-- xyz
	float4 direction;	//-- xyz
};

//--------------------------------------------------------------------------------------------------
half3 gamma2linear(const half3 gammaSpaceColor)
{
#if 0
	return pow(gammaSpaceColor, (half3)g_gammaCorrection.xxx);
#else
	//-- use much cheaper approximation (2.0 gamma instead of 2.2)
	if (g_gammaCorrection.x > 1)
	{
		return gammaSpaceColor * gammaSpaceColor;
	}
	else
	{
		return gammaSpaceColor;
	}
#endif
}

//--------------------------------------------------------------------------------------------------
half4 gamma2linear(const half4 gammaSpaceColorWithAlpha)
{
	return half4(gamma2linear(gammaSpaceColorWithAlpha.rgb), gammaSpaceColorWithAlpha.a);
}

//--------------------------------------------------------------------------------------------------
half3 linear2gamma(const half3 linearSpaceColor)
{
#if 0
	return pow(linearSpaceColor, (half3)g_gammaCorrection.yyy);
#else
	//-- use much cheaper approximation (2.0 gamma instead of 2.2)
	if (g_gammaCorrection.x > 1)
	{
		return sqrt(linearSpaceColor);
	}
	else
	{
		return linearSpaceColor;
	}
#endif
}

//--------------------------------------------------------------------------------------------------
half4 linear2gamma(const half4 linearSpaceColorWithAlpha)
{
	return half4(linear2gamma(linearSpaceColorWithAlpha.rgb), linearSpaceColorWithAlpha.a);
}
 
//--------------------------------------------------------------------------------------------------
half luminance(half3 i)
{
	return dot(i, half3(0.2125, 0.7154, 0.0721));
}

//--------------------------------------------------------------------------------------------------
float3 normalisedEyeVector( in float3 pos, in float3 cameraPos )
{
	return normalize(cameraPos - pos);
}

//--------------------------------------------------------------------------------------------------
half3 sunAmbientTerm()
{
	return (half3)g_sunLight.m_ambient * g_debugVisualizer.x * g_HDRParams.z;
}

//--------------------------------------------------------------------------------------------------
half3 sunDiffuseTerm(in half3 worldNormal, in half lightAdjust = 0)
{
	half NdotL = dot(-(half3)g_sunLight.m_dir.xyz, worldNormal);
	NdotL	   = lerp(lightAdjust, 1, saturate(NdotL));

	return NdotL * (half3)g_sunLight.m_color.rgb * (half)g_HDRParams.y * (half)g_debugVisualizer.y;
}

//--------------------------------------------------------------------------------------------------
half3 sunSpecTerm(in half3 worldNormal, in half3 eye, in half power = 32)
{
	half facing = dot(-(half3)g_sunLight.m_dir.xyz, worldNormal) > 0;
	half3 h     = normalize(eye - (half3)g_sunLight.m_dir.xyz);
	half  att   = saturate(dot(worldNormal, h));
	att         = pow(att, power);

	return att * facing * (half3)g_sunLight.m_color.rgb * (half)g_HDRParams.y * (half)g_debugVisualizer.z;
}

//--------------------------------------------------------------------------------------------------
half3 pointLight(in float3 position, in half3 normal, in PointLight light)
{
	half3 lDir		= normalize( light.position.xyz - position );
	half  distance	= dot( light.position.xyz - position, lDir );
	half2 att		= { (-distance + light.attenuation.x) * light.attenuation.y, dot(lDir, normal) };
	att = saturate(att);

	return att.x * att.y * (half3)light.colour.rgb;
}

//--------------------------------------------------------------------------------------------------
half3 pointSpecLight(in float3 position, in half3 normal, in half3 eye, in PointLight light, in half power = 32)
{
	half3 lightDir = light.position.xyz - position;
	half  lightLen = length(lightDir);
	lightDir /= lightLen;

	half3 h   = normalize(eye + lightDir);
	half  att = saturate(dot(normal, h));
	att = pow(att,power);

	return saturate((-lightLen + light.attenuation.x) * light.attenuation.y) * att * (half3)light.colour.rgb;
	
}

//--------------------------------------------------------------------------------------------------
half3 spotLight(in float3 position, in half3 normal, in SpotLight light)
{
	half3 lDir	   = normalize(light.position.xyz - position);
	half  distance = dot(light.position.xyz - position, lDir);
	
	half3 att = {
		(-distance + light.attenuation.x) * light.attenuation.y, 
		dot( -light.direction.xyz, normal ),  
		(dot( -light.direction.xyz, lDir ) -light.attenuation.z) / (1 - light.attenuation.z)
	};
	att = saturate(att);

	return att.x * att.y * att.z * (half3)light.colour.rgb;
}

//--------------------------------------------------------------------------------------------------
void spotSpecLight(in float3 position, in half3 normal, in half3 eye, in SpotLight light, out half3 diffuse, out half3 spec)
{
	half3 lDir		= normalize(light.position.xyz - position);
	half  distance	= dot(light.position.xyz - position, lDir);
	half3 h		 	= normalize(eye + lDir);
	
	half4 att = {
		(-distance + light.attenuation.x) * light.attenuation.y, 
		dot( -light.direction.xyz, normal ),  
		(dot( -light.direction.xyz, lDir ) -light.attenuation.z) / (1 - light.attenuation.z),
		dot(normal, h)
	};

	att = saturate(att);
	
	diffuse = (att.x * att.y * att.z * (half3)light.colour.xyz);	
	
	spec = att.x * att.z * pow(att.w, 32) * (half3)light.colour.rgb;	
}

#endif  //LIGHTING_HELPERS_FXH

/**
 *	This file contains all the helpers for doing fresnel calculations.
 */

//Fresnel term calculation:
#define BW_ARTIST_EDITABLE_FRESNEL\
float fresnelExp\
<\
	bool artistEditable = true;\
	string UIName = "Fresnel falloff";\
	string UIDesc = "Fresnel term edging";\
	float UIMin = 1.0;\
	float UIMax = 7.0;\
	int UIDigits = 2;\
> = 5.0;\
\
float fresnelConstant\
<\
	bool artistEditable = true;\
	string UIName = "Fresnel constant";\
	string UIDesc = "Fresnel constant";\
	float UIMin = 0;\
	float UIMax = 0.5;\
	int UIDigits = 4;\
> = 0.5;

#define BW_FRESNEL\
float fresnelExp = 5.0;\
float fresnelConstant = 0.3;

// Calculates fresnel term, assumes constant is 0. Useful as it has two
// less instructions than constant function.
float fresnelNoConstant( float3 vec, float3 normal, float exponent )
{
	float edotn = abs(dot(vec, normal));
	return pow(1.0-edotn, exponent);
}

// Calculates the fresnel term. Assumes the input is normalized.
float fresnel( float3 vec, float3 normal, float exponent, float constant )
{
	float f = fresnelNoConstant( vec, normal, exponent );
	return (constant + ( 1.0-constant) * f );
}
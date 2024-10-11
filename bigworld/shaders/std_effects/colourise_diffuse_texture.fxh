#ifndef COLOURISE_DIFFUSE_TEXTURE_H
#define COLOURISE_DIFFUSE_TEXTURE_H

float4 colorTint1
<
	bool artistEditable = true;
	string UIName = "Tint Color #1";
	string UIWidget = "Color";
	float UIMin = -2;
	float UIMax = 2;
	int UIDigits = 1;
> = {0, 0, 0, 0};

float4 colorTint2
<
	bool artistEditable = true;
	string UIName = "Tint Color #2";
	string UIWidget = "Color";
	float UIMin = -2;
	float UIMax = 2;
	int UIDigits = 1;
> = {0, 0, 0, 0};

float4 colorTint3
<
	bool artistEditable = true;
	string UIName = "Tint Color #3";
	string UIWidget = "Color";
	float UIMin = -2;
	float UIMax = 2;
	int UIDigits = 1;
> = {0, 0, 0, 0};

float4 colorTint4
<
	bool artistEditable = true;
	string UIName = "Tint Color #4";
	string UIWidget = "Color";
	float UIMin = -2;
	float UIMax = 2;
	int UIDigits = 1;
> = {0, 0, 0, 0};

float4 tintTiling
<
	bool artistEditable = true;
	string UIName = "Tint Mask Tiling";
	int UIDigits = 1;
> = { 1, 1, 0, 0 };

float4 tintEnabling
<
	bool artistEditable = true;
	string UIName = "Tint channels enabling";
	float UIMin = 0;
	float UIMax = 1;
	int UIDigits = 0;
> = { 1, 1, 1, 1 };

DECLARE_OTHER_MAP(tintMap, tintMapSampler, "Tint Map", "")
DECLARE_OTHER_MAP(exclusionMap, exclusionMapSampler, "Exclusion Map", "")

half4 colouriseDiffuseTex(half4 color, float2 uv)
{
	half4 tintMask = tex2D(tintMapSampler, uv * tintTiling.xy + tintTiling.zw);
	tintMask *= tintEnabling;

	half3 rgb = color.rgb;
	rgb = lerp(rgb, colorTint1.rgb, tintMask.r);
	rgb = lerp(rgb, colorTint2.rgb, tintMask.g);
	rgb = lerp(rgb, colorTint3.rgb, tintMask.b);
	rgb = lerp(rgb, colorTint4.rgb, tintMask.a);

	half4 exclusionMask = tex2D(exclusionMapSampler, uv);
	rgb = lerp(color.rgb, rgb, exclusionMask.r);

	return half4(rgb, color.w);
}

#endif // COLOURISE_DIFFUSE_TEXTURE_H

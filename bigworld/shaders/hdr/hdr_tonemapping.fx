#include "stdinclude.fxh"
#include "deferred_shading.fxh"

//-- params.
texture		 g_avgLumMap;
texture		 g_HDRMap;
texture		 g_bloomMap;
const float4 g_bloomParams;   //-- x - enabled/disabled, y - bloom factor.
const float4 g_params;		  //-- x - middle gray, y - white point.

//-------------------------------------------------------------------------------------------------
sampler g_avgLumMapSampler = sampler_state
{
	Texture 		= (g_avgLumMap);
	ADDRESSU 		= CLAMP;
	ADDRESSV 		= CLAMP;
	ADDRESSW 		= CLAMP;
	MAGFILTER 		= POINT;
	MINFILTER 		= POINT;
	MIPFILTER 		= POINT;
	MAXMIPLEVEL 	= 0;
	MIPMAPLODBIAS 	= 0;
};

//-------------------------------------------------------------------------------------------------
sampler g_bloomMapSampler = sampler_state
{
	Texture 		= (g_bloomMap);
	ADDRESSU 		= CLAMP;
	ADDRESSV 		= CLAMP;
	ADDRESSW 		= CLAMP;
	MAGFILTER 		= LINEAR;
	MINFILTER 		= LINEAR;
	MIPFILTER 		= LINEAR;
	MAXMIPLEVEL 	= 0;
	MIPMAPLODBIAS 	= 0;
};

//-------------------------------------------------------------------------------------------------
sampler g_HDRMapSampler = sampler_state
{
	Texture 		= (g_HDRMap);
	ADDRESSU 		= CLAMP;
	ADDRESSV 		= CLAMP;
	ADDRESSW 		= CLAMP;
	MAGFILTER 		= POINT;
	MINFILTER 		= POINT;
	MIPFILTER 		= POINT;
	MAXMIPLEVEL 	= 0;
	MIPMAPLODBIAS 	= 0;
};

//-------------------------------------------------------------------------------------------------
struct VertexXYZUV
{
   float4 pos: 	POSITION;
   float2 tc:	TEXCOORD0;
};

//-------------------------------------------------------------------------------------------------
struct VertexOut
{
	float4 pos:	POSITION;
	float2 tc: 	TEXCOORD0;
};

//-------------------------------------------------------------------------------------------------
float3 RGB2XYZ(in float3 rgb)
{
	// RGB -> XYZ conversion
	const float3x3 RGB2XYZ_mat = {
		0.5141364, 0.3238786,  0.16036376,
		0.265068,  0.67023428, 0.06409157,
		0.0241188, 0.1228178,  0.84442666
	};  

	float3 XYZ = mul(RGB2XYZ_mat, rgb);
  
	// XYZ -> Yxy conversion
	float3 Yxy;
	Yxy.r = XYZ.g;                            // copy luminance Y
	Yxy.g = XYZ.r / (XYZ.r + XYZ.g + XYZ.b ); // x = X / (X + Y + Z)
	Yxy.b = XYZ.g / (XYZ.r + XYZ.g + XYZ.b ); // y = Y / (X + Y + Z)

	return Yxy;
}

//-------------------------------------------------------------------------------------------------
float3 XYZ2RGB(in float3 Yxy)
{
	float3 XYZ;

	// Yxy -> XYZ conversion
	XYZ.r = Yxy.r * Yxy.g / Yxy. b;               // X = Y * x / y
	XYZ.g = Yxy.r;                                // copy luminance Y
	XYZ.b = Yxy.r * (1 - Yxy.g - Yxy.b) / Yxy.b;  // Z = Y * (1-x-y) / y
    
	// XYZ -> RGB conversion
	const float3x3 XYZ2RGB_mat  = {
		2.5651,-1.1665,-0.3986,
		-1.0217, 1.9777, 0.0439, 
		0.0753, -0.2543, 1.1892
	};
  
	float3 rgb = mul(XYZ2RGB_mat, XYZ);

	return rgb; 
}

//--------------------------------------------------------------------------------------------------
float min_channel(in float3 v)
{
	float t = (v.x < v.y) ? v.x : v.y;
    return (t < v.z) ? t : v.z;
}

//--------------------------------------------------------------------------------------------------
float max_channel(in float3 v)
{
    float t = (v.x > v.y) ? v.x : v.y;
    return (t > v.z) ? t : v.z;
}

//--------------------------------------------------------------------------------------------------
float3 RGB2HSV(in float3 rgb)
{
    float3 hsv = float3(0,0,0);

    float minVal = min_channel(rgb);
    float maxVal = max_channel(rgb);

	//-- delta RGB value.
    float delta = maxVal - minVal;

    hsv.z = maxVal;

	//-- If gray, leave H & S at zero.
    if (delta != 0)
	{
       hsv.y = delta / maxVal;

       float3 delRGB = (((maxVal.xxx - rgb) / 6.0f) + (delta / 2.0f)) / delta;

       if      (rgb.x == maxVal) hsv.x = delRGB.z - delRGB.y;
       else if (rgb.y == maxVal) hsv.x = (1.0f / 3.0f) + delRGB.x - delRGB.z;
       else if (rgb.z == maxVal) hsv.x = (2.0f / 3.0f) + delRGB.y - delRGB.x;

       if (hsv.x < 0.0) { hsv.x += 1.0; }
       if (hsv.x > 1.0) { hsv.x -= 1.0; }
    }

    return hsv;
}

//--------------------------------------------------------------------------------------------------
float3 HSV2RGB(in float3 hsv)
{
    float3 rgb = hsv.z;

    if (hsv.y != 0)
	{
       float var_h = hsv.x * 6;
       float var_i = floor(var_h);   // Or ... var_i = floor( var_h )
       float var_1 = hsv.z * (1.0 - hsv.y);
       float var_2 = hsv.z * (1.0 - hsv.y * (var_h-var_i));
       float var_3 = hsv.z * (1.0 - hsv.y * (1-(var_h-var_i)));

       if      (var_i == 0) { rgb = float3(hsv.z, var_3, var_1); }
       else if (var_i == 1) { rgb = float3(var_2, hsv.z, var_1); }
       else if (var_i == 2) { rgb = float3(var_1, hsv.z, var_3); }
       else if (var_i == 3) { rgb = float3(var_1, var_2, hsv.z); }
       else if (var_i == 4) { rgb = float3(var_3, var_1, hsv.z); }
       else                 { rgb = float3(hsv.z, var_1, var_2); }
   }

   return rgb;
}

//-------------------------------------------------------------------------------------------------
VertexOut VS(VertexXYZUV i)
{
	VertexOut o = (VertexOut)0;
	o.pos = i.pos;
	o.tc  = i.tc;
	
	return o;
}

//-------------------------------------------------------------------------------------------------
float4 PS(VertexOut i) : COLOR0
{
	const half avgLum	  = tex2D(g_avgLumMapSampler, float2(0,0));
	const half middleGray = g_params.x;
	const half whitePoint = g_params.y;

	float4 color  = tex2D(g_HDRMapSampler, i.tc);
	float  lum    = luminance(color.rgb);

	//-- (Lp) Map average luminance to the middlegrey zone by scaling pixel luminance
	float  Lp = lum * middleGray / avgLum;

	//-- multiply color by scaled luminance.
	color.rgb *= Lp;

	//-- (Ld) Scale all luminance within a displayable range of 0 to 1
	float3 o = (color.rgb * (1.0f + color.rgb / (whitePoint * whitePoint))) / (1.0f + color.rgb);

	return float4(o, 0.0f);
}

//-------------------------------------------------------------------------------------------------
float4 PS2(VertexOut i) : COLOR0
{
	const half avgLum	  = tex2D(g_avgLumMapSampler, float2(0,0));
	const half middleGray = g_params.x;
	const half whitePoint = g_params.y;

	float3 xyz = RGB2XYZ(tex2D(g_HDRMapSampler, i.tc));
	float  lum = xyz.r;

	//-- (Lp) Map average luminance to the middlegrey zone by scaling pixel luminance
	float Lp = lum * middleGray / avgLum;
	//-- (Ld) Scale all luminance within a displayable range of 0 to 1
	xyz.r *= (Lp * (1.0f + Lp / (whitePoint * whitePoint))) / (1.0f + Lp);

	float3 rgb = XYZ2RGB(xyz);

	return float4(rgb, 0.0f);
}

//-------------------------------------------------------------------------------------------------
float4 PS3(VertexOut i) : COLOR0
{
	const half avgLum	  = tex2D(g_avgLumMapSampler, float2(0,0));
	const half middleGray = g_params.x;
	const half whitePoint = g_params.y;

	float3 hsv = RGB2HSV(tex2D(g_HDRMapSampler, i.tc));

	//-- (Lp) Map average luminance to the middlegrey zone by scaling pixel luminance
	float Lp = hsv.z * middleGray / avgLum;
	//-- (Ld) Scale all luminance within a displayable range of 0 to 1
	hsv.z *= (Lp * (1.0f + Lp / (whitePoint * whitePoint))) / (1.0f + Lp);

	float3 rgb = HSV2RGB(hsv);

	return float4(rgb, 0.0f);
}

//-- Crysis's version.
//-------------------------------------------------------------------------------------------------
float4 PS4(VertexOut i) : COLOR0
{
	//-- read common parameters for "Reinhard HDR with White Point".
	const half avgLum	  = tex2D(g_avgLumMapSampler, float2(0,0));
	const half middleGray = g_params.x;
	const half whitePoint = g_params.y;

	//-- read color and calculate current luminance.
	half4 color = tex2D(g_HDRMapSampler, i.tc);
	half  lum   = luminance(color.rgb);

	//-- calculate HDR adjust parameter.
	//-- (Lp) Map average luminance to the middlegrey zone by scaling pixel luminance
	half Lp = lum * middleGray / avgLum;
	//-- (Ld) Scale all luminance within a displayable range of 0 to 1
	half Ld = (Lp * (1 + Lp / (whitePoint * whitePoint))) / (1 + Lp);

	color.rgb *= Ld / lum;

	//-- bloom.
	const half bloomEnable = g_bloomParams.x;
	const half bloomFactor = g_bloomParams.y;

	half3 bloomColor = tex2D(g_bloomMapSampler, i.tc).rgb / 8.0f;
	color.rgb += bloomColor * bloomFactor * bloomEnable;

	//-- gamma correction.
	color.rgb = linear2gamma(color.rgb);

	return color;
}

//--
float3 Uncharted2Tonemap(float3 x)
{
	float A = 0.15;
	float B = 0.50;
	float C = 0.10;
	float D = 0.20;
	float E = 0.02;
	float F = 0.30;
	float W = 11.2;

   return ((x*(A*x+C*B)+D*E)/(x*(A*x+B)+D*F))-E/F;
}

//-- Uncharted2's version.
//-------------------------------------------------------------------------------------------------
float4 PS5(VertexOut i) : COLOR0
{
	//-- read common parameters for "Reinhard HDR with White Point".
	const half avgLum = tex2D(g_avgLumMapSampler, float2(0,0));
	const half middleGray = g_params.x;
	const half whitePoint = g_params.y;

	//-- read color in linear space and calculate current luminance.
	float4 color = pow(tex2D(g_HDRMapSampler, i.tc), 2.2f);
	float  lum = luminance(color.rgb);

	//-- calculate HDR adjust parameter.
	//-- (Lp) Map average luminance to the middlegrey zone by scaling pixel luminance
	float Lp = lum * middleGray / avgLum;

   float3 curr = Uncharted2Tonemap(Lp * color);

   float3 whiteScale = 1.0f / Uncharted2Tonemap(whitePoint);
   color.rgb = curr * whiteScale;

	//-- bloom.
	const float bloomEnable = g_bloomParams.x;
	const float bloomFactor = g_bloomParams.y;

	float3 bloomColor = pow(tex2D(g_bloomMapSampler, i.tc).rgb / 8.0f, 2.2f);
	color.rgb += bloomColor * bloomFactor * bloomEnable;
	 
	//-- back to gamma space.
	color.rgb = linear2gamma(color.rgb);

	return color;
}

//-------------------------------------------------------------------------------------------------
technique shaderTransfer
{
	pass Pass_0
	{
		ALPHABLENDENABLE = FALSE;
		ALPHATESTENABLE = FALSE;
		ZENABLE = FALSE;
		ZWRITEENABLE = FALSE;
		FOGENABLE = FALSE;
		CULLMODE = CW;
		
		VertexShader = compile vs_3_0 VS();
		PixelShader  = compile ps_3_0 PS4();
	}
}
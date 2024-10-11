#include "post_processing.fxh"

DECLARE_EDITABLE_TEXTURE( inputTexture, inputSampler, CLAMP, CLAMP, LINEAR, "Input texture/render target" )


float alpha
<
	bool artistEditable = true;
	float UIMin = 0;
	float UIMax = 1.0;
	int UIDigits = 2;
	string UIDesc = "Alpha value";
> = 1.0;


float saturation
<
	bool artistEditable = true;
	float UIMin = -1.0;
	float UIMax = 1.0;
	int UIDigits = 2;
	string UIDesc = "Adjust to increase/decrease colour saturation";
> = 0.0;


float brightness
<
	bool artistEditable = true;
	float UIMin = -1.0;
	float UIMax = 1.0;
	int UIDigits = 2;
	string UIDesc = "Adjust to increase/decrease brightness";
> = 0.0;


//---------------------------------------------------------------------
//	Section Colour Correct in HSV
//---------------------------------------------------------------------
float EPSILON = 0.0001;

void RGBtoHSB(float3 p, out float3 hsb )
{
	float red;
	float green;
	float blue;	

	red = p.r;
	green = p.g;
	blue = p.b;

	float mx = max(max(red, green), blue);
	float mn = min(min(red, green), blue);
	float delta = mx - mn;
	float deltadiv = 1.0 / delta;

	// Brightness is the magnitude of the brightest channel.
	hsb.b = mx;

	// Saturation is the relative difference between the lowest and highest channels.
	if (mx > EPSILON)
		hsb.g = delta / mx ;
	else
		hsb.g = 0.0 ;

	if (delta < EPSILON)
		hsb.r = 0.0; // hue is meaningless for greys
	else
	{
		if ( red == mx )
			// Hue between yellow and magenta
			hsb.r = (green - blue) * deltadiv; // / delta;
		else if ( green == mx )
			// Hue between ? and ?
			hsb.r = 2.0 + (blue - red) * deltadiv; // / delta ;
		else
			// Hue between ? and ?
			hsb.r = 4.0 + (red - green) * deltadiv; // / delta ;

		hsb.r = hsb.r / 6.0;

		if ( hsb.r < 0.0 )
			hsb.r += 1.0;
	}
	
}


float3 HSBtoRGB(double hue, double saturation, double brightness)
{
	float3 colour;
	int hextant;
	double remainder, p, q, t;

	/* Determine which facet of the HSV hexcone we are in. */
	if ( 1.0 == hue)
		hue = 0.0;
	hextant = (int)(hue * 6.0);

	/* Find out how far we are into this hextant. */
	remainder = hue * 6.0 - hextant ;

	p = brightness * (1.0-saturation);
	q = brightness * (1.0-(saturation * remainder));
	t = brightness * (1.0-(saturation * (1.0 - remainder)));

	double red;
	double green;
	double blue;

	//switch (hextant)
	if (hextant == 0)
	{
		//case 0:
		colour.r = brightness ;
		colour.g = t;
		colour.b = p;		
	}
	else if (hextant == 1)
	{
		//case 1:
		colour.r = q;
		colour.g = brightness;
		colour.b = p;				
	}
	else if (hextant == 2)
	{
		//case 2:
		colour.r = p;
		colour.g = brightness;
		colour.b = t;		
	}
	else if (hextant == 3)
	{
		//case 3:
		colour.r = p;
		colour.g = q;
		colour.b = brightness;
	}
	else if (hextant == 4)
	{
		//case 4:
		colour.r = t;
		colour.g = p;
		colour.b = brightness;		
	}
	else if (hextant == 5)
	{
		//case 5:
		colour.r = brightness;
		colour.g = p;
		colour.b = q;		
	}
	else
	{
		colour.rgb = float3(1,1,1);
	}
	return colour;
}


float4 ps_main( PS_INPUT input ) : COLOR0
{	
	float4 bb = tex2D( inputSampler, input.tc2 );
	float3 hsv;
	float4 colour;	
	RGBtoHSB( bb, hsv );
	colour.rgb = HSBtoRGB( hsv.r, saturate(hsv.g + saturation), saturate(hsv.b + brightness) );
	colour.a = (alpha);
	return colour;	
}


STANDARD_PP_TECHNIQUE( compile vs_3_0 vs_pp_default(), compile ps_3_0 ps_main() )

#include "stdinclude.fxh"
#include "read_g_buffer.fxh"

//--------------------------------------------------------------------------------------------------

bool g_useStencilOptimization = true;
int g_sampleNum; // from 1 to 8
bool g_useNormal;
bool g_useDownsampledDepth;
float g_radius;
float g_amplify;
float g_fade;

//--------------------------------------------------------------------------------------------------

// Текстура шума. Обязаны бать 4x4.
static const float2 noiseTextureSize = float2(4.f, 4.f);
texture g_noiseMapSSAO;

// Уменьшенный буффер глубины. 
// Используется в том случае, если g_useDownsampledDepth = true.
// В противном случае не выставляется.
texture g_depth;

//--------------------------------------------------------------------------------------------------

// Распределенные случайным образом точки внутри единичной сферы.
// TODO(a_cherkes): не знаю точного типа распределения (гаусово или равномерное).
static const float3 kernel[32] = {
	float3(-0.556641,-0.037109,-0.654297), 
	float3(0.173828,0.111328,0.064453),    
	float3(0.001953,0.082031,-0.060547),   
	float3(0.220703,-0.359375,-0.062500),  
	float3(0.242188,0.126953,-0.250000),   
	float3(0.070313,-0.025391,0.148438),   
	float3(-0.078125,0.013672,-0.314453),  
	float3(0.117188,-0.140625,-0.199219),  
	float3(-0.251953,-0.558594,0.082031),  
	float3(0.308594,0.193359,0.324219),    
	float3(0.173828,-0.140625,0.031250),   
	float3(0.179688,-0.044922,0.046875),   
	float3(-0.146484,-0.201172,-0.029297),  
	float3(-0.300781,0.234375,0.539063),   
	float3(0.228516,0.154297,-0.119141),   
	float3(-0.119141,-0.003906,-0.066406),  
	float3(-0.218750,0.214844,-0.250000),  
	float3(0.113281,-0.091797,0.212891),   
	float3(0.105469,-0.039063,-0.019531),  
	float3(-0.705078,-0.060547,0.023438),   
	float3(0.021484,0.326172,0.115234),     
	float3(0.353516,0.208984,-0.294922),   
	float3(-0.029297,-0.259766,0.089844),  
	float3(-0.240234,0.146484,-0.068359),  
	float3(-0.296875,0.410156,-0.291016),  
	float3(0.078125,0.113281,-0.126953),   
	float3(-0.152344,-0.019531,0.142578),  
	float3(-0.214844,-0.175781,0.191406),  
	float3(0.134766,0.414063,-0.707031),   
	float3(0.291016,-0.833984,-0.183594),  
	float3(-0.058594,-0.111328,0.457031),  
	float3(-0.115234,-0.287109,-0.259766),  
};

//--------------------------------------------------------------------------------------------------

sampler g_noiseMapSampler = sampler_state
{		
	Texture = <g_noiseMapSSAO>;
	MIPFILTER = POINT;
	MAGFILTER = POINT;
	MINFILTER = POINT;
	ADDRESSU = WRAP;
	ADDRESSV = WRAP;
};

sampler g_depthSampler = sampler_state
{		
	Texture = <g_depth>;
	//-- TODO: reconsider. Does we really need this?
	MIPFILTER = LINEAR;  //-- we can use linear interpolation because we use R32F texture 
	MAGFILTER = LINEAR;  //-- downsampled depth buffer and values in this buffer is not packed.
	MINFILTER = LINEAR;
	ADDRESSU = WRAP;
	ADDRESSV = WRAP;
};

//--------------------------------------------------------------------------------------------------

BW_DS_LIGHT_PASS_VS2PS VS(BW_DS_LIGHT_PASS_VS i)
{
	BW_DS_LIGHT_PASS_VS2PS o = (BW_DS_LIGHT_PASS_VS2PS) 0;
	o.pos = i.pos;
	o.tc  = i.tc;
	return o;
}

//--------------------------------------------------------------------------------------------------

float4 PS(BW_DS_LIGHT_PASS_VS2PS i, 
		  uniform int sampleNum, 
		  uniform bool useNormal, 
		  uniform bool useDownsampledDepth) : COLOR
{
	//-- sample depth in [0..1] liner space

	float centerDepth = useDownsampledDepth 
	                  ? tex2D(g_depthSampler, i.tc).x
	                  : g_buffer_readLinearZ(i.tc);

	//-- sample view space normal

	float3 centerNormal = g_buffer_readWorldNormal(i.tc);
	centerNormal = mul(float4(centerNormal, 0.f), g_viewMat).xyz;
	centerNormal *= float3(1.f, -1.0f, 1.0f);
	centerNormal = normalize(centerNormal);

	//-- sample random vector

	float2 noiseTC = fmod(g_screen.xy * i.tc, noiseTextureSize) / noiseTextureSize;
	float3 randomVector =  2.f * tex2D(g_noiseMapSampler, noiseTC).xyz - 1.0f;
	randomVector = normalize(randomVector);

	//-- calc SSAO

	// Вычисляем SSAO путем "выпускания" тестовых лучей из центральной точки (текущий пиксель).
	// Длина и напровление каждого луча рандомизированы.
	// Коэфицент затенения считается как отношение количества тестовых лучей пересекающих окружающую 
	// геометрию к общему количеству лучей. Факт пересечения устанавливается приближенно:
	// вместо поиска реального пересечения, проверяется глубина точки-окончания луча и сравнивается 
	// со значением записанным в буффере глубины. Если окончание луча перекрывается геометрией с точки
	// зрения наблюдателя, то считаем, что луч пересекает геометрию.
	// 
	// В одной итерации цикла общитывается сразу по 4 луча. Это позволяет сделать некоторые операции 
	// (в данном случае те, что идут в конце цикла), векторизированными. Таким образом уменьшается количество 
	// шейдерных инструкций.
	//

	float4 r = float4(0.f, 0.f, 0.f, 0.f);
	for(int index = 0; index < sampleNum; index += 4)
	{
		// Находим рандомизированные тестовые лучи.

		float3 s0 = g_radius * reflect(kernel[index + 0], randomVector);
		float3 s1 = g_radius * reflect(kernel[index + 1], randomVector);
		float3 s2 = g_radius * reflect(kernel[index + 2], randomVector);
		float3 s3 = g_radius * reflect(kernel[index + 3], randomVector);

		// Корректируем направление лучей так, чтобы все они были сонаправлены с нормалью.

		if(useNormal)
		{
			s0 = dot(s0, centerNormal.xyz) >= 0.f ? s0 : - s0;
			s1 = dot(s1, centerNormal.xyz) >= 0.f ? s1 : - s1;
			s2 = dot(s2, centerNormal.xyz) >= 0.f ? s2 : - s2;
			s3 = dot(s3, centerNormal.xyz) >= 0.f ? s3 : - s3;
		}

		// Глубины окончаний тестовых лучей нормированные к глубине центра.

		float4 sampleDepth = 1.f + float4(s0.z, s1.z, s2.z, s3.z);

		// Глубины соответсвующие окончаниям тестовых лучей, прочитанные из 
		// буффера глубины, нормированные к глубине центра.

		float4 bufferDepth;
		if(useDownsampledDepth)
		{
			bufferDepth.x = tex2D(g_depthSampler, i.tc + s0.xy);
			bufferDepth.y = tex2D(g_depthSampler, i.tc + s1.xy);
			bufferDepth.z = tex2D(g_depthSampler, i.tc + s2.xy);
			bufferDepth.w = tex2D(g_depthSampler, i.tc + s3.xy);
		}
		else
		{
			bufferDepth.x = g_buffer_readLinearZ(i.tc + s0.xy);
			bufferDepth.y = g_buffer_readLinearZ(i.tc + s1.xy);
			bufferDepth.z = g_buffer_readLinearZ(i.tc + s2.xy);
			bufferDepth.w = g_buffer_readLinearZ(i.tc + s3.xy);
		}
		bufferDepth /= centerDepth;

		// Не учитываем террейн и флору.
		// Если луч попал на эти материалы, считаем, что он не пересек геометрию.
		// Т.е флоре и террейн "осветляют" конечный коэфицент.

		float4 maskedOutPixels = float4(1,1,1,1);
#if 1
		//-- Warning: should be in sync with G_OBJECT_KIND_* in stdinclude.fxh
		static const float g_ssaoMask[] = {0, 1, 0, 1, 1, 1};

		maskedOutPixels.x = g_ssaoMask[(int)g_buffer_readObjectKind(i.tc + s0.xy)];
		maskedOutPixels.y = g_ssaoMask[(int)g_buffer_readObjectKind(i.tc + s1.xy)];
		maskedOutPixels.z = g_ssaoMask[(int)g_buffer_readObjectKind(i.tc + s2.xy)];
		maskedOutPixels.w = g_ssaoMask[(int)g_buffer_readObjectKind(i.tc + s3.xy)];
#endif

		//-- d[i] is a distance between sampleDepth[i] and bufferDepth[i] measuared in g_radius
		//-- > 0 - random shpere sample is obscured by geometry
		//-- < 0 - random sphere sample is not obscured by geometry
		float4 d = (sampleDepth - bufferDepth) / g_radius;

		float4 amount = d > 0 ? 1.f : 0.f; // step(0.f, d);

		// Вес сильно удаленной от центра геометрии уменьшается пропорционально расстоянию.

		float4 fadeOut = saturate(g_fade / d);

		// Прибавляем результат к общей сумме.

		r += amount * fadeOut * maskedOutPixels;
	}

	// Считаем конечный коэфицент затенения, как среднее арифметическое результатов 
	// тестов пересечений луч-геометрия.

	float t = dot(r, 1.f); // t = r.x + r.y + r.z + r.w
	t /= sampleNum;

	// Применяем параметр amplify и приводим значение к финальному виду.

	t = pow(abs(t), g_amplify);
	t = saturate(1.f - t);

	return float4(t, t, t, t);
}

//--------------------------------------------------------------------------------------------------

// Компиляция шейдера с разными параметрами.
PixelShader g_pixel_shaders[] = 
{
	compile ps_3_0 PS( 4, false, false),
	compile ps_3_0 PS( 8, false, false),
	compile ps_3_0 PS(12, false, false),
	compile ps_3_0 PS(16, false, false),
	compile ps_3_0 PS(20, false, false),
	compile ps_3_0 PS(24, false, false),
	compile ps_3_0 PS(28, false, false),
	compile ps_3_0 PS(32, false, false),

	compile ps_3_0 PS( 4, true, false),
	compile ps_3_0 PS( 8, true, false),
	compile ps_3_0 PS(12, true, false),
	compile ps_3_0 PS(16, true, false),
	compile ps_3_0 PS(20, true, false),
	compile ps_3_0 PS(24, true, false),
	compile ps_3_0 PS(28, true, false),
	compile ps_3_0 PS(32, true, false),

	compile ps_3_0 PS( 4, false, true),
	compile ps_3_0 PS( 8, false, true),
	compile ps_3_0 PS(12, false, true),
	compile ps_3_0 PS(16, false, true),
	compile ps_3_0 PS(20, false, true),
	compile ps_3_0 PS(24, false, true),
	compile ps_3_0 PS(28, false, true),
	compile ps_3_0 PS(32, false, true),

	compile ps_3_0 PS( 4, true, true),
	compile ps_3_0 PS( 8, true, true),
	compile ps_3_0 PS(12, true, true),
	compile ps_3_0 PS(16, true, true),
	compile ps_3_0 PS(20, true, true),
	compile ps_3_0 PS(24, true, true),
	compile ps_3_0 PS(28, true, true),
	compile ps_3_0 PS(32, true, true)
};

technique SSAO
{
	pass Pass_0
	{
		ALPHATESTENABLE = FALSE;
		ZENABLE = FALSE;
		ZWRITEENABLE = FALSE;
		ALPHABLENDENABLE = FALSE;
		FOGENABLE = FALSE;
		POINTSPRITEENABLE = FALSE; // ???
		CULLMODE = CW;

		//-- use stencil to mark only valid g-buffer pixels (i.e. not sky and flora pixels)
		STENCILENABLE = <g_useStencilOptimization>;
		STENCILFUNC = NOTEQUAL;
		STENCILWRITEMASK = 0x00;
		//-- TODO(a_cherkes): reconsider
		//--                  we can exclude flora from SSAO resolving by using G_STENCIL_USAGE_FLORA
		STENCILMASK = G_STENCIL_USAGE_ALL_OPAQUE;
		//STENCILMASK = G_STENCIL_USAGE_SPEEDTREE | G_STENCIL_USAGE_FLORA | G_STENCIL_USAGE_OTHER_OPAQUE;
		STENCILREF = 0;

		VertexShader = compile vs_3_0 VS();
		PixelShader  = g_pixel_shaders[(g_sampleNum - 1) + 8 * g_useNormal + 16 * g_useDownsampledDepth];
	}
};

//--------------------------------------------------------------------------------------------------
//-- End

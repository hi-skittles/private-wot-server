#ifndef _UV_FXH_
#define _UV_FXH_

//-------------------------------------------------------------------------------------------------
//-- Файл определяет макросы для трансформации UV координат в вершинном шейдере
//-------------------------------------------------------------------------------------------------

//-- Входные параметры:
//----------------------------
//--
//-- Должны объявляться в файле материалов перед вставкой файла skinned/unskinned_effect_include.fxf
//--
//-- DUAL_UV               -- использовать двойной UV набор
//-- UV_TRANSFORM_DIFFUSE  -- применять UV-анимацию для основной текстуры 
//-- UV_TRANSFORM_OTHER    -- применять UV-анимацию для дополнительной текстуры
//--
//--
//-- Выходные макросы:
//----------------------------
//--
//-- main (reflection pass)
//-- BW_CALCULATE_UVS
//-- BW_INSTANCING_CALCULATE_UVS
//--
//-- color pass
//-- BW_DS_CALCULATE_UVS
//-- BW_DS_INSTANCING_CALCULATE_UVS
//--
//-- shadow pass
//-- BW_SHADOWS_CALCULATE_UVS
//-- BW_SHADOWS_INSTANCING_CALCULATE_UVS
//--
//--
//-- Коментарии к использованию:
//----------------------------
//--
//-- На данный момент существет несколько режимов преобразования UV-координат:
//-- 1) DUAL_UV: 
//--    Входные вершины содержат два UV-набора (объявлена константа DUAL_UV).
//--    На данный момент в этом режиме невозможно осуществлять анимацию текстурных 
//--    координат (можно пересмотреть). Вершинный шейдер выдает два UV-набора без изменений.
//-- 2) UV_TRANSFORM_DIFFUSE || UV_TRANSFORM_OTHER: 
//--    Входные вершины содержат один UV-набор. Возможна анимация текстурных координат.
//--    а) Используется одна диффузная текстура (diffuseMap) с анимацией текстурных координат 
//--       или без. Вершинный шейдер выдает один UV-набор.
//--    б) Используется дополнительная (вторая) диффузная тектстура (otherMap). Возможна анимация 
//--       текстурных координат. Вершинный шейдер выдает два UV-набора, которые получаются из 
//--       одного входного UV-набора заданного во входных вершинах. Анимированными могут быть как 
//--       основная либо дополнительная цветовая карта (UV_TRANSFORM_OTHER) либо обе карты вместе 
//--       (UV_TRANSFORM_DIFFUSE + UV_TRANSFORM_OTHER). Параметры анимации задаются для обеих карт 
//--       независимо. Вершинный шейдер выдает два UV-набора.
//-- 
//-- Примечание: использование режимов на практике
//--    режим DUAL_UV - для текстурирования зданий
//--    режим 2.а     - для анимирования гусениц танков
//-- 	режим 2.б     - для моделей типа водопада или лавы, для пола в tankEditor
//-- 
//-------------------------------------------------------------------------------------------------

#ifdef DUAL_UV
#if (defined UV_TRANSFORM_DIFFUSE) || (defined UV_TRANSFORM_OTHER)
#error "You can't use UV transform with dual UV set."
#endif
#endif

//-------------------------------------------------------------------------------------------------

#ifdef UV_TRANSFORM_OTHER
float4 uTransform
<
	bool artistEditable = true;
	string UIName = "U Transform Diffuse";
	string UIDesc = "The U-transform vector for the diffuse material";
	string UIWidget = "Spinner";
	float UIMax = 100;
	float UIMin = -100;
> = {1,0,0,0};

float4 vTransform
<
	bool artistEditable = true;
	string UIName = "V Transform Diffuse";
	string UIDesc = "The V-transform vector for the diffuse material";
	string UIWidget = "Spinner";
	float UIMax = 100;
	float UIMin = -100;
> = {0,1,0,0};
#endif // UV_TRANSFORM_OTHER

#ifdef UV_TRANSFORM_DIFFUSE
float4 uTransform_diffuse
<
	bool artistEditable = true;
	string UIName = "U Transform";
	string UIDesc = "The U-transform vector for the material";
	string UIWidget = "Spinner";
	float UIMax = 100;
	float UIMin = -100;
> = {1,0,0,0};

float4 vTransform_diffuse
<
	bool artistEditable = true;
	string UIName = "V Transform";
	string UIDesc = "The V-transform vector for the material";
	string UIWidget = "Spinner";
	float UIMax = 100;
	float UIMin = -100;
> = {0,1,0,0};
#endif // UV_TRANSFORM_DIFFUSE

//-------------------------------------------------------------------------------------------------

//-- UV1 (diffuse)

#ifdef UV_TRANSFORM_DIFFUSE
	#define _GET_UV1(o)\
		o.tc.x = dot(tc, uTransform_diffuse * float4(1, 1, g_time, 1));\
		o.tc.y = dot(tc, vTransform_diffuse * float4(1, 1, g_time, 1));
#else
	#define _GET_UV1(o)\
		o.tc.xy = tc.xy;
#endif // UV_TRANSFORM_DIFFUSE

//-- UV2 (other)

#ifdef UV_TRANSFORM_OTHER
	#define _GET_UV2(o)\
		o.tc2.x = dot(tc, uTransform * float4(1, 1, g_time, 1));\
		o.tc2.y = dot(tc, vTransform * float4(1, 1, g_time, 1));
#else
	#define _GET_UV2(o)
#endif // UV_TRANSFORM_OTHER

//-- DUAL

#ifdef DUAL_UV
	#define _GET_UV_ALL(o)\
		o.tc.xy  = BW_UNPACK_TEXCOORD(i.tc );\
		o.tc2.xy = BW_UNPACK_TEXCOORD(i.tc2);
#else
	#define _GET_UV_ALL(o)\
		float4 tc = float4(BW_UNPACK_TEXCOORD(i.tc), 1, 1);\
		_GET_UV1(o)\
		_GET_UV2(o)
#endif // DUAL_UV

//-- FINAL

#define BW_CALCULATE_UVS(o)						_GET_UV_ALL(o)
#define BW_INSTANCING_CALCULATE_UVS(o)			BW_CALCULATE_UVS(o)
#define BW_DS_CALCULATE_UVS(o)					BW_CALCULATE_UVS(o)
#define BW_DS_INSTANCING_CALCULATE_UVS(o)		BW_DS_CALCULATE_UVS(o)
#define BW_SHADOWS_CALCULATE_UVS(o)				BW_DS_CALCULATE_UVS(o)
#define BW_SHADOWS_INSTANCING_CALCULATE_UVS(o)	BW_DS_CALCULATE_UVS(o)

//-------------------------------------------------------------------------------------------------

#endif //-- _UV_FXH_
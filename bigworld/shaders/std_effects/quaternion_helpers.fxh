#ifndef QUATERNION_HELPERS_FXH
#define QUATERNION_HELPERS_FXH

//-- rotate vector by quaternion.
//--------------------------------------------------------------------------------------------------
float3 qrot(float3 v, float4 q)
{
	return v + 2 * cross(q.xyz, cross(q.xyz, v) + q.w * v);
}

//-- rotate vector by inversed quaternion.
//--------------------------------------------------------------------------------------------------
float3 qrot(float4 q, float3 v)
{
	q =  float4(-q.xyz, q.w);
	return v + 2 * cross(q.xyz, cross(q.xyz, v) + q.w * v);
}

//-- combine quaternions
//--------------------------------------------------------------------------------------------------
float4 qmul(float4 a, float4 b)
{
	return float4(cross(a.xyz, b.xyz) + a.xyz * b.w + b.xyz * a.w, a.w * b.w - dot(a.xyz, b.xyz));
}

//-- initializes quaternion from axis and rotation angle around this axis.
//--------------------------------------------------------------------------------------------------
float4 quat(float angle, float3 axis)
{
	float2 sc;
    sincos(angle * 0.5f, sc.x, sc.y);

	return float4(axis * sc.x, sc.y);
}

#endif //-- QUATERNION_HELPERS_FXH
// HLSL Vertex/Fragment Shader for URP
// Minimal custom pass structure for learning and custom effects.
// Uses HLSLPROGRAM with URP includes.

Shader "Custom/VertexFragment"
{
    Properties
    {
        _Color ("Color", Color) = (0.5, 0.8, 1.0, 1.0)
        _FresnelPower ("Fresnel Power", Range(0.1, 10)) = 3.0
    }

    SubShader
    {
        Tags
        {
            "RenderType" = "Opaque"
            "RenderPipeline" = "UniversalPipeline"
            "Queue" = "Geometry"
        }

        Pass
        {
            HLSLPROGRAM
            #pragma vertex vert
            #pragma fragment frag

            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

            struct Attributes
            {
                float4 positionOS : POSITION;
                float3 normalOS : NORMAL;
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float3 normalWS : TEXCOORD0;
                float3 viewDirWS : TEXCOORD1;
            };

            CBUFFER_START(UnityPerMaterial)
                half4 _Color;
                half _FresnelPower;
            CBUFFER_END

            Varyings vert(Attributes input)
            {
                Varyings output;
                VertexPositionInputs posInputs = GetVertexPositionInputs(input.positionOS.xyz);
                output.positionCS = posInputs.positionCS;
                output.normalWS = TransformObjectToWorldNormal(input.normalOS);
                output.viewDirWS = GetWorldSpaceNormalizeViewDir(posInputs.positionWS);
                return output;
            }

            half4 frag(Varyings input) : SV_Target
            {
                half fresnel = pow(1.0 - saturate(dot(input.normalWS, input.viewDirWS)), _FresnelPower);
                half3 finalColor = lerp(_Color.rgb, half3(1, 1, 1), fresnel);
                return half4(finalColor, 1.0);
            }
            ENDHLSL
        }
    }

    Fallback "Universal Render Pipeline/Unlit"
}

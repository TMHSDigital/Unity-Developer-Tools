---
title: Shader Development
description: Shader creation with Shader Graph, HLSL, and ShaderLab for URP and HDRP projects.
globs: ["**/*.shader", "**/*.hlsl", "**/*.cginc", "**/*.shadergraph"]
standards-version: 1.10.0
---

# Shader Development

## Choosing a Shader Workflow

### Shader Graph (Primary - URP/HDRP)

Node-based visual editor. Use for the majority of shader work:
- Material effects (dissolve, outline, hologram, water)
- Artist-facing shaders that need visual tweaking
- Rapid prototyping and iteration
- Custom Function nodes for injecting HLSL where needed

### ShaderLab + HLSL (Code-based)

Use for performance-critical shaders, custom render passes, and advanced techniques that Shader Graph cannot express:
- Custom Render Graph passes
- Compute shaders
- Procedural geometry shaders
- Full control over shader variants and keywords

### Surface Shaders (Legacy - Built-in only)

Surface shaders (`#pragma surface`) are a Built-in Render Pipeline feature. Since BiRP is deprecated in Unity 6.5, surface shaders should not be used for new projects. They do not work with URP or HDRP.

## HLSL Shader Structure for URP

All modern Unity shaders use `HLSLPROGRAM` blocks. The legacy `CGPROGRAM` is deprecated for scriptable render pipelines.

```hlsl
Shader "Custom/BasicUnlit"
{
    Properties
    {
        _MainTex ("Texture", 2D) = "white" {}
        _Color ("Color", Color) = (1, 1, 1, 1)
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
                float2 uv : TEXCOORD0;
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float2 uv : TEXCOORD0;
            };

            TEXTURE2D(_MainTex);
            SAMPLER(sampler_MainTex);

            CBUFFER_START(UnityPerMaterial)
                float4 _MainTex_ST;
                half4 _Color;
            CBUFFER_END

            Varyings vert(Attributes input)
            {
                Varyings output;
                output.positionCS = TransformObjectToHClip(input.positionOS.xyz);
                output.uv = TRANSFORM_TEX(input.uv, _MainTex);
                return output;
            }

            half4 frag(Varyings input) : SV_Target
            {
                half4 texColor = SAMPLE_TEXTURE2D(_MainTex, sampler_MainTex, input.uv);
                return texColor * _Color;
            }
            ENDHLSL
        }
    }

    Fallback "Universal Render Pipeline/Unlit"
}
```

## Key Shader Conventions

### SRP Batcher Compatibility

Wrap per-material properties in a CBUFFER to enable SRP Batcher:

```hlsl
CBUFFER_START(UnityPerMaterial)
    float4 _MainTex_ST;
    half4 _Color;
    half _Metallic;
    half _Smoothness;
CBUFFER_END
```

### Property Naming

All shader properties use underscore prefix: `_MainTex`, `_Color`, `_Metallic`, `_Smoothness`, `_BumpMap`.

### Shader Keywords and Variants

Use `shader_feature` for keywords that are set per material, `multi_compile` for global keywords:

```hlsl
#pragma shader_feature_local _EMISSION
#pragma multi_compile _ _MAIN_LIGHT_SHADOWS
```

Minimize variants to reduce build time and memory. Use `shader_feature_local` over `shader_feature` when the keyword is material-specific.

### Precision

Use `half` precision where full `float` is unnecessary, especially on mobile:

```hlsl
half4 color;      // 16-bit, sufficient for colors
float3 position;  // 32-bit, needed for positions
half3 normal;     // 16-bit, usually sufficient for normals
```

## Shader Graph Patterns

### Custom Function Node

Inject HLSL into Shader Graph:

1. Create an .hlsl file with your function
2. Add a Custom Function node, select "File" mode, point to the file
3. Define inputs and outputs to match function parameters

```hlsl
// CustomFunctions.hlsl
#ifndef CUSTOM_FUNCTIONS_INCLUDED
#define CUSTOM_FUNCTIONS_INCLUDED

void Dissolve_float(float alpha, float threshold, float edge, out float result)
{
    result = smoothstep(threshold, threshold + edge, alpha);
}

#endif
```

### Common Effects

- **Dissolve**: Noise texture + clip/alpha threshold
- **Outline**: Vertex extrusion + inverted normals pass or post-process edge detection
- **Hologram**: Fresnel + scanline + vertex displacement
- **Water**: Sine-based vertex displacement + normal map scrolling + depth-based transparency
- **Toon/Cel**: Step function on NdotL for discrete shading bands

## Render Graph Custom Passes

For advanced rendering effects in Unity 6, use Render Graph compatible passes instead of extra cameras:

```csharp
public class CustomRenderPass : ScriptableRenderPass
{
    public override void RecordRenderGraph(RenderGraph renderGraph, ContextContainer frameData)
    {
        // Record rendering commands using the Render Graph API
    }
}
```

Extra cameras are now considered a legacy performance anti-pattern. Use Render Graph passes for custom rendering effects.

## GPU Instancing

Enable instancing for shaders that will be used on many identical objects:

```hlsl
#pragma multi_compile_instancing

UNITY_INSTANCING_BUFFER_START(Props)
    UNITY_DEFINE_INSTANCED_PROP(half4, _Color)
UNITY_INSTANCING_BUFFER_END(Props)
```

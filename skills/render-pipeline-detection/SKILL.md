---
title: Render Pipeline Detection
description: Detecting the active render pipeline (URP, HDRP, or Built-in) and adapting code, shaders, and settings accordingly.
globs: ["**/*.cs", "**/*.shader", "**/*.shadergraph"]
standards-version: 1.10.0
---

# Render Pipeline Detection

## Current Pipeline Landscape (2026)

- **URP (Universal Render Pipeline)**: The default and actively developed pipeline. Use for all new projects.
- **HDRP (High Definition Render Pipeline)**: In maintenance mode. No new features planned beyond Switch 2 support. Existing HDRP projects can continue, but new projects should prefer URP.
- **Built-in Render Pipeline (BiRP)**: Officially deprecated as of Unity 6.5. Supported through Unity 6.7 LTS but not recommended for any new work.

## Detection at Edit Time

Check the Render Pipeline Asset in Graphics Settings:

```csharp
#if UNITY_EDITOR
using UnityEditor;
using UnityEngine.Rendering;

public static class PipelineDetector
{
    public static string GetCurrentPipeline()
    {
        var rpAsset = GraphicsSettings.currentRenderPipeline;

        if (rpAsset == null)
            return "Built-in (Deprecated)";

        string typeName = rpAsset.GetType().Name;

        if (typeName.Contains("Universal"))
            return "URP";
        if (typeName.Contains("HDRenderPipeline"))
            return "HDRP";

        return $"Unknown SRP: {typeName}";
    }
}
#endif
```

## Detection at Runtime

```csharp
using UnityEngine.Rendering;

public static bool IsURP()
{
    return GraphicsSettings.currentRenderPipeline != null
        && GraphicsSettings.currentRenderPipeline.GetType().Name.Contains("Universal");
}

public static bool IsHDRP()
{
    return GraphicsSettings.currentRenderPipeline != null
        && GraphicsSettings.currentRenderPipeline.GetType().Name.Contains("HDRenderPipeline");
}

public static bool IsBuiltIn()
{
    return GraphicsSettings.currentRenderPipeline == null;
}
```

## Scripting Define Detection

Use preprocessor directives when the pipeline packages are installed:

```csharp
#if USING_URP
    // URP-specific code
    var cameraData = camera.GetUniversalAdditionalCameraData();
#elif USING_HDRP
    // HDRP-specific code
    var cameraData = camera.GetComponent<HDAdditionalCameraData>();
#else
    // Built-in or no SRP
#endif
```

Add custom scripting defines in Project Settings > Player > Scripting Define Symbols, or use assembly definition version constraints.

## Pipeline-Specific Differences

### Shader Includes

| Pipeline | Include Path |
|----------|-------------|
| URP | `Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl` |
| HDRP | `Packages/com.unity.render-pipelines.high-definition/Runtime/ShaderLibrary/ShaderVariables.hlsl` |
| Built-in | `UnityCG.cginc` (legacy) |

### Shader Program Blocks

- URP/HDRP: Use `HLSLPROGRAM` / `ENDHLSL`
- Built-in: Used `CGPROGRAM` / `ENDCG` (deprecated)

### Post-Processing

| Feature | URP / HDRP | Built-in |
|---------|-----------|----------|
| System | Volume framework | Post-Processing Stack v2 |
| Bloom | Volume > Bloom | PostProcessVolume > Bloom |
| Color Grading | Volume > Color Adjustments | PostProcessVolume > Color Grading |
| Configuration | Volume Profile asset | Post-Process Profile asset |

### Camera Differences

- **URP**: Camera component + Universal Additional Camera Data. Camera stacking for layered rendering.
- **HDRP**: Camera component + HD Additional Camera Data. Physical camera model with exposure.
- **Built-in**: Standard Camera component only.

### Lighting

| Feature | URP | HDRP | Built-in |
|---------|-----|------|----------|
| Per-object light limit | Configurable (default 8) | Virtually unlimited | 8 (forward) |
| Area lights | Baked only | Real-time | Baked only |
| Volumetric lighting | Light cookies/fog | Full volumetric | Third-party |
| Global Illumination | SCGI (6.7), Lightmaps | Ray tracing, Path tracing | Lightmaps |

### Render Graph Backend

Both URP and HDRP use the Render Graph backend as of Unity 6.3. This enables:
- Automatic render pass optimization
- Dynamic resource allocation
- Reduced CPU overhead for complex rendering setups

When writing custom rendering code, use the Render Graph API:

```csharp
public override void RecordRenderGraph(RenderGraph renderGraph, ContextContainer frameData)
{
    // Render Graph-compatible custom pass
}
```

## Migration Recommendations

### BiRP to URP

1. Install URP package via Package Manager
2. Create a URP Render Pipeline Asset
3. Assign it in Project Settings > Graphics
4. Use Edit > Rendering > Materials > Convert to URP
5. Update custom shaders: replace CGPROGRAM with HLSLPROGRAM, update includes
6. Replace Post-Processing Stack v2 with Volume framework

### HDRP to URP

Consider this for projects that do not need HDRP-exclusive features. HDRP is in maintenance mode, while URP continues to receive new features. Conversion requires shader and material updates, as the two pipelines use different shader libraries.

---
title: Render Pipeline Detection
description: Use when advice depends on URP, HDRP, or Built-in, materials turn pink or magenta, a shader or effect works in one pipeline but not another, or the user is migrating pipelines. Covers detecting the active pipeline and adapting code, shaders, lighting, and post-processing to it.
globs: ["**/*.cs", "**/*.shader", "**/*.shadergraph"]
standards-version: 1.10.0
---

# Render Pipeline Detection

## Check the Project First

Before giving pipeline-specific advice, call the `analyze_project` MCP tool with the Unity project root. It reports the pipeline actually in use (resolved from the asset assigned in Graphics or Quality settings), the URP/HDRP package version, and the `pipeline` value to pass to `shader_helper`. Only fall back to asking the user, or to the runtime checks below, when the tool is unavailable.

## Current Pipeline Landscape (2026)

- **URP (Universal Render Pipeline)**: The default and actively developed pipeline. Use for all new projects.
- **HDRP (High Definition Render Pipeline)**: Unity plans no new HDRP features and focuses its maintenance on stability, regressions, and critical issues; Switch 2 support is the one area in active work. Existing HDRP projects can continue, but new projects should prefer URP.
- **Built-in Render Pipeline (BiRP)**: Deprecated starting in Unity 6.5. It is still available in Unity 6.7 LTS and Unity commits to supporting it until at least the end of 2028; no removal version has been announced. Not recommended for new work.

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
- Built-in: Traditionally `CGPROGRAM` / `ENDCG`. Not formally deprecated, but CG shaders are not SRP Batcher compatible, so convert them when moving to URP or HDRP.

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
| Per-object light limit | Forward: 1 main + up to 8 additional. Forward+: no per-object limit (per-camera limits apply) | Virtually unlimited | Pixel Light Count (Quality settings) lit per pixel, up to 4 per vertex, the rest by spherical harmonics |
| Area lights | Baked only | Real-time | Baked only |
| Volumetric lighting | Light cookies/fog | Full volumetric | Third-party |
| Global Illumination | Lightmaps, Adaptive Probe Volumes; Surface Cache GI in preview, planned for Unity 6.7 LTS | Ray tracing, Path tracing | Lightmaps |

### Render Graph Backend

URP uses Render Graph by default from Unity 6.0. URP Compatibility Mode (the non-Render Graph path) was removed in Unity 6.3, so custom URP passes must use the Render Graph API. HDRP is also built on Render Graph. This enables:
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

## Sources

Version-specific statements above were checked on 2026-10-10 against:

- Render pipelines strategy for 2026 (Unity staff): <https://discussions.unity.com/t/render-pipelines-strategy-for-2026/1710004>
- Upgrade to Unity 6.3 (URP Compatibility Mode removal): <https://docs.unity3d.com/6000.3/Documentation/Manual/UpgradeGuideUnity63.html>
- Light limits in URP: <https://docs.unity3d.com/6000.3/Documentation/Manual/urp/lighting/light-limits-in-urp.html>
- Surface Cache GI preview (Unity staff): <https://discussions.unity.com/t/surface-cache-gi-preview/1720494>
- Converting Built-in shaders to URP (CGPROGRAM and SRP Batcher): <https://docs.unity3d.com/6000.3/Documentation/Manual/urp/urp-shaders/birp-urp-custom-shader-upgrade-guide.html>

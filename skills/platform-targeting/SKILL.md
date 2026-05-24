---
title: Platform Targeting
description: Platform-specific compilation, scripting defines, build settings, and cross-platform considerations.
globs: ["**/*.cs"]
standards-version: 1.10.0
---

# Platform Targeting

## Scripting Defines

Use preprocessor directives for platform-specific code:

```csharp
#if UNITY_EDITOR
    Debug.Log("Editor only");
#endif

#if UNITY_STANDALONE_WIN
    InitializeDirectX();
#elif UNITY_STANDALONE_OSX
    InitializeMetal();
#elif UNITY_STANDALONE_LINUX
    InitializeVulkan();
#endif

#if UNITY_ANDROID || UNITY_IOS
    EnableTouchControls();
#endif

#if !UNITY_WEBGL
    StartBackgroundThread();
#endif
```

### Common Defines

| Define | Platform |
|--------|----------|
| `UNITY_EDITOR` | Running in the Unity Editor |
| `UNITY_EDITOR_WIN` | Editor on Windows |
| `UNITY_EDITOR_OSX` | Editor on macOS |
| `UNITY_STANDALONE` | Any desktop platform |
| `UNITY_STANDALONE_WIN` | Windows player |
| `UNITY_STANDALONE_OSX` | macOS player |
| `UNITY_STANDALONE_LINUX` | Linux player |
| `UNITY_ANDROID` | Android |
| `UNITY_IOS` | iOS |
| `UNITY_WEBGL` | WebGL / Unity Web |
| `UNITY_PS5` | PlayStation 5 |
| `UNITY_GAMECORE_XBOXONE` | Xbox One |
| `UNITY_GAMECORE_SCARLETT` | Xbox Series X/S |
| `UNITY_SWITCH` | Nintendo Switch |

## Build Settings

### Scripting Backend

| Backend | Use Case | Performance | Build Time |
|---------|----------|-------------|------------|
| **IL2CPP** | Production builds, all platforms | Excellent (AOT compiled) | Slower |
| **Mono** | Editor iteration, quick testing | Good | Fast |
| **CoreCLR** | Experimental (Unity 6.7 desktop) | Excellent (2-3x over Mono) | Moderate |

IL2CPP is the recommended backend for all release builds. It compiles C# to C++ for native performance and makes reverse engineering harder.

### API Compatibility Level

- **.NET Standard**: Smaller footprint, cross-platform compatible. Use for most projects.
- **.NET Framework**: Larger API surface. Use when you need specific .NET APIs not in Standard.

### Managed Stripping Level

Higher stripping removes more unused code, reducing build size:
- **Minimal**: Safe, removes almost nothing
- **Low**: Removes obvious unused types
- **Medium**: Recommended for most projects
- **High**: Aggressive, may require `[Preserve]` attributes on reflected types

## Mobile (Android / iOS)

### Android
- Target API level: 33+ (Android 13)
- 16KB page size support added in Unity 6
- Use ASTC texture compression
- IL2CPP is required for ARM64
- Gradle build system is mandatory

### iOS
- Minimum deployment target: iOS 15+
- Bitcode is no longer used (removed by Apple)
- Use ASTC texture compression
- Metal is the only graphics API
- Code signing and provisioning profiles required

### Mobile-Specific Considerations
- Touch input vs mouse: use the Input System's pointer abstraction
- Screen DPI varies: use `Screen.dpi` for UI scaling
- Battery and thermal throttling: use Adaptive Performance package
- App size limits: use Addressables for on-demand content
- Accelerometer: `Input.acceleration` or Input System's `Accelerometer.current`

## WebGL (Unity Web)

### Limitations
- No threads (no System.Threading, no Jobs with threads)
- No raw sockets (no TCP/UDP, use WebSocket or HTTP)
- Limited file I/O (no direct filesystem access)
- No clipboard access without user interaction
- Larger initial download size
- Memory is limited by browser tab

### WebGPU (Unity 6)

WebGPU is now supported for Unity Web builds, providing:
- Compute shader support in the browser
- Modern GPU features (storage buffers, indirect draw)
- Better performance than WebGL 2.0

Enable WebGPU in Player Settings > WebGL > Graphics APIs.

### WebGL Best Practices
- Minimize build size with aggressive code stripping
- Use compression (Brotli or Gzip) for build files
- Pre-load critical assets, stream everything else
- Use `Application.ExternalCall` or jslib plugins for browser integration

## Console (PS5, Xbox, Switch)

Console development requires:
- Platform-specific SDK licenses from the manufacturer
- NDA-covered documentation and tools
- Certification compliance testing
- Memory budgets (Switch is particularly constrained)
- Specific input handling for each controller

General console guidance:
- Test early and often on hardware or dev kits
- Profile on target hardware, not just the editor
- Console builds always use IL2CPP
- Follow Technical Requirements Checklists (TRCs) from each manufacturer

## Adaptive Performance

The Adaptive Performance package provides automatic quality scaling:

```csharp
using UnityEngine.AdaptivePerformance;

var ap = Holder.Instance;
if (ap != null && ap.ThermalStatus.ThermalMetrics.WarningLevel > WarningLevel.NoWarning)
{
    ReduceQuality();
}
```

Supports: Samsung (Android), PS4, PS5, Xbox. Adjusts rendering quality, framerate targets, and CPU/GPU workload based on device thermal state.

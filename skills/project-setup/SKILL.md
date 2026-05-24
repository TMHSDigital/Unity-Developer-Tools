---
title: Unity Project Setup
description: Guide for creating and configuring Unity projects with recommended folder structure, assembly definitions, version control, and package management.
globs: ["**/*.asmdef", "**/*.asmref", "**/ProjectSettings/**"]
standards-version: 1.10.0
---

# Unity Project Setup

## Target Version

Unity 6.3 LTS is the recommended baseline for new projects. Unity 6.4 adds opt-in features like Agentic AI tools and core Entities integration. Always use the Unity Hub to manage installations and create projects from verified templates.

## Recommended Folder Structure

```
Assets/
|-- Scripts/
|   |-- Runtime/
|   |-- Editor/
|-- Prefabs/
|-- Scenes/
|-- Materials/
|-- Textures/
|-- Shaders/
|-- Audio/
|-- Animations/
|-- UI/
|-- ScriptableObjects/
|-- Plugins/
|-- Resources/         # Use sparingly, prefer Addressables
|-- StreamingAssets/
|-- Editor Default Resources/
```

Keep `Scripts/Runtime/` for game code and `Scripts/Editor/` for editor-only tools. The `Editor/` folder name is special: Unity excludes it from player builds automatically.

## Assembly Definition Files (.asmdef)

Assembly definitions control how Unity compiles your C# code. Use them to:

- Reduce recompilation time by isolating code into separate assemblies
- Enforce architectural boundaries (game logic cannot reference editor code)
- Control which packages and assemblies your code can access

Recommended assembly layout:

| Assembly | Folder | References |
|----------|--------|------------|
| `MyGame.Runtime` | `Scripts/Runtime/` | Unity defaults |
| `MyGame.Editor` | `Scripts/Editor/` | `MyGame.Runtime`, UnityEditor |
| `MyGame.Tests.EditMode` | `Tests/EditMode/` | `MyGame.Runtime`, NUnit |
| `MyGame.Tests.PlayMode` | `Tests/PlayMode/` | `MyGame.Runtime`, NUnit, UnityEngine.TestRunner |

Always set "Auto Referenced" to true for your main runtime assembly. For editor assemblies, add the platform filter "Editor" only.

## Version Control (.gitignore)

Unity projects generate large amounts of intermediate data. Your .gitignore must exclude:

```
Library/
Temp/
Logs/
obj/
Builds/
UserSettings/
MemoryCaptures/
*.csproj
*.sln
*.suo
*.user
*.pidb
*.booproj
```

Always commit `.meta` files. Unity uses them to track asset GUIDs, import settings, and component references. Losing a .meta file breaks all references to that asset.

## Render Pipeline Selection

- **URP (Universal Render Pipeline)**: Default choice for all new projects in 2026. Covers mobile through high-end console and PC. Active development with Render Graph backend, physical light units, and SCGI (Surface Caching Global Illumination).
- **HDRP (High Definition Render Pipeline)**: Maintenance mode. Use only for existing projects that depend on HDRP-specific features like volumetric fog or area lights. No new major features planned.
- **Built-in Render Pipeline**: Officially deprecated in Unity 6.5. Do not start new projects with Built-in. Migration to URP is recommended for all legacy projects.

## Project Settings Recommendations

### Physics
- Set Fixed Timestep to 0.02 (50Hz) for most games
- Enable "Auto Sync Transforms" only if needed (it has a performance cost)
- Configure Layer Collision Matrix to disable unnecessary collision pairs

### Quality
- Create at least three quality levels: Low, Medium, High
- Tie quality levels to platform defaults (mobile = Low, console = High)
- Use URP Render Pipeline Asset per quality level for granular control

### Player
- Set "Scripting Backend" to IL2CPP for release builds (better performance, harder to decompile)
- Use .NET Standard for API compatibility level in most cases
- Enable "Managed Stripping Level: Medium" or higher to reduce build size

### Input
- Install the Input System package (com.unity.inputsystem) for all new projects
- Set "Active Input Handling" to "Input System Package (New)" in Player Settings
- The legacy Input Manager is not recommended for new development

## Package Manager Essentials

Install these packages for most projects:

| Package | ID | Purpose |
|---------|-----|---------|
| TextMeshPro | `com.unity.textmeshpro` | Text rendering (never use legacy Text) |
| Input System | `com.unity.inputsystem` | Modern input handling |
| Cinemachine | `com.unity.cinemachine` | Camera management |
| Addressables | `com.unity.addressables` | Asset loading and management |
| Unity UI | `com.unity.ugui` | Legacy Canvas UI (still valid for world-space) |
| UI Toolkit | (built-in) | Modern UI for menus, HUD, editor tools |

As of Unity 6.3, packages must be signed for core standards compliance. The Package Manager shows trust indicators for verified packages. Prefer verified packages over unverified third-party sources.

## Project Initialization Checklist

1. Create project from URP template in Unity Hub
2. Set up .gitignore and initialize repository
3. Create folder structure under Assets/
4. Add assembly definitions for Runtime and Editor code
5. Install essential packages via Package Manager
6. Configure Player Settings (scripting backend, input handling)
7. Set up quality levels with per-level URP Render Pipeline Assets
8. Create initial scene with proper lighting setup

---
title: Unity Project Setup
description: Use when the user starts a new Unity project, organizes folders, adds assembly definitions, sets up Git or Unity Version Control, writes a .gitignore, or adds and pins packages. Covers folder layout, asmdefs, version control settings, and Package Manager hygiene.
globs: ["**/*.asmdef", "**/*.asmref", "**/ProjectSettings/**"]
standards-version: 1.10.0
---

# Unity Project Setup

## MCP Tools

Call `analyze_project` with the project root to read the editor version, installed packages, input handling, scripting backend, and existing assembly definitions before recommending changes. If the tools are unavailable, continue without them.

## Target Version

Unity 6.3 LTS (supported until December 2027) is the recommended baseline for new projects. Newer Tech Stream releases add features such as core ECS packages (Unity 6.4); Unity AI (Assistant, the Unity MCP server, and Generators) is in open beta for Unity 6 and later. Always use the Unity Hub to manage installations and create projects from verified templates.

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
- **Built-in Render Pipeline**: Deprecated starting in Unity 6.5 and still available in Unity 6.7 LTS; Unity has not announced a removal version. Do not start new projects with Built-in, and plan a migration to URP for existing ones.

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

From Unity 6.3 the Package Manager checks signatures on tarball packages. Unsigned packages are not blocked; they show a "Signature: Missing" warning. A package with an invalid signature shows an error and should be removed. Prefer Unity-signed and verified packages, and pin third-party packages to a specific version or commit.

## Project Initialization Checklist

1. Create project from URP template in Unity Hub
2. Set up .gitignore and initialize repository
3. Create folder structure under Assets/
4. Add assembly definitions for Runtime and Editor code
5. Install essential packages via Package Manager
6. Configure Player Settings (scripting backend, input handling)
7. Set up quality levels with per-level URP Render Pipeline Assets
8. Create initial scene with proper lighting setup

## Sources

Version-specific statements above were checked on 2026-10-10 against:

- Render pipelines strategy for 2026 (Unity staff): <https://discussions.unity.com/t/render-pipelines-strategy-for-2026/1710004>
- Package signatures (Unity 6.3 manual): <https://docs.unity3d.com/6000.3/Documentation/Manual/upm-signature.html>
- Unity 6 release and support dates: <https://unity.com/releases/unity-6/support>

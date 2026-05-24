<!-- standards-version: 1.9.0 -->

# CLAUDE.md

Project documentation for Claude Code and AI assistants working on this repository.

## Project Overview

Unity Developer Tools is a Cursor IDE plugin for Unity game development. It includes 18 skills, 8 rules, 20 code snippets across C# / HLSL / Visual Scripting, 5 starter templates, and a companion Python MCP server with 4 tools for script scaffolding, Unity API lookup, shader patterns, and platform information.

**Works with:** Cursor (plugin), Claude Code (terminal and in-editor), and any MCP-compatible client.

This is a monorepo. Skills, rules, snippets, templates, and the companion MCP server live in the same repository because Unity development crosses all of those layers in a single workflow.

**Version:** 1.4.6
**License:** CC-BY-NC-ND-4.0
**Author:** TMHSDigital

## Plugin Architecture

```
Unity-Developer-Tools/
  .cursor-plugin/
    plugin.json              # Plugin manifest (version, skills, rules)
  skills/
    <skill-name>/
      SKILL.md               # One skill per directory (kebab-case)
  rules/
    <rule-name>.mdc          # Cursor rule files
  snippets/
    csharp/                  # C# patterns and examples
    shaders/                 # HLSL / ShaderLab patterns
    visual-scripting/        # Visual Scripting graphs and notes
  templates/                 # Starter project archetypes
  mcp-server/
    server.py                # MCP server entry point (Python, FastMCP)
    data/                    # API reference, deprecated patterns, shader props, platform defines
    requirements.txt
  docs/                      # MkDocs Material site (ARCHITECTURE, ROADMAP, GETTING-STARTED)
  .github/
    workflows/               # CI / release / docs / drift-check automation
```

## Skills (18)

| Skill | Description |
|-------|-------------|
| `project-setup` | Folder structure, assembly definitions, version control, and package management for Unity projects |
| `monobehaviour-patterns` | MonoBehaviour lifecycle, async patterns with Awaitable, and common Unity design patterns |
| `scriptableobjects` | Data-driven design with ScriptableObjects (events, variables, runtime sets, configuration) |
| `physics-2d-3d` | Collision, raycasting, layers, and rigidbody management for 2D and 3D projects |
| `ui-development` | UI Toolkit (primary) and Canvas/UGUI, including data binding, styling, responsive layouts |
| `shader-development` | Shader Graph, HLSL, and ShaderLab for URP and HDRP projects |
| `animation-systems` | Animator Controller, Timeline, DOTween, and sprite animation for 2D |
| `audio-systems` | AudioSource, AudioMixer, spatial audio, and audio management patterns |
| `input-systems` | New Input System package and migration guidance from the legacy Input Manager |
| `networking` | Multiplayer networking with Netcode for GameObjects, Netcode for Entities, Mirror, Photon Fusion |
| `editor-scripting` | Custom inspectors, editor windows, property drawers, gizmos, Scene View overlays via UI Toolkit |
| `performance-optimization` | CPU, GPU, memory, and profiling tools (Profiler, Memory Profiler, Frame Debugger) |
| `render-pipeline-detection` | Detect and adapt to URP, HDRP, or Built-in pipelines |
| `ecs-dots` | Entity Component System with Unity Entities, Jobs, and Burst |
| `visual-scripting` | Script Graphs, State Graphs, Subgraphs, and custom units |
| `testing` | Unity Test Framework 2.x with Edit Mode and Play Mode tests, async Awaitable support |
| `addressables-assets` | Async loading, memory management, and remote content delivery via Addressables |
| `platform-targeting` | Scripting defines, build settings, and cross-platform considerations |

## Rules (8)

| Rule | Scope | Description |
|------|-------|-------------|
| `csharp-unity-conventions.mdc` | `**/*.cs` | C# coding conventions for Unity development |
| `monobehaviour-lifecycle.mdc` | `**/*.cs` | Correct usage of MonoBehaviour lifecycle methods |
| `performance-rules.mdc` | `**/*.cs` | Performance optimization rules (allocations, FindObject, tight loops) |
| `naming-conventions.mdc` | `**/*.cs` | Naming conventions for Unity C# code |
| `serialization-rules.mdc` | `**/*.cs` | Unity serialization best practices (`[SerializeField]`, ISerializationCallbackReceiver) |
| `shader-conventions.mdc` | `**/*.shader`, `**/*.hlsl`, `**/*.cginc`, `**/*.shadergraph` | Conventions for Unity shader development (HLSLPROGRAM, SRP Batcher) |
| `visual-scripting-conventions.mdc` | `**/*.asset` | Best practices for Unity Visual Scripting graphs |
| `security-and-builds.mdc` | `**/*.cs`, `**/*.json`, `**/*.asset` | Security and build configuration rules (no hardcoded secrets, build target hygiene) |

## MCP Server (4 tools)

The companion MCP server is Python-based (FastMCP). It exposes Unity-aware tools that read from local data files (`mcp-server/data/`) and accept agent-supplied parameters.

| Tool | Description |
|------|-------------|
| `scaffold_script` | Generate a structured C# script (MonoBehaviour, ScriptableObject, EditorWindow, custom inspector, property drawer, interface, state machine, test) with recommended folder placement |
| `lookup_api` | Search the Unity API reference (name, namespace, signature, examples) with optional category filter and deprecated-pattern warnings |
| `shader_helper` | Fetch shader patterns and property setups for common effects (dissolve, outline, toon, water, hologram, fresnel) per render pipeline |
| `platform_info` | Get platform-specific scripting defines, capabilities, limitations, and recommendations (Windows, macOS, Linux, Android, iOS, WebGL, PS5, Xbox, Switch) |

## Development Workflow

### Plugin development (symlink)

**macOS / Linux:**
```bash
ln -s "$(pwd)" ~/.cursor/plugins/unity-developer-tools
```

**Windows (PowerShell as Admin):**
```powershell
New-Item -ItemType SymbolicLink -Path "$env:USERPROFILE\.cursor\plugins\unity-developer-tools" -Target (Get-Location)
```

### MCP server development

```bash
cd mcp-server
pip install -r requirements.txt
python server.py
```

### Running validation

```bash
# JSON schema and content-count checks (run by CI)
python .github/scripts/validate_plugin.py
```

## Release Workflow

Releases are automated. The `release.yml` workflow:

1. Reads conventional commits since the last tag.
2. Computes the next semver bump (PATCH for `fix:`, MINOR for `feat:`, MAJOR for `BREAKING CHANGE`).
3. Updates `plugin.json` `version` and the README version badge.
4. Creates the tag, the GitHub Release, and floating major / minor tags.
5. Invokes `release-doc-sync` to update `**Version:**` in this file and prepend a CHANGELOG entry.

Do not hand-edit `plugin.json` `version`, the README badge, or the `**Version:**` line above. The release pipeline owns them.

## Key Conventions

- **No em dashes.** Use regular dashes (`-`) or rewrite the sentence. CI flags em and en dashes in markdown.
- **No hardcoded credentials.** Use environment variables, `EditorUserSettings`, or a secrets store. CI flags suspicious patterns.
- **Skill frontmatter:** `title`, `description`, `globs` (when path-scoped), and `standards-version`.
- **Rule frontmatter:** `title`, `description`, `globs`, `alwaysApply`, and `standards-version`.
- **Snippets:** must compile against Unity 6.x and use modern APIs (Awaitable, `FindFirstObjectByType`, UI Toolkit). No placeholder credentials.
- **Templates:** every template needs a top-level `README.md` describing usage, scripts, and any project setup notes (assembly definitions, package dependencies).
- **MCP tool naming:** snake_case Python functions decorated with `@mcp.tool()`.

## Unity Reference Quick Links

| Resource | Use |
|----------|-----|
| `docs.unity3d.com/Manual/index.html` | Authoritative Unity manual |
| `docs.unity3d.com/ScriptReference/index.html` | Scripting API reference |
| `docs.unity3d.com/Packages/` | Package-specific manuals (URP, HDRP, Input System, Netcode, Entities) |
| `mcp-server/data/unity_api_common.json` | Local Unity API quick-reference index |
| `mcp-server/data/deprecated_patterns.json` | Deprecation map (legacy -> replacement) |
| `mcp-server/data/shader_properties.json` | Shader effect patterns and property setups |
| `mcp-server/data/platform_defines.json` | Platform scripting defines and capabilities |

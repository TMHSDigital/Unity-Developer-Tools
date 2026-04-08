# Unity Developer Tools

![Version](https://img.shields.io/badge/version-1.1.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)

AI-powered development toolkit for Unity. Scaffold scripts, look up APIs, write shaders, and build games with best-practice rules for C#, Visual Scripting, and HLSL.

## What This Is

A Cursor IDE plugin that bundles 18 skills, 8 rules, 20 snippets, 5 templates, and an MCP server with 4 tools - all focused on Unity game development. Whether you are a beginner learning Unity, a solo dev at a game jam, or an intermediate developer wanting productivity tools and best-practice enforcement, this plugin provides an AI-assisted environment optimized for building games, tools, and interactive experiences.

## Quick Start

1. Clone this repository
2. Open the folder in Cursor IDE
3. The plugin loads automatically - skills, rules, and snippets are available immediately
4. For MCP tools, install Python dependencies: `pip install -r mcp-server/requirements.txt`
5. Start building

## Features

### Skills (18)

| Skill | Description |
|-------|-------------|
| Project Setup | Unity project configuration, folder structure, assembly definitions |
| MonoBehaviour Patterns | Lifecycle, Awaitable async, common design patterns |
| ScriptableObjects | Data-driven architecture, events, variables, runtime sets |
| Physics (2D/3D) | Rigidbody, collisions, raycasting, layers |
| UI Development | UI Toolkit (primary) and Canvas/UGUI |
| Shader Development | Shader Graph, HLSL, ShaderLab for URP |
| Animation Systems | Animator, DOTween, Timeline, sprite animation |
| Audio Systems | AudioSource, AudioMixer, spatial audio |
| Input Systems | New Input System (primary), legacy migration |
| Networking | Netcode for GameObjects, Netcode for Entities, Photon, Mirror |
| Editor Scripting | Custom inspectors, editor windows, overlays, gizmos |
| Performance Optimization | CPU, GPU, memory, profiling tools |
| Render Pipeline Detection | URP, HDRP, Built-in detection and adaptation |
| ECS/DOTS | Entity Component System, Jobs, Burst |
| Visual Scripting | Script Graphs, State Graphs, Subgraphs |
| Testing | Edit Mode and Play Mode tests with UTF 2.x |
| Addressables | Async asset loading, groups, remote content |
| Platform Targeting | Platform defines, build settings, cross-platform |

### Rules (8)

- C# Unity Conventions
- MonoBehaviour Lifecycle
- Performance Rules
- Naming Conventions
- Serialization Rules
- Shader Conventions
- Visual Scripting Conventions
- Security and Builds

### Snippets (20)

- 15 C# snippets (MonoBehaviour, Singleton, Object Pool, ScriptableObject, Coroutine, Events, State Machine, Custom Inspector, Editor Window, Property Drawer, Input System, Raycasting, Async/Await, Interfaces, Save/Load)
- 4 shader snippets (Unlit URP, Surface Legacy, URP Lit PBR, HLSL Vertex/Fragment)
- 1 Visual Scripting guide

### Templates (5)

- 2D Platformer (player controller, game manager, camera follow)
- 3D FPS (FPS controller, weapon system, game manager)
- UI Menu System (UI Toolkit menus, settings with persistence)
- ScriptableObject Architecture (events, variables, runtime sets)
- Editor Tool (level builder window with UI Toolkit)

### MCP Tools (4)

- **scaffold_script** - Generate C# scripts following Unity conventions
- **lookup_api** - Search the Unity API reference database
- **shader_helper** - Get shader code patterns for common effects
- **platform_info** - Get platform-specific defines and build tips

## Supported Workflows

- MonoBehaviour (classic Unity scripting)
- ScriptableObject Architecture (data-driven design)
- ECS/DOTS (high-performance data-oriented)
- Visual Scripting (node-based for designers)
- Editor Tooling (custom inspectors, windows, overlays)

## Supported Render Pipelines

- **URP** (Universal Render Pipeline) - Primary, recommended for all new projects
- **HDRP** (High Definition Render Pipeline) - Maintenance mode, existing projects only
- **Built-in** (Legacy) - Deprecated as of Unity 6.5, migration guidance provided

## MCP Server Setup

The MCP server is configured in `.cursor/mcp.json` and starts automatically when Cursor invokes a tool.

Prerequisites:
```bash
pip install -r mcp-server/requirements.txt
```

## Project Structure

```
Unity-Developer-Tools/
|-- .cursor-plugin/plugin.json      # Plugin manifest
|-- .cursor/mcp.json                # MCP server configuration
|-- skills/                         # 18 SKILL.md files
|-- rules/                          # 8 .mdc rule files
|-- snippets/
|   |-- csharp/                     # 15 C# code snippets
|   |-- shaders/                    # 4 shader snippets
|   |-- visual-scripting/           # VS graph pattern guide
|-- templates/                      # 5 starter project templates
|-- mcp-server/
|   |-- server.py                   # MCP server entry point
|   |-- tools/                      # Tool implementations
|   |-- data/                       # API reference and data files
|-- docs/                           # Documentation
```

## Roadmap

See [docs/ROADMAP.md](docs/ROADMAP.md) for planned milestones.

## Contributing

See [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.

## License

MIT - see [LICENSE](LICENSE) for details.

## Credits

- Built by [TMHSDigital](https://github.com/TMHSDigital)
- Unity documentation: https://docs.unity3d.com/Manual/
- Unity Scripting API: https://docs.unity3d.com/ScriptReference/
- Cursor plugin specification: https://github.com/cursor/plugins

# Getting Started

## Prerequisites

- [Cursor IDE](https://cursor.sh) installed
- Python 3.10+ (for MCP server tools)
- Unity 6.3 LTS or later (for building actual Unity projects)

## Installation

The plugin is installed once into Cursor's local plugins folder. You then open **your own Unity project** in Cursor, not this repository.

1. Clone the plugin into Cursor's local plugins folder:

   **macOS / Linux:**
   ```bash
   git clone https://github.com/TMHSDigital/Unity-Developer-Tools.git ~/.cursor/plugins/local/unity-developer-tools
   ```

   **Windows (PowerShell):**
   ```powershell
   git clone https://github.com/TMHSDigital/Unity-Developer-Tools.git "$env:USERPROFILE\.cursor\plugins\local\unity-developer-tools"
   ```

   Or download the zip from the [latest release](https://github.com/TMHSDigital/Unity-Developer-Tools/releases/latest) and extract it into that same folder, so that `.cursor-plugin/plugin.json` sits directly inside `unity-developer-tools/`. Do not extract it into a Unity project.

2. Install the MCP server dependencies with the same Python that `python` runs:
   ```bash
   python -m pip install -r ~/.cursor/plugins/local/unity-developer-tools/mcp-server/requirements.txt
   ```
   On Windows, use `"$env:USERPROFILE\.cursor\plugins\local\unity-developer-tools\mcp-server\requirements.txt"`.

3. Restart Cursor, or run **Developer: Reload Window** from the command palette.

4. Open your Unity project folder (the one containing `Assets/` and `ProjectSettings/`) with **File > Open Folder**.

### Verify it works

1. Open **Customize** in the Cursor sidebar. Unity Developer Tools should be listed with its skills, rules, and the `unity-dev-tools` MCP server.
2. Open any `.cs` file in your project. The C# rules apply to it automatically.
3. Ask the agent: *"What are the scripting defines for WebGL?"* It should call the `platform_info` tool and answer with `UNITY_WEBGL`.

### Updating

Run `git pull` inside `~/.cursor/plugins/local/unity-developer-tools`, then reload Cursor. If you installed from a zip, replace the folder with the new release.

## Using Skills

Skills provide AI context when working with specific file types. For example:

- Open a `.cs` file and the AI knows about MonoBehaviour lifecycle, performance rules, and naming conventions
- Open a `.shader` file and the AI knows about HLSL conventions, SRP Batcher, and URP includes
- Ask the AI to "create a player controller" and it will use the project-setup and MonoBehaviour skills

## Using Rules

Rules are automatically applied based on file type:

- **Always-on rules** (lifecycle, performance, naming): active on all `.cs` files
- **Opt-in rules** (serialization, shaders, security): active when matching file globs

## Using Snippets

Reference snippets when asking the AI for code patterns:

- "Use the singleton pattern from the snippets"
- "Create an object pool like the snippet"
- "Set up input handling following the input system snippet"

## Using Templates

Templates provide complete starter projects:

1. Copy a template folder into your Unity project's Assets directory
2. The scripts are ready to attach to GameObjects
3. Follow the README in each template for setup instructions

## Using MCP Tools

Ask the AI to use MCP tools naturally:

- "Scaffold a MonoBehaviour called PlayerHealth"
- "Look up the Rigidbody API"
- "Show me shader properties for a dissolve effect"
- "What are the platform limitations for WebGL?"

## Troubleshooting

**The plugin does not appear in Customize**
- Check the path: `.cursor-plugin/plugin.json` must be at `~/.cursor/plugins/local/unity-developer-tools/.cursor-plugin/plugin.json`. A zip extracted into an extra nested folder will not load.
- Symlinks are skipped when they point to a folder outside `~/.cursor/plugins/local`. Clone or copy the plugin into that folder instead.
- On Cursor Teams or Enterprise, an admin must enable **Allow Local Plugin Imports** (Dashboard > Settings > Security & Identity > Marketplace and Plugins).
- Reload the window after installing.

**The `unity-dev-tools` MCP server shows an error or no tools**
- `python` must be on your PATH. Run `python --version`; it must report 3.10 or newer. On macOS, if only `python3` exists, install Python from python.org or a package manager that provides `python`.
- `ModuleNotFoundError: No module named 'mcp'`: install the requirements with the same interpreter, using `python -m pip install -r .../mcp-server/requirements.txt`.
- `Missing data file`: the plugin folder is incomplete. Re-clone it or extract the release zip again.

**Rules do not apply to my scripts**
- Make sure the Cursor workspace is your Unity project, not the plugin repository. Rules are matched against files in the open workspace (for example, `**/*.cs`).

**Unity reports compile errors after copying files**
- Copy individual snippets or a single template folder into `Assets/`, never the whole plugin. Each template README lists the packages it needs, such as the Input System.

## Next Steps

- Explore the [Architecture](ARCHITECTURE.md) to understand plugin structure
- Check the [Roadmap](ROADMAP.md) for upcoming features
- Read [Contributing](CONTRIBUTING.md) if you want to help improve the plugin

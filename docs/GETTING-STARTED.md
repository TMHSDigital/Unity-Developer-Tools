# Getting Started

## Prerequisites

- [Cursor IDE](https://cursor.sh) installed
- Python 3.10+ (for MCP server tools)
- Unity 6.3 LTS or later (for building actual Unity projects)

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/TMHSDigital/Unity-Developer-Tools.git
   ```

2. Open the cloned folder in Cursor IDE

3. The plugin loads automatically. You should see skills and rules activate when editing C# or shader files.

4. (Optional) Install MCP server dependencies for tool access:
   ```bash
   pip install -r mcp-server/requirements.txt
   ```

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

## Next Steps

- Explore the [Architecture](ARCHITECTURE.md) to understand plugin structure
- Check the [Roadmap](ROADMAP.md) for upcoming features
- Read [Contributing](CONTRIBUTING.md) if you want to help improve the plugin

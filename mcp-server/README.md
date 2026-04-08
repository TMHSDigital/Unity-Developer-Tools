# Unity Developer Tools MCP Server

A Model Context Protocol server providing Unity development tools for the Cursor IDE.

## Tools

### scaffold_script
Generate well-structured C# scripts following Unity conventions.
- **type**: monobehaviour, scriptableobject, editor-window, custom-inspector, property-drawer, interface, state-machine, test
- **name**: Class name for the generated script
- **namespace**: Optional namespace (default: MyGame)

### lookup_api
Search the Unity API reference database for classes, methods, and usage patterns.
- **query**: Search term (class name, method name, or keyword)
- **category**: Optional filter (physics, ui, animation, audio, rendering, input, networking, editor)

### shader_helper
Get shader code patterns and property setups for common effects.
- **effect**: Effect name (dissolve, outline, toon, water, hologram, fresnel)
- **pipeline**: Target render pipeline (urp, hdrp, builtin)

### platform_info
Get platform-specific scripting defines, capabilities, and build recommendations.
- **platform**: Target platform (windows, macos, linux, android, ios, webgl, ps5, xbox, switch)

## Running

The server is started automatically by Cursor via the configuration in `.cursor/mcp.json`.

Manual start:
```bash
pip install -r requirements.txt
python server.py
```

## Data Files

- `unity_api_common.json` - Common Unity API reference (200+ classes and methods)
- `shader_properties.json` - Built-in shader properties and effect patterns
- `platform_defines.json` - Platform scripting defines and capabilities
- `lifecycle_order.json` - MonoBehaviour execution order reference
- `deprecated_patterns.json` - Legacy-to-modern API mapping

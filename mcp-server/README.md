# Unity Developer Tools MCP Server

A Model Context Protocol server providing Unity development tools for the Cursor IDE.

## Tools

### scaffold_script
Generate well-structured C# scripts following Unity conventions.
- **type**: monobehaviour, scriptableobject, editor-window, custom-inspector, property-drawer, interface, state-machine, test
- **name**: Class name for the generated script (must be a valid C# identifier)
- **namespace**: Optional namespace (default: MyGame)
- **target_type**: Type inspected or drawn, for custom-inspector and property-drawer. Defaults to the name without its Editor/Inspector/Drawer suffix (`PlayerEditor` -> `Player`)

### lookup_api
Search the Unity API reference database for classes, methods, and usage patterns. Multi-word queries match entries containing every word; exact name matches rank first.
- **query**: Search term (class name, method name, or keyword)
- **category**: Optional filter (general, physics, ui, animation, audio, rendering, input, networking, editor)

### shader_helper
Get shader code patterns and property setups for common effects. Hand-written HLSL currently targets URP; HDRP and Built-in requests return properties and Shader Graph guidance only.
- **effect**: Effect name (dissolve, outline, toon, water, hologram, fresnel)
- **pipeline**: Target render pipeline (urp, hdrp, builtin)

### platform_info
Get platform-specific scripting defines, capabilities, and build recommendations.
- **platform**: Target platform (windows, macos, linux, android, ios, webgl, ps5, xbox, switch)

## Running

The plugin registers the server in `mcp.json` at the plugin root, and Cursor starts it automatically once the plugin is installed.

Manual start:
```bash
pip install -r requirements.txt
python server.py
```

The server reads its data from `data/` next to `server.py`, so it can be started from any directory. Set `UNITY_DATA_PATH` to use a different data folder. If a data file is missing, the server exits with an error instead of returning empty results.

## Testing

```bash
pip install -r requirements-dev.txt
python -m pytest tests
```

The suite covers every tool and includes a stdio smoke test that starts the server and calls it through the MCP client.

## Data Files

- `unity_api_common.json` - Curated Unity 6 API reference (75 entries across 9 categories)
- `shader_properties.json` - Built-in shader properties and effect patterns
- `platform_defines.json` - Platform scripting defines and capabilities
- `lifecycle_order.json` - MonoBehaviour execution order reference
- `deprecated_patterns.json` - Legacy-to-modern API mapping

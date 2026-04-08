# Architecture

## Plugin Structure

This is a single Cursor IDE plugin following the standard plugin specification. All components live at the repository root.

```
.cursor-plugin/plugin.json    <- Plugin manifest (name, version, skills, rules)
.cursor/mcp.json              <- MCP server configuration
skills/                       <- AI context files (SKILL.md with YAML frontmatter)
rules/                        <- Convention enforcement (.mdc with frontmatter)
snippets/                     <- Production-ready code patterns
templates/                    <- Starter project scaffolds
mcp-server/                   <- Python MCP server with tools and data
docs/                         <- Documentation
```

## Component Types

### Skills (skills/*.md)

Skills provide domain knowledge to the AI. Each SKILL.md has:
- YAML frontmatter: title, description, globs (file patterns that activate it)
- Markdown body: comprehensive reference material

Skills do not enforce rules - they inform the AI about best practices, APIs, and patterns so it can generate better code.

### Rules (rules/*.mdc)

Rules enforce coding standards. Each .mdc file has:
- Frontmatter: title, description, globs, alwaysApply
- Body: specific do/don't rules

Rules with `alwaysApply: true` are active on every matching file. Rules with `alwaysApply: false` are activated when the file matches the glob pattern.

### Snippets (snippets/*)

Ready-to-use code patterns organized by language:
- `csharp/` - Unity C# patterns
- `shaders/` - HLSL and ShaderLab templates
- `visual-scripting/` - Graph pattern documentation

### Templates (templates/*)

Complete starter project scaffolds. Each template is a self-contained directory with scripts and a README explaining setup.

### MCP Server (mcp-server/)

A Python FastAPI server implementing the Model Context Protocol. Provides 4 tools:
- `scaffold_script` - Generate scripts from templates
- `lookup_api` - Search Unity API reference data
- `shader_helper` - Get shader effect patterns
- `platform_info` - Get platform-specific information

Data files in `mcp-server/data/` provide the reference databases:
- `unity_api_common.json` - Common Unity API entries
- `shader_properties.json` - Shader effect patterns
- `platform_defines.json` - Platform scripting defines
- `lifecycle_order.json` - MonoBehaviour execution order
- `deprecated_patterns.json` - Legacy-to-modern API mapping

## Version Management

The version in `.cursor-plugin/plugin.json` is the source of truth. The release workflow auto-bumps it based on conventional commit prefixes.

## Design Principles

1. **URP-first**: All rendering content defaults to URP as the standard pipeline
2. **Modern patterns**: Awaitable over coroutines, UI Toolkit over IMGUI, HLSLPROGRAM over CGPROGRAM
3. **Deprecated awareness**: All tools and skills warn about deprecated APIs and suggest modern replacements
4. **Platform-aware**: Content adapts to the target platform's capabilities and limitations
5. **Zero credentials**: No API keys, tokens, or secrets anywhere in the codebase

# AGENTS.md

This file tells AI coding agents how the Unity Developer Tools repo works and how to contribute correctly.

## Repository overview

This is a Cursor IDE plugin for Unity game development. It contains:

- **`.cursor-plugin/plugin.json`** - plugin manifest (version, skills, rules)
- **`skills/`** - 18 SKILL.md files teaching the AI Unity development knowledge
- **`rules/`** - 8 .mdc rule files enforcing coding conventions
- **`snippets/`** - 20 code snippet files (C#, shaders, visual scripting guide)
- **`templates/`** - 5 starter project templates (2D platformer, 3D FPS, UI menu, SO architecture, editor tool)
- **`mcp-server/`** - Python MCP server with 4 tools and JSON data files
- **`docs/`** - ARCHITECTURE.md, ROADMAP.md, CONTRIBUTING.md, GETTING-STARTED.md
- **`CHANGELOG.md`** - manually maintained release history
- **`.github/workflows/`** - CI/CD automation

## Branching and commit model

- **Single branch**: `main` only. No develop/release branches.
- **Conventional commits** are required. The release workflow parses them:
  - `feat:` or `feat(scope):` - triggers a **minor** version bump
  - `feat!:` or `BREAKING CHANGE` - triggers a **major** version bump
  - Everything else (`fix:`, `chore:`, `docs:`, `refactor:`, etc.) - triggers a **patch** bump
- Commit messages should be concise and describe the "why", not the "what".

## CI/CD workflows

### `validate.yml` (runs on PR and push to main)

Checks:
- JSON validity for plugin.json and MCP data files
- Plugin manifest required fields and skill/rule file existence
- Content counts in README match actual files on disk (skills, rules, snippets, templates)
- Em dash and en dash detection (use hyphens, not em/en dashes)
- Hardcoded credential patterns
- Python syntax for all MCP server modules

### `release.yml` (runs on push to main, ignores docs/md/github changes)

Automatic flow:
1. Reads current version from `plugin.json`
2. Determines bump type from conventional commit messages since last tag
3. Computes new semver version
4. Updates `plugin.json` version and `README.md` version badge
5. Commits with `[skip ci]` to prevent re-triggering
6. Creates git tag `vX.Y.Z`
7. Creates GitHub Release with grouped release notes

### `stale.yml`

Marks issues/PRs as stale after inactivity and closes them after further inactivity.

## Version management

- The **source of truth** for the current version is `.cursor-plugin/plugin.json`.
- The release workflow auto-bumps it and the README badge on every qualifying push to main.
- Never manually change the version.
- **CHANGELOG.md is manually maintained.** Update it when making significant changes.

## Code conventions

- **No em dashes or en dashes** - use hyphens or rewrite. CI will reject them.
- **No hardcoded credentials** - CI scans for password/token/api_key patterns.
- **Target Unity 6.x** - use modern APIs (Awaitable, FindFirstObjectByType, HLSLPROGRAM, UI Toolkit).
- **URP is default** - all shader and rendering content should default to URP.
- Python code in `mcp-server/` must pass `py_compile`.
- Snippets, templates, and skills should be accurate to the current Unity 6.x APIs.

## Adding content

### New skill

1. Create `skills/<skill-name>/SKILL.md` with YAML frontmatter (title, description, globs)
2. Add the path to `plugin.json` under `"skills"`
3. Update counts in README.md stats and skills table
4. Use `fix:` or `feat:` commit prefix depending on scope

### New rule

1. Create `rules/<rule-name>.mdc` with frontmatter (`description`, `globs`, `alwaysApply`)
2. Add the path to `plugin.json` under `"rules"`

### New snippet

1. Add the file to `snippets/<language>/` (csharp, shaders, visual-scripting)
2. Include a header comment explaining what the snippet does
3. Update counts in README.md

### New template

1. Create `templates/<template-name>/` with C# scripts and a README.md
2. Follow existing template patterns for consistency

## MCP server

- Entry point: `mcp-server/server.py`
- Tool modules: `mcp-server/tools/` (placeholder modules)
- Data: `mcp-server/data/` (JSON reference databases)
- Dependencies: `mcp-server/requirements.txt`

The MCP server is configured in `.cursor/mcp.json` and starts automatically when Cursor invokes a tool.

## Key technical facts

- Unity 6.3 LTS is the primary target. Unity 6.4 adds opt-in features.
- URP is the default render pipeline. HDRP is in maintenance mode. Built-in is deprecated in 6.5.
- Awaitable replaces coroutines for new async code (single-await pooling rule).
- ECS/DOTS is now a core engine package (Entities 1.4+), not experimental.
- FindObjectOfType is deprecated; use FindFirstObjectByType.
- CGPROGRAM is deprecated; use HLSLPROGRAM for URP/HDRP shaders.
- The MCP server uses Python FastMCP with 4 tools and 5 JSON data files.

## License

MIT. All contributions fall under this license.

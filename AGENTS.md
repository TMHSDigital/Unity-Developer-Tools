<!-- standards-version: 1.10.0 -->

# AGENTS.md

This file tells AI coding agents how the Unity Developer Tools repo works and how to contribute correctly.

## Repository overview

This is a Cursor IDE plugin for Unity game development. It contains:

- **`.cursor-plugin/plugin.json`** - plugin manifest (version, skills, rules)
- **`skills/`** - 18 SKILL.md files teaching the AI Unity development knowledge
- **`rules/`** - 8 .mdc rule files enforcing coding conventions
- **`snippets/`** - 20 code snippet files (C#, shaders, visual scripting guide)
- **`templates/`** - 5 starter project templates (2D platformer, 3D FPS, UI menu, SO architecture, editor tool)
- **`mcp-server/`** - Python MCP server with 5 tools and JSON data files
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

Each check job calls `.github/scripts/validate_plugin.py` (run it locally with no arguments to run every check):

| Job | What it checks |
|-----|----------------|
| validate-json | `validate_plugin.py manifest data`: required manifest fields, kebab-case name, semver version, listed skills and rules exist (and every file on disk is listed), MCP registration, and schemas of all MCP data files |
| validate-skills | `validate_plugin.py skills`: SKILL.md frontmatter (title, description, globs, standards-version) and minimum body length |
| validate-rules | `validate_plugin.py rules`: .mdc frontmatter, and no `alwaysApply: true` combined with globs |
| validate-content | `validate_plugin.py content`: em/en dashes, hardcoded credentials, C# 10+ syntax or advice, empty snippets |
| validate-templates | `validate_plugin.py templates`: each template has README.md and .cs files |
| validate-counts | `validate_plugin.py counts`: skill, rule, snippet, template, tool, and workflow counts in README, CLAUDE.md, AGENTS.md, .cursorrules, and docs |
| validate-python | ruff lint and the pytest suite (including an MCP stdio smoke test) on Python 3.10 and 3.12 |
| compile-csharp | Compiles every C# snippet and template against Unity 6 reference assemblies (player and editor passes) |

### `release.yml` (runs on push to main, ignores docs/md/github changes)

Automatic flow:
1. Reads current version from `plugin.json`
2. Determines bump type from conventional commit messages since last tag
3. Computes new semver version
4. Updates `plugin.json` version and `README.md` version badge
5. Builds a distributable zip of the plugin (excludes __pycache__)
6. Commits with `[skip ci]` to prevent re-triggering
7. Creates git tag `vX.Y.Z`
8. Creates GitHub Release with grouped release notes and zip artifact attached

Has a concurrency guard - only one release can run at a time.

### `update-unity-api.yml` (weekly on Monday 06:00 UTC, or manual dispatch)

1. Runs `.github/scripts/refresh_unity_data.py` to fetch latest lifecycle method docs
2. Validates all MCP data files against their schemas
3. If data changed, commits and pushes with `chore:` prefix (patch bump)

Do not manually edit data files that this workflow manages. To change the refresh logic, edit `.github/scripts/refresh_unity_data.py`.

### `label-sync.yml` (runs on PR open/sync)

Automatically labels PRs based on changed file paths:
- `skills/` -> `skills` label
- `rules/` -> `rules` label
- `snippets/` -> `snippets` label
- `templates/` -> `templates` label
- `mcp-server/` -> `mcp-server` label
- `docs/` -> `documentation` label
- `.github/` -> `ci` label
- Plugin config files -> `plugin-config` label

### `deploy-docs.yml` (runs on push to main, or manual dispatch)

Builds and deploys the MkDocs Material documentation site to GitHub Pages.

1. Copies CHANGELOG.md, skills/, and mcp-server/README.md into docs/ (MkDocs requires all content under docs/)
2. Copies logo and favicon assets into docs/assets/
3. Builds with `mkdocs build --strict`
4. Uploads and deploys to GitHub Pages

The site lives at `https://tmhsdigital.github.io/Unity-Developer-Tools/`.

When adding a new skill, also add it to the `nav:` section in `mkdocs.yml`.

### `stale.yml` (weekly on Sunday midnight UTC)

Marks issues/PRs as stale after inactivity and closes them after further inactivity. Exempts `pinned`, `security`, and `bug` labels.

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
- Tests: `mcp-server/tests/` (`python -m pytest mcp-server/tests`)
- Data: `mcp-server/data/` (JSON reference databases)
- Dependencies: `mcp-server/requirements.txt`

The MCP server is registered by the plugin in `mcp.json` (referenced from `.cursor-plugin/plugin.json`) and starts automatically when Cursor invokes a tool.

## Key technical facts

- Unity 6.3 LTS is the primary target. Unity 6.4 adds opt-in features.
- URP is the default render pipeline. HDRP is in maintenance mode. Built-in is deprecated in 6.5.
- Awaitable replaces coroutines for new async code (single-await pooling rule).
- ECS/DOTS is now a core engine package (Entities 1.4+), not experimental.
- FindObjectOfType is deprecated; use FindFirstObjectByType.
- CGPROGRAM is deprecated; use HLSLPROGRAM for URP/HDRP shaders.
- The MCP server uses Python FastMCP with 5 tools and 5 JSON data files.

## License

CC-BY-NC-ND-4.0. All contributions fall under this license.

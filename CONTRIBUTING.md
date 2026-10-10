# Contributing to Unity Developer Tools

Thanks for helping improve this plugin. This document describes how to set up locally, extend skills and rules, and submit changes.

By participating you agree to the [Code of Conduct](https://github.com/TMHSDigital/Unity-Developer-Tools/blob/main/CODE_OF_CONDUCT.md). Report security problems privately as described in the [Security Policy](https://github.com/TMHSDigital/Unity-Developer-Tools/blob/main/SECURITY.md), not in a public issue. Questions and ideas go in [Discussions](https://github.com/TMHSDigital/Unity-Developer-Tools/discussions).

## Getting Started

Cursor loads local plugins from `~/.cursor/plugins/local/<name>` and skips symlinks that point outside that folder, so fork the repository and clone your fork straight into the local plugins folder:

**macOS / Linux:**

```bash
git clone https://github.com/<your-username>/Unity-Developer-Tools.git ~/.cursor/plugins/local/unity-developer-tools
cd ~/.cursor/plugins/local/unity-developer-tools
```

**Windows (PowerShell):**

```powershell
git clone https://github.com/<your-username>/Unity-Developer-Tools.git "$env:USERPROFILE\.cursor\plugins\local\unity-developer-tools"
cd "$env:USERPROFILE\.cursor\plugins\local\unity-developer-tools"
```

Create a branch for your work (`git checkout -b feat/my-change`), then run **Developer: Reload Window** in Cursor after changing the manifest, rules, skills, or `mcp.json`.

## Plugin Structure

The repo is organized as a Cursor plugin with **18 skills** and **8 rules**, plus snippets, templates, and a companion MCP server.

```text
.cursor-plugin/
  plugin.json
skills/
  <skill-name-kebab>/
    SKILL.md
rules/
  <rule-name>.mdc
snippets/
  csharp/
  shaders/
  visual-scripting/
templates/
mcp-server/
  server.py
  data/
docs/
.github/
  workflows/
```

- **`plugin.json`** - manifest (name, version, paths to skills/rules).
- **`skills/`** - one directory per skill; each contains `SKILL.md`.
- **`rules/`** - Cursor rules as `.mdc` files with YAML frontmatter.
- **`snippets/`** - C#, HLSL/ShaderLab, and Visual Scripting examples organized by language.
- **`templates/`** - starter project archetypes (2D platformer, 3D FPS, UI menu, ScriptableObject architecture, editor tool).
- **`mcp-server/`** - Python MCP server exposing Unity-aware tools (script scaffolding, API lookup, shader patterns, platform info, project analysis), with tests in `mcp-server/tests/`.

## Adding a Skill

1. Add a **kebab-case** directory under `skills/`, e.g. `skills/unity-example-flow/`.
2. Create **`SKILL.md`** with YAML frontmatter including `title`, `description`, `standards-version`, and `globs` (path-scoped patterns where applicable, e.g. `["**/*.cs"]`, `["**/*.shader", "**/*.hlsl"]`).
3. In the body, include sections (use `##` headings) such as:
   - **Overview / Why** - when the skill applies and what problem it solves.
   - **Required Inputs** - what the agent or user must provide.
   - **Workflow** - step-by-step guidance.
   - **Key References** - Unity manual links, package names, or repo paths.
   - **Example Interaction** - short example prompt/response pattern.
   - **MCP Usage** - when to use the companion MCP server, if relevant.
   - **Common Pitfalls** - mistakes to avoid (deprecated APIs, render-pipeline confusion, MonoBehaviour lifecycle traps, etc.).
   - **See Also** - links to related skills or rules.

Match tone, formatting, and frontmatter style of existing skills in this repo.

## Adding a Rule

1. Add a **`.mdc`** file under `rules/`, e.g. `rules/unity-example.mdc`.
2. Start with YAML **frontmatter**:
   - `title` - one-line summary.
   - `description` - longer description for humans and tooling.
   - `globs` - glob patterns scoping the rule (e.g. `["**/*.cs"]`, `["**/*.shader", "**/*.hlsl", "**/*.cginc", "**/*.shadergraph"]`). Keep them narrow: `**/*.asset` matches every material, ScriptableObject, and settings file in a project.
   - `alwaysApply: false`. Cursor ignores `globs` on `alwaysApply: true` rules and injects them into every conversation, so CI rejects that combination. Use `alwaysApply: true` only with `globs: []` for guidance that truly applies everywhere.
   - `standards-version` - copy it from an existing rule.

3. Below the frontmatter, write the rule content in Markdown (constraints, patterns, anti-patterns).
4. Register the file under `rules` in `.cursor-plugin/plugin.json` and update the rule counts in the docs.

Keep rules focused; prefer linking to a skill for long workflows. Rules must not contradict the skills; if a skill covers the same topic, keep them in agreement.

## Adding a Snippet or Template

1. Snippets live under `snippets/` grouped by language (`csharp/`, `shaders/`, `visual-scripting/`). Each file should be self-contained, target Unity 6.x APIs (Awaitable, `FindFirstObjectByType`, UI Toolkit), and free of hardcoded credentials.
2. Templates live under `templates/`. A new template needs at least a top-level `README.md` describing usage, the canonical scripts, and any project setup notes (assembly definitions, package dependencies, scripting defines).
3. Editor-only code (`UnityEditor`, custom inspectors, drawers, windows) goes inside `#if UNITY_EDITOR` so the file is safe in any folder.
4. CI compiles every C# snippet (one file at a time) and every template folder against Unity 6 reference assemblies, once as a player build and once as an editor build, with C# 9 and with obsolete APIs treated as errors. To run it locally (needs Python 3.12 and the .NET SDK; the first download streams the Unity editor archive, several GB):

   ```bash
   python .github/scripts/fetch_unity_refs.py --unity-version 6000.0.84f1 --inputsystem-version 1.20.1 --out .unity-refs
   python .github/scripts/compile_csharp.py --unity .unity-refs/Editor/Data --inputsystem .unity-refs/inputsystem/package
   ```

## Validation

CI runs the same checks you can run locally:

```bash
# Manifest, data schemas, frontmatter and rule scoping, dashes, credentials, C# 9, templates, and counts
python .github/scripts/validate_plugin.py
# MCP server tests and lint
pip install -r mcp-server/requirements-dev.txt
python -m pytest mcp-server/tests
ruff check mcp-server .github/scripts
```

`validate_plugin.py` also checks that every skill, rule, snippet, template, tool, and workflow count in `README.md`, `CLAUDE.md`, `AGENTS.md`, `.cursorrules`, and the docs matches the repo, so update those counts when you add or remove content.

## Commit Conventions

Releases are automated from commit messages on `main`:

- `feat:` - new features (minor version bump)
- `fix:`, `docs:`, `chore:`, `refactor:` - patch version bump
- `feat!:` or a `BREAKING CHANGE` footer - major version bump

Do not edit the `version` in `plugin.json`, the README version badge, or the `**Version:**` line in `CLAUDE.md`; the release workflow owns them.

## Content Rules

- No em dashes or en dashes; use hyphens or rewrite the sentence.
- No hardcoded credentials, tokens, API keys, or passwords, including placeholders that look real.
- Target Unity 6 (CI compiles against 6000.0 LTS) and modern APIs: Awaitable, `FindFirstObjectByType`, `HLSLPROGRAM`, UI Toolkit.
- C# must compile as C# 9 (no file-scoped namespaces, no primary constructors).

## Pull Request Process

1. **Update docs** if you change behavior or content lists (`README.md`, `CLAUDE.md`, `AGENTS.md`, `docs/`).
2. **Run validation** locally (see above).
3. **Open a PR** against `main` with a clear title using a conventional commit prefix.
4. **Respond to review** feedback; CI must pass before merge.

## Developer Certificate of Origin and Inbound License Grant

This project uses CC-BY-NC-ND-4.0 as its outbound license, which forbids derivatives. Every pull request is a derivative. Contributions are accepted inbound under a broader grant via the Developer Certificate of Origin (DCO), which resolves the conflict so the project can accept and redistribute contributions.

### Required grant

By submitting a contribution to this repository, you certify that you have the right to do so under the Developer Certificate of Origin (DCO) 1.1, and you grant TMHSDigital a perpetual, worldwide, non-exclusive, royalty-free, irrevocable license to use, reproduce, prepare derivative works of, publicly display, publicly perform, sublicense, and distribute your contribution under the project's current license (CC-BY-NC-ND-4.0) or any successor license chosen by the project.

### DCO sign-off

Every commit in a pull request must have a `Signed-off-by:` trailer matching the commit author:

```
Signed-off-by: Jane Developer <jane@example.com>
```

Signing is done at commit time:

```bash
git commit -s -m "feat: add new skill"
```

The GitHub DCO App enforces this on every PR.

For the full inbound/outbound model and rationale, see [`standards/licensing.md`](https://github.com/TMHSDigital/Developer-Tools-Directory/blob/main/standards/licensing.md) in the Developer-Tools-Directory meta-repo.

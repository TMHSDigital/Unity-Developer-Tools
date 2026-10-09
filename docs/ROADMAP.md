# Roadmap

Planned work is tracked in [GitHub issues](https://github.com/TMHSDigital/Unity-Developer-Tools/issues); this page groups it by theme.

## Milestone 1 - Foundation (done, v1.0.0)

- [x] Repository structure and plugin manifest
- [x] All skill files (18 skills)
- [x] All rule files (8 rules)
- [x] Snippet library (15 C# snippets, 4 shader snippets)
- [x] Template projects (5 starter templates)
- [x] MCP server with 4 tools
- [x] Reference data (API, shaders, platforms, lifecycle, deprecated patterns)
- [x] README and documentation

## Milestone 2 - Correctness and project awareness (in progress)

- [x] Compile every C# snippet and template against Unity 6 in CI
- [x] MCP server test suite with a stdio smoke test
- [x] Plugin-relative MCP registration so the server works after install
- [x] `analyze_project` tool: detect editor version, render pipeline, packages, and settings from project files
- [x] Test Framework scaffolding (`scaffold_script` with `script_type="test"`)
- [x] Rule scoping by file type, enforced in CI
- [ ] Correct remaining skill examples and contradictions between skills and rules
- [ ] Source or remove forward-looking Unity version claims
- [ ] Use project context in `scaffold_script` and `shader_helper` (asmdef namespaces, active pipeline)
- [ ] `check_code` tool for deprecated and anti-pattern Unity APIs
- [ ] Version-accurate Unity API index for `lookup_api`

## Milestone 3 - Coverage

- [ ] Skill descriptions tuned for triggering, pointing at the MCP tools
- [ ] New skills: Cinemachine 3, build automation and CI, save systems, AI Navigation, UGS multiplayer, VFX Graph, localization, XR
- [ ] Snippet gaps: asmdefs, `.inputactions`, UXML/USS, Render Graph features, tests
- [ ] Templates as a UPM package
- [ ] Unity Editor bridge for compile errors, console, and tests (evaluate building vs integrating)

## Milestone 4 - Distribution and community

- [ ] Publish the MCP server to PyPI and MCP registries
- [ ] Cursor marketplace listing and a Claude Code plugin manifest
- [ ] Community health files, issue and PR templates
- [ ] README demo and before/after examples

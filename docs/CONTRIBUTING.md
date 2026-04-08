# Contributing

## How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feat/my-feature`)
3. Make your changes following the conventions below
4. Commit using conventional commits
5. Open a pull request

## Commit Conventions

Use conventional commits:
- `feat:` - New features (minor version bump)
- `fix:` - Bug fixes (patch version bump)
- `docs:` - Documentation changes (patch version bump)
- `chore:` - Maintenance tasks (patch version bump)
- `refactor:` - Code restructuring (patch version bump)
- `feat!:` or `BREAKING CHANGE` - Breaking changes (major version bump)

## Adding a Skill

1. Create `skills/<skill-name>/SKILL.md` with YAML frontmatter (title, description, globs)
2. Add the path to `plugin.json` under "skills"
3. Update the skills count in README.md
4. Write thorough, accurate content targeting Unity 6.x

## Adding a Rule

1. Create `rules/<rule-name>.mdc` with frontmatter (title, description, globs, alwaysApply)
2. Add the path to `plugin.json` under "rules"
3. Update the rules count in README.md

## Adding a Snippet

1. Add the file to `snippets/<language>/`
2. Include a header comment explaining what the snippet does and when to use it
3. Update the snippets count in README.md

## Adding a Template

1. Create `templates/<template-name>/` with scripts and a README.md
2. Follow existing template patterns for consistency
3. Update the templates count in README.md

## Content Rules

- No em dashes or en dashes - use hyphens or rewrite
- No hardcoded credentials, tokens, API keys, or passwords
- Target Unity 6.3 LTS as the baseline
- Use modern APIs: Awaitable, FindFirstObjectByType, HLSLPROGRAM, UI Toolkit
- Python code in mcp-server/ must pass py_compile
- All JSON files must be valid

## Code Style

- C# snippets: follow the naming-conventions.mdc rules
- Shaders: HLSLPROGRAM for URP/HDRP, include SRP Batcher compatibility
- Python: standard formatting, type hints where helpful

## Testing Changes

Run the validate workflow locally to check:
- JSON validity
- Plugin manifest completeness
- File count consistency
- Em dash detection
- Credential scanning

## Summary

<!-- What does this change and why? Link the issue it fixes, for example "Fixes #12". -->

## Checklist

- [ ] PR title is a conventional commit (`feat:`, `fix:`, `docs:`, `chore:` ...)
- [ ] `python .github/scripts/validate_plugin.py` passes
- [ ] No em or en dashes in Markdown or rules
- [ ] New or edited skills and rules have `title`, `description`, `globs`, and `standards-version` frontmatter
- [ ] C# in snippets and templates compiles against Unity 6 (see CONTRIBUTING.md for the local compile check)
- [ ] Version-specific Unity claims link an official source
- [ ] Counts in README.md, CLAUDE.md, and docs updated if a skill, rule, snippet, template, or tool was added or removed
- [ ] Did not hand-edit the plugin.json version, the README badge, or the `**Version:**` line

# Security Policy

## Supported Versions

Only the latest release receives fixes. The plugin and MCP server are released together from `main`, so update to the newest tag before reporting.

## Reporting a Vulnerability

Please do not open a public issue for security problems.

Report privately through GitHub: open the repository's **Security** tab and choose **Report a vulnerability**. Include:

- What is affected (MCP server tool, a workflow, a rule or skill that gives unsafe advice)
- Steps to reproduce, or a proof of concept
- The impact you expect

You should get a first response within 7 days. Once a fix is released, the advisory is published with credit to the reporter unless you ask to stay anonymous.

## Scope

In scope:

- The MCP server in `mcp-server/` (for example, path traversal in `analyze_project`, or a tool that reads or writes outside the paths it is given)
- GitHub Actions workflows in `.github/workflows/` (for example, script injection or token exposure)
- Skills, rules, snippets, or templates that recommend insecure practices, such as shipping secrets in a build

Out of scope:

- Vulnerabilities in Unity itself or in third-party packages; report those to the vendor
- Issues that need an already compromised machine or a malicious local Unity project you chose to open

"""Validate plugin content. CI runs each check as its own job; run locally with no arguments to run them all.

    python .github/scripts/validate_plugin.py              # every check
    python .github/scripts/validate_plugin.py rules counts # selected checks

Exits non-zero and prints one ::error:: line per problem when a check fails.
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ".cursor-plugin/plugin.json"
DATA_DIR = "mcp-server/data"


def read(rel):
    return (ROOT / rel).read_text(encoding="utf-8")


def tracked_files():
    # Only files git knows about, so local scratch files do not fail the checks
    out = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    return [p for p in out.splitlines() if (ROOT / p).is_file()]


def frontmatter(rel):
    """Return (fields, body) for a file with --- delimited frontmatter, or (None, reason)."""
    content = read(rel)
    if not content.startswith("---"):
        return None, "missing YAML frontmatter"
    parts = content.split("---", 2)
    if len(parts) < 3:
        return None, "malformed frontmatter (no closing ---)"
    fields = {}
    for line in parts[1].splitlines():
        key, sep, value = line.partition(":")
        if sep and key.strip() and not key.startswith((" ", "\t")):
            fields[key.strip()] = value.strip()
    return fields, parts[2].strip()


def parse_globs(value):
    try:
        globs = json.loads(value)
    except (TypeError, ValueError):
        return None
    if isinstance(globs, list) and all(isinstance(g, str) for g in globs):
        return globs
    return None


# Checks: each returns a list of error strings and may print a summary line


def check_data():
    schemas = {
        "unity_api_common.json": {"name": str, "namespace": str, "category": str, "description": str, "signature": str},
        "deprecated_patterns.json": {"legacy": str, "replacement": str, "reason": str, "since_version": str},
        "lifecycle_order.json": {"method": str, "phase": str, "description": str, "runs_per_frame": bool},
        "shader_properties.json": {"effect": str, "description": str, "pipelines": list, "properties": list},
        "platform_defines.json": {"platform": str, "display_name": str, "define": str, "capabilities": list},
    }
    errors = []
    for name, fields in schemas.items():
        data = json.loads(read(f"{DATA_DIR}/{name}"))
        if not isinstance(data, list):
            errors.append(f"{name} must be an array")
            continue
        for i, entry in enumerate(data):
            for field, kind in fields.items():
                if field not in entry:
                    errors.append(f"{name}[{i}]: missing {field}")
                elif not isinstance(entry[field], kind):
                    errors.append(f"{name}[{i}]: {field} must be {kind.__name__}")
        print(f"{name}: {len(data)} entries")
    return errors


def check_manifest():
    errors = []
    m = json.loads(read(MANIFEST))
    json.loads(read("mcp.json"))
    required = ["name", "displayName", "description", "version", "author", "license", "skills", "rules"]
    errors += [f"{MANIFEST}: missing field {f}" for f in required if f not in m]
    if not re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", m.get("name", "")):
        errors.append(f"{MANIFEST}: name must be lowercase kebab-case")
    if not re.match(r"^\d+\.\d+\.\d+$", m.get("version", "")):
        errors.append(f"{MANIFEST}: version must be semver (X.Y.Z)")
    if not (isinstance(m.get("author"), dict) and "name" in m["author"]):
        errors.append(f"{MANIFEST}: author must be an object with a name")
    if not isinstance(m.get("keywords"), list):
        errors.append(f"{MANIFEST}: keywords must be an array")

    for key in ("skills", "rules"):
        for path in m.get(key, []):
            if not (ROOT / path).exists():
                errors.append(f"{MANIFEST}: {key} entry not found: {path}")
    listed = set(m.get("skills", []))
    for skill in sorted((ROOT / "skills").glob("*/SKILL.md")):
        rel = skill.relative_to(ROOT).as_posix()
        if rel not in listed:
            errors.append(f"{MANIFEST}: {rel} exists but is not listed under skills")
    listed = set(m.get("rules", []))
    for rule in sorted((ROOT / "rules").glob("*.mdc")):
        rel = rule.relative_to(ROOT).as_posix()
        if rel not in listed:
            errors.append(f"{MANIFEST}: {rel} exists but is not listed under rules")

    config = m.get("mcpServers")
    if not (isinstance(config, str) and (ROOT / config).exists()):
        errors.append(f"{MANIFEST}: mcpServers must point to an existing file, got {config!r}")
    else:
        servers = json.loads(read(config)).get("mcpServers") or {}
        if not servers:
            errors.append(f"{config}: no MCP servers registered")
        for name, server in servers.items():
            for arg in server.get("args", []):
                if arg.startswith("${CURSOR_PLUGIN_ROOT}/"):
                    path = arg[len("${CURSOR_PLUGIN_ROOT}/"):]
                    if not (ROOT / path).exists():
                        errors.append(f"{config}: {name}: {path} not found")
                if os.path.isabs(arg):
                    errors.append(f"{config}: {name}: absolute path {arg} breaks other installs")
        print(f"MCP servers registered: {', '.join(servers)}")
    print(f"Manifest lists {len(m.get('skills', []))} skills and {len(m.get('rules', []))} rules")
    return errors


def check_skills():
    errors = []
    dirs = sorted(d for d in (ROOT / "skills").iterdir() if d.is_dir())
    for d in dirs:
        rel = f"skills/{d.name}/SKILL.md"
        if not (ROOT / rel).exists():
            errors.append(f"{rel}: SKILL.md missing")
            continue
        fields, body = frontmatter(rel)
        if fields is None:
            errors.append(f"{rel}: {body}")
            continue
        for field in ("title", "description", "globs", "standards-version"):
            if field not in fields:
                errors.append(f"{rel}: frontmatter missing {field}")
        if "globs" in fields and parse_globs(fields["globs"]) is None:
            errors.append(f"{rel}: globs must be a JSON-style list of strings")
        if len(body) < 100:
            errors.append(f"{rel}: body too short ({len(body)} chars, minimum 100)")
    print(f"Checked {len(dirs)} skills")
    return errors


def check_rules():
    errors = []
    files = sorted((ROOT / "rules").glob("*.mdc"))
    for path in files:
        rel = path.relative_to(ROOT).as_posix()
        fields, body = frontmatter(rel)
        if fields is None:
            errors.append(f"{rel}: {body}")
            continue
        for field in ("title", "description", "globs", "alwaysApply", "standards-version"):
            if field not in fields:
                errors.append(f"{rel}: frontmatter missing {field}")
        always = fields.get("alwaysApply")
        if always not in ("true", "false"):
            errors.append(f"{rel}: alwaysApply must be true or false")
        globs = parse_globs(fields.get("globs", ""))
        if globs is None:
            errors.append(f"{rel}: globs must be a JSON-style list of strings")
        elif always == "true" and globs:
            # Cursor ignores globs on always-applied rules, so the scope would silently be everything
            errors.append(f"{rel}: alwaysApply: true ignores globs; set alwaysApply: false or use globs: []")
        if len(body) < 20:
            errors.append(f"{rel}: body too short ({len(body)} chars)")
    print(f"Checked {len(files)} rules")
    return errors


DASH_EXTS = (".md", ".mdc", ".cs", ".json", ".py", ".shader", ".hlsl", ".uxml", ".uss")
CREDENTIAL = re.compile(
    r"""password\s*=\s*["'][^"']+|api_key\s*=\s*["'][^"']+|token\s*=\s*["'][A-Za-z0-9]+""", re.IGNORECASE
)
DASHES = re.compile("[" + chr(0x2013) + chr(0x2014) + "]")  # en and em dash
CREDENTIAL_ALLOW = ("example", "placeholder", "mock", "destroyCancellationToken")
FILE_SCOPED_NAMESPACE = re.compile(r"^\s*namespace\s+[A-Za-z0-9_.]+\s*;", re.MULTILINE)
CSHARP10_ADVICE = re.compile(r"\b(use|prefer)\s+(file-scoped namespaces|primary constructors)", re.IGNORECASE)


def check_content():
    errors = []
    files = tracked_files()
    for rel in files:
        if not rel.endswith(DASH_EXTS):
            continue
        text = read(rel)
        for n, line in enumerate(text.splitlines(), 1):
            if DASHES.search(line):
                errors.append(f"{rel}:{n}: em or en dash; use a hyphen or rewrite")
            if (
                rel.endswith((".cs", ".py", ".json"))
                and CREDENTIAL.search(line)
                and not any(word in line for word in CREDENTIAL_ALLOW)
            ):
                errors.append(f"{rel}:{n}: possible hardcoded credential")
        if rel.endswith(".cs") and FILE_SCOPED_NAMESPACE.search(text):
            errors.append(f"{rel}: file-scoped namespaces are C# 10; Unity 6 compiles C# 9")
        if (
            rel.endswith((".md", ".mdc"))
            and rel.split("/")[0] in ("skills", "rules", "snippets", "templates")
            and CSHARP10_ADVICE.search(text)
        ):
            errors.append(f"{rel}: recommends C# 10+ features that Unity 6 cannot compile")

    snippets = [p for p in (ROOT / "snippets").rglob("*") if p.is_file() and p.name != "README.md"]
    for p in snippets:
        if p.stat().st_size < 10:
            errors.append(f"{p.relative_to(ROOT).as_posix()}: snippet is empty or too small")
    print(f"Scanned {len(files)} tracked files and {len(snippets)} snippets")
    return errors


def check_templates():
    errors = []
    dirs = sorted(d for d in (ROOT / "templates").iterdir() if d.is_dir())
    for d in dirs:
        rel = f"templates/{d.name}"
        if not (d / "README.md").exists():
            errors.append(f"{rel}: missing README.md")
        scripts = sorted(d.glob("*.cs"))
        if not scripts:
            errors.append(f"{rel}: no .cs files found")
        for cs in scripts:
            if len(cs.read_text(encoding="utf-8")) < 50:
                errors.append(f"{rel}/{cs.name}: file too small")
    print(f"Checked {len(dirs)} templates")
    return errors


# Files whose counts must match the repo. Release-history lines (v1.0.0 etc.) are skipped.
COUNT_FILES = ["README.md", "CLAUDE.md", "AGENTS.md", "CONTRIBUTING.md", ".cursorrules",
               "docs/index.md", "docs/ARCHITECTURE.md", "docs/GETTING-STARTED.md"]
HISTORY_LINE = re.compile(r"\bv\d+\.\d+\.\d+\b")


def actual_counts():
    m = json.loads(read(MANIFEST))
    snippets = [p for p in (ROOT / "snippets").rglob("*") if p.is_file() and p.name != "README.md"]
    return {
        "skills": len(m.get("skills", [])),
        "rules": len(m.get("rules", [])),
        "snippets": len(snippets),
        "csharp": sum(1 for p in snippets if p.suffix == ".cs"),
        "shaders": sum(1 for p in snippets if p.suffix in (".shader", ".hlsl")),
        "templates": sum(1 for d in (ROOT / "templates").iterdir() if (d / "README.md").exists()),
        "tools": len(re.findall(r"^@mcp\.tool\(\)", read("mcp-server/server.py"), re.MULTILINE)),
        "workflows": len(list((ROOT / ".github" / "workflows").glob("*.yml"))),
    }


COUNT_PATTERNS = [
    (re.compile(r"\b(\d+) (?:\*\*)?skills\b|## Skills \((\d+)\)"), "skills"),
    (re.compile(r"\b(\d+) (?:\*\*)?rules\b|## Rules \((\d+)\)"), "rules"),
    (re.compile(r"\b(\d+) (?:code )?snippets\b|## Snippets \((\d+)\)"), "snippets"),
    (re.compile(r"C# \((\d+)\)"), "csharp"),
    (re.compile(r"Shaders \((\d+)\)"), "shaders"),
    (re.compile(r"\b(\d+) (?:starter )?templates\b|## Templates \((\d+)\)"), "templates"),
    (re.compile(r"\b(\d+) (?:MCP )?tools\b|Available Tools \((\d+)\)"), "tools"),
    (re.compile(r"\b(\d+) workflows\b"), "workflows"),
]


def check_counts():
    errors = []
    actual = actual_counts()
    for rel in COUNT_FILES:
        if not (ROOT / rel).exists():
            continue
        for n, line in enumerate(read(rel).splitlines(), 1):
            if HISTORY_LINE.search(line):
                continue
            for pattern, key in COUNT_PATTERNS:
                for match in pattern.finditer(line):
                    claimed = int(next(g for g in match.groups() if g))
                    if claimed != actual[key]:
                        errors.append(f"{rel}:{n}: says {claimed} {key}, repo has {actual[key]}")
    print("Counts: " + ", ".join(f"{v} {k}" for k, v in actual.items()))
    return errors


CHECKS = {
    "data": check_data,
    "manifest": check_manifest,
    "skills": check_skills,
    "rules": check_rules,
    "content": check_content,
    "templates": check_templates,
    "counts": check_counts,
}


def main(argv):
    names = argv or list(CHECKS)
    unknown = [n for n in names if n not in CHECKS]
    if unknown:
        print(f"Unknown check(s): {', '.join(unknown)}. Valid: {', '.join(CHECKS)}", file=sys.stderr)
        return 2
    failed = False
    for name in names:
        print(f"== {name}")
        errors = CHECKS[name]()
        for e in errors:
            print(f"::error::{e}")
        failed |= bool(errors)
    print("FAILED" if failed else "All checks passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

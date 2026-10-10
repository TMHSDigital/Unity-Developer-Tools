"""Unity Developer Tools MCP Server.

Provides scaffold_script, lookup_api, shader_helper, platform_info, and
analyze_project tools for Unity game development in the Cursor IDE.
"""

import json
import os
import re
import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP

# Resolve data next to this file so the server works from any working
# directory. UNITY_DATA_PATH remains available as an explicit override.
DATA_PATH = Path(
    os.environ.get("UNITY_DATA_PATH") or Path(__file__).resolve().parent / "data"
)

DATA_FILES = (
    "unity_api_common.json",
    "deprecated_patterns.json",
    "shader_properties.json",
    "platform_defines.json",
)

mcp = FastMCP("unity-dev-tools")


def _load_json(filename: str) -> list:
    filepath = DATA_PATH / filename
    if not filepath.exists():
        raise FileNotFoundError(
            f"Unity data file not found: {filepath}. "
            "Check UNITY_DATA_PATH or reinstall the plugin."
        )
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def _check_data_files() -> None:
    """Fail at startup instead of answering every query with 'not found'."""
    for filename in DATA_FILES:
        _load_json(filename)


# ---------- Tool: scaffold_script ----------

SCRIPT_TEMPLATES = {
    "monobehaviour": '''using UnityEngine;

namespace {namespace}
{{
    public class {name} : MonoBehaviour
    {{
        [Header("Configuration")]
        [SerializeField] private float _speed = 5f;

        private void Awake()
        {{
            // Cache components here
        }}

        private void OnEnable()
        {{
            // Subscribe to events
        }}

        private void OnDisable()
        {{
            // Unsubscribe from events
        }}

        private void Update()
        {{
            // Per-frame logic
        }}
    }}
}}''',
    "scriptableobject": '''using UnityEngine;

namespace {namespace}
{{
    [CreateAssetMenu(fileName = "New {name}", menuName = "Data/{name}")]
    public class {name} : ScriptableObject
    {{
        [Header("Configuration")]
        [SerializeField] private string _displayName;
        [SerializeField] [TextArea(2, 5)] private string _description;

        public string DisplayName => _displayName;
        public string Description => _description;

        private void OnValidate()
        {{
            if (string.IsNullOrEmpty(_displayName))
                _displayName = name;
        }}
    }}
}}''',
    "editor-window": '''using UnityEditor;
using UnityEngine;
using UnityEngine.UIElements;

namespace {namespace}.Editor
{{
    public class {name} : EditorWindow
    {{
        [MenuItem("Tools/{name}")]
        public static void ShowWindow()
        {{
            GetWindow<{name}>("{name}");
        }}

        public void CreateGUI()
        {{
            var root = rootVisualElement;
            root.Add(new Label("{name}"));
            root.Add(new Button(() => Debug.Log("Clicked")) {{ text = "Action" }});
        }}
    }}
}}''',
    "custom-inspector": '''using UnityEditor;
using UnityEditor.UIElements;
using UnityEngine.UIElements;

namespace {namespace}.Editor
{{
    [CustomEditor(typeof({target_type}))]
    public class {name} : UnityEditor.Editor
    {{
        public override VisualElement CreateInspectorGUI()
        {{
            var root = new VisualElement();
            InspectorElement.FillDefaultInspector(root, serializedObject, this);
            return root;
        }}
    }}
}}''',
    "property-drawer": '''using UnityEditor;
using UnityEngine.UIElements;

namespace {namespace}.Editor
{{
    [CustomPropertyDrawer(typeof({target_type}))]
    public class {name} : PropertyDrawer
    {{
        public override VisualElement CreatePropertyGUI(SerializedProperty property)
        {{
            var container = new VisualElement();
            container.style.flexDirection = FlexDirection.Row;
            return container;
        }}
    }}
}}''',
    "interface": '''namespace {namespace}
{{
    public interface {name}
    {{
        bool IsActive {{ get; }}
        void Execute();
    }}
}}''',
    "state-machine": '''using UnityEngine;

namespace {namespace}
{{
    public interface I{name}State
    {{
        void Enter();
        void Update();
        void FixedUpdate();
        void Exit();
    }}

    public class {name} : MonoBehaviour
    {{
        private I{name}State _currentState;

        public void ChangeState(I{name}State newState)
        {{
            _currentState?.Exit();
            _currentState = newState;
            _currentState?.Enter();
        }}

        private void Update() => _currentState?.Update();
        private void FixedUpdate() => _currentState?.FixedUpdate();
    }}
}}''',
    "test": '''using NUnit.Framework;

namespace {namespace}.Tests
{{
    public class {name}
    {{
        [SetUp]
        public void SetUp()
        {{
            // Test setup
        }}

        [TearDown]
        public void TearDown()
        {{
            // Test cleanup
        }}

        [Test]
        public void Example_ReturnsExpected()
        {{
            Assert.Pass("Replace with actual test");
        }}
    }}
}}''',
}


CSHARP_KEYWORDS = frozenset(["abstract", "as", "base", "bool", "break", "byte", "case", "catch", "char", "checked", "class", "const", "continue", "decimal", "default", "delegate", "do", "double", "else", "enum", "event", "explicit", "extern", "false", "finally", "fixed", "float", "for", "foreach", "goto", "if", "implicit", "in", "int", "interface", "internal", "is", "lock", "long", "namespace", "new", "null", "object", "operator", "out", "override", "params", "private", "protected", "public", "readonly", "ref", "return", "sbyte", "sealed", "short", "sizeof", "stackalloc", "static", "string", "struct", "switch", "this", "throw", "true", "try", "typeof", "uint", "ulong", "unchecked", "unsafe", "ushort", "using", "virtual", "void", "volatile", "while"])

_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

# Suffixes stripped from an inspector or drawer class name to guess its target.
_TARGET_SUFFIXES = ("PropertyDrawer", "Inspector", "Editor", "Drawer")


def _identifier_error(value: str, label: str) -> str | None:
    if not _IDENTIFIER.match(value):
        return (
            f"Invalid {label} '{value}': use letters, digits, and underscores, "
            "starting with a letter (e.g. PlayerHealth)."
        )
    if value in CSHARP_KEYWORDS:
        return f"Invalid {label} '{value}': it is a reserved C# keyword."
    return None


def _guess_target_type(name: str) -> str:
    for suffix in _TARGET_SUFFIXES:
        if name.endswith(suffix) and len(name) > len(suffix):
            return name[: -len(suffix)]
    return ""


@mcp.tool()
def scaffold_script(
    type: str,
    name: str,
    namespace: str = "MyGame",
    target_type: str = "",
) -> str:
    """Generate a well-structured C# script following Unity conventions.

    Args:
        type: Script type (monobehaviour, scriptableobject, editor-window,
              custom-inspector, property-drawer, interface, state-machine, test)
        name: Class name for the generated script
        namespace: C# namespace (default: MyGame)
        target_type: Type inspected or drawn, for custom-inspector and
                     property-drawer. Defaults to the name without an
                     Editor/Inspector/Drawer suffix (PlayerEditor -> Player).
    """
    template = SCRIPT_TEMPLATES.get(type)
    if not template:
        valid = ", ".join(SCRIPT_TEMPLATES.keys())
        return f"Unknown script type: {type}. Valid types: {valid}"

    error = _identifier_error(name, "class name")
    for segment in namespace.split("."):
        error = error or _identifier_error(segment, "namespace segment")
    if error:
        return error

    notes = []
    if type in ("custom-inspector", "property-drawer"):
        target_type = target_type or _guess_target_type(name)
        if not target_type:
            return (
                f"Cannot infer the target type for '{name}'. Pass target_type, "
                "or name the class <Target>Editor / <Target>Drawer."
            )
        error = _identifier_error(target_type, "target type")
        if error:
            return error

    if type == "interface" and not re.match(r"^I[A-Z]", name):
        notes.append(
            f"// Note: interfaces use an I prefix by convention (I{name})."
        )

    code = template.format(name=name, namespace=namespace, target_type=target_type)

    folder_map = {
        "monobehaviour": "Assets/Scripts/Runtime",
        "scriptableobject": "Assets/Scripts/Runtime",
        "editor-window": "Assets/Scripts/Editor",
        "custom-inspector": "Assets/Scripts/Editor",
        "property-drawer": "Assets/Scripts/Editor",
        "interface": "Assets/Scripts/Runtime",
        "state-machine": "Assets/Scripts/Runtime",
        "test": "Assets/Tests/EditMode",
    }
    folder = folder_map.get(type, "Assets/Scripts")
    path = f"{folder}/{name}.cs"

    if folder.endswith("/Editor"):
        notes.append(
            "// Editor-only: keep this in an Editor folder or an Editor-only "
            "assembly definition (includePlatforms: [\"Editor\"]) so player "
            "builds do not include UnityEditor."
        )
    if type == "test":
        notes.append(
            "// Requires a test assembly: create one with Assets > Create > "
            "Testing > Tests Assembly Folder, and reference your runtime asmdef."
        )

    header = "\n".join([f"// Recommended path: {path}", *notes])
    return f"{header}\n\n{code}"


# ---------- Tool: lookup_api ----------

@mcp.tool()
def lookup_api(
    query: str,
    category: str = "",
) -> str:
    """Search the Unity API reference database.

    Args:
        query: Search term (class name, method name, or keyword)
        category: Optional filter (general, physics, ui, animation, audio,
                  rendering, input, networking, editor)
    """
    api_data = _load_json("unity_api_common.json")
    deprecated = _load_json("deprecated_patterns.json")

    categories = sorted({e.get("category", "").lower() for e in api_data})
    category = category.strip().lower()
    if category and category not in categories:
        return (
            f"Unknown category '{category}'. "
            f"Valid categories: {', '.join(categories)}"
        )

    query_lower = query.strip().lower()
    terms = query_lower.split()
    scored = []

    for entry in api_data:
        name = entry.get("name", "").lower()
        if category and entry.get("category", "").lower() != category:
            continue

        haystack = " ".join(
            entry.get(field, "") for field in ("name", "namespace", "description")
        ).lower()
        if not terms or not all(term in haystack for term in terms):
            continue

        # Exact name first, then name matches, then description-only matches.
        if name == query_lower:
            score = 0
        elif all(term in name for term in terms):
            score = 1
        else:
            score = 2
        scored.append((score, entry))

    scored.sort(key=lambda item: item[0])
    results = [entry for _, entry in scored]

    warnings = []
    for dep in deprecated:
        legacy = dep.get("legacy", "").lower()
        if terms and all(term in legacy for term in terms):
            warnings.append(
                f"WARNING: '{dep['legacy']}' is deprecated. "
                f"Use '{dep['replacement']}' instead. "
                f"Reason: {dep.get('reason', 'N/A')}"
            )

    output = []
    if warnings:
        output.extend(warnings)
        output.append("")

    if not results:
        output.append(
            f"No API entries found for '{query}'. "
            f"Try a class or member name, or filter by category: "
            f"{', '.join(categories)}"
        )
    else:
        for entry in results[:15]:
            output.append(f"## {entry['name']}")
            output.append(f"**Namespace**: {entry.get('namespace', 'UnityEngine')}")
            output.append(f"**Category**: {entry.get('category', 'General')}")
            output.append(f"**Description**: {entry.get('description', '')}")
            if entry.get("signature"):
                output.append(f"**Signature**: `{entry['signature']}`")
            if entry.get("example"):
                output.append(f"**Example**: {entry['example']}")
            output.append("")

    return "\n".join(output)


# ---------- Tool: shader_helper ----------

@mcp.tool()
def shader_helper(
    effect: str,
    pipeline: str = "urp",
) -> str:
    """Get shader code patterns and property setups for common effects.

    Args:
        effect: Effect name (dissolve, outline, toon, water, hologram, fresnel)
        pipeline: Target render pipeline (urp, hdrp, builtin)
    """
    shader_data = _load_json("shader_properties.json")

    effect_lower = effect.strip().lower()
    pipeline = pipeline.strip().lower()
    valid_pipelines = ("urp", "hdrp", "builtin")
    if pipeline not in valid_pipelines:
        return (
            f"Unknown pipeline '{pipeline}'. "
            f"Valid pipelines: {', '.join(valid_pipelines)}"
        )

    results = []

    for entry in shader_data:
        if effect_lower in entry.get("effect", "").lower() and pipeline in entry.get("pipelines", []):
            results.append(entry)

    if not results:
        effects = ", ".join(e.get("effect", "").lower() for e in shader_data)
        return (
            f"No shader patterns found for effect '{effect}' "
            f"on pipeline '{pipeline}'. Available effects: {effects}"
        )

    output = []
    for entry in results:
        output.append(f"## {entry['effect']} - {pipeline.upper()}")
        output.append(f"**Description**: {entry.get('description', '')}")

        if entry.get("properties"):
            output.append("\n**Properties**:")
            for prop in entry["properties"]:
                output.append(
                    f"- `{prop['name']}` ({prop['type']}): {prop['description']}"
                )

        # The hand-written HLSL targets a single pipeline; never present it as
        # code for another one.
        code_pipeline = entry.get("code_pipeline", "urp")
        if entry.get("code_snippet") and code_pipeline == pipeline:
            output.append(f"\n**Code**:\n```hlsl\n{entry['code_snippet']}\n```")
        elif entry.get("code_snippet"):
            output.append(
                f"\n**Code**: No hand-written HLSL for {pipeline.upper()} yet "
                f"(the reference snippet targets {code_pipeline.upper()} and "
                "will not compile here). Use the Shader Graph approach below."
            )

        if entry.get("shader_graph_nodes"):
            output.append("\n**Shader Graph Approach**:")
            for node in entry["shader_graph_nodes"]:
                output.append(f"- {node}")

        output.append("")

    return "\n".join(output)


# ---------- Tool: platform_info ----------

@mcp.tool()
def platform_info(
    platform: str,
) -> str:
    """Get platform-specific scripting defines, capabilities, and build tips.

    Args:
        platform: Target platform (windows, macos, linux, android, ios, webgl,
                  ps5, xbox, switch)
    """
    platform_data = _load_json("platform_defines.json")

    platform_lower = platform.lower()
    for entry in platform_data:
        if entry.get("platform", "").lower() == platform_lower:
            output = [f"## {entry.get('display_name', platform)}"]
            output.append(
                f"**Scripting Define**: `{entry.get('define', 'N/A')}`"
            )
            output.append(
                f"**Scripting Backend**: {entry.get('backend', 'IL2CPP')}"
            )
            output.append(
                f"**Graphics API**: {entry.get('graphics_api', 'N/A')}"
            )

            if entry.get("capabilities"):
                output.append("\n**Capabilities**:")
                for cap in entry["capabilities"]:
                    output.append(f"- {cap}")

            if entry.get("limitations"):
                output.append("\n**Limitations**:")
                for lim in entry["limitations"]:
                    output.append(f"- {lim}")

            if entry.get("recommendations"):
                output.append("\n**Recommendations**:")
                for rec in entry["recommendations"]:
                    output.append(f"- {rec}")

            return "\n".join(output)

    valid = [e.get("platform", "") for e in platform_data]
    return f"Unknown platform: {platform}. Valid: {', '.join(valid)}"


# ---------- Tool: analyze_project ----------

# Script GUIDs of the render pipeline asset classes (from the URP/HDRP .cs.meta files)
_PIPELINE_SCRIPT_GUIDS = {
    "bf2edee5c58d82540a51f03df9d42094": "urp",
    "0cf1dab834d4ec34195b920ea7bbf9ec": "hdrp",
}
_PIPELINE_PACKAGES = {
    "com.unity.render-pipelines.universal": "urp",
    "com.unity.render-pipelines.high-definition": "hdrp",
}
_PIPELINE_NAMES = {"urp": "URP", "hdrp": "HDRP", "builtin": "Built-in"}

# Packages worth calling out because they change which APIs and patterns apply
_NOTABLE_PACKAGES = {
    "com.unity.inputsystem": "Input System",
    "com.unity.netcode.gameobjects": "Netcode for GameObjects",
    "com.unity.netcode": "Netcode for Entities",
    "com.unity.entities": "Entities (ECS)",
    "com.unity.addressables": "Addressables",
    "com.unity.cinemachine": "Cinemachine",
    "com.unity.ugui": "uGUI / TextMeshPro",
    "com.unity.visualscripting": "Visual Scripting",
    "com.unity.test-framework": "Test Framework",
    "com.unity.ai.navigation": "AI Navigation",
    "com.unity.timeline": "Timeline",
    "com.unity.shadergraph": "Shader Graph",
    "com.unity.visualeffectgraph": "VFX Graph",
    "com.unity.burst": "Burst",
    "com.unity.collections": "Collections",
    "com.unity.localization": "Localization",
    "com.unity.xr.interaction.toolkit": "XR Interaction Toolkit",
}

_INPUT_HANDLING = {"0": "Input Manager (old)", "1": "Input System Package (new)", "2": "Both"}
_SCRIPTING_BACKEND = {"0": "Mono", "1": "IL2CPP"}
_API_LEVEL = {"3": ".NET Framework", "6": ".NET Standard 2.1"}
_MAX_ASMDEFS = 50
_MAX_META_SCAN = 20000


def _read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def _is_text_yaml(text: str) -> bool:
    return text.startswith("%YAML")


def _yaml_scalar(text: str, key: str) -> str | None:
    match = re.search(rf"^[ \t]*{re.escape(key)}:[ \t]*(.*?)\r?$", text, re.MULTILINE)
    return match.group(1).strip() if match else None


def _yaml_platform_map(text: str, key: str) -> dict:
    """Read a Unity per-platform map such as scriptingBackend: {Standalone: 1}."""
    match = re.search(rf"^([ \t]*){re.escape(key)}:[ \t]*\r?\n((?:\1[ \t]+.*\n?)*)", text, re.MULTILINE)
    if not match:
        return {}
    result = {}
    for line in match.group(2).splitlines():
        name, sep, value = line.strip().partition(":")
        if sep:
            result[name.strip() or "Default"] = value.strip()
    return result


def _pipeline_refs(text: str, key: str) -> list:
    """GUIDs referenced by m_CustomRenderPipeline / customRenderPipeline entries."""
    return re.findall(rf"{key}: \{{fileID: \d+, guid: ([0-9a-f]{{32}})", text)


def _find_assets_by_guid(project: Path, guids: set) -> dict:
    """Map asset GUIDs to asset paths by scanning .meta files under Assets/."""
    found = {}
    assets = project / "Assets"
    if not guids or not assets.is_dir():
        return found
    for count, meta in enumerate(assets.rglob("*.asset.meta")):
        if count >= _MAX_META_SCAN or len(found) == len(guids):
            break
        text = _read_text(meta) or ""
        match = re.search(r"^guid: ([0-9a-f]{32})", text, re.MULTILINE)
        if match and match.group(1) in guids:
            found[match.group(1)] = meta.with_suffix("")
    return found


def _classify_pipeline_asset(path: Path) -> str | None:
    text = _read_text(path) or ""
    match = re.search(r"m_Script: \{fileID: \d+, guid: ([0-9a-f]{32})", text)
    if match and match.group(1) in _PIPELINE_SCRIPT_GUIDS:
        return _PIPELINE_SCRIPT_GUIDS[match.group(1)]
    if "m_RendererDataList:" in text:
        return "urp"
    if "m_RenderPipelineSettings:" in text:
        return "hdrp"
    return None


@mcp.tool()
def analyze_project(
    project_path: str,
) -> str:
    """Summarize a Unity project: editor version, render pipeline, packages,
    input handling, scripting backend, define symbols, and assembly definitions.

    Reads project files only; Unity does not need to be running. Call this
    before giving version-, pipeline-, or package-specific advice.

    Args:
        project_path: Path to the Unity project root (the folder that contains
                      Assets/, Packages/, and ProjectSettings/)
    """
    project = Path(project_path).expanduser()
    settings = project / "ProjectSettings"
    if not project.is_dir():
        return f"Not a directory: {project_path}"
    if not settings.is_dir() or not (project / "Assets").is_dir():
        return (
            f"{project_path} does not look like a Unity project "
            "(expected Assets/ and ProjectSettings/ folders)."
        )

    output = [f"## Unity project: {project.name}"]
    notes = []

    # Editor version
    version_text = _read_text(settings / "ProjectVersion.txt") or ""
    editor_version = _yaml_scalar(version_text, "m_EditorVersion")
    output.append(f"**Editor version**: {editor_version or 'unknown'}")

    # Packages
    packages = {}
    manifest_text = _read_text(project / "Packages" / "manifest.json")
    if manifest_text:
        try:
            packages = json.loads(manifest_text).get("dependencies", {})
        except json.JSONDecodeError:
            notes.append("Packages/manifest.json is not valid JSON.")
    else:
        notes.append("Packages/manifest.json not found.")

    lock_versions = {}
    lock_text = _read_text(project / "Packages" / "packages-lock.json")
    if lock_text:
        try:
            for name, info in json.loads(lock_text).get("dependencies", {}).items():
                lock_versions[name] = info.get("version")
        except json.JSONDecodeError:
            pass

    def package_version(name: str) -> str | None:
        version = lock_versions.get(name) or packages.get(name)
        return str(version) if version is not None else None

    # Render pipeline: Graphics default, then per-quality-level overrides
    graphics_text = _read_text(settings / "GraphicsSettings.asset") or ""
    quality_text = _read_text(settings / "QualitySettings.asset") or ""
    if graphics_text and not _is_text_yaml(graphics_text):
        notes.append("Settings are not text-serialized; set Asset Serialization to Force Text for full detection.")

    default_guids = _pipeline_refs(graphics_text, "m_CustomRenderPipeline")
    quality_guids = _pipeline_refs(quality_text, "customRenderPipeline")
    assets_by_guid = _find_assets_by_guid(project, set(default_guids + quality_guids))

    detected = []
    for guid in default_guids + quality_guids:
        path = assets_by_guid.get(guid)
        kind = _classify_pipeline_asset(path) if path else None
        if kind:
            detected.append((kind, path.relative_to(project).as_posix()))

    installed_pipelines = [p for pkg, p in _PIPELINE_PACKAGES.items() if pkg in packages or pkg in lock_versions]

    if detected:
        pipeline = detected[0][0]
        source = f"pipeline asset `{detected[0][1]}`"
    elif default_guids or quality_guids:
        pipeline = installed_pipelines[0] if len(installed_pipelines) == 1 else "unknown"
        source = "a pipeline asset is assigned but could not be read; inferred from installed packages"
    elif installed_pipelines:
        pipeline = "builtin"
        source = "no pipeline asset is assigned in Graphics or Quality settings"
        notes.append(
            f"{_PIPELINE_NAMES[installed_pipelines[0]]} is installed but no pipeline asset is assigned, "
            "so the project renders with the Built-in pipeline."
        )
    else:
        pipeline = "builtin"
        source = "no SRP package or pipeline asset found"

    kinds = {kind for kind, _ in detected}
    if len(kinds) > 1:
        notes.append("Quality levels use different pipelines: " + ", ".join(sorted(_PIPELINE_NAMES[k] for k in kinds)))

    pipeline_line = f"**Render pipeline**: {_PIPELINE_NAMES.get(pipeline, 'Unknown')}"
    for pkg, kind in _PIPELINE_PACKAGES.items():
        if kind == pipeline and package_version(pkg):
            pipeline_line += f" ({pkg} {package_version(pkg)})"
    output.append(pipeline_line)
    output.append(f"  - Detected from {source}")
    if pipeline in ("urp", "hdrp", "builtin"):
        output.append(f"  - Use `pipeline=\"{pipeline}\"` with shader_helper")

    # Player settings
    player_text = _read_text(settings / "ProjectSettings.asset") or ""
    input_value = _yaml_scalar(player_text, "activeInputHandler")
    output.append(f"**Active input handling**: {_INPUT_HANDLING.get(input_value or '', 'unknown')}")
    if input_value in ("1", "2") and "com.unity.inputsystem" not in packages and "com.unity.inputsystem" not in lock_versions:
        notes.append("Input handling uses the Input System but com.unity.inputsystem is not installed.")

    backends = _yaml_platform_map(player_text, "scriptingBackend")
    if backends:
        output.append("**Scripting backend**: " + ", ".join(
            f"{platform} {_SCRIPTING_BACKEND.get(value, value)}" for platform, value in backends.items()
        ))
    api_levels = _yaml_platform_map(player_text, "apiCompatibilityLevelPerPlatform")
    if api_levels:
        output.append("**API compatibility**: " + ", ".join(
            f"{platform} {_API_LEVEL.get(value, value)}" for platform, value in api_levels.items()
        ))
    defines = {p: v for p, v in _yaml_platform_map(player_text, "scriptingDefineSymbols").items() if v}
    if defines:
        output.append("**Scripting define symbols**:")
        output.extend(f"  - {platform}: `{value}`" for platform, value in defines.items())

    # Packages summary
    if packages:
        notable = [
            f"{label} {package_version(name)}"
            for name, label in _NOTABLE_PACKAGES.items()
            if name in packages or name in lock_versions
        ]
        output.append(f"\n**Packages** ({len(packages)} in manifest)")
        output.append("  - Notable: " + (", ".join(notable) if notable else "none"))

    # Assembly definitions
    asmdefs = []
    for count, path in enumerate(sorted((project / "Assets").rglob("*.asmdef"))):
        if count >= _MAX_ASMDEFS:
            break
        try:
            data = json.loads(_read_text(path) or "{}")
        except json.JSONDecodeError:
            continue
        editor_only = data.get("includePlatforms") == ["Editor"]
        tests = "UNITY_INCLUDE_TESTS" in data.get("defineConstraints", [])
        tags = [t for t, on in (("editor", editor_only), ("tests", tests)) if on]
        root_ns = data.get("rootNamespace")
        detail = ", ".join(tags + ([f"namespace {root_ns}"] if root_ns else []))
        rel = path.relative_to(project).as_posix()
        asmdefs.append(f"  - {data.get('name', path.stem)} (`{rel}`" + (f"; {detail})" if detail else ")"))
    output.append(f"\n**Assembly definitions** ({len(asmdefs)})")
    output.extend(asmdefs or ["  - none (all scripts compile into Assembly-CSharp)"])

    if notes:
        output.append("\n**Notes**:")
        output.extend(f"- {note}" for note in notes)

    return "\n".join(output)


if __name__ == "__main__":
    try:
        _check_data_files()
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        # stdout carries the MCP protocol, so report on stderr.
        print(f"unity-dev-tools: {exc}", file=sys.stderr)
        sys.exit(1)
    mcp.run(transport="stdio")

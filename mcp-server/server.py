"""Unity Developer Tools MCP Server.

Provides scaffold_script, lookup_api, shader_helper, and platform_info tools
for Unity game development in the Cursor IDE.
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


CSHARP_KEYWORDS = frozenset("""
abstract as base bool break byte case catch char checked class const continue
decimal default delegate do double else enum event explicit extern false finally
fixed float for foreach goto if implicit in int interface internal is lock long
namespace new null object operator out override params private protected public
readonly ref return sbyte sealed short sizeof stackalloc static string struct
switch this throw true try typeof uint ulong unchecked unsafe ushort using
virtual void volatile while
""".split())

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
        if effect_lower in entry.get("effect", "").lower():
            if pipeline in entry.get("pipelines", []):
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


if __name__ == "__main__":
    try:
        _check_data_files()
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        # stdout carries the MCP protocol, so report on stderr.
        print(f"unity-dev-tools: {exc}", file=sys.stderr)
        sys.exit(1)
    mcp.run(transport="stdio")

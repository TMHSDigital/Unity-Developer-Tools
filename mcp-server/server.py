"""Unity Developer Tools MCP Server.

Provides scaffold_script, lookup_api, shader_helper, and platform_info tools
for Unity game development in the Cursor IDE.
"""

import json
import os
from pathlib import Path

from mcp.server.fastmcp import FastMCP

DATA_PATH = Path(os.environ.get("UNITY_DATA_PATH", "./data"))

mcp = FastMCP("unity-dev-tools")


def _load_json(filename: str) -> list | dict:
    filepath = DATA_PATH / filename
    if not filepath.exists():
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


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
    [CustomEditor(typeof(TARGET_TYPE))]
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
    [CustomPropertyDrawer(typeof(TARGET_TYPE))]
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
    public interface IState
    {{
        void Enter();
        void Update();
        void FixedUpdate();
        void Exit();
    }}

    public class {name} : MonoBehaviour
    {{
        private IState _currentState;

        public void ChangeState(IState newState)
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


@mcp.tool()
def scaffold_script(
    type: str,
    name: str,
    namespace: str = "MyGame",
) -> str:
    """Generate a well-structured C# script following Unity conventions.

    Args:
        type: Script type (monobehaviour, scriptableobject, editor-window,
              custom-inspector, property-drawer, interface, state-machine, test)
        name: Class name for the generated script
        namespace: C# namespace (default: MyGame)
    """
    template = SCRIPT_TEMPLATES.get(type)
    if not template:
        valid = ", ".join(SCRIPT_TEMPLATES.keys())
        return f"Unknown script type: {type}. Valid types: {valid}"

    code = template.format(name=name, namespace=namespace)

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
    path = f"{folder_map.get(type, 'Assets/Scripts')}/{name}.cs"

    return f"// Recommended path: {path}\n\n{code}"


# ---------- Tool: lookup_api ----------

@mcp.tool()
def lookup_api(
    query: str,
    category: str = "",
) -> str:
    """Search the Unity API reference database.

    Args:
        query: Search term (class name, method name, or keyword)
        category: Optional filter (physics, ui, animation, audio, rendering,
                  input, networking, editor)
    """
    api_data = _load_json("unity_api_common.json")
    deprecated = _load_json("deprecated_patterns.json")

    query_lower = query.lower()
    results = []

    for entry in api_data:
        name = entry.get("name", "")
        desc = entry.get("description", "")
        cat = entry.get("category", "")

        if category and cat.lower() != category.lower():
            continue

        if query_lower in name.lower() or query_lower in desc.lower():
            results.append(entry)

    warnings = []
    for dep in deprecated:
        if query_lower in dep.get("legacy", "").lower():
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
        output.append(f"No API entries found for '{query}'.")
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

    effect_lower = effect.lower()
    results = []

    for entry in shader_data:
        if effect_lower in entry.get("effect", "").lower():
            if pipeline.lower() in entry.get("pipelines", []):
                results.append(entry)

    if not results:
        return (
            f"No shader patterns found for effect '{effect}' "
            f"on pipeline '{pipeline}'."
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

        if entry.get("code_snippet"):
            output.append(f"\n**Code**:\n```hlsl\n{entry['code_snippet']}\n```")

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
    mcp.run(transport="stdio")

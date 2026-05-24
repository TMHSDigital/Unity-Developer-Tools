---
title: Editor Scripting
description: Extending the Unity Editor with custom inspectors, editor windows, property drawers, gizmos, and Scene View overlays using UI Toolkit.
globs: ["**/Editor/**/*.cs"]
standards-version: 1.10.0
---

# Editor Scripting

## Overview

All editor scripts must be placed in an `Editor/` folder (or reference an Editor-only assembly definition). Code in Editor folders is excluded from player builds.

In Unity 6, UI Toolkit is the recommended system for editor UI. The legacy IMGUI (OnGUI/OnInspectorGUI) approach still works but is considered legacy for new tools.

## Custom Inspectors

### UI Toolkit Approach (Recommended)

```csharp
using UnityEditor;
using UnityEditor.UIElements;
using UnityEngine.UIElements;

[CustomEditor(typeof(EnemyConfig))]
public class EnemyConfigEditor : Editor
{
    public override VisualElement CreateInspectorGUI()
    {
        var root = new VisualElement();

        // Automatically creates fields for all serialized properties
        InspectorElement.FillDefaultInspector(root, serializedObject, this);

        // Add custom elements
        var healthBar = new ProgressBar
        {
            title = "Health Preview",
            value = ((EnemyConfig)target).MaxHealth / 100f
        };
        root.Add(healthBar);

        var testButton = new Button(() => Debug.Log("Test!"))
        {
            text = "Test Enemy"
        };
        root.Add(testButton);

        return root;
    }
}
```

### PropertyField for Automatic Serialization

`PropertyField` handles all serialization types automatically:

```csharp
public override VisualElement CreateInspectorGUI()
{
    var root = new VisualElement();

    var healthProp = new PropertyField(serializedObject.FindProperty("_maxHealth"));
    var speedProp = new PropertyField(serializedObject.FindProperty("_moveSpeed"));

    root.Add(healthProp);
    root.Add(speedProp);

    return root;
}
```

## Editor Windows

```csharp
public class LevelBuilderWindow : EditorWindow
{
    [MenuItem("Tools/Level Builder")]
    public static void ShowWindow()
    {
        GetWindow<LevelBuilderWindow>("Level Builder");
    }

    public void CreateGUI()
    {
        var root = rootVisualElement;

        root.Add(new Label("Level Builder Tool"));

        var prefabField = new ObjectField("Prefab")
        {
            objectType = typeof(GameObject)
        };
        root.Add(prefabField);

        var placeButton = new Button(() => PlacePrefab(prefabField.value as GameObject))
        {
            text = "Place in Scene"
        };
        root.Add(placeButton);
    }

    private void PlacePrefab(GameObject prefab)
    {
        if (!prefab) return;
        var instance = (GameObject)PrefabUtility.InstantiatePrefab(prefab);
        instance.transform.position = SceneView.lastActiveSceneView.pivot;
        Selection.activeGameObject = instance;
        Undo.RegisterCreatedObjectUndo(instance, "Place Prefab");
    }
}
```

## Property Drawers

Custom rendering for a specific type or attribute in the inspector:

```csharp
[CustomPropertyDrawer(typeof(RangedFloat))]
public class RangedFloatDrawer : PropertyDrawer
{
    public override VisualElement CreatePropertyGUI(SerializedProperty property)
    {
        var container = new VisualElement();
        container.style.flexDirection = FlexDirection.Row;

        var minField = new FloatField("Min") { bindingPath = "min" };
        var maxField = new FloatField("Max") { bindingPath = "max" };

        container.Add(minField);
        container.Add(maxField);

        return container;
    }
}
```

## Gizmos

Visual debugging in the Scene view:

```csharp
private void OnDrawGizmosSelected()
{
    Gizmos.color = Color.red;
    Gizmos.DrawWireSphere(transform.position, _attackRange);

    Gizmos.color = Color.yellow;
    Gizmos.DrawWireSphere(transform.position, _detectionRange);
}

private void OnDrawGizmos()
{
    // Always visible, even when not selected
    Gizmos.color = Color.green;
    Gizmos.DrawLine(transform.position, transform.position + transform.forward * 2f);
}
```

## Scene View Overlays

Overlays are the modern replacement for floating IMGUI windows in the Scene view:

```csharp
using UnityEditor;
using UnityEditor.Overlays;
using UnityEngine.UIElements;

[Overlay(typeof(SceneView), "Quick Placer", true)]
public class QuickPlacerOverlay : Overlay
{
    public override VisualElement CreatePanelContent()
    {
        var root = new VisualElement();
        root.Add(new Label("Quick Placer"));
        root.Add(new Button(() => PlaceObject()) { text = "Place Object" });
        return root;
    }

    private void PlaceObject() { /* placement logic */ }
}
```

## Menu Items

```csharp
[MenuItem("Tools/Reset Player Position")]
private static void ResetPlayerPosition()
{
    var player = FindFirstObjectByType<PlayerController>();
    if (player)
    {
        Undo.RecordObject(player.transform, "Reset Player Position");
        player.transform.position = Vector3.zero;
    }
}

[MenuItem("Tools/Reset Player Position", true)]
private static bool ValidateResetPlayerPosition()
{
    return FindFirstObjectByType<PlayerController>() != null;
}
```

## Editor Callbacks

```csharp
[InitializeOnLoadMethod]
private static void OnEditorLoad()
{
    EditorApplication.playModeStateChanged += OnPlayModeChanged;
}

private static void OnPlayModeChanged(PlayModeStateChange state)
{
    if (state == PlayModeStateChange.EnteredPlayMode)
    {
        Debug.Log("Entered Play Mode");
    }
}
```

## AssetDatabase

Programmatic asset manipulation:

```csharp
// Create an asset
AssetDatabase.CreateAsset(myScriptableObject, "Assets/Data/Config.asset");

// Find assets by type
string[] guids = AssetDatabase.FindAssets("t:ScriptableObject", new[] { "Assets/Data" });

// Refresh after external changes
AssetDatabase.Refresh();
```

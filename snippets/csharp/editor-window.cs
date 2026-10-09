// Editor Window using UI Toolkit
// Custom tool window accessible from the Tools menu.
// Place in an Editor/ folder. The UNITY_EDITOR guard keeps player builds safe if it is not.

#if UNITY_EDITOR
using UnityEditor;
using UnityEditor.UIElements;
using UnityEngine;
using UnityEngine.UIElements;

namespace MyGame.Editor
{
    public class QuickPlacer : EditorWindow
    {
        [MenuItem("Tools/Quick Placer")]
        public static void ShowWindow()
        {
            var window = GetWindow<QuickPlacer>("Quick Placer");
            window.minSize = new Vector2(300, 200);
        }

        public void CreateGUI()
        {
            var root = rootVisualElement;

            root.Add(new Label("Quick Placer Tool")
            {
                style = { fontSize = 16, unityFontStyleAndWeight = FontStyle.Bold, marginBottom = 10 }
            });

            var prefabField = new ObjectField("Prefab to Place")
            {
                objectType = typeof(GameObject),
                allowSceneObjects = false
            };
            root.Add(prefabField);

            var placeButton = new Button(() =>
            {
                var prefab = prefabField.value as GameObject;
                if (prefab == null)
                {
                    Debug.LogWarning("Select a prefab first");
                    return;
                }

                var sceneView = SceneView.lastActiveSceneView;
                if (sceneView == null) return;

                var instance = (GameObject)PrefabUtility.InstantiatePrefab(prefab);
                instance.transform.position = sceneView.pivot;
                Undo.RegisterCreatedObjectUndo(instance, "Place Prefab");
                Selection.activeGameObject = instance;
            })
            {
                text = "Place at Scene View Center"
            };
            placeButton.style.marginTop = 10;
            root.Add(placeButton);
        }
    }
}
#endif

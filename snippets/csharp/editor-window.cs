// Editor Window using UI Toolkit
// Custom tool window accessible from the Tools menu.
// Place in an Editor/ folder.

using UnityEditor;
using UnityEngine;
using UnityEngine.UIElements;

namespace MyGame.Editor
{
    public class QuickPlacer : EditorWindow
    {
        [SerializeField] private VisualTreeAsset _layout;

        private ObjectField _prefabField;

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

            var prefabField = new UnityEditor.UIElements.ObjectField("Prefab to Place")
            {
                objectType = typeof(GameObject)
            };
            root.Add(prefabField);

            var spacing = new FloatField("Grid Spacing") { value = 2f };
            root.Add(spacing);

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
                Selection.activeGameObject = instance;
                Undo.RegisterCreatedObjectUndo(instance, "Place Prefab");
            })
            {
                text = "Place at Scene View Center"
            };
            placeButton.style.marginTop = 10;
            root.Add(placeButton);
        }
    }
}

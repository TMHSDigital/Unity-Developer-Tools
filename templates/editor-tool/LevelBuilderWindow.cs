using UnityEditor;
using UnityEngine;
using UnityEngine.UIElements;

namespace MyGame.Editor
{
    public class LevelBuilderWindow : EditorWindow
    {
        private UnityEditor.UIElements.ObjectField _prefabField;
        private FloatField _gridSizeField;
        private Toggle _snapToggle;
        private Label _statusLabel;

        private GameObject _selectedPrefab;
        private float _gridSize = 1f;
        private bool _snapToGrid = true;

        [MenuItem("Tools/Level Builder")]
        public static void ShowWindow()
        {
            var window = GetWindow<LevelBuilderWindow>("Level Builder");
            window.minSize = new Vector2(350, 400);
        }

        public void CreateGUI()
        {
            var root = rootVisualElement;

            // Title
            root.Add(new Label("Level Builder")
            {
                style =
                {
                    fontSize = 18,
                    unityFontStyleAndWeight = FontStyle.Bold,
                    marginBottom = 10,
                    marginTop = 5,
                    marginLeft = 5
                }
            });

            // Prefab selector
            _prefabField = new UnityEditor.UIElements.ObjectField("Prefab")
            {
                objectType = typeof(GameObject)
            };
            _prefabField.RegisterValueChangedCallback(e =>
            {
                _selectedPrefab = e.newValue as GameObject;
                UpdateStatus();
            });
            root.Add(_prefabField);

            // Grid size
            _gridSizeField = new FloatField("Grid Size") { value = _gridSize };
            _gridSizeField.RegisterValueChangedCallback(e => _gridSize = Mathf.Max(0.1f, e.newValue));
            root.Add(_gridSizeField);

            // Snap toggle
            _snapToggle = new Toggle("Snap to Grid") { value = _snapToGrid };
            _snapToggle.RegisterValueChangedCallback(e => _snapToGrid = e.newValue);
            root.Add(_snapToggle);

            // Action buttons
            var buttonContainer = new VisualElement
            {
                style = { flexDirection = FlexDirection.Row, marginTop = 10 }
            };

            buttonContainer.Add(new Button(PlaceAtSceneCenter)
            {
                text = "Place at Center",
                style = { flexGrow = 1 }
            });

            buttonContainer.Add(new Button(PlaceAtOrigin)
            {
                text = "Place at Origin",
                style = { flexGrow = 1 }
            });

            root.Add(buttonContainer);

            // Status
            _statusLabel = new Label("Select a prefab to begin")
            {
                style = { marginTop = 10, color = Color.gray }
            };
            root.Add(_statusLabel);

            UpdateStatus();
        }

        private void PlaceAtSceneCenter()
        {
            if (!_selectedPrefab) return;

            var sceneView = SceneView.lastActiveSceneView;
            if (sceneView == null) return;

            Vector3 position = sceneView.pivot;
            if (_snapToGrid)
                position = SnapPosition(position);

            PlacePrefab(position);
        }

        private void PlaceAtOrigin()
        {
            if (!_selectedPrefab) return;
            PlacePrefab(Vector3.zero);
        }

        private void PlacePrefab(Vector3 position)
        {
            var instance = (GameObject)PrefabUtility.InstantiatePrefab(_selectedPrefab);
            instance.transform.position = position;
            Selection.activeGameObject = instance;
            Undo.RegisterCreatedObjectUndo(instance, "Place Prefab");
            UpdateStatus();
        }

        private Vector3 SnapPosition(Vector3 pos)
        {
            return new Vector3(
                Mathf.Round(pos.x / _gridSize) * _gridSize,
                Mathf.Round(pos.y / _gridSize) * _gridSize,
                Mathf.Round(pos.z / _gridSize) * _gridSize
            );
        }

        private void UpdateStatus()
        {
            if (_statusLabel == null) return;
            _statusLabel.text = _selectedPrefab
                ? $"Ready: {_selectedPrefab.name}"
                : "Select a prefab to begin";
        }
    }
}

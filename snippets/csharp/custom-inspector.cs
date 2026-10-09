// Custom Inspector using UI Toolkit
// Override the default inspector for a MonoBehaviour or ScriptableObject.
// Save as EnemyConfig.cs in a runtime folder (the file name must match the MonoBehaviour).
// The editor class is wrapped in UNITY_EDITOR so it is stripped from player builds.
// For larger projects, move the editor class into its own file under an Editor/ folder instead.

using UnityEngine;
#if UNITY_EDITOR
using UnityEditor;
using UnityEditor.UIElements;
using UnityEngine.UIElements;
#endif

namespace MyGame
{
    // The target component
    public class EnemyConfig : MonoBehaviour
    {
        [SerializeField] private string _enemyName = "Goblin";
        [SerializeField] [Range(1, 1000)] private int _maxHealth = 100;
        [SerializeField] private float _moveSpeed = 3f;
        [SerializeField] private Color _debugColor = Color.red;

        public string EnemyName => _enemyName;
        public int MaxHealth => _maxHealth;
        public float MoveSpeed => _moveSpeed;
        public Color DebugColor => _debugColor;
    }
}

#if UNITY_EDITOR
namespace MyGame.Editor
{
    [CustomEditor(typeof(EnemyConfig))]
    public class EnemyConfigEditor : UnityEditor.Editor
    {
        public override VisualElement CreateInspectorGUI()
        {
            var root = new VisualElement();

            // Draw default fields
            InspectorElement.FillDefaultInspector(root, serializedObject, this);

            // Add a preview section that follows the serialized value
            var previewLabel = new Label("Preview");
            previewLabel.style.unityFontStyleAndWeight = FontStyle.Bold;
            previewLabel.style.marginTop = 10;
            root.Add(previewLabel);

            var nameProperty = serializedObject.FindProperty("_enemyName");
            var infoLabel = new Label($"Enemy: {nameProperty.stringValue}");
            infoLabel.TrackPropertyValue(nameProperty, p => infoLabel.text = $"Enemy: {p.stringValue}");
            root.Add(infoLabel);

            // Add a utility button
            var testButton = new Button(() => Debug.Log($"Testing {((EnemyConfig)target).EnemyName}"))
            {
                text = "Test Configuration"
            };
            testButton.style.marginTop = 5;
            root.Add(testButton);

            return root;
        }
    }
}
#endif

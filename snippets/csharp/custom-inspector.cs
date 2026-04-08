// Custom Inspector using UI Toolkit
// Override the default inspector for a MonoBehaviour or ScriptableObject.
// Place in an Editor/ folder.

using UnityEditor;
using UnityEditor.UIElements;
using UnityEngine;
using UnityEngine.UIElements;

namespace MyGame.Editor
{
    // The target component
    public class EnemyConfig : MonoBehaviour
    {
        [SerializeField] private string _enemyName = "Goblin";
        [SerializeField] [Range(1, 1000)] private int _maxHealth = 100;
        [SerializeField] private float _moveSpeed = 3f;
        [SerializeField] private Color _debugColor = Color.red;
    }

    [CustomEditor(typeof(EnemyConfig))]
    public class EnemyConfigEditor : UnityEditor.Editor
    {
        public override VisualElement CreateInspectorGUI()
        {
            var root = new VisualElement();

            // Draw default fields
            InspectorElement.FillDefaultInspector(root, serializedObject, this);

            // Add a preview section
            var previewLabel = new Label("--- Preview ---");
            previewLabel.style.unityFontStyleAndWeight = FontStyle.Bold;
            previewLabel.style.marginTop = 10;
            root.Add(previewLabel);

            var config = (EnemyConfig)target;
            var infoLabel = new Label($"Enemy: {serializedObject.FindProperty("_enemyName").stringValue}");
            root.Add(infoLabel);

            // Add a utility button
            var testButton = new Button(() => Debug.Log("Testing enemy config..."))
            {
                text = "Test Configuration"
            };
            testButton.style.marginTop = 5;
            root.Add(testButton);

            return root;
        }
    }
}

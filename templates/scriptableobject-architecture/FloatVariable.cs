using UnityEngine;

namespace SOArchitecture
{
    [CreateAssetMenu(fileName = "New Float Variable", menuName = "Variables/Float")]
    public class FloatVariable : ScriptableObject
    {
        [SerializeField] private float _initialValue;

        [System.NonSerialized]
        public float RuntimeValue;

        private void OnEnable()
        {
            RuntimeValue = _initialValue;
#if UNITY_EDITOR
            // With Enter Play Mode Options (no domain reload) OnEnable does not run again
            // on Play, so reset explicitly when entering Play Mode
            UnityEditor.EditorApplication.playModeStateChanged -= OnPlayModeStateChanged;
            UnityEditor.EditorApplication.playModeStateChanged += OnPlayModeStateChanged;
#endif
        }

#if UNITY_EDITOR
        private void OnDisable()
        {
            UnityEditor.EditorApplication.playModeStateChanged -= OnPlayModeStateChanged;
        }

        private void OnPlayModeStateChanged(UnityEditor.PlayModeStateChange state)
        {
            if (state == UnityEditor.PlayModeStateChange.ExitingEditMode)
                RuntimeValue = _initialValue;
        }
#endif

        public void SetValue(float value) => RuntimeValue = value;
        public void Add(float amount) => RuntimeValue += amount;
        public void Subtract(float amount) => RuntimeValue -= amount;
    }
}

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
        }

        public void SetValue(float value) => RuntimeValue = value;
        public void Add(float amount) => RuntimeValue += amount;
        public void Subtract(float amount) => RuntimeValue -= amount;
    }
}

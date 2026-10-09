using UnityEngine;

namespace SOArchitecture
{
    // Add to any GameObject that should appear in a TransformRuntimeSet while it is active
    public class RuntimeSetMember : MonoBehaviour
    {
        [SerializeField] private TransformRuntimeSet _set;

        private void OnEnable()
        {
            if (_set) _set.Add(transform);
        }

        private void OnDisable()
        {
            if (_set) _set.Remove(transform);
        }
    }
}

// MonoBehaviour Template
// Starting point for any new MonoBehaviour script.
// Includes lifecycle methods, component caching, and proper cleanup.

using UnityEngine;

namespace MyGame
{
    public class MyComponent : MonoBehaviour
    {
        [Header("Configuration")]
        [SerializeField] private float _speed = 5f;
        [SerializeField] private LayerMask _groundLayer;

        [Header("References")]
        [SerializeField] private Transform _target;

        private Rigidbody _rb;

        private void Awake()
        {
            _rb = GetComponent<Rigidbody>();
        }

        private void OnEnable()
        {
            // Subscribe to events
        }

        private void OnDisable()
        {
            // Unsubscribe from events
        }

        private void Start()
        {
            // Cross-object initialization
        }

        private void Update()
        {
            // Per-frame logic
        }

        private void FixedUpdate()
        {
            // Physics logic
        }

        private void OnDestroy()
        {
            // Final cleanup
        }
    }
}

// Input System Actions
// Modern input handling with the Input System package (1.8+) and project-wide actions.
// Unity 6 projects ship a default actions asset with "Player/Move" and "Player/Jump";
// assign your own under Project Settings > Input System Package if you use different names.

using UnityEngine;
using UnityEngine.InputSystem;

namespace MyGame
{
    [RequireComponent(typeof(Rigidbody))]
    public class InputController : MonoBehaviour
    {
        [SerializeField] private float _moveSpeed = 6f;
        [SerializeField] private float _jumpForce = 8f;

        private InputAction _moveAction;
        private InputAction _jumpAction;
        private Rigidbody _rb;
        private Vector2 _moveInput;
        private bool _jumpRequested;

        private void Awake()
        {
            _rb = GetComponent<Rigidbody>();
            _moveAction = InputSystem.actions.FindAction("Player/Move", throwIfNotFound: true);
            _jumpAction = InputSystem.actions.FindAction("Player/Jump", throwIfNotFound: true);
        }

        private void Update()
        {
            _moveInput = _moveAction.ReadValue<Vector2>();

            // Latch the press here; FixedUpdate may not run on the frame it happens
            if (_jumpAction.WasPressedThisFrame())
            {
                _jumpRequested = true;
            }
        }

        private void FixedUpdate()
        {
            Vector3 movement = new Vector3(_moveInput.x, 0f, _moveInput.y) * _moveSpeed;
            _rb.linearVelocity = new Vector3(movement.x, _rb.linearVelocity.y, movement.z);

            if (_jumpRequested)
            {
                _rb.AddForce(Vector3.up * _jumpForce, ForceMode.Impulse);
                _jumpRequested = false;
            }
        }
    }
}

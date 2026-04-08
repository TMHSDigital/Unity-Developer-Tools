// Input System Actions
// Modern input handling with the Input System package.
// Uses direct C# API with composite bindings for efficient input reading.

using UnityEngine;
using UnityEngine.InputSystem;

namespace MyGame
{
    [RequireComponent(typeof(Rigidbody))]
    public class InputController : MonoBehaviour
    {
        [SerializeField] private float _moveSpeed = 6f;
        [SerializeField] private float _jumpForce = 8f;

        private PlayerInputActions _input;
        private Rigidbody _rb;
        private Vector2 _moveInput;
        private bool _jumpRequested;

        private void Awake()
        {
            _rb = GetComponent<Rigidbody>();
            _input = new PlayerInputActions();
        }

        private void OnEnable()
        {
            _input.Player.Enable();
            _input.Player.Jump.performed += OnJump;
        }

        private void OnDisable()
        {
            _input.Player.Jump.performed -= OnJump;
            _input.Player.Disable();
        }

        private void Update()
        {
            _moveInput = _input.Player.Move.ReadValue<Vector2>();
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

        private void OnJump(InputAction.CallbackContext ctx)
        {
            _jumpRequested = true;
        }
    }
}

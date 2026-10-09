using UnityEngine;
using UnityEngine.InputSystem;

namespace FPS3D
{
    [RequireComponent(typeof(CharacterController))]
    public class FPSController : MonoBehaviour
    {
        [Header("Movement")]
        [SerializeField] private float _moveSpeed = 6f;
        [SerializeField] private float _sprintMultiplier = 1.5f;
        [SerializeField] private float _jumpHeight = 1.2f;
        [SerializeField] private float _gravity = -20f;

        [Header("Mouse Look")]
        [SerializeField] private Transform _cameraTransform;
        [SerializeField] private float _mouseSensitivity = 2f;
        [SerializeField] private float _maxLookAngle = 80f;

        private CharacterController _controller;
        private Vector2 _moveInput;
        private Vector2 _lookInput;
        private float _verticalVelocity;
        private float _cameraPitch;
        private InputAction _sprintAction;

        private void Awake()
        {
            _controller = GetComponent<CharacterController>();

            // Player Input's Send Messages mode does not report button releases,
            // so held buttons are read directly from the project-wide actions
            _sprintAction = InputSystem.actions.FindAction("Player/Sprint");
            Cursor.lockState = CursorLockMode.Locked;
            Cursor.visible = false;
        }

        private void Update()
        {
            // Mouse delta is not scaled by time, so skip look while the game is paused (timeScale 0)
            if (Time.timeScale > 0f)
                HandleLook();
            HandleMovement();
        }

        public void OnMove(InputValue value) => _moveInput = value.Get<Vector2>();
        public void OnLook(InputValue value) => _lookInput = value.Get<Vector2>();

        public void OnJump(InputValue value)
        {
            if (value.isPressed && _controller.isGrounded)
            {
                _verticalVelocity = Mathf.Sqrt(_jumpHeight * -2f * _gravity);
            }
        }

        private void HandleLook()
        {
            _cameraPitch -= _lookInput.y * _mouseSensitivity;
            _cameraPitch = Mathf.Clamp(_cameraPitch, -_maxLookAngle, _maxLookAngle);

            _cameraTransform.localRotation = Quaternion.Euler(_cameraPitch, 0f, 0f);
            transform.Rotate(Vector3.up * _lookInput.x * _mouseSensitivity);
        }

        private void HandleMovement()
        {
            if (_controller.isGrounded && _verticalVelocity < 0f)
                _verticalVelocity = -2f;

            bool isSprinting = _sprintAction != null && _sprintAction.IsPressed();
            float speed = isSprinting ? _moveSpeed * _sprintMultiplier : _moveSpeed;
            Vector3 move = transform.right * _moveInput.x + transform.forward * _moveInput.y;
            _controller.Move(move * speed * Time.deltaTime);

            _verticalVelocity += _gravity * Time.deltaTime;
            _controller.Move(Vector3.up * _verticalVelocity * Time.deltaTime);
        }
    }
}

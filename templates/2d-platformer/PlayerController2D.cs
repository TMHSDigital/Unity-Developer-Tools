using UnityEngine;
using UnityEngine.InputSystem;

namespace Platformer2D
{
    [RequireComponent(typeof(Rigidbody2D))]
    [RequireComponent(typeof(BoxCollider2D))]
    public class PlayerController2D : MonoBehaviour
    {
        [Header("Movement")]
        [SerializeField] private float _moveSpeed = 8f;
        [SerializeField] private float _jumpForce = 14f;
        [SerializeField] private float _coyoteTime = 0.15f;
        [SerializeField] private float _jumpBufferTime = 0.1f;

        [Header("Ground Check")]
        [SerializeField] private Transform _groundCheck;
        [SerializeField] private float _groundCheckRadius = 0.2f;
        [SerializeField] private LayerMask _groundLayer;

        private Rigidbody2D _rb;
        private SpriteRenderer _sprite;
        private Animator _animator;

        private Vector2 _moveInput;
        private float _coyoteCounter;
        private float _jumpBufferCounter;
        private bool _isGrounded;

        private void Awake()
        {
            _rb = GetComponent<Rigidbody2D>();
            TryGetComponent(out _sprite);
            TryGetComponent(out _animator);
        }

        private void Update()
        {
            CheckGround();
            HandleCoyoteTime();
            HandleJumpBuffer();
            HandleFlip();
            UpdateAnimator();
        }

        private void FixedUpdate()
        {
            _rb.linearVelocity = new Vector2(_moveInput.x * _moveSpeed, _rb.linearVelocity.y);
        }

        public void OnMove(InputValue value)
        {
            _moveInput = value.Get<Vector2>();
        }

        public void OnJump(InputValue value)
        {
            if (value.isPressed)
            {
                _jumpBufferCounter = _jumpBufferTime;
            }
        }

        private void CheckGround()
        {
            _isGrounded = Physics2D.OverlapCircle(
                _groundCheck.position, _groundCheckRadius, _groundLayer
            );
        }

        private void HandleCoyoteTime()
        {
            if (_isGrounded)
                _coyoteCounter = _coyoteTime;
            else
                _coyoteCounter -= Time.deltaTime;
        }

        private void HandleJumpBuffer()
        {
            if (_jumpBufferCounter > 0f)
            {
                _jumpBufferCounter -= Time.deltaTime;

                if (_coyoteCounter > 0f)
                {
                    _rb.linearVelocity = new Vector2(_rb.linearVelocity.x, _jumpForce);
                    _jumpBufferCounter = 0f;
                    _coyoteCounter = 0f;
                }
            }
        }

        private void HandleFlip()
        {
            if (_sprite && _moveInput.x != 0f)
            {
                _sprite.flipX = _moveInput.x < 0f;
            }
        }

        private void UpdateAnimator()
        {
            if (!_animator) return;
            _animator.SetFloat("Speed", Mathf.Abs(_moveInput.x));
            _animator.SetBool("IsGrounded", _isGrounded);
            _animator.SetFloat("VerticalSpeed", _rb.linearVelocity.y);
        }

        private void OnDrawGizmosSelected()
        {
            if (_groundCheck)
            {
                Gizmos.color = Color.green;
                Gizmos.DrawWireSphere(_groundCheck.position, _groundCheckRadius);
            }
        }
    }
}

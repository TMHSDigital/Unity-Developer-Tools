using UnityEngine;

namespace Platformer2D
{
    public class CameraFollow2D : MonoBehaviour
    {
        [Header("Target")]
        [SerializeField] private Transform _target;

        [Header("Follow Settings")]
        [Tooltip("Higher values catch up faster. Frame-rate independent.")]
        [SerializeField] private float _smoothSpeed = 8f;
        [SerializeField] private Vector3 _offset = new(0f, 1f, -10f);

        [Header("Dead Zone")]
        [Tooltip("The target can move this far (world units) from the camera focus before the camera follows.")]
        [SerializeField] private Vector2 _deadZone = new(1f, 0.5f);

        [Header("Bounds (optional)")]
        [SerializeField] private bool _useBounds;
        [SerializeField] private float _minX = -10f;
        [SerializeField] private float _maxX = 10f;
        [SerializeField] private float _minY = -5f;
        [SerializeField] private float _maxY = 5f;

        private Vector3 _focus;

        private void Start()
        {
            if (_target) _focus = _target.position;
        }

        private void LateUpdate()
        {
            if (!_target) return;

            // Move the focus point only when the target leaves the dead zone
            Vector3 delta = _target.position - _focus;
            if (Mathf.Abs(delta.x) > _deadZone.x)
                _focus.x += delta.x - Mathf.Sign(delta.x) * _deadZone.x;
            if (Mathf.Abs(delta.y) > _deadZone.y)
                _focus.y += delta.y - Mathf.Sign(delta.y) * _deadZone.y;

            Vector3 targetPosition = _focus + _offset;

            if (_useBounds)
            {
                targetPosition.x = Mathf.Clamp(targetPosition.x, _minX, _maxX);
                targetPosition.y = Mathf.Clamp(targetPosition.y, _minY, _maxY);
            }

            float t = 1f - Mathf.Exp(-_smoothSpeed * Time.deltaTime);
            transform.position = Vector3.Lerp(transform.position, targetPosition, t);
        }

        private void OnDrawGizmosSelected()
        {
            Vector3 center = Application.isPlaying ? _focus : (_target ? _target.position : transform.position);
            Gizmos.color = Color.yellow;
            Gizmos.DrawWireCube(center, new Vector3(_deadZone.x * 2f, _deadZone.y * 2f, 0f));
        }
    }
}

using UnityEngine;

namespace Platformer2D
{
    public class CameraFollow2D : MonoBehaviour
    {
        [Header("Target")]
        [SerializeField] private Transform _target;

        [Header("Follow Settings")]
        [SerializeField] private float _smoothSpeed = 8f;
        [SerializeField] private Vector3 _offset = new(0f, 1f, -10f);

        [Header("Bounds (optional)")]
        [SerializeField] private bool _useBounds;
        [SerializeField] private float _minX = -10f;
        [SerializeField] private float _maxX = 10f;
        [SerializeField] private float _minY = -5f;
        [SerializeField] private float _maxY = 5f;

        private void LateUpdate()
        {
            if (!_target) return;

            Vector3 targetPosition = _target.position + _offset;

            if (_useBounds)
            {
                targetPosition.x = Mathf.Clamp(targetPosition.x, _minX, _maxX);
                targetPosition.y = Mathf.Clamp(targetPosition.y, _minY, _maxY);
            }

            transform.position = Vector3.Lerp(
                transform.position, targetPosition, _smoothSpeed * Time.deltaTime
            );
        }
    }
}

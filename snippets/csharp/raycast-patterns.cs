// Raycast Patterns
// Common raycasting techniques with zero-allocation NonAlloc variants.

using UnityEngine;

namespace MyGame
{
    public class RaycastExamples : MonoBehaviour
    {
        [SerializeField] private LayerMask _interactableLayer;
        [SerializeField] private float _interactRange = 3f;
        [SerializeField] private float _groundCheckDistance = 1.1f;

        private Camera _mainCam;
        private readonly RaycastHit[] _hitBuffer = new RaycastHit[10];

        private void Awake()
        {
            _mainCam = Camera.main;
        }

        // Single raycast from camera center
        public bool TryGetLookedAtObject(out RaycastHit hit)
        {
            Ray ray = _mainCam.ViewportPointToRay(new Vector3(0.5f, 0.5f, 0f));
            return Physics.Raycast(ray, out hit, _interactRange, _interactableLayer);
        }

        // Ground check with short downward ray
        public bool IsGrounded()
        {
            return Physics.Raycast(
                transform.position, Vector3.down,
                _groundCheckDistance, _interactableLayer
            );
        }

        // NonAlloc multi-hit (zero GC allocation)
        public int GetAllHitsInDirection(Vector3 direction)
        {
            return Physics.RaycastNonAlloc(
                transform.position, direction,
                _hitBuffer, _interactRange, _interactableLayer
            );
        }

        // Sphere overlap for area detection (NonAlloc)
        private readonly Collider[] _overlapBuffer = new Collider[20];

        public int GetNearbyObjects(float radius)
        {
            return Physics.OverlapSphereNonAlloc(
                transform.position, radius,
                _overlapBuffer, _interactableLayer
            );
        }
    }
}

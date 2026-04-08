// Object Pool Pattern
// Reuse objects instead of Instantiate/Destroy to reduce GC pressure.
// Uses Unity's built-in ObjectPool<T> for thread-safe pooling.

using UnityEngine;
using UnityEngine.Pool;

namespace MyGame
{
    public class ProjectilePool : MonoBehaviour
    {
        [SerializeField] private GameObject _prefab;
        [SerializeField] private int _defaultCapacity = 20;
        [SerializeField] private int _maxSize = 100;

        private ObjectPool<GameObject> _pool;

        private void Awake()
        {
            _pool = new ObjectPool<GameObject>(
                createFunc: CreateProjectile,
                actionOnGet: OnGetProjectile,
                actionOnRelease: OnReleaseProjectile,
                actionOnDestroy: OnDestroyProjectile,
                collectionCheck: true,
                defaultCapacity: _defaultCapacity,
                maxSize: _maxSize
            );
        }

        public GameObject Get() => _pool.Get();

        public void Release(GameObject obj) => _pool.Release(obj);

        private GameObject CreateProjectile()
        {
            var obj = Instantiate(_prefab);
            obj.SetActive(false);
            return obj;
        }

        private void OnGetProjectile(GameObject obj) => obj.SetActive(true);
        private void OnReleaseProjectile(GameObject obj) => obj.SetActive(false);
        private void OnDestroyProjectile(GameObject obj) => Destroy(obj);
    }
}

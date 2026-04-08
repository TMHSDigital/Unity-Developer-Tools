using UnityEngine;
using UnityEngine.InputSystem;

namespace FPS3D
{
    public class WeaponSystem : MonoBehaviour
    {
        [Header("Weapon Stats")]
        [SerializeField] private float _fireRate = 10f;
        [SerializeField] private float _damage = 25f;
        [SerializeField] private float _range = 100f;
        [SerializeField] private int _maxAmmo = 30;
        [SerializeField] private float _reloadTime = 1.5f;

        [Header("References")]
        [SerializeField] private Transform _muzzlePoint;
        [SerializeField] private LayerMask _hitLayers;
        [SerializeField] private ParticleSystem _muzzleFlash;

        private int _currentAmmo;
        private float _nextFireTime;
        private bool _isReloading;
        private bool _fireHeld;
        private Camera _mainCam;

        public int CurrentAmmo => _currentAmmo;
        public int MaxAmmo => _maxAmmo;
        public bool IsReloading => _isReloading;

        private void Awake()
        {
            _mainCam = Camera.main;
            _currentAmmo = _maxAmmo;
        }

        private void Update()
        {
            if (_fireHeld && !_isReloading && Time.time >= _nextFireTime && _currentAmmo > 0)
            {
                Fire();
            }
        }

        public void OnFire(InputValue value) => _fireHeld = value.isPressed;

        public async void OnReload(InputValue value)
        {
            if (value.isPressed && !_isReloading && _currentAmmo < _maxAmmo)
            {
                await ReloadAsync();
            }
        }

        private void Fire()
        {
            _nextFireTime = Time.time + 1f / _fireRate;
            _currentAmmo--;

            if (_muzzleFlash)
                _muzzleFlash.Play();

            Ray ray = _mainCam.ViewportPointToRay(new Vector3(0.5f, 0.5f, 0f));
            if (Physics.Raycast(ray, out RaycastHit hit, _range, _hitLayers))
            {
                if (hit.collider.TryGetComponent<IDamageable>(out var target))
                {
                    target.TakeDamage(Mathf.RoundToInt(_damage));
                }
            }

            if (_currentAmmo <= 0)
            {
                _ = ReloadAsync();
            }
        }

        private async Awaitable ReloadAsync()
        {
            _isReloading = true;
            await Awaitable.WaitForSecondsAsync(_reloadTime, destroyCancellationToken);
            _currentAmmo = _maxAmmo;
            _isReloading = false;
        }
    }

    public interface IDamageable
    {
        void TakeDamage(int amount);
    }
}

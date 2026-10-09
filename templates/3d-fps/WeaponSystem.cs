using System;
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
        private InputAction _attackAction;
        private Camera _mainCam;

        public int CurrentAmmo => _currentAmmo;
        public int MaxAmmo => _maxAmmo;
        public bool IsReloading => _isReloading;

        private void Awake()
        {
            _mainCam = Camera.main;

            // Player Input's Send Messages mode does not report button releases,
            // so the held fire button is read directly from the project-wide actions
            _attackAction = InputSystem.actions.FindAction("Player/Attack", throwIfNotFound: true);
            _currentAmmo = _maxAmmo;
        }

        private void Update()
        {
            if (Time.timeScale <= 0f) return;

            if (_attackAction.IsPressed() && !_isReloading && Time.time >= _nextFireTime && _currentAmmo > 0)
            {
                Fire();
            }
        }

        // Needs a "Reload" action added to the Player action map (see README)
        public void OnReload(InputValue value)
        {
            if (value.isPressed)
                StartReload();
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
                StartReload();
            }
        }

        // async void is the entry point so Unity logs any exception; cancellation is expected
        private async void StartReload()
        {
            if (_isReloading || _currentAmmo >= _maxAmmo) return;

            _isReloading = true;
            try
            {
                await Awaitable.WaitForSecondsAsync(_reloadTime, destroyCancellationToken);
                _currentAmmo = _maxAmmo;
            }
            catch (OperationCanceledException)
            {
                // The weapon was destroyed mid-reload
            }
            finally
            {
                _isReloading = false;
            }
        }
    }

    public interface IDamageable
    {
        void TakeDamage(int amount);
    }
}

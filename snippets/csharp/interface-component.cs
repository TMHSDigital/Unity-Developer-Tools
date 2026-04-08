// Interface Component Pattern
// Use interfaces to define contracts for game systems.
// Enables polymorphism across unrelated MonoBehaviours.

using UnityEngine;

namespace MyGame
{
    public interface IDamageable
    {
        int CurrentHealth { get; }
        int MaxHealth { get; }
        bool IsAlive { get; }
        void TakeDamage(int amount);
        void Heal(int amount);
    }

    public interface IInteractable
    {
        string InteractionPrompt { get; }
        bool CanInteract { get; }
        void Interact(GameObject interactor);
    }

    // Example: Damageable enemy
    public class EnemyHealth : MonoBehaviour, IDamageable
    {
        [SerializeField] private int _maxHealth = 100;
        private int _currentHealth;

        public int CurrentHealth => _currentHealth;
        public int MaxHealth => _maxHealth;
        public bool IsAlive => _currentHealth > 0;

        private void Awake()
        {
            _currentHealth = _maxHealth;
        }

        public void TakeDamage(int amount)
        {
            _currentHealth = Mathf.Max(0, _currentHealth - amount);
            if (!IsAlive)
                Die();
        }

        public void Heal(int amount)
        {
            _currentHealth = Mathf.Min(_maxHealth, _currentHealth + amount);
        }

        private void Die()
        {
            Debug.Log($"{name} died");
            gameObject.SetActive(false);
        }
    }

    // Usage with TryGetComponent
    public class DamageDealer : MonoBehaviour
    {
        [SerializeField] private int _damage = 25;

        private void OnTriggerEnter(Collider other)
        {
            if (other.TryGetComponent<IDamageable>(out var target))
            {
                target.TakeDamage(_damage);
            }
        }
    }
}

// Unity Singleton Pattern
// Use for managers that need exactly one instance (AudioManager, GameManager).
// Survives scene loads. Self-creates if missing.
// Uses FindFirstObjectByType (not the deprecated FindObjectOfType).
// Works with Enter Play Mode Options (domain reload disabled).
// Unity APIs are main-thread only, so no lock is needed.

using UnityEngine;

namespace MyGame
{
    public class Singleton<T> : MonoBehaviour where T : MonoBehaviour
    {
        private static T _instance;

        public static T Instance
        {
            get
            {
                // Avoid creating a new object while the application shuts down
                if (SingletonState.IsQuitting)
                    return null;

                // Unity's == treats a destroyed object (e.g. from a previous play session) as null
                if (_instance == null)
                {
                    _instance = FindFirstObjectByType<T>();

                    if (_instance == null)
                    {
                        // AddComponent runs Awake, which registers and persists the instance
                        new GameObject(typeof(T).Name).AddComponent<T>();
                    }
                }

                return _instance;
            }
        }

        protected virtual void Awake()
        {
            if (_instance == null)
            {
                _instance = this as T;
            }
            else if (_instance != this)
            {
                Destroy(gameObject);
                return;
            }

            // Also covers the case where Instance found this object before its Awake ran
            DontDestroyOnLoad(gameObject);
        }

        protected virtual void OnDestroy()
        {
            if (_instance == this)
                _instance = null;
        }
    }

    // Non-generic so RuntimeInitializeOnLoadMethod can reset it each play session
    internal static class SingletonState
    {
        public static bool IsQuitting { get; private set; }

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.SubsystemRegistration)]
        private static void Reset()
        {
            IsQuitting = false;
            Application.quitting -= OnQuitting;
            Application.quitting += OnQuitting;
        }

        private static void OnQuitting() => IsQuitting = true;
    }
}

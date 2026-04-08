using UnityEngine;
using UnityEngine.SceneManagement;

namespace FPS3D
{
    public class GameManager : MonoBehaviour
    {
        public static GameManager Instance { get; private set; }

        [SerializeField] private int _targetFrameRate = 60;

        private int _score;
        private bool _isPaused;

        public int Score => _score;
        public bool IsPaused => _isPaused;

        public System.Action<int> OnScoreChanged;
        public System.Action<bool> OnPauseChanged;

        private void Awake()
        {
            if (Instance != null && Instance != this)
            {
                Destroy(gameObject);
                return;
            }
            Instance = this;
            DontDestroyOnLoad(gameObject);
            Application.targetFrameRate = _targetFrameRate;
        }

        public void AddScore(int amount)
        {
            _score += amount;
            OnScoreChanged?.Invoke(_score);
        }

        public void TogglePause()
        {
            _isPaused = !_isPaused;
            Time.timeScale = _isPaused ? 0f : 1f;
            Cursor.lockState = _isPaused ? CursorLockMode.None : CursorLockMode.Locked;
            Cursor.visible = _isPaused;
            OnPauseChanged?.Invoke(_isPaused);
        }

        public void RestartLevel()
        {
            Time.timeScale = 1f;
            SceneManager.LoadScene(SceneManager.GetActiveScene().buildIndex);
        }
    }
}

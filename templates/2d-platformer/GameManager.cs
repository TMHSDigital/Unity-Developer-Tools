using UnityEngine;
using UnityEngine.SceneManagement;

namespace Platformer2D
{
    public class GameManager : MonoBehaviour
    {
        public static GameManager Instance { get; private set; }

        [Header("Game Settings")]
        [SerializeField] private int _startingLives = 3;

        private int _score;
        private int _lives;

        public int Score => _score;
        public int Lives => _lives;

        public System.Action<int> OnScoreChanged;
        public System.Action<int> OnLivesChanged;
        public System.Action OnGameOver;

        private void Awake()
        {
            if (Instance != null && Instance != this)
            {
                Destroy(gameObject);
                return;
            }
            Instance = this;
            DontDestroyOnLoad(gameObject);
            _lives = _startingLives;
        }

        public void AddScore(int amount)
        {
            _score += amount;
            OnScoreChanged?.Invoke(_score);
        }

        public void LoseLife()
        {
            _lives--;
            OnLivesChanged?.Invoke(_lives);

            if (_lives <= 0)
            {
                OnGameOver?.Invoke();
            }
            else
            {
                ReloadCurrentScene();
            }
        }

        public void ReloadCurrentScene()
        {
            SceneManager.LoadScene(SceneManager.GetActiveScene().buildIndex);
        }

        public void LoadScene(string sceneName)
        {
            SceneManager.LoadScene(sceneName);
        }
    }
}

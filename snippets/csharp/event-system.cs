// C# Event System
// Decouple game systems using C# events and delegates.
// Prefer this over SendMessage/BroadcastMessage.

using System;
using UnityEngine;

namespace MyGame
{
    public static class GameEvents
    {
        public static event Action<int> OnScoreChanged;
        public static event Action OnGameOver;
        public static event Action<Vector3> OnPlayerDied;
        public static event Action<string, int> OnItemCollected;

        public static void RaiseScoreChanged(int newScore)
            => OnScoreChanged?.Invoke(newScore);

        public static void RaiseGameOver()
            => OnGameOver?.Invoke();

        public static void RaisePlayerDied(Vector3 position)
            => OnPlayerDied?.Invoke(position);

        public static void RaiseItemCollected(string itemName, int quantity)
            => OnItemCollected?.Invoke(itemName, quantity);
    }

    // Example subscriber
    public class ScoreDisplay : MonoBehaviour
    {
        [SerializeField] private TMPro.TMP_Text _scoreText;

        private void OnEnable()
        {
            GameEvents.OnScoreChanged += UpdateScore;
        }

        private void OnDisable()
        {
            GameEvents.OnScoreChanged -= UpdateScore;
        }

        private void UpdateScore(int score)
        {
            _scoreText.SetText("Score: {0}", score);
        }
    }
}

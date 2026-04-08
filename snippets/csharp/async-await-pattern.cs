// Async/Await Pattern with Awaitable
// Modern async pattern for Unity 6+. Replaces coroutines for new code.
// CRITICAL: An Awaitable instance must never be awaited more than once.
// After the first await, the instance returns to the internal pool.

using UnityEngine;

namespace MyGame
{
    public class AsyncExample : MonoBehaviour
    {
        [SerializeField] private float _fadeTime = 1f;
        [SerializeField] private CanvasGroup _canvasGroup;

        // Basic delay
        private async void Start()
        {
            await Awaitable.WaitForSecondsAsync(2f);
            Debug.Log("Two seconds passed");
        }

        // Fade with cancellation support
        public async Awaitable FadeOutAsync()
        {
            float elapsed = 0f;
            while (elapsed < _fadeTime)
            {
                elapsed += Time.deltaTime;
                _canvasGroup.alpha = 1f - (elapsed / _fadeTime);
                await Awaitable.NextFrameAsync();
            }
            _canvasGroup.alpha = 0f;
        }

        // Cancellation via destroyCancellationToken
        public async Awaitable SpawnWavesAsync()
        {
            for (int wave = 0; wave < 5; wave++)
            {
                SpawnWave(wave);
                await Awaitable.WaitForSecondsAsync(3f, destroyCancellationToken);
            }
        }

        // Async scene loading
        public async Awaitable LoadSceneAsync(string sceneName)
        {
            var op = UnityEngine.SceneManagement.SceneManager.LoadSceneAsync(sceneName);
            await Awaitable.FromAsyncOperation(op);
        }

        // Wait for next fixed update (physics)
        public async Awaitable WaitForPhysicsAsync()
        {
            await Awaitable.FixedUpdateAsync();
        }

        // Wait for end of frame (screenshot, post-render)
        public async Awaitable CaptureScreenAsync()
        {
            await Awaitable.EndOfFrameAsync();
            ScreenCapture.CaptureScreenshot("screenshot.png");
        }

        private void SpawnWave(int waveNumber)
        {
            Debug.Log($"Spawning wave {waveNumber}");
        }
    }
}

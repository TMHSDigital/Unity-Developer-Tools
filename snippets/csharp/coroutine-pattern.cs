// Coroutine Pattern (Legacy Reference)
// Coroutines are still supported but Awaitable is preferred for new code.
// Use this pattern only when maintaining existing codebases.
// See async-await-pattern.cs for the modern approach.

using System.Collections;
using UnityEngine;

namespace MyGame
{
    public class CoroutineExample : MonoBehaviour
    {
        [SerializeField] private float _spawnInterval = 1f;
        [SerializeField] private int _waveSize = 5;

        private Coroutine _spawnCoroutine;

        public void StartSpawning()
        {
            if (_spawnCoroutine != null)
                StopCoroutine(_spawnCoroutine);

            _spawnCoroutine = StartCoroutine(SpawnWaveRoutine());
        }

        public void StopSpawning()
        {
            if (_spawnCoroutine != null)
            {
                StopCoroutine(_spawnCoroutine);
                _spawnCoroutine = null;
            }
        }

        private IEnumerator SpawnWaveRoutine()
        {
            for (int i = 0; i < _waveSize; i++)
            {
                SpawnEnemy();
                yield return new WaitForSeconds(_spawnInterval);
            }

            yield return new WaitForSeconds(3f);
            StartCoroutine(SpawnWaveRoutine());
        }

        private void SpawnEnemy()
        {
            Debug.Log("Enemy spawned");
        }
    }
}

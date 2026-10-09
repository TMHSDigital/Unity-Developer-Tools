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

        // Loop inside one coroutine so _spawnCoroutine always refers to the running routine.
        // Starting a new coroutine per wave would leave StopSpawning() holding a stale handle.
        private IEnumerator SpawnWaveRoutine()
        {
            var spawnDelay = new WaitForSeconds(_spawnInterval);
            var waveDelay = new WaitForSeconds(3f);

            while (true)
            {
                for (int i = 0; i < _waveSize; i++)
                {
                    SpawnEnemy();
                    yield return spawnDelay;
                }

                yield return waveDelay;
            }
        }

        private void SpawnEnemy()
        {
            Debug.Log("Enemy spawned");
        }
    }
}

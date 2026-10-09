using UnityEngine;
using UnityEngine.Events;

namespace SOArchitecture
{
    public class GameEventListener : MonoBehaviour
    {
        [SerializeField] private GameEvent _event;
        [SerializeField] private UnityEvent _response;

        private void OnEnable()
        {
            if (_event == null)
            {
                Debug.LogWarning($"{name}: GameEventListener has no GameEvent assigned.", this);
                return;
            }
            _event.RegisterListener(this);
        }

        private void OnDisable()
        {
            if (_event != null)
                _event.UnregisterListener(this);
        }

        public void OnEventRaised() => _response.Invoke();
    }
}

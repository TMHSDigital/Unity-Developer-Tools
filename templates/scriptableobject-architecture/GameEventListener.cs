using UnityEngine;
using UnityEngine.Events;

namespace SOArchitecture
{
    public class GameEventListener : MonoBehaviour
    {
        [SerializeField] private GameEvent _event;
        [SerializeField] private UnityEvent _response;

        private void OnEnable() => _event.RegisterListener(this);
        private void OnDisable() => _event.UnregisterListener(this);

        public void OnEventRaised() => _response.Invoke();
    }
}

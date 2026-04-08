using System.Collections.Generic;
using UnityEngine;

namespace SOArchitecture
{
    [CreateAssetMenu(fileName = "New Game Event", menuName = "Events/Game Event")]
    public class GameEvent : ScriptableObject
    {
        private readonly List<GameEventListener> _listeners = new();

        public void Raise()
        {
            for (int i = _listeners.Count - 1; i >= 0; i--)
            {
                _listeners[i].OnEventRaised();
            }
        }

        public void RegisterListener(GameEventListener listener)
        {
            if (!_listeners.Contains(listener))
                _listeners.Add(listener);
        }

        public void UnregisterListener(GameEventListener listener)
        {
            _listeners.Remove(listener);
        }
    }
}

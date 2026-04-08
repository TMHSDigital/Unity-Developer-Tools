using System.Collections.Generic;
using UnityEngine;

namespace SOArchitecture
{
    public abstract class RuntimeSet<T> : ScriptableObject
    {
        private readonly List<T> _items = new();

        public IReadOnlyList<T> Items => _items;
        public int Count => _items.Count;

        public void Add(T item)
        {
            if (!_items.Contains(item))
                _items.Add(item);
        }

        public void Remove(T item)
        {
            _items.Remove(item);
        }

        private void OnDisable()
        {
            _items.Clear();
        }
    }
}

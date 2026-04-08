// ScriptableObject Template
// Data container that lives as a project asset.
// Use for shared config: weapon stats, enemy profiles, level settings.

using UnityEngine;

namespace MyGame
{
    [CreateAssetMenu(fileName = "New Item Data", menuName = "Game/Item Data")]
    public class ItemData : ScriptableObject
    {
        [Header("Basic Info")]
        [SerializeField] private string _itemName;
        [SerializeField] [TextArea(2, 5)] private string _description;
        [SerializeField] private Sprite _icon;

        [Header("Stats")]
        [SerializeField] [Range(0, 100)] private int _value;
        [SerializeField] private float _weight;
        [SerializeField] private ItemType _type;

        public string ItemName => _itemName;
        public string Description => _description;
        public Sprite Icon => _icon;
        public int Value => _value;
        public float Weight => _weight;
        public ItemType Type => _type;

        public enum ItemType
        {
            Weapon,
            Armor,
            Consumable,
            Material,
            Quest
        }

        private void OnValidate()
        {
            if (string.IsNullOrEmpty(_itemName))
                _itemName = name;
        }
    }
}

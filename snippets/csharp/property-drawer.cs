// Custom Property Drawer
// Custom rendering for a serializable type in the inspector.
// Place in an Editor/ folder.

using System;
using UnityEditor;
using UnityEngine;
using UnityEngine.UIElements;

namespace MyGame
{
    [Serializable]
    public struct MinMaxRange
    {
        public float Min;
        public float Max;

        public MinMaxRange(float min, float max)
        {
            Min = min;
            Max = max;
        }

        public float RandomValue => UnityEngine.Random.Range(Min, Max);
    }
}

namespace MyGame.Editor
{
    [CustomPropertyDrawer(typeof(MinMaxRange))]
    public class MinMaxRangeDrawer : PropertyDrawer
    {
        public override VisualElement CreatePropertyGUI(SerializedProperty property)
        {
            var container = new VisualElement();
            container.style.flexDirection = FlexDirection.Row;

            var label = new Label(property.displayName);
            label.style.width = 120;
            container.Add(label);

            var minField = new FloatField("Min")
            {
                bindingPath = property.FindPropertyRelative("Min").propertyPath,
                style = { flexGrow = 1 }
            };
            container.Add(minField);

            var maxField = new FloatField("Max")
            {
                bindingPath = property.FindPropertyRelative("Max").propertyPath,
                style = { flexGrow = 1 }
            };
            container.Add(maxField);

            return container;
        }
    }
}

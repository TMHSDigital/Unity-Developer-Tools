// Custom Property Drawer
// Custom rendering for a serializable type in the inspector.
// Keep this file in a runtime folder (not Editor/) so game code can use MinMaxRange.
// The drawer is wrapped in UNITY_EDITOR so it is stripped from player builds.
// For larger projects, move the drawer into its own file under an Editor/ folder instead.

using System;
using UnityEngine;
#if UNITY_EDITOR
using UnityEditor;
using UnityEngine.UIElements;
#endif

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

#if UNITY_EDITOR
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
                bindingPath = property.FindPropertyRelative(nameof(MinMaxRange.Min)).propertyPath,
                style = { flexGrow = 1 }
            };
            container.Add(minField);

            var maxField = new FloatField("Max")
            {
                bindingPath = property.FindPropertyRelative(nameof(MinMaxRange.Max)).propertyPath,
                style = { flexGrow = 1 }
            };
            container.Add(maxField);

            return container;
        }
    }
}
#endif

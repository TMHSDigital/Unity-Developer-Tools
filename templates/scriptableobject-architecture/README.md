# ScriptableObject Architecture Template

A data-driven architecture using ScriptableObjects for events, variables, and runtime sets. Based on Ryan Hipple's GDC 2017 talk.

## Scripts

- **GameEvent.cs** - ScriptableObject event channel
- **GameEventListener.cs** - MonoBehaviour that subscribes to GameEvent
- **FloatVariable.cs** - Shared float variable as ScriptableObject
- **RuntimeSet.cs** - Generic runtime set for tracking active entities

## Usage

1. Create GameEvent assets (right-click > Events > Game Event)
2. Create FloatVariable assets (right-click > Variables > Float)
3. Add GameEventListener to GameObjects that respond to events
4. Wire up UnityEvents in the inspector

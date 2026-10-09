# ScriptableObject Architecture Template

A data-driven architecture using ScriptableObjects for events, variables, and runtime sets. Based on Ryan Hipple's GDC 2017 talk.

## Scripts

- **GameEvent.cs** - ScriptableObject event channel
- **GameEventListener.cs** - MonoBehaviour that subscribes to a GameEvent and invokes a UnityEvent
- **FloatVariable.cs** - Shared float variable; the runtime value resets to the initial value each time you enter Play Mode
- **RuntimeSet.cs** - Generic base class for tracking active objects
- **TransformRuntimeSet.cs** - Concrete runtime set of Transforms (create as an asset)
- **RuntimeSetMember.cs** - Adds its GameObject to a TransformRuntimeSet while enabled

## Requirements

- Unity 6, no extra packages. Works with Enter Play Mode Options (domain reload disabled).

## Usage

**Events**
1. Create a GameEvent asset (**Create > Events > Game Event**).
2. Add **GameEventListener** to a GameObject, assign the event, and add responses to its UnityEvent.
3. Call `Raise()` on the event from code or from another UnityEvent.

**Variables**
1. Create a FloatVariable asset (**Create > Variables > Float**) and set its initial value.
2. Reference the asset from any script and read or change `RuntimeValue`.

**Runtime sets**
1. Create a TransformRuntimeSet asset (**Create > Runtime Sets > Transform Set**), for example `Enemies`.
2. Add **RuntimeSetMember** to each enemy prefab and assign the set.
3. Any system can reference the same asset and iterate `Items` to find every active enemy.

To track a different type, add a subclass such as `public class EnemyRuntimeSet : RuntimeSet<Enemy> { }` with its own `[CreateAssetMenu]`.

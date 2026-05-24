---
title: MonoBehaviour Patterns
description: Comprehensive guide to MonoBehaviour lifecycle, async patterns with Awaitable, and common Unity design patterns.
globs: ["**/*.cs"]
standards-version: 1.10.0
---

# MonoBehaviour Patterns

## Lifecycle Execution Order

Unity calls MonoBehaviour methods in a strict order each frame:

1. **Awake** - Called once when the script instance loads. Use for self-initialization: cache own components, set default values. Called even if the component is disabled.
2. **OnEnable** - Called when the component becomes active. Subscribe to events here.
3. **Start** - Called once before the first Update, only if the component is enabled. Use for cross-object initialization: find other objects, resolve dependencies.
4. **FixedUpdate** - Called on a fixed timestep (default 50Hz). Use exclusively for physics: apply forces, set velocities, move Rigidbodies.
5. **Update** - Called once per frame. Use for input polling, non-physics movement, game logic.
6. **LateUpdate** - Called after all Update calls complete. Use for camera follow, UI updates that depend on object positions.
7. **OnDisable** - Called when the component is deactivated. Unsubscribe from events here.
8. **OnDestroy** - Called when the GameObject is destroyed or the scene unloads. Final cleanup: unsubscribe from static events, release native resources.

### Critical Rules

- NEVER put physics code (forces, velocity) in Update. Use FixedUpdate.
- NEVER put frame-dependent logic (input, animation) in FixedUpdate.
- NEVER reference other GameObjects in Awake. They may not exist yet. Use Start.
- NEVER call GetComponent in Update/FixedUpdate/LateUpdate. Cache in Awake.

## Async Patterns with Awaitable

Unity 6 introduced the `Awaitable` class as the modern replacement for coroutines. Awaitable instances are pooled by the engine, producing near-zero garbage collection pressure.

### Critical Rule: Single Await Only

An Awaitable instance must NEVER be awaited more than once. After the first await completes, the instance returns to the internal pool. A second await will cause undefined behavior.

```csharp
// CORRECT: each call produces a fresh Awaitable
await Awaitable.NextFrameAsync();
await Awaitable.WaitForSecondsAsync(2f);

// WRONG: reusing an Awaitable reference
var wait = Awaitable.NextFrameAsync();
await wait;
await wait; // undefined behavior - instance already returned to pool
```

### Common Awaitable Methods

| Method | Replaces |
|--------|----------|
| `Awaitable.NextFrameAsync()` | `yield return null` |
| `Awaitable.WaitForSecondsAsync(float)` | `yield return new WaitForSeconds(float)` |
| `Awaitable.EndOfFrameAsync()` | `yield return new WaitForEndOfFrame()` |
| `Awaitable.FixedUpdateAsync()` | `yield return new WaitForFixedUpdate()` |
| `Awaitable.FromAsyncOperation(op)` | `yield return asyncOperation` |

### Example: Async Game Loop

```csharp
private async void Start()
{
    await SpawnWaveAsync();
    await Awaitable.WaitForSecondsAsync(3f);
    await SpawnWaveAsync();
}

private async Awaitable SpawnWaveAsync()
{
    for (int i = 0; i < 5; i++)
    {
        SpawnEnemy();
        await Awaitable.WaitForSecondsAsync(0.5f);
    }
}
```

### Cancellation with destroyCancellationToken

Every MonoBehaviour has a `destroyCancellationToken` that triggers when the object is destroyed:

```csharp
private async void Start()
{
    try
    {
        await Awaitable.WaitForSecondsAsync(10f, destroyCancellationToken);
    }
    catch (OperationCanceledException)
    {
        // Object was destroyed before the wait completed
    }
}
```

## Legacy Coroutines

Coroutines are still supported but are considered legacy for new code. Use them only when maintaining existing codebases.

```csharp
private IEnumerator LegacySpawnWave()
{
    for (int i = 0; i < 5; i++)
    {
        SpawnEnemy();
        yield return new WaitForSeconds(0.5f);
    }
}
```

## Common Design Patterns

### Singleton

Use for managers that need exactly one instance (AudioManager, GameManager). See `snippets/csharp/singleton-pattern.cs`.

### Component Caching

```csharp
private Rigidbody _rb;
private Collider _col;

private void Awake()
{
    _rb = GetComponent<Rigidbody>();
    _col = GetComponent<Collider>();
}
```

### Tag Comparison

Always use `CompareTag` instead of string equality:

```csharp
// CORRECT
if (other.CompareTag("Player")) { }

// WRONG - allocates a string
if (other.gameObject.tag == "Player") { }
```

### TryGetComponent

Use when the component might not exist:

```csharp
if (TryGetComponent<IDamageable>(out var damageable))
{
    damageable.TakeDamage(10);
}
```

### RequireComponent

Enforce component dependencies at the class level:

```csharp
[RequireComponent(typeof(Rigidbody))]
public class PlayerMovement : MonoBehaviour
{
    // Rigidbody is guaranteed to exist
}
```

### Null Checks for Unity Objects

Use the implicit bool operator, not C# null checks:

```csharp
// CORRECT - uses Unity's lifetime check
if (myObject) { }

// AVOID - bypasses Unity's destroyed-object tracking
if (myObject != null) { }
```

### FindFirstObjectByType (Not FindObjectOfType)

`FindObjectOfType` is deprecated. Use the modern replacement:

```csharp
// CORRECT
var player = FindFirstObjectByType<PlayerController>();

// DEPRECATED
var player = FindObjectOfType<PlayerController>();
```

For finding multiple objects, use `FindObjectsByType<T>(FindObjectsSortMode)`.

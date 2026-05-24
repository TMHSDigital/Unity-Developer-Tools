---
title: ScriptableObject Architecture
description: Data-driven design patterns using ScriptableObjects for events, variables, runtime sets, and configuration.
globs: ["**/*.cs", "**/*.asset"]
standards-version: 1.10.0
---

# ScriptableObject Architecture

## What Are ScriptableObjects

ScriptableObjects are data containers that live as project assets, not on GameObjects. They persist between play sessions in the editor and are ideal for:

- Shared configuration data (weapon stats, enemy profiles, level settings)
- Event channels that decouple systems
- Variable containers that multiple objects can read/write
- Runtime sets for tracking active game entities

## Creating Custom ScriptableObjects

Use the `[CreateAssetMenu]` attribute to make them easy to create in the Project window:

```csharp
[CreateAssetMenu(fileName = "New Weapon Data", menuName = "Game/Weapon Data")]
public class WeaponData : ScriptableObject
{
    [SerializeField] private string _weaponName;
    [SerializeField] private int _damage;
    [SerializeField] private float _fireRate;
    [SerializeField] private AudioClip _fireSound;
    [SerializeField] private GameObject _projectilePrefab;

    public string WeaponName => _weaponName;
    public int Damage => _damage;
    public float FireRate => _fireRate;
    public AudioClip FireSound => _fireSound;
    public GameObject ProjectilePrefab => _projectilePrefab;
}
```

## ScriptableObject Event System

Based on Ryan Hipple's GDC 2017 architecture. This pattern completely decouples event senders from receivers.

### GameEvent (the channel)

```csharp
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

    public void RegisterListener(GameEventListener listener) => _listeners.Add(listener);
    public void UnregisterListener(GameEventListener listener) => _listeners.Remove(listener);
}
```

### GameEventListener (the subscriber)

```csharp
public class GameEventListener : MonoBehaviour
{
    [SerializeField] private GameEvent _event;
    [SerializeField] private UnityEvent _response;

    private void OnEnable() => _event.RegisterListener(this);
    private void OnDisable() => _event.UnregisterListener(this);

    public void OnEventRaised() => _response.Invoke();
}
```

## Variable Types as ScriptableObjects

Shared variables that any system can read or write without direct references:

```csharp
[CreateAssetMenu(fileName = "New Float Variable", menuName = "Variables/Float")]
public class FloatVariable : ScriptableObject
{
    [SerializeField] private float _initialValue;
    [System.NonSerialized] public float RuntimeValue;

    private void OnEnable()
    {
        RuntimeValue = _initialValue;
    }
}
```

Usage: a health bar reads `PlayerHealth.RuntimeValue`, while the player controller writes to it. Neither knows the other exists.

## Runtime Sets

Track all active instances of a type without using FindObjectsByType:

```csharp
public abstract class RuntimeSet<T> : ScriptableObject
{
    private readonly List<T> _items = new();
    public IReadOnlyList<T> Items => _items;

    public void Add(T item)
    {
        if (!_items.Contains(item))
            _items.Add(item);
    }

    public void Remove(T item) => _items.Remove(item);
}
```

Concrete implementation:

```csharp
[CreateAssetMenu(fileName = "New Enemy Set", menuName = "Runtime Sets/Enemy Set")]
public class EnemyRuntimeSet : RuntimeSet<EnemyController> { }
```

Enemies register in OnEnable and unregister in OnDisable.

## ScriptableObject Lifecycle

- **OnEnable**: Called when the asset loads or when entering play mode. Reset runtime state here.
- **OnDisable**: Called when the asset unloads or when exiting play mode.
- **OnValidate**: Called in the editor when a value changes in the inspector. Use for validation and auto-calculation.

## When NOT to Use ScriptableObjects

- Per-instance mutable state that needs saving (use serialization instead)
- Data that changes every frame per entity (use components)
- Anything that needs to survive a build without being referenced (use Addressables)

ScriptableObject data persists in the editor between play sessions. This is useful for debugging but means runtime writes to SO fields will "stick" in the editor. Always reset runtime values in OnEnable.

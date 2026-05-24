---
title: Performance Optimization
description: Unity-specific performance best practices for CPU, GPU, memory, and profiling tools.
globs: ["**/*.cs"]
standards-version: 1.10.0
---

# Performance Optimization

## CPU Optimization

### Cache Component References

Never call GetComponent in Update loops. Cache in Awake:

```csharp
// GOOD
private Rigidbody _rb;
private void Awake() => _rb = GetComponent<Rigidbody>();

// BAD - allocates and searches every frame
private void Update()
{
    GetComponent<Rigidbody>().AddForce(Vector3.up);
}
```

### Avoid Find Methods at Runtime

`FindFirstObjectByType`, `FindObjectsByType`, and `GameObject.Find` are expensive. Use them only during initialization, never in Update.

Prefer:
- Direct serialized references
- Events and callbacks
- Runtime sets (ScriptableObject pattern)
- Dependency injection

### String Operations

```csharp
// BAD - allocates garbage every frame
_text.text = "Score: " + score.ToString();

// GOOD - zero allocation with TMP
_tmpText.SetText("Score: {0}", score);

// GOOD - StringBuilder for complex strings
private readonly StringBuilder _sb = new(64);
private void UpdateUI()
{
    _sb.Clear();
    _sb.Append("HP: ").Append(_health).Append('/').Append(_maxHealth);
    _text.text = _sb.ToString();
}
```

### Avoid Allocations in Hot Paths

These allocate on the heap and trigger GC:

| Allocation Source | Alternative |
|-------------------|-------------|
| `new List<T>()` in Update | Pre-allocate, reuse |
| LINQ (Where, Select) | Manual for/foreach loops |
| `string + string` | StringBuilder or TMP.SetText |
| `foreach` on non-generic IEnumerable | Use `for` with index |
| `params` arrays | Use explicit overloads |
| Boxing (int to object) | Use generics |
| Closures / lambdas capturing locals | Cache delegates |

### Physics - NonAlloc Variants

```csharp
// BAD - allocates array every call
RaycastHit[] hits = Physics.RaycastAll(origin, direction, maxDist);

// GOOD - reuse pre-allocated buffer
private readonly RaycastHit[] _hitBuffer = new RaycastHit[16];
int count = Physics.RaycastNonAlloc(origin, direction, _hitBuffer, maxDist);
```

Also: `OverlapSphereNonAlloc`, `OverlapBoxNonAlloc`, `SphereCastNonAlloc`, `BoxCastNonAlloc`.

### Object Pooling

Replace Instantiate/Destroy patterns with object pools:

```csharp
// Use Unity's built-in ObjectPool<T> (Unity 2021+)
private ObjectPool<GameObject> _pool;

private void Awake()
{
    _pool = new ObjectPool<GameObject>(
        createFunc: () => Instantiate(_prefab),
        actionOnGet: obj => obj.SetActive(true),
        actionOnRelease: obj => obj.SetActive(false),
        actionOnDestroy: obj => Destroy(obj),
        maxSize: 50
    );
}
```

### Cache Camera.main

`Camera.main` calls `FindGameObjectWithTag("MainCamera")` internally:

```csharp
// BAD
void Update() { Camera.main.ScreenToWorldPoint(...); }

// GOOD
private Camera _mainCam;
void Awake() => _mainCam = Camera.main;
```

### Burst Compiler and Jobs

For CPU-intensive work, use the Jobs system with Burst:

```csharp
[BurstCompile]
public struct CalculateDistancesJob : IJobParallelFor
{
    [ReadOnly] public NativeArray<float3> Positions;
    public NativeArray<float> Distances;
    public float3 Target;

    public void Execute(int index)
    {
        Distances[index] = math.distance(Positions[index], Target);
    }
}
```

## GPU Optimization

### Draw Call Batching

- **Static Batching**: Mark non-moving objects as Static. Unity combines their meshes at build time.
- **Dynamic Batching**: Automatic for small meshes (< 300 vertices). Limited usefulness.
- **GPU Instancing**: Enable on materials for many identical objects (trees, grass, debris).
- **SRP Batcher**: Enabled by default in URP. Requires shaders with CBUFFER-wrapped properties.

### Render Graph (Unity 6)

The Render Graph backend in URP/HDRP optimizes rendering passes automatically:
- Eliminates redundant render target switches
- Reduces memory bandwidth
- Use Render Graph custom passes instead of extra cameras

### Occlusion Culling

Bake occlusion data so Unity skips rendering objects hidden behind walls. Set up in Window > Rendering > Occlusion Culling.

### LOD Groups

Reduce polygon count for distant objects:
- LOD0: Full detail (close)
- LOD1: Medium detail (mid-range)
- LOD2: Low detail (far)
- Culled: Not rendered (very far)

### Shader Complexity

- Minimize shader variants with `shader_feature_local`
- Use half precision on mobile
- Avoid complex math in fragment shaders when possible
- Use shader stripping to remove unused variants from builds

## Memory Optimization

- Compress textures per platform (ASTC for mobile, BC7 for desktop)
- Use Sprite Atlases for 2D to reduce draw calls
- Use Addressables for on-demand loading instead of preloading everything
- Call `Resources.UnloadUnusedAssets()` after major scene transitions
- Use Addressables.Release(handle) to free loaded assets

## Profiling Tools

- **Profiler Window** (Window > Analysis > Profiler): CPU, GPU, memory, rendering, audio, physics
- **Frame Debugger** (Window > Analysis > Frame Debugger): Step through draw calls one at a time
- **Memory Profiler**: Detailed memory snapshots and comparison
- **Profile Analyzer**: Compare profiler captures for regression testing

## Mobile-Specific

- Target 30fps for battery-friendly games, 60fps for action games
- Reduce fill rate: minimize overdraw, use simpler shaders
- Compress textures to ASTC (Android/iOS)
- Disable real-time shadows on low-end devices
- Use Adaptive Performance providers for automatic quality scaling

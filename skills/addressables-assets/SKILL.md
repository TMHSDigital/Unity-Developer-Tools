---
title: Addressables and Asset Management
description: Managing assets with the Addressables system for async loading, memory management, and remote content delivery.
globs: ["**/*.cs", "**/*.asset"]
standards-version: 1.10.0
---

# Addressables and Asset Management

## Why Addressables

The Addressables system (com.unity.addressables 2.x) is the recommended approach for all scalable Unity projects. It replaces both the Resources folder and manual Asset Bundles.

Benefits:
- Asynchronous loading (non-blocking)
- Automatic dependency management
- Memory tracking with reference counting
- Remote content delivery for DLC and updates
- Build-time analysis for size optimization

## Setup

1. Install via Package Manager: `com.unity.addressables`
2. Mark assets as Addressable in the inspector
3. Organize into Groups (local, remote, per-scene)
4. Build Addressables before building the player

## Loading Assets

### Async Loading (Always Use This)

```csharp
using UnityEngine.AddressableAssets;
using UnityEngine.ResourceManagement.AsyncOperations;

private AsyncOperationHandle<GameObject> _handle;

private async Awaitable LoadPrefabAsync()
{
    _handle = Addressables.LoadAssetAsync<GameObject>("Enemies/Goblin");
    await _handle.Task;

    if (_handle.Status == AsyncOperationStatus.Succeeded)
    {
        Instantiate(_handle.Result);
    }
}
```

### Instantiation

```csharp
private AsyncOperationHandle<GameObject> _instanceHandle;

private async Awaitable SpawnEnemyAsync()
{
    _instanceHandle = Addressables.InstantiateAsync("Enemies/Goblin", spawnPoint.position, Quaternion.identity);
    await _instanceHandle.Task;
}
```

### Loading by Label

```csharp
private async Awaitable LoadAllWeaponsAsync()
{
    var handle = Addressables.LoadAssetsAsync<WeaponData>("weapons", weapon =>
    {
        _weaponList.Add(weapon);
    });
    await handle.Task;
}
```

## Releasing Assets - CRITICAL

Every loaded asset must be released to prevent memory leaks:

```csharp
// Release a loaded asset
Addressables.Release(_handle);

// Release an instantiated object
Addressables.ReleaseInstance(spawnedObject);

// In OnDestroy
private void OnDestroy()
{
    if (_handle.IsValid())
    {
        Addressables.Release(_handle);
    }
}
```

Failure to release handles is the most common Addressables bug. Every `LoadAssetAsync` needs a matching `Release`. Every `InstantiateAsync` needs a matching `ReleaseInstance`.

## Groups and Labels

### Groups

Organize assets by loading pattern:
- **Local Static**: Always included in the build (core gameplay assets)
- **Local Dynamic**: Included but loaded on demand (level-specific assets)
- **Remote**: Downloaded at runtime (DLC, seasonal content)

### Labels

Tag assets for batch operations:
- "weapons" - all weapon ScriptableObjects
- "level-1" - all assets for level 1
- "audio-sfx" - all sound effect clips

## ContiguousBundles

Enable in Addressables settings for 10% to 50% faster loading of complex assets like large UI prefabs. This optimizes the physical layout of assets within bundles.

## Build and Deploy

### Build Steps

1. Open Window > Asset Management > Addressables > Groups
2. Click "Build > New Build > Default Build Script"
3. Then build the player normally

### Remote Content

1. Configure a Remote Load Path (CDN URL)
2. Assign assets to a remote group
3. Build Addressables
4. Upload the remote catalog and bundles to your CDN
5. The game downloads assets on demand at runtime

### Catalog Updates

```csharp
private async Awaitable CheckForUpdatesAsync()
{
    var checkHandle = Addressables.CheckForCatalogUpdates();
    await checkHandle.Task;

    if (checkHandle.Result.Count > 0)
    {
        var updateHandle = Addressables.UpdateCatalogs(checkHandle.Result);
        await updateHandle.Task;
    }

    Addressables.Release(checkHandle);
}
```

## Migration from Resources

Move assets out of the Resources folder:

1. Mark the asset as Addressable (checkbox in inspector)
2. Replace `Resources.Load<T>("path")` with `Addressables.LoadAssetAsync<T>("key")`
3. Add release logic in OnDestroy or when the asset is no longer needed
4. Remove the asset from the Resources folder

The Resources folder is legacy. It loads everything synchronously, cannot unload individual assets cleanly, and bloats the initial build size.

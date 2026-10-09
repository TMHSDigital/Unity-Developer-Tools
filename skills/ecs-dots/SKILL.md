---
title: ECS and DOTS
description: Entity Component System development with Unity Entities, Jobs, and Burst for high-performance simulation.
globs: ["**/*.cs"]
standards-version: 1.10.0
---

# ECS and DOTS

## Status in 2026

The Data-Oriented Technology Stack (DOTS) is now a core part of the Unity engine, not an experimental package. As of Unity 6.4, the Entities package (1.4/1.7) is integrated into the core engine packages. ECS is production-ready for:

- Massive entity counts (thousands to millions)
- High-performance simulations and physics
- Large-scale multiplayer (Netcode for Entities)
- Procedural world generation

## Core Concepts

### Entity

A lightweight identifier (integer) that represents a game object in ECS. Entities have no behavior or data themselves - they are just IDs that components are attached to.

### IComponentData

Data containers with no behavior. Must be structs:

```csharp
public struct MoveSpeed : IComponentData
{
    public float Value;
}

public struct Health : IComponentData
{
    public int Current;
    public int Max;
}
```

### Systems

Logic that processes entities with specific component combinations.

#### ISystem (Unmanaged - Preferred)

```csharp
[BurstCompile]
public partial struct MoveSystem : ISystem
{
    [BurstCompile]
    public void OnUpdate(ref SystemState state)
    {
        float dt = SystemAPI.Time.DeltaTime;

        foreach (var (transform, speed) in
            SystemAPI.Query<RefRW<LocalTransform>, RefRO<MoveSpeed>>())
        {
            transform.ValueRW.Position += new float3(0, 0, speed.ValueRO.Value * dt);
        }
    }
}
```

#### SystemAPI.Query (Main Thread)

Use for simple iteration on the main thread. Structural changes (creating or destroying entities, adding or removing components) are not allowed while a query is being iterated, so record them in an `EntityCommandBuffer` and let a command buffer system play them back:

```csharp
[BurstCompile]
public partial struct DeathSystem : ISystem
{
    public void OnCreate(ref SystemState state)
    {
        state.RequireForUpdate<EndSimulationEntityCommandBufferSystem.Singleton>();
    }

    [BurstCompile]
    public void OnUpdate(ref SystemState state)
    {
        var ecb = SystemAPI.GetSingleton<EndSimulationEntityCommandBufferSystem.Singleton>()
            .CreateCommandBuffer(state.WorldUnmanaged);

        foreach (var (health, entity) in SystemAPI.Query<RefRO<Health>>().WithEntityAccess())
        {
            if (health.ValueRO.Current <= 0)
            {
                ecb.DestroyEntity(entity);
            }
        }
    }
}
```

#### IJobEntity (Parallel - High Performance)

Use for parallel processing across multiple threads:

```csharp
[BurstCompile]
public partial struct DamageJob : IJobEntity
{
    public int DamageAmount;

    public void Execute(ref Health health)
    {
        health.Current -= DamageAmount;
    }
}

// Schedule in system:
new DamageJob { DamageAmount = 10 }.ScheduleParallel();
```

## Deprecated ECS Patterns

Entities 1.3 marked these obsolete; they still work in 1.x but will be removed in a future major release:

| Deprecated | Replacement |
|-----------|-------------|
| `Entities.ForEach` | `SystemAPI.Query` or `IJobEntity` |
| `IAspect` | Components, `ComponentLookup`, and `EntityQuery` directly |

`SystemBase` is not deprecated. Prefer `ISystem` for new code because it is unmanaged and can be Burst-compiled end to end; use `SystemBase` when a system needs managed data (managed components, class references, or main-thread UnityEngine APIs).

## Jobs System

The C# Job System provides safe multithreaded code:

```csharp
[BurstCompile]
public struct DistanceCalculationJob : IJobParallelFor
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

Use `NativeArray<T>`, `NativeList<T>`, `NativeHashMap<K,V>` for job-safe collections.

## Burst Compiler

Burst compiles C# Jobs into highly optimized native code:

- 10x to 100x performance improvement over standard C#
- SIMD vectorization automatic
- Add `[BurstCompile]` to jobs and ISystem structs
- Restrictions: no managed types, no reference types, no try/catch

Use `Unity.Mathematics` types (`float3`, `quaternion`, `math.*`) for best Burst optimization.

## Baking (Authoring to Runtime)

Convert GameObjects to entities at build time:

```csharp
public class MoveSpeedAuthoring : MonoBehaviour
{
    public float Speed;

    public class Baker : Baker<MoveSpeedAuthoring>
    {
        public override void Bake(MoveSpeedAuthoring authoring)
        {
            var entity = GetEntity(TransformUsageFlags.Dynamic);
            AddComponent(entity, new MoveSpeed { Value = authoring.Speed });
        }
    }
}
```

## Hybrid Approach

Mix ECS with GameObjects for incremental adoption:

- Use ECS for simulation-heavy systems (AI, pathfinding, particles)
- Keep GameObjects for UI, cameras, and player controllers
- Hierarchy V2 (Unity 6.5 opt-in) allows viewing GameObjects and Entities in the same window

## When to Use ECS

- Thousands of similar entities that need processing
- CPU-bound simulations (flocking, pathfinding, ballistics)
- Large-scale multiplayer with Netcode for Entities
- Procedural generation and world streaming

## When NOT to Use ECS

- Small games with fewer than 100 active entities
- UI-heavy applications
- Rapid prototypes where iteration speed matters more than performance
- Teams unfamiliar with data-oriented programming (learning curve is steep)

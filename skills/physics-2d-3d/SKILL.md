---
title: Physics Systems (2D and 3D)
description: Physics programming for both 2D and 3D Unity projects including collision, raycasting, layers, and rigidbody management.
globs: ["**/*.cs"]
standards-version: 1.10.0
---

# Physics Systems (2D and 3D)

## Component Equivalents

| 3D | 2D |
|----|-----|
| Rigidbody | Rigidbody2D |
| Collider (Box, Sphere, Capsule, Mesh) | Collider2D (Box, Circle, Capsule, Polygon, Composite) |
| OnCollisionEnter/Stay/Exit | OnCollisionEnter2D/Stay2D/Exit2D |
| OnTriggerEnter/Stay/Exit | OnTriggerEnter2D/Stay2D/Exit2D |
| Physics.Raycast | Physics2D.Raycast |
| PhysicsMaterial | PhysicsMaterial2D |

## Rigidbody Types

- **Dynamic**: Fully simulated. Responds to forces, gravity, and collisions. Use for players, projectiles, physics objects.
- **Kinematic**: Not affected by forces or gravity. Moves only via script (`MovePosition`, `MoveRotation`). Use for platforms, doors, elevators.
- **Static**: Does not move at all. Use for walls, floors, terrain colliders. A Collider without a Rigidbody is implicitly static.

## Collision Detection

### Collision Callbacks (require both objects to have colliders, at least one with Rigidbody)

```csharp
private void OnCollisionEnter(Collision collision)
{
    if (collision.gameObject.CompareTag("Ground"))
    {
        _isGrounded = true;
    }
}
```

### Trigger Callbacks (one collider must have "Is Trigger" enabled)

```csharp
private void OnTriggerEnter(Collider other)
{
    if (other.TryGetComponent<ICollectible>(out var collectible))
    {
        collectible.Collect();
    }
}
```

## Raycasting

### Basic Raycast

```csharp
if (Physics.Raycast(transform.position, transform.forward, out RaycastHit hit, 100f))
{
    Debug.Log($"Hit: {hit.collider.name} at {hit.point}");
}
```

### NonAlloc Raycasting (zero-allocation)

Pre-allocate a results buffer and reuse it every frame:

```csharp
private readonly RaycastHit[] _raycastResults = new RaycastHit[10];

private void FixedUpdate()
{
    int count = Physics.RaycastNonAlloc(
        transform.position, transform.forward,
        _raycastResults, 100f
    );

    for (int i = 0; i < count; i++)
    {
        ProcessHit(_raycastResults[i]);
    }
}
```

Other NonAlloc variants: `Physics.SphereCastNonAlloc`, `Physics.BoxCastNonAlloc`, `Physics.OverlapSphereNonAlloc`, `Physics.OverlapBoxNonAlloc`.

### LayerMask Filtering

```csharp
[SerializeField] private LayerMask _groundLayer;

private bool CheckGround()
{
    return Physics.Raycast(transform.position, Vector3.down, 1.1f, _groundLayer);
}
```

## Physics Rules

- ALWAYS use FixedUpdate for physics code (forces, velocity, MovePosition)
- NEVER move a Rigidbody with `transform.position` directly; use `Rigidbody.MovePosition` or apply forces
- NEVER scale physics objects non-uniformly; it causes unstable collision behavior
- Use `Physics.SyncTransforms()` only when you must read physics state immediately after moving transforms
- Use Continuous collision detection for fast-moving objects to prevent tunneling

## Joints

### 3D Joints
- **HingeJoint**: Rotation around a single axis (doors, wheels)
- **SpringJoint**: Elastic connection between two bodies
- **FixedJoint**: Rigid connection (welding objects together)
- **CharacterJoint**: Ragdoll limb connections
- **ConfigurableJoint**: Full control over all axes

### 2D Joints
- **HingeJoint2D**, **SpringJoint2D**, **FixedJoint2D**, **DistanceJoint2D**, **SliderJoint2D**

## Physics Materials

Control friction and bounciness:

```
Friction: 0.0 (ice) to 1.0 (rubber)
Bounciness: 0.0 (no bounce) to 1.0 (full bounce)
Friction Combine: Average, Minimum, Maximum, Multiply
Bounce Combine: Average, Minimum, Maximum, Multiply
```

## Common Gotchas

- A Collider without a Rigidbody is static. Moving it forces Unity to rebuild the physics world (expensive).
- Triggers do not generate collision contacts. Use OnTriggerEnter, not OnCollisionEnter.
- Scale affects collider size. Non-uniform scale on mesh colliders is especially problematic.
- 2D and 3D physics are completely separate systems. A Rigidbody2D does not interact with a 3D Collider.
- Rigidbody.isKinematic prevents all physics forces. Use it for scripted movement.

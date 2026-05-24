---
title: Animation Systems
description: Unity animation workflows including Animator Controller, Timeline, DOTween, and sprite animation for 2D.
globs: ["**/*.cs", "**/*.controller", "**/*.anim", "**/*.playable"]
standards-version: 1.10.0
---

# Animation Systems

## Animator Controller

The Animator Controller is Unity's primary animation state machine. It manages states, transitions, parameters, layers, and blend trees.

### States and Transitions

- Each state plays an Animation Clip or Blend Tree
- Transitions define conditions for switching between states
- Use "Has Exit Time" for animations that must complete (attack finishers)
- Disable "Has Exit Time" for instant transitions (idle to run)

### Parameters

Control transitions from scripts using parameters:

```csharp
private Animator _animator;

private void Awake()
{
    _animator = GetComponent<Animator>();
}

private void Update()
{
    _animator.SetFloat("Speed", _currentSpeed);
    _animator.SetBool("IsGrounded", _isGrounded);
}

public void Attack()
{
    _animator.SetTrigger("Attack");
}
```

Parameter types: `SetFloat`, `SetBool`, `SetInteger`, `SetTrigger`.

Triggers reset automatically after the transition fires. Bools persist until explicitly changed.

### Blend Trees

Blend between multiple animations based on parameters:
- 1D Blend Tree: walk to run based on speed
- 2D Freeform: directional movement blending (strafe, forward, backward)
- Direct: explicit weight control per child motion

### Layers

Use layers for independent animation on different body parts:
- Base Layer: locomotion (full body)
- Upper Body Layer: aiming, shooting (override or additive blending)
- Face Layer: facial expressions (additive)

Set layer weight with `_animator.SetLayerWeight(layerIndex, weight)`.

## Animation Events

Call methods from specific frames in an animation clip:

```csharp
public void OnFootstep()
{
    _audioSource.PlayOneShot(_footstepClip);
}

public void OnAttackHit()
{
    DealDamageInRange();
}
```

Add events in the Animation window by selecting a frame and clicking "Add Event."

## Root Motion vs Scripted Movement

- **Root Motion**: Animation drives the transform. Enable "Apply Root Motion" on Animator. Good for realistic character movement where animation artists control locomotion.
- **Scripted Movement**: Code drives the transform; animation is cosmetic. Disable "Apply Root Motion." Better for precise gameplay control.

Use `OnAnimatorMove()` to customize how root motion is applied:

```csharp
private void OnAnimatorMove()
{
    Vector3 velocity = _animator.deltaPosition / Time.deltaTime;
    _rb.linearVelocity = new Vector3(velocity.x, _rb.linearVelocity.y, velocity.z);
}
```

## Inverse Kinematics (IK)

Use `OnAnimatorIK` to adjust limb positions at runtime:

```csharp
private void OnAnimatorIK(int layerIndex)
{
    if (_lookTarget)
    {
        _animator.SetLookAtWeight(1f);
        _animator.SetLookAtPosition(_lookTarget.position);
    }

    if (_rightHandTarget)
    {
        _animator.SetIKPositionWeight(AvatarIKGoal.RightHand, 1f);
        _animator.SetIKPosition(AvatarIKGoal.RightHand, _rightHandTarget.position);
    }
}
```

Requires a Humanoid avatar and an Animator Controller with IK Pass enabled on the layer.

## DOTween / LeanTween

For procedural, code-driven animation:

```csharp
// DOTween examples
transform.DOMove(targetPosition, 1f).SetEase(Ease.OutQuad);
transform.DOScale(Vector3.one * 1.5f, 0.3f).SetLoops(2, LoopType.Yoyo);
_canvasGroup.DOFade(0f, 0.5f).OnComplete(() => gameObject.SetActive(false));

// Sequences
DOTween.Sequence()
    .Append(transform.DOMove(pos1, 0.5f))
    .Append(transform.DOMove(pos2, 0.5f))
    .Join(transform.DORotate(new Vector3(0, 180, 0), 0.5f));
```

Use DOTween for UI animations, camera effects, and any animation that needs to be driven by game logic rather than pre-authored clips.

## Timeline

Timeline is for cinematic sequences, cutscenes, and scripted events:

- Activation Track: enable/disable GameObjects at specific times
- Animation Track: play animation clips on specific objects
- Audio Track: trigger audio clips with precise timing
- Signal Track: fire events at specific points in the timeline
- Cinemachine Track: control camera shots and transitions

Control playback from code:

```csharp
[SerializeField] private PlayableDirector _director;

public void PlayCutscene()
{
    _director.Play();
}

public void SkipCutscene()
{
    _director.time = _director.duration;
    _director.Evaluate();
}
```

## 2D Sprite Animation

For 2D games, animate sprites using the Animator:

1. Import a sprite sheet and set Sprite Mode to "Multiple"
2. Use the Sprite Editor to slice individual frames
3. Create an Animation Clip by dragging frames into the Animation window
4. The Animator Controller manages state transitions between clips

Use `SpriteRenderer.flipX` for direction changes instead of duplicating animations.

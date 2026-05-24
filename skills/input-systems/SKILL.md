---
title: Input Systems
description: Input handling with the New Input System package and legacy Input Manager migration guidance.
globs: ["**/*.cs", "**/*.inputactions"]
standards-version: 1.10.0
---

# Input Systems

## New Input System (Recommended)

The Input System package (com.unity.inputsystem 1.7+) is the modern standard for all new Unity projects. It provides an event-driven model, unified device support, and built-in rebinding.

### Input Actions Asset

Create an `.inputactions` asset to define all input bindings:

1. Right-click in Project window: Create > Input Actions
2. Define Action Maps (Player, UI, Vehicle)
3. Define Actions within each map (Move, Jump, Fire, Look)
4. Add Bindings to each action (keyboard, gamepad, touch)

### Action Maps

Organize input by context:
- **Player**: movement, jumping, attacking, interacting
- **UI**: navigation, submit, cancel, scroll
- **Vehicle**: steering, acceleration, braking
- **Menu**: back, tab switching

Switch maps at runtime:

```csharp
_playerInput.SwitchCurrentActionMap("UI");
```

### Composite Bindings

Use composites for multi-key inputs:
- **2D Vector** (WASD): combines W/A/S/D into a Vector2
- **1D Axis**: combines two keys into a float (-1 to 1)
- **Button With One Modifier**: Ctrl+S, Shift+Click

Composites are more efficient than polling individual keys.

### PlayerInput Component

The simplest way to receive input. Add the PlayerInput component and choose a behavior mode:

- **Send Messages**: Calls `OnMove(InputValue)`, `OnJump(InputValue)` methods on the same GameObject
- **Invoke Unity Events**: Wire actions to UnityEvents in the inspector
- **Invoke C# Events**: Subscribe in code

### Direct C# API

For full control:

```csharp
using UnityEngine.InputSystem;

public class PlayerController : MonoBehaviour
{
    private PlayerInputActions _input;

    private void Awake()
    {
        _input = new PlayerInputActions();
    }

    private void OnEnable()
    {
        _input.Player.Enable();
        _input.Player.Jump.performed += OnJump;
        _input.Player.Fire.performed += OnFire;
    }

    private void OnDisable()
    {
        _input.Player.Jump.performed -= OnJump;
        _input.Player.Fire.performed -= OnFire;
        _input.Player.Disable();
    }

    private void Update()
    {
        Vector2 moveInput = _input.Player.Move.ReadValue<Vector2>();
        Move(moveInput);
    }

    private void OnJump(InputAction.CallbackContext ctx)
    {
        Jump();
    }

    private void OnFire(InputAction.CallbackContext ctx)
    {
        Fire();
    }
}
```

### Callback Phases

Each action has three phases:
- **started**: Input begins (key pressed, stick moved off center)
- **performed**: Input reaches its threshold (button fully pressed, hold time met)
- **canceled**: Input ends (key released, stick returns to center)

### Runtime Rebinding

```csharp
public async void StartRebinding(InputAction action)
{
    action.Disable();

    var operation = action.PerformInteractiveRebinding()
        .WithControlsExcluding("Mouse/position")
        .OnComplete(op =>
        {
            op.Dispose();
            action.Enable();
            SaveBindings();
        })
        .Start();
}
```

### Local Multiplayer

Use `PlayerInputManager` for split-screen or shared-screen multiplayer:
- Set Join Behavior (press button to join, auto-join on connect)
- Assign different control schemes per player
- PlayerInput components are auto-instantiated per player

## Legacy Input Manager

The old `Input.GetKey`/`Input.GetAxis` API. Use only for:
- Maintaining legacy projects that cannot migrate
- Ultra-quick throwaway prototypes

```csharp
// Legacy - avoid for new projects
float h = Input.GetAxis("Horizontal");
float v = Input.GetAxis("Vertical");
bool jump = Input.GetButtonDown("Jump");
```

### Why Migrate

- No runtime rebinding support
- No composite bindings
- Poor device abstraction (gamepad support is limited)
- Polling-based (checks every frame even when nothing changes)
- No action map switching

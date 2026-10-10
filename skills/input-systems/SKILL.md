---
title: Input Systems
description: Use when the user handles keyboard, mouse, gamepad, or touch input, sees errors from UnityEngine.Input, sets up PlayerInput or .inputactions assets, adds key rebinding, or adds local multiplayer. Covers the Input System package, action maps, callbacks, rebinding, and migrating from the legacy Input Manager.
globs: ["**/*.cs", "**/*.inputactions"]
standards-version: 1.10.0
---

# Input Systems

## Check the Project First

Call the `analyze_project` MCP tool with the Unity project root before writing input code. Its **Active input handling** line says whether the project uses the Input Manager (old), the Input System package (new), or both, and the package list shows the installed `com.unity.inputsystem` version. Write code for what the project actually uses: `UnityEngine.Input` calls throw at runtime when only the new Input System is active.

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

The rebinding operation is callback based, so the method does not need to be `async`. Keep a reference so you can dispose it when it finishes, is canceled, or the object is destroyed:

```csharp
private InputActionRebindingExtensions.RebindingOperation _rebind;

public void StartRebinding(InputAction action, int bindingIndex)
{
    action.Disable();
    _rebind = action.PerformInteractiveRebinding(bindingIndex)
        .WithControlsExcluding("<Mouse>/position")
        .WithCancelingThrough("<Keyboard>/escape")
        .OnComplete(_ => FinishRebinding(action))
        .OnCancel(_ => FinishRebinding(action))
        .Start();
}

private void FinishRebinding(InputAction action)
{
    _rebind.Dispose();
    _rebind = null;
    action.Enable();
    PlayerPrefs.SetString("rebinds", action.actionMap.asset.SaveBindingOverridesAsJson());
}

private void OnDestroy() => _rebind?.Dispose();
```

Restore saved overrides at startup with `asset.LoadBindingOverridesFromJson(PlayerPrefs.GetString("rebinds"))`.

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

# 3D FPS Template

A starter template for a first-person shooter with character controller, mouse look, and weapon system.

## Scripts

- **FPSController.cs** - CharacterController movement, sprint, jump, and mouse look (look stops while paused)
- **WeaponSystem.cs** - Raycast shooting with fire rate, ammo, and reload; damages anything implementing `IDamageable`
- **GameManager.cs** - Singleton game manager with score and pause state

## Requirements

- Unity 6 with the **Input System** package (installed by default in new Unity 6 projects).
  **Project Settings > Player > Active Input Handling** must be *Input System Package* or *Both*.
- The project-wide input actions asset (created by default). Its **Player** map already has
  **Move**, **Look**, **Jump**, **Sprint**, and **Attack**. Add a **Reload** button action
  (for example bound to `R` and the gamepad West button) to use reloading.

## Setup

1. Create a project from the **Universal 3D** template and copy this folder into `Assets/`.
2. Create a Player GameObject and add **FPSController** (a CharacterController is added automatically).
3. Move the Main Camera under the Player at head height and assign it to **Camera Transform**.
4. Add **WeaponSystem** to the Player. Set **Hit Layers** to the layers that can be shot, and optionally assign a **Muzzle Point** and **Muzzle Flash**.
5. Add a **Player Input** component to the Player, assign the project-wide actions asset, and set **Behavior** to **Send Messages**. This calls `OnMove`, `OnLook`, `OnJump`, and `OnReload`.
   Held buttons (**Sprint**, **Attack**) are read with `InputAction.IsPressed()` from `InputSystem.actions`, because Send Messages does not report button releases.
6. Add an empty GameObject with **GameManager**. Call `GameManager.Instance.TogglePause()` from your pause input or menu.

## Damage

Implement `IDamageable` on enemies or props:

```csharp
public class Target : MonoBehaviour, FPS3D.IDamageable
{
    public void TakeDamage(int amount) => Debug.Log($"Hit for {amount}");
}
```

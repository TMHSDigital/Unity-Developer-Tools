# 3D FPS Template

A starter template for a first-person shooter with character controller, mouse look, and weapon system.

## Scripts

- **FPSController.cs** - CharacterController-based FPS movement with mouse look
- **WeaponSystem.cs** - Raycast-based shooting with fire rate, ammo, and reload
- **GameManager.cs** - Singleton game manager with score and game state

## Setup

1. Create a 3D URP project
2. Add FPSController to your player (needs CharacterController component)
3. Create a child Camera for the player
4. Add WeaponSystem to the player or weapon mount
5. Configure Input Actions for Move, Look, Fire, Reload, Jump

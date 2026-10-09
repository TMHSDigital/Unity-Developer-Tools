# 2D Platformer Template

A starter template for a 2D side-scrolling platformer with player movement, jumping, and camera follow.

## Scripts

- **PlayerController2D.cs** - Rigidbody2D movement with ground check, coyote time, and jump buffering
- **GameManager.cs** - Singleton game manager for score, lives, and game state
- **CameraFollow2D.cs** - Smooth, frame-rate independent camera follow with a dead zone and optional bounds

## Requirements

- Unity 6 with the **Input System** package (installed by default in new Unity 6 projects).
  **Project Settings > Player > Active Input Handling** must be *Input System Package* or *Both*.
- The project-wide input actions asset (created by default) with **Player/Move** and **Player/Jump** actions

## Setup

1. Create a project from the **Universal 2D** template and copy this folder into `Assets/`.
2. Create a **Ground** layer (**Project Settings > Tags and Layers**) and put your ground tiles or colliders on it.
3. Create a Player GameObject with a SpriteRenderer, then add **PlayerController2D**. Rigidbody2D and BoxCollider2D are added automatically.
4. On PlayerController2D, set **Ground Layer** to `Ground`. **Ground Check** is optional: leave it empty to test from the bottom of the collider, or assign an empty child placed at the feet.
5. Add a **Player Input** component to the Player, assign the project-wide actions asset, and set **Behavior** to **Send Messages**. This calls `OnMove` and `OnJump` on PlayerController2D.
6. Add **CameraFollow2D** to the Main Camera and assign the Player as **Target**. Tune **Dead Zone** and enable **Use Bounds** to clamp the camera to your level.
7. Add an empty GameObject with **GameManager** to the scene.

## Optional animator parameters

If the Player has an Animator, PlayerController2D drives these parameters: `Speed` (float), `IsGrounded` (bool), and `VerticalSpeed` (float).

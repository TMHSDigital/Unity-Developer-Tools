# 2D Platformer Template

A starter template for a 2D side-scrolling platformer with player movement, jumping, and camera follow.

## Scripts

- **PlayerController2D.cs** - Rigidbody2D-based movement with ground check, jumping, and coyote time
- **GameManager.cs** - Singleton game manager for score, lives, and game state
- **CameraFollow2D.cs** - Smooth camera follow with dead zone and bounds

## Setup

1. Create a 2D URP project
2. Add these scripts to your project
3. Create a Player GameObject with Rigidbody2D, BoxCollider2D, and PlayerController2D
4. Create a Camera with CameraFollow2D and assign the player as target
5. Create ground objects on the "Ground" layer
6. Add a GameManager to the scene

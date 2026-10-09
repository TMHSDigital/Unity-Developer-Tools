# Editor Tool Template

A UI Toolkit Editor Window that places prefab instances in the open scene, with optional grid snapping and full Undo support.

## Scripts

- **LevelBuilderWindow.cs** - EditorWindow with a prefab field, grid size, snap toggle, and buttons to place the prefab at the Scene view center or the world origin

## Requirements

- Unity 6, no extra packages. Editor only: the file is wrapped in `#if UNITY_EDITOR`, so it is excluded from player builds.

## Setup

1. Copy `LevelBuilderWindow.cs` into an `Editor/` folder (for example `Assets/Editor/`).
2. Open **Tools > Level Builder**.
3. Drag a prefab asset from the Project window into **Prefab**. Scene objects are not accepted.
4. Set **Grid Size** and **Snap to Grid**, then click **Place at Center** (Scene view pivot, snapped) or **Place at Origin**.
5. Each placement is selected and can be undone with Ctrl+Z / Cmd+Z.

## Extending

Ideas for growing this into a full level builder: a palette of several prefabs, click-to-place in the Scene view via `SceneView.duringSceneGui`, and rotation or parenting options.

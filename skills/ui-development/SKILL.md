---
title: UI Development
description: Building user interfaces with UI Toolkit (primary) and Canvas/UGUI, including data binding, styling, and responsive layouts.
globs: ["**/*.cs", "**/*.uxml", "**/*.uss", "**/*.prefab"]
standards-version: 1.10.0
---

# UI Development

## Choosing a UI System

### UI Toolkit (Recommended for new projects)

The modern, retained-mode UI system. Uses UXML for layout and USS for styling, similar to HTML/CSS. Best for:

- Main menus, settings screens, HUD overlays
- Editor tools and custom inspectors
- Data-heavy interfaces (inventories, skill trees, dashboards)
- Projects that need source-control-friendly UI definitions

### Canvas/UGUI (Legacy, still supported)

The older immediate-style system using GameObjects and Canvas components. Still valid for:

- World-space UI (floating health bars, interaction prompts)
- Projects already using Canvas extensively
- Quick prototypes where visual layout in the scene view is preferred

## UI Toolkit

### Document Structure

A UI Toolkit panel needs a `UIDocument` component referencing a UXML file:

```csharp
public class MainMenuController : MonoBehaviour
{
    [SerializeField] private UIDocument _document;

    private Button _startButton;
    private Button _settingsButton;

    private void OnEnable()
    {
        var root = _document.rootVisualElement;
        _startButton = root.Q<Button>("start-button");
        _settingsButton = root.Q<Button>("settings-button");

        _startButton.clicked += OnStartClicked;
        _settingsButton.clicked += OnSettingsClicked;
    }

    private void OnDisable()
    {
        _startButton.clicked -= OnStartClicked;
        _settingsButton.clicked -= OnSettingsClicked;
    }

    private void OnStartClicked() => SceneManager.LoadScene("Game");
    private void OnSettingsClicked() => ShowSettingsPanel();
}
```

### USS Styling

```css
.main-menu {
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.8);
}

.menu-button {
    width: 300px;
    height: 60px;
    margin: 10px;
    font-size: 24px;
    -unity-font-style: bold;
    background-color: rgb(40, 40, 40);
    color: rgb(220, 220, 220);
    border-radius: 8px;
}

.menu-button:hover {
    background-color: rgb(60, 60, 60);
}
```

### Runtime Data Binding (Unity 6)

Bind game variables directly to UI elements without boilerplate:

```csharp
[UxmlElement]
public partial class HealthBar : VisualElement
{
    [UxmlAttribute]
    public float CurrentHealth { get; set; }

    [UxmlAttribute]
    public float MaxHealth { get; set; }
}
```

### Custom Controls with [UxmlElement]

The deprecated `UXMLFactory` pattern is replaced by attribute-based registration:

```csharp
[UxmlElement]
public partial class RadialProgress : VisualElement
{
    [UxmlAttribute]
    public float Progress { get; set; }

    public RadialProgress()
    {
        generateVisualContent += OnGenerateVisualContent;
    }

    private void OnGenerateVisualContent(MeshGenerationContext ctx)
    {
        // Custom drawing logic
    }
}
```

## Canvas/UGUI

### Canvas Render Modes

- **Screen Space - Overlay**: Renders on top of everything. No camera required. Use for HUD.
- **Screen Space - Camera**: Renders as if a fixed distance from a camera. Supports post-processing.
- **World Space**: Exists in 3D space. Use for in-game screens, floating labels, VR interfaces.

### Layout Components

- **HorizontalLayoutGroup**: Arrange children in a row
- **VerticalLayoutGroup**: Arrange children in a column
- **GridLayoutGroup**: Arrange children in a grid
- **ContentSizeFitter**: Auto-size to content
- **LayoutElement**: Override layout sizing per element

### Anchoring for Responsive UI

Set anchors to handle different screen resolutions:
- Anchor to corners for elements that should stay at screen edges
- Anchor to center for centered elements
- Stretch anchors for elements that should scale with screen size

### Performance

- Minimize Canvas rebuilds: separate dynamic and static elements onto different Canvases
- Use Canvas Groups to toggle visibility instead of enabling/disabling GameObjects
- Mark static UI elements with "Raycast Target: false" if they do not need click detection
- Use TextMeshPro for ALL text rendering; never use the legacy Text component

## TextMeshPro

Always use TextMeshPro (TMP) for text:

```csharp
using TMPro;

[SerializeField] private TMP_Text _scoreText;

private void UpdateScore(int score)
{
    _scoreText.SetText("Score: {0}", score);
}
```

Use `SetText` with format parameters instead of string concatenation to avoid garbage collection.

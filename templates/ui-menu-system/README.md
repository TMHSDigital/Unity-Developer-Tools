# UI Menu System Template

A UI Toolkit main menu with a settings panel (volume, quality, fullscreen) that persists to PlayerPrefs.

## Files

- **MenuManager.cs** - Shows the main menu or settings panel, loads the game scene, quits
- **SettingsManager.cs** - Volume sliders (AudioMixer), quality level, and fullscreen, saved to PlayerPrefs and applied on start
- **MainMenu.uxml** - Layout with every element the scripts query
- **MainMenu.uss** - Basic styling (referenced from the UXML)

## Requirements

- Unity 6 (UI Toolkit is built in; no extra packages)
- An AudioMixer with three exposed parameters named exactly `MasterVolume`, `MusicVolume`, and `SfxVolume`
  (select the mixer group, right-click its Volume in the Inspector, choose **Expose**, then rename it in the
  Exposed Parameters list)
- A scene named `Game` in the Build Profiles scene list, or change **Game Scene Name** on MenuManager

## Setup

1. Copy this folder into `Assets/` (for example `Assets/UIMenuSystem/`).
2. In your menu scene, create **GameObject > UI Toolkit > UI Document**.
3. Assign `MainMenu.uxml` to the UI Document's **Source Asset**. A Panel Settings asset is created automatically if the project has none.
4. Add **MenuManager** to the same GameObject (it requires the UI Document).
5. Add **SettingsManager**, then assign the UI Document and your AudioMixer in the Inspector.
6. Press Play. The settings panel opens from the Settings button, and values persist between sessions.

## Element names

If you build your own UXML, keep these names so the scripts can find the elements:

| Name | Type | Used by |
|------|------|---------|
| `main-menu` | VisualElement | MenuManager |
| `settings-panel` | VisualElement | MenuManager |
| `play-button`, `settings-button`, `quit-button`, `back-button` | Button | MenuManager |
| `master-volume`, `music-volume`, `sfx-volume` | Slider (0 to 1) | SettingsManager |
| `quality-dropdown` | DropdownField | SettingsManager |
| `fullscreen-toggle` | Toggle | SettingsManager |

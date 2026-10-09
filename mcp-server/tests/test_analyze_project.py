"""Tests for analyze_project using minimal Unity 6 project trees.

The YAML layouts mirror real Unity 6 projects: wrapped GUID lines in
GraphicsSettings, per-quality-level pipelines, and the empty-key default
entry in scriptingDefineSymbols.
"""

import json

import server

URP_SCRIPT_GUID = "bf2edee5c58d82540a51f03df9d42094"
HDRP_SCRIPT_GUID = "0cf1dab834d4ec34195b920ea7bbf9ec"
ASSET_GUID = "8f54365222beb0c48917d3cbb0648548"

PLAYER_SETTINGS = """%YAML 1.1
%TAG !u! tag:unity3d.com,2011:
--- !u!129 &1
PlayerSettings:
  productName: Demo
  scriptingDefineSymbols:
    : USE_FEATURE_A;USE_FEATURE_B
    Android: MOBILE_BUILD
  additionalCompilerArguments: {{}}
  scriptingBackend:
    Android: 1
    Standalone: 0
  il2cppCompilerConfiguration: {{}}
  apiCompatibilityLevelPerPlatform:
    Standalone: 6
  activeInputHandler: {input}
  windowsGamepadBackendHint: 0
"""


def make_project(root, *, packages=None, graphics_guid=None, quality_guids=(),
                 pipeline_script=None, pipeline_body="", input_handler=1, asmdefs=()):
    (root / "Assets").mkdir(parents=True)
    settings = root / "ProjectSettings"
    settings.mkdir()
    (root / "Packages").mkdir()

    (settings / "ProjectVersion.txt").write_text(
        "m_EditorVersion: 6000.0.84f1\nm_EditorVersionWithRevision: 6000.0.84f1 (78ab6fc243d5)\n"
    )
    (settings / "ProjectSettings.asset").write_text(PLAYER_SETTINGS.format(input=input_handler))

    if graphics_guid:
        graphics_ref = f"{{fileID: 11400000, guid: {graphics_guid},\n    type: 2}}"
    else:
        graphics_ref = "{fileID: 0}"
    (settings / "GraphicsSettings.asset").write_text(
        "%YAML 1.1\n--- !u!30 &1\nGraphicsSettings:\n"
        f"  m_CustomRenderPipeline: {graphics_ref}\n  m_TransparencySortMode: 0\n"
    )

    levels = "".join(
        f"  - serializedVersion: 4\n    name: Level{i}\n"
        f"    customRenderPipeline: {{fileID: 11400000, guid: {guid}, type: 2}}\n"
        for i, guid in enumerate(quality_guids)
    )
    (settings / "QualitySettings.asset").write_text(
        f"%YAML 1.1\n--- !u!47 &1\nQualitySettings:\n  m_CurrentQuality: 0\n  m_QualitySettings:\n{levels}"
    )

    (root / "Packages" / "manifest.json").write_text(json.dumps({"dependencies": packages or {}}))

    if pipeline_script:
        settings_dir = root / "Assets" / "Settings"
        settings_dir.mkdir()
        asset = settings_dir / "PipelineAsset.asset"
        asset.write_text(
            "%YAML 1.1\n--- !u!114 &11400000\nMonoBehaviour:\n"
            f"  m_Script: {{fileID: 11500000, guid: {pipeline_script}, type: 3}}\n"
            f"  m_Name: PipelineAsset\n{pipeline_body}"
        )
        (settings_dir / "PipelineAsset.asset.meta").write_text(
            f"fileFormatVersion: 2\nguid: {ASSET_GUID}\nNativeFormatImporter:\n"
        )

    for rel, data in asmdefs:
        path = root / "Assets" / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data))
    return root


def test_urp_project_detected_from_graphics_settings(tmp_path):
    project = make_project(
        tmp_path / "UrpGame",
        packages={"com.unity.render-pipelines.universal": "17.0.4", "com.unity.inputsystem": "1.14.0"},
        graphics_guid=ASSET_GUID,
        pipeline_script=URP_SCRIPT_GUID,
        pipeline_body="  m_RendererDataList:\n  - {fileID: 0}\n",
    )
    result = server.analyze_project(str(project))
    assert "**Editor version**: 6000.0.84f1" in result
    assert "**Render pipeline**: URP (com.unity.render-pipelines.universal 17.0.4)" in result
    assert "Assets/Settings/PipelineAsset.asset" in result
    assert 'pipeline="urp"' in result
    assert "Input System Package (new)" in result
    assert "Input System 1.14.0" in result


def test_urp_assigned_only_per_quality_level(tmp_path):
    # Real Unity 6 projects can leave Graphics empty and assign URP per quality level
    project = make_project(
        tmp_path / "QualityOnly",
        packages={"com.unity.render-pipelines.universal": "17.0.3"},
        quality_guids=[ASSET_GUID],
        pipeline_script=URP_SCRIPT_GUID,
    )
    assert "**Render pipeline**: URP" in server.analyze_project(str(project))


def test_hdrp_project_detected(tmp_path):
    project = make_project(
        tmp_path / "HdrpGame",
        packages={"com.unity.render-pipelines.high-definition": "17.0.4"},
        graphics_guid=ASSET_GUID,
        pipeline_script=HDRP_SCRIPT_GUID,
        pipeline_body="  m_RenderPipelineSettings:\n    supportShadowMask: 1\n",
    )
    result = server.analyze_project(str(project))
    assert "**Render pipeline**: HDRP (com.unity.render-pipelines.high-definition 17.0.4)" in result
    assert 'pipeline="hdrp"' in result


def test_builtin_project(tmp_path):
    project = make_project(tmp_path / "Legacy", packages={"com.unity.ugui": "2.0.0"}, input_handler=0)
    result = server.analyze_project(str(project))
    assert "**Render pipeline**: Built-in" in result
    assert "Input Manager (old)" in result
    assert 'pipeline="builtin"' in result


def test_srp_installed_but_unassigned_is_builtin_with_note(tmp_path):
    project = make_project(tmp_path / "Unassigned", packages={"com.unity.render-pipelines.universal": "17.0.4"})
    result = server.analyze_project(str(project))
    assert "**Render pipeline**: Built-in" in result
    assert "URP is installed but no pipeline asset is assigned" in result


def test_unreadable_pipeline_asset_falls_back_to_packages(tmp_path):
    project = make_project(
        tmp_path / "MissingAsset",
        packages={"com.unity.render-pipelines.universal": "17.0.4"},
        graphics_guid="0123456789abcdef0123456789abcdef",
    )
    result = server.analyze_project(str(project))
    assert "**Render pipeline**: URP" in result
    assert "inferred from installed packages" in result


def test_player_settings_maps(tmp_path):
    project = make_project(tmp_path / "Settings", input_handler=2)
    result = server.analyze_project(str(project))
    assert "**Active input handling**: Both" in result
    assert "Android IL2CPP" in result and "Standalone Mono" in result
    assert "Standalone .NET Standard 2.1" in result
    assert "Default: `USE_FEATURE_A;USE_FEATURE_B`" in result
    assert "Android: `MOBILE_BUILD`" in result
    assert "com.unity.inputsystem is not installed" in result


def test_crlf_settings_are_parsed(tmp_path):
    project = make_project(tmp_path / "Crlf")
    path = project / "ProjectSettings" / "ProjectSettings.asset"
    path.write_bytes(path.read_text().replace("\n", "\r\n").encode())
    result = server.analyze_project(str(project))
    assert "Input System Package (new)" in result
    assert "Android IL2CPP" in result


def test_asmdefs_listed(tmp_path):
    project = make_project(
        tmp_path / "Asm",
        asmdefs=[
            ("Scripts/Game.asmdef", {"name": "Game", "rootNamespace": "MyGame"}),
            ("Editor/Game.Editor.asmdef", {"name": "Game.Editor", "includePlatforms": ["Editor"]}),
            ("Tests/Game.Tests.asmdef", {"name": "Game.Tests", "defineConstraints": ["UNITY_INCLUDE_TESTS"]}),
        ],
    )
    result = server.analyze_project(str(project))
    assert "**Assembly definitions** (3)" in result
    assert "Game (`Assets/Scripts/Game.asmdef`; namespace MyGame)" in result
    assert "Game.Editor (`Assets/Editor/Game.Editor.asmdef`; editor)" in result
    assert "tests" in result


def test_no_asmdefs(tmp_path):
    result = server.analyze_project(str(make_project(tmp_path / "Plain")))
    assert "all scripts compile into Assembly-CSharp" in result


def test_not_a_unity_project(tmp_path):
    assert "does not look like a Unity project" in server.analyze_project(str(tmp_path))
    assert "Not a directory" in server.analyze_project(str(tmp_path / "missing"))

"""Tests for the Unity Developer Tools MCP server tools."""

import asyncio
import json
import sys
from pathlib import Path

import pytest

import server

SERVER_DIR = Path(__file__).resolve().parent.parent


# ---------- data loading ----------

def test_tools_work_from_any_working_directory(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert "## Rigidbody.AddForce" in server.lookup_api("Rigidbody")
    assert "UNITY_STANDALONE_WIN" in server.platform_info("windows")


def test_missing_data_file_raises(tmp_path, monkeypatch):
    monkeypatch.setattr(server, "DATA_PATH", tmp_path)
    with pytest.raises(FileNotFoundError, match="unity_api_common.json"):
        server.lookup_api("Rigidbody")


def test_all_data_files_present():
    server._check_data_files()


# ---------- lookup_api ----------

@pytest.mark.parametrize(
    "category",
    ["general", "physics", "ui", "animation", "audio", "rendering",
     "input", "networking", "editor"],
)
def test_every_advertised_category_has_entries(category):
    entries = [
        e for e in server._load_json("unity_api_common.json")
        if e["category"] == category
    ]
    assert entries, f"category '{category}' is advertised but empty"


def test_category_filter_returns_only_that_category():
    result = server.lookup_api("Input", "input")
    assert "## InputAction.ReadValue" in result
    assert "**Category**: physics" not in result


def test_unknown_category_lists_valid_ones():
    result = server.lookup_api("Rigidbody", "weapons")
    assert "Unknown category" in result
    assert "physics" in result


def test_multi_word_query_matches_all_terms():
    assert "## SceneManager.LoadSceneAsync" in server.lookup_api("load scene async")


def test_results_ranked_exact_then_name_then_description(tmp_path, monkeypatch):
    def api(name, description):
        return {"name": name, "namespace": "UnityEngine", "category": "general",
                "description": description, "signature": ""}

    # Stored in worst-first order so the test fails if ranking is skipped.
    (tmp_path / "unity_api_common.json").write_text(json.dumps([
        api("Time.timeScale", "Scales Time.deltaTime."),
        api("Time.deltaTimeScaled", "Name contains the query."),
        api("Time.deltaTime", "Exact match."),
    ]))
    (tmp_path / "deprecated_patterns.json").write_text("[]")
    monkeypatch.setattr(server, "DATA_PATH", tmp_path)

    result = server.lookup_api("Time.deltaTime")
    order = [line[3:] for line in result.splitlines() if line.startswith("## ")]
    assert order == ["Time.deltaTime", "Time.deltaTimeScaled", "Time.timeScale"]


def test_no_obsolete_velocity_entry():
    names = {e["name"] for e in server._load_json("unity_api_common.json")}
    assert "Rigidbody.velocity" not in names
    assert "Rigidbody.linearVelocity" in names


def test_velocity_query_warns_about_unity6_rename():
    result = server.lookup_api("velocity")
    assert "WARNING" in result
    assert "linearVelocity" in result


def test_no_results_message_suggests_categories():
    result = server.lookup_api("zzznotanapi")
    assert "No API entries found" in result
    assert "networking" in result


# ---------- shader_helper ----------

def test_urp_returns_hlsl_code():
    result = server.shader_helper("toon", "urp")
    assert "```hlsl" in result
    assert "GetMainLight" in result


@pytest.mark.parametrize("pipeline", ["hdrp", "builtin"])
def test_non_urp_pipelines_do_not_get_urp_code(pipeline):
    for effect in ("dissolve", "outline", "fresnel", "toon", "water", "hologram"):
        result = server.shader_helper(effect, pipeline)
        assert "```hlsl" not in result, f"{effect} on {pipeline} returned URP code"
        assert "Shader Graph" in result


def test_unknown_pipeline_rejected():
    assert "Unknown pipeline" in server.shader_helper("toon", "lwrp")


def test_unknown_effect_lists_available_effects():
    result = server.shader_helper("lava", "urp")
    assert "Available effects" in result
    assert "dissolve" in result


# ---------- scaffold_script ----------

ALL_TYPES = list(server.SCRIPT_TEMPLATES)


@pytest.mark.parametrize("script_type", ALL_TYPES)
def test_templates_have_no_placeholders_and_balanced_braces(script_type):
    name = {
        "custom-inspector": "PlayerEditor",
        "property-drawer": "RangeDrawer",
        "interface": "IDamageable",
    }.get(script_type, "PlayerHealth")
    result = server.scaffold_script(script_type, name, "Game.Core")
    assert "TARGET_TYPE" not in result
    assert "{" in result and result.count("{") == result.count("}")
    assert f"class {name}" in result or f"interface {name}" in result


@pytest.mark.parametrize("bad_name", ["My Player", "1Player", "Player-Health", "class", ""])
def test_invalid_class_names_rejected(bad_name):
    result = server.scaffold_script("monobehaviour", bad_name)
    assert result.startswith("Invalid class name")


def test_invalid_namespace_rejected():
    result = server.scaffold_script("monobehaviour", "Player", "Game..Core")
    assert result.startswith("Invalid namespace segment")


def test_inspector_infers_target_type_from_name():
    result = server.scaffold_script("custom-inspector", "PlayerEditor")
    assert "[CustomEditor(typeof(Player))]" in result


def test_drawer_uses_explicit_target_type():
    result = server.scaffold_script("property-drawer", "MinMaxView", target_type="MinMaxRange")
    assert "[CustomPropertyDrawer(typeof(MinMaxRange))]" in result


def test_inspector_without_inferable_target_asks_for_one():
    result = server.scaffold_script("custom-inspector", "Inspector")
    assert "Pass target_type" in result


def test_state_machines_do_not_share_an_interface_name():
    first = server.scaffold_script("state-machine", "EnemyBrain")
    second = server.scaffold_script("state-machine", "PlayerBrain")
    assert "interface IEnemyBrainState" in first
    assert "interface IPlayerBrainState" in second


def test_editor_scripts_get_editor_only_note():
    result = server.scaffold_script("editor-window", "LevelTools")
    assert "Assets/Scripts/Editor/LevelTools.cs" in result
    assert "Editor-only" in result


def test_test_scripts_mention_test_assembly():
    result = server.scaffold_script("test", "HealthTests")
    assert "Tests Assembly Folder" in result


def test_interface_without_prefix_gets_note():
    assert "I prefix" in server.scaffold_script("interface", "Damageable")
    assert "I prefix" not in server.scaffold_script("interface", "IDamageable")


def test_unknown_type_lists_valid_types():
    result = server.scaffold_script("ecs", "Mover")
    assert "Unknown script type" in result
    assert "monobehaviour" in result


# ---------- platform_info ----------

def test_platform_info_known_and_unknown():
    assert "UNITY_WEBGL" in server.platform_info("WebGL")
    result = server.platform_info("dreamcast")
    assert "Unknown platform" in result
    assert "windows" in result


# ---------- MCP protocol smoke test ----------

def test_stdio_server_lists_and_calls_tools(tmp_path):
    """Start server.py over stdio from an unrelated directory and call a tool."""
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    params = StdioServerParameters(
        command=sys.executable,
        args=[str(SERVER_DIR / "server.py")],
        cwd=str(tmp_path),
    )

    async def run():
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = await session.list_tools()
                names = {tool.name for tool in tools.tools}
                result = await session.call_tool("platform_info", {"platform": "ios"})
                return names, result.content[0].text

    names, text = asyncio.run(asyncio.wait_for(run(), timeout=60))
    assert names == {"scaffold_script", "lookup_api", "shader_helper", "platform_info"}
    assert "UNITY_IOS" in text

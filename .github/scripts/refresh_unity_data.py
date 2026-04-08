"""
Refresh Unity MCP data files.

Fetches the latest deprecated patterns and lifecycle methods from
Unity documentation and updates the local JSON data files.

This script is called by the update-unity-api.yml workflow.
It performs conservative updates - only modifying files if the
fetched data actually differs from what's on disk.
"""

import json
import os
import sys
import urllib.request
import urllib.error
import re
from pathlib import Path

DATA_DIR = Path("mcp-server/data")

UNITY_DOCS_BASE = "https://docs.unity3d.com/6000.1/Documentation/ScriptReference"

LIFECYCLE_METHODS = [
    ("Awake", "Initialization", False),
    ("OnEnable", "Initialization", False),
    ("Reset", "Initialization", False),
    ("Start", "Initialization", False),
    ("FixedUpdate", "Physics", True),
    ("OnTriggerEnter", "Physics", False),
    ("OnTriggerStay", "Physics", True),
    ("OnTriggerExit", "Physics", False),
    ("OnCollisionEnter", "Physics", False),
    ("OnCollisionStay", "Physics", True),
    ("OnCollisionExit", "Physics", False),
    ("Update", "Game Logic", True),
    ("LateUpdate", "Game Logic", True),
    ("OnAnimatorMove", "Animation", True),
    ("OnAnimatorIK", "Animation", True),
    ("OnPreCull", "Rendering", True),
    ("OnBecameVisible", "Rendering", False),
    ("OnBecameInvisible", "Rendering", False),
    ("OnWillRenderObject", "Rendering", True),
    ("OnPreRender", "Rendering", True),
    ("OnRenderObject", "Rendering", True),
    ("OnPostRender", "Rendering", True),
    ("OnRenderImage", "Rendering", True),
    ("OnGUI", "GUI", True),
    ("OnDrawGizmos", "Editor", True),
    ("OnDrawGizmosSelected", "Editor", False),
    ("OnApplicationPause", "Application", False),
    ("OnApplicationFocus", "Application", False),
    ("OnApplicationQuit", "Application", False),
    ("OnDisable", "Decommissioning", False),
    ("OnDestroy", "Decommissioning", False),
]


def fetch_page(url):
    """Fetch a URL and return the text, or None on failure."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "UnityDevTools/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
        print(f"  Warning: could not fetch {url}: {e}")
        return None


def try_enrich_lifecycle():
    """Try to fetch descriptions for lifecycle methods from Unity docs."""
    result = []
    for method, phase, runs_per_frame in LIFECYCLE_METHODS:
        description = f"MonoBehaviour.{method} callback."
        url = f"{UNITY_DOCS_BASE}/MonoBehaviour.{method}.html"
        page = fetch_page(url)
        if page:
            match = re.search(
                r'<p class="cl-summary">(.*?)</p>', page, re.DOTALL
            )
            if match:
                desc = re.sub(r"<[^>]+>", "", match.group(1)).strip()
                if len(desc) > 10:
                    description = desc

        result.append({
            "method": method,
            "phase": phase,
            "description": description,
            "runs_per_frame": runs_per_frame,
            "thread": "main",
        })

    return result


def update_file(path, new_data):
    """Write JSON if content changed. Returns True if file was updated."""
    new_json = json.dumps(new_data, indent=2, ensure_ascii=False) + "\n"

    if path.exists():
        old_json = path.read_text(encoding="utf-8")
        if old_json == new_json:
            print(f"  {path.name}: no changes")
            return False

    path.write_text(new_json, encoding="utf-8")
    print(f"  {path.name}: updated ({len(new_data)} entries)")
    return True


def main():
    print("Refreshing Unity MCP data files...")
    changed = False

    print("\n1. Lifecycle methods:")
    lifecycle = try_enrich_lifecycle()
    if lifecycle:
        if update_file(DATA_DIR / "lifecycle_order.json", lifecycle):
            changed = True
    else:
        print("  Skipped - no data fetched")

    if changed:
        print("\nData files updated.")
    else:
        print("\nNo changes detected.")

    return 0


if __name__ == "__main__":
    sys.exit(main())

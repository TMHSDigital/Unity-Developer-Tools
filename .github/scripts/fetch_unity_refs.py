"""Download Unity reference assemblies and the Input System package for compile_csharp.py.

Streams the Linux editor archive (several GB) and keeps only the managed
reference assemblies, so nothing large is written to disk. No Unity license
is needed because the editor is never run.

Usage:
    python fetch_unity_refs.py --unity-version 6000.0.84f1 --inputsystem-version 1.20.1 --out .unity-refs

Produces:
    <out>/Editor/Data/Managed/UnityEngine/*.dll
    <out>/Editor/Data/NetStandard/ref/2.1.0/netstandard.dll
    <out>/inputsystem/package/...
"""

import argparse
import io
import json
import lzma
import sys
import tarfile
import urllib.parse
import urllib.request
from pathlib import Path

RELEASES_API = "https://services.api.unity.com/unity/editor/release/v1/releases"
PACKAGES_API = "https://packages.unity.com"
KEEP_PREFIXES = ("Editor/Data/Managed/UnityEngine/", "Editor/Data/NetStandard/ref/2.1.0/")


def editor_url(version: str) -> str:
    query = urllib.parse.urlencode({
        "version": version,
        "platform": "LINUX",
        "architecture": "X86_64",
        "limit": 25,
    })
    with urllib.request.urlopen(f"{RELEASES_API}?{query}") as resp:
        releases = json.load(resp)["results"]
    for release in releases:
        if release["version"] == version:
            for download in release["downloads"]:
                if download["url"].endswith(".tar.xz"):
                    return download["url"]
    sys.exit(f"No Linux editor download found for Unity {version}")


def fetch_editor(version: str, out: Path) -> None:
    url = editor_url(version)
    print(f"Streaming {url}")
    count = 0
    with urllib.request.urlopen(url) as resp, lzma.open(resp) as xz, tarfile.open(fileobj=xz, mode="r|") as tar:
        for member in tar:
            name = member.name.lstrip("./")
            if member.isfile() and name.endswith(".dll") and name.startswith(KEEP_PREFIXES):
                dest = out / name
                dest.parent.mkdir(parents=True, exist_ok=True)
                with tar.extractfile(member) as src:
                    dest.write_bytes(src.read())
                count += 1
    if count == 0:
        sys.exit("No reference assemblies found in the editor archive")
    print(f"Extracted {count} assemblies")


def fetch_package(name: str, version: str, out: Path) -> None:
    with urllib.request.urlopen(f"{PACKAGES_API}/{name}") as resp:
        meta = json.load(resp)
    if version not in meta["versions"]:
        sys.exit(f"{name} {version} not found in the Unity package registry")
    tarball = meta["versions"][version]["dist"]["tarball"]
    print(f"Downloading {tarball}")
    with urllib.request.urlopen(tarball) as resp:
        data = resp.read()
    with tarfile.open(fileobj=io.BytesIO(data)) as tar:
        tar.extractall(out, filter="data")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--unity-version", required=True)
    parser.add_argument("--inputsystem-version", required=True)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    fetch_editor(args.unity_version, args.out)
    fetch_package("com.unity.inputsystem", args.inputsystem_version, args.out / "inputsystem")


if __name__ == "__main__":
    main()

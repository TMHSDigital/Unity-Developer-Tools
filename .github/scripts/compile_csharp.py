"""Compile C# snippets and templates against Unity reference assemblies.

Each snippet file and each template folder is compiled on its own (they reuse
type names such as GameManager), twice:

- player pass: UnityEngine modules only, no UNITY_EDITOR define. Fails if
  editor-only code leaks into what would be a player build.
- editor pass: UNITY_EDITOR defined and UnityEditor modules referenced.

Uses of [Obsolete] APIs (CS0618) are errors so snippets stay on modern APIs.

Usage:
    python compile_csharp.py --unity <Editor/Data> --inputsystem <package dir>

The Editor/Data folder only needs Managed/UnityEngine/*.dll and
NetStandard/ref/2.1.0/netstandard.dll (see fetch_unity_refs.py).
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LANG_VERSION = "9"

# Unity version defines for a 6000.0 editor
UNITY_DEFINES = (
    [f"UNITY_5_{m}_OR_NEWER" for m in range(3, 7)]
    + [f"UNITY_{y}_{m}_OR_NEWER" for y in range(2017, 2024) for m in range(1, 5)]
    + ["UNITY_6000_0_OR_NEWER", "UNITY_6000_0", "UNITY_6000", "ENABLE_INPUT_SYSTEM"]
)

# Unity serializes private fields, so "never assigned" and "unused" warnings are noise
NOWARN = "0169,0414,0649,1701,1702"


def find_csc() -> list:
    override = os.environ.get("CSC")
    if override:
        return [override]
    dotnet = shutil.which("dotnet")
    if not dotnet:
        sys.exit("dotnet SDK not found; install it or set CSC to a csc executable")
    sdks = subprocess.run([dotnet, "--list-sdks"], capture_output=True, text=True, check=True).stdout
    candidates = []
    for line in sdks.splitlines():
        match = re.match(r"(\S+) \[(.+)\]", line.strip())
        if match:
            csc = Path(match.group(2)) / match.group(1) / "Roslyn" / "bincore" / "csc.dll"
            if csc.exists():
                candidates.append(csc)
    if not candidates:
        sys.exit("csc.dll not found in any installed .NET SDK")
    return [dotnet, str(candidates[-1])]


def compile_unit(csc, name, sources, refs, defines, out_dir, extra=()) -> bool:
    out = out_dir / f"{re.sub(r'[^A-Za-z0-9_.]', '_', name)}.dll"
    rsp = out_dir / f"{out.stem}.rsp"
    args = [
        "-nologo", "-noconfig", "-nostdlib+", "-target:library", "-deterministic",
        f"-langversion:{LANG_VERSION}", f"-nowarn:{NOWARN}", f"-out:{out}",
        "-define:" + ";".join(defines),
        *extra,
        *[f"-r:{r}" for r in refs],
        *[str(s) for s in sources],
    ]
    rsp.write_text("\n".join(f'"{a}"' if " " in a else a for a in args), encoding="utf-8")
    result = subprocess.run([*csc, f"@{rsp}"], capture_output=True, text=True, check=False)
    if result.returncode != 0:
        print(f"FAIL {name}")
        for line in (result.stdout + result.stderr).splitlines():
            if "error" in line:
                print("    " + line.replace(str(ROOT) + os.sep, ""))
        return False
    print(f"ok   {name}")
    return True


def package_sources(package_root: Path):
    """C# files of the package's main assembly, skipping nested assemblies and tests."""
    asm_root = package_root / "InputSystem"
    nested = {p.parent for p in asm_root.rglob("*.asmdef") if p.parent != asm_root}
    return sorted(
        p for p in asm_root.rglob("*.cs")
        if not any(n in p.parents for n in nested)
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--unity", required=True, type=Path, help="Unity Editor/Data folder")
    parser.add_argument("--inputsystem", required=True, type=Path, help="com.unity.inputsystem package folder")
    args = parser.parse_args()

    modules = args.unity / "Managed" / "UnityEngine"
    netstandard = args.unity / "NetStandard" / "ref" / "2.1.0" / "netstandard.dll"
    if not modules.is_dir() or not netstandard.is_file():
        sys.exit(f"Unity reference assemblies not found under {args.unity}")

    engine_refs = [netstandard, *sorted(modules.glob("UnityEngine*.dll"))]
    editor_refs = [*engine_refs, *sorted(modules.glob("UnityEditor*.dll"))]

    csc = find_csc()
    units = [(f"snippets/csharp/{p.name}", [p]) for p in sorted((ROOT / "snippets" / "csharp").glob("*.cs"))]
    units += [
        (f"templates/{d.name}", sorted(d.glob("*.cs")))
        for d in sorted((ROOT / "templates").iterdir())
        if d.is_dir() and any(d.glob("*.cs"))
    ]

    ok = True
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        passes = {
            "player": (engine_refs, UNITY_DEFINES),
            "editor": (editor_refs, [*UNITY_DEFINES, "UNITY_EDITOR", "DEBUG", "TRACE"]),
        }
        for pass_name, (refs, defines) in passes.items():
            out_dir = tmp / pass_name
            out_dir.mkdir()
            print(f"== {pass_name} pass")

            # Build the Input System package as a reference, like Unity would
            input_dll = out_dir / "Unity.InputSystem.dll"
            if not compile_unit(
                csc, "Unity.InputSystem", package_sources(args.inputsystem), refs,
                [*defines, "UNITY_INPUT_SYSTEM_ENABLE_PHYSICS", "UNITY_INPUT_SYSTEM_ENABLE_PHYSICS2D"],
                out_dir, extra=["-unsafe+", "-nowarn:0618,0108,0114,0162,0219,0414,0618,0672,1717"],
            ):
                return 1

            for name, sources in units:
                ok &= compile_unit(
                    csc, name, sources, [*refs, input_dll], defines, out_dir,
                    extra=["-warnaserror+:CS0618"],
                )
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

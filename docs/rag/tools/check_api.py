#!/usr/bin/env python3
"""Check BlenderToMob source against the Blender 5.2 API symbol index.

Scans Python files for fully-qualified API references (bpy.types.*, bpy.ops.*,
bpy.props.*, bpy.utils.*, bpy.app.*, bmesh.*, mathutils.*, gpu.*, gpu_extras.*,
blf.*, bpy_extras.*) and for gpu.shader.from_builtin('<NAME>') shader names, then
reports anything that does not exist in the 5.2 reference.

Custom operators (bl_idname defined in this repo) and custom bpy.types
subclasses are ignored. Attribute access through variables (obj.foo) is not
checked -- only dotted references written out in full.

Usage:
    python3 docs/rag/tools/check_api.py              # scans blendertomob/
    python3 docs/rag/tools/check_api.py path/ file.py
    python3 docs/rag/tools/check_api.py --json
"""

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SYMBOLS = ROOT / "docs" / "rag" / "blender-api" / "index" / "symbols.tsv"
GPU_SHADER_DOC = ROOT / "docs" / "rag" / "blender-api" / "corpus" / "gpu.shader.md"

REF_RE = re.compile(
    r"\b((?:bpy\.(?:types|ops|props|utils|app|path|msgbus)|bmesh|mathutils|gpu_extras|gpu|blf|bl_math|bpy_extras)"
    r"(?:\.[A-Za-z_][A-Za-z0-9_]*)+)"
)
BUILTIN_RE = re.compile(r"from_builtin\(\s*['\"]([A-Z0-9_]+)['\"]")
IDNAME_RE = re.compile(r"bl_idname\s*=\s*['\"]([a-z0-9_]+\.[a-z0-9_]+)['\"]")
CUSTOM_PROP_RE = re.compile(r"(bpy\.types\.[A-Za-z_]\w*\.[A-Za-z_]\w*)\s*(?::[^=\n]*)?=(?!=)")
UI_CLASS_RE = re.compile(r"^[A-Z0-9]+_(MT|PT|HT|UL|OT|GT|GGT)_")
CLASS_RE = re.compile(r"^class\s+([A-Za-z_][A-Za-z0-9_]*)", re.M)


def load_symbols():
    syms = {}
    with open(SYMBOLS, encoding="utf-8") as f:
        next(f)
        for line in f:
            sym, role, _ = line.split("\t", 2)
            if role.startswith("py:"):
                syms[sym] = role
    return syms


def builtin_shader_names():
    if not GPU_SHADER_DOC.exists():
        return set()
    text = GPU_SHADER_DOC.read_text(encoding="utf-8")
    return set(re.findall(r"`([A-Z][A-Z0-9_]{3,})`", text))


def resolve(ref, syms, prefixes):
    """True if ref (or its longest documented prefix + an attribute) is known."""
    if ref in syms:
        return True
    parts = ref.split(".")
    # Allow chained attribute access past a documented class/attr/function,
    # e.g. bpy.types.Object.bl_rna or bpy.app.handlers.load_post.append.
    for n in range(len(parts) - 1, 1, -1):
        head = ".".join(parts[:n])
        if head in syms:
            if syms[head] == "py:module":
                return False  # a module's members are all documented: unknown child = missing
            tail = parts[n]
            if head.startswith("bpy.types.") and n == 3:
                return f"{head}.{tail}" in syms or tail in ("append", "prepend", "remove", "bl_rna", "is_registered")
            return True
    return ref in prefixes


def documented_prefix(ref, syms):
    parts = ref.split(".")
    for n in range(len(parts), 1, -1):
        if ".".join(parts[:n]) in syms:
            return ".".join(parts[:n])
    return ref


def symbol_paths():
    paths = {}
    with open(SYMBOLS, encoding="utf-8") as f:
        next(f)
        for line in f:
            sym, role, path = line.rstrip("\n").split("\t")
            if role.startswith("py:"):
                paths[sym] = path
    return paths


def write_map(out, used, n_files):
    paths = symbol_paths()
    groups = defaultdict(list)
    for sym, files in used.items():
        top = sym.split(".")[0] if not sym.startswith("bpy.") else ".".join(sym.split(".")[:2])
        groups[top].append((sym, files))
    lines = [
        "# Mapa de API do Blender usada pelo BlenderToMob",
        "",
        "> Gerado por `python3 docs/rag/tools/check_api.py --map docs/rag/project/01_mapa_api_blendertomob.md`.",
        f"> {n_files} arquivos de `blendertomob/` varridos. Links apontam para a referência 5.2 em `docs/rag/blender-api/corpus/`.",
        "> Só referências escritas por extenso (ex.: `bpy.types.Object`) aparecem; acessos via variável (`obj.location`) não.",
        "",
    ]
    for top in sorted(groups, key=lambda t: -sum(len(f) for _, f in groups[t])):
        lines += [f"## {top}", "", "| Símbolo | Arquivos | Referência 5.2 |", "|---|---:|---|"]
        for sym, files in sorted(groups[top], key=lambda x: (-len(x[1]), x[0])):
            path = paths.get(sym)
            link = f"[{path.split('#')[0].removeprefix('corpus/')}](../blender-api/{path})" if path else "—"
            lines.append(f"| `{sym}` | {len(files)} | {link} |")
        lines.append("")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Map written: {out}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="*", default=[str(ROOT / "blendertomob")])
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--map", metavar="OUT.md", help="write a Markdown map: API symbol used -> count -> reference page")
    args = ap.parse_args()

    syms = load_symbols()
    prefixes = {".".join(s.split(".")[:i]) for s in syms for i in range(1, len(s.split(".")))}
    shaders = builtin_shader_names()
    ops_modules = {s.split(".")[2] for s in syms if s.startswith("bpy.ops.") and s.count(".") >= 3}

    files = []
    for p in map(Path, args.paths):
        files += sorted(p.rglob("*.py")) if p.is_dir() else [p]
    files = [f for f in files if "__pycache__" not in f.parts]

    sources = {f: f.read_text(encoding="utf-8", errors="replace") for f in files}
    custom_ops = {m for s in sources.values() for m in IDNAME_RE.findall(s)}
    custom_classes = {m for s in sources.values() for m in CLASS_RE.findall(s)}
    # Properties the add-on registers itself: bpy.types.Object.foo = PointerProperty(...)
    custom_props = {m for s in sources.values() for m in CUSTOM_PROP_RE.findall(s)}

    problems = defaultdict(list)
    used = defaultdict(set)
    for f, src in sources.items():
        rel = f.relative_to(ROOT) if f.is_relative_to(ROOT) else f
        for lineno, line in enumerate(src.splitlines(), 1):
            code = line.split("#", 1)[0]
            for ref in REF_RE.findall(code):
                ref = ref.rstrip(".")
                parts = ref.split(".")
                if ref.startswith("bpy.ops."):
                    if len(parts) < 4:
                        continue
                    op = f"{parts[2]}.{parts[3]}"
                    if op in custom_ops or parts[2] not in ops_modules:
                        continue
                    ref = ".".join(parts[:4])
                if ref.startswith("bpy.types.") and len(parts) >= 3 and parts[2] in custom_classes:
                    continue
                # Built-in UI classes (VIEW3D_MT_*, TOPBAR_MT_*...) live in Blender's Python
                # UI scripts and are not part of the reference: not verifiable here.
                if ref.startswith("bpy.types.") and UI_CLASS_RE.match(parts[2]):
                    continue
                if ".".join(parts[:4]) in custom_props:
                    continue
                if not resolve(ref, syms, prefixes):
                    problems[ref].append(f"{rel}:{lineno}")
                else:
                    used[documented_prefix(ref, syms)].add(str(rel))
            for name in BUILTIN_RE.findall(code):
                if shaders and name not in shaders:
                    problems[f"gpu.shader.from_builtin('{name}')"].append(f"{rel}:{lineno}")

    if args.map:
        write_map(Path(args.map), used, len(files))
    if args.json:
        print(json.dumps(problems, indent=1))
    else:
        print(f"Scanned {len(files)} files against {len(syms)} Blender 5.2 symbols.")
        if not problems:
            print("OK: no unknown API references found.")
        for ref, locs in sorted(problems.items()):
            print(f"\n[UNKNOWN in 5.2] {ref}  ({len(locs)}x)")
            for loc in locs[:6]:
                print(f"    {loc}")
            if len(locs) > 6:
                print(f"    ... +{len(locs) - 6}")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()

"""Manifesto do módulo salvo pelo usuário (feature 003, T002; D-10). Python puro, sem `bpy`.

Contrato: `_reversa_forward/003-modulos-agregados-reposicionar/interfaces/user-module-file.md`.
"""

import json
import re

from . import spec as spec_mod

FORMAT = "caffmob_draw.user-module"
SCHEMA_VERSION = "1.0.0"
SUPPORTED_MAJOR = 1
LIBRARIES = ('FRAMELESS', 'FACE_FRAME', 'CLOSETS', 'BTM')
_FORBIDDEN = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def file_stem(name):
    """Nome de arquivo seguro em Windows/Linux; o nome original fica no manifesto."""
    stem = _FORBIDDEN.sub("_", str(name)).strip().rstrip(".")
    return stem or "modulo"


def build(name, category, library, root_object, spec, *, created="", addon_version="", dimensions_mm=None,
          styles=None, materials=(), pulls=()):
    return {
        "format": FORMAT,
        "schema_version": SCHEMA_VERSION,
        "name": str(name),
        "category": str(category),
        "library": str(library),
        "root_object": str(root_object),
        "created": str(created),
        "addon_version": str(addon_version),
        "dimensions_mm": dict(dimensions_mm or {}),
        "styles": dict(styles or {}),
        "materials": sorted({str(m) for m in materials if m}),
        "pulls": sorted({str(p) for p in pulls if p and p != spec_mod.NO_PULL}),
        "spec": spec_mod.to_dict(spec),
    }


def _major(version):
    try:
        return int(str(version).split(".")[0])
    except ValueError:
        return None


def validate(data):
    errors = []
    if not isinstance(data, dict):
        return ["o manifesto não é um objeto JSON"]
    if data.get("format") != FORMAT:
        errors.append(f"formato desconhecido: {data.get('format')!r}")
    major = _major(data.get("schema_version", ""))
    if major is None or major > SUPPORTED_MAJOR:
        errors.append(f"schema_version {data.get('schema_version')!r} não suportada (máximo {SUPPORTED_MAJOR}.x)")
    if data.get("library") not in LIBRARIES:
        errors.append(f"biblioteca desconhecida: {data.get('library')!r}")
    if not str(data.get("name", "")).strip():
        errors.append("nome vazio")
    if not str(data.get("root_object", "")).strip():
        errors.append("objeto raiz não informado")
    if not errors:
        errors += spec_mod.validate(spec_mod.from_dict(data.get("spec")))
    return errors


def dumps(data):
    return json.dumps(data, ensure_ascii=False, indent=2, sort_keys=False) + "\n"


def loads(text):
    """Lê e valida; devolve (dados, spec, erros). Com erro, `spec` é None."""
    try:
        data = json.loads(text)
    except ValueError as exc:
        return None, None, [f"JSON inválido: {exc}"]
    errors = validate(data)
    if errors:
        return data, None, errors
    return data, spec_mod.from_dict(data.get("spec")), []

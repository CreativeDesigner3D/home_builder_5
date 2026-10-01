"""Imagens de referência do Configurador de Dimensões (T029; D-17).

Coleção `bpy.utils.previews` carregada sob demanda a partir de `assets/dimension_refs/<image_key>.png`.
Imagem ausente devolve o ícone 0 e é avisada uma única vez no console; a coleção é removida no `unregister()`.
"""

import os

import bpy.utils.previews

REFS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "dimension_refs")

_collection = None
_missing = set()


def _get_collection():
    global _collection
    if _collection is None:
        _collection = bpy.utils.previews.new()
    return _collection


def image_path(image_key):
    return os.path.join(REFS_DIR, f"{image_key}.png")


def icon_id(image_key):
    """`icon_id` da imagem de referência (para `template_icon`); 0 se a imagem não existir."""
    if not image_key:
        return 0
    pcoll = _get_collection()
    if image_key in pcoll:
        return pcoll[image_key].icon_id
    path = image_path(image_key)
    if not os.path.exists(path):
        if image_key not in _missing:
            _missing.add(image_key)
            print(f"BlenderToMob: imagem de referência ausente: {path}")
        return 0
    return pcoll.load(image_key, path, 'IMAGE').icon_id


def register():
    _get_collection()


def unregister():
    global _collection
    if _collection is not None:
        bpy.utils.previews.remove(_collection)
        _collection = None
    _missing.clear()

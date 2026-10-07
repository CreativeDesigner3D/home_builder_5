"""Salvar fechado (T069; D-28, RN-14).

`save_pre` fecha as frentes abertas para inspeção e guarda o estado em memória; `save_post` (e `save_post_fail`)
reabre como estavam, para a vista do usuário não mudar. Com `btm_settings.save_fronts_open` ligado na cena, nada é
feito nela (escolha explícita do RF-090).
"""

import bpy  # type: ignore
from bpy.app.handlers import persistent  # type: ignore

from . import fronts

_reopen = []   # (nome da cena, chave da frente, valor)


def _saves_open(scene):
    settings = getattr(scene, 'btm_settings', None)
    return settings is not None and settings.save_fronts_open


def close_for_save():
    """Fecha as frentes abertas de todas as cenas e devolve quantas foram fechadas."""
    _reopen.clear()
    seen = set()
    for scene in bpy.data.scenes:
        if _saves_open(scene):
            continue
        for front in fronts.iter_fronts(scene):
            if front.key in seen:
                continue
            seen.add(front.key)
            try:
                value = front.get()
                if front.is_open():
                    front.commit(0.0)
                    _reopen.append((scene.name, front.key, value))
            except ReferenceError:
                continue
    return len(_reopen)


def reopen_after_save():
    """Reabre o que `close_for_save` fechou. Devolve quantas frentes foram reabertas."""
    pending = list(_reopen)
    _reopen.clear()
    reopened = 0
    by_scene = {}
    for scene_name, key, value in pending:
        by_scene.setdefault(scene_name, {})[key] = value
    for scene_name, values in by_scene.items():
        scene = bpy.data.scenes.get(scene_name)
        if scene is None:
            continue
        for front in fronts.iter_fronts(scene):
            if front.key in values:
                try:
                    front.commit(values.pop(front.key))
                    reopened += 1
                except ReferenceError:
                    continue
    return reopened


@persistent
def save_pre(_filepath):
    close_for_save()


@persistent
def save_post(_filepath):
    reopen_after_save()


_HANDLERS = (
    (bpy.app.handlers.save_pre, save_pre),
    (bpy.app.handlers.save_post, save_post),
    (bpy.app.handlers.save_post_fail, save_post),
)


def register():
    for handlers, func in _HANDLERS:
        if func not in handlers:
            handlers.append(func)


def unregister():
    for handlers, func in _HANDLERS:
        while func in handlers:
            handlers.remove(func)
    _reopen.clear()

"""Sincronização Padrão de Dimensões → bibliotecas legadas (T019; D-05, D-06, D-16a; RN-23).

Grava os valores da definição nas propriedades de cena consumidas pelo frameless (`Scene.hb_frameless`) e pelo
closets (`Scene.hb_closets`), conforme `legacy_targets` do esquema, e atualiza os módulos existentes.
Medidas marcadas como editadas à mão (`btm_overrides` no objeto raiz) são preservadas, salvo `include_manual`.
"""

import json

import bpy

from ..data import dimension_schema as schema

OVERRIDES_PROP = 'btm_overrides'
LINE_PROP = 'btm_line'

FRAMELESS_TAG = 'IS_FRAMELESS_CABINET_CAGE'
CLOSET_TAG = 'IS_CLOSET_STARTER_CAGE'

# Profundidade de sincronização em andamento: escritas feitas pela sincronização não viram medida manual.
_SYNC_DEPTH = [0]


def is_syncing():
    return _SYNC_DEPTH[0] > 0


# ----------------------------------------------------------------------------------------------------------------
# Medidas editadas à mão (btm_overrides)
# ----------------------------------------------------------------------------------------------------------------

def module_root(obj):
    """Objeto raiz do módulo (gabinete frameless ou starter de closets) que contém `obj`."""
    current = obj
    while current is not None:
        if current.get(FRAMELESS_TAG) or current.get(CLOSET_TAG):
            return current
        current = current.parent
    return None


def get_overrides(obj):
    raw = obj.get(OVERRIDES_PROP)
    if not raw:
        return set()
    try:
        return set(json.loads(raw))
    except (TypeError, ValueError):
        return set()


def add_override(obj, name):
    """Marca `name` como medida editada à mão no módulo de `obj` (usado pelos diálogos de prompts)."""
    root = module_root(obj) or obj
    overrides = get_overrides(root)
    if name not in overrides:
        overrides.add(name)
        root[OVERRIDES_PROP] = json.dumps(sorted(overrides))


def clear_overrides(obj):
    root = module_root(obj) or obj
    if OVERRIDES_PROP in root:
        del root[OVERRIDES_PROP]


def make_skip(include_manual, skipped):
    """Função `skip(obj, nome)` para as rotinas de atualização; conta as medidas puladas em `skipped`."""
    def skip(obj, name):
        if include_manual:
            return False
        root = module_root(obj) or obj
        if name in get_overrides(root):
            skipped.append((root.name, name))
            return True
        return False
    return skip


# ----------------------------------------------------------------------------------------------------------------
# Contagem e escrita
# ----------------------------------------------------------------------------------------------------------------

def affected_modules(scene):
    """Módulos que a aplicação de uma definição pode alterar (para a confirmação "N módulos" — D-16a)."""
    return [obj for obj in scene.objects if obj.get(FRAMELESS_TAG) or obj.get(CLOSET_TAG)]


def _scenes_for(scene):
    from . import api
    main = api.main_scene(scene)
    scenes = [main] if main else []
    if scene is not None and scene not in scenes:
        scenes.append(scene)
    return scenes


def write_legacy_targets(scene, values):
    """Grava em `Scene.hb_frameless` / `Scene.hb_closets` (metros). Devolve a lista de destinos escritos."""
    written = []
    for key, param in schema.PARAMS.items():
        if not param.legacy_targets or key not in values:
            continue
        meters = float(values[key]) / 1000.0
        for target in param.legacy_targets:
            group_name, prop = target.split('.', 1)
            for sc in _scenes_for(scene):
                group = getattr(sc, group_name, None)
                if group is None or not hasattr(group, prop):
                    continue
                if abs(getattr(group, prop) - meters) > 1e-9:
                    setattr(group, prop, meters)
                written.append(target)
    return sorted(set(written))


def _update_frameless(context, skip):
    from ..product_libraries.frameless.operators import ops_defaults
    touched = 0
    touched += ops_defaults.update_material_thickness_prompts(context, skip)
    touched += ops_defaults.update_toe_kick_prompts(context, skip)
    touched += ops_defaults.update_cabinet_sizes(context, skip)
    return touched


def _update_closets(scene, skip):
    from ..product_libraries.closets import types_closets
    props = scene.hb_closets
    heights = {'BASE': props.base_panel_height, 'TALL': props.tall_panel_height}
    count = 0
    for root in [obj for obj in scene.objects if obj.get(CLOSET_TAG)]:
        starter = getattr(root, 'hb_closet_starter', None)
        if starter is None:
            continue
        targets = {
            'toe_kick_height': props.toe_kick_height,
            'toe_kick_setback': props.toe_kick_setback,
            'depth': props.default_panel_depth,
        }
        if starter.closet_type in heights:
            targets['height'] = heights[starter.closet_type]
        for name, value in targets.items():
            if not skip(root, name) and abs(getattr(starter, name) - value) > 1e-9:
                setattr(starter, name, value)
        # A espessura de painel/prateleira é lida da cena no recálculo.
        types_closets.recalculate_closet_starter(root)
        count += 1
    return count


def _tag_lines(scene):
    for obj in scene.objects:
        if obj.get(FRAMELESS_TAG) and not obj.get(LINE_PROP):
            obj[LINE_PROP] = 'COZ'
        elif obj.get(CLOSET_TAG) and not obj.get(LINE_PROP):
            obj[LINE_PROP] = 'DOR'


def apply_definition(scene, definition, include_manual=False, changed_keys=None):
    """Aplica a definição ao projeto. Devolve o relatório da sincronização."""
    _SYNC_DEPTH[0] += 1
    try:
        return _apply_definition(scene, definition, include_manual, changed_keys)
    finally:
        _SYNC_DEPTH[0] -= 1


def _apply_definition(scene, definition, include_manual, changed_keys):
    from . import api
    context = bpy.context
    scene = scene or context.scene
    values = api.definition_values(definition)
    targets = write_legacy_targets(scene, values)
    skipped = []
    skip = make_skip(include_manual, skipped)
    _tag_lines(scene)
    frameless_count = len([o for o in scene.objects if o.get(FRAMELESS_TAG)])
    if frameless_count and hasattr(scene, 'hb_frameless'):
        _update_frameless(context, skip)
    closets_count = _update_closets(scene, skip) if hasattr(scene, 'hb_closets') else 0
    settings = getattr(scene, 'btm_settings', None)
    if settings is not None and hasattr(settings, 'cut_plan_stale'):
        settings.cut_plan_stale = True
    keys = changed_keys if changed_keys is not None else []
    without_target = [k for k in keys if not schema.PARAMS[k].legacy_targets]
    return {
        'definition': definition.name,
        'modules_updated': frameless_count + closets_count,
        'frameless': frameless_count,
        'closets': closets_count,
        'targets_written': targets,
        'skipped_manual': skipped,
        'without_target': without_target,
    }

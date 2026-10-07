"""Adaptador de personalização do closets/roupeiros (feature 003, T035-T036; D-05 a D-09).

O estado do vão está em idprops (`hb_door_swing`, `hb_drawer_qty`, `hb_adj_shelf_qty`...) e o roupeiro inteiro é
recalculado por `recalculate_closet_starter`, que recria frentes e puxadores; estilo, puxador e material por vão são
reaplicados no fim do recálculo (gancho no próprio `recalculate_closet_starter`).
"""

import os

import bpy  # type: ignore

from .. import spec
from . import common

LIBRARY = 'CLOSETS'
DOOR_ROLE, DRAWER_ROLE = 'CLOSET_DOOR_FRONT', 'CLOSET_DRAWER_FRONT'
SWING_TO_FRONT = {'LEFT': 'DOOR_LEFT', 'RIGHT': 'DOOR_RIGHT', 'DOUBLE': 'DOUBLE_DOORS'}
FRONT_TO_CONFIG = {'DOOR_LEFT': 'DOOR_LEFT', 'DOOR_RIGHT': 'DOOR_RIGHT', 'DOUBLE_DOORS': 'DOOR_DOUBLE'}
PULL_EDGE = 0.05


def _tc():
    from ...product_libraries.closets import types_closets
    return types_closets


def capabilities(root):
    return {section: None for section in spec.SECTIONS}


def front_types(root):
    return ['DOOR_LEFT', 'DOOR_RIGHT', 'DOUBLE_DOORS', 'DRAWERS', 'OPEN']


def openings(root):
    tag = _tc().TAG_OPENING_CAGE
    return [(f"opening{i}", o) for i, o in enumerate(common.ordered([c for c in root.children_recursive
                                                                      if c.get(tag)]))]


def fronts(opening):
    return [o for o in opening.children_recursive if o.get('hb_part_role') in (DOOR_ROLE, DRAWER_ROLE)]


def pulls(front):
    return [c for c in front.children if c.get('IS_CABINET_PULL')]


def front_type(opening):
    tc = _tc()
    swing = opening.get(tc.PROP_DOOR_SWING, "")
    if swing in SWING_TO_FRONT:
        return SWING_TO_FRONT[swing], 0
    qty = int(opening.get(tc.PROP_DRAWER_QTY, 0) or 0)
    if qty:
        return 'DRAWERS', qty
    if opening.get(tc.PROP_CUBBY_COLS):
        return "", 0
    return 'OPEN', 0


def _read_interior(opening):
    asked = common.interior_of(opening)
    if asked is not None:
        return asked
    return spec.Interior(shelves=int(opening.get(_tc().PROP_ADJ_SHELF_QTY, 0) or 0))


def read(root):
    result = spec.Spec(library=LIBRARY)
    for path, opening in openings(root):
        item = result.ensure_opening(path)
        item.front, item.drawer_count = front_type(opening)
        custom = opening.btm_custom
        item.door_style, item.drawer_style = custom.door_style, custom.drawer_style
        item.pull_model, item.pull_position, item.front_material = (custom.pull_model, custom.pull_position,
                                                                    custom.front_material)
        item.interior = _read_interior(opening)
    common.read_materials(root, result, [o for o in root.children_recursive if common.is_cutpart(o)])
    result.pull_all_fronts = root.btm_custom.pull_model if root.btm_custom.pull_all_fronts else ""
    return result


def set_front(context, root, opening, front, drawer_count=1):
    tc = _tc()
    if front in FRONT_TO_CONFIG:
        config = FRONT_TO_CONFIG[front]
    elif front == 'DRAWERS':
        config = f"DRAWERS_{max(1, min(8, int(drawer_count)))}"
    elif front == 'OPEN':
        tc.clear_opening_contents(opening)
        tc.recalculate_closet_starter(root)
        return []
    else:
        return [f"O closets não tem a frente '{spec.FRONT_LABELS.get(front, front)}'"]
    return [] if tc.apply_opening_config(opening, config) else ["A biblioteca recusou a troca da frente"]


def set_interior(context, root, opening, interior):
    tc = _tc()
    messages = spec.validate_interior(interior)
    if messages:
        return messages
    opening.btm_custom.interior = spec.interior_to_json(interior)
    if interior.shelves:
        opening[tc.PROP_ADJ_SHELF_QTY] = int(interior.shelves)
    elif tc.PROP_ADJ_SHELF_QTY in opening:
        del opening[tc.PROP_ADJ_SHELF_QTY]
    if interior.dividers:
        messages.append("O closets não tem divisória vertical dentro do vão; use outro compartimento")
    if interior.drawers:
        messages.append("No closets as gavetas são frentes; troque a frente do vão para Gavetas")
    if interior.heights:
        messages.append("O closets distribui as prateleiras por igual; as alturas digitadas foram ignoradas")
    tc.recalculate_closet_starter(root)
    return messages


def style_names():
    from ...product_libraries.closets import fronts_closets
    return [identifier for identifier, _label, _d in fronts_closets.FRONT_STYLES]


def pull_items():
    from ...product_libraries.closets import pulls_closets
    return [(f, os.path.splitext(f)[0]) for f in pulls_closets.get_pull_files()]


def _pull_object(filename, warnings):
    key = "closets/" + filename
    for obj in bpy.data.objects:
        if obj.get('btm_pull_file') == key:
            return obj
    from ...product_libraries.closets import pulls_closets
    obj = pulls_closets.resolve_pull_object(filename)
    if obj is None:
        warnings.append(f"Puxador '{os.path.splitext(filename)[0]}' não encontrado")
        return None
    obj['btm_pull_file'] = key
    pulls_closets._pull_cache['selection'] = None     # o objeto é nosso; o próximo pedido da cena recarrega o dela
    pulls_closets._pull_cache['object'] = None
    return obj


def _apply_pull(front, model, position, warnings):
    current = pulls(front)
    if model == spec.NO_PULL:
        for pull in current:
            bpy.data.objects.remove(pull, do_unlink=True)
        return
    from ...product_libraries.closets import pulls_closets
    pull_obj = _pull_object(model, warnings) if model else None
    mod = common.gn_modifier(front, 'GeoNodeCutpart')
    height = common.compat.try_get_gn_input(mod, 'Width', 0.0) or 0.0     # no closets: Length = largura, Width = altura
    for pull in current:
        if pull_obj is not None:
            pull.data = pull_obj.data
            pull['hb_pull_name'] = os.path.splitext(model)[0]
        half = pulls_closets.pull_length(pull_obj or pull) / 2.0
        if position == 'TOP':
            pull.location.y = height - PULL_EDGE - half
        elif position == 'BOTTOM':
            pull.location.y = PULL_EDGE + half
        elif position == 'MIDDLE':
            pull.location.y = height / 2.0


def reapply(context, root):
    from ...product_libraries.closets import fronts_closets
    warnings = []
    root_custom = root.btm_custom
    common.apply_group_materials(root, warnings)
    for _path, opening in openings(root):
        custom = opening.btm_custom
        model = root_custom.pull_model if root_custom.pull_all_fronts else custom.pull_model
        mat = common.material(custom.front_material, warnings)
        for front in fronts(opening):
            is_drawer = front.get('hb_part_role') == DRAWER_ROLE
            style = custom.drawer_style if is_drawer else custom.door_style
            if style:
                if style in style_names():
                    fronts_closets.apply_style_to_front(front, is_drawer, style=style)
                    front['DOOR_STYLE_NAME'] = style
                else:
                    warnings.append(f"Estilo '{style}' não existe no closets")
            if model or custom.pull_position != 'DEFAULT':
                _apply_pull(front, model, custom.pull_position, warnings)
            if mat is not None and not front.btm_custom.material:
                common.set_cutpart_material(front, mat)
    return common.unique(warnings)

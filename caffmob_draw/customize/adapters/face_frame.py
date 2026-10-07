"""Adaptador de personalização do face frame (feature 003, T032-T033; D-03, D-05 a D-09).

O face frame recria frentes, puxadores e materiais a cada recálculo (`recalculate_face_frame_cabinet`); o estado do
vão está em `Object.face_frame_opening` e o estilo por frente já é guardado no vão pela própria biblioteca
(`assign_style_to_front(record_override=True)`). Puxador e material por vão são reaplicados no fim do recálculo
(gancho em `types_face_frame.recalculate_face_frame_cabinet`).
"""

import math
import os

import bpy  # type: ignore

from ... import hb_project
from .. import spec
from . import common

LIBRARY = 'FACE_FRAME'
FRONT_ROLES = ('DOOR', 'DRAWER_FRONT', 'PULLOUT_FRONT', 'FALSE_FRONT', 'TILT_OUT', 'INSET_PANEL')
DRAWER_ROLES = ('DRAWER_FRONT', 'PULLOUT_FRONT', 'TILT_OUT')
HINGE_TO_FRONT = {'LEFT': 'DOOR_LEFT', 'RIGHT': 'DOOR_RIGHT', 'DOUBLE': 'DOUBLE_DOORS', 'TOP': 'FLIP_UP',
                  'BOTTOM': 'FLIP_UP'}
FRONT_TO_HINGE = {'DOOR_LEFT': 'LEFT', 'DOOR_RIGHT': 'RIGHT', 'DOUBLE_DOORS': 'DOUBLE', 'FLIP_UP': 'TOP'}
PULL_EDGE = 0.05      # distância da borda para TOP/BOTTOM (m)


def _tff():
    from ...product_libraries.face_frame import types_face_frame
    return types_face_frame


def _props():
    return hb_project.get_main_scene().hb_face_frame


def capabilities(root):
    return {section: None for section in spec.SECTIONS}


def front_types(root):
    return list(spec.FRONT_TYPES)


def openings(root):
    tag = _tff().TAG_OPENING_CAGE
    cages = [o for o in root.children_recursive if o.get(tag)]
    leaves = [o for o in cages if not any(c.get(tag) for c in o.children_recursive)]
    return [(f"opening{i}", o) for i, o in enumerate(common.ordered(leaves))]


def fronts(opening):
    return [o for o in opening.children_recursive if o.get('hb_part_role') in FRONT_ROLES]


def pulls(front):
    return [c for c in front.children if c.get('IS_CABINET_PULL')]


def front_type(opening):
    props = opening.face_frame_opening
    kind = props.front_type
    if kind == 'DOOR':
        return HINGE_TO_FRONT.get(props.hinge_side, 'DOOR_RIGHT'), 0
    if kind in ('DRAWER_FRONT', 'PULLOUT', 'TILT_OUT'):
        return 'DRAWERS', 1
    if kind in ('FALSE_FRONT', 'INSET_PANEL'):
        return 'PANEL', 0
    if kind == 'NONE':
        return 'OPEN', 0
    return "", 0


def _read_interior(opening):
    asked = common.interior_of(opening)
    if asked is not None:
        return asked
    inner = spec.Interior()
    for item in opening.face_frame_opening.interior_items:
        if item.kind in ('ADJUSTABLE_SHELF', 'GLASS_SHELF'):
            inner.shelves += int(item.shelf_qty)
        elif item.kind == 'ROLLOUT':
            inner.drawers += int(item.qty)
    return inner


def read(root):
    result = spec.Spec(library=LIBRARY)
    for path, opening in openings(root):
        item = result.ensure_opening(path)
        item.front, item.drawer_count = front_type(opening)
        custom = opening.btm_custom
        item.door_style = custom.door_style or opening.get('hb_front_door_style', "")
        item.drawer_style = custom.drawer_style or opening.get('hb_front_drawer_style', "")
        item.pull_model, item.pull_position, item.front_material = (custom.pull_model, custom.pull_position,
                                                                    custom.front_material)
        item.interior = _read_interior(opening)
    common.read_materials(root, result, [o for o in root.children_recursive if common.is_cutpart(o)])
    result.pull_all_fronts = root.btm_custom.pull_model if root.btm_custom.pull_all_fronts else ""
    return result


# Mudanças estruturais --------------------------------------------------------------------------------------------

def set_front(context, root, opening, front, drawer_count=1):
    props = opening.face_frame_opening
    if front == 'DRAWERS' and int(drawer_count) > 1:
        count = min(int(drawer_count), 8)
        view_layer = context.view_layer
        previous = view_layer.objects.active
        view_layer.objects.active = opening
        try:
            kwargs = {f"front_type_{i}": 'DRAWER_FRONT' for i in range(count)}
            with context.temp_override(active_object=opening, object=opening):
                result = bpy.ops.caffmob_face_frame.split_opening('EXEC_DEFAULT', axis='H', count=count, **kwargs)
        finally:
            view_layer.objects.active = previous
        return [] if 'FINISHED' in result else ["A biblioteca recusou dividir o vão em gavetas"]
    if front in FRONT_TO_HINGE:
        props.hinge_side = FRONT_TO_HINGE[front]
        props.front_type = 'DOOR'
    elif front == 'DRAWERS':
        props.front_type = 'DRAWER_FRONT'
    elif front == 'PANEL':
        props.front_type = 'FALSE_FRONT'
    elif front == 'OPEN':
        props.front_type = 'NONE'
    else:
        return [f"Frente '{front}' não suportada"]
    _tff().recalculate_face_frame_cabinet(root)
    return []


def set_interior(context, root, opening, interior):
    messages = spec.validate_interior(interior)
    if messages:
        return messages
    if interior.heights:
        messages.append("O face frame distribui as prateleiras por igual; as alturas digitadas foram ignoradas")
    opening.btm_custom.interior = spec.interior_to_json(interior)
    items = opening.face_frame_opening.interior_items
    for i in reversed(range(len(items))):
        if items[i].kind in ('ADJUSTABLE_SHELF', 'GLASS_SHELF', 'ROLLOUT'):
            items.remove(i)
    if interior.shelves:
        item = items.add()
        item.kind = 'ADJUSTABLE_SHELF'
        item.unlock_shelf_qty = True
        item.shelf_qty = int(interior.shelves)
    if interior.drawers:
        item = items.add()
        item.kind = 'ROLLOUT'
        item.unlock_qty = True
        item.qty = int(interior.drawers)
    if interior.dividers:
        has_tree = any(c.get(_tff().TAG_INTERIOR_SPLIT_NODE) or c.get(_tff().TAG_INTERIOR_REGION)
                       for c in opening.children)
        if has_tree:
            messages.append("Este vão já tem divisões; edite-as pela ferramenta do face frame")
        else:
            result = bpy.ops.caffmob_face_frame.add_interior_division(target_name=opening.name)
            if 'FINISHED' not in result:
                messages.append("A biblioteca recusou a divisória")
            if int(interior.dividers) > 1:
                messages.append("O face frame cria uma divisória por vez; as demais pela ferramenta do face frame")
    _tff().recalculate_face_frame_cabinet(root)
    return messages


# Reaplicação ------------------------------------------------------------------------------------------------------

def style_names():
    props = _props()
    return sorted({s.name for s in props.door_styles} | {s.name for s in props.drawer_front_styles})


def pull_items():
    from ...product_libraries.face_frame import pulls as ffp
    items = []
    for _cat_id, folder, _desc in ffp.get_pull_categories():
        if _cat_id == 'NONE':
            continue
        items += [(f"{folder}/{filename}", stem) for filename, stem, _d in ffp.get_pulls_in_category(folder)]
    return sorted(items, key=lambda item: item[1])


def _pull_object(key, warnings):
    for obj in bpy.data.objects:
        if obj.get('btm_pull_file') == key:
            return obj
    from ...product_libraries.face_frame import pulls as ffp
    folder, _sep, filename = key.rpartition("/")
    obj = ffp.load_pull_object(filename, folder or None)
    if obj is None:
        warnings.append(f"Puxador '{os.path.splitext(filename)[0]}' não encontrado")
        return None
    obj['btm_pull_file'] = key
    return obj


def _apply_style(front, name, warnings):
    props = _props()
    pool = props.drawer_front_styles if front.get('hb_part_role') in DRAWER_ROLES else props.door_styles
    style = pool.get(name) or props.door_styles.get(name)
    if style is None:
        warnings.append(f"Estilo '{name}' não existe neste arquivo")
        return
    style.assign_style_to_front(front, record_override=True)


def _apply_pull(front, model, position, warnings):
    from ...product_libraries.face_frame import pulls as ffp
    current = pulls(front)
    if model == spec.NO_PULL:
        for pull in current:
            bpy.data.objects.remove(pull, do_unlink=True)
        return
    pull_obj = _pull_object(model, warnings) if model else None
    for pull in current:
        if pull_obj is not None:
            pull.data = pull_obj.data
        if position == 'DEFAULT':
            continue
        mod = common.gn_modifier(front, 'GeoNodeCutpart')
        length = common.compat.try_get_gn_input(mod, 'Length', 0.0) or 0.0
        half = ffp.pull_length(pull_obj or pull) / 2.0
        horizontal = abs(pull.rotation_euler.z - math.radians(90.0)) < 1e-3
        edge = 0.0 if horizontal else half
        if position == 'TOP':
            pull.location.x = length - PULL_EDGE - edge
        elif position == 'BOTTOM':
            pull.location.x = PULL_EDGE + edge
        elif position == 'MIDDLE':
            pull.location.x = length / 2.0


def reapply(context, root):
    warnings = []
    root_custom = root.btm_custom
    common.apply_group_materials(root, warnings)
    for _path, opening in openings(root):
        custom = opening.btm_custom
        model = root_custom.pull_model if root_custom.pull_all_fronts else custom.pull_model
        mat = common.material(custom.front_material, warnings)
        for front in fronts(opening):
            is_drawer = front.get('hb_part_role') in DRAWER_ROLES
            style = custom.drawer_style if is_drawer else custom.door_style
            if style and front.get('DOOR_STYLE_NAME') != style:
                _apply_style(front, style, warnings)
            if model or custom.pull_position != 'DEFAULT':
                _apply_pull(front, model, custom.pull_position, warnings)
            if mat is not None and not front.btm_custom.material:
                common.set_cutpart_material(front, mat)
    return common.unique(warnings)

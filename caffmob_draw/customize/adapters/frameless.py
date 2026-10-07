"""Adaptador de personalização do frameless (feature 003, T020-T025; D-05 a D-09).

Vãos: o vão "estável" é a gaiola `IS_FRAMELESS_OPENING_CAGE` cujo pai não é outro vão; trocar a frente
(`caffmob_frameless.change_opening_type`) recria só os filhos dele, então `btm_custom` mora nele (D-03).
O tipo atual é lido no vão mais interno (a inserção criada pela troca).
"""

import json
import os

import bpy  # type: ignore

from ... import hb_project, hb_types, hb_utils
from .. import spec
from . import common

LIBRARY = 'FRAMELESS'
OPENING_TAG = 'IS_FRAMELESS_OPENING_CAGE'
BAY_TAG = 'IS_FRAMELESS_BAY_CAGE'
INTERIOR_TAG = 'IS_FRAMELESS_INTERIOR_CAGE'
FRONT_TO_TYPE = {'DOOR_LEFT': 'LEFT_DOOR', 'DOOR_RIGHT': 'RIGHT_DOOR', 'DOUBLE_DOORS': 'DOUBLE_DOORS',
                 'FLIP_UP': 'FLIP_UP_DOOR', 'PANEL': 'FALSE_FRONT', 'OPEN': 'OPEN'}
DOOR_SWING_TO_FRONT = {0: 'DOOR_LEFT', 1: 'DOOR_RIGHT', 2: 'DOUBLE_DOORS'}
MAX_STACKED_DRAWERS = 4
ROLLOUT_SECTION_HEIGHT = 0.18     # altura reservada por gaveta interna (m)


def _props():
    return hb_project.get_main_scene().hb_frameless


# Estrutura -------------------------------------------------------------------------------------------------------

def capabilities(root):
    return {section: None for section in spec.SECTIONS}


def front_types(root):
    return list(spec.FRONT_TYPES)


def _bays(root):
    return common.ordered([c for c in root.children if c.get(BAY_TAG)])


def _stable_openings(node):
    found = []
    for child in node.children:
        if child.get(OPENING_TAG):
            found.append(child)
        else:
            found.extend(_stable_openings(child))
    return found


def openings(root):
    result = []
    for i, bay in enumerate(_bays(root)):
        for j, opening in enumerate(common.ordered(_stable_openings(bay))):
            result.append((f"bay{i}/opening{j}", opening))
    return result


def leaf_opening(opening):
    current = opening
    while True:
        inner = [c for c in current.children if c.get(OPENING_TAG)]
        if not inner:
            return current
        current = inner[0]


def fronts(opening):
    return [o for o in opening.children_recursive if o.get('IS_CABINET_FRONT')]


def pulls(front):
    return [c for c in front.children if c.get('IS_CABINET_PULL')]


def front_type(opening):
    leaf = leaf_opening(opening)
    items = fronts(leaf)
    if any(o.get('IS_FLIP_UP_DOOR') for o in items):
        return 'FLIP_UP', 0
    if 'Door Swing' in leaf and any(o.get('IS_DOOR_FRONT') for o in items):
        return DOOR_SWING_TO_FRONT.get(int(leaf['Door Swing']), 'DOUBLE_DOORS'), 0
    drawers = [o for o in items if o.get('IS_DRAWER_FRONT') or o.get('IS_PULLOUT_FRONT')]
    if drawers and all(o.get('False Front') for o in drawers):
        return 'PANEL', 0
    if drawers:
        return 'DRAWERS', len(drawers)
    return ('OPEN', 0) if not leaf.get('APPLIANCE_NAME') else ("", 0)


# Leitura ---------------------------------------------------------------------------------------------------------

def _interior_cage(opening):
    leaf = leaf_opening(opening)
    for child in leaf.children:
        if child.get(INTERIOR_TAG):
            return child
    return None


def _read_interior(opening):
    asked = common.interior_of(opening)
    if asked is not None:
        return asked
    cage = _interior_cage(opening)
    if cage is None:
        return spec.Interior()
    return spec.Interior(shelves=int(cage.get('Shelf Quantity', 0)))


def read(root):
    result = spec.Spec(library=LIBRARY)
    for path, opening in openings(root):
        item = result.ensure_opening(path)
        item.front, item.drawer_count = front_type(opening)
        custom = opening.btm_custom
        item.door_style = custom.door_style or next(
            (o.get('DOOR_STYLE_NAME', "") for o in fronts(opening) if o.get('IS_DOOR_FRONT')), "")
        item.drawer_style = custom.drawer_style
        item.pull_model, item.pull_position, item.front_material = (custom.pull_model, custom.pull_position,
                                                                    custom.front_material)
        item.interior = _read_interior(opening)
    common.read_materials(root, result, [o for o in root.children_recursive if common.is_cutpart(o)])
    result.pull_all_fronts = root.btm_custom.pull_model if root.btm_custom.pull_all_fronts else ""
    return result


# Mudanças estruturais --------------------------------------------------------------------------------------------

def set_front(context, root, opening, front, drawer_count=1):
    """Troca a frente do vão pela própria biblioteca (D-05). Devolve mensagens; vazio = ok."""
    if front == 'DRAWERS' and int(drawer_count) > 1:
        if not opening.parent or not opening.parent.get(BAY_TAG):
            return ["Mais de uma gaveta só num vão que ocupa o compartimento inteiro"]
        count = min(int(drawer_count), MAX_STACKED_DRAWERS)
        preset = 'SINGLE_DRAWER' if count == 1 else f"{count}_DRAWER_STACK"
        result = common.run_operator(context, bpy.ops.caffmob_frameless.change_bay_opening, opening.parent,
                                     opening_type=preset)
        messages = [] if 'FINISHED' in result else ["A biblioteca recusou a troca das gavetas"]
        if int(drawer_count) > MAX_STACKED_DRAWERS:
            messages.append(f"O frameless empilha no máximo {MAX_STACKED_DRAWERS} gavetas")
        return messages
    opening_type = 'SINGLE_DRAWER' if front == 'DRAWERS' else FRONT_TO_TYPE.get(front)
    if opening_type is None:
        return [f"Frente '{front}' não suportada"]
    result = common.run_operator(context, bpy.ops.caffmob_frameless.change_opening_type, opening,
                                 opening_type=opening_type)
    return [] if 'FINISHED' in result else ["A biblioteca recusou a troca da frente"]


def _remove_tree(obj):
    for child in list(obj.children):
        _remove_tree(child)
    bpy.data.objects.remove(obj, do_unlink=True)


def _attach(interior, leaf):
    cage = hb_types.GeoNodeCage(leaf)
    interior.obj.parent = leaf
    dims = [cage.var_input(name, var) for name, var in (('Dim X', 'dim_x'), ('Dim Y', 'dim_y'), ('Dim Z', 'dim_z'))]
    for (name, var), dim in zip((('Dim X', 'dim_x'), ('Dim Y', 'dim_y'), ('Dim Z', 'dim_z')), dims):
        interior.driver_input(name, var, [dim])


def set_interior(context, root, opening, interior):
    """Refaz o interior do vão (D-09); o pedido fica em `btm_custom.interior` para sobreviver a recálculos."""
    from ...product_libraries.frameless import types_frameless as tf
    leaf = leaf_opening(opening)
    height = hb_types.GeoNodeCage(leaf).get_input('Dim Z')
    messages = spec.validate_interior(interior, inner_height=height)
    if messages:
        return messages
    opening.btm_custom.interior = spec.interior_to_json(interior)
    for child in [c for c in leaf.children if c.get(INTERIOR_TAG)]:
        _remove_tree(child)
    if interior.drawers:
        splitter = tf.InteriorSplitterVertical()
        splitter.splitter_qty = 1
        drawers_height = min(height * 0.8, ROLLOUT_SECTION_HEIGHT * interior.drawers)
        splitter.section_sizes = [0, drawers_height]
        splitter.section_types = ['SHELVES' if interior.shelves else 'EMPTY', 'ROLLOUTS']
        splitter.rollout_qty = int(interior.drawers)
        splitter.create()
        _attach(splitter, leaf)
    elif interior.dividers:
        splitter = tf.InteriorSplitterHorizontal()
        splitter.splitter_qty = int(interior.dividers)
        splitter.section_types = ['SHELVES' if interior.shelves else 'EMPTY'] * (int(interior.dividers) + 1)
        splitter.create()
        _attach(splitter, leaf)
    elif interior.heights:
        splitter = tf.InteriorSplitterVertical()
        splitter.splitter_qty = len(interior.heights)
        thickness = _props().default_carcass_part_thickness
        tops = [height] + [h for h in reversed(interior.heights)]
        bottoms = [h + thickness for h in reversed(interior.heights)] + [0.0]
        splitter.section_sizes = [max(0.001, top - bottom) for top, bottom in zip(tops, bottoms)]
        splitter.section_sizes[-1] = 0         # a última seção fica com o resto (calculadora)
        splitter.section_types = ['EMPTY'] * (len(interior.heights) + 1)
        splitter.create()
        _attach(splitter, leaf)
    elif interior.shelves:
        shelves = tf.CabinetShelves()
        shelves.create('Interior')
        _attach(shelves, leaf)
        shelves.obj['Shelf Quantity'] = int(interior.shelves)
    hb_utils.run_calc_fix_until_stable(context, root)
    return []


# Reaplicação (estilo, puxador, materiais) ------------------------------------------------------------------------

def style_names():
    return [s.name for s in _props().door_styles]


def pull_items():
    from ...product_libraries.frameless import props_hb_frameless as pf
    items = []
    for category, _label, _desc in pf.get_pull_categories():
        if category == 'ALL':
            continue
        items += [(p['filename'], p['name']) for p in pf.get_pulls_in_category(category)]
    return sorted(set(items), key=lambda item: item[1])


def _pull_object(filename, warnings):
    for obj in bpy.data.objects:
        if obj.get('btm_pull_file') == filename:
            return obj
    from ...product_libraries.frameless import props_hb_frameless as pf
    obj = pf.load_pull_object(filename)
    if obj is None:
        warnings.append(f"Puxador '{os.path.splitext(filename)[0]}' não encontrado")
        return None
    obj['btm_pull_file'] = filename
    return obj


def _apply_style(front, name, warnings):
    styles = _props().door_styles
    index = styles.find(name)
    if index < 0:
        warnings.append(f"Estilo '{name}' não existe neste arquivo")
        return
    result = styles[index].assign_style_to_front(front)
    front['DOOR_STYLE_INDEX'] = index
    front['DOOR_STYLE_NAME'] = name
    if isinstance(result, str):
        warnings.append(f"{front.name}: {result}")


def _set_pull_position(front, position, length, pull_length):
    if position == 'DEFAULT':
        return
    if front.get('IS_DRAWER_FRONT') or front.get('IS_PULLOUT_FRONT'):
        if 'Center Pull' in front:
            front['Center Pull'] = position == 'MIDDLE'
        if position == 'BOTTOM' and 'Handle Horizontal Location' in front:
            front['Handle Horizontal Location'] = max(0.0, length - pull_length - 0.05)
        elif position == 'TOP' and 'Handle Horizontal Location' in front:
            front['Handle Horizontal Location'] = _props().pull_vertical_location_drawers
        return
    if 'Pull Location' not in front:
        return
    if position == 'TOP':
        front['Pull Location'] = 0
    elif position == 'BOTTOM':
        front['Pull Location'] = 2
    elif position == 'MIDDLE':
        front['Pull Location'] = 1
        front['Tall Pull Vertical Location'] = max(0.0, length / 2.0 - pull_length / 2.0)


def _apply_pull(front, model, position, warnings):
    pull_obj = None
    if model and model != spec.NO_PULL:
        pull_obj = _pull_object(model, warnings)
    for pull in pulls(front):
        mod = common.gn_modifier(pull, 'GeoNodeHardware')
        if model == spec.NO_PULL:
            common.compat.try_set_gn_input(mod, 'Object', None)
        elif pull_obj is not None:
            common.compat.try_set_gn_input(mod, 'Object', pull_obj)
    if pull_obj is not None and 'Pull Length' in front:
        front['Pull Length'] = pull_obj.dimensions.x
    length = hb_types.GeoNodeObject(front).get_input('Length') or 0.0
    _set_pull_position(front, position, length, float(front.get('Pull Length', 0.1)))


def reapply(context, root):
    """Reaplica o que está em `btm_custom` (D-04). Devolve avisos."""
    warnings = []
    root_custom = root.btm_custom
    cabinet_type = root.get('CABINET_TYPE')
    common.apply_group_materials(root, warnings, cabinet_type)
    for _path, opening in openings(root):
        custom = opening.btm_custom
        model = root_custom.pull_model if root_custom.pull_all_fronts else custom.pull_model
        mat = common.material(custom.front_material, warnings)
        for front in fronts(opening):
            is_door = bool(front.get('IS_DOOR_FRONT'))
            style = custom.door_style if is_door else custom.drawer_style
            if style:
                _apply_style(front, style, warnings)
            if model or custom.pull_position != 'DEFAULT':
                _apply_pull(front, model, custom.pull_position, warnings)
            if mat is not None and not front.btm_custom.material:
                common.set_cutpart_material(front, mat)
        asked = common.interior_of(opening)
        cage = _interior_cage(opening)
        if asked is not None and cage is not None and 'Shelf Quantity' in cage and asked.shelves:
            cage['Shelf Quantity'] = int(asked.shelves)
    hb_utils.run_calc_fix(context, root)
    return common.unique(warnings)


def describe(root):
    return json.dumps(spec.to_dict(read(root)), ensure_ascii=False)

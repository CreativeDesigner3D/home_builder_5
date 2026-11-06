"""Which bay preset a bay is built as, read from what it holds.

A bay keeps no record of the preset it was made from, and it can be
edited after: an opening split, a front changed. So the configuration
is read off the bay itself -- its tree of splits and openings, each
opening's front -- and matched against the presets of its cabinet type.
A bay that matches none is Custom.

The Inspector's bay page shows the result as a dropdown; picking another
configuration runs Change Bay.
"""

import bpy

from . import bay_presets
from . import types_face_frame


_SHELF_KINDS = ('ADJUSTABLE_SHELF', 'HALF_DEPTH_SHELF')
CUSTOM = 'CUSTOM'


# ---- Signatures -------------------------------------------------------------
# A signature is a nested tuple: ('L', front, hinge, drawer look, door
# look, door look direction, shelves) for an opening, ('S', axis,
# children) for a split. `loose` reads a single door's hinge as either
# hand, so a combo preset whose door was flipped still reads as itself.

def _hinge(front, hinge, loose):
    if front != 'DOOR':
        return ''
    if loose and hinge in ('LEFT', 'RIGHT'):
        return 'SINGLE'
    return hinge


def _leaf(front, hinge, drawer_look, door_look, door_dir, shelves, loose):
    return ('L', front, _hinge(front, hinge, loose), drawer_look, door_look,
            door_dir if door_look != 'NONE' else '',
            bool(shelves) if front == 'NONE' else False)


def _recipe_sig(recipe, loose):
    from .operators import ops_cabinet
    if recipe[0] == 'leaf':
        preset = ops_cabinet._OPENING_PRESETS.get(recipe[1])
        if preset is None:
            return None
        return _leaf(preset['front_type'], preset.get('hinge_side', ''),
                     preset.get('drawer_look', 'NONE'),
                     preset.get('door_look', 'NONE'),
                     preset.get('door_look_dir', 'ACROSS'),
                     recipe[1] == 'OPEN_WITH_SHELVES', loose)
    children = tuple(_recipe_sig(c, loose) for c in recipe[2])
    if None in children:
        return None
    return ('S', recipe[1], children)


def _nodes(obj):
    out = [c for c in obj.children
           if c.get(types_face_frame.TAG_OPENING_CAGE)
           or c.get(types_face_frame.TAG_SPLIT_NODE)]
    out.sort(key=lambda c: c.get('hb_split_child_index', 0))
    return out


def _tree_sig(obj, loose):
    if obj.get(types_face_frame.TAG_OPENING_CAGE):
        op = obj.face_frame_opening
        shelves = any(i.kind in _SHELF_KINDS for i in op.interior_items)
        return _leaf(op.front_type, op.hinge_side, op.drawer_look_divisions,
                     op.door_look_divisions, op.door_look_direction,
                     shelves, loose)
    return ('S', obj.face_frame_split.axis,
            tuple(_tree_sig(c, loose) for c in _nodes(obj)))


def _bay_sig(bay_obj, loose):
    nodes = _nodes(bay_obj)
    if len(nodes) != 1:
        return None
    return _tree_sig(nodes[0], loose)


def _bay_props_fit(bay_obj, config):
    """The bay-level construction a few presets carry (a lap drawer
    floats, a panel bay's rails follow its neighbours)."""
    bp = bay_obj.face_frame_bay
    wants = bay_presets.BAY_PROPS.get(config, {})
    for prop in ('floating_bay', 'panel_bay'):
        if bool(getattr(bp, prop, False)) != bool(wants.get(prop, False)):
            return False
    if wants.get('remove_bottom') and not bp.remove_bottom:
        return False
    if 'kick_height' in wants and abs(bp.kick_height - wants['kick_height']) > 1e-4:
        return False
    return True


# ---- Reading a bay ----------------------------------------------------------

def entries(cabinet_type):
    """(config, label) of the presets a cabinet type offers, in menu
    order, without separators."""
    return [(e[0], e[1]) for e in bay_presets.MENU_ENTRIES.get(cabinet_type, ())
            if e[0] != 'SEP']


def detect(bay_obj):
    """The preset id the bay is built as, or CUSTOM."""
    root = types_face_frame.find_cabinet_root(bay_obj)
    if root is None:
        return CUSTOM
    cabinet_type = root.face_frame_cabinet.cabinet_type
    presets = bay_presets.PRESETS.get(cabinet_type) or {}
    candidates = [c for c, _label in entries(cabinet_type) if c in presets]
    # A preset that also changes how the bay is built (a support frame
    # is an open bay with no bottom) is tried before the plain layout
    # it shares its openings with.
    candidates.sort(key=lambda c: c not in bay_presets.BAY_PROPS)
    for loose in (False, True):
        sig = _bay_sig(bay_obj, loose)
        if sig is None:
            return CUSTOM
        for config in candidates:
            recipe = (bay_presets.panel_recipe(bay_obj.face_frame_bay.width)
                      if config == 'PANEL' else presets[config])
            if (_recipe_sig(recipe, loose) == sig
                    and _bay_props_fit(bay_obj, config)):
                return config
    return CUSTOM


def label(bay_obj):
    config = detect(bay_obj)
    root = types_face_frame.find_cabinet_root(bay_obj)
    cabinet_type = root.face_frame_cabinet.cabinet_type if root else ''
    return next((l for c, l in entries(cabinet_type) if c == config),
                "Custom")


# ---- As a field -------------------------------------------------------------

def _key(cabinet_type):
    return 'FF_BAY_CONFIG_' + cabinet_type


def owner(bay_obj):
    """The bay seen as a 'config' enum: its preset, or Custom; setting
    it runs Change Bay on the selected bays."""
    from ...operators import prop_proxy
    root = types_face_frame.find_cabinet_root(bay_obj)
    if root is None:
        return None
    cabinet_type = root.face_frame_cabinet.cabinet_type
    if not bay_presets.MENU_ENTRIES.get(cabinet_type):
        return None
    key = _key(cabinet_type)
    if key not in prop_proxy._schemas:
        items = [(CUSTOM, "Custom")]
        for config, text in entries(cabinet_type):
            if config.startswith('CUSTOM_'):
                text += "…"
            items.append((config, text))

        def set_config(obj, value):
            if value == CUSTOM or value == detect(obj):
                return
            with bpy.context.temp_override(active_object=obj):
                bpy.ops.hb_face_frame.change_bay(config=value)
        prop_proxy.register(key, {
            'config': prop_proxy.computed(detect, set_config, type='ENUM',
                                          items=items),
        })
    return prop_proxy.owner(bay_obj, key)


def field_blocks(context, bay_obj):
    from ...operators import options_panel
    o = owner(bay_obj)
    if o is None:
        return []
    return options_panel.field_blocks(context, (
        ('enum', 'config', "Configuration"),
    ), o)

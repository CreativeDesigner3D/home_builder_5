"""Open Mode do face frame — atalho do modo de inspeção único (T065; D-26).

O clique para abrir/fechar portas, gavetas e pullouts passou para `btm.inspect_fronts`
(`blendertomob/inspection/ops_inspect.py`), que atende todas as linhas de produto. Este módulo mantém o `bl_idname`
legado `hb_face_frame.open_mode` (menus e atalhos existentes) e as funções que posicionam os pivôs sem recalcular o
gabinete, usadas pelo adaptador `inspection/adapters/face_frame.py`:

- `_SwingOverrideProxy`: o solver vê um `swing_percent` arbitrário sem gravar na propriedade (que recalcularia);
- `_build_tween_context(vão)`: layout, retângulo e pivôs do vão;
- `_apply_swing(ctx, valor)`: escreve as transformações dos pivôs a partir de `front_leaves`.
"""

import bpy

from .. import types_face_frame
from .. import solver_face_frame as solver


class _SwingOverrideProxy:
    """Wraps an opening_props instance so the solver sees an arbitrary
    swing value without us having to write through the real prop (which
    would trigger a full cabinet recalc on every tween tick).
    """
    __slots__ = ('_inner', '_swing')

    def __init__(self, inner, swing):
        object.__setattr__(self, '_inner', inner)
        object.__setattr__(self, '_swing', float(swing))

    def __getattr__(self, name):
        if name == 'swing_percent':
            return self._swing
        return getattr(self._inner, name)


def _find_bay_cage(opening_cage):
    cur = opening_cage.parent
    while cur is not None:
        if cur.get(types_face_frame.TAG_BAY_CAGE):
            return cur
        cur = cur.parent
    return None


def _build_tween_context(opening_cage):
    """Resolve everything we need to animate this opening's fronts.

    Returns dict with cabinet props, layout, rect, pivot list, or None
    if the opening isn't in a valid cabinet structure.
    """
    root = types_face_frame.find_cabinet_root(opening_cage)
    if root is None:
        return None
    bay = _find_bay_cage(opening_cage)
    if bay is None:
        return None
    bay_index = bay.get('hb_bay_index')
    if bay_index is None:
        return None

    layout = solver.FaceFrameLayout(root)
    parts = solver.bay_openings(layout, int(bay_index))
    rect = next((r for r in parts['leaves']
                 if r['obj_name'] == opening_cage.name), None)
    if rect is None:
        return None

    # Pivots ordered left-to-right so DOUBLE-door leaves (solver returns
    # left first, then right) line up with the children we found.
    pivots = [c for c in opening_cage.children
              if c.get('hb_part_role') == 'FRONT_PIVOT']
    if not pivots:
        return None
    pivots.sort(key=lambda p: p.location.x)

    return {
        'opening': opening_cage,
        'cab_props': root.face_frame_cabinet,
        'op_props': opening_cage.face_frame_opening,
        'layout': layout,
        'rect': rect,
        'pivots': pivots,
    }


def _apply_swing(ctx, swing_value):
    """Run the leaf solver with an overridden swing value and write the
    resulting transforms to the existing pivots. No recalc, no part
    rebuild.
    """
    proxy = _SwingOverrideProxy(ctx['op_props'], swing_value)
    leaves = solver.front_leaves(
        ctx['layout'], ctx['rect'], ctx['cab_props'], proxy
    )
    for pivot, leaf in zip(ctx['pivots'], leaves):
        pivot.location = leaf['pivot_position']
        pivot.rotation_euler = leaf['pivot_rotation']


class hb_face_frame_OT_open_mode(bpy.types.Operator):
    """Abre o modo de inspeção: clique em portas, basculantes e gavetas para abrir ou fechar. Esc sai"""
    bl_idname = "hb_face_frame.open_mode"
    bl_label = "Open Mode"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return context.area is not None and context.area.type == 'VIEW_3D'

    def invoke(self, context, event):
        return bpy.ops.btm.inspect_fronts('INVOKE_DEFAULT')

    def execute(self, context):
        return bpy.ops.btm.inspect_fronts('INVOKE_DEFAULT')


def register():
    bpy.utils.register_class(hb_face_frame_OT_open_mode)


def unregister():
    bpy.utils.unregister_class(hb_face_frame_OT_open_mode)

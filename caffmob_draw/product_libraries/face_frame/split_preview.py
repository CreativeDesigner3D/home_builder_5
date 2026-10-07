"""GPU viewport overlay that previews how split_opening will divide an
opening. While the operator's props dialog is open the overlay draws the
splitter bands - at their real mid-rail / mid-stile width - and the
resulting sub-opening outlines, recomputed live from the operator's
properties.
"""

import bpy
import gpu
from gpu_extras.batch import batch_for_shader
from mathutils import Vector

from ... import hb_utils


# Only one split dialog can be open at a time, so a single handler slot
# is enough. Module globals persist for the life of the Blender session.
_handler = None
_opening_name = ""

_SPLITTER_COLOR = (1.0, 0.55, 0.1, 0.5)   # translucent band for splitters
_OUTLINE_COLOR = (1.0, 1.0, 1.0, 0.9)     # sub-opening outline
_FACE_OFFSET = 0.003                       # nudge proud of the face (metres)


def tag_redraw(self, context):
    """Operator-property update callback. The props dialog does not
    redraw the 3D view on its own, so every VIEW_3D area is tagged when
    a previewed property changes."""
    wm = context.window_manager if context else bpy.context.window_manager
    if wm is None:
        return
    for window in wm.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()


def _child_sizes(parent_dim, splitter_width, count, sizes, unlocks):
    """Mirror FaceFrameCabinet._redistribute_split_node: children whose
    unlock flag is set hold their typed size, the rest share whatever
    span is left after the splitters and the held children."""
    n_splitters = count - 1
    held = 0.0
    flex = 0
    for i in range(count):
        if unlocks[i]:
            held += sizes[i]
        else:
            flex += 1
    remainder = parent_dim - n_splitters * splitter_width - held
    share = remainder / flex if flex else 0.0
    return [sizes[i] if unlocks[i] else share for i in range(count)]


def _cage_dims(obj):
    """Return (dim_x, dim_z) for a GeoNodeCage object, read from the
    modifier's Dim inputs. bound_box is unreliable here: a cage created
    while hidden - e.g. an opening built in Bay selection mode - is
    never depsgraph-evaluated, so its bound_box stays degenerate. The
    modifier inputs are stored values and are valid regardless."""
    for m in obj.modifiers:
        if m.type == 'NODES' and m.node_group:
            ids = {it.name: it.identifier
                   for it in m.node_group.interface.items_tree
                   if getattr(it, 'in_out', None) == 'INPUT'}
            dx = hb_utils.try_get_gn_input(m, ids.get('Dim X', ''))
            dz = hb_utils.try_get_gn_input(m, ids.get('Dim Z', ''))
            if dx is not None and dz is not None:
                return dx, dz
    # Fallback: bound box (valid once the cage has been evaluated).
    bb = obj.bound_box
    xs = [c[0] for c in bb]
    zs = [c[2] for c in bb]
    return max(xs) - min(xs), max(zs) - min(zs)


def _world_matrix(obj):
    """Reconstruct obj's world matrix for the opening cage being previewed.

    Two transforms in the chain need different treatment:

    - The opening / split-node / bay cages BELOW the cabinet root can be
      created while hidden in Bay selection mode and never get
      depsgraph-evaluated, so their own matrix_world reads as identity.
      Their matrix_basis / matrix_parent_inverse are stored values and
      stay valid, so we rebuild from those.
    - The cabinet root's placement on a wall is NOT stored in loc/rot/
      scale: HB5 walls in a chain are constraint-driven, so the wall's
      offset lives in matrix_world only. Rebuilding the whole chain from
      matrix_basis silently drops that offset and the preview lands ~2ft
      off the cabinet (the original bug this guards against).

    So: anchor on the cabinet ROOT cage's matrix_world - it is always
    visible / evaluated and already bakes in any constraint-driven wall
    placement above it - then walk back DOWN through the cage hierarchy
    using matrix_parent_inverse @ matrix_basis. Falls back to the
    topmost ancestor's matrix_world when no cabinet root is in the chain.
    """
    from . import types_face_frame
    tag_root = types_face_frame.TAG_CABINET_CAGE

    chain = []
    node = obj
    while node is not None and not node.get(tag_root):
        chain.append(node)
        node = node.parent
    if node is None:
        # No cabinet root in the chain - anchor on the topmost ancestor.
        node = obj
        chain = []
        while node.parent is not None:
            chain.append(node)
            node = node.parent

    mw = node.matrix_world.copy()
    for child in reversed(chain):
        mw = mw @ child.matrix_parent_inverse @ child.matrix_basis
    return mw


def _cage_face(obj):
    """Return (origin, x_edge, z_edge, dim_x, dim_z) for the opening
    cage's front face in world space. The cage's local geometry spans
    (0,0,0) to (Dim X, Dim Y, Dim Z); the front face is the X-Z plane
    at local Y = 0, nudged proud of the face. x_edge / z_edge are
    full-length world edge vectors."""
    dim_x, dim_z = _cage_dims(obj)
    y = -_FACE_OFFSET
    mw = _world_matrix(obj)
    origin = mw @ Vector((0.0, y, 0.0))
    x_edge = (mw @ Vector((dim_x, y, 0.0))) - origin
    z_edge = (mw @ Vector((0.0, y, dim_z))) - origin
    return origin, x_edge, z_edge, dim_x, dim_z


def _draw(op):
    """SpaceView3D POST_VIEW callback. Reads the operator's live
    properties; self-removes if the operator has been freed."""
    try:
        axis = op.axis
        count = op.count
        sizes = list(op.sizes)
        unlocks = list(op.unlocks)
        splitter_width = (op.mid_rail_width if axis == 'H'
                          else op.mid_stile_width)
    except ReferenceError:
        # Dialog closed without execute()/cancel() firing - drop the
        # handler before it can draw against a dead operator.
        remove_preview()
        return

    opening = bpy.data.objects.get(_opening_name)
    if opening is None or count < 2:
        return
    origin, x_edge, z_edge, dim_x, dim_z = _cage_face(opening)
    if dim_x <= 0.0 or dim_z <= 0.0:
        return

    parent_dim = dim_z if axis == 'H' else dim_x
    child = _child_sizes(parent_dim, splitter_width, count, sizes, unlocks)

    def face_pt(u, v):
        return origin + (u / dim_x) * x_edge + (v / dim_z) * z_edge

    def quad(lo, hi):
        # lo / hi are positions along the split axis measured from the
        # first-child edge: the top edge for H, the left edge for V.
        if axis == 'H':
            a, b = dim_z - hi, dim_z - lo
            return (face_pt(0.0, a), face_pt(dim_x, a),
                    face_pt(dim_x, b), face_pt(0.0, b))
        return (face_pt(lo, 0.0), face_pt(hi, 0.0),
                face_pt(hi, dim_z), face_pt(lo, dim_z))

    bands, outlines = [], []
    cursor = 0.0
    for i in range(count):
        outlines.append(quad(cursor, cursor + child[i]))
        cursor += child[i]
        if i < count - 1:
            bands.append(quad(cursor, cursor + splitter_width))
            cursor += splitter_width

    _render(bands, outlines)


def _render(bands, outlines):
    """Draw the splitter bands as filled translucent quads and the
    sub-openings as outlines."""
    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    gpu.state.blend_set('ALPHA')
    # Draw on top: the opening cage's front face sits ~3/4" BEHIND the
    # proud door / drawer fronts and face-frame plane, so a depth-tested
    # overlay gets occluded by those solids whenever they're shown - the
    # preview then appears only when the fronts happen to be hidden. The
    # 3mm _FACE_OFFSET nudge can't clear the fronts reliably (door/FF
    # thickness varies), so disable depth testing instead and let the
    # band/outline always paint on the face. The dialog is modal (no
    # orbit), so drawing on top reads correctly without parallax.
    gpu.state.depth_test_set('NONE')
    gpu.state.line_width_set(2.0)

    shader.uniform_float("color", _SPLITTER_COLOR)
    for q in bands:
        batch_for_shader(shader, 'TRIS', {"pos": q},
                         indices=[(0, 1, 2), (0, 2, 3)]).draw(shader)

    shader.uniform_float("color", _OUTLINE_COLOR)
    for q in outlines:
        edges = [q[0], q[1], q[1], q[2], q[2], q[3], q[3], q[0]]
        batch_for_shader(shader, 'LINES', {"pos": edges}).draw(shader)

    gpu.state.line_width_set(1.0)
    gpu.state.blend_set('NONE')


def add_preview(op, opening_name):
    """Begin drawing the split preview for `op`. Call from
    split_opening.invoke before the props dialog opens."""
    global _handler, _opening_name
    remove_preview()
    _opening_name = opening_name
    _handler = bpy.types.SpaceView3D.draw_handler_add(
        _draw, (op,), 'WINDOW', 'POST_VIEW')
    tag_redraw(op, bpy.context)


def remove_preview():
    """Stop drawing the preview. Call from split_opening.execute and
    .cancel; also called defensively by the draw callback itself."""
    global _handler, _opening_name
    if _handler is not None:
        bpy.types.SpaceView3D.draw_handler_remove(_handler, 'WINDOW')
        _handler = None
    _opening_name = ""

"""Column and beam wraps - 2-, 3- and 4-sided boxes of finished stock.

A column stands on the floor and runs vertically; a beam runs
horizontally under the ceiling. Both are the same box: a FRONT and a
BACK board carrying the run, plus a second pair closing the section -
LEFT / RIGHT on a column, BOTTOM / TOP on a beam. Any of the four can be
left off, which is what makes a 4-sided box, a 3-sided wrap against a
wall or ceiling, or a 2-sided L around an outside corner.

NOT a bay/opening product: like the mantle and the valance it is a fixed
parameterized assembly built from the cage dims plus its own propgroup.

Geometry rules
--------------
- FRONT / BACK span the full section and cover the edges of the other
  pair, so a seam falls on the side rather than on the face you look at.
- The other pair is inset in Y by one stock thickness wherever a FRONT
  or BACK board is present, and runs out to the open face where one is
  not.
- A framed side keeps its flat board as the panel and stands stiles and
  rails proud of it. Panel count divides the run, with a stile landing
  between each pair of panels.
- A false ceiling is a panel set up inside the box from its underside,
  leaving a recess for indirect lighting.

Seams, staggered seams and angled ends are order options rather than
geometry: they ride the propgroup and are published in the spec string,
so a consumer downstream can read them off the object.
"""
import math

import bpy

from ... import hb_utils
from ...units import inch
from ...hb_types import GeoNodeCutpart
from ..frameless.types_frameless import CabinetPart
from . import types_face_frame as ff


COLUMN_BEAM_TAG = 'IS_COLUMN_BEAM_PRODUCT'
COLUMN_BEAM_SPEC_KEY = 'COLUMN_BEAM_SPEC'

PART_ROLE_FRONT = 'COLUMN_BEAM_FRONT'
PART_ROLE_BACK = 'COLUMN_BEAM_BACK'
PART_ROLE_LEFT = 'COLUMN_BEAM_LEFT'
PART_ROLE_RIGHT = 'COLUMN_BEAM_RIGHT'
PART_ROLE_BOTTOM = 'COLUMN_BEAM_BOTTOM'
PART_ROLE_TOP = 'COLUMN_BEAM_TOP'
PART_ROLE_FALSE_CEILING = 'COLUMN_BEAM_FALSE_CEILING'
PART_ROLE_FRAME_MEMBER = 'COLUMN_BEAM_FRAME_MEMBER'

# Faces in the order the UI lists them: (side prop, framed prop, column
# label, beam label). LEFT / RIGHT belong to a column, BOTTOM / TOP to a
# beam; the other two are shared.
FACES = (
    ('side_front', 'framed_front', "Front", "Front"),
    ('side_back', 'framed_back', "Back", "Back"),
    ('side_left', 'framed_left', "Left", None),
    ('side_right', 'framed_right', "Right", None),
    ('side_bottom', 'framed_bottom', None, "Bottom"),
    ('side_top', 'framed_top', None, "Top"),
)


def faces_for(orientation):
    """The four faces this orientation has, front and back first."""
    column = orientation == 'COLUMN'
    label = 2 if column else 3
    out = []
    for face in FACES:
        if face[label] is None:
            continue
        out.append((face[0], face[1], face[label]))
    return out


class ColumnBeamProduct(ff.FaceFrameCabinet):
    """A column or beam wrap. ``orientation`` on the propgroup decides
    which way it runs, and therefore which pair of faces closes the
    section; everything else is shared between the two."""

    single_placement = True
    fill_no_bays = False
    follow_cursor_z = True
    default_cabinet_type = 'BASE'
    default_orientation = 'COLUMN'

    def __init__(self):
        super().__init__()
        if self.default_orientation == 'COLUMN':
            self.default_width = inch(7.0)
            self.default_depth = inch(7.0)
            self.default_height = inch(96.0)
        else:
            self.default_width = inch(96.0)    # the run
            self.default_depth = inch(7.0)
            self.default_height = inch(7.0)

    def _has_toe_kick(self):
        return False

    def _has_carcass(self):
        return False

    def create(self, name="Column", bay_qty=1):
        # bay_qty is accepted (the placement modal always passes it) and
        # ignored - a wrap has no bays.
        self.create_cabinet_root(name)
        self.obj[COLUMN_BEAM_TAG] = True
        self.obj['MENU_ID'] = 'HOME_BUILDER_MT_face_frame_column_beam_commands'
        cb = self.obj.column_beam_product
        cb.orientation = self.default_orientation
        if self.default_orientation == 'BEAM':
            # A beam wraps under the ceiling: closed below, open on top.
            cb.side_top = False
            cb.side_bottom = True
        self.recalculate()

    # -- parts ---------------------------------------------------------
    def _ensure_part(self, role, name, index=None):
        key = role if index is None else '%s:%s' % (role, index)
        for child in self.obj.children:
            if child.get('hb_part_key') == key:
                child['MENU_ID'] = 'HOME_BUILDER_MT_face_frame_part_commands'
                return child
        part = CabinetPart()
        part.create(name)
        part.obj.parent = self.obj
        part.obj['hb_part_role'] = role
        part.obj['hb_part_key'] = key
        part.obj['CABINET_PART'] = True
        part.obj['MENU_ID'] = 'HOME_BUILDER_MT_face_frame_part_commands'
        return part.obj

    def _drop_orientation_parts(self, column):
        """Remove the closing pair belonging to the other orientation.

        A wrap is built once as the cage comes up and again when the
        orientation lands, and a column switched to a beam has no use
        for its left and right boards (or the other way round), so the
        pair that no longer applies goes rather than lingering hidden.
        """
        stale = ((PART_ROLE_BOTTOM, PART_ROLE_TOP) if column
                 else (PART_ROLE_LEFT, PART_ROLE_RIGHT))
        for child in list(self.obj.children):
            if child.get('hb_part_role') in stale:
                hb_utils.delete_obj_and_children(child)

    def _drop_unused_members(self, keep):
        """Remove frame members left over from a bigger panel count or a
        side that is no longer framed."""
        for child in list(self.obj.children):
            key = child.get('hb_part_key') or ''
            if key.startswith(PART_ROLE_FRAME_MEMBER) and key not in keep:
                hb_utils.delete_obj_and_children(child)

    def _place(self, obj, length, width, thickness, loc, rot, mirror=None):
        # A Make Editable part owns its mesh and transform; leave it
        # alone, the way the other board products do.
        if obj.get('IS_MANUAL_PART'):
            return
        gn = GeoNodeCutpart(obj)
        gn.set_input('Length', length)
        gn.set_input('Width', width)
        gn.set_input('Thickness', thickness)
        obj.location = loc
        obj.rotation_euler = rot
        for key, value in (mirror or {}).items():
            gn.set_input(key, value)
        obj['IS_FINISHED'] = True

    def _show(self, obj, visible):
        if obj.get('IS_MANUAL_PART'):
            return
        obj.hide_viewport = not visible
        obj.hide_render = not visible

    # -- build ---------------------------------------------------------
    def recalculate(self):
        cab = self.obj.face_frame_cabinet
        cb = self.obj.column_beam_product

        width = cab.width
        depth = cab.depth
        height = cab.height
        self.set_input('Dim X', width)
        self.set_input('Dim Y', depth)
        self.set_input('Dim Z', height)

        t = cb.material_thickness
        column = cb.orientation == 'COLUMN'
        self._drop_orientation_parts(column)
        # Run = the length that gets ordered; the section is the other
        # two dims of the box.
        run = height if column else width
        # FRONT / BACK are the Y-extreme faces on both orientations, so
        # the closing pair insets in Y wherever one of them is present.
        y0 = -depth + (t if cb.side_front else 0.0)
        y1 = -(t if cb.side_back else 0.0)
        inner_depth = max(y1 - y0, 0.0)

        # --- FRONT / BACK: full section, thickness into the box. ---
        front = self._ensure_part(PART_ROLE_FRONT, 'Front')
        back = self._ensure_part(PART_ROLE_BACK, 'Back')
        self._place(front, width, height, t, (0.0, -depth, 0.0),
                    (math.radians(90), 0.0, 0.0),
                    {'Mirror Y': False, 'Mirror Z': True})
        self._show(front, cb.side_front)
        # Mirror Z drives which way the thickness runs (True = +Y), so
        # the back board leaves it off to grow into the box. Mirror Y
        # would flip the board end for end, not its thickness.
        self._place(back, width, height, t, (0.0, 0.0, 0.0),
                    (math.radians(90), 0.0, 0.0),
                    {'Mirror Y': False, 'Mirror Z': False})
        self._show(back, cb.side_back)

        if column:
            # LEFT / RIGHT close a column's section, floor to top.
            left = self._ensure_part(PART_ROLE_LEFT, 'Left')
            right = self._ensure_part(PART_ROLE_RIGHT, 'Right')
            self._place(left, inner_depth, height, t, (0.0, y1, 0.0),
                        (math.radians(-90), 0.0, math.radians(90)),
                        {'Mirror X': True, 'Mirror Y': True, 'Mirror Z': True})
            self._show(left, cb.side_left)
            self._place(right, inner_depth, height, t, (width, y1, 0.0),
                        (math.radians(-90), 0.0, math.radians(90)),
                        {'Mirror X': True, 'Mirror Y': True})
            self._show(right, cb.side_right)
            closing = ((cb.side_left, cb.framed_left, 'CROSS_A'),
                       (cb.side_right, cb.framed_right, 'CROSS_B'))
        else:
            # BOTTOM / TOP close a beam's section.
            bottom = self._ensure_part(PART_ROLE_BOTTOM, 'Bottom')
            top = self._ensure_part(PART_ROLE_TOP, 'Top')
            self._place(bottom, width, inner_depth, t, (0.0, y1, 0.0),
                        (0.0, 0.0, 0.0), {'Mirror Y': True})
            self._show(bottom, cb.side_bottom)
            self._place(top, width, inner_depth, t, (0.0, y1, height),
                        (0.0, 0.0, 0.0), {'Mirror Y': True, 'Mirror Z': True})
            self._show(top, cb.side_top)
            closing = ((cb.side_bottom, cb.framed_bottom, 'CROSS_A'),
                       (cb.side_top, cb.framed_top, 'CROSS_B'))

        # --- False ceiling: a panel set up inside from the underside,
        #     leaving the recess the lighting hides in. Beams only. ---
        false_ceiling = self._ensure_part(PART_ROLE_FALSE_CEILING,
                                          'False Ceiling')
        self._place(false_ceiling, width, inner_depth,
                    cb.false_ceiling_thickness,
                    (0.0, y1, cb.false_ceiling_recess),
                    (0.0, 0.0, 0.0), {'Mirror Y': True})
        self._show(false_ceiling, cb.include_false_ceiling and not column)

        # --- Framed sides. ---
        keep = set()
        for present, framed, tag in (
                (cb.side_front, cb.framed_front, 'FRONT'),
                (cb.side_back, cb.framed_back, 'BACK')) + closing:
            if not (present and framed):
                continue
            # How wide this face is, across the run: the closing pair
            # spans the gap between the front and back boards; the
            # front and back span the section's other dim.
            if tag in ('CROSS_A', 'CROSS_B'):
                across = inner_depth
            else:
                across = width if column else height
            keep |= self._build_frame(tag, run, across, cb, column,
                                      width, depth, height, t)
        self._drop_unused_members(keep)

        self._publish_spec(cb, run, width, depth, height, column)

    def _frame_origin(self, tag, cb, column, width, depth, height, t):
        """Where a framed face's members sit: (origin, rotation).

        Members stand proud of the board they frame, on the face you
        see, so the flat board behind them reads as the panel. A face on
        the closing pair starts at the inner face of the back board and
        runs forward, the same way the board it sits on does.
        """
        y1 = -(t if cb.side_back else 0.0)
        if tag == 'FRONT':
            return (0.0, -depth - t, 0.0), (math.radians(90), 0.0, 0.0)
        if tag == 'BACK':
            # The back board's outer face is the cage origin plane, so
            # its members start there and stand proud in +Y.
            return (0.0, 0.0, 0.0), (math.radians(90), 0.0, 0.0)
        if column:
            if tag == 'CROSS_A':                      # left
                return (0.0, y1, 0.0), (math.radians(-90), 0.0,
                                        math.radians(90))
            return (width, y1, 0.0), (math.radians(-90), 0.0,
                                      math.radians(90))
        if tag == 'CROSS_A':                          # beam bottom
            return (0.0, y1, 0.0), (0.0, 0.0, 0.0)
        return (0.0, y1, height), (0.0, 0.0, 0.0)

    def _build_frame(self, tag, run, across, cb, column, width, depth,
                     height, t):
        """Stand stiles and rails on one face, returning the part keys
        used so members from a bigger panel count get cleaned up.

        ``run`` is the length of the wrap and ``across`` the width of
        this face. One pair runs the length at either edge; the rest
        cross it, at both ends and between each pair of panels.
        """
        keep = set()
        # Stiles stand upright and rails cross them, so which of the two
        # follows the length of the wrap flips with the orientation: a
        # column's stiles run its length, a beam's rails do.
        lengthwise = cb.frame_stile_width if column else cb.frame_rail_width
        crosswise = cb.frame_rail_width if column else cb.frame_stile_width
        member_t = cb.frame_member_thickness
        count = max(int(cb.panel_count), 1)
        loc, rot = self._frame_origin(tag, cb, column, width, depth, height, t)

        def member(index, u, v, along, deep):
            """One frame member. ``u`` runs along the wrap, ``v`` across
            the face; ``along`` / ``deep`` are its sizes in those two
            directions."""
            key = '%s:%s' % (tag, index)
            obj = self._ensure_part(PART_ROLE_FRAME_MEMBER,
                                    '%s Frame Member' % tag.title(), key)
            keep.add('%s:%s' % (PART_ROLE_FRAME_MEMBER, key))
            if column and tag in ('CROSS_A', 'CROSS_B'):
                self._place(obj, deep, along, member_t,
                            (loc[0], loc[1] - v, loc[2] + u), rot,
                            {'Mirror X': True, 'Mirror Y': True,
                             'Mirror Z': tag == 'CROSS_B'})
            elif column:
                self._place(obj, deep, along, member_t,
                            (loc[0] + v, loc[1], loc[2] + u), rot,
                            {'Mirror Y': False, 'Mirror Z': True})
            elif tag in ('CROSS_A', 'CROSS_B'):
                self._place(obj, along, deep, member_t,
                            (loc[0] + u, loc[1] - v, loc[2]), rot,
                            {'Mirror Y': True, 'Mirror Z': tag == 'CROSS_A'})
            else:
                self._place(obj, along, deep, member_t,
                            (loc[0] + u, loc[1], loc[2] + v), rot,
                            {'Mirror Y': False, 'Mirror Z': True})

        # The pair running the length of the face, one at each edge.
        member(0, 0.0, 0.0, run, lengthwise)
        member(1, 0.0, max(across - lengthwise, 0.0), run, lengthwise)
        # The crossing members: one at each end of the run and one
        # centred on each division between panels.
        span = run / float(count)
        for i in range(count + 1):
            centred = 0 < i < count
            u = i * span - (crosswise / 2.0 if centred else 0.0)
            if i == count:
                u = run - crosswise
            u = min(max(u, 0.0), max(run - crosswise, 0.0))
            member(2 + i, u, 0.0, crosswise, across)
        return keep

    def _publish_spec(self, cb, run, width, depth, height, column):
        """Publish what was built for consumers downstream (schedules,
        drawings, order codes): sizes in inches, one flat string so it
        survives a link / append like the other product stamps."""
        sides = [name for name, present in (
            ('FRONT', cb.side_front),
            ('BACK', cb.side_back),
            ('LEFT', cb.side_left and column),
            ('RIGHT', cb.side_right and column),
            ('BOTTOM', cb.side_bottom and not column),
            ('TOP', cb.side_top and not column)) if present]
        framed = [name for name, on in (
            ('FRONT', cb.framed_front and cb.side_front),
            ('BACK', cb.framed_back and cb.side_back),
            ('LEFT', cb.framed_left and cb.side_left and column),
            ('RIGHT', cb.framed_right and cb.side_right and column),
            ('BOTTOM', cb.framed_bottom and cb.side_bottom and not column),
            ('TOP', cb.framed_top and cb.side_top and not column)) if on]
        section_w, section_d = (width, depth) if column else (depth, height)
        one_inch = inch(1.0)
        spec = (
            'kind=%s' % ('COLUMN' if column else 'BEAM'),
            'sides=%d' % len(sides),
            'faces=%s' % ('+'.join(sides) if sides else 'NONE'),
            'w=%s' % round(section_w / one_inch, 3),
            'd=%s' % round(section_d / one_inch, 3),
            'len=%s' % round(run / one_inch, 3),
            'framed=%s' % ('+'.join(framed) if framed else 'NONE'),
            'false_ceiling=%s' % ('Y' if (cb.include_false_ceiling
                                          and not column) else 'N'),
            'butt_seams=%d' % int(cb.butt_seam_sides),
            'staggered_seams=%d' % int(cb.random_staggered_sides),
            'angled_ends=%d' % (int(cb.angled_end_start)
                                + int(cb.angled_end_end)),
        )
        self.obj[COLUMN_BEAM_SPEC_KEY] = ';'.join(spec)


class ColumnProduct(ColumnBeamProduct):
    """A column: runs vertically, section is width x depth."""
    default_orientation = 'COLUMN'

    def create(self, name="Column", bay_qty=1):
        return super().create(name, bay_qty)


class BeamProduct(ColumnBeamProduct):
    """A beam: runs horizontally along X, section is depth x height."""
    default_orientation = 'BEAM'

    def create(self, name="Beam", bay_qty=1):
        return super().create(name, bay_qty)


# ---------------------------------------------------------------------------
# Dispatch (mutates the registries in types_face_frame at import)
# ---------------------------------------------------------------------------
ff.CABINET_NAME_DISPATCH.update({
    "Column": ColumnProduct,
    "Beam": BeamProduct,
})

ff.WRAP_CLASS_REGISTRY.update({
    'ColumnProduct': ColumnProduct,
    'BeamProduct': BeamProduct,
    'ColumnBeamProduct': ColumnBeamProduct,
})

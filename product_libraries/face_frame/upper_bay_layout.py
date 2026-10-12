"""Lay out a fresh upper's bays around everything under it at once.

An upper can run over a refrigerator (a bay raised onto its top, see
upper_over_refrigerator) and a range or cooktop (a bay centered on it,
see upper_over_range) on the same wall. Each module alone laid the bays
out for its own appliance; this plans them together: the upper is split
into gaps and features, left to right -- gap, feature, gap, feature,
gap -- each feature getting one bay whose opening matches it (stiles
just outside), each gap as many bays as it needs (36" at most), and a
gap too narrow for a bay of its own handing its width to the feature
beside it.

The placement preview and the drop both read the same plan, so what is
shown is what gets built.
"""

import math

from ...units import inch
from . import upper_over_refrigerator as _fridge
from . import upper_over_range as _range

MIN_OPENING = _fridge.MIN_RAISED_OPENING
MIN_SIDE_SPAN = _fridge.MIN_SIDE_SPAN
MAX_BAY_WIDTH = _fridge.MAX_BAY_WIDTH
MIN_RAISED_HEIGHT = _fridge.MIN_RAISED_HEIGHT


class Feature:
    """One appliance under the upper: its span along the wall (clipped
    to the upper) and, for a refrigerator, the top a raised bay sits
    on."""

    def __init__(self, obj, x0, x1, top=None, kind='FRIDGE'):
        self.obj, self.x0, self.x1, self.top, self.kind = obj, x0, x1, top, kind

    @property
    def raised(self):
        return self.top is not None


def features_under(wall, upper_x0, width, upper_y, upper_top):
    """The refrigerators (raised bay) and ranges / cooktops (centered
    bay) under an upper at ``upper_x0`` .. ``+width``, left to right,
    overlaps dropped."""
    upper_x1 = upper_x0 + width
    found = []
    for obj, x0, x1, top in _fridge.fridges_under(
            wall, upper_x0, upper_x1, upper_y, upper_top):
        found.append(Feature(obj, max(x0, upper_x0), min(x1, upper_x1), top,
                             'FRIDGE'))
    for obj, x0, x1, _top in _range.cooking_spots(wall, upper_y):
        if (x0 >= upper_x0 - _range.COVER_TOL
                and x1 <= upper_x1 + _range.COVER_TOL):
            found.append(Feature(obj, max(x0, upper_x0), min(x1, upper_x1),
                                 None, 'RANGE'))
    found.sort(key=lambda f: f.x0)
    out = []
    for f in found:
        if f.x1 - f.x0 < MIN_OPENING:
            continue
        if out and f.x0 < out[-1].x1 - 1e-6:
            continue                    # overlaps the one before it
        out.append(f)
    return out


def _gap_bays(gap):
    if gap < MIN_SIDE_SPAN:
        return 0
    return math.ceil(gap / MAX_BAY_WIDTH)


class Layout:
    """The plan for one upper: ``segments`` alternate ('gap', n) and
    ('feature', Feature), starting and ending with a gap."""

    def __init__(self, upper_x0, width, features):
        self.upper_x0, self.width = upper_x0, width
        self.features = features
        edges = [upper_x0] + [e for f in features for e in (f.x0, f.x1)] \
            + [upper_x0 + width]
        self.segments = []
        for i, f in enumerate(features):
            self.segments.append(('gap', _gap_bays(edges[2 * i + 1]
                                                   - edges[2 * i])))
            self.segments.append(('feature', f))
        self.segments.append(('gap', _gap_bays(edges[-1] - edges[-2])))

    @property
    def bay_count(self):
        return sum(1 if kind == 'feature' else n
                   for kind, n in self.segments)

    @property
    def has_range(self):
        return any(f.kind == 'RANGE' for f in self.features)

    def feature_bay_indices(self, kind=None):
        out, i = [], 0
        for seg, val in self.segments:
            if seg == 'feature':
                if kind is None or val.kind == kind:
                    out.append(i)
                i += 1
            else:
                i += val
        return out

    def free_bays(self):
        """The bays left to share out the width -- the last gap that has
        any -- so the widths always add up if a stile changes later."""
        i, last = 0, ()
        for seg, val in self.segments:
            if seg == 'feature':
                i += 1
            else:
                if val:
                    last = tuple(range(i, i + val))
                i += val
        return last

    def preview_bays(self):
        """[(x0, x1, feature or None)] bay spans, wall-local, without the
        stiles: what the plan builds, for drawing while placing."""
        x0, x1 = self.upper_x0, self.upper_x0 + self.width
        segs = self.segments
        out = []
        cursor = x0
        for i, (seg, val) in enumerate(segs):
            if seg == 'gap':
                if not val:
                    continue
                end = x1 if i == len(segs) - 1 else segs[i + 1][1].x0
                step = (end - cursor) / val
                for j in range(val):
                    out.append((cursor + j * step, cursor + (j + 1) * step,
                                None))
                cursor = end
            else:
                nxt = segs[i + 1][1]
                last = i + 1 == len(segs) - 1
                end = x1 if (not nxt and last) else val.x1
                out.append((cursor, end, val))
                cursor = end
        return out

    def plan(self, cab_props, upper_z):
        """[(opening_width, raised_height or None)] per bay for the
        built cabinet, or None when the stiles leave no room. Openings
        are fitted to the real stile widths, so call it once the
        cabinet's style has set them."""
        width = cab_props.width
        lsw = cab_props.left_stile_width
        rsw = cab_props.right_stile_width
        mids = [m.width for m in cab_props.mid_stile_widths]
        if len(mids) < self.bay_count - 1:
            return None
        segs = self.segments
        bays = []
        k = 0                  # mids[k] is the stile after the next bay
        cursor = lsw           # where the next bay's opening starts
        for i, (seg, val) in enumerate(segs):
            last = i == len(segs) - 1
            if seg == 'gap':
                if not val:
                    continue
                if last:
                    end = width - rsw
                    inner = mids[k:k + val - 1]
                else:
                    # The stile after the gap's last bay ends where the
                    # feature starts.
                    end = (segs[i + 1][1].x0 - self.upper_x0
                           - mids[k + val - 1])
                    inner = mids[k:k + val - 1]
                room = end - cursor - sum(inner)
                bays += [(room / val, None)] * val
                if last:
                    k += val - 1
                else:
                    k += val
                    cursor = segs[i + 1][1].x0 - self.upper_x0
            else:
                nxt_gap = segs[i + 1][1]
                to_end = not nxt_gap and i + 1 == len(segs) - 1
                end = (width - rsw) if to_end else (val.x1 - self.upper_x0)
                height = (cab_props.height - (val.top - upper_z)
                          if val.raised else None)
                bays.append((end - cursor, height))
                if not to_end:
                    cursor = end + mids[k]
                    k += 1
        if len(bays) != self.bay_count:
            return None
        if any(w < MIN_OPENING for w, _h in bays):
            return None
        if any(h is not None and h < MIN_RAISED_HEIGHT for _w, h in bays):
            return None
        return bays

    def apply(self, cab_obj, bay_plan, microwave=False):
        """Write the plan onto the built cabinet's bays (one bay keeps
        its own width), and hang the microwave under each range bay
        when asked for."""
        if self.bay_count > 1:
            if not _fridge.apply(cab_obj, bay_plan, free=self.free_bays()):
                return False
        else:
            from . import types_face_frame
            bay = next((c for c in cab_obj.children
                        if c.get(types_face_frame.TAG_BAY_CAGE)), None)
            if bay is None:
                return False
            height = bay_plan[0][1]
            if height is not None:
                bay.face_frame_bay.unlock_height = True
                bay.face_frame_bay.height = height
        if microwave:
            from . import types_face_frame
            bays = sorted(
                [c for c in cab_obj.children
                 if c.get(types_face_frame.TAG_BAY_CAGE)],
                key=lambda c: c.get('hb_bay_index', 0))
            features = [f for f in self.features]
            for idx, f in zip(self.feature_bay_indices(), features):
                if f.kind != 'RANGE' or idx >= len(bays):
                    continue
                bp = bays[idx].face_frame_bay
                bp.under_cabinet_appliance_width = f.x1 - f.x0
                bp.under_cabinet_appliance = 'MICROWAVE'
        return True


def pick(wall, upper_x0, width, upper_y, upper_top):
    """The Layout for an upper at ``upper_x0`` .. ``+width`` on ``wall``,
    or None when nothing under it needs one."""
    if wall is None or not wall.get('IS_WALL_BP'):
        return None
    features = features_under(wall, upper_x0, width, upper_y, upper_top)
    if not features:
        return None
    return Layout(upper_x0, width, features)

"""Part names for frameless cabinet and filler parts.

A part is named for the product it is in, the part it is, and how it is
finished:

    Product Type + Part Name + "Finished" + "Open"

    "Upper Left Side Finished Open", "Sink Bottom", "Base Top Open",
    "Tall Back Open"

- Product Type: Upper, Base, Sink or Tall, from the cabinet the part is in.
- Part Name: the part's own name (Left Side, Bottom, Back, Door ...).
- "Finished": a side, back, top or bottom whose outside is in the finish
  material, the condition the cabinet's finished end fields show. Under an
  applied panel the side itself is not finished.
- "Open": a side, back, top or bottom of a cabinet with a Finished
  Interior.

Fillers carry the product type too, without "Face": "Base Filler",
"Upper Filler Kick".

The board across the top front of a sink base is its "Sub Front"
("Sink Sub Front"). A "Vertical Splitter N" built as the narrow front stretcher under a
drawer is a "Drawer Stretcher N" ("Base Drawer Stretcher 1"); any other
splitter keeps its name. The object keeps its own name, which the solver
matches on - this is the displayed name only.

The Selected card shows this name for a picked part.
"""

import re

PRODUCT_TYPES = {'UPPER': "Upper", 'BASE': "Base", 'TALL': "Tall"}

# Parts whose name is set by what they are, whatever the object was
# called when it was made: the board across the top front of a sink base
# is its sub front ("Sink Sub Front"), in cabinets made before it was
# named that too.
ROLE_NAMES = {'SINK_APRON': "Sub Front"}

# Carcass parts that take "Finished" / "Open", and the side each one is.
CARCASS_SIDES = {
    'LEFT_SIDE': 'LEFT',
    'RIGHT_SIDE': 'RIGHT',
    'BACK': 'BACK',
    'TOP': 'TOP',
    'BOTTOM': 'BOTTOM',
}


def _clean(name):
    head, dot, tail = str(name or "").rpartition('.')
    if dot and tail.isdigit():
        return head.strip()
    return str(name or "").strip()


def _top_cage(obj, key):
    found = None
    o = obj.parent if obj is not None else None
    while o is not None:
        if o.get(key):
            found = o
        o = o.parent
    return found


def _type_in_name(name):
    for word in ("Upper", "Tall", "Base"):
        if word.lower() in str(name or "").lower().split():
            return word
    return None


def _is_filler(product):
    return bool(product.get('IS_CORNER_FILLER')
                or "filler" in str(product.name).lower())


def product_type(obj):
    """'Upper' / 'Base' / 'Sink' / 'Tall' for a part of a frameless
    cabinet or filler, else None."""
    cab = _top_cage(obj, 'IS_FRAMELESS_CABINET_CAGE')
    if cab is not None:
        if cab.get('IS_SINK_CABINET'):
            return "Sink"
        return PRODUCT_TYPES.get(str(cab.get('CABINET_TYPE') or "").upper())
    prod = _top_cage(obj, 'IS_FRAMELESS_PRODUCT_CAGE')
    if prod is not None and _is_filler(prod):
        return _type_in_name(prod.get('PRODUCT_NAME') or prod.name)
    return None


def _finished(cab, side):
    try:
        from .operators import ops_finished_ends
        return ops_finished_ends.finish_condition(cab, side) == 'FINISHED'
    except Exception:
        return False


def _filler_part_name(base):
    words = [w for w in base.split() if w.lower() not in ("filler", "face")]
    return " ".join(["Filler"] + words)


_SPLITTER_NAME = re.compile(r"^Vertical Splitter (\d+)$")


def _drawer_stretcher_name(obj, base):
    """'Drawer Stretcher N' for a 'Vertical Splitter N' the solver builds
    as the front stretcher under a drawer, else None."""
    m = _SPLITTER_NAME.match(base)
    splitter = obj.parent
    if m is None or splitter is None:
        return None
    try:
        from . import solver_frameless as sf
        index = obj.get(sf.SPLIT_INDEX_KEY) or int(m.group(1))
        opening = sf.split_parts(splitter).get(('OPENING', int(index)))
        if sf._drawer_stretcher_board(splitter, opening):
            return "Drawer Stretcher " + m.group(1)
    except Exception:
        pass
    return None


def part_name(obj):
    """The name for one frameless part, or None when the part is not in
    an Upper / Base / Sink / Tall cabinet or a filler."""
    if obj is None:
        return None
    ptype = product_type(obj)
    if not ptype:
        return None
    base = _clean(obj.name)
    cab = _top_cage(obj, 'IS_FRAMELESS_CABINET_CAGE')
    if cab is None:
        base = _filler_part_name(base)
    else:
        base = (ROLE_NAMES.get(obj.get('hb_part_role'))
                or _drawer_stretcher_name(obj, base) or base)
    words = base.split()
    if words and words[0].lower() == ptype.lower():
        words = words[1:]
    name = [ptype] + words
    side = CARCASS_SIDES.get(obj.get('hb_part_role')) if cab is not None else None
    if side is not None:
        if _finished(cab, side):
            name.append("Finished")
        if cab.get('Finished Interior'):
            name.append("Open")
    return " ".join(name)

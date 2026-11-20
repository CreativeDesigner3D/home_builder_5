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

The Selected card shows this name for a picked part.
"""

PRODUCT_TYPES = {'UPPER': "Upper", 'BASE': "Base", 'TALL': "Tall"}

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

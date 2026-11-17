"""Quick Actions: the commands a selected-item page leads with, laid out
the same way in every product library.

A page hands over the actions it wants shown (its own picks, or the
first commands of the item's right-click menu) and gets them back in
four sections that always come in the same order:

    Edit      change what the item is or how it is set up
    Add       put something in, beside or on it (insert, split, copy)
    Arrange   move it or share out its space (join, break, equalize)
    Remove    take it away or out of sight

so a command sits in the same place whichever library the item is from.
An action is the tuple the option pages already use for a button:
``(label, operator id or menu opener, kwargs, ...)``. Which section it
lands in is read from its label and operator, so a page never has to
say; a pair a page lists together stays together where both land in the
same section.
"""

SECTIONS = ("Edit", "Add", "Arrange", "Remove")
TITLE = "Quick Actions"
PER_ROW = 2

# Words that place an action, looked for in its label and then in its
# operator's name, as whole words ("clear", not "clearance"). A label
# that says it edits is an edit whatever its operator is called; after
# that the first section with a match takes it, and anything unmatched
# is an edit.
_EDIT_WORDS = frozenset(("edit", "change", "adjust", "prompts", "options",
                         "style", "configuration"))
_WORDS = (
    ("Remove", frozenset(("delete", "remove", "hide", "clear"))),
    ("Add", frozenset(("add", "insert", "split", "divide", "duplicate",
                       "copy", "paste", "accessory", "accessories", "new"))),
    ("Arrange", frozenset(("join", "break", "equal", "equalize", "move",
                           "align", "drop", "swap", "group", "center",
                           "flip"))),
)

_menu_cache = (None, 0.0, ())      # (key, time, actions)


def _words(text):
    return {word for word in
            "".join(c if c.isalnum() else " " for c in text.lower()).split()}


def section_of(action):
    """The section an action belongs in."""
    label = _words(str(action[0] or ""))
    op_id = action[1] if len(action) > 1 and isinstance(action[1], str) else ""
    name = _words(op_id.rsplit('.', 1)[-1])
    if label & _EDIT_WORDS:
        return "Edit"
    for words in (label, name):
        for section, known in _WORDS:
            if words & known:
                return section
    return "Edit"


def sectioned(actions):
    """``[(section, [action, ...]), ...]`` in section order, the empty
    sections left out and each section's actions in the order given."""
    found = {name: [] for name in SECTIONS}
    for action in actions:
        found[section_of(action)].append(action)
    return [(name, found[name]) for name in SECTIONS if found[name]]


def _rows(actions):
    return [tuple(actions[i:i + PER_ROW])
            for i in range(0, len(actions), PER_ROW)]


def blocks(actions, title=TITLE):
    """The actions as page blocks: the title, then each section under
    its name. Nothing for no actions."""
    out = []
    groups = sectioned(actions)
    if not groups:
        return out
    out.append(('label', title))
    for name, group in groups:
        out.append(('hint', name))
        out.extend(('actions', row) for row in _rows(group))
    return out


def fields(actions, title=TITLE):
    """The same, in the field vocabulary a page's field list is written
    in."""
    out = []
    groups = sectioned(actions)
    if not groups:
        return ()
    out.append(('label', None, title))
    for name, group in groups:
        out.append(('hints', lambda _context, name=name: (name,), None))
        out.extend(('actions', row, None) for row in _rows(group))
    return tuple(out)


def from_menu(context, menu, skip=(), limit=None):
    """The commands of a right-click menu as actions, in menu order:
    operators, sub-menus (a button that drops the list down) and enum
    pickers. ``skip`` names operators and menus to leave out; ``limit``
    stops after that many."""
    import time
    from . import generic_page
    global _menu_cache
    picked = []
    if not menu:
        return picked
    # Reading a menu means drawing it; a page is rebuilt far more often
    # than its menu changes.
    obj = context.active_object
    key = (menu, obj.name if obj else "", len(context.selected_objects),
           tuple(skip), limit)
    if (_menu_cache[0] == key and time.monotonic() - _menu_cache[1]
            < generic_page.CACHE_SECONDS):
        return list(_menu_cache[2])
    for rec in generic_page._record(context, menu):
        if rec[0] == 'op':
            if rec[2] in skip:
                continue
            label = (rec[1] or generic_page._op_label(rec[2])).rstrip('.')
            picked.append((label, rec[2], dict(rec[3]._values), None))
        elif rec[0] == 'menu':
            if rec[2] in skip:
                continue
            label = rec[1] or generic_page._menu_label(rec[2])
            picked.append((label + "  ›",
                           generic_page._opener(rec[2], label), None, None,
                           1.0, None))
        elif rec[0] == 'enum':
            if rec[2] in skip:
                continue
            label = rec[1] or generic_page._op_label(rec[2])
            picked.append((label + "  ›",
                           generic_page._enum_opener(rec[2], rec[3]),
                           None, None, 1.0, None))
        else:
            continue
        if limit is not None and len(picked) >= limit:
            break
    _menu_cache = (key, time.monotonic(), tuple(picked))
    return picked

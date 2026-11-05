"""The panel tabs as the user has arranged them.

The strip at the top left holds every tab, built-in and contributed, in
the order the add-ons give it. People work differently -- one lives in
the library, another in the drawings -- so the strip can be made theirs:

* **Order** -- drag a tab along the strip to move it. The order is
  locked until they unlock it, so a click that slides a little never
  moves a tab by accident.
* **Hidden** -- a tab they never use can come off the strip. It still
  opens itself where it would (the Tool tab while a tool runs), and
  shows while it is open so it can be closed again.
* **Coloured icons** -- Rooms, Drawings and Details in the colours the
  Rooms tab gives their lists, so the strip reads like that list.

The three dots at the end of the strip open these settings. Like the
inspector's placement they are kept for the user rather than the file,
so everyone keeps their own strip and nobody else's changes. A tab the
user has not placed yet -- a new one, or one an add-on contributes
later -- keeps its default spot beside its default neighbour.
"""

import json
import os

import bpy

_STATE_FILE = 'panel_tabs.json'

_state = None   # {'order': [keys], 'hidden': [keys], 'locked', 'colored'}


# ---- Remembered arrangement ------------------------------------------------------

def _state_path(create=False):
    from . import options_panel
    path = options_panel._state_path(create=create)
    return os.path.join(os.path.dirname(path), _STATE_FILE) if path else None


def _load():
    global _state
    if _state is None:
        _state = {'order': [], 'hidden': [], 'locked': True, 'colored': False}
        try:
            with open(_state_path(), encoding='utf-8') as fh:
                saved = json.load(fh)
            for key in ('order', 'hidden'):
                if isinstance(saved.get(key), list):
                    _state[key] = [str(k) for k in saved[key]]
            _state['locked'] = bool(saved.get('locked', True))
            _state['colored'] = bool(saved.get('colored', False))
        except Exception:
            pass            # no file yet, or one that cannot be read
    return _state


def save():
    try:
        with open(_state_path(create=True), 'w', encoding='utf-8') as fh:
            json.dump(_load(), fh, indent=1)
    except Exception as ex:
        print('Home Builder: could not save the panel tabs: %s' % ex)


def revert():
    """Drop what is not saved -- a drag called off -- by reading the
    file again."""
    global _state
    _state = None


# ---- Reading it ------------------------------------------------------------------

def arrange(default):
    """The tab keys `default` (in their default order) as the user has
    them. One they have not placed goes in after the tab it follows by
    default, or first when nothing before it is placed."""
    placed = [k for k in _load()['order'] if k in default]
    if not placed:
        return tuple(default)
    out = list(placed)
    for i, key in enumerate(default):
        if key in out:
            continue
        before = next((d for d in reversed(default[:i]) if d in out), None)
        out.insert(out.index(before) + 1 if before is not None else 0, key)
    return tuple(out)


def hidden(key):
    return key in _load()['hidden']


def locked():
    return _load()['locked']


def colored():
    return _load()['colored']


# ---- Changing it -----------------------------------------------------------------

def move(key, before_index, current):
    """Put `key` at `before_index` of `current` (the arranged keys).
    Not saved: a drag calls this as it goes and saves once, at the
    release."""
    order = [k for k in current if k != key]
    order.insert(max(0, min(before_index, len(order))), key)
    _load()['order'] = order


def step(key, delta, current):
    """Move `key` one place along the strip (-1 left, +1 right)."""
    order = list(current)
    if key not in order:
        return
    i = order.index(key)
    j = i + delta
    if 0 <= j < len(order):
        order[i], order[j] = order[j], order[i]
        _load()['order'] = order
        save()


def set_hidden(key, hide):
    keys = [k for k in _load()['hidden'] if k != key]
    if hide:
        keys.append(key)
    _load()['hidden'] = keys
    save()


def set_locked(value):
    _load()['locked'] = bool(value)
    save()


def set_colored(value):
    _load()['colored'] = bool(value)
    save()


def reset():
    _load().update(order=[], hidden=[])
    save()


# ---- The settings popup ----------------------------------------------------------

def _tag():
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()


class home_builder_OT_panel_tabs_settings(bpy.types.Operator):
    """Arrange the panel tabs: their order, which show, and their colours"""
    bl_idname = "home_builder.panel_tabs_settings"
    bl_label = "Panel Tabs"
    bl_options = {'INTERNAL'}

    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=240)

    def execute(self, context):
        return {'FINISHED'}

    def draw(self, context):
        from . import scene_navigator as nav
        layout = self.layout
        layout.label(text="Panel Tabs")
        col = layout.column(align=True)
        is_locked = locked()
        col.operator('home_builder.panel_tabs_set',
                     text="Tab Order Locked" if is_locked
                     else "Tab Order Unlocked (drag to move)",
                     icon='LOCKED' if is_locked else 'UNLOCKED',
                     depress=is_locked).action = 'LOCK'
        col.operator('home_builder.panel_tabs_set', text="Color Tab Icons",
                     icon='CHECKBOX_HLT' if colored() else 'CHECKBOX_DEHLT'
                     ).action = 'COLOR'
        layout.separator()
        keys = nav.tabs()
        box = layout.column(align=True)
        for i, key in enumerate(keys):
            row = box.row(align=True)
            shown = not hidden(key)
            op = row.operator('home_builder.panel_tabs_set', text="",
                              icon='HIDE_OFF' if shown else 'HIDE_ON',
                              emboss=False)
            op.action, op.key = 'HIDE', key
            label = row.row()
            label.enabled = shown
            label.label(text=nav.tab_label(key).title())
            up = row.row(align=True)
            up.enabled = i > 0
            op = up.operator('home_builder.panel_tabs_set', text="",
                             icon='TRIA_UP')
            op.action, op.key = 'LEFT', key
            down = row.row(align=True)
            down.enabled = i < len(keys) - 1
            op = down.operator('home_builder.panel_tabs_set', text="",
                               icon='TRIA_DOWN')
            op.action, op.key = 'RIGHT', key
        layout.label(text="Some tabs show only where they apply")
        layout.operator('home_builder.panel_tabs_set', text="Reset Order and Hidden",
                        icon='LOOP_BACK').action = 'RESET'


class home_builder_OT_panel_tabs_set(bpy.types.Operator):
    """Change how the panel tabs are arranged"""
    bl_idname = "home_builder.panel_tabs_set"
    bl_label = "Arrange Panel Tabs"
    bl_options = {'INTERNAL'}

    action: bpy.props.EnumProperty(items=(
        ('LOCK', "Lock", ""), ('COLOR', "Color", ""), ('HIDE', "Hide", ""),
        ('LEFT', "Move Up", ""), ('RIGHT', "Move Down", ""),
        ('RESET', "Reset", ""),
    ))  # type: ignore
    key: bpy.props.StringProperty()  # type: ignore

    @classmethod
    def description(cls, context, props):
        return {
            'LOCK': "Lock or unlock dragging tabs along the strip",
            'COLOR': "Color the Rooms, Drawings and Details icons like the Rooms list",
            'HIDE': "Show or hide this tab on the strip",
            'LEFT': "Move this tab one place earlier",
            'RIGHT': "Move this tab one place later",
            'RESET': "Put every tab back in its default place and show them all",
        }.get(props.action, "")

    def execute(self, context):
        from . import scene_navigator as nav
        if self.action == 'LOCK':
            set_locked(not locked())
        elif self.action == 'COLOR':
            set_colored(not colored())
        elif self.action == 'HIDE':
            set_hidden(self.key, not hidden(self.key))
        elif self.action in ('LEFT', 'RIGHT'):
            step(self.key, -1 if self.action == 'LEFT' else 1, nav.tabs())
        elif self.action == 'RESET':
            reset()
        _tag()
        return {'FINISHED'}


classes = (home_builder_OT_panel_tabs_settings,
           home_builder_OT_panel_tabs_set)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

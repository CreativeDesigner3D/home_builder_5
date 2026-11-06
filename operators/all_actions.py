"""Every command of the pick's right-click menu, in the inspector.

A product page shows the settings and the few commands reached for
most. The rest stay on the right-click menu -- and a new user does not
know it is there. ``All Actions`` opens the whole menu in the inspector
itself: read off the menu's own draw (``generic_page``), so it holds
exactly what the right-click holds, in the same order and groups, and
keeps up as the menu changes. A submenu is a button that drops its
list; a filter narrows the list as it is typed; Back returns to the
page. It closes by itself when the pick changes.
"""
import bpy

from . import generic_page, prop_proxy


SCHEMA = 'HB_ALL_ACTIONS'

_open_for = None        # name of the object the list was opened on
_filter = ""

# What the list is called, by the menu it reads.
TITLES = {
    'HOME_BUILDER_MT_face_frame_cabinet_commands': "All Cabinet Actions",
    'HOME_BUILDER_MT_face_frame_bay_commands': "All Bay Actions",
    'HOME_BUILDER_MT_face_frame_opening_commands': "All Opening Actions",
    'HOME_BUILDER_MT_face_frame_part_commands': "All Part Actions",
}


def _set_filter(_obj, value):
    global _filter
    _filter = str(value or "")


def _ensure_schema():
    if SCHEMA not in prop_proxy._schemas:
        prop_proxy.register(SCHEMA, {
            'find': prop_proxy.computed(lambda _o: _filter, _set_filter,
                                        type='STRING'),
        })


def open_list(context):
    """Show the active object's whole menu in place of its page."""
    global _open_for, _filter
    obj = context.active_object
    _open_for = obj.name if obj is not None else None
    _filter = ""
    _tag()


def close():
    global _open_for, _filter
    _open_for = None
    _filter = ""
    _tag()


def showing(context):
    """Whether the list is up for the object picked now. A new pick
    closes it."""
    global _open_for
    obj = context.active_object
    if _open_for is None:
        return False
    if obj is None or obj.name != _open_for or not obj.select_get():
        _open_for = None
        return False
    return True


def _matches(text):
    return not _filter or _filter.lower() in (text or "").lower()


def _submenu_matches(context, menu, label):
    if _matches(label):
        return True
    return any(_matches(e[0]) for e in generic_page._list_entries(context, menu)
               if e[1] is not None)


def page_blocks(context):
    obj = context.active_object
    menu = generic_page.menu_id(obj)
    title = TITLES.get(menu, "All Actions")
    _ensure_schema()
    from . import options_panel
    out = [('back', (title, close))]
    out.extend(options_panel.field_blocks(
        context, (('text', 'find', "Find"),), prop_proxy.owner(obj, SCHEMA)))
    out.append(('gap', None))
    if not menu:
        out.append(('note', "This pick has no commands."))
        return out
    shown = 0
    for rec in generic_page._record(context, menu):
        kind = rec[0]
        if kind == 'op':
            label = rec[1] or generic_page._op_label(rec[2])
            if _matches(label):
                out.append(('actions', ((label, rec[2],
                                         dict(rec[3]._values), None),)))
                shown += 1
        elif kind in ('menu', 'enum'):
            if kind == 'menu':
                label = rec[1] or generic_page._menu_label(rec[2])
                opener = generic_page._opener(rec[2], label)
                ok = _submenu_matches(context, rec[2], label)
            else:
                label = rec[1] or rec[3].replace('_', ' ').title()
                opener = generic_page._enum_opener(rec[2], rec[3])
                ok = _matches(label)
            if ok:
                out.append(('actions', ((label + "  ›", opener,
                                         None, None),)))
                shown += 1
        elif kind == 'sep' and not _filter:
            if out[-1] != ('gap', None):
                out.append(('gap', None))
        elif kind == 'label' and rec[1] and not _filter:
            out.append(('label', rec[1]))
    while out and out[-1] == ('gap', None):
        out.pop()
    if not shown:
        out.append(('note', "No action matches “%s”." % _filter))
    return out


def _tag():
    try:
        for window in bpy.context.window_manager.windows:
            for area in window.screen.areas:
                if area.type == 'VIEW_3D':
                    area.tag_redraw()
    except Exception:
        pass


class home_builder_OT_all_actions(bpy.types.Operator):
    """Show every command of the right-click menu for what is picked"""
    bl_idname = "home_builder.all_actions"
    bl_label = "All Actions"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return bool(generic_page.menu_id(context.active_object))

    def execute(self, context):
        open_list(context)
        return {'FINISHED'}


classes = (home_builder_OT_all_actions,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    close()
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

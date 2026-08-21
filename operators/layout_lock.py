"""Lock the 3D model on a layout view so only annotations select.

Drafting on a sheet means working on the dimensions and notes, not the
model behind them. Box-selecting a run of dims used to be impossible --
the marquee swept up the drawing content too -- so drafters clicked each
dim one at a time.

A layout view holds its drawing content as EMPTY objects with
``instance_type == 'COLLECTION'``. Those instancers exist only in that
view's scene, so flipping ``hide_select`` on them is naturally scoped to
the page: the model stops taking clicks and marquees there while staying
fully selectable in the room scene and on every other sheet.

The state is a scene property so it persists in the file and so the
viewport HUD button can read it. A page rebuild makes fresh instancers
with ``hide_select`` cleared, so ``apply_lock`` is re-applied by the
drawing sync after it refreshes a page.
"""

import bpy


LOCK_PROP = "hb_lock_3d_model"
LAYOUT_VIEW_TAG = "IS_LAYOUT_VIEW"


def content_instancers(scene):
    """The drawing-content collection instances on a layout view."""
    if scene is None:
        return []
    return [obj for obj in scene.objects
            if obj.type == "EMPTY" and obj.instance_type == "COLLECTION"]


def is_layout_view(scene):
    return bool(scene is not None and scene.get(LAYOUT_VIEW_TAG))


def is_locked(scene):
    return bool(scene is not None and getattr(scene, LOCK_PROP, False))


def apply_lock(scene):
    """Push the scene's lock state onto its content instancers.

    Idempotent, and safe to call on any scene -- a non-layout scene has no
    instancers to touch. Call it after a page rebuild: the fresh
    instancers come back selectable otherwise. Returns the number of
    instancers set.
    """
    if not is_layout_view(scene):
        return 0
    locked = is_locked(scene)
    touched = 0
    for obj in content_instancers(scene):
        if locked:
            # Deselect BEFORE flipping the flag: an object left selected
            # keeps its outline and rides along into the next operator,
            # which reads as the lock not working -- and deselecting an
            # already-unselectable object is not reliable.
            for view_layer in scene.view_layers:
                try:
                    obj.select_set(False, view_layer=view_layer)
                except RuntimeError:
                    pass
        obj.hide_select = locked
        touched += 1
    return touched


def _on_lock_changed(self, context):
    apply_lock(self)
    if context is not None and context.area is not None:
        context.area.tag_redraw()


class home_builder_OT_toggle_lock_3d_model(bpy.types.Operator):
    """Toggle the layout view's model lock.

    Backs the HUD button and gives the command a home in the keymap /
    search for anyone who runs with the HUD switched off.
    """

    bl_idname = "home_builder.toggle_lock_3d_model"
    bl_label = "Lock 3D Model"
    bl_description = ("Stop the 3D model taking clicks on this sheet, so "
                      "dimensions and notes can be box-selected")
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return is_layout_view(context.scene)

    def execute(self, context):
        scene = context.scene
        setattr(scene, LOCK_PROP, not is_locked(scene))
        # The property's update callback does the work; report the result
        # so the command reads the same way from search as from the HUD.
        self.report({"INFO"},
                    "3D model locked" if is_locked(scene)
                    else "3D model unlocked")
        return {"FINISHED"}


def register():
    bpy.utils.register_class(home_builder_OT_toggle_lock_3d_model)
    setattr(bpy.types.Scene, LOCK_PROP, bpy.props.BoolProperty(
        name="Lock 3D Model",
        description=("Stop the 3D model taking clicks on this sheet, so "
                     "dimensions and notes can be box-selected"),
        default=False,
        update=_on_lock_changed,
    ))


def unregister():
    if hasattr(bpy.types.Scene, LOCK_PROP):
        delattr(bpy.types.Scene, LOCK_PROP)
    bpy.utils.unregister_class(home_builder_OT_toggle_lock_3d_model)

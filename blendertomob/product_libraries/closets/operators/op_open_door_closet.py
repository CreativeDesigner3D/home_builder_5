"""Open Door do closets — atalho do modo de inspeção único (T066; D-26).

A pílula "Open Door" do overlay (modo Parts) continua chamando `hb_closets.open_door_mode` e as funções
`open_door_is_active()` / `request_open_door_exit()`; agora todas delegam a `btm.inspect_fronts`
(`blendertomob/inspection/ops_inspect.py`), que abre portas e gavetas de todas as linhas. A pose das frentes do
closets continua em `types_closets.apply_door_open` / `apply_drawer_open`, usadas pelo adaptador da inspeção.
"""
import bpy


def open_door_is_active():
    from ....inspection import ops_inspect
    return ops_inspect.inspection_running()


def request_open_door_exit():
    from ....inspection import ops_inspect
    active = ops_inspect._active
    if active is not None:
        active._exit_requested = True
        try:
            if active._exit_timer is None:
                active._exit_timer = bpy.context.window_manager.event_timer_add(
                    0.001, window=bpy.context.window)
        except (AttributeError, RuntimeError):
            pass


class hb_closets_OT_open_door_mode(bpy.types.Operator):
    """Abre o modo de inspeção: clique em uma porta ou gaveta para abrir ou fechar. Esc ou botão direito sai"""
    bl_idname = "hb_closets.open_door_mode"
    bl_label = "Open Door"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return context.area is not None and context.area.type == 'VIEW_3D'

    def invoke(self, context, event):
        return bpy.ops.btm.inspect_fronts('INVOKE_DEFAULT')

    def execute(self, context):
        return bpy.ops.btm.inspect_fronts('INVOKE_DEFAULT')


def register():
    bpy.utils.register_class(hb_closets_OT_open_door_mode)


def unregister():
    bpy.utils.unregister_class(hb_closets_OT_open_door_mode)

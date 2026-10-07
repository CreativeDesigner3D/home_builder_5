"""Plano de inserção (feature 003, T059; RF-28, RN-17, D-24).

Menu de contexto do objeto › "Usar como plano de inserção" e um clique na face: ela passa a ser o plano onde caem as inserções e os movimentos que não acertam nenhum objeto (no lugar do piso Z = 0), até
"Limpar plano de inserção". Vale para a sessão (`WindowManager.btm_insertion_plane`).
"""

import bpy  # type: ignore
from bpy_extras import view3d_utils  # type: ignore
from mathutils import Matrix, Vector  # type: ignore


def _plane_matrix(location, normal):
    normal = normal.normalized()
    rotation = normal.to_track_quat('Z', 'Y').to_matrix().to_4x4()
    return Matrix.Translation(location) @ rotation


class BTM_OT_SetInsertionPlane(bpy.types.Operator):
    """Usa a face sob o cursor como plano das próximas inserções"""
    bl_idname = "caffmob.set_insertion_plane"
    bl_label = "Usar como plano de inserção"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return context.area is not None and context.area.type == 'VIEW_3D'

    def invoke(self, context, event):
        # O clique no menu não está sobre a face: pede um clique na face (Esc/botão direito cancela).
        context.window_manager.modal_handler_add(self)
        context.workspace.status_text_set("Plano de inserção  |  Clique na face  |  Esc/botão direito: cancelar")
        context.window.cursor_set('EYEDROPPER')
        return {'RUNNING_MODAL'}

    def _end(self, context):
        context.workspace.status_text_set(None)
        context.window.cursor_set('DEFAULT')

    def modal(self, context, event):
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            region, rv3d = context.region, context.region_data
            coord = (event.mouse_region_x, event.mouse_region_y)
            origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)
            direction = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
            hit, location, normal, _index, obj, _matrix = context.scene.ray_cast(
                context.evaluated_depsgraph_get(), origin, direction)
            self._end(context)
            if not hit:
                self.report({'WARNING'}, "Nenhuma face sob o cursor")
                return {'CANCELLED'}
            return self.set_plane(context, location, normal, obj.name)
        if event.type in {'ESC', 'RIGHTMOUSE'} and event.value == 'PRESS':
            self._end(context)
            return {'CANCELLED'}
        return {'PASS_THROUGH'} if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'} \
            else {'RUNNING_MODAL'}

    def set_plane(self, context, location, normal, source):
        plane = context.window_manager.btm_insertion_plane
        plane.matrix = [v for row in _plane_matrix(Vector(location), Vector(normal)) for v in row]
        plane.source_name = source
        plane.active = True
        self.report({'INFO'}, f"Plano de inserção: face de {source}")
        return {'FINISHED'}

    def execute(self, context):
        self.report({'WARNING'}, "Use com o botão direito sobre uma face")
        return {'CANCELLED'}


class BTM_OT_ClearInsertionPlane(bpy.types.Operator):
    """Volta as inserções para o piso"""
    bl_idname = "caffmob.clear_insertion_plane"
    bl_label = "Limpar plano de inserção"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return context.window_manager.btm_insertion_plane.active

    def execute(self, context):
        context.window_manager.btm_insertion_plane.active = False
        return {'FINISHED'}


def _menu(self, context):
    layout = self.layout
    layout.separator()
    layout.operator_context = 'INVOKE_DEFAULT'
    layout.operator(BTM_OT_SetInsertionPlane.bl_idname, icon='SNAP_FACE')
    if context.window_manager.btm_insertion_plane.active:
        layout.operator(BTM_OT_ClearInsertionPlane.bl_idname, icon='X')


classes = (BTM_OT_SetInsertionPlane, BTM_OT_ClearInsertionPlane)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.VIEW3D_MT_object_context_menu.append(_menu)


def unregister():
    bpy.types.VIEW3D_MT_object_context_menu.remove(_menu)
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)

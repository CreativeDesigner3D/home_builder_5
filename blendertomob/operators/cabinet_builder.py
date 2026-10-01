import bpy  # type: ignore
from ..geometry.mesh_gen import generate_cabinet_mesh
from ..geometry import door_controller
from ..data import units


class BTM_OT_CabinetBuilder(bpy.types.Operator):
    """Cria um módulo de armário paramétrico"""
    bl_idname = "btm.cabinet_builder"
    bl_label = "Inserir Armário"
    bl_options = {'REGISTER', 'UNDO'}

    # Anotações limpas compatíveis com o linter Pyrefly
    width: bpy.props.FloatProperty(name="Largura", default=0.8, min=0.1, subtype='DISTANCE')
    height: bpy.props.FloatProperty(name="Altura", default=0.7, min=0.1, subtype='DISTANCE')
    depth: bpy.props.FloatProperty(name="Profundidade", default=0.55, min=0.1, subtype='DISTANCE')
    thickness: bpy.props.FloatProperty(name="Espessura MDF", default=0.018, min=0.006, subtype='DISTANCE')

    def invoke(self, context, event):
        # Espessura da lateral vem do Padrão de Dimensões ativo (linha Cozinha).
        if hasattr(context.scene, "btm_standards"):
            from ..standards import api
            self.thickness = api.get_value_m(context.scene, 'COZ.sheets.LAT.thickness')
        return self.execute(context)

    def execute(self, context):
        # Cria novo mesh container
        mesh = bpy.data.meshes.new(name="BTM_Cabinet_Mesh")
        obj = bpy.data.objects.new("BTM_Cabinet", mesh)

        # Vincula na coleção ativa
        context.collection.objects.link(obj)
        context.view_layer.objects.active = obj
        obj.select_set(True)

        # Define propriedades personalizadas
        obj.btm_plane.object_kind = 'MODULE'
        obj.btm_cabinet.width = self.width
        obj.btm_cabinet.height = self.height
        obj.btm_cabinet.depth = self.depth
        obj.btm_cabinet.thickness = self.thickness
        obj.btm_cabinet.door_open = 0.0
        obj.btm_cabinet.door_swing = 'LEFT' # Sentido padrão

        # Posiciona no cursor 3D
        cursor_loc = context.scene.cursor.location.copy()
        obj.location = cursor_loc

        # Gera a geometria da caixa e as portas iniciais
        generate_cabinet_mesh(obj, self.width, self.height, self.depth, self.thickness)
        door_controller.update_door_geometry_and_controller(obj)

        w_str = units.format_value(self.width, context.scene)
        h_str = units.format_value(self.height, context.scene)
        d_str = units.format_value(self.depth, context.scene)
        self.report({'INFO'}, f"Módulo de Armário inserido: {w_str} x {h_str} x {d_str}")
        return {'FINISHED'}

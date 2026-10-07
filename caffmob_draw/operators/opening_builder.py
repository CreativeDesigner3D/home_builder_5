import bpy
import gpu
import json
from gpu_extras.batch import batch_for_shader
from mathutils import Vector, Matrix
from ..geometry.mesh_gen import generate_opening_tool_mesh
from ..data import units


class BTM_OT_InsertOpening(bpy.types.Operator):
    """Insere uma abertura (porta/janela) interativa na parede com perfuração automática e snapping (escala em metros)"""
    bl_idname = "caffmob.insert_opening"
    bl_label = "Inserir Abertura"
    bl_options = {'REGISTER', 'UNDO'}

    opening_type: bpy.props.EnumProperty(
        name="Tipo",
        items=[
            ('DOOR', "Porta", "Porta de ambiente"),
            ('WINDOW', "Janela", "Janela de ambiente"),
        ],
        default='DOOR'
    )
    width: bpy.props.FloatProperty(
        name="Largura",
        default=0.8,
        min=0.1,
        max=5.0,
        subtype='DISTANCE'
    )
    height: bpy.props.FloatProperty(
        name="Altura",
        default=2.1,
        min=0.1,
        max=5.0,
        subtype='DISTANCE'
    )
    sill_height: bpy.props.FloatProperty(
        name="Peitoril",
        description="Afastamento do piso até a base (0 para portas)",
        default=0.0,
        min=0.0,
        max=5.0,
        subtype='DISTANCE'
    )

    @classmethod
    def poll(cls, context):
        return any(
            obj.btm_plane.object_kind == 'WALL'
            for obj in context.scene.objects
            if hasattr(obj, 'btm_plane')
        )

    def execute(self, context):
        # 1. Busca todas as paredes na cena
        self.wall_objs = [
            obj for obj in context.scene.objects
            if hasattr(obj, 'btm_plane') and obj.btm_plane.object_kind == 'WALL'
        ]
        if not self.wall_objs:
            self.report({'WARNING'}, "Nenhuma parede encontrada na cena para inserir a abertura.")
            return {'CANCELLED'}

        # 2. Parede padrão inicial
        active = context.active_object
        if active in self.wall_objs:
            self.target_wall = active
        else:
            self.target_wall = self.wall_objs[0]

        # 3. Cria objeto de visualização temporária (cutter)
        name_prefix = "BTM_Preview_Porta" if self.opening_type == 'DOOR' else "BTM_Preview_Janela"
        self.preview_mesh = bpy.data.meshes.new(name=f"{name_prefix}_Mesh")
        self.preview_obj = bpy.data.objects.new(name_prefix, self.preview_mesh)
        context.collection.objects.link(self.preview_obj)

        self.target_thickness = self.target_wall.btm_wall.thickness
        self.target_height = self.target_wall.btm_wall.height_start
        generate_opening_tool_mesh(self.preview_obj, self.width, self.height, self.target_thickness * 3)

        self.preview_obj.display_type = 'WIRE'
        self.preview_obj.show_bounds = True
        self.preview_obj.color = (0.2, 1.0, 0.3, 1.0) # Verde brilhante

        self.wall_t = 0.5  # meio do segmento
        self.target_seg_idx = 0

        self.sill = self.sill_height
        if self.opening_type == 'DOOR':
            self.sill = 0.0
        elif self.opening_type == 'WINDOW' and self.sill == 0.0:
            self.sill = 1.0  # Janela padrão com 1m de peitoril

        # Buffers de digitação
        self.typed_value = ""
        self.typing = False
        self.active_field = 'POSITION' # POSITION, SILL_HEIGHT

        self.ray_origin = None
        self.ray_direction = None
        self.mouse_pos_3d = None

        self.building = True
        self._draw_handler = bpy.types.SpaceView3D.draw_handler_add(
            self._draw_overlay, (context,), 'WINDOW', 'POST_VIEW'
        )

        context.window_manager.modal_handler_add(self)
        self._update_preview(context)
        self._update_header(context)

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=300)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "opening_type")
        layout.separator()

        col = layout.column(align=True)
        col.prop(self, "width")
        col.prop(self, "height")

        if self.opening_type == 'WINDOW':
            col.prop(self, "sill_height")

    def modal(self, context, event):
        context.area.tag_redraw()

        if event.type in ('ESC', 'RIGHTMOUSE') and event.value == 'PRESS':
            self._cleanup(context)
            self.report({'INFO'}, "Inserção de abertura cancelada.")
            return {'CANCELLED'}

        if event.type == 'MOUSEMOVE':
            self._update_mouse_position(context, event)
            if self.mouse_pos_3d is not None and not self.typing:
                self._update_closest_wall_segment()
                self._update_preview(context)
            self._update_header(context)

        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            self._commit_typed_value(context)
            self._confirm_insertion(context)
            return {'FINISHED'}

        if event.value == 'PRESS':
            digit_map = {
                'ZERO': '0', 'ONE': '1', 'TWO': '2', 'THREE': '3',
                'FOUR': '4', 'FIVE': '5', 'SIX': '6', 'SEVEN': '7',
                'EIGHT': '8', 'NINE': '9', 'PERIOD': '.', 'MINUS': '-',
                'NUMPAD_0': '0', 'NUMPAD_1': '1', 'NUMPAD_2': '2',
                'NUMPAD_3': '3', 'NUMPAD_4': '4', 'NUMPAD_5': '5',
                'NUMPAD_6': '6', 'NUMPAD_7': '7', 'NUMPAD_8': '8',
                'NUMPAD_9': '9', 'NUMPAD_PERIOD': '.',
            }
            if event.type in digit_map:
                self.typing = True
                self.typed_value += digit_map[event.type]
                self._update_preview(context)
                self._update_header(context)
                return {'RUNNING_MODAL'}

            if event.type == 'BACK_SPACE' and self.typed_value:
                self.typed_value = self.typed_value[:-1]
                if not self.typed_value:
                    self.typing = False
                self._update_preview(context)
                self._update_header(context)
                return {'RUNNING_MODAL'}

            if event.type == 'TAB':
                self._commit_typed_value(context)
                self.active_field = 'SILL_HEIGHT' if self.active_field == 'POSITION' else 'POSITION'
                self.typed_value = ""
                self.typing = False
                self._update_header(context)
                return {'RUNNING_MODAL'}

            if event.type in ('RET', 'NUMPAD_ENTER'):
                self._commit_typed_value(context)
                if not self.typing:
                    self._confirm_insertion(context)
                    return {'FINISHED'}
                self.typing = False
                self.typed_value = ""
                self._update_header(context)
                return {'RUNNING_MODAL'}

        return {'PASS_THROUGH'}

    # -------------------------------------------------------------------
    # Wall segment loading
    # -------------------------------------------------------------------

    def _get_wall_segments(self, wall_obj):
        """Carrega os segmentos de parede a partir dos dados do JSON (em metros)."""
        segments = []
        segments_str = wall_obj.get("btm_wall_segments", "")
        if segments_str:
            try:
                segments_data = json.loads(segments_str)
                for seg in segments_data:
                    start_local = Vector((seg['start'][0], seg['start'][1], 0.0))
                    end_local = Vector((seg['end'][0], seg['end'][1], 0.0))
                    segments.append((start_local, end_local, seg['thickness'], seg['height']))
            except Exception:
                pass

        if not segments:
            # Fallback
            length = wall_obj.btm_wall.length
            start_local = Vector((0.0, 0.0, 0.0))
            end_local = Vector((length, 0.0, 0.0))
            segments.append((start_local, end_local, wall_obj.btm_wall.thickness, wall_obj.btm_wall.height_start))

        return segments

    # -------------------------------------------------------------------
    # Snap & Slide Logic
    # -------------------------------------------------------------------

    def _distance_to_segment(self, p, a, b):
        ap = Vector((p.x - a.x, p.y - a.y, 0.0))
        ab = Vector((b.x - a.x, b.y - a.y, 0.0))
        ab_len_sq = ab.length_squared
        if ab_len_sq < 0.0001:
            return (p - a).length, 0.0
        t = ap.dot(ab) / ab_len_sq
        t = max(0.0, min(1.0, t))
        projection = a + t * ab
        dist = Vector((p.x - projection.x, p.y - projection.y, 0.0)).length
        return dist, t

    def _update_mouse_position(self, context, event):
        region = context.region
        rv3d = context.region_data
        if not region or not rv3d:
            return

        from bpy_extras.view3d_utils import region_2d_to_origin_3d, region_2d_to_vector_3d

        coord = (event.mouse_region_x, event.mouse_region_y)
        self.ray_origin = region_2d_to_origin_3d(region, rv3d, coord)
        self.ray_direction = region_2d_to_vector_3d(region, rv3d, coord)

        if abs(self.ray_direction.z) > 0.0001:
            t = -self.ray_origin.z / self.ray_direction.z
            self.mouse_pos_3d = self.ray_origin + self.ray_direction * t
        else:
            self.mouse_pos_3d = None

    def _update_closest_wall_segment(self):
        min_dist = float('inf')
        best_wall = self.target_wall
        best_seg_idx = 0
        best_t = 0.5

        for wall_obj in self.wall_objs:
            segments = self._get_wall_segments(wall_obj)
            for idx, seg in enumerate(segments):
                A = wall_obj.matrix_world @ seg[0]
                B = wall_obj.matrix_world @ seg[1]

                dist, t = self._distance_to_segment(self.mouse_pos_3d, A, B)
                if dist < min_dist:
                    min_dist = dist
                    best_wall = wall_obj
                    best_seg_idx = idx
                    best_t = t

        self.target_wall = best_wall
        self.target_seg_idx = best_seg_idx
        self.wall_t = best_t

        segments = self._get_wall_segments(best_wall)
        seg = segments[best_seg_idx]
        self.target_thickness = seg[2]
        self.target_height = seg[3]

    def _update_preview(self, context):
        if not self.preview_obj or not self.target_wall:
            return

        segments = self._get_wall_segments(self.target_wall)
        if self.target_seg_idx >= len(segments):
            return

        seg = segments[self.target_seg_idx]
        A = self.target_wall.matrix_world @ seg[0]
        B = self.target_wall.matrix_world @ seg[1]

        # Posição base na parede
        P_base = A + self.wall_t * (B - A)

        # Determina altura do peitoril via raycast vertical se não estiver digitando
        if self.ray_origin is not None and self.ray_direction is not None and not self.typing:
            dir_vec = (B - A).normalized()
            normal_vec = Vector((-dir_vec.y, dir_vec.x, 0.0)).normalized()
            denom = self.ray_direction.dot(normal_vec)
            if abs(denom) > 0.0001:
                t_ray = (A - self.ray_origin).dot(normal_vec) / denom
                P_hit = self.ray_origin + t_ray * self.ray_direction

                if self.opening_type == 'DOOR':
                    self.sill = 0.0
                else:
                    self.sill = max(0.0, min(self.target_height - self.height, P_hit.z))

        dir_vec = (B - A).normalized()
        normal_vec = Vector((-dir_vec.y, dir_vec.x, 0.0)).normalized()

        rot_mat = Matrix.Identity(3)
        rot_mat.col[0] = dir_vec
        rot_mat.col[1] = normal_vec
        rot_mat.col[2] = Vector((0.0, 0.0, 1.0))

        self.preview_obj.rotation_euler = rot_mat.to_euler()
        self.preview_obj.location = P_base + Vector((0.0, 0.0, self.sill))

        # Regenera malha do cutter
        generate_opening_tool_mesh(self.preview_obj, self.width, self.height, self.target_thickness * 3)

    # -------------------------------------------------------------------
    # Digitação de valores
    # -------------------------------------------------------------------

    def _commit_typed_value(self, context):
        if not self.typed_value:
            return

        try:
            val = float(self.typed_value)
        except ValueError:
            self.typed_value = ""
            self.typing = False
            return

        active_unit = units.get_scene_length_unit(context.scene)
        val_m = units.to_meters(val, active_unit)

        if self.active_field == 'POSITION':
            segments = self._get_wall_segments(self.target_wall)
            if self.target_seg_idx < len(segments):
                seg = segments[self.target_seg_idx]
                seg_len = (seg[1] - seg[0]).length
                self.wall_t = max(0.0, min(1.0, val_m / seg_len))
        elif self.active_field == 'SILL_HEIGHT':
            if self.opening_type == 'DOOR':
                self.sill = 0.0
            else:
                self.sill = val_m

        self.typed_value = ""
        self.typing = False

    # -------------------------------------------------------------------
    # Confirmação
    # -------------------------------------------------------------------

    def _confirm_insertion(self, context):
        name_prefix = "BTM_Porta" if self.opening_type == 'DOOR' else "BTM_Janela"
        mesh = bpy.data.meshes.new(name=f"{name_prefix}_Cut_Mesh")
        cut_obj = bpy.data.objects.new(f"{name_prefix}_Cut", mesh)

        context.collection.objects.link(cut_obj)

        generate_opening_tool_mesh(cut_obj, self.width, self.height, self.target_thickness * 3)
        cut_obj.location = self.preview_obj.location.copy()
        cut_obj.rotation_euler = self.preview_obj.rotation_euler.copy()

        cut_obj.parent = self.target_wall
        cut_obj.matrix_parent_inverse = self.target_wall.matrix_world.inverted()

        cut_obj.display_type = 'WIRE'
        cut_obj.hide_render = True

        # Metadados
        cut_obj.btm_plane.object_kind = 'OPENING'
        cut_obj.btm_plane.parent_plane = self.target_wall
        cut_obj.btm_opening.opening_type = self.opening_type
        cut_obj.btm_opening.width = self.width
        cut_obj.btm_opening.height = self.height
        cut_obj.btm_opening.sill_height = self.sill
        cut_obj.btm_opening.parent_wall = self.target_wall

        # Modificador Booleano na parede
        mod = self.target_wall.modifiers.new(
            name=f"cut_{cut_obj.name}",
            type='BOOLEAN'
        )
        mod.operation = 'DIFFERENCE'
        mod.object = cut_obj
        mod.solver = 'EXACT'

        # Ativa seleção
        context.view_layer.objects.active = cut_obj
        cut_obj.select_set(True)

        type_name = "Porta" if self.opening_type == 'DOOR' else "Janela"
        self.report({'INFO'}, f"{type_name} inserida na parede {self.target_wall.name}.")

        self._cleanup(context)

    # -------------------------------------------------------------------
    # Cleanup & UI
    # -------------------------------------------------------------------

    def _cleanup(self, context):
        self.building = False
        if self._draw_handler is not None:
            bpy.types.SpaceView3D.draw_handler_remove(self._draw_handler, 'WINDOW')
            self._draw_handler = None

        if self.preview_obj:
            bpy.data.objects.remove(self.preview_obj, do_unlink=True)
            self.preview_obj = None

        context.area.header_text_set(None)

    def _update_header(self, context):
        if not self.building:
            return

        field_labels = {
            'POSITION': 'Afastamento Inicial',
            'SILL_HEIGHT': 'Peitoril',
        }

        active_unit = units.get_scene_length_unit(context.scene)

        if self.typing:
            display_val = self.typed_value
            suffix = " m" if active_unit == 'M' else (" cm" if active_unit == 'CM' else " mm")
            display_val += suffix
        else:
            if self.active_field == 'POSITION':
                segments = self._get_wall_segments(self.target_wall)
                seg = segments[self.target_seg_idx]
                seg_len = (seg[1] - seg[0]).length
                display_val = units.format_value(self.wall_t * seg_len, context.scene)
            elif self.active_field == 'SILL_HEIGHT':
                display_val = units.format_value(self.sill, context.scene)
            else:
                display_val = "—"

        active = field_labels.get(self.active_field, '?')
        context.area.header_text_set(
            f"Adicionar Abertura ({self.opening_type})  |  "
            f"Parede: {self.target_wall.name} (Seg: {self.target_seg_idx + 1})  |  "
            f"[{active}]: {display_val}  |  "
            f"TAB: alternar campo  |  ENTER: confirmar  |  ESC/RMB: cancelar"
        )

    # -------------------------------------------------------------------
    # GPU Overlay
    # -------------------------------------------------------------------

    def _draw_overlay(self, context):
        if not self.building or not self.preview_obj or not self.target_wall:
            return

        segments = self._get_wall_segments(self.target_wall)
        if self.target_seg_idx >= len(segments):
            return

        seg = segments[self.target_seg_idx]
        A = self.target_wall.matrix_world @ seg[0]
        B = self.target_wall.matrix_world @ seg[1]

        P_door = self.preview_obj.location.copy()
        P_door.z = A.z

        dir_vec = (B - A).normalized()
        normal_vec = Vector((-dir_vec.y, dir_vec.x, 0.0)).normalized()

        offset_distance = 0.35
        A_off = A + normal_vec * offset_distance
        B_off = B + normal_vec * offset_distance
        P_off = P_door + normal_vec * offset_distance

        region = context.region
        rv3d = context.region_data
        if not region or not rv3d:
            return

        from bpy_extras.view3d_utils import location_3d_to_region_2d

        # 1. Linhas de extensão (cinza translúcido)
        gpu.state.blend_set('ALPHA')
        shader = gpu.shader.from_builtin('POLYLINE_UNIFORM_COLOR')

        ext_verts = [A, A_off, B, B_off, P_door, P_off]
        batch_ext = batch_for_shader(shader, 'LINES', {"pos": ext_verts})
        shader.bind()
        shader.uniform_float("color", (0.5, 0.5, 0.5, 0.4))
        shader.uniform_float("lineWidth", 1.0)
        shader.uniform_float("viewportSize", (region.width, region.height))
        batch_ext.draw(shader)

        # 2. Linhas de cota (ciano)
        dim_verts = [A_off, P_off, P_off, B_off]
        batch_dim = batch_for_shader(shader, 'LINES', {"pos": dim_verts})
        shader.uniform_float("color", (0.0, 0.7, 1.0, 0.8))
        shader.uniform_float("lineWidth", 2.0)
        batch_dim.draw(shader)

        # 3. Textos (Cotas)
        import blf
        font_id = 0
        blf.size(font_id, 16)

        m1 = A_off + (P_off - A_off) * 0.5
        m2 = P_off + (B_off - P_off) * 0.5

        span1 = (P_door - A).length
        span2 = (B - P_door).length

        co_2d_1 = location_3d_to_region_2d(region, rv3d, m1)
        co_2d_2 = location_3d_to_region_2d(region, rv3d, m2)

        span1_formatted = units.format_value(span1, context.scene)
        span2_formatted = units.format_value(span2, context.scene)

        # Sombra do texto
        blf.color(font_id, 0.0, 0.0, 0.0, 0.9)
        if co_2d_1:
            blf.position(font_id, co_2d_1.x + 1, co_2d_1.y - 1, 0)
            blf.draw(font_id, span1_formatted)
        if co_2d_2:
            blf.position(font_id, co_2d_2.x + 1, co_2d_2.y - 1, 0)
            blf.draw(font_id, span2_formatted)

        # Cor do texto
        blf.color(font_id, 1.0, 1.0, 1.0, 1.0)
        if co_2d_1:
            blf.position(font_id, co_2d_1.x, co_2d_1.y, 0)
            blf.draw(font_id, span1_formatted)
        if co_2d_2:
            blf.position(font_id, co_2d_2.x, co_2d_2.y, 0)
            blf.draw(font_id, span2_formatted)

        # Cota de peitoril para janelas
        if self.opening_type == 'WINDOW':
            m_sill = P_door + Vector((0.0, 0.0, self.sill / 2.0))
            co_2d_sill = location_3d_to_region_2d(region, rv3d, m_sill)
            if co_2d_sill:
                sill_formatted = f"Peitoril: {units.format_value(self.sill, context.scene)}"
                blf.color(font_id, 0.0, 0.0, 0.0, 0.9)
                blf.position(font_id, co_2d_sill.x + 1, co_2d_sill.y - 1, 0)
                blf.draw(font_id, sill_formatted)

                blf.color(font_id, 1.0, 0.8, 0.2, 1.0)
                blf.position(font_id, co_2d_sill.x, co_2d_sill.y, 0)
                blf.draw(font_id, sill_formatted)

        gpu.state.blend_set('NONE')


class BTM_OT_RemoveOpening(bpy.types.Operator):
    """Remove a abertura selecionada e seu modificador boolean da parede"""
    bl_idname = "caffmob.remove_opening"
    bl_label = "Remover Abertura"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (
            obj is not None
            and hasattr(obj, 'btm_plane')
            and obj.btm_plane.object_kind == 'OPENING'
        )

    def execute(self, context):
        cut_obj = context.active_object
        parent_wall = cut_obj.btm_opening.parent_wall

        if parent_wall and parent_wall.modifiers:
            for mod in parent_wall.modifiers:
                if mod.type == 'BOOLEAN' and mod.object == cut_obj:
                    parent_wall.modifiers.remove(mod)
                    break

        bpy.data.objects.remove(cut_obj, do_unlink=True)
        self.report({'INFO'}, "Abertura removida e parede restaurada.")
        return {'FINISHED'}

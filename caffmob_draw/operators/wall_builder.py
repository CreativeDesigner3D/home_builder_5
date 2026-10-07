import bpy
import math
import gpu
from gpu_extras.batch import batch_for_shader
from mathutils import Vector
from ..geometry.mesh_gen import generate_wall_from_segments
from ..data import units


class BTM_OT_WallBuilder(bpy.types.Operator):
    """Construtor Interativo de Paredes (Modal com suporte a metros/cm/mm e Scene Units)"""
    bl_idname = "caffmob.wall_builder"
    bl_label = "Construir Parede"
    bl_options = {'REGISTER', 'UNDO'}

    # Propriedades padrão em metros
    thickness: bpy.props.FloatProperty(name="Espessura", default=0.15, min=0.01, subtype='DISTANCE')
    height: bpy.props.FloatProperty(name="Pé-Direito", default=2.7, min=0.1, subtype='DISTANCE')
    offset: bpy.props.FloatProperty(name="Afastamento", default=0.0, min=0.0, subtype='DISTANCE')
    linear_increment: bpy.props.FloatProperty(name="Incr. Linear", default=0.05, min=0.001, subtype='DISTANCE')
    angular_increment: bpy.props.FloatProperty(name="Incr. Angular (°)", default=5.0, min=0.5)
    orientation: bpy.props.EnumProperty(
        name="Construção",
        items=[('RIGHT', "Direita", ""), ('LEFT', "Esquerda", "")],
        default='RIGHT'
    )
    wall_type: bpy.props.EnumProperty(
        name="Tipo de Parede",
        items=[
            ('NORMAL', "Normal", ""),
            ('DRYWALL', "Drywall", ""),
            ('GLASS', "Vidro", ""),
        ],
        default='NORMAL'
    )

    def invoke(self, context, event):
        # Estado do construtor de paredes modal (tudo em metros)
        self.segments = []           # Segmentos confirmados: lista de dicts
        self.current_start = None    # Ponto de início do segmento atual (Vector 2D, metros)
        self.mouse_pos_3d = None     # Posição 3D do mouse sob o piso
        self.mouse_length = 0.0      # Comprimento calculado a partir do mouse
        self.mouse_angle = 0.0       # Ângulo calculado a partir do mouse

        # Estado de digitação numérica
        self.typed_value = ""        # Buffer de digitação
        self.typing = False
        self.active_field = 'LENGTH' # LENGTH, ANGLE, THICKNESS, HEIGHT

        # Desenho
        self._draw_handler = None
        self._header_text = ""
        self.building = False

        # Limiar de fechamento de loop (0.1 metros = 10cm)
        self.close_threshold = 0.1

        # Registra overlay de preview
        self._draw_handler = bpy.types.SpaceView3D.draw_handler_add(
            self._draw_preview, (context,), 'WINDOW', 'POST_VIEW'
        )

        context.window_manager.modal_handler_add(self)
        self._update_header(context)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        context.area.tag_redraw()

        # ESC: cancela
        if event.type == 'ESC' and event.value == 'PRESS':
            self._cleanup(context)
            self.report({'INFO'}, "Construção de paredes cancelada.")
            return {'CANCELLED'}

        # MOUSEMOVE: atualiza preview
        if event.type == 'MOUSEMOVE':
            self._update_mouse_position(context, event)
            if self.building and not self.typing:
                self._compute_from_mouse()
            self._update_header(context)

        # Clique Esquerdo: inicia ou confirma segmento
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            if not self.building:
                self._update_mouse_position(context, event)
                if self.mouse_pos_3d is not None:
                    self.current_start = Vector((
                        self.mouse_pos_3d.x,
                        self.mouse_pos_3d.y
                    ))
                    self.building = True
                    self.report({'INFO'}, "Ponto inicial definido. Mova o mouse ou digite a dimensão.")
            else:
                self._commit_typed_value(context)
                self._confirm_segment(context)
            return {'RUNNING_MODAL'}

        # Clique Direito: finaliza polilinha aberta
        if event.type == 'RIGHTMOUSE' and event.value == 'PRESS':
            if self.building and self.segments:
                self._finish(context)
                return {'FINISHED'}
            elif not self.segments:
                self._cleanup(context)
                return {'CANCELLED'}

        # Digitação numérica
        if self.building and event.value == 'PRESS':
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
                self._update_header(context)
                return {'RUNNING_MODAL'}

            # Backspace
            if event.type == 'BACK_SPACE' and self.typed_value:
                self.typed_value = self.typed_value[:-1]
                if not self.typed_value:
                    self.typing = False
                self._update_header(context)
                return {'RUNNING_MODAL'}

            # TAB: rotaciona campo ativo
            if event.type == 'TAB':
                self._commit_typed_value(context)
                field_cycle = ['LENGTH', 'ANGLE', 'THICKNESS', 'HEIGHT']
                idx = field_cycle.index(self.active_field)
                self.active_field = field_cycle[(idx + 1) % len(field_cycle)]
                self.typed_value = ""
                self.typing = False
                self._update_header(context)
                return {'RUNNING_MODAL'}

            # ENTER: confirma segmento
            if event.type in ('RET', 'NUMPAD_ENTER'):
                self._commit_typed_value(context)
                self._confirm_segment(context)
                return {'RUNNING_MODAL'}

        return {'PASS_THROUGH'}

    # -------------------------------------------------------------------
    # Mouse raycasting
    # -------------------------------------------------------------------

    def _update_mouse_position(self, context, event):
        region = context.region
        rv3d = context.region_data
        if not region or not rv3d:
            return

        from bpy_extras.view3d_utils import region_2d_to_origin_3d, region_2d_to_vector_3d

        coord = (event.mouse_region_x, event.mouse_region_y)
        origin = region_2d_to_origin_3d(region, rv3d, coord)
        direction = region_2d_to_vector_3d(region, rv3d, coord)

        if abs(direction.z) > 0.0001:
            t = -origin.z / direction.z
            if t > 0:
                self.mouse_pos_3d = origin + direction * t
            else:
                self.mouse_pos_3d = None
        else:
            self.mouse_pos_3d = None

    def _compute_from_mouse(self):
        if self.mouse_pos_3d is None or self.current_start is None:
            return

        mouse_m = Vector((self.mouse_pos_3d.x, self.mouse_pos_3d.y))
        delta = mouse_m - self.current_start

        raw_length = delta.length
        raw_angle = math.degrees(math.atan2(delta.y, delta.x))

        # Incremento linear (em metros)
        inc_l = self.linear_increment
        if inc_l > 0:
            self.mouse_length = round(raw_length / inc_l) * inc_l
        else:
            self.mouse_length = raw_length

        # Incremento angular
        inc_a = self.angular_increment
        if inc_a > 0:
            self.mouse_angle = round(raw_angle / inc_a) * inc_a
        else:
            self.mouse_angle = raw_angle

    # -------------------------------------------------------------------
    # Digitação de Valores
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

        # O valor digitado é interpretado de acordo com a unidade da cena
        # Se for comprimento, espessura ou altura, converte da unidade ativa para metros
        active_unit = units.get_scene_length_unit(context.scene)

        if self.active_field == 'LENGTH':
            self.mouse_length = units.to_meters(val, active_unit)
        elif self.active_field == 'ANGLE':
            self.mouse_angle = val
        elif self.active_field == 'THICKNESS':
            self.thickness = units.to_meters(val, active_unit)
        elif self.active_field == 'HEIGHT':
            self.height = units.to_meters(val, active_unit)

        self.typed_value = ""
        self.typing = False

    # -------------------------------------------------------------------
    # Confirmação de Segmento
    # -------------------------------------------------------------------

    def _get_current_end_point(self):
        if self.current_start is None:
            return None

        angle_rad = math.radians(self.mouse_angle)
        length = self.mouse_length if self.mouse_length > 0 else 0.1

        end = Vector((
            self.current_start.x + math.cos(angle_rad) * length,
            self.current_start.y + math.sin(angle_rad) * length
        ))
        return end

    def _closes_loop(self, end_point):
        if not self.segments:
            return False
        first_start = Vector((self.segments[0]['start'][0], self.segments[0]['start'][1]))
        return (end_point - first_start).length < self.close_threshold

    def _confirm_segment(self, context):
        end = self._get_current_end_point()
        if end is None:
            return

        # Fecha o loop de forma precisa
        if self._closes_loop(end):
            end = Vector((self.segments[0]['start'][0], self.segments[0]['start'][1]))

        seg = {
            'start': (self.current_start.x, self.current_start.y),
            'end': (end.x, end.y),
            'thickness': self.thickness,
            'height': self.height,
            'offset': self.offset,
        }
        self.segments.append(seg)

        length_formatted = units.format_value((end - self.current_start).length, context.scene)
        self.report({'INFO'}, f"Segmento {len(self.segments)}: {length_formatted} confirmado.")

        if self._closes_loop(end):
            self._finish(context)
            return

        # Próximo ponto de partida
        self.current_start = end.copy()
        self.mouse_length = 0.0
        self.typed_value = ""
        self.typing = False
        self.active_field = 'LENGTH'

    # -------------------------------------------------------------------
    # Conclusão e Geração
    # -------------------------------------------------------------------

    def _finish(self, context):
        if not self.segments:
            self._cleanup(context)
            return

        # Cria objeto de parede no Blender
        mesh = bpy.data.meshes.new(name="BTM_Wall_Mesh")
        obj = bpy.data.objects.new("BTM_Wall", mesh)
        context.collection.objects.link(obj)
        context.view_layer.objects.active = obj
        obj.select_set(True)

        obj.btm_plane.object_kind = 'WALL'

        # Salva o primeiro segmento nas propriedades do add-on
        first = self.segments[0]
        obj.btm_wall.length = Vector((
            first['end'][0] - first['start'][0],
            first['end'][1] - first['start'][1]
        )).length
        obj.btm_wall.thickness = first['thickness']
        obj.btm_wall.height_start = first['height']
        obj.btm_wall.height_end = first['height']

        # Salva em JSON e gera a malha
        import json
        obj["btm_wall_segments"] = json.dumps(self.segments)
        generate_wall_from_segments(obj, self.segments)

        total_length = sum(
            Vector((s['end'][0] - s['start'][0], s['end'][1] - s['start'][1])).length
            for s in self.segments
        )
        total_formatted = units.format_value(total_length, context.scene)
        self.report({'INFO'}, f"Paredes geradas: {len(self.segments)} segmentos, total: {total_formatted}.")

        self._cleanup(context)

    def _cleanup(self, context):
        if self._draw_handler is not None:
            bpy.types.SpaceView3D.draw_handler_remove(self._draw_handler, 'WINDOW')
            self._draw_handler = None
        context.area.header_text_set(None)

    # -------------------------------------------------------------------
    # Header bar
    # -------------------------------------------------------------------

    def _update_header(self, context):
        if not self.building:
            context.area.header_text_set(
                "Construtor de Parede | Clique no piso para definir o ponto inicial  |  ESC: cancelar"
            )
            return

        field_labels = {
            'LENGTH': 'Comprimento',
            'ANGLE': 'Ângulo',
            'THICKNESS': 'Espessura',
            'HEIGHT': 'Altura',
        }

        # Formata os valores exibidos no cabeçalho na unidade ativa do Blender
        active_unit = units.get_scene_length_unit(context.scene)

        if self.typing:
            display_val = self.typed_value
            if self.active_field != 'ANGLE':
                suffix = " m" if active_unit == 'M' else (" cm" if active_unit == 'CM' else " mm")
                display_val += suffix
            else:
                display_val += "°"
        else:
            if self.active_field == 'LENGTH':
                display_val = units.format_value(self.mouse_length, context.scene)
            elif self.active_field == 'ANGLE':
                display_val = f"{self.mouse_angle:.1f}°"
            elif self.active_field == 'THICKNESS':
                display_val = units.format_value(self.thickness, context.scene)
            elif self.active_field == 'HEIGHT':
                display_val = units.format_value(self.height, context.scene)
            else:
                display_val = "—"

        active = field_labels.get(self.active_field, '?')
        seg_count = len(self.segments)

        context.area.header_text_set(
            f"Parede | Segmento: {seg_count + 1}  |  "
            f"[{active}]: {display_val}  |  "
            f"TAB: próximo campo  |  ENTER: confirmar  |  "
            f"Botão Direito: concluir polilinha  |  ESC: cancelar"
        )

    # -------------------------------------------------------------------
    # GPU Visual Preview
    # -------------------------------------------------------------------

    def _draw_preview(self, context):
        if not self.building or self.current_start is None:
            return

        end = self._get_current_end_point()
        if end is None:
            return

        # Posições em metros
        start_m = Vector((self.current_start.x, self.current_start.y, 0.001))
        end_m = Vector((end.x, end.y, 0.001))

        # Desenha linha do segmento em construção (verde brilhante)
        shader = gpu.shader.from_builtin('POLYLINE_UNIFORM_COLOR')
        gpu.state.blend_set('ALPHA')
        gpu.state.line_width_set(3.0)

        batch = batch_for_shader(
            shader, 'LINES',
            {"pos": [start_m, end_m]}
        )
        shader.bind()
        shader.uniform_float("color", (0.2, 1.0, 0.3, 0.8))

        region = context.region
        shader.uniform_float("lineWidth", 3.0)
        shader.uniform_float("viewportSize", (region.width, region.height))

        batch.draw(shader)

        # Desenha segmentos já confirmados (linhas ciano)
        if self.segments:
            seg_verts = []
            for seg in self.segments:
                s = Vector((seg['start'][0], seg['start'][1], 0.002))
                e = Vector((seg['end'][0], seg['end'][1], 0.002))
                seg_verts.extend([s, e])

            batch2 = batch_for_shader(
                shader, 'LINES',
                {"pos": seg_verts}
            )
            shader.uniform_float("color", (0.0, 0.8, 1.0, 0.6))
            batch2.draw(shader)

        # Desenha o ponto inicial da polilinha para fechamento (ponto vermelho)
        if self.segments:
            first_start = Vector((
                self.segments[0]['start'][0],
                self.segments[0]['start'][1],
                0.003
            ))
            gpu.state.point_size_set(10.0)
            dot_shader = gpu.shader.from_builtin('UNIFORM_COLOR')
            dot_batch = batch_for_shader(
                dot_shader, 'POINTS',
                {"pos": [first_start]}
            )
            dot_shader.bind()
            dot_shader.uniform_float("color", (1.0, 0.2, 0.2, 0.9))
            dot_batch.draw(dot_shader)

        gpu.state.blend_set('NONE')
        gpu.state.line_width_set(1.0)
        gpu.state.point_size_set(1.0)

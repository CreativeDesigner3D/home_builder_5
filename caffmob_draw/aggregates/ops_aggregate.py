"""Operadores de agregado (feature 003, T048; RF-12, RF-13, RF-18, D-12).

Converter (malhas selecionadas + pai ativo), desconverter, mover arrastando no plano da face (com limite) e apagar
um pai perguntando se os agregados vão junto.
"""

import bpy  # type: ignore
from bpy_extras import view3d_utils  # type: ignore
from mathutils import Vector, geometry  # type: ignore

from . import apply, convert, limits, props

_addon_keymaps = []


def _selected_meshes(context):
    parent = context.active_object
    return parent, [o for o in context.selected_objects if o is not parent and o.type == 'MESH']


def _aggregates(context):
    return [o for o in context.selected_objects if getattr(o, 'btm_aggregate', None) is not None
            and o.btm_aggregate.is_aggregate]


class BTM_OT_AggregateConvert(bpy.types.Operator):
    """Converte as malhas selecionadas em agregados do objeto ativo (selecione o pai por último)"""
    bl_idname = "caffmob.aggregate_convert"
    bl_label = "Converter em agregado"
    bl_options = {'REGISTER', 'UNDO'}

    face: bpy.props.EnumProperty(
        name="Face", items=[('AUTO', "Mais próxima", "")] + [(f, limits.FACE_LABELS[f], "") for f in limits.FACES],
        default='AUTO')  # type: ignore

    @classmethod
    def poll(cls, context):
        parent, meshes = _selected_meshes(context)
        return parent is not None and bool(meshes)

    def execute(self, context):
        parent, meshes = _selected_meshes(context)
        done = []
        for obj in meshes:
            reason = convert.can_convert(obj, parent)
            if reason:
                self.report({'WARNING'}, f"{obj.name}: {reason}")
                continue
            face = convert.convert(obj, parent, None if self.face == 'AUTO' else self.face)
            done.append(f"{obj.name} ({limits.FACE_LABELS[face]})")
        if not done:
            return {'CANCELLED'}
        for obj in context.selected_objects:
            obj.select_set(False)
        meshes[0].select_set(True)
        context.view_layer.objects.active = meshes[0]
        self.report({'INFO'}, f"Agregado(s) de {parent.name}: " + ", ".join(done))
        return {'FINISHED'}


class BTM_OT_LeafConvert(bpy.types.Operator):
    """Converte a malha selecionada em folha de porta do objeto ativo, com barra de abertura (selecione o pai por
    último)"""
    bl_idname = "caffmob.leaf_convert"
    bl_label = "Converter em folha de porta"
    bl_options = {'REGISTER', 'UNDO'}

    motion: bpy.props.EnumProperty(name="Movimento", items=props.MOTION_ITEMS, default='SWING')  # type: ignore
    hinge: bpy.props.EnumProperty(name="Eixo", items=props.HINGE_ITEMS, default='LEFT')  # type: ignore
    swing_sign: bpy.props.EnumProperty(name="Sentido", items=props.SWING_ITEMS, default='OUT')  # type: ignore
    max_angle: bpy.props.FloatProperty(name="Ângulo máximo", default=90.0, min=1.0, max=180.0)  # type: ignore
    slide_dir: bpy.props.EnumProperty(name="Sentido", items=props.SLIDE_ITEMS, default='POS_X')  # type: ignore
    travel: bpy.props.FloatProperty(name="Curso", default=0.5, min=0.001, subtype='DISTANCE',
                                    unit='LENGTH')  # type: ignore

    @classmethod
    def poll(cls, context):
        parent, meshes = _selected_meshes(context)
        return parent is not None and len(meshes) == 1

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=320)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "motion", expand=True)
        if self.motion == 'SWING':
            layout.prop(self, "hinge")
            layout.prop(self, "swing_sign")
            layout.prop(self, "max_angle")
        else:
            layout.prop(self, "slide_dir")
            layout.prop(self, "travel")

    def execute(self, context):
        from . import leaf
        parent, meshes = _selected_meshes(context)
        obj = meshes[0]
        reason = convert.can_convert(obj, parent)
        if reason:
            self.report({'WARNING'}, reason)
            return {'CANCELLED'}
        leaf.make_leaf(obj, parent, self.motion, self.hinge, self.swing_sign, self.max_angle, self.slide_dir,
                       self.travel)
        for other in context.selected_objects:
            other.select_set(False)
        obj.select_set(True)
        context.view_layer.objects.active = obj
        self.report({'INFO'}, f"{obj.name} virou folha de porta de {parent.name}; use a barra Abertura")
        return {'FINISHED'}


class BTM_OT_AggregateUnconvert(bpy.types.Operator):
    """Desfaz a conversão: tira recortes e folha e devolve o objeto como estava"""
    bl_idname = "caffmob.aggregate_unconvert"
    bl_label = "Desconverter"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return bool(_aggregates(context))

    def execute(self, context):
        count = sum(1 for obj in _aggregates(context) if convert.unconvert(obj))
        self.report({'INFO'}, f"{count} objeto(s) desconvertido(s)")
        return {'FINISHED'}


class BTM_OT_AggregateMove(bpy.types.Operator):
    """Arrasta o agregado no plano da face do pai; ele para na borda (Esc ou botão direito cancela)"""
    bl_idname = "caffmob.aggregate_move"
    bl_label = "Mover agregado"
    bl_options = {'REGISTER', 'UNDO', 'BLOCKING'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (context.area is not None and context.area.type == 'VIEW_3D' and obj is not None
                and getattr(obj, 'btm_aggregate', None) is not None and obj.btm_aggregate.is_aggregate)

    def _plane(self):
        agg = self.obj.btm_aggregate
        parent = agg.parent_ref
        n, sign, ua, va = limits.face_axes(agg.face)
        box = apply.parent_box(self.obj)
        point = Vector((0.0, 0.0, 0.0))
        point[n] = box[1][n] if sign > 0 else box[0][n]
        normal = Vector((0.0, 0.0, 0.0))
        normal[n] = sign
        world = parent.matrix_world
        return world @ point, (world.to_3x3() @ normal).normalized(), ua, va

    def _hit(self, context, event):
        region, rv3d = context.region, context.region_data
        coord = (event.mouse_region_x, event.mouse_region_y)
        origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)
        direction = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
        plane_co, plane_no, _ua, _va = self._plane()
        return geometry.intersect_line_plane(origin, origin + direction, plane_co, plane_no)

    def invoke(self, context, event):
        self.obj = context.active_object
        agg = self.obj.btm_aggregate
        self.start = (agg.u, agg.v)
        self.anchor = self._hit(context, event)
        if self.anchor is None:
            self.report({'WARNING'}, "Gire a vista para enxergar a face do pai")
            return {'CANCELLED'}
        context.window_manager.modal_handler_add(self)
        context.workspace.status_text_set("Mover agregado  |  Clique: confirmar  |  Botão direito/Esc: cancelar")
        return {'RUNNING_MODAL'}

    def _finish(self, context):
        context.workspace.status_text_set(None)

    def modal(self, context, event):
        if event.type == 'MOUSEMOVE':
            hit = self._hit(context, event)
            if hit is not None:
                agg = self.obj.btm_aggregate
                parent_inv = agg.parent_ref.matrix_world.inverted()
                delta = parent_inv @ hit - parent_inv @ self.anchor
                _n, _s, ua, va = limits.face_axes(agg.face)
                agg.u = self.start[0] + delta[ua]          # o update aplica o limite (RN-08)
                agg.v = self.start[1] + delta[va]
            return {'RUNNING_MODAL'}
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            self._finish(context)
            return {'FINISHED'}
        if event.type in {'RIGHTMOUSE', 'ESC'} and event.value == 'PRESS':
            agg = self.obj.btm_aggregate
            agg.u, agg.v = self.start
            self._finish(context)
            return {'CANCELLED'}
        return {'RUNNING_MODAL'}


class BTM_OT_DeleteWithAggregates(bpy.types.Operator):
    """Apaga os objetos selecionados; se tiverem agregados, pergunta se eles vão junto"""
    bl_idname = "caffmob.delete_with_aggregates"
    bl_label = "Apagar"
    bl_options = {'REGISTER', 'UNDO'}

    with_aggregates: bpy.props.BoolProperty(
        name="Apagar também os agregados", default=True,
        description="Desligado: os agregados ficam soltos na mesma posição")  # type: ignore

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT' and any(_children_aggregates(o) for o in context.selected_objects)

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, title="O objeto tem agregados")

    def draw(self, context):
        count = sum(len(_children_aggregates(o)) for o in context.selected_objects)
        self.layout.label(text=f"{count} agregado(s) presos aos objetos selecionados.")
        self.layout.prop(self, "with_aggregates")

    def execute(self, context):
        targets = list(context.selected_objects)
        for obj in targets:
            for child in _children_aggregates(obj):
                if self.with_aggregates:
                    if child not in targets:
                        targets.append(child)
                else:
                    convert.unconvert(child)
        for obj in targets:
            if obj.name in bpy.data.objects:
                for agg in [c for c in obj.children_recursive if getattr(c, 'btm_aggregate', None) is not None
                            and c.btm_aggregate.cutter is not None]:
                    cutter = agg.btm_aggregate.cutter
                    if cutter.name in bpy.data.objects:
                        bpy.data.objects.remove(cutter, do_unlink=True)
                bpy.data.objects.remove(obj, do_unlink=True)
        return {'FINISHED'}


def _children_aggregates(obj):
    try:
        return [c for c in obj.children_recursive if getattr(c, 'btm_aggregate', None) is not None
                and c.btm_aggregate.is_aggregate]
    except ReferenceError:
        return []


classes = (BTM_OT_AggregateConvert, BTM_OT_LeafConvert, BTM_OT_AggregateUnconvert, BTM_OT_AggregateMove, BTM_OT_DeleteWithAggregates)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon if wm else None
    if kc is not None:
        km = kc.keymaps.new(name='Object Mode', space_type='EMPTY')
        for key in ('X', 'DEL'):
            # Só age quando a seleção tem agregados (poll); senão o Delete do Blender segue normal.
            kmi = km.keymap_items.new(BTM_OT_DeleteWithAggregates.bl_idname, key, 'PRESS', head=True)
            _addon_keymaps.append((km, kmi))


def unregister():
    for km, kmi in _addon_keymaps:
        try:
            km.keymap_items.remove(kmi)
        except (ReferenceError, RuntimeError):
            pass
    _addon_keymaps.clear()
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)

"""Modo "Mover Sobre": botão, atalho do botão direito e arraste (T025; D-14, RN-05, RN-10).

- `caffmob.move_over_toggle` liga/desliga `WindowManager.btm_move_over.enabled` (sem modal permanente: o salvamento
  automático continua).
- Um item de keymap do add-on em "3D View" (`RIGHTMOUSE` `PRESS`, `head=True`) chama `caffmob.move_over_drag`. O `poll`
  só passa com o modo ligado; desligado, o evento segue para o menu de contexto do Blender.
- Com o modo ligado, o botão direito nunca abre menu: sem objeto movível sob o cursor, o operador consome o clique.
- O arraste desenha uma linha do ponto de partida até o cursor e o nome do objeto sob o cursor; soltar sobre um
  objeto de referência (B) abre a janela `caffmob.move_over_dialog`; soltar no vazio, sobre A ou após um clique sem arraste
  não faz nada.
"""

import bpy  # type: ignore
from bpy_extras import view3d_utils  # type: ignore

from ..canvas2d import draw
from ..selection import classify

DRAG_THRESHOLD_PX = 5
_addon_keymaps = []


def mode_enabled(context):
    state = getattr(context.window_manager, 'btm_move_over', None)
    return bool(state and state.enabled)


def raycast(context, mouse_region):
    region, rv3d = context.region, context.region_data
    if region is None or rv3d is None:
        return None
    origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, mouse_region)
    direction = view3d_utils.region_2d_to_vector_3d(region, rv3d, mouse_region)
    hit, _loc, _normal, _index, obj, _matrix = context.scene.ray_cast(
        context.evaluated_depsgraph_get(), origin, direction)
    return obj if hit else None


class BTM_OT_MoveOverToggle(bpy.types.Operator):
    """Liga ou desliga o "Mover Sobre": arraste um objeto sobre outro com o botão direito para alinhá-los"""
    bl_idname = "caffmob.move_over_toggle"
    bl_label = "Mover Sobre"
    bl_options = {'REGISTER'}

    def execute(self, context):
        state = context.window_manager.btm_move_over
        state.enabled = not state.enabled
        self.report({'INFO'}, "Mover Sobre ligado: arraste com o botão direito." if state.enabled
                    else "Mover Sobre desligado: o botão direito volta ao normal.")
        return {'FINISHED'}


class BTM_OT_MoveOverDrag(bpy.types.Operator):
    """Arraste com o botão direito de um objeto até outro para abrir a janela "Mover Sobre\""""
    bl_idname = "caffmob.move_over_drag"
    bl_label = "Mover Sobre (arrastar)"
    bl_options = {'REGISTER'}

    _handle = None

    @classmethod
    def poll(cls, context):
        return (context.area is not None and context.area.type == 'VIEW_3D' and context.region is not None
                and context.region.type == 'WINDOW' and mode_enabled(context))

    def invoke(self, context, event):
        start = (event.mouse_region_x, event.mouse_region_y)
        hit = raycast(context, start)
        self.a = classify.movable_root(hit) if hit else None
        if self.a is None:
            return {'FINISHED'}   # modo ligado: o botão direito não abre menu (RN-10)
        self.start = start
        self.cursor = start
        self.b = None
        self._handle = bpy.types.SpaceView3D.draw_handler_add(self._draw, (), 'WINDOW', 'POST_PIXEL')
        context.window_manager.modal_handler_add(self)
        context.workspace.status_text_set(
            f"Mover Sobre: solte o botão direito sobre o objeto de referência  |  Esc: cancelar  ({self.a.name})")
        return {'RUNNING_MODAL'}

    def _draw(self):
        sh = draw.begin()
        color = draw.COLORS['reference'] if self.b is not None else draw.COLORS['moving']
        draw.lines(sh, draw.dashed(self.start, self.cursor), color)
        label = f"{self.a.name} → {self.b.name}" if self.b is not None else self.a.name
        draw.text(self.cursor[0] + 12, self.cursor[1] + 10, label, color)
        draw.end()

    def _finish(self, context):
        if self._handle is not None:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            self._handle = None
        try:
            context.workspace.status_text_set(None)
        except (AttributeError, RuntimeError):
            pass
        if context.area:
            context.area.tag_redraw()

    def cancel(self, context):
        self._finish(context)

    def modal(self, context, event):
        if event.type == 'MOUSEMOVE':
            self.cursor = (event.mouse_region_x, event.mouse_region_y)
            hit = raycast(context, self.cursor)
            candidate = classify.reference_root(hit) if hit else None
            self.b = candidate if candidate is not None and candidate != self.a else None
            context.area.tag_redraw()
            return {'RUNNING_MODAL'}
        if event.type == 'RIGHTMOUSE' and event.value == 'RELEASE':
            moved = abs(self.cursor[0] - self.start[0]) + abs(self.cursor[1] - self.start[1])
            a, b = self.a, self.b
            self._finish(context)
            if moved >= DRAG_THRESHOLD_PX and b is not None:
                bpy.ops.caffmob.move_over_dialog('INVOKE_DEFAULT', a_name=a.name, b_name=b.name)
            return {'FINISHED'}
        if event.type == 'ESC':
            self._finish(context)
            return {'CANCELLED'}
        return {'RUNNING_MODAL'}


classes = (BTM_OT_MoveOverToggle, BTM_OT_MoveOverDrag)


# Mapas de modo da viewport cujo botão direito abre um menu de contexto no teclado padrão do Blender 5.2. Eles são
# processados antes do "3D View"; sem o atalho neles, o menu captura o clique e o arraste nunca começa (D-29, A001).
VIEW3D_MODE_KEYMAPS = (
    'Object Mode', 'Mesh', 'Curve', 'Curves', 'Armature', 'Metaball', 'Lattice', 'Font', 'Pose', 'Particle',
    'Sculpt', 'Vertex Paint', 'Weight Paint', 'Image Paint', 'Grease Pencil Edit Mode', 'Grease Pencil Draw Mode',
    'Grease Pencil Sculpt Mode', 'Grease Pencil Vertex Paint', 'Grease Pencil Weight Paint',
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon if wm else None
    if kc is not None:
        targets = [('3D View', 'VIEW_3D')] + [(name, 'EMPTY') for name in VIEW3D_MODE_KEYMAPS]
        for name, space in targets:
            km = kc.keymaps.new(name=name, space_type=space)
            kmi = km.keymap_items.new(BTM_OT_MoveOverDrag.bl_idname, 'RIGHTMOUSE', 'PRESS', head=True)
            _addon_keymaps.append((km, kmi))


def unregister():
    for km, kmi in _addon_keymaps:
        try:
            km.keymap_items.remove(kmi)
        except (ReferenceError, RuntimeError):
            pass
    _addon_keymaps.clear()
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

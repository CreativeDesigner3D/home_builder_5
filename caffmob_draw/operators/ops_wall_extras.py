"""Operações de parede da referência Promob (T034, T035; RF-35 a RF-37, D-19).

- `caffmob.wall_remove`: remove a parede com as opções "Segmento" (só o trecho), "Tudo" (todo o contorno ligado) ou
  "Manter o selecionado" (remove os outros trechos do contorno), e "Remover módulos que estão na parede". Sem a
  caixa, os módulos ficam soltos na mesma posição; portas, janelas e cotas da parede saem com ela.
- `caffmob.wall_lower`: rebaixar/desfazer o rebaixamento. A parede fica escondida na viewport (sem mudar as medidas
  gravadas) e uma filha `<parede>_Rebaixada` de 150 mm mostra o contorno no piso; os itens filhos continuam visíveis.
- `caffmob.wall_visibility`: parede ou teto visível, invisível (só contorno) ou com o contorno escondido.
"""

import bmesh  # type: ignore
import bpy  # type: ignore

from .. import hb_types

LOWERED_PROP = 'btm_wall_lowered'
LOWERED_PROXY = 'btm_lowered_proxy'
LOWERED_HEIGHT = 0.15
DISPLAY_PREV = 'btm_display_prev'
KEEP_WITH_WALL = ('obj_x', 'IS_2D_ANNOTATION', 'IS_ENTRY_DOOR_BP', 'IS_WINDOW_BP', LOWERED_PROXY)


def wall_of(obj):
    if obj is None:
        return None
    if obj.get('IS_WALL_BP'):
        return obj
    if obj.parent is not None and obj.parent.get('IS_WALL_BP'):
        return obj.parent
    return None


def chain_of(wall_obj):
    """Paredes ligadas à parede (contorno inteiro), na ordem da esquerda para a direita."""
    start = hb_types.GeoNodeWall(wall_obj)
    seen = {wall_obj.name}
    current = start
    while True:
        left = current.get_connected_wall('left')
        if left is None or left.obj.name in seen:
            break
        seen.add(left.obj.name)
        current = left
    ordered, names = [], set()
    while current is not None and current.obj.name not in names:
        names.add(current.obj.name)
        ordered.append(current.obj)
        current = current.get_connected_wall('right')
    return ordered


def remove_wall(obj, remove_modules=False):
    """Remove uma parede do Home Builder 5, solta a vizinha da direita e limpa a referência da esquerda.

    Módulos e geometrias filhos ficam soltos na mesma posição, a não ser que `remove_modules`.
    """
    wall = hb_types.GeoNodeWall(obj)
    left = wall.get_connected_wall('left')
    right = wall.get_connected_wall('right')
    if right is not None:
        world = right.obj.matrix_world.translation.copy()
        for con in list(right.obj.constraints):
            if con.type == 'COPY_LOCATION' and con.target == wall.obj_x:
                right.obj.constraints.remove(con)
        right.obj.location = world
    if left is not None and left.obj_x is not None:
        left.obj_x.home_builder.connected_object = None
    if not remove_modules:
        for child in list(obj.children):
            if any(child.get(tag) for tag in KEEP_WITH_WALL):
                continue
            matrix = child.matrix_world.copy()
            child.parent = None
            child.matrix_world = matrix
    for child in list(obj.children_recursive):
        if child.name in bpy.data.objects:
            bpy.data.objects.remove(child, do_unlink=True)
    bpy.data.objects.remove(obj, do_unlink=True)
    return [w.obj.name for w in (left, right) if w is not None]


def _remiter(names):
    from .walls import calculate_wall_miter_angles
    for name in names:
        obj = bpy.data.objects.get(name)
        if obj is not None:
            calculate_wall_miter_angles(obj)


class BTM_OT_WallRemove(bpy.types.Operator):
    """Remove a parede: só o trecho, o contorno inteiro ou os outros trechos do contorno"""
    bl_idname = "caffmob.wall_remove"
    bl_label = "Remover Parede"
    bl_options = {'REGISTER', 'UNDO'}

    mode: bpy.props.EnumProperty(
        name="Remover",
        items=[('SEGMENT', "Segmento", "Só o trecho selecionado"),
               ('ALL', "Tudo", "Todo o contorno ligado ao trecho"),
               ('KEEP', "Manter o selecionado", "Remove os outros trechos do contorno")],
        default='SEGMENT')  # type: ignore
    remove_modules: bpy.props.BoolProperty(name="Remover módulos que estão na parede", default=False)  # type: ignore

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT' and wall_of(context.active_object) is not None

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "mode", expand=True)
        layout.prop(self, "remove_modules")

    def execute(self, context):
        selected = wall_of(context.active_object)
        chain = chain_of(selected)
        if self.mode == 'SEGMENT':
            targets = [selected]
        elif self.mode == 'ALL':
            targets = chain
        else:
            targets = [w for w in chain if w != selected]
        names = {t.name for t in targets}
        neighbors = set()
        for target in targets:
            if target.name in bpy.data.objects:
                neighbors.update(remove_wall(target, self.remove_modules))
        _remiter(neighbors - names)
        self.report({'INFO'}, f"{len(targets)} parede(s) removida(s).")
        return {'FINISHED'}


# Rebaixar ------------------------------------------------------------------------------------------------------

def _proxy_of(obj):
    return next((c for c in obj.children if c.get(LOWERED_PROXY)), None)


def lower_wall(context, obj):
    wall = hb_types.GeoNodeWall(obj)
    length, thickness = wall.get_input('Length'), wall.get_input('Thickness')
    data = bpy.data.meshes.new(f"{obj.name}_Rebaixada")
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x = (v.co.x + 0.5) * length
        v.co.y = (v.co.y + 0.5) * thickness
        v.co.z = (v.co.z + 0.5) * LOWERED_HEIGHT
    bm.to_mesh(data)
    bm.free()
    proxy = bpy.data.objects.new(data.name, data)
    for collection in obj.users_collection:
        collection.objects.link(proxy)
    proxy.parent = obj
    proxy[LOWERED_PROXY] = True
    if obj.active_material is not None:
        data.materials.append(obj.active_material)
    obj[LOWERED_PROP] = True
    obj.hide_viewport = True
    return proxy


def raise_wall(obj):
    proxy = _proxy_of(obj)
    if proxy is not None:
        data = proxy.data
        bpy.data.objects.remove(proxy, do_unlink=True)
        if data.users == 0:
            bpy.data.meshes.remove(data)
    obj.hide_viewport = False
    if LOWERED_PROP in obj:
        del obj[LOWERED_PROP]


class BTM_OT_WallLower(bpy.types.Operator):
    """Rebaixa a parede a 150 mm na viewport (sem mudar o pé-direito), ou desfaz o rebaixamento"""
    bl_idname = "caffmob.wall_lower"
    bl_label = "Rebaixar Parede"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT' and any(wall_of(o) is not None for o in context.selected_objects)

    def execute(self, context):
        walls = {wall_of(o) for o in context.selected_objects} - {None}
        lowered = raised = 0
        for obj in walls:
            if obj.get(LOWERED_PROP):
                raise_wall(obj)
                raised += 1
            else:
                lower_wall(context, obj)
                lowered += 1
        self.report({'INFO'}, f"{lowered} parede(s) rebaixada(s), {raised} restaurada(s).")
        return {'FINISHED'}


# Invisível -----------------------------------------------------------------------------------------------------

def _visibility_target(obj):
    if obj is None:
        return None
    if obj.get('IS_CEILING_BP'):
        return obj
    return wall_of(obj)


def set_visibility(obj, mode):
    if mode == 'VISIBLE':
        obj.display_type = obj.get(DISPLAY_PREV) or 'TEXTURED'
        obj.hide_set(False)
        if DISPLAY_PREV in obj:
            del obj[DISPLAY_PREV]
        return
    if DISPLAY_PREV not in obj:
        obj[DISPLAY_PREV] = obj.display_type
    obj.display_type = 'WIRE'
    obj.hide_set(mode == 'HIDDEN')


class BTM_OT_WallVisibility(bpy.types.Operator):
    """Parede ou teto visível, invisível (só contorno) ou com o contorno escondido"""
    bl_idname = "caffmob.wall_visibility"
    bl_label = "Visibilidade da Parede"
    bl_options = {'REGISTER', 'UNDO'}

    mode: bpy.props.EnumProperty(
        name="Mostrar",
        items=[('VISIBLE', "Visível", "Parede normal"),
               ('WIRE', "Invisível", "Só o contorno"),
               ('HIDDEN', "Esconder contorno", "Nem o contorno aparece (Mostrar Todas as Paredes não traz de volta; "
                                               "use Visível no menu da parede ou Alt+H)")],
        default='WIRE')  # type: ignore

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT' and any(_visibility_target(o) is not None for o in context.selected_objects)

    def execute(self, context):
        targets = {_visibility_target(o) for o in context.selected_objects} - {None}
        for obj in targets:
            set_visibility(obj, self.mode)
        return {'FINISHED'}


classes = (BTM_OT_WallRemove, BTM_OT_WallLower, BTM_OT_WallVisibility)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

import json

import bmesh  # type: ignore
import bpy  # type: ignore
from mathutils import Matrix, Vector  # type: ignore

from ..geometry import floor_outline
from ..geometry.mesh_gen import generate_floor_mesh
from ..data import units


def scene_walls(scene):
    """Paredes reais da cena: do Home Builder 5 (`IS_WALL_BP`) e da camada nova (com `btm_wall_segments`).

    Não usa `btm_plane.object_kind == 'WALL'`, que é o valor padrão de todo objeto (BUG-20261007-A2G7).
    """
    hb, layer = [], []
    for obj in scene.objects:
        if obj.get('IS_WALL_BP'):
            hb.append(obj)
        elif obj.type == 'MESH' and obj.get("btm_wall_segments"):
            layer.append(obj)
    return hb, layer


def _hb_thickness(wall):
    from .. import compat
    for mod in wall.modifiers:
        if mod.type == 'NODES' and mod.node_group:
            value = compat.try_get_gn_input(mod, 'Thickness')
            if value is not None:
                return float(value)
    return 0.0


def _layer_segments(obj):
    try:
        raw = json.loads(obj.get("btm_wall_segments", ""))
    except (TypeError, ValueError):
        return []
    world = obj.matrix_world
    segments = []
    for seg in raw:
        a = world @ Vector((float(seg['start'][0]), float(seg['start'][1]), 0.0))
        b = world @ Vector((float(seg['end'][0]), float(seg['end'][1]), 0.0))
        segments.append({'start': (a.x, a.y), 'end': (b.x, b.y), 'thickness': float(seg.get('thickness', 0.15)),
                         'height': float(seg.get('height', 2.6))})
    return segments


def room_outlines(scene):
    """(polígonos das salas pela face interna, pontas das paredes); os polígonos em ordem anti-horária."""
    from .walls import find_wall_chains, get_room_boundary_points, get_wall_endpoints, is_closed_loop
    hb, layer = scene_walls(scene)
    polygons, ends = [], []
    if hb:
        for chain in find_wall_chains():
            points = get_room_boundary_points(chain)
            for wall in chain:
                ends.extend(get_wall_endpoints(wall))
            if len(points) >= 4 and is_closed_loop(points):
                nodes = [(p.x, p.y) for p in points[:-1]]
                polygons.append(floor_outline.hb_loop_inner(nodes, [_hb_thickness(w) for w in chain]))
    segments = [seg for obj in layer for seg in _layer_segments(obj)]
    polygons.extend(floor_outline.segments_inner_loops(segments))
    ends.extend(p for seg in segments for p in (seg['start'], seg['end']))
    return polygons, [tuple(p[:2]) for p in ends]


def build_floor_mesh(floor_obj, polygons):
    """Um n-gono por sala (aceita sala côncava), em coordenadas do mundo, com o piso na matriz identidade."""
    bm = bmesh.new()
    for polygon in polygons:
        verts = [bm.verts.new((x, y, 0.0)) for x, y in polygon]
        try:
            bm.faces.new(verts)
        except ValueError:
            continue
    bm.to_mesh(floor_obj.data)
    bm.free()
    floor_obj.data.update()
    floor_obj.matrix_world = Matrix.Identity(4)


class BTM_OT_AdjustFloor(bpy.types.Operator):
    """Ajusta o piso à face interna das paredes do ambiente"""
    bl_idname = "caffmob.adjust_floor"
    bl_label = "Ajustar Limites do Piso"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        hb, layer = scene_walls(context.scene)
        return bool(hb or layer)

    def execute(self, context):
        polygons, ends = room_outlines(context.scene)
        if not polygons:
            rect = floor_outline.bounding_rect(ends)
            if rect is None:
                self.report({'WARNING'}, "Nenhuma parede encontrada na cena.")
                return {'CANCELLED'}
            polygons = [rect]
            message = "Nenhuma sala fechada: piso pelo retângulo das paredes."
        else:
            message = f"Piso ajustado à face interna das paredes ({len(polygons)} sala(s))."

        # Encontra ou cria o piso
        floor_obj = None
        for obj in context.scene.objects:
            if hasattr(obj, 'btm_plane') and obj.btm_plane.object_kind == 'FLOOR':
                floor_obj = obj
                break

        if floor_obj is None:
            mesh = bpy.data.meshes.new(name="BTM_Floor_Mesh")
            floor_obj = bpy.data.objects.new("BTM_Floor", mesh)
            context.collection.objects.link(floor_obj)
            floor_obj.btm_plane.object_kind = 'FLOOR'

        build_floor_mesh(floor_obj, polygons)
        context.view_layer.objects.active = floor_obj
        floor_obj.select_set(True)
        self.report({'INFO'}, message)
        return {'FINISHED'}


class BTM_OT_FloorBuilder(bpy.types.Operator):
    """Cria o piso base para o ambiente 3D (modo manual)"""
    bl_idname = "caffmob.floor_builder"
    bl_label = "Criar Piso Manual"
    bl_options = {'REGISTER', 'UNDO'}

    size_x: bpy.props.FloatProperty(name="Largura X", default=5.0, subtype='DISTANCE')
    size_y: bpy.props.FloatProperty(name="Comprimento Y", default=5.0, subtype='DISTANCE')

    def execute(self, context):
        mesh = bpy.data.meshes.new(name="BTM_Floor_Mesh")
        obj = bpy.data.objects.new("BTM_Floor", mesh)

        context.collection.objects.link(obj)
        context.view_layer.objects.active = obj
        obj.select_set(True)

        obj.btm_plane.object_kind = 'FLOOR'

        generate_floor_mesh(obj, self.size_x, self.size_y)

        x_str = units.format_value(self.size_x, context.scene)
        y_str = units.format_value(self.size_y, context.scene)
        self.report({'INFO'}, f"Piso base criado: {x_str} x {y_str}")
        return {'FINISHED'}

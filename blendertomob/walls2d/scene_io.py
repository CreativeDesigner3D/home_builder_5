"""Leitura das paredes do Home Builder 5 para o modelo do editor (T019; D-03, D-05, D-06).

As paredes (`IS_WALL_BP`) formam cadeias: a parede seguinte tem uma restrição `COPY_LOCATION` presa ao `obj_x` (fim)
da anterior (`hb_types.GeoNodeWall.get_connected_wall`). Uma cadeia começa na parede sem vizinha à esquerda e segue
pela direita; fecha quando o fim da última coincide com o início da primeira (0,01 m, mesma regra do legado).

Cada trecho guarda o nome da parede de origem (`Segment.source`), para o aplicador atualizar em vez de recriar.
Os nós são a base da parede (Y local 0), que é a face interna, e a espessura fica à esquerda do sentido (Direção
esquerda, D-25).
"""

import json
import math

from .. import hb_types
from . import convert, model

CLOSE_TOLERANCE = 0.01


def _wall_props(obj):
    wall = hb_types.GeoNodeWall(obj)
    return {
        'length': wall.get_input('Length'),
        'thickness': wall.get_input('Thickness'),
        'height': wall.get_input('Height'),
        'end_height': wall.get_input('End Height'),
    }


def _start_end(obj, length):
    start = obj.matrix_world.translation
    rot = obj.matrix_world.to_euler().z
    return (start.x, start.y), (start.x + math.cos(rot) * length, start.y + math.sin(rot) * length)


def walls_in(scene):
    return [o for o in scene.objects if o.get('IS_WALL_BP') and hb_types.GeoNodeWall(o).has_modifier()]


def reference_segments(scene, exclude=()):
    """Contorno no piso das paredes da camada nova (`btm.wall_builder`, `btm_plane.object_kind = 'WALL'`), em
    coordenadas do mundo: arestas da malha com as duas pontas na cota mais baixa. Só para referência (D-05)."""
    segments = []
    for obj in scene.objects:
        if not is_other_layer_wall(obj) or obj.name in exclude:
            continue
        verts = obj.data.vertices
        if not verts:
            continue
        world = [obj.matrix_world @ v.co for v in verts]
        floor = min(p.z for p in world)
        for edge in obj.data.edges:
            a, b = (world[i] for i in edge.vertices)
            if abs(a.z - floor) < 1e-4 and abs(b.z - floor) < 1e-4:
                segments.append(((a.x, a.y), (b.x, b.y)))
    return segments


def read_plan(scene):
    """`WallPlan` com as cadeias de paredes da cena (todas as paredes do Home Builder 5) e, como referência, o
    contorno das paredes da camada nova."""
    walls = walls_in(scene)
    names = {w.name for w in walls}
    starts = [w for w in walls if hb_types.GeoNodeWall(w).get_connected_wall('left') is None]
    visited = set()
    chains = []
    for first in starts + walls:          # paredes em laço sem início marcado também entram
        if first.name in visited:
            continue
        ordered = []
        current = hb_types.GeoNodeWall(first)
        while current is not None and current.obj.name in names and current.obj.name not in visited:
            visited.add(current.obj.name)
            ordered.append(current.obj)
            current = current.get_connected_wall('right')
        if ordered:
            chains.append(_chain_from(ordered))
    return model.WallPlan(chains, reference_segments(scene))


def _chain_from(walls):
    nodes, segments = [], []
    end = None
    for obj in walls:
        props = _wall_props(obj)
        start, end = _start_end(obj, props['length'])
        nodes.append(start)
        segments.append(model.Segment(
            thickness=props['thickness'], height=props['height'], end_height=props['end_height'],
            wall_type=str(obj.get('btm_wall_type', 'NORMAL')), source=obj.name))
    first_start = nodes[0]
    closed = len(walls) >= 3 and math.hypot(end[0] - first_start[0], end[1] - first_start[1]) < CLOSE_TOLERANCE
    if not closed:
        nodes.append(end)
    # O legado põe a espessura à esquerda do sentido; `btm_wall_orientation` antigo é ignorado (D-25, M-11).
    return model.Chain(nodes, segments, closed=closed, side='LEFT')


def is_other_layer_wall(obj):
    """Parede da camada nova (`btm.wall_builder`), fora do Home Builder 5."""
    plane = getattr(obj, 'btm_plane', None)
    return obj is not None and obj.type == 'MESH' and not obj.get('IS_WALL_BP') and plane is not None \
        and plane.object_kind == 'WALL'


def convert_into(plan, objects, scene):
    """Converte as paredes da camada nova `objects` em cadeias novas do rascunho (D-22, RF-38).

    Usa `obj["btm_wall_segments"]` (linha de centro, espessura, altura) no mundo. O objeto entra em
    `plan.converted_sources` (removido no OK) e sai das referências. Devolve os nomes sem dados (ficam como referência).
    """
    skipped = []
    for obj in objects:
        try:
            raw = json.loads(obj.get("btm_wall_segments", ""))
        except (TypeError, ValueError):
            raw = None
        if not raw:
            skipped.append(obj.name)
            continue
        world = obj.matrix_world
        segments = []
        for seg in raw:
            a = world @ _vec(seg['start'])
            b = world @ _vec(seg['end'])
            segments.append({'start': (a.x, a.y), 'end': (b.x, b.y), 'thickness': float(seg['thickness']),
                             'height': float(seg.get('height', 2.6))})
        plan.chains.extend(convert.chains_from_segments(segments))
        plan.converted_sources.append(obj.name)
    plan.references = reference_segments(scene, exclude=set(plan.converted_sources))
    return skipped


def _vec(point):
    from mathutils import Vector  # type: ignore
    return Vector((float(point[0]), float(point[1]), 0.0))

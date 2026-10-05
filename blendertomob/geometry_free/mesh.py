"""Malha da placa e da caixa (T021; D-18) e as chapas que as formam (lista de peças, data-delta §5).

Python puro nas funções de medida (`size`, `sheets`); só `update`/`create_object` tocam o Blender.
"""

import bmesh  # type: ignore
import bpy  # type: ignore

GEOMETRY_FLAG = 'IS_BTM_GEOMETRY'


def size(kind, plane, width, depth, height, thickness):
    """(x, y, z) da peça: na placa, o eixo da espessura recebe `thickness`."""
    if kind == 'PLACA':
        if plane == 'XY':
            return width, depth, thickness
        if plane == 'XZ':
            return width, thickness, height
        return thickness, depth, height
    return width, depth, height


def sheets(kind, plane, width, depth, height, thickness):
    """[(nome, comprimento, largura, espessura)] em metros.

    Placa: uma chapa com comprimento e largura pelas duas maiores medidas e espessura pela menor.
    Caixa: fundo e tampo inteiros; laterais entre eles; frente e trás entre as laterais.
    """
    if kind == 'PLACA':
        a, b, c = sorted(size(kind, plane, width, depth, height, thickness), reverse=True)
        return [("Placa", a, b, c)]
    t = thickness
    inner_h = max(0.001, height - 2 * t)
    inner_w = max(0.001, width - 2 * t)
    return [
        ("Fundo", width, depth, t), ("Tampo", width, depth, t),
        ("Lateral esquerda", inner_h, depth, t), ("Lateral direita", inner_h, depth, t),
        ("Frente", inner_w, inner_h, t), ("Trás", inner_w, inner_h, t),
    ]


def _props(obj):
    g = obj.btm_geometry
    return g.kind, g.plane, g.width, g.depth, g.height, g.thickness


def update(obj):
    """Refaz a malha (caixa com origem no canto mínimo) a partir de `btm_geometry`."""
    x, y, z = size(*_props(obj))
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x = (v.co.x + 0.5) * x
        v.co.y = (v.co.y + 0.5) * y
        v.co.z = (v.co.z + 0.5) * z
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()


def create_object(context, kind='PLACA', name=None):
    """Cria a geometria na coleção ativa, marcada como `GEOMETRY`."""
    label = name or ("Placa" if kind == 'PLACA' else "Caixa")
    data = bpy.data.meshes.new(label)
    obj = bpy.data.objects.new(label, data)
    context.collection.objects.link(obj)
    obj[GEOMETRY_FLAG] = True
    obj.btm_plane.object_kind = 'GEOMETRY'
    obj.btm_geometry.kind = kind
    update(obj)
    return obj


def is_geometry(obj):
    return obj is not None and obj.type == 'MESH' and getattr(obj, 'btm_plane', None) is not None \
        and obj.btm_plane.object_kind == 'GEOMETRY' and getattr(obj, 'btm_geometry', None) is not None

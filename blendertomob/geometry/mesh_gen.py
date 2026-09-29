import bmesh
import math
from mathutils import Vector


def clear_mesh(obj):
    """Limpa de forma segura toda a geometria de um objeto de malha (mesh)."""
    if not obj or obj.type != 'MESH':
        return
    bm = bmesh.new()
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()


# ---------------------------------------------------------------------------
# Single Wall Segment
# ---------------------------------------------------------------------------

def generate_wall_mesh(obj, length, thickness, height):
    """Gera um segmento reto paramétrico de parede usando bmesh (escala em metros)."""
    clear_mesh(obj)
    comprimento = length
    t = thickness
    h = height

    bm = bmesh.new()

    # Cria os 4 vértices da base
    v0 = bm.verts.new((-comprimento / 2, -t / 2, 0.0))
    v1 = bm.verts.new((comprimento / 2, -t / 2, 0.0))
    v2 = bm.verts.new((comprimento / 2, t / 2, 0.0))
    v3 = bm.verts.new((-comprimento / 2, t / 2, 0.0))

    # Cria a face inferior
    base_face = bm.faces.new([v0, v1, v2, v3])

    # Extrui para cima
    result = bmesh.ops.extrude_face_region(bm, geom=[base_face])

    # Obtém os vértices extrudados e move-os verticalmente pela altura
    verts_extruded = [v for v in result['geom'] if isinstance(v, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, vec=(0.0, 0.0, h), verts=verts_extruded)

    # Conclui e salva na malha
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()


# ---------------------------------------------------------------------------
# Multi-Segment Wall (Polyline Wall Builder)
# ---------------------------------------------------------------------------

def generate_wall_from_segments(obj, segments):
    """
    Gera uma malha completa de parede a partir de uma polilinha de segmentos (escala em metros).

    Args:
        obj: Objeto Blender para receber a geometria da parede.
        segments: lista de dicionários, cada um contendo:
            - 'start': Vector (x, y) em metros
            - 'end': Vector (x, y) em metros
            - 'thickness': float em metros
            - 'height': float em metros
            - 'offset': float em metros
    """
    clear_mesh(obj)
    if not segments:
        return

    bm = bmesh.new()

    for seg in segments:
        start = Vector((seg['start'][0], seg['start'][1], seg.get('offset', 0.0)))
        end = Vector((seg['end'][0], seg['end'][1], seg.get('offset', 0.0)))
        t = seg['thickness'] / 2.0
        h = seg['height']

        # Direção e normal
        direction = (end - start)
        direction.z = 0
        if direction.length < 0.0001:
            continue
        normal = Vector((-direction.y, direction.x, 0.0)).normalized()

        offset_vec = normal * t

        # Quatro cantos da base deste segmento de parede
        p0 = start - offset_vec
        p1 = end - offset_vec
        p2 = end + offset_vec
        p3 = start + offset_vec

        # Cria vértices da base
        v0 = bm.verts.new(p0)
        v1 = bm.verts.new(p1)
        v2 = bm.verts.new(p2)
        v3 = bm.verts.new(p3)

        # Face inferior
        base_face = bm.faces.new([v0, v1, v2, v3])

        # Extrui para cima
        result = bmesh.ops.extrude_face_region(bm, geom=[base_face])
        verts_ext = [v for v in result['geom'] if isinstance(v, bmesh.types.BMVert)]
        bmesh.ops.translate(bm, vec=(0.0, 0.0, h), verts=verts_ext)

    # Recalcula as normais
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()


# ---------------------------------------------------------------------------
# Floor from Wall Contour
# ---------------------------------------------------------------------------

def generate_floor_from_walls(obj, wall_objects):
    """
    Gera uma malha de piso que acompanha o contorno interno das paredes (escala em metros).
    """
    clear_mesh(obj)

    if not wall_objects:
        return False

    all_bottom_verts = []
    for wall_obj in wall_objects:
        if not wall_obj or wall_obj.type != 'MESH':
            continue
        mesh = wall_obj.data
        if not mesh.vertices:
            continue

        min_z = min(v.co.z for v in mesh.vertices)
        for v in mesh.vertices:
            if abs(v.co.z - min_z) < 0.01:
                world_co = wall_obj.matrix_world @ v.co
                all_bottom_verts.append(Vector((world_co.x, world_co.y)))

    if len(all_bottom_verts) < 3:
        return False

    # Convex hull 2D (Graham scan)
    hull_points = _convex_hull_2d(all_bottom_verts)

    if len(hull_points) < 3:
        return False

    bm = bmesh.new()

    verts = []
    for pt in hull_points:
        verts.append(bm.verts.new((pt.x, pt.y, 0.0)))

    try:
        bm.faces.new(verts)
    except ValueError:
        bm.free()
        return False

    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()

    obj.btm_plane.object_kind = 'FLOOR'

    return True


def _convex_hull_2d(points):
    if len(points) < 3:
        return points

    start = min(points, key=lambda p: (p.y, p.x))

    def polar_angle(p):
        dx = p.x - start.x
        dy = p.y - start.y
        return math.atan2(dy, dx)

    sorted_pts = sorted(points, key=polar_angle)

    unique = [sorted_pts[0]]
    for i in range(1, len(sorted_pts)):
        if (sorted_pts[i] - unique[-1]).length > 0.001:
            unique.append(sorted_pts[i])
    sorted_pts = unique

    if len(sorted_pts) < 3:
        return sorted_pts

    hull = [sorted_pts[0], sorted_pts[1]]
    for i in range(2, len(sorted_pts)):
        while len(hull) > 1:
            cross = _cross_2d(hull[-2], hull[-1], sorted_pts[i])
            if cross <= 0:
                hull.pop()
            else:
                break
        hull.append(sorted_pts[i])

    return hull


def _cross_2d(o, a, b):
    return (a.x - o.x) * (b.y - o.y) - (a.y - o.y) * (b.x - o.x)


# ---------------------------------------------------------------------------
# Simple Floor (fallback / default)
# ---------------------------------------------------------------------------

def generate_floor_mesh(obj, size_x=5.0, size_y=5.0):
    """Gera um plano de piso simples com as dimensões em metros."""
    clear_mesh(obj)
    x = size_x
    y = size_y

    bm = bmesh.new()

    v0 = bm.verts.new((-x / 2, -y / 2, 0.0))
    v1 = bm.verts.new((x / 2, -y / 2, 0.0))
    v2 = bm.verts.new((x / 2, y / 2, 0.0))
    v3 = bm.verts.new((-x / 2, y / 2, 0.0))

    bm.faces.new([v0, v1, v2, v3])

    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()


# ---------------------------------------------------------------------------
# Cabinet Mesh
# ---------------------------------------------------------------------------

def generate_cabinet_mesh(obj, w, h, d, t):
    """Gera uma caixa de armário paramétrico (laterais, base, tampo, fundo) em metros."""
    clear_mesh(obj)

    bm = bmesh.new()

    # Helper para adicionar caixas ao bmesh
    def add_box(bm, x_min, x_max, y_min, y_max, z_min, z_max):
        verts = [
            bm.verts.new((x_min, y_min, z_min)),
            bm.verts.new((x_max, y_min, z_min)),
            bm.verts.new((x_max, y_max, z_min)),
            bm.verts.new((x_min, y_max, z_min)),
            bm.verts.new((x_min, y_min, z_max)),
            bm.verts.new((x_max, y_min, z_max)),
            bm.verts.new((x_max, y_max, z_max)),
            bm.verts.new((x_min, y_max, z_max))
        ]
        faces = [
            bm.faces.new([verts[0], verts[1], verts[2], verts[3]]),  # Base
            bm.faces.new([verts[4], verts[7], verts[6], verts[5]]),  # Topo
            bm.faces.new([verts[0], verts[4], verts[5], verts[1]]),  # Frente
            bm.faces.new([verts[1], verts[5], verts[6], verts[2]]),  # Direita
            bm.faces.new([verts[2], verts[6], verts[7], verts[3]]),  # Trás
            bm.faces.new([verts[3], verts[7], verts[4], verts[0]])   # Esquerda
        ]
        return faces

    # Lateral Esquerda
    add_box(bm, -w / 2, -w / 2 + t, -d, 0.0, 0.0, h)

    # Lateral Direita
    add_box(bm, w / 2 - t, w / 2, -d, 0.0, 0.0, h)

    # Base (painel inferior)
    add_box(bm, -w / 2 + t, w / 2 - t, -d, 0.0, 0.0, t)

    # Tampo (painel superior)
    add_box(bm, -w / 2 + t, w / 2 - t, -d, 0.0, h - t, h)

    # Fundo (painel traseiro)
    add_box(bm, -w / 2 + t, w / 2 - t, -t, 0.0, t, h - t)

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()


# ---------------------------------------------------------------------------
# Door Leaf Mesh
# ---------------------------------------------------------------------------

def generate_door_mesh(obj, w, h, t):
    """
    Gera a geometria da folha de porta (placa retangular).
    A origem (0, 0, 0) deste objeto será seu ponto de giro (pivot/dobradiça).
    A porta será gerada no quadrante X+ (ou X- se espelhada), Z+ e Y+ (ou Y- dependendo da profundidade).
    Convenção: folha se estende de X: 0 a w, Z: 0 a h, Y: 0 a t.
    """
    clear_mesh(obj)
    bm = bmesh.new()

    verts = [
        bm.verts.new((0.0, 0.0, 0.0)),
        bm.verts.new((w, 0.0, 0.0)),
        bm.verts.new((w, t, 0.0)),
        bm.verts.new((0.0, t, 0.0)),
        bm.verts.new((0.0, 0.0, h)),
        bm.verts.new((w, 0.0, h)),
        bm.verts.new((w, t, h)),
        bm.verts.new((0.0, t, h))
    ]

    bm.faces.new([verts[0], verts[1], verts[2], verts[3]])
    bm.faces.new([verts[4], verts[7], verts[6], verts[5]])
    bm.faces.new([verts[0], verts[4], verts[5], verts[1]])
    bm.faces.new([verts[1], verts[5], verts[6], verts[2]])
    bm.faces.new([verts[2], verts[6], verts[7], verts[3]])
    bm.faces.new([verts[3], verts[7], verts[4], verts[0]])

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()


# ---------------------------------------------------------------------------
# Opening Cut Tool (for boolean operations)
# ---------------------------------------------------------------------------

def generate_opening_tool_mesh(obj, width, height, depth=0.5):
    """Gera a malha do bloco de corte boolean para aberturas (escala em metros)."""
    clear_mesh(obj)
    w = width
    h = height
    d = depth

    bm = bmesh.new()

    v0 = bm.verts.new((-w / 2, -d / 2, 0.0))
    v1 = bm.verts.new((w / 2, -d / 2, 0.0))
    v2 = bm.verts.new((w / 2, d / 2, 0.0))
    v3 = bm.verts.new((-w / 2, d / 2, 0.0))
    v4 = bm.verts.new((-w / 2, -d / 2, h))
    v5 = bm.verts.new((w / 2, -d / 2, h))
    v6 = bm.verts.new((w / 2, d / 2, h))
    v7 = bm.verts.new((-w / 2, d / 2, h))

    bm.faces.new([v0, v1, v2, v3])  # Base
    bm.faces.new([v4, v7, v6, v5])  # Topo
    bm.faces.new([v0, v4, v5, v1])  # Frente
    bm.faces.new([v1, v5, v6, v2])  # Direita
    bm.faces.new([v2, v6, v7, v3])  # Trás
    bm.faces.new([v3, v7, v4, v0])  # Esquerda

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()

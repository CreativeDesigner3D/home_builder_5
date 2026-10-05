"""Cotas de um módulo na cena (T014; RN-04, D-11).

Liga `measure/cotas.py` (Python puro) aos objetos do Blender:
- módulo na parede (filho de uma parede do Home Builder 5, do lado da frente): posição local `x`, `z` e `y` (fundo do
  módulo na origem do gabinete), largura/altura/profundidade pelos inputs `Dim X/Y/Z`; obstáculos pelos outros filhos
  da parede na mesma faixa de altura (`hb_placement.PlacementMixin.get_wall_children_sorted`);
- módulo livre (sem parede ou do lado de trás): só as cotas verticais.

O pé-direito vem de `scene.home_builder.ceiling_height` (cena principal); sem ele, da altura da parede.
"""

import math

from .. import hb_types
from ..selection import classify
from . import cotas


def _dims(root):
    """(largura, profundidade, altura) do módulo em metros."""
    try:
        geo = hb_types.GeoNodeObject(root)
        if getattr(root, 'home_builder', None) is not None and root.home_builder.mod_name:
            return geo.get_input('Dim X'), geo.get_input('Dim Y'), geo.get_input('Dim Z')
    except Exception:
        pass
    cabinet = getattr(root, 'btm_cabinet', None)
    if cabinet is not None and cabinet.width > 0:
        return cabinet.width, cabinet.depth, cabinet.height
    d = root.dimensions
    return d.x, d.y, d.z


def _wall_of(root):
    parent = root.parent
    if parent is not None and parent.get('IS_WALL_BP'):
        return parent
    return None


def _on_front_side(root, wall):
    """Módulo do lado da frente da parede e sem rotação própria (os de trás giram 180°)."""
    rz = root.rotation_euler.z % (2 * math.pi)
    return min(rz, 2 * math.pi - rz) < 0.01 and root.location.y < 0.5 * _wall_thickness(wall)


def _wall_thickness(wall):
    try:
        return hb_types.GeoNodeWall(wall).get_input('Thickness')
    except Exception:
        return 0.0


def ceiling_height(scene, wall=None):
    from .. import hb_project
    main = hb_project.get_main_scene() or scene
    props = getattr(main, 'home_builder', None)
    value = getattr(props, 'ceiling_height', 0.0) if props is not None else 0.0
    if value > 0:
        return value
    if wall is not None:
        try:
            return hb_types.GeoNodeWall(wall).get_input('Height')
        except Exception:
            pass
    return 2.6


class ModuleCotas:
    """Contexto de cotas de um módulo: lê, calcula e aplica (escreve a posição)."""

    def __init__(self, root, scene):
        self.root = root
        self.scene = scene
        self.wall = _wall_of(root)
        width, depth, height = _dims(root)
        self.on_wall = self.wall is not None and _on_front_side(root, self.wall)
        if self.on_wall:
            loc = root.location
            self.placement = cotas.Placement(loc.x, width, loc.z, height, loc.y)
            self.wall_length = hb_types.GeoNodeWall(self.wall).get_input('Length')
        else:
            base_z = root.matrix_world.translation.z
            self.placement = cotas.Placement(0.0, width, base_z, height, 0.0)
            self.wall_length = None
        self.ceiling = ceiling_height(scene, self.wall)
        self.depth = depth

    def obstacles(self):
        if not self.on_wall:
            return []
        from ..hb_placement import PlacementMixin
        found = PlacementMixin().get_wall_children_sorted(
            self.wall, exclude_obj=self.root, object_z_start=self.placement.z0, object_height=self.placement.height)
        z0, z1 = self.placement.z0, self.placement.z0 + self.placement.height
        return [(x0, x1, z0, z1) for x0, x1, obj in found
                if obj is not None and not obj.get('IS_2D_ANNOTATION') and not obj.get('IS_SNAP_LINE')]

    def compute(self):
        if self.on_wall:
            return cotas.compute(self.placement, self.obstacles(), self.wall_length, self.ceiling)
        return cotas.compute_free(self.placement, self.ceiling)

    def apply(self, field, value):
        """Aplica a cota (RN-04); levanta ValueError("Valor Inválido…") sem mudar nada se for inválida."""
        if not self.on_wall and field in ('anterior', 'posterior', 'afastamento'):
            raise ValueError("Valor Inválido: módulo livre (sem parede) não tem cota anterior, posterior ou afastamento.")
        if self.on_wall:
            new = cotas.apply(field, value, self.placement, self.obstacles(), self.wall_length, self.ceiling)
            self.root.location = (new.x0, new.back_y, new.z0)
        else:
            new = cotas.apply(field, value, self.placement, [], 1e9, self.ceiling)
            delta = new.z0 - self.placement.z0
            self.root.location.z += delta
        self.placement = new
        return new


def for_object(obj, scene):
    """`ModuleCotas` do módulo que contém `obj`; None se não for módulo, peça ou frente de módulo."""
    info = classify.classify(obj)
    if info is None or info.kind not in (classify.MODULE, classify.PART, classify.FRONT):
        return None
    return ModuleCotas(info.root, scene)

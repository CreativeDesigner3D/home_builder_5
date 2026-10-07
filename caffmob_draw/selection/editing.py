"""Leitura e escrita de dimensões por tipo de objeto (T015; RN-03, D-10).

Cada biblioteca guarda as medidas num lugar diferente:
- frameless: inputs `Dim X/Y/Z` da raiz (via `compat`), registrando medida manual (`btm_overrides`, 001 RN-23);
- face frame: `root.face_frame_cabinet.width/height/depth` (o `update` recalcula o gabinete);
- closets: `root.hb_closet_starter.width/height/depth`;
- módulo rápido: `root.btm_cabinet.width/height/depth`;
- porta e janela de ambiente (Home Builder 5): inputs `Dim X` (largura) e `Dim Z` (altura); peitoril = `location.z`;
- parede (Home Builder 5): inputs `Length`, `Height`, `End Height`, `Thickness`, com recálculo das esquadrias.

Valores fora do domínio levantam `ValueError("Valor Inválido: …")` sem alterar nada.
"""

from .. import hb_types
from ..data import units
from . import classify

DIM_FIELDS = ('width', 'height', 'depth')
DIM_LABELS = {'width': "Largura", 'height': "Altura", 'depth': "Profundidade"}
GN_DIM = {'width': 'Dim X', 'depth': 'Dim Y', 'height': 'Dim Z'}
WALL_FIELDS = {'length': ('Length', "Comprimento"), 'height': ('Height', "Pé-direito inicial"),
               'end_height': ('End Height', "Pé-direito final"), 'thickness': ('Thickness', "Espessura")}
LIMITS = {'width': (0.01, 10.0), 'height': (0.01, 10.0), 'depth': (0.005, 10.0),
          'length': (0.05, 100.0), 'end_height': (0.5, 10.0), 'thickness': (0.01, 2.0), 'sill': (0.0, 5.0)}
WALL_LIMITS = {'height': (0.5, 10.0)}


def _check(field, value, label, limits=None):
    lo, hi = (limits or LIMITS)[field]
    if not lo <= value <= hi:
        unit = units.get_scene_length_unit()
        raise ValueError(f"Valor Inválido: {label} deve estar entre {units.format_length(lo, unit)} e "
                         f"{units.format_length(hi, unit)} (recebido: {units.format_length(value, unit)}).")


def _geo(obj):
    return hb_types.GeoNodeObject(obj)


def has_dimensions(info):
    return info is not None and info.kind in (classify.MODULE, classify.ROOM_DOOR, classify.WINDOW,
                                              classify.GEOMETRY, classify.OBSTACLE)


def editable_dimensions(info):
    """Campos de dimensão editáveis para o tipo (obstáculos e objetos sem fonte conhecida são só leitura)."""
    if info is None:
        return ()
    if info.kind == classify.MODULE:
        return DIM_FIELDS
    if info.kind in (classify.ROOM_DOOR, classify.WINDOW) and info.library == 'HB':
        return ('width', 'height')
    return ()


def get_dimension(info, field):
    obj = info.root if info.kind in (classify.MODULE, classify.FRONT, classify.PART) else info.obj
    library = info.library
    if info.kind == classify.MODULE or info.kind in (classify.FRONT, classify.PART):
        if library == 'FACE_FRAME' and getattr(obj, 'face_frame_cabinet', None) is not None:
            return getattr(obj.face_frame_cabinet, field)
        if library == 'CLOSETS' and getattr(obj, 'hb_closet_starter', None) is not None:
            return getattr(obj.hb_closet_starter, field)
        if library == 'BTM' and getattr(obj, 'btm_cabinet', None) is not None:
            return getattr(obj.btm_cabinet, field)
    if getattr(obj, 'home_builder', None) is not None and obj.home_builder.mod_name and field in GN_DIM:
        try:
            return _geo(obj).get_input(GN_DIM[field])
        except Exception:
            pass
    d = obj.dimensions
    return {'width': d.x, 'depth': d.y, 'height': d.z}[field]


def set_dimension(context, info, field, value):
    if field not in editable_dimensions(info):
        raise ValueError(f"Valor Inválido: {DIM_LABELS[field]} não é editável para este objeto.")
    _check(field, value, DIM_LABELS[field])
    obj = info.root if info.kind == classify.MODULE else info.obj
    if info.kind == classify.MODULE and info.library == 'FACE_FRAME':
        setattr(obj.face_frame_cabinet, field, value)
    elif info.kind == classify.MODULE and info.library == 'CLOSETS':
        setattr(obj.hb_closet_starter, field, value)
    elif info.kind == classify.MODULE and info.library == 'BTM':
        setattr(obj.btm_cabinet, field, value)
    else:
        _geo(obj).set_input(GN_DIM[field], value)
        if info.kind == classify.MODULE:
            from ..standards import sync
            sync.add_override(obj, GN_DIM[field])
            from .. import hb_utils
            hb_utils.run_calc_fix(context, obj)


# Peitoril (porta/janela de ambiente) ------------------------------------------------------------------------

def get_sill(info):
    return info.obj.location.z


def set_sill(info, value):
    if info.kind == classify.ROOM_DOOR:
        raise ValueError("Valor Inválido: o peitoril de uma porta é sempre 0.")
    _check('sill', value, "Peitoril")
    info.obj.location.z = value


# Parede -----------------------------------------------------------------------------------------------------

def get_wall(info, field):
    return hb_types.GeoNodeWall(info.obj).get_input(WALL_FIELDS[field][0])


def set_wall(info, field, value):
    if info.library != 'HB':
        raise ValueError("Valor Inválido: esta parede não é editável por aqui.")
    gn_name, label = WALL_FIELDS[field]
    _check(field, value, label, {**LIMITS, **WALL_LIMITS})
    wall = hb_types.GeoNodeWall(info.obj)
    wall.set_input(gn_name, value)
    if field == 'height':
        # Pé-direito final acompanha o inicial (RN-18).
        wall.set_input('End Height', value)
    from ..operators import walls
    walls.update_all_wall_miters()

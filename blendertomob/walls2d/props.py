"""Estado do Editor de Paredes (T007; data-delta §1).

- `Session` (em memória, uma por vez): rascunho (`model.WallPlan`), vista 2D, seleção, lápis, janela/área do editor.
- `WindowManager.btm_wall_editor`: ferramenta, grade, padrões do lápis e os campos do trecho selecionado. Os campos do
  trecho são propriedades virtuais (`get`/`set`) sobre o rascunho: nada vai para o 3D até o OK (RN-16).
"""

import math

import bpy  # type: ignore

from . import model


class Session:
    """Editor aberto: rascunho e estado de interação."""

    def __init__(self, plan, scene_name):
        self.plan = plan
        self.scene_name = scene_name
        self.view = None
        self.window_ptr = 0
        self.area_ptr = 0
        self.restore_area_type = None     # quando o editor ocupa uma área da janela atual
        self.selected = None              # (cadeia, trecho)
        self.selected_node = None         # (cadeia, nó) — digitação direta no vértice (D-27)
        self.line = model.INNER
        self.drawing = None               # cadeia sendo desenhada a lápis
        self.cursor = None                # posição do cursor no mundo 2D
        self.typed = ""
        self.prompt = None                # 'close' = pergunta de fechamento
        self.error = ""
        self.warnings = []
        self.removed_modules = []         # módulos de trechos apagados (D-21)
        self.remove_modules = False       # "Remover os módulos junto?" (padrão: não)
        self.confirm_pending = False
        self.request = None               # 'ok' | 'cancel'
        self.signature = model.plan_signature(plan)   # rascunho na abertura (confirmação do Cancelar, D-30)
        self.prompt_chain = None          # cadeia da pergunta de fechamento por arraste (D-34)
        self.pending_point = None         # trecho digitado que chegou ao início, aplicado se a resposta for "Não"
        self.project_height = 2.6         # pé-direito do projeto lido na abertura (D-36)
        self.equalize_height = True       # "Igualar ao pé-direito do projeto" (D-37)
        self.height_mismatches = []

    def dirty(self):
        return model.plan_signature(self.plan) != self.signature

    def segment(self):
        if self.selected is None:
            return None, None
        ci, si = self.selected
        if ci >= len(self.plan.chains) or si >= self.plan.chains[ci].segment_count():
            self.selected = None
            return None, None
        return self.plan.chains[ci], si

    def redraw(self):
        for window in bpy.context.window_manager.windows:
            for area in window.screen.areas:
                if area.as_pointer() == self.area_ptr:
                    area.tag_redraw()


_session = [None]


def session():
    return _session[0]


def start(plan, scene_name):
    _session[0] = Session(plan, scene_name)
    return _session[0]


def end():
    _session[0] = None


# Campos virtuais do trecho -----------------------------------------------------------------------------------

def _guard(apply):
    s = session()
    if s is None:
        return
    try:
        apply()
        s.error = ""
    except ValueError as exc:
        s.error = str(exc)
    s.redraw()


def _seg_get(field, default=0.0):
    def get(_self):
        s = session()
        chain, i = s.segment() if s else (None, None)
        if chain is None:
            return default
        if field == 'length':
            return chain.face_length(i, s.line)
        if field == 'angle_abs':
            return math.radians(chain.angle_abs(i))
        if field == 'angle_rel':
            return math.radians(chain.angle_rel(i))
        return getattr(chain.segments[i], field)
    return get


def _seg_set(field):
    def set_(_self, value):
        s = session()
        chain, i = s.segment() if s else (None, None)
        if chain is None:
            return
        if field == 'length':
            _guard(lambda: chain.set_length(i, value, s.line))
        elif field == 'angle_abs':
            _guard(lambda: chain.set_angle_abs(i, math.degrees(value) % 360.0))
        elif field == 'angle_rel':
            _guard(lambda: chain.set_angle_rel(i, math.degrees(value)))
        else:
            _guard(lambda: chain.set_segment_value(i, field, value))
    return set_


def _type_get(_self):
    s = session()
    chain, i = s.segment() if s else (None, None)
    return model.WALL_TYPES.index(chain.segments[i].wall_type) if chain is not None else 0


def _type_set(_self, value):
    s = session()
    chain, i = s.segment() if s else (None, None)
    if chain is not None:
        _guard(lambda: chain.set_segment_value(i, 'wall_type', model.WALL_TYPES[value]))


def _side_get(_self):
    s = session()
    chain, _i = s.segment() if s else (None, None)
    return model.SIDES.index(chain.side) if chain is not None else 0


def _side_set(_self, value):
    s = session()
    chain, i = s.segment() if s else (None, None)
    if chain is None:
        return
    chain.side = model.SIDES[value]
    if any(seg.source for seg in chain.segments):
        s.error = ("Direção trocada em paredes existentes: no OK elas mudam de sentido e os itens presos ficam onde "
                   "estão.")
    s.redraw()


def _line_get(_self):
    s = session()
    return (model.INNER, model.OUTER).index(s.line) if s else 0


def _line_set(_self, value):
    s = session()
    if s is not None:
        s.line = (model.INNER, model.OUTER)[value]
        s.redraw()


def _equalize_get(_self):
    s = session()
    return bool(s and s.equalize_height)


def _equalize_set(_self, value):
    s = session()
    if s is not None:
        s.equalize_height = bool(value)


def _remove_modules_get(_self):
    s = session()
    return bool(s and s.remove_modules)


def _remove_modules_set(_self, value):
    s = session()
    if s is not None:
        s.remove_modules = bool(value)


def _length(name, field, description=""):
    return bpy.props.FloatProperty(name=name, description=description, subtype='DISTANCE', unit='LENGTH',
                                   precision=1, get=_seg_get(field), set=_seg_set(field))


def _angle(name, field):
    return bpy.props.FloatProperty(name=name, subtype='ANGLE', unit='ROTATION', precision=2,
                                   get=_seg_get(field), set=_seg_set(field))


SIDE_ITEMS = [('LEFT', "Esquerda", "A parede cresce para a esquerda da linha desenhada (face interna)"),
              ('RIGHT', "Direita", "A parede cresce para a direita da linha desenhada (face interna)")]
TYPE_ITEMS = [('NORMAL', "Normal", ""), ('DIVISORIA', "Divisória", "Padrão de espessura 100 mm"),
              ('MURETA', "Mureta", "Padrão de altura 1.100 mm")]


class BTM_PG_WallEditorState(bpy.types.PropertyGroup):
    tool: bpy.props.EnumProperty(
        name="Ferramenta",
        items=[('SELECT', "Selecionar/Mover", "Selecionar trechos e arrastar vértices", 'RESTRICT_SELECT_OFF', 0),
               ('DRAW', "Construir Parede", "Desenhar paredes a lápis", 'GREASEPENCIL', 1),
               ('INVERT', "Inverter Sentido", "Inverter o sentido da parede clicada", 'ARROW_LEFTRIGHT', 2),
               ('ADD_NODE', "Adicionar Vértice", "Dividir o trecho no ponto clicado", 'ADD', 3),
               ('REMOVE_NODE', "Remover Vértice", "Unir os trechos do vértice clicado", 'REMOVE', 4)],
        default='SELECT')  # type: ignore
    grid_size: bpy.props.FloatProperty(name="Tamanho", subtype='DISTANCE', unit='LENGTH', default=1.0, min=0.01,
                                       max=5.0, update=lambda s, c: session() and session().redraw())  # type: ignore
    magnetic: bpy.props.BoolProperty(name="Linhas Magnéticas", default=False,
                                     description="Vértices encaixam nos cruzamentos da grade")  # type: ignore
    new_direction: bpy.props.EnumProperty(
        name="Direção", items=SIDE_ITEMS, default='LEFT',
        description="Lado da espessura nas paredes novas; ao fechar uma sala, a espessura vai para fora")  # type: ignore
    new_thickness: bpy.props.FloatProperty(name="Espessura", subtype='DISTANCE', unit='LENGTH', default=0.15,
                                           min=0.01, max=2.0)  # type: ignore
    new_height: bpy.props.FloatProperty(name="Pé-direito", subtype='DISTANCE', unit='LENGTH', default=2.6,
                                        min=0.5, max=10.0)  # type: ignore
    line: bpy.props.EnumProperty(name="Linha", items=[('INNER', "Interna", "Face interna (medida real, tracejada)"),
                                                      ('OUTER', "Externa", "Face externa (interna + espessuras)")],
                                 get=_line_get, set=_line_set)  # type: ignore
    length: _length("Comprimento", 'length', "Comprimento na linha selecionada (interna ou externa)")  # type: ignore
    angle_abs: _angle("Ângulo Absoluto", 'angle_abs')  # type: ignore
    angle_rel: _angle("Ângulo Relativo", 'angle_rel')  # type: ignore
    lock_angle: bpy.props.BoolProperty(name="Bloquear Ângulo", get=_seg_get('lock_angle', False),
                                       set=_seg_set('lock_angle'))  # type: ignore
    thickness: _length("Espessura", 'thickness')  # type: ignore
    height: _length("Pé-direito Inicial", 'height')  # type: ignore
    end_height: _length("Pé-direito Final", 'end_height')  # type: ignore
    direction: bpy.props.EnumProperty(name="Direção", items=SIDE_ITEMS, get=_side_get, set=_side_set,
                                      description="Lado para onde a espessura cresce; a medida interna não muda")  # type: ignore
    wall_type: bpy.props.EnumProperty(name="Tipo de Parede", items=TYPE_ITEMS, get=_type_get,
                                      set=_type_set)  # type: ignore
    equalize_height: bpy.props.BoolProperty(
        name="Igualar ao pé-direito do projeto",
        description="As paredes listadas passam ao pé-direito das Configurações (Mureta, meia-parede e parede falsa "
                    "ficam como estão)",
        get=_equalize_get, set=_equalize_set)  # type: ignore
    remove_modules: bpy.props.BoolProperty(
        name="Remover os módulos junto?",
        description="Os módulos dos trechos apagados saem com a parede; desmarcado, ficam soltos no lugar",
        get=_remove_modules_get, set=_remove_modules_set)  # type: ignore


classes = (BTM_PG_WallEditorState,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.WindowManager.btm_wall_editor = bpy.props.PointerProperty(type=BTM_PG_WallEditorState)


def unregister():
    end()
    if hasattr(bpy.types.WindowManager, 'btm_wall_editor'):
        del bpy.types.WindowManager.btm_wall_editor
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

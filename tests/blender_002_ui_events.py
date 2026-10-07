"""Teste de interface da feature 002 com eventos simulados (T071).

Precisa de janela (não roda em --background):
    blender --factory-startup --enable-event-simulate --python tests/blender_002_ui_events.py

`Window.event_simulate` injeta cliques, movimentos e teclas pelo caminho real (modais, botões dos painéis, atalhos).
Com essa opção o Blender ignora o mouse e o teclado de verdade, por isso o teste roda numa instância própria e a
encerra no fim, com código de saída 0 (tudo certo) ou 1 (falhas listadas no console).

Cobre: botão direito do "Mover Sobre" em Modo Objeto e em Edição (D-29); troca de ferramenta pelo painel do Editor de
Paredes, lápis com digitação, fechamento, OK pelo painel e Cancelar com confirmação (D-30).
"""

import os
import sys
import traceback
import types
from pathlib import Path

import bpy
from bpy_extras import view3d_utils
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import caffmob_draw as addon  # noqa: E402

addon.register()
# Sem a extensão instalada não há preferências do add-on (cor da parede).
type(bpy.context.window_manager.home_builder).get_user_preferences = \
    lambda self, c: types.SimpleNamespace(wall_color=(0.5, 0.5, 0.5, 1.0), door_window_color=(0.3, 0.3, 0.3, 1.0))

from caffmob_draw import hb_utils  # noqa: E402
from caffmob_draw.product_libraries.frameless import types_frameless as tf  # noqa: E402
from caffmob_draw.walls2d import ops_editor, props  # noqa: E402
from caffmob_draw.walls2d import window as w2d  # noqa: E402

FAILURES = []


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


def alive(win):
    return any(w.as_pointer() == win.as_pointer() for w in bpy.context.window_manager.windows)


def ev(win, kind, value='PRESS', x=0, y=0, char=''):
    if not alive(win):
        raise RuntimeError("janela fechada")
    if char:
        win.event_simulate(kind, value, unicode=char, x=int(x), y=int(y))
    else:
        win.event_simulate(kind, value, x=int(x), y=int(y))


def tap(win, x, y, button='LEFTMOUSE'):
    """Clique real: o Blender ativa o botão no movimento do mouse e só depois recebe o clique (gerador)."""
    ev(win, 'MOUSEMOVE', 'NOTHING', x, y)
    yield 0.05
    ev(win, button, 'PRESS', x, y)
    ev(win, button, 'RELEASE', x, y)


KEYS = {'0': 'ZERO', '1': 'ONE', '2': 'TWO', '3': 'THREE', '4': 'FOUR', '5': 'FIVE', '6': 'SIX', '7': 'SEVEN',
        '8': 'EIGHT', '9': 'NINE'}


def type_number(win, text, x, y):
    for ch in text:
        ev(win, KEYS[ch], 'PRESS', x, y, char=ch)
        ev(win, KEYS[ch], 'RELEASE', x, y)
    ev(win, 'RET', 'PRESS', x, y)
    ev(win, 'RET', 'RELEASE', x, y)


def view3d(win):
    area = next(a for a in win.screen.areas if a.type == 'VIEW_3D')
    return area, next(r for r in area.regions if r.type == 'WINDOW'), area.spaces.active.region_3d


def modal_ids(ctx):
    return [op.bl_idname for w in ctx.window_manager.windows for op in w.modal_operators]


def script():
    ctx = bpy.context
    scene = ctx.scene
    for obj in list(scene.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    win = ctx.window_manager.windows[0]
    area, region, rv3d = view3d(win)
    yield 0.5

    # 1. "Mover Sobre": botão direito em Modo Objeto e em Edição.
    a_mod = tf.BaseCabinet()
    a_mod.default_exterior = 'Open'
    a_mod.create("A_mod")
    a_mod.obj.location = (0.0, 0.0, 0.0)
    b_mod = tf.BaseCabinet()
    b_mod.default_exterior = 'Open'
    b_mod.create("B_mod")
    b_mod.obj.location = (2.0, 0.0, 0.0)
    for obj in (a_mod.obj, b_mod.obj):
        hb_utils.run_calc_fix_until_stable(ctx, obj)
    ctx.view_layer.update()
    with ctx.temp_override(window=win, area=area, region=region):
        bpy.ops.view3d.view_axis(type='TOP')
        bpy.ops.view3d.view_all()
    yield 0.4

    def to_win(co):
        p = view3d_utils.location_3d_to_region_2d(region, rv3d, Vector(co))
        return region.x + p.x, region.y + p.y

    pa = to_win(a_mod.obj.matrix_world.translation + Vector((0.3, -0.3, 0.9)))
    pb = to_win(b_mod.obj.matrix_world.translation + Vector((0.3, -0.3, 0.9)))
    ctx.window_manager.btm_move_over.enabled = True
    # Aquecimento: na janela recém-aberta, o 1º botão direito simulado se perde (efeito da simulação; o 2º funciona
    # sem mudar nada). Um clique direito num ponto vazio consome esse primeiro evento.
    empty = (region.x + 15, region.y + 15)
    ev(win, 'MOUSEMOVE', 'NOTHING', *empty)
    ev(win, 'RIGHTMOUSE', 'PRESS', *empty)
    ev(win, 'RIGHTMOUSE', 'RELEASE', *empty)
    yield 0.3
    ev(win, 'ESC', 'PRESS', *empty)
    ev(win, 'ESC', 'RELEASE', *empty)
    yield 0.2
    for mode in ('OBJECT', 'EDIT'):
        if mode == 'EDIT':
            bpy.ops.mesh.primitive_plane_add(location=(0.0, 4.0, 0.0))
            with ctx.temp_override(window=win, area=area, region=region):
                bpy.ops.object.mode_set(mode='EDIT')
            yield 0.3
        ev(win, 'MOUSEMOVE', 'NOTHING', *pa)
        ev(win, 'RIGHTMOUSE', 'PRESS', *pa)
        yield 0.15
        started = 'CAFFMOB_OT_move_over_drag' in modal_ids(ctx)
        for k in range(1, 8):
            ev(win, 'MOUSEMOVE', 'NOTHING', pa[0] + (pb[0] - pa[0]) * k / 7, pa[1] + (pb[1] - pa[1]) * k / 7)
            yield 0.05
        ev(win, 'RIGHTMOUSE', 'RELEASE', *pb)
        yield 0.5
        dialog = 'CAFFMOB_OT_move_over_dialog' in modal_ids(ctx)
        check(f"Mover Sobre com botão direito ({mode})", started and dialog, str(modal_ids(ctx)))
        ev(win, 'ESC', 'PRESS', *pb)
        ev(win, 'ESC', 'RELEASE', *pb)
        yield 0.3
        if mode == 'EDIT':
            with ctx.temp_override(window=win, area=area, region=region):
                bpy.ops.object.mode_set(mode='OBJECT')
    ctx.window_manager.btm_move_over.enabled = False
    for obj in list(scene.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    yield 0.3

    # 2. Editor de Paredes: ferramentas pelo painel, lápis, fechamento, OK; Cancelar com confirmação.
    with ctx.temp_override(window=win, area=area, region=region):
        bpy.ops.caffmob.wall_editor('INVOKE_DEFAULT')
    yield 1.5
    s = props.session()
    ewin, earea, ereg = w2d.editor_area(ctx)
    ui = next(r for r in earea.regions if r.type == 'UI')
    state = ctx.window_manager.btm_wall_editor
    found = {}
    cx = ui.x + ui.width * 0.5
    y = ui.y + ui.height - 34                               # abaixo do cabeçalho do 1º painel (clicar nele o recolhe)
    first_hit = None
    while y > ui.y + 10 and len(found) < 4:          # Selecionar já é a ativa: as outras 4 bastam
        before = state.tool
        yield from tap(ewin, cx, y)
        yield 0.12
        if props.session() is None or s.request is not None:
            first_hit = first_hit or 'cancelou'
            break
        if state.tool != before:
            found.setdefault(state.tool, y)
            first_hit = first_hit or 'ferramenta'
        y -= 6
    check("o topo do painel são as Ferramentas (OK/Cancelar no fim)", first_hit == 'ferramenta', str(first_hit))
    check("trocar ferramenta pelo painel", len(found) == 4, str(sorted(found)))
    if props.session() is None:
        return
    if 'DRAW' in found:
        yield from tap(ewin, cx, found['DRAW'])
        yield 0.2
    else:
        state.tool = 'DRAW'
    view = s.view

    def scr(pt):
        p = view.to_screen(pt)
        return ereg.x + p[0], ereg.y + p[1]

    yield from tap(ewin, *scr((0.0, 0.0)))
    yield 0.2
    for target, length in (((1.0, 0.0), "3000"), ((3.0, 1.0), "2000"), ((2.0, 2.0), "3000")):
        tx, ty = scr(target)
        ev(ewin, 'MOUSEMOVE', 'NOTHING', tx, ty)
        yield 0.1
        type_number(ewin, length, tx, ty)
        yield 0.2
    yield from tap(ewin, *scr(s.drawing.nodes[0]))
    yield 0.3
    _box, yes, _no = ops_editor._prompt_rects(ereg)
    yield from tap(ewin, ereg.x + yes[0] + 10, ereg.y + yes[1] + 10)
    yield 0.3
    chain = s.plan.chains[-1] if s.plan.chains else None
    check("lápis com digitação e fechamento", chain is not None and chain.closed and chain.segment_count() == 4,
          str(chain.nodes if chain else None))
    check("sala anti-horária fecha com a espessura para fora", chain is not None and chain.side == 'RIGHT',
          chain.side if chain else "")
    # OK pelo painel: varre a metade esquerda de baixo para cima.
    ox = ui.x + ui.width * 0.28
    y = ui.y + 10
    applied = False
    while y < ui.y + ui.height - 10:
        yield from tap(ewin, ox, y)
        yield 0.2
        if props.session() is None:
            applied = True
            break
        y += 6
    yield 0.8
    walls = [o for o in scene.objects if o.get('IS_WALL_BP')]
    check("OK pelo painel aplica as paredes", applied and len(walls) == 4, f"paredes={len(walls)}")

    # Cancelar com alterações: Esc pergunta; "Não" mantém o editor; Esc de novo + "Sim" fecha sem mudar o 3D.
    with ctx.temp_override(window=win, area=area, region=region):
        bpy.ops.caffmob.wall_editor('INVOKE_DEFAULT')
    yield 1.5
    s = props.session()
    ewin, earea, ereg = w2d.editor_area(ctx)
    from caffmob_draw import hb_types
    lengths_before = sorted(round(hb_types.GeoNodeWall(w).get_input('Length'), 4) for w in walls)
    ci, si = 0, 0
    s.selected = (ci, si)
    s.plan.chains[ci].set_length(si, s.plan.chains[ci].length(si) + 0.5)
    mx, my = ereg.x + 40, ereg.y + 40
    ev(ewin, 'MOUSEMOVE', 'NOTHING', mx, my)
    ev(ewin, 'ESC', 'PRESS', mx, my)
    ev(ewin, 'ESC', 'RELEASE', mx, my)
    yield 0.3
    check("Esc com alterações pergunta antes de descartar", s.prompt == 'discard' and props.session() is not None,
          f"prompt={s.prompt}")
    _box, yes, no = ops_editor._prompt_rects(ereg)
    yield from tap(ewin, ereg.x + no[0] + 10, ereg.y + no[1] + 10)
    yield 0.3
    check("'Não' mantém o editor aberto", props.session() is not None and s.prompt is None)
    ev(ewin, 'ESC', 'PRESS', mx, my)
    ev(ewin, 'ESC', 'RELEASE', mx, my)
    yield 0.3
    yield from tap(ewin, ereg.x + yes[0] + 10, ereg.y + yes[1] + 10)
    yield 1.0
    lengths_after = sorted(round(hb_types.GeoNodeWall(w).get_input('Length'), 4) for w in walls)
    check("'Sim' descarta, fecha e não muda o 3D", props.session() is None and lengths_after == lengths_before,
          f"{lengths_before} → {lengths_after}")

    # 3. Ímã no editor: com 3 trechos, o clique a 10 px do início pergunta (D-33).
    for w in list(walls):
        bpy.data.objects.remove(w, do_unlink=True)
    yield 0.3
    with ctx.temp_override(window=win, area=area, region=region):
        bpy.ops.caffmob.wall_editor('INVOKE_DEFAULT')
    yield 1.5
    s = props.session()
    ewin, earea, ereg = w2d.editor_area(ctx)
    ctx.window_manager.btm_wall_editor.tool = 'DRAW'
    view = s.view

    def scr2(pt):
        p = view.to_screen(pt)
        return ereg.x + p[0], ereg.y + p[1]

    for pt in ((0.0, 0.0), (3.0, 0.0), (3.0, 2.0), (0.0, 2.0)):
        yield from tap(ewin, *scr2(pt))
        yield 0.15
    sx, sy = scr2((0.0, 0.0))
    ev(ewin, 'MOUSEMOVE', 'NOTHING', sx + 10, sy + 3)
    yield 0.15
    yield from tap(ewin, sx + 10, sy + 3)
    yield 0.3
    check("ímã do editor: clique a 10 px do início pergunta", s.prompt == 'close' and len(s.drawing.nodes) == 4,
          f"prompt={s.prompt} nós={len(s.drawing.nodes) if s.drawing else None}")
    s.request = 'cancel'
    yield 1.0

    # 4. "Desenhar Paredes" 3D: ímã de 15 px, pergunta, Enter fecha (D-39).
    area, region, rv3d = view3d(win)
    with ctx.temp_override(window=win, area=area, region=region):
        bpy.ops.view3d.view_axis(type='TOP')
    rv3d.view_location = (1.5, 1.0, 0.0)
    rv3d.view_distance = 8.0
    yield 0.4

    def to_win(co):
        p = view3d_utils.location_3d_to_region_2d(region, rv3d, Vector(co))
        return region.x + p.x, region.y + p.y

    before = {o.name for o in scene.objects if o.get('IS_WALL_BP')}
    with ctx.temp_override(window=win, area=area, region=region):
        r = bpy.ops.caffmob_walls.draw_walls('INVOKE_DEFAULT')
    yield 0.4
    for co in ((0.0, 0.0, 0.0), (3.0, 0.0, 0.0), (3.0, 2.0, 0.0), (0.0, 2.0, 0.0)):
        x, y = to_win(co)
        for k in range(3):
            ev(win, 'MOUSEMOVE', 'NOTHING', x + k, y)
            yield 0.05
        yield from tap(win, x + 2, y)
        yield 0.2
    sx, sy = to_win((0.0, 0.0, 0.0))
    for k in range(3):
        ev(win, 'MOUSEMOVE', 'NOTHING', sx + 8 + k, sy + 4)
        yield 0.05
    yield from tap(win, sx + 10, sy + 4)
    yield 0.3
    asked = 'CAFFMOB_WALLS_OT_draw_walls' in [m for m in modal_ids(ctx)] or 'CAFFMOB_WALLS_OT_draw_walls' in \
        modal_ids(ctx)
    ev(win, 'RET', 'PRESS', sx + 10, sy + 4)
    ev(win, 'RET', 'RELEASE', sx + 10, sy + 4)
    yield 0.5
    new_walls = [o for o in scene.objects if o.get('IS_WALL_BP') and o.name not in before]
    from caffmob_draw.walls2d import scene_io
    chains = scene_io.read_plan(scene).chains
    closed = any(c.closed and c.segment_count() == 4 for c in chains)
    check("Desenhar Paredes 3D: ímã pergunta (modal continua após o clique)", asked, f"r={r} modais={modal_ids(ctx)}")
    check("Desenhar Paredes 3D: Enter fecha a sala", closed and len(new_walls) == 4,
          f"paredes={len(new_walls)} cadeias={[(c.closed, c.segment_count()) for c in chains]}")


_gen = script()


def tick():
    try:
        return next(_gen)
    except StopIteration:
        pass
    except Exception:
        traceback.print_exc()
        FAILURES.append("exceção no roteiro")
    print(f"blender_002_ui_events: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}", flush=True)
    os._exit(1 if FAILURES else 0)        # instância de teste própria: encerra com o código do resultado


bpy.app.timers.register(tick, first_interval=2.0)

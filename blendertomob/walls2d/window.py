"""Janela do Editor de Paredes (T028; D-02).

Abre a planta numa **janela própria**: duplica a área 3D atual numa janela nova (`screen.area_dupli`) e troca o tipo
dessa área para Image Editor sem imagem — a tela 2D. A região lateral (N) do Image Editor recebe os painéis do editor.
Se a janela nova não puder ser criada, o editor ocupa a própria área atual e devolve o tipo original ao fechar.

O desenho da planta é um handler `SpaceImageEditor.draw_handler_add(... 'POST_PIXEL')`, registrado uma vez no
`register()` e removido no `unregister()`; ele só desenha na área marcada pela sessão (`props.Session.area_ptr`).
"""

import bpy  # type: ignore

from . import props

_draw_handle = []


def editor_area(context):
    """(janela, área, região principal) do editor aberto, ou (None, None, None)."""
    s = props.session()
    if s is None:
        return None, None, None
    for window in context.window_manager.windows:
        for area in window.screen.areas:
            if area.as_pointer() == s.area_ptr:
                region = next((r for r in area.regions if r.type == 'WINDOW'), None)
                return window, area, region
    return None, None, None


def side_panel(area):
    """Região lateral (N) visível da área, ou None."""
    ui = next((r for r in area.regions if r.type == 'UI'), None) if area is not None else None
    return ui if ui is not None and ui.width > 1 and ui.height > 1 else None


def over_side_panel(area, mouse_x, mouse_y):
    """O mouse (coordenadas da janela) está sobre o painel lateral? Com a sobreposição de regiões ligada (padrão do
    Blender), o painel fica por cima da região da planta, então o modal precisa deixar esses eventos passarem."""
    ui = side_panel(area)
    return ui is not None and ui.x <= mouse_x < ui.x + ui.width and ui.y <= mouse_y < ui.y + ui.height


def visible_width(area, region):
    """Largura da planta que não fica atrás do painel lateral (sobreposição de regiões)."""
    ui = side_panel(area)
    if ui is None or ui.x <= region.x or ui.x >= region.x + region.width:
        return float(region.width)
    return float(ui.x - region.x)


def is_editor_area(context):
    s = props.session()
    return s is not None and context.area is not None and context.area.as_pointer() == s.area_ptr


def _prepare(area):
    area.type = 'IMAGE_EDITOR'
    space = area.spaces.active
    space.image = None
    space.show_region_ui = True
    # Só a planta: sem os menus e as ferramentas de imagem do Image Editor.
    space.show_region_toolbar = False
    space.show_region_tool_header = False
    area.show_menus = False
    space.show_region_header = False          # sem View/New/Open do Image Editor: só a planta e o painel
    return next((r for r in area.regions if r.type == 'WINDOW'), None)


EDITOR_CATEGORY = "Editor de Paredes"


def focus_editor_tab(area):
    """Põe a região lateral na aba do editor (e não na "Tool" do Image Editor). A aba só existe depois do primeiro
    desenho da região; devolve True quando ficou ativa."""
    ui = next((r for r in area.regions if r.type == 'UI'), None) if area is not None else None
    if ui is None:
        return False
    if ui.active_panel_category != EDITOR_CATEGORY:
        try:
            ui.active_panel_category = EDITOR_CATEGORY
        except (TypeError, AttributeError, ValueError):
            return False
        area.tag_redraw()
    return ui.active_panel_category == EDITOR_CATEGORY


def open_editor(context):
    """Abre a janela do editor. Devolve (janela, área, região) ou levanta RuntimeError."""
    s = props.session()
    source = context.area if context.area is not None and context.area.type == 'VIEW_3D' else None
    window = area = None
    if source is not None and context.window is not None:
        before = {w.as_pointer() for w in context.window_manager.windows}
        try:
            with context.temp_override(window=context.window, area=source):
                bpy.ops.screen.area_dupli('INVOKE_DEFAULT')
        except RuntimeError:
            pass
        new = [w for w in context.window_manager.windows if w.as_pointer() not in before]
        if new:
            window = new[0]
            area = max(window.screen.areas, key=lambda a: a.width * a.height)
    if area is None:
        if context.area is None or context.window is None:
            raise RuntimeError("O Editor de Paredes precisa de uma janela do Blender aberta.")
        window, area = context.window, context.area
        s.restore_area_type = area.type
    region = _prepare(area)
    s.window_ptr = window.as_pointer()
    s.area_ptr = area.as_pointer()
    return window, area, region


def _close(window_ptr, area_ptr, restore_area_type):
    wm = bpy.context.window_manager
    for win in wm.windows:
        for area in win.screen.areas:
            if area.as_pointer() != area_ptr:
                continue
            if restore_area_type:
                area.show_menus = True
                area.spaces.active.show_region_header = True
                area.type = restore_area_type
            elif win.as_pointer() == window_ptr and len(wm.windows) > 1:
                try:
                    with bpy.context.temp_override(window=win):
                        bpy.ops.wm.window_close()
                except RuntimeError:
                    area.type = 'VIEW_3D'
            return None
    return None


def close_later(window_ptr, area_ptr, restore_area_type):
    """Fecha a janela (ou devolve o tipo da área) num timer, fora do modal que está rodando nela."""
    bpy.app.timers.register(lambda: _close(window_ptr, area_ptr, restore_area_type), first_interval=0.05)


def _draw():
    if is_editor_area(bpy.context):
        from . import ops_editor
        ops_editor.draw_plan(bpy.context)


def register():
    if not _draw_handle:
        _draw_handle.append(bpy.types.SpaceImageEditor.draw_handler_add(_draw, (), 'WINDOW', 'POST_PIXEL'))


def unregister():
    while _draw_handle:
        bpy.types.SpaceImageEditor.draw_handler_remove(_draw_handle.pop(), 'WINDOW')

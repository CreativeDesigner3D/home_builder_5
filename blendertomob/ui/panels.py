"""
BlenderToMob UI Panels — Interface de Marcenaria e CAD Paramétrico
Organizada em abas (CONSTRUTOR, GALERIA, CONFIGURAÇÕES e PLANO DE CORTE)
com suporte integral a Português do Brasil (pt_BR) e unidades dinâmicas (mm, cm, m).
"""

import bpy  # type: ignore


# ==========================================================================
# Helpers de cena
# ==========================================================================

def _scene_has_walls(context):
    for obj in context.scene.objects:
        if hasattr(obj, 'btm_plane') and obj.btm_plane.object_kind == 'WALL':
            return True
    return False


# ==========================================================================
# Blocos reutilizáveis: Padrão de Dimensões e Plano de Corte (T039)
# ==========================================================================

SUMMARY_KEYS = (
    ('COZ.sheets.LAT.thickness', "Lateral"),
    ('COZ.sheets.FUN_INF.thickness', "Fundo"),
    ('COZ.sheets.POR.thickness', "Portas"),
    ('COZ.sheets.PRAT.thickness', "Prateleiras"),
    ('COZ.external.base_height', "Altura balcão"),
    ('COZ.external.base_depth', "Prof. balcão"),
)


def draw_standards_box(layout, context):
    """Definição ativa, Configurador e gestão das definições."""
    from ..data import dimension_schema as schema
    from ..standards import api
    scene = context.scene
    box = layout.box()
    box.label(text="Padrão de Dimensões", icon='CON_SIZELIMIT')
    definition = api.active_definition(scene)
    row = box.row(align=True)
    row.operator_menu_enum("btm.standards_set_active", "definition",
                           text=definition.name if definition else "Nenhuma definição",
                           icon='LOCKED' if definition is not None and definition.builtin else 'PRESET')
    row.operator("btm.standards_duplicate", text="", icon='DUPLICATE')
    row.operator("btm.standards_rename", text="", icon='GREASEPENCIL')
    row.operator("btm.standards_delete", text="", icon='TRASH')

    col = box.column()
    col.scale_y = 1.3
    col.operator("btm.standards_configurator", text="Abrir Configurador de Dimensões", icon='WINDOW')

    if definition is not None:
        unit = api.user_unit(scene)
        grid = box.grid_flow(columns=2, even_columns=True, align=True)
        for key, title in SUMMARY_KEYS:
            param = schema.get_param(key)
            value = api.get_definition_value(definition, key)
            grid.label(text=f"{title}: {api.format_param_value(param, value, unit)}")

    sub = box.column(align=True)
    row = sub.row(align=True)
    row.operator("btm.standards_import_json", text="Importar", icon='IMPORT')
    row.operator("btm.standards_export_json", text="Exportar", icon='EXPORT')
    row = sub.row(align=True)
    row.operator("btm.standards_import_promob", text="Importar do Promob", icon='IMPORT')
    row.operator("btm.standards_export_promob", text="Exportar p/ Promob", icon='EXPORT')


def draw_inspection_box(layout, context):
    """Inspeção de portas e gavetas: modo de clique, abrir/fechar tudo, salvar fechado e interferência (T076)."""
    state = getattr(context.window_manager, 'btm_inspection', None)
    settings = context.scene.btm_settings
    box = layout.box()
    box.label(text="Inspeção de Portas e Gavetas", icon='HIDE_OFF')
    if state is None:
        box.label(text="Inspeção indisponível.", icon='ERROR')
        return
    row = box.row()
    row.scale_y = 1.2
    row.operator("btm.inspect_fronts", text="Sair do Modo de Abrir" if state.active else "Abrir Portas e Gavetas",
                 icon='CANCEL' if state.active else 'RESTRICT_SELECT_OFF', depress=state.active)
    move_over = getattr(context.window_manager, 'btm_move_over', None)
    if move_over is not None:
        row = box.row()
        row.scale_y = 1.2
        row.prop(move_over, "enabled", toggle=True, icon='ORIENTATION_GIMBAL',
                 text="Sair do Mover Sobre" if move_over.enabled else "Mover Sobre (botão direito)")
    row = box.row(align=True)
    op = row.operator("btm.fronts_set_open", text="Abrir tudo 90°", icon='TRIA_RIGHT_BAR')
    op.scope, op.mode = 'ALL', 'OPEN_90'
    op = row.operator("btm.fronts_set_open", text="45°")
    op.scope, op.mode = 'ALL', 'OPEN_45'
    op = row.operator("btm.fronts_set_open", text="Fechar tudo", icon='TRIA_LEFT_BAR')
    op.scope, op.mode = 'ALL', 'CLOSE'
    col = box.column(align=True)
    col.prop(state, "default_angle", text="Ângulo do clique")
    col.prop(state, "snap_stops")
    col.prop(settings, "save_fronts_open")

    sub = box.box()
    sub.operator("btm.check_front_interference", text="Verificar Interferência", icon='MOD_PHYSICS')
    if state.checked_fronts < 0:
        sub.label(text="Ainda não verificado.", icon='INFO')
    elif state.checked_fronts == 0:
        sub.label(text="Nenhuma frente verificada.", icon='INFO')
    elif not state.interferences:
        sub.label(text=f"Sem interferência em {state.checked_fronts} frente(s).", icon='CHECKMARK')
    else:
        warn = sub.column(align=True)
        warn.alert = True
        warn.label(text=f"{len(state.interferences)} interferência(s) em {state.checked_fronts} frente(s):",
                   icon='ERROR')
        for index, item in enumerate(state.interferences[:8]):
            row = sub.row(align=True)
            row.label(text=f"{item.module_name} › {item.front_name} × {item.hit_name}")
            row.operator("btm.interference_goto", text="", icon='VIEWZOOM').index = index
        if len(state.interferences) > 8:
            sub.label(text=f"… e mais {len(state.interferences) - 8}")


def draw_cut_plan(layout, context, compact=False):
    """Cálculo, aviso de desatualizado, incompatíveis e exportações do plano de corte."""
    from ..data import units as btm_units
    from ..operators import ops_cutting
    scene = context.scene
    settings = scene.btm_settings

    if settings.cut_plan_stale and "btm_nesting_sheets_count" in scene:
        warn = layout.box()
        warn.alert = True
        warn.label(text="O projeto mudou: recalcule o plano de corte.", icon='ERROR')

    row = layout.row(align=True)
    row.scale_y = 1.3
    row.operator("btm.calculate_nesting", text="Calcular Plano de Corte", icon='PLAY')

    col = layout.column(align=True)
    row = col.row(align=True)
    row.operator("btm.export_cut_plan_json", text="Exportar JSON Global", icon='EXPORT')
    row.operator("btm.export_parts_csv", text="Exportar Peças (CSV)", icon='SPREADSHEET')
    if not compact:
        col.operator("btm.import_cut_plan_json", text="Importar JSON Global", icon='IMPORT')
        col.prop(settings, "cut_include_client")

    box = layout.box()
    box.label(text=scene.get("btm_nesting_result", "Nenhuma otimização calculada."), icon='INFO')
    if compact:
        return

    if "btm_nesting_sheets_count" in scene:
        col = box.column(align=True)
        col.label(text=f"Total de peças: {scene.get('btm_nesting_parts_count', 0)}")
        col.label(text=f"Chapas necessárias: {scene.get('btm_nesting_sheets_count', 0)}")
        col.label(text=f"Aproveitamento: {scene.get('btm_nesting_utilization', 0.0)}%")

    incompatible = ops_cutting.incompatible_parts(scene)
    if incompatible:
        bad = layout.box()
        bad.alert = True
        bad.label(text=f"Peças maiores que o limite de chapa: {len(incompatible)}", icon='ERROR')
        col = bad.column(align=True)
        for item in incompatible[:10]:
            size = (f"{btm_units.format_value(item['length'] / 1000.0, scene)} × "
                    f"{btm_units.format_value(item['width'] / 1000.0, scene)}")
            reason = "comprimento" if item['status'] == 'EXCEEDS_LENGTH' else "largura"
            col.label(text=f"{item['module']} › {item['name']}: {size} (excede {reason})")
        if len(incompatible) > 10:
            col.label(text=f"… e mais {len(incompatible) - 10}")


# ==========================================================================
# PAINEL PRINCIPAL: Criador de Ambientes (Blender to Mob)
# ==========================================================================

class BTM_PT_EnvironmentBuilder(bpy.types.Panel):
    bl_label = "Blender to Mob"
    bl_idname = "BTM_PT_environment_builder"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Blender to Mob"
    bl_order = 0

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        settings = scene.btm_settings
        hb_scene = getattr(scene, 'home_builder', None)

        # Seletor de Abas (Segmented Buttons)
        row = layout.row(align=True)
        row.scale_y = 1.3
        row.prop(settings, "btm_active_tab", expand=True)

        layout.separator(factor=0.8)

        tab = settings.btm_active_tab

        # ------------------------------------------------------------------
        # ABA: CONSTRUTOR
        # ------------------------------------------------------------------
        if tab == 'CONSTRUTOR':
            # Seção: Paredes e Piso
            box = layout.box()
            box.label(text="Paredes & Piso", icon='GREASEPENCIL')
            grid = box.grid_flow(columns=2, even_columns=True, even_rows=True, align=True)
            grid.operator("home_builder_walls.draw_walls", text="Desenhar Paredes", icon='GREASEPENCIL')
            grid.operator("btm.wall_editor", text="Editor de Paredes", icon='MESH_GRID')
            grid.operator("btm.adjust_floor", text="Ajustar Piso", icon='MESH_GRID')
            grid.operator("btm.floor_builder", text="Piso Manual", icon='MESH_PLANE')
            grid.operator("home_builder_walls.add_ceiling", text="Criar Teto", icon='MESH_CUBE')

            # Seção: Aberturas
            box = layout.box()
            box.label(text="Aberturas & Vãos", icon='MOD_BOOLEAN')
            grid = box.grid_flow(columns=2, even_columns=True, even_rows=True, align=True)
            grid.operator("home_builder_doors_windows.place_door", text="Porta Simples", icon='IMPORT')
            grid.operator("home_builder_doors_windows.place_double_door", text="Porta Dupla", icon='EXPORT')
            grid.operator("home_builder_doors_windows.place_window", text="Janela", icon='MESH_GRID')
            grid.operator("home_builder_doors_windows.place_open_door", text="Vão Livre", icon='WORLD')

            # Seção: Módulos & Iluminação
            box = layout.box()
            box.label(text="Mobiliário & Iluminação", icon='LIGHT')
            grid = box.grid_flow(columns=2, even_columns=True, even_rows=True, align=True)
            grid.operator("btm.cabinet_builder", text="Módulo Rápido", icon='OUTLINER_OB_MESH')
            grid.operator("btm.standards_configurator", text="Config. Dimensões", icon='PREFERENCES')
            grid.operator("home_builder_walls.add_room_lights", text="Luzes do Quarto", icon='LIGHT')
            grid.operator("home_builder_obstacles.place_obstacle", text="Inserir Obstáculo", icon='ERROR')
            grid.operator("btm.geometry_create", text="Placa", icon='MESH_PLANE').kind = 'PLACA'
            grid.operator("btm.geometry_create", text="Caixa", icon='MESH_CUBE').kind = 'CAIXA'

            # Seção: Inspeção (abrir portas e gavetas, interferência)
            draw_inspection_box(layout, context)

        # ------------------------------------------------------------------
        # ABA: GALERIA DE MÓDULOS
        # ------------------------------------------------------------------
        elif tab == 'GALERIA':
            if hb_scene is None:
                layout.label(text="Biblioteca de módulos indisponível", icon='ERROR')
                return

            layout.prop(hb_scene, "product_tab", text="Biblioteca")
            layout.separator(factor=0.5)

            box = layout.box()
            if hb_scene.product_tab == 'FRAMELESS' and hasattr(scene, 'hb_frameless'):
                scene.hb_frameless.draw_library_ui(box, context)
            elif hb_scene.product_tab == 'FACE FRAME' and hasattr(scene, 'hb_face_frame'):
                scene.hb_face_frame.draw_library_ui(box, context)
            elif hasattr(scene, 'hb_closets'):
                scene.hb_closets.draw_library_ui(box, context)

        # ------------------------------------------------------------------
        # ABA: CONFIGURAÇÕES (Unidades, Dimensões e Limites MDF)
        # ------------------------------------------------------------------
        elif tab == 'CONFIGURACOES':
            # 1. Unidades e Snap
            box_unit = layout.box()
            box_unit.label(text="Unidade & Precisão", icon='SCENE_DATA')
            col = box_unit.column(align=True)
            col.prop(settings, "btm_unit", text="Unidade do Projeto")
            col.prop(settings, "snap_grid", text="Atrair ao Grid (Snap)")
            if settings.snap_grid:
                col.prop(settings, "snap_increment", text="Incremento do Snap")
            col.prop(settings, "collision_global", text="Evitar Sobreposição")

            # 2. Padrão de Dimensões (Configurador de Dimensões)
            draw_standards_box(layout, context)

            # 3. Limites e Especificações de Chapas MDF
            box_mdf = layout.box()
            box_mdf.label(text="Limites & Configurações de Chapas MDF", icon='STICKY_UVS_DISABLE')
            mdf = settings.mdf_config

            col_mdf = box_mdf.column(align=True)
            col_mdf.prop(mdf, "sheet_format", text="Formato")
            col_mdf.prop(mdf, "sheet_width", text="Largura")
            col_mdf.prop(mdf, "sheet_height", text="Comprimento/Altura")

            box_refilo = box_mdf.box()
            box_refilo.label(text="Refilos (Descarte de Bordas)", icon='ARROW_LEFTRIGHT')
            grid_ref = box_refilo.grid_flow(columns=2, align=True)
            grid_ref.prop(mdf, "refilo_top", text="Superior")
            grid_ref.prop(mdf, "refilo_bottom", text="Inferior")
            grid_ref.prop(mdf, "refilo_left", text="Esquerdo")
            grid_ref.prop(mdf, "refilo_right", text="Direito")

            col_mdf.prop(mdf, "kerf", text="Lâmina de Serra (Kerf)")
            col_mdf.prop(mdf, "allow_rotation", text="Permitir Rotação de Peças")
            col_mdf.prop(mdf, "respect_grain", text="Respeitar Veio da Madeira")

            # 4. Gerenciador de Ambientes e Elevações
            if hb_scene is not None:
                from .. import hb_project
                room_scenes = hb_project.get_room_scenes()
                room_scenes.sort(key=lambda s: s.home_builder.sort_order if hasattr(s, 'home_builder') else 0)

                box_rooms = layout.box()
                box_rooms.label(text="Gerenciador de Ambientes", icon='HOME')

                col_rooms = box_rooms.column(align=True)
                for r_scene in room_scenes:
                    row = col_rooms.row(align=True)
                    is_selected = r_scene == context.scene
                    icon = 'CHECKBOX_HLT' if is_selected else 'CHECKBOX_DEHLT'

                    op = row.operator("blendertomob.switch_room", text=r_scene.name, icon=icon)
                    op.scene_name = r_scene.name

                    if len(room_scenes) > 1:
                        del_op = row.operator("blendertomob.delete_room", text="", icon='X')
                        del_op.scene_name = r_scene.name

                row_actions = box_rooms.row(align=True)
                row_actions.operator("blendertomob.create_room", text="Novo Ambiente", icon='ADD')
                row_actions.operator("blendertomob.rename_room", text="Renomear", icon='GREASEPENCIL')

        # ------------------------------------------------------------------
        # ABA: PLANO DE CORTE (Nesting & Exportação JSON)
        # ------------------------------------------------------------------
        elif tab == 'PLANO_CORTE':
            box_actions = layout.box()
            box_actions.label(text="Lista de Peças e Plano de Corte", icon='ALIGN_JUSTIFY')
            draw_cut_plan(box_actions, context)


# ==========================================================================
# PAINEL: Plano de Corte (Nesting)
# ==========================================================================

class BTM_PT_NestingPanel(bpy.types.Panel):
    bl_label = "Plano de Corte (Nesting)"
    bl_idname = "BTM_PT_nesting_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Blender to Mob"
    bl_order = 2
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.label(text="Otimizador de Chapas MDF", icon='ALIGN_JUSTIFY')
        draw_cut_plan(layout, context, compact=True)


# ==========================================================================
# Registro
# ==========================================================================

classes = (
    BTM_PT_EnvironmentBuilder,
    BTM_PT_NestingPanel,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

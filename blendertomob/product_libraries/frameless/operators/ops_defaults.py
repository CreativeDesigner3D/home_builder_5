import bpy
from .... import hb_utils, hb_project, hb_types

# ---------------------------------------------------------------------------------------------------------------
# Funções de atualização (chamadas pela sincronização do Padrão de Dimensões, standards/sync.py, e pelos operadores)
#
# `skip(obj, prompt_name)` permite pular medidas editadas à mão (btm_overrides, RN-23); None = atualizar tudo.
# Cada função devolve a quantidade de objetos alterados.
# ---------------------------------------------------------------------------------------------------------------

TOE_KICK_TYPE_INDEX = {
    'Notch Ends to Floor': 0,
    'Ladder Style': 1,
    'Floating': 2,
    'Leg Levelers': 3,
}

BASE_TOP_CONSTRUCTION_INDEX = {
    'Full Top': 0,
    'Stretchers': 1,
}


def _set_prompt(obj, name, value, skip):
    if name not in obj or (skip and skip(obj, name)):
        return False
    if obj[name] == value:
        return False
    obj[name] = value
    return True


def update_toe_kick_prompts(context, skip=None):
    """Aplica altura, recuo e tipo de rodapé padrão da cena a todos os objetos com esses prompts."""
    props = context.scene.hb_frameless
    type_index = TOE_KICK_TYPE_INDEX.get(props.default_toe_kick_type, 0)
    count = 0
    for obj in context.scene.objects:
        changed = _set_prompt(obj, 'Toe Kick Height', props.default_toe_kick_height, skip)
        changed |= _set_prompt(obj, 'Toe Kick Setback', props.default_toe_kick_setback, skip)
        changed |= _set_prompt(obj, 'Toe Kick Type', type_index, skip)
        if changed:
            hb_utils.run_calc_fix(context, obj)
            count += 1
    return count


def update_material_thickness_prompts(context, skip=None):
    """Aplica a espessura padrão da caixa a `Material Thickness` e às espessuras usadas no cálculo das frentes."""
    thickness = context.scene.hb_frameless.default_carcass_part_thickness
    count = 0
    for obj in context.scene.objects:
        changed = _set_prompt(obj, 'Material Thickness', thickness, skip)
        for key in ('Left Thickness', 'Right Thickness', 'Top Thickness', 'Bottom Thickness'):
            changed |= _set_prompt(obj, key, thickness, skip)
        if changed:
            hb_utils.run_calc_fix(context, obj)
            count += 1
    return count


def update_base_top_construction_prompts(context, skip=None):
    """Aplica a construção do topo dos inferiores (tampo inteiro ou travessas) aos gabinetes BASE existentes.

    Gabinetes com avental de pia (índice 2) são mantidos: é uma escolha do módulo, não do padrão.
    """
    props = hb_project.get_main_scene().hb_frameless
    index = BASE_TOP_CONSTRUCTION_INDEX.get(props.base_top_construction)
    if index is None:
        return 0
    count = 0
    for obj in context.scene.objects:
        if not obj.get('IS_FRAMELESS_CABINET_CAGE') or obj.get('CABINET_TYPE') != 'BASE':
            continue
        if obj.get('Base Top Construction') == 2:
            continue
        if _set_prompt(obj, 'Base Top Construction', index, skip):
            hb_utils.run_calc_fix(context, obj)
            count += 1
    return count


def update_drawer_front_height_prompts(context, new_height, old_height, skip=None):
    """Troca a altura fixa das gavetas superiores que seguiam o padrão anterior (`old_height`).

    A altura da gaveta superior é gravada na criação como `Opening 1 Height` fixo da calculadora do splitter;
    só os valores iguais ao padrão anterior mudam — alturas escolhidas à mão são preservadas.
    """
    if old_height is None or abs(new_height - old_height) < 1e-9:
        return 0
    count = 0
    for obj in context.scene.objects:
        calculators = getattr(getattr(obj, 'home_builder', None), 'calculators', None)
        if not calculators:
            continue
        if skip and skip(obj, 'Opening 1 Height'):
            continue
        for calculator in calculators:
            prompt = calculator.get_calculator_prompt('Opening 1 Height')
            if prompt is None or prompt.equal:
                continue
            if abs(prompt.distance_value - old_height) < 1e-6:
                prompt.distance_value = new_height
                calculator.calculate()
                count += 1
    return count


def update_cabinet_sizes(context, skip=None):
    """Aplica profundidade e altura padrão da cena aos gabinetes frameless conforme o tipo (BASE/TALL/UPPER)."""
    props = hb_project.get_main_scene().hb_frameless
    sizes = {
        'BASE': (props.base_cabinet_depth, props.base_cabinet_height),
        'TALL': (props.tall_cabinet_depth, props.tall_cabinet_height),
        'UPPER': (props.upper_cabinet_depth, props.upper_cabinet_height),
    }
    count = 0
    for obj in context.scene.objects:
        if not obj.get('IS_FRAMELESS_CABINET_CAGE'):
            continue
        size = sizes.get(obj.get('CABINET_TYPE', ''))
        if size is None:
            continue
        cabinet = hb_types.GeoNodeObject(obj)
        changed = False
        for input_name, value in (('Dim Y', size[0]), ('Dim Z', size[1])):
            if skip and skip(obj, input_name):
                continue
            if abs(cabinet.get_input(input_name) - value) > 1e-9:
                cabinet.set_input(input_name, value)
                changed = True
        if changed:
            count += 1
    return count


# ---------------------------------------------------------------------------------------------------------------
# Operadores (atalhos para as funções acima)
# ---------------------------------------------------------------------------------------------------------------

class hb_frameless_OT_update_toe_kick_prompts(bpy.types.Operator):
    bl_idname = "hb_frameless.update_toe_kick_prompts"
    bl_label = "Update Toe Kick Prompts"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        count = update_toe_kick_prompts(context)
        self.report({'INFO'}, f"Rodapé atualizado em {count} objeto(s)")
        return {'FINISHED'}


class hb_frameless_OT_update_material_thickness_prompts(bpy.types.Operator):
    bl_idname = "hb_frameless.update_material_thickness_prompts"
    bl_label = "Update Material Thickness Prompts"
    bl_description = "Update all cabinets in the project with the current material thickness"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        count = update_material_thickness_prompts(context)
        self.report({'INFO'}, f"Espessura atualizada em {count} objeto(s)")
        return {'FINISHED'}


class hb_frameless_OT_update_base_top_construction_prompts(bpy.types.Operator):
    bl_idname = "hb_frameless.update_base_top_construction_prompts"
    bl_label = "Update Base Top Construction Prompts"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        count = update_base_top_construction_prompts(context)
        self.report({'INFO'}, f"Topo atualizado em {count} gabinete(s)")
        return {'FINISHED'}


class hb_frameless_OT_update_drawer_front_height_prompts(bpy.types.Operator):
    bl_idname = "hb_frameless.update_drawer_front_height_prompts"
    bl_label = "Update Drawer Front Height Prompts"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = hb_project.get_main_scene().hb_frameless
        scene = context.scene
        old_height = scene.get('btm_last_top_drawer_front_height')
        count = update_drawer_front_height_prompts(context, props.top_drawer_front_height, old_height)
        scene['btm_last_top_drawer_front_height'] = props.top_drawer_front_height
        self.report({'INFO'}, f"Altura da gaveta superior atualizada em {count} vão(s)")
        return {'FINISHED'}


class hb_frameless_OT_update_door_and_drawer_front_style(bpy.types.Operator):
    """Update all door and drawer fronts with the selected door style"""
    bl_idname = "hb_frameless.update_door_and_drawer_front_style"
    bl_label = "Update Door and Drawer Front Style"
    bl_options = {'REGISTER', 'UNDO'}

    selected_index: bpy.props.IntProperty(name="Selected Index", default=-1)# type: ignore

    def execute(self, context):
        main_scene = hb_project.get_main_scene()
        frameless_props = main_scene.hb_frameless

        if self.selected_index < 0 or self.selected_index >= len(frameless_props.door_styles):
            self.report({'WARNING'}, "Invalid door style index")
            return {'CANCELLED'}

        selected_door_style = frameless_props.door_styles[self.selected_index]
        success_count = 0
        skip_count = 0

        for obj in context.scene.objects:
            if 'IS_DOOR_FRONT' in obj or 'IS_DRAWER_FRONT' in obj:
                result = selected_door_style.assign_style_to_front(obj)
                if result:
                    success_count += 1
                else:
                    skip_count += 1

        if skip_count > 0:
            self.report({'WARNING'}, f"Updated {success_count} front(s), skipped {skip_count} (too small for style)")
        else:
            self.report({'INFO'}, f"Updated {success_count} front(s) with style '{selected_door_style.name}'")
        return {'FINISHED'}


class hb_frameless_OT_update_cabinet_sizes(bpy.types.Operator):
    bl_idname = "hb_frameless.update_cabinet_sizes"
    bl_label = "Update Cabinet Sizes"
    bl_description = "Update all cabinet depths and heights to match the current size settings"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        try:
            count = update_cabinet_sizes(context)
        except Exception as exc:
            self.report({'WARNING'}, f"Não foi possível atualizar os gabinetes: {exc}")
            return {'CANCELLED'}
        if count:
            self.report({'INFO'}, f"{count} gabinete(s) atualizado(s)")
        else:
            self.report({'INFO'}, "Nenhum gabinete a atualizar")
        return {'FINISHED'}


classes = (
    hb_frameless_OT_update_toe_kick_prompts,
    hb_frameless_OT_update_material_thickness_prompts,
    hb_frameless_OT_update_base_top_construction_prompts,
    hb_frameless_OT_update_drawer_front_height_prompts,
    hb_frameless_OT_update_door_and_drawer_front_style,
    hb_frameless_OT_update_cabinet_sizes,
)

def register():
    for cls in classes:
        reg_cls = getattr(bpy.types, cls.__name__, None)
        if reg_cls:
            try:
                bpy.utils.unregister_class(reg_cls)
            except Exception:
                pass
        try:
            bpy.utils.register_class(cls)
        except Exception:
            pass


def unregister():
    for cls in reversed(classes):
        reg_cls = getattr(bpy.types, cls.__name__, None)
        if reg_cls:
            try:
                bpy.utils.unregister_class(reg_cls)
            except Exception:
                pass

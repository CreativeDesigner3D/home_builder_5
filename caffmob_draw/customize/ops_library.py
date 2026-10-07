"""Operadores da biblioteca de módulos do usuário (feature 003, T029; RF-07 a RF-10, D-10, D-11)."""

import math
import os
import platform
import subprocess

import bpy  # type: ignore
from mathutils import Vector  # type: ignore

from .. import hb_placement, hb_snap
from . import adapters, library_io


def _entry(filepath):
    for entry in library_io.list_modules():
        if entry["blend"] == filepath:
            return entry
    return None


def _redraw(context):
    for area in (context.screen.areas if context.screen else []):
        area.tag_redraw()


class BTM_OT_ModuleSave(bpy.types.Operator):
    """Salva o módulo selecionado, com a personalização, na biblioteca do usuário"""
    bl_idname = "caffmob.module_save"
    bl_label = "Salvar como módulo"
    bl_options = {'REGISTER'}

    module_name: bpy.props.StringProperty(name="Nome")  # type: ignore
    category: bpy.props.StringProperty(name="Categoria", default=library_io.GENERAL)  # type: ignore
    overwrite: bpy.props.BoolProperty(name="Substituir o módulo existente", default=False)  # type: ignore
    thumbnail: bpy.props.BoolProperty(name="Gerar miniatura", default=True)  # type: ignore

    @classmethod
    def poll(cls, context):
        return adapters.for_object(context.active_object)[1] is not None

    def invoke(self, context, event):
        root = adapters.module_root(context.active_object)
        self.module_name = root.name
        self.overwrite = False
        return context.window_manager.invoke_props_dialog(self, width=360)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "module_name")
        layout.prop(self, "category")
        layout.prop(self, "thumbnail")
        if self.module_name.strip() and library_io.exists(self.module_name, self.category):
            box = layout.box()
            box.alert = True
            box.label(text="Já existe um módulo com esse nome nesta categoria.", icon='ERROR')
            box.prop(self, "overwrite")

    def execute(self, context):
        name = self.module_name.strip()
        if not name:
            self.report({'ERROR'}, "Digite um nome para o módulo")
            return {'CANCELLED'}
        if library_io.exists(name, self.category) and not self.overwrite:
            self.report({'WARNING'}, f"O módulo '{name}' já existe; marque \"Substituir\" para gravar por cima")
            return {'CANCELLED'}
        root = adapters.module_root(context.active_object)
        paths, errors = library_io.save(context, root, name, self.category.strip(), self.thumbnail)
        if errors:
            self.report({'ERROR'}, " | ".join(errors))
            return {'CANCELLED'}
        self.report({'INFO'}, f"Módulo salvo: {paths['blend']}")
        _redraw(context)
        return {'FINISHED'}


class BTM_OT_ModuleInsert(bpy.types.Operator, hb_placement.PlacementMixin):
    """Insere um módulo da biblioteca do usuário. Clique para posicionar; R gira 90°; botão direito ou Esc cancela"""
    bl_idname = "caffmob.module_insert"
    bl_label = "Inserir módulo"
    bl_options = {'REGISTER', 'UNDO'}

    filepath: bpy.props.StringProperty(options={'HIDDEN'})  # type: ignore
    place: bpy.props.BoolProperty(default=True, options={'HIDDEN', 'SKIP_SAVE'})  # type: ignore

    def execute(self, context):
        entry = _entry(self.filepath)
        if entry is None or not os.path.exists(self.filepath):
            self.report({'ERROR'}, f"Módulo não encontrado: {self.filepath}")
            return {'CANCELLED'}
        self.init_placement(context)
        self.root, loaded, warnings = library_io.load(context, entry)
        for obj in loaded:
            if obj.parent is None:
                self.register_placement_object(obj)
        if self.root is None:
            for obj in list(loaded):
                if obj.name in bpy.data.objects:
                    bpy.data.objects.remove(obj, do_unlink=True)
            self.placement_objects = []
            self.report({'WARNING'}, " | ".join(warnings))
            return {'CANCELLED'}
        if warnings:
            self.report({'WARNING'}, " | ".join(warnings))
        self.others = {obj: obj.location - self.root.location for obj in loaded
                       if obj.parent is None and obj is not self.root and not obj.hide_viewport}
        for obj in context.selected_objects:
            obj.select_set(False)
        self.root.select_set(True)
        context.view_layer.objects.active = self.root
        if not self.place or context.area is None:
            self.placement_objects = []          # inserção direta (testes, scripts): fica onde foi salvo
            return {'FINISHED'}
        hb_placement.draw_header_text(context, "Clique para posicionar  |  R: girar 90°  |  Botão direito/Esc: cancelar")
        context.window.cursor_set('CROSSHAIR')
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def _hide(self, hide):
        for obj in [self.root] + list(self.root.children_recursive) + list(self.others):
            try:
                if not obj.hide_viewport:
                    obj.hide_set(hide)
            except ReferenceError:
                pass

    def modal(self, context, event):
        context.area.tag_redraw()
        if event.type == 'INBETWEEN_MOUSEMOVE':
            return {'RUNNING_MODAL'}
        self._hide(True)
        self.update_snap(context, event)
        self._hide(False)
        if self.hit_location:
            snapped = hb_snap.snap_vector_to_grid(Vector(self.hit_location))
            self.root.location = snapped
            for obj, offset in self.others.items():
                obj.location = snapped + offset
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            hb_placement.clear_header_text(context)
            context.window.cursor_set('DEFAULT')
            return {'FINISHED'}
        if event.type == 'R' and event.value == 'PRESS':
            self.root.rotation_euler.z += math.radians(90)
            return {'RUNNING_MODAL'}
        if event.type in {'RIGHTMOUSE', 'ESC'} and event.value == 'PRESS':
            self.cancel_placement(context)
            hb_placement.clear_header_text(context)
            context.window.cursor_set('DEFAULT')
            return {'CANCELLED'}
        if hb_snap.event_is_pass_through(event):
            return {'PASS_THROUGH'}
        return {'RUNNING_MODAL'}


class BTM_OT_ModuleDelete(bpy.types.Operator):
    """Apaga o módulo da biblioteca do usuário (arquivo, miniatura e manifesto)"""
    bl_idname = "caffmob.module_delete"
    bl_label = "Apagar módulo"

    filepath: bpy.props.StringProperty(options={'HIDDEN'})  # type: ignore

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event, title="Apagar módulo da biblioteca?",
                                                     confirm_text="Apagar", icon='WARNING')

    def execute(self, context):
        entry = _entry(self.filepath)
        if entry is None:
            self.report({'ERROR'}, "Módulo não encontrado")
            return {'CANCELLED'}
        library_io.delete(entry)
        self.report({'INFO'}, f"Módulo apagado: {entry['name']}")
        _redraw(context)
        return {'FINISHED'}


class BTM_OT_ModuleRename(bpy.types.Operator):
    """Renomeia o módulo da biblioteca do usuário"""
    bl_idname = "caffmob.module_rename"
    bl_label = "Renomear módulo"

    filepath: bpy.props.StringProperty(options={'HIDDEN'})  # type: ignore
    new_name: bpy.props.StringProperty(name="Novo nome")  # type: ignore

    def invoke(self, context, event):
        entry = _entry(self.filepath)
        self.new_name = entry["name"] if entry else ""
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        entry = _entry(self.filepath)
        if entry is None or not self.new_name.strip():
            self.report({'ERROR'}, "Módulo ou nome inválido")
            return {'CANCELLED'}
        errors = library_io.rename(entry, self.new_name.strip())
        if errors:
            self.report({'WARNING'}, " | ".join(errors))
            return {'CANCELLED'}
        _redraw(context)
        return {'FINISHED'}


class BTM_OT_ModuleOpenFolder(bpy.types.Operator):
    """Abre a pasta da biblioteca de módulos do usuário"""
    bl_idname = "caffmob.module_open_folder"
    bl_label = "Abrir pasta dos módulos"

    def execute(self, context):
        path = library_io.modules_root()
        if platform.system() == 'Windows':
            os.startfile(path)  # type: ignore[attr-defined]
        elif platform.system() == 'Darwin':
            subprocess.Popen(['open', path])
        else:
            subprocess.Popen(['xdg-open', path])
        return {'FINISHED'}


classes = (BTM_OT_ModuleSave, BTM_OT_ModuleInsert, BTM_OT_ModuleDelete, BTM_OT_ModuleRename, BTM_OT_ModuleOpenFolder)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)

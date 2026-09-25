"""Style template ops: save the project's styles as a named template,
load one into this project, and pick the template new projects start
from. The file handling lives in style_templates."""
import bpy
from bpy.types import Operator

from .. import style_templates
from ..props_hb_face_frame import get_style_props
from .ops_styles import _refresh_style_colors


def _default_items(self, context):
    items = [('NONE', "Built-in Defaults",
              "Start new projects from the built-in styles")]
    items += [(name, name, "") for name, _path in
              style_templates.list_templates()]
    _default_items.cache = items
    return items


class hb_face_frame_OT_save_style_template(Operator):
    """Save this project's cabinet, door and drawer front styles as a
    template to reuse in other projects"""
    bl_idname = "hb_face_frame.save_style_template"
    bl_label = "Save Styles as Template"
    bl_options = {'REGISTER'}

    name: bpy.props.StringProperty(name="Name")  # type: ignore
    make_default: bpy.props.BoolProperty(
        name="Use for New Projects",
        description="Start new projects from this template instead of "
                    "the built-in styles")  # type: ignore

    @classmethod
    def poll(cls, context):
        ff = get_style_props(context)
        return ff is not None and len(ff.cabinet_styles) > 0

    def invoke(self, context, event):
        if not self.name:
            self.name = style_templates.get_default_template() or "My Styles"
        return context.window_manager.invoke_props_dialog(self, width=320)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "name")
        layout.prop(self, "make_default")
        if self.name.strip() and style_templates.find_template(
                self.name.strip()):
            layout.label(text="Replaces the saved template of this name",
                         icon='INFO')

    def execute(self, context):
        name = self.name.strip()
        if not name:
            self.report({'WARNING'}, "Give the template a name")
            return {'CANCELLED'}
        ff = get_style_props(context)
        try:
            style_templates.save_template(ff, name)
            if self.make_default:
                style_templates.set_default_template(name)
        except Exception as ex:
            self.report({'ERROR'}, "Template not saved: %s" % ex)
            return {'CANCELLED'}
        self.report({'INFO'}, "Saved style template: %s" % name)
        return {'FINISHED'}


class hb_face_frame_OT_load_style_template(Operator):
    """Load a saved style template into this project. Styles with the
    same name are updated, the rest are added, none are removed"""
    bl_idname = "hb_face_frame.load_style_template"
    bl_label = "Load Style Template"
    bl_options = {'REGISTER', 'UNDO'}

    template: bpy.props.StringProperty(name="Template")  # type: ignore

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(
            self, event, title="Load %s" % self.template,
            message="Styles with the same name are updated, and every "
                    "cabinet using them changes to match.",
            confirm_text="Load")

    def execute(self, context):
        path = style_templates.find_template(self.template)
        if not path:
            self.report({'WARNING'}, "No template named %s" % self.template)
            return {'CANCELLED'}
        try:
            data = style_templates.read_template(path)
            n_cab, n_front, skipped = style_templates.apply_template(
                context, data)
        except Exception as ex:
            self.report({'ERROR'}, "Template not loaded: %s" % ex)
            return {'CANCELLED'}
        _refresh_style_colors(context)
        msg = "Loaded %s: %d cabinet style%s, %d door / drawer style%s" % (
            self.template, n_cab, "" if n_cab == 1 else "s",
            n_front, "" if n_front == 1 else "s")
        if skipped:
            msg += " (%d value%s skipped, see console)" % (
                len(skipped), "" if len(skipped) == 1 else "s")
            self.report({'WARNING'}, msg)
        else:
            self.report({'INFO'}, msg)
        return {'FINISHED'}


class hb_face_frame_OT_default_style_template(Operator):
    """Choose the style template new projects start from"""
    bl_idname = "hb_face_frame.default_style_template"
    bl_label = "Styles for New Projects"
    bl_options = {'REGISTER'}

    template: bpy.props.EnumProperty(
        name="Start From", items=_default_items)  # type: ignore

    def invoke(self, context, event):
        current = style_templates.get_default_template()
        try:
            self.template = current or 'NONE'
        except TypeError:
            pass
        return context.window_manager.invoke_props_dialog(self, width=320)

    def draw(self, context):
        self.layout.prop(self, "template")

    def execute(self, context):
        name = '' if self.template == 'NONE' else self.template
        try:
            style_templates.set_default_template(name)
        except Exception as ex:
            self.report({'ERROR'}, str(ex))
            return {'CANCELLED'}
        self.report({'INFO'}, "New projects start from %s"
                    % (name or "the built-in styles"))
        return {'FINISHED'}


class hb_face_frame_OT_open_style_template_folder(Operator):
    """Open the folder the style templates are saved in, to copy them to
    another computer"""
    bl_idname = "hb_face_frame.open_style_template_folder"
    bl_label = "Open Templates Folder"

    def execute(self, context):
        bpy.ops.wm.path_open(filepath=style_templates.template_folder())
        return {'FINISHED'}


def template_menu_entries(context):
    """The Templates... menu in the cabinet styles list."""
    default = style_templates.get_default_template()
    entries = [("Save Styles as Template...",
                'hb_face_frame.save_style_template', {'INVOKE': True})]
    for name, _path in style_templates.list_templates():
        label = "Load %s" % name
        if name == default:
            label += " (new projects)"
        entries.append((label, 'hb_face_frame.load_style_template',
                        {'template': name, 'INVOKE': True}))
    entries.append(("Styles for New Projects...",
                    'hb_face_frame.default_style_template', {'INVOKE': True}))
    entries.append(("Open Templates Folder",
                    'hb_face_frame.open_style_template_folder', {}))
    return entries


classes = (
    hb_face_frame_OT_save_style_template,
    hb_face_frame_OT_load_style_template,
    hb_face_frame_OT_default_style_template,
    hb_face_frame_OT_open_style_template_folder,
)


_register_classes, _unregister_classes = bpy.utils.register_classes_factory(classes)


def register():
    _register_classes()


def unregister():
    _unregister_classes()

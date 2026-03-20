import bpy

# Custom properties that mark objects we should DELETE during export prep
DELETE_FLAGS = {
    'IS_DIMENSION',
    'IS_DETAIL_LINE',
    'IS_DETAIL_POLYLINE',
    'IS_DETAIL_CIRCLE',
    'IS_DETAIL_TEXT',
    'IS_DETAIL_VIEW',
    'IS_DETAIL_COLLECTION',
    'IS_DETAIL_INSTANCE',
    'IS_ELEVATION_VIEW',
    'IS_PLAN_VIEW',
    'IS_LAYOUT_VIEW',
    'IS_MULTI_VIEW',
    'IS_CUTTING_OBJ',
    'IS_GEONODE_CAGE',
    'IS_CAGE_GROUP',
    'IS_FRAMELESS_BAY_CAGE',
    'IS_FRAMELESS_CABINET_CAGE',
    'IS_FRAMELESS_DOORS_CAGE',
    'IS_FRAMELESS_INTERIOR_CAGE',
    'IS_FRAMELESS_LADDER_CAGE',
    'IS_FRAMELESS_MISC_PART',
    'IS_FRAMELESS_OPENING_CAGE',
    'IS_FRAMELESS_PRODUCT_CAGE',
    'IS_FRAMELESS_SPLITTER_HORIZONTAL_CAGE',
    'IS_FRAMELESS_SPLITTER_VERTICAL_CAGE',
    'IS_SNAP_LINE',
    'IS_FREESTYLE_DASHED',
    'IS_FREESTYLE_SOLID',
    'IS_FREESTYLE_IGNORE',
    'IS_TITLE_BLOCK_BOARDER',
    'IS_TEMPLATE_PREVIEW',
    'IS_MOLDING_PROFILE',
    'IS_CROWN_PROFILE_COPY',
    'IS_TOE_KICK_PROFILE_COPY',
    'IS_UPPER_BOTTOM_PROFILE_COPY',
    'IS_ROOM_LIGHT',
    'IS_SNAP_LINE',
    'IS_LINKED_ROOM',
}


def should_delete_object(obj):
    """Check if an object should be deleted during export prep."""
    for flag in DELETE_FLAGS:
        if obj.get(flag):
            return True

    if obj.type == 'EMPTY':
        return True

    if obj.type == 'CAMERA':
        return True

    # Curve objects without geometry node modifiers are profile curves
    if obj.type == 'CURVE':
        has_geo_nodes = any(m.type == 'NODES' for m in obj.modifiers)
        if not has_geo_nodes:
            return True

    return False


class HOME_BUILDER_OT_prepare_for_export(bpy.types.Operator):
    bl_idname = "home_builder.prepare_for_export"
    bl_label = "Prepare for Export"
    bl_description = "Flatten the scene for export to Unreal, Unity, or other 3D platforms. This will modify the current file"

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event,
            message="This will permanently modify the current scene. Make sure you have saved a backup before continuing.",
            title="Prepare for Export",
            confirm_text="Prepare for Export",
            icon='WARNING',
        )

    def execute(self, context):
        deleted_count = 0
        converted_count = 0
        driver_count = 0

        scenes_to_process = []
        for scene in bpy.data.scenes:
            if scene.get('IS_ROOM_SCENE') or scene.get('IS_MAIN_SCENE'):
                scenes_to_process.append(scene)

        if not scenes_to_process:
            scenes_to_process.append(context.scene)

        original_scene = context.scene

        for scene in scenes_to_process:
            context.window.scene = scene

            # --- PASS 1: Delete helper objects that shouldnt be exported ---
            objects_to_delete = []
            for obj in scene.objects:
                if should_delete_object(obj):
                    objects_to_delete.append(obj)

            for obj in objects_to_delete:
                bpy.data.objects.remove(obj, do_unlink=True)
                deleted_count += 1

            # --- PASS 2: Remove all drivers from remaining objects ---
            for obj in scene.objects:
                if obj.animation_data:
                    drivers_to_remove = []
                    for d in obj.animation_data.drivers:
                        drivers_to_remove.append((d.data_path, d.array_index))
                    for data_path, index in drivers_to_remove:
                        try:
                            obj.driver_remove(data_path, index)
                            driver_count += 1
                        except TypeError:
                            try:
                                obj.driver_remove(data_path)
                                driver_count += 1
                            except TypeError:
                                pass

            # --- PASS 3: Remove all constraints ---
            for obj in scene.objects:
                for constraint in list(obj.constraints):
                    obj.constraints.remove(constraint)

            # --- PASS 4: Bake world transforms and clear parenting ---
            # Store world matrices first since clearing parents changes child transforms
            world_matrices = {}
            for obj in scene.objects:
                world_matrices[obj.name] = obj.matrix_world.copy()

            # Clear all parents while preserving world position
            for obj in scene.objects:
                if obj.parent:
                    obj.parent = None
                obj.matrix_world = world_matrices[obj.name]

            # --- PASS 5: Convert remaining objects to mesh ---
            for obj in list(scene.objects):
                if obj.type in {'MESH', 'CURVE', 'SURFACE', 'FONT'}:
                    bpy.ops.object.select_all(action='DESELECT')
                    obj.select_set(True)
                    context.view_layer.objects.active = obj

                    try:
                        bpy.ops.object.convert(target='MESH')
                        converted_count += 1
                    except RuntimeError:
                        pass

        context.window.scene = original_scene

        self.report({'INFO'},
            f"Export prep complete: {converted_count} objects converted, "
            f"{deleted_count} helper objects removed, {driver_count} drivers removed. "
            f"You can now export using File > Export > FBX or glTF.")

        return {'FINISHED'}


classes = (
    HOME_BUILDER_OT_prepare_for_export,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

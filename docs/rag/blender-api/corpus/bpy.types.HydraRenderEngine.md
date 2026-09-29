<!-- source: Blender Python API reference 5.2 / bpy.types.HydraRenderEngine.html -->

<a id="hydrarenderengine-renderengine"></a>

# HydraRenderEngine(RenderEngine)

Base class for integrating USD Hydra based renderers.

<a id="usd-hydra-based-renderer"></a>

## USD Hydra Based Renderer

```python
import bpy

class CustomHydraRenderEngine(bpy.types.HydraRenderEngine):
    # Identifier and name in the user interface.
    bl_idname = "CUSTOM_HYDRA_RENDERER"
    bl_label = "Custom Hydra Renderer"

    # Name of the render plugin.
    bl_delegate_id = "HdCustomRendererPlugin"

    # Use MaterialX instead of `UsdPreviewSurface` for materials.
    bl_use_materialx = True

    # Register path to plugin.
    @classmethod
    def register(cls):
        # Make `pxr` module available, for running as `bpy` PIP package.
        bpy.utils.expose_bundled_modules()

        import pxr.Plug
        pxr.Plug.Registry().RegisterPlugins(['/path/to/plugin'])

    # Render settings that will be passed to the delegate.
    def get_render_settings(self, engine_type):
        return {
            'myBoolean': True,
            'myValue': 8,
            'aovToken:Depth': "depth",
        }

    # RenderEngine methods for update, render and draw are implemented in
    # HydraRenderEngine. Optionally extra work can be done before or after
    # by implementing the methods like this.
    def update(self, data, depsgraph):
        super().update(data, depsgraph)
        # Do extra work here.

    def update_render_passes(self, scene, render_layer):
        if render_layer.use_pass_z:
            self.register_pass(scene, render_layer, 'Depth', 1, 'Z', 'VALUE')

# Registration.
def register():
    bpy.utils.register_class(CustomHydraRenderEngine)

def unregister():
    bpy.utils.unregister_class(CustomHydraRenderEngine)

if __name__ == "__main__":
    register()
```

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`RenderEngine`](bpy.types.RenderEngine.md#bpy.types.RenderEngine "bpy.types.RenderEngine")

<a id="bpy.types.HydraRenderEngine"></a>

### class bpy.types.HydraRenderEngine(RenderEngine)

Base class from USD Hydra based renderers

<a id="bpy.types.HydraRenderEngine.get_render_settings"></a>

#### bpy.types.HydraRenderEngine.get_render_settings(engine_type)

Provide render settings for `HdRenderDelegate`.

**Parameters:**

**engine_type** (Literal['PREVIEW', 'FINAL', 'VIEWPORT']) – Render mode.

**Returns:**

Mapping of render-delegate setting name to value.

**Return type:**

dict[str, Any]

<a id="bpy.types.HydraRenderEngine.bl_rna_get_subclass"></a>

#### classmethod bpy.types.HydraRenderEngine.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.HydraRenderEngine.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.HydraRenderEngine.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="inherited-properties"></a>

### Inherited Properties

bpy_struct.id_data, RenderEngine.is_animation, RenderEngine.is_preview, RenderEngine.camera_override, RenderEngine.layer_override, RenderEngine.resolution_x, RenderEngine.resolution_y, RenderEngine.temporary_directory, RenderEngine.render, RenderEngine.use_highlight_tiles, RenderEngine.bl_idname, RenderEngine.bl_label, RenderEngine.bl_use_preview, RenderEngine.bl_use_postprocess, RenderEngine.bl_use_eevee_viewport, RenderEngine.bl_use_custom_freestyle, RenderEngine.bl_use_image_save, RenderEngine.bl_use_gpu_context, RenderEngine.bl_use_shading_nodes_custom, RenderEngine.bl_use_spherical_stereo, RenderEngine.bl_use_stereo_viewport, RenderEngine.bl_use_materialx

<a id="inherited-functions"></a>

### Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values, RenderEngine.update, RenderEngine.render, RenderEngine.render_frame_finish, RenderEngine.draw, RenderEngine.bake, RenderEngine.view_update, RenderEngine.view_draw, RenderEngine.update_script_node, RenderEngine.update_render_passes, RenderEngine.update_custom_camera, RenderEngine.tag_redraw, RenderEngine.tag_update, RenderEngine.begin_result, RenderEngine.update_result, RenderEngine.end_result, RenderEngine.add_pass, RenderEngine.get_result, RenderEngine.test_break, RenderEngine.pass_by_index_get, RenderEngine.active_view_get, RenderEngine.active_view_set, RenderEngine.camera_shift_x, RenderEngine.camera_model_matrix, RenderEngine.use_spherical_stereo, RenderEngine.update_stats, RenderEngine.frame_set, RenderEngine.update_progress, RenderEngine.update_memory_stats, RenderEngine.report, RenderEngine.error_set, RenderEngine.bind_display_space_shader, RenderEngine.unbind_display_space_shader, RenderEngine.support_display_space_shader, RenderEngine.get_preview_pixel_size, RenderEngine.free_blender_memory, RenderEngine.tile_highlight_set, RenderEngine.tile_highlight_clear_all, RenderEngine.register_pass, RenderEngine.bl_rna_get_subclass, RenderEngine.bl_rna_get_subclass_py

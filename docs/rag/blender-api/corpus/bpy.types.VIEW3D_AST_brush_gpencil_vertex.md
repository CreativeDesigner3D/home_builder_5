<!-- source: Blender Python API reference 5.2 / bpy.types.VIEW3D_AST_brush_gpencil_vertex.html -->

<a id="view3d-ast-brush-gpencil-vertex-assetshelf"></a>

# VIEW3D_AST_brush_gpencil_vertex(AssetShelf)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`AssetShelf`](bpy.types.AssetShelf.md#bpy.types.AssetShelf "bpy.types.AssetShelf")

<a id="bpy.types.VIEW3D_AST_brush_gpencil_vertex"></a>

### class bpy.types.VIEW3D_AST_brush_gpencil_vertex(AssetShelf)

<a id="bpy.types.VIEW3D_AST_brush_gpencil_vertex.brush_type_poll"></a>

#### classmethod bpy.types.VIEW3D_AST_brush_gpencil_vertex.brush_type_poll(context, asset)

Test if *asset* is compatible with the active tool’s brush type.

**Parameters:**

- **context** ([`bpy.types.Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context")) – The context.
- **asset** ([`bpy.types.AssetRepresentation`](bpy.types.AssetRepresentation.md#bpy.types.AssetRepresentation "bpy.types.AssetRepresentation")) – Brush asset to test.

**Returns:**

True when the asset’s brush type matches the active tool.

**Return type:**

bool

<a id="bpy.types.VIEW3D_AST_brush_gpencil_vertex.draw_popup_selector"></a>

#### static bpy.types.VIEW3D_AST_brush_gpencil_vertex.draw_popup_selector(layout, context, brush, show_name=True)

Draw a brush asset-shelf popover into *layout* for the active paint mode.

**Parameters:**

- **layout** ([`bpy.types.UILayout`](bpy.types.UILayout.md#bpy.types.UILayout "bpy.types.UILayout")) – Layout to draw into.
- **context** ([`bpy.types.Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context")) – The context.
- **brush** ([`bpy.types.Brush`](bpy.types.Brush.md#bpy.types.Brush "bpy.types.Brush") | None) – Brush whose preview/name is shown on the button.
- **show_name** (bool) – Display the brush name next to the preview.

<a id="bpy.types.VIEW3D_AST_brush_gpencil_vertex.get_shelf_name_from_context"></a>

#### static bpy.types.VIEW3D_AST_brush_gpencil_vertex.get_shelf_name_from_context(context)

Look up the brush asset-shelf identifier for the current paint mode.

**Parameters:**

**context** ([`bpy.types.Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context")) – The context.

**Returns:**

The asset-shelf `bl_idname`, or `None` when no paint mode is active.

**Return type:**

str | None

<a id="bpy.types.VIEW3D_AST_brush_gpencil_vertex.has_tool_with_brush_type"></a>

#### classmethod bpy.types.VIEW3D_AST_brush_gpencil_vertex.has_tool_with_brush_type(context, brush_type)

Test if any tool active in the current space matches *brush_type*.

**Parameters:**

- **context** ([`bpy.types.Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context")) – The context.
- **brush_type** (int) – Brush type identifier to match against tool brush types.

**Returns:**

True when a registered tool uses this brush type.

**Return type:**

bool

<a id="bpy.types.VIEW3D_AST_brush_gpencil_vertex.bl_rna_get_subclass"></a>

#### classmethod bpy.types.VIEW3D_AST_brush_gpencil_vertex.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.VIEW3D_AST_brush_gpencil_vertex.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.VIEW3D_AST_brush_gpencil_vertex.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="inherited-properties"></a>

## Inherited Properties

bpy_struct.id_data, AssetShelf.bl_idname, AssetShelf.bl_space_type, AssetShelf.bl_options, AssetShelf.bl_activate_operator, AssetShelf.bl_drag_operator, AssetShelf.bl_default_preview_size, AssetShelf.filter_action, AssetShelf.filter_armature, AssetShelf.filter_brush, AssetShelf.filter_camera, AssetShelf.filter_cachefile, AssetShelf.filter_curve, AssetShelf.filter_annotations, AssetShelf.filter_grease_pencil, AssetShelf.filter_group, AssetShelf.filter_curves, AssetShelf.filter_image, AssetShelf.filter_light, AssetShelf.filter_light_probe, AssetShelf.filter_linestyle, AssetShelf.filter_lattice, AssetShelf.filter_material, AssetShelf.filter_metaball, AssetShelf.filter_movie_clip, AssetShelf.filter_mesh, AssetShelf.filter_mask, AssetShelf.filter_node_tree, AssetShelf.filter_object, AssetShelf.filter_particle_settings, AssetShelf.filter_palette, AssetShelf.filter_paint_curve, AssetShelf.filter_pointcloud, AssetShelf.filter_scene, AssetShelf.filter_speaker, AssetShelf.filter_sound, AssetShelf.filter_texture, AssetShelf.filter_text, AssetShelf.filter_font, AssetShelf.filter_volume, AssetShelf.filter_world, AssetShelf.filter_work_space, AssetShelf.asset_library_reference, AssetShelf.show_names, AssetShelf.preview_size, AssetShelf.search_filter

<a id="inherited-functions"></a>

## Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values, AssetShelf.poll, AssetShelf.asset_poll, AssetShelf.get_active_asset, AssetShelf.draw_context_menu, AssetShelf.bl_rna_get_subclass, AssetShelf.bl_rna_get_subclass_py

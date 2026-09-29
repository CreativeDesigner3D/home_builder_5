<!-- source: Blender Python API reference 5.2 / bpy.types.AssetShelf.html -->

<a id="assetshelf-bpy-struct"></a>

# AssetShelf(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

Subclasses

- [IMAGE_AST_brush_paint(AssetShelf)](bpy.types.IMAGE_AST_brush_paint.md)
- [NODE_AST_compositor(AssetShelf)](bpy.types.NODE_AST_compositor.md)
- [VIEW3D_AST_brush_gpencil_paint(AssetShelf)](bpy.types.VIEW3D_AST_brush_gpencil_paint.md)
- [VIEW3D_AST_brush_gpencil_sculpt(AssetShelf)](bpy.types.VIEW3D_AST_brush_gpencil_sculpt.md)
- [VIEW3D_AST_brush_gpencil_vertex(AssetShelf)](bpy.types.VIEW3D_AST_brush_gpencil_vertex.md)
- [VIEW3D_AST_brush_gpencil_weight(AssetShelf)](bpy.types.VIEW3D_AST_brush_gpencil_weight.md)
- [VIEW3D_AST_brush_sculpt(AssetShelf)](bpy.types.VIEW3D_AST_brush_sculpt.md)
- [VIEW3D_AST_brush_sculpt_curves(AssetShelf)](bpy.types.VIEW3D_AST_brush_sculpt_curves.md)
- [VIEW3D_AST_brush_texture_paint(AssetShelf)](bpy.types.VIEW3D_AST_brush_texture_paint.md)
- [VIEW3D_AST_brush_vertex_paint(AssetShelf)](bpy.types.VIEW3D_AST_brush_vertex_paint.md)
- [VIEW3D_AST_brush_weight_paint(AssetShelf)](bpy.types.VIEW3D_AST_brush_weight_paint.md)
- [VIEW3D_AST_pose_library(AssetShelf)](bpy.types.VIEW3D_AST_pose_library.md)

<a id="bpy.types.AssetShelf"></a>

### class bpy.types.AssetShelf(bpy_struct)

Regions for quick access to assets

<a id="bpy.types.AssetShelf.asset_library_reference"></a>

#### bpy.types.AssetShelf.asset_library_reference

Choose the asset library to display assets from (default `'ALL'`)

- `ALL`
  All Libraries – Show assets from all of the listed asset libraries.
- `LOCAL`
  Current File – Show the assets currently available in this Blender session.
- `ESSENTIALS`
  Essentials – Show basic building blocks and utilities coming with Blender.
- `ONLINE_ESSENTIALS`
  Online Essentials – Show additional building blocks and utilities available online.
- `CUSTOM`
  Custom – Show assets from the asset libraries configured in the Preferences.

**Type:**

Literal[‘ALL’, ‘LOCAL’, ‘ESSENTIALS’, ‘ONLINE_ESSENTIALS’, ‘CUSTOM’]

<a id="bpy.types.AssetShelf.bl_activate_operator"></a>

#### bpy.types.AssetShelf.bl_activate_operator

Operator to call when activating an item with asset reference properties (default “”, never None)

**Type:**

str

<a id="bpy.types.AssetShelf.bl_default_preview_size"></a>

#### bpy.types.AssetShelf.bl_default_preview_size

Default size of the asset preview thumbnails in pixels (in [32, 256], default 0)

**Type:**

int

<a id="bpy.types.AssetShelf.bl_drag_operator"></a>

#### bpy.types.AssetShelf.bl_drag_operator

Operator to call when dragging an item with asset reference properties (default “”, never None)

**Type:**

str

<a id="bpy.types.AssetShelf.bl_idname"></a>

#### bpy.types.AssetShelf.bl_idname

If this is set, the asset gets a custom ID, otherwise it takes the name of the class used to define the asset (for example, if the class name is “OBJECT_AST_hello”, and bl_idname is not set by the script, then bl_idname = “OBJECT_AST_hello”) (default “”, never None)

**Type:**

str

<a id="bpy.types.AssetShelf.bl_options"></a>

#### bpy.types.AssetShelf.bl_options

Options for this asset shelf type (default set())

- `NO_ASSET_DRAG`
  No Asset Dragging – Disable the default asset dragging on drag events. Useful for implementing custom dragging via custom key-map items..
- `DEFAULT_VISIBLE`
  Visible by Default – Unhide the asset shelf when it’s available for the first time, otherwise it will be hidden.
- `STORE_ENABLED_CATALOGS_IN_PREFERENCES`
  Store Enabled Catalogs in Preferences – Store the shelf’s enabled catalogs in the preferences rather than the local asset shelf settings.
- `ACTIVATE_FOR_CONTEXT_MENU`
  When spawning a context menu for an asset, activate the asset and call `bl_activate_operator` if present, rather than just highlighting the asset.

**Type:**

set[Literal[‘NO_ASSET_DRAG’, ‘DEFAULT_VISIBLE’, ‘STORE_ENABLED_CATALOGS_IN_PREFERENCES’, ‘ACTIVATE_FOR_CONTEXT_MENU’]]

<a id="bpy.types.AssetShelf.bl_space_type"></a>

#### bpy.types.AssetShelf.bl_space_type

The space where the asset shelf will show up in. Ignored for popup asset shelves which can be displayed in any space. (default `'EMPTY'`)

**Type:**

Literal[[Space Type Items](bpy_types_enum_items/space_type_items.md#rna-enum-space-type-items)]

<a id="bpy.types.AssetShelf.filter_action"></a>

#### bpy.types.AssetShelf.filter_action

Show Action data-blocks (default False)

**Type:**

bool

<a id="bpy.types.AssetShelf.filter_annotations"></a>

#### bpy.types.AssetShelf.filter_annotations

Show Annotation data-blocks (default False)

**Type:**

bool

<a id="bpy.types.AssetShelf.filter_armature"></a>

#### bpy.types.AssetShelf.filter_armature

Show Armature data-blocks (default False)

**Type:**

bool

<a id="bpy.types.AssetShelf.filter_brush"></a>

#### bpy.types.AssetShelf.filter_brush

Show Brushes data-blocks (default False)

**Type:**

bool

<a id="bpy.types.AssetShelf.filter_cachefile"></a>

#### bpy.types.AssetShelf.filter_cachefile

Show Cache File data-blocks (default False)

**Type:**

bool

<a id="bpy.types.AssetShelf.filter_camera"></a>

#### bpy.types.AssetShelf.filter_camera

Show Camera data-blocks (default False)

**Type:**

bool

<a id="bpy.types.AssetShelf.filter_curve"></a>

#### bpy.types.AssetShelf.filter_curve

Show Curve data-blocks (default False)

**Type:**

bool

<a id="bpy.types.AssetShelf.filter_curves"></a>

#### bpy.types.AssetShelf.filter_curves

Show/hide Curves data-blocks (default False)

**Type:**

bool

<a id="bpy.types.AssetShelf.filter_font"></a>

#### bpy.types.AssetShelf.filter_font

Show Font data-blocks (default False)

**Type:**

bool

<a id="bpy.types.AssetShelf.filter_grease_pencil"></a>

#### bpy.types.AssetShelf.filter_grease_pencil

Show Grease Pencil data-blocks (default False)

**Type:**

bool

<a id="bpy.types.AssetShelf.filter_group"></a>

#### bpy.types.AssetShelf.filter_group

Show Collection data-blocks (default False)

**Type:**

bool

<a id="bpy.types.AssetShelf.filter_image"></a>

#### bpy.types.AssetShelf.filter_image

Show Image data-blocks (default False)

**Type:**

bool

<a id="bpy.types.AssetShelf.filter_lattice"></a>

#### bpy.types.AssetShelf.filter_lattice

Show Lattice data-blocks (default False)

**Type:**

bool

<a id="bpy.types.AssetShelf.filter_light"></a>

#### bpy.types.AssetShelf.filter_light

Show Light data-blocks (default False)

**Type:**

bool

<a id="bpy.types.AssetShelf.filter_light_probe"></a>

#### bpy.types.AssetShelf.filter_light_probe

Show Light Probe data-blocks (default False)

**Type:**

bool

<a id="bpy.types.AssetShelf.filter_linestyle"></a>

#### bpy.types.AssetShelf.filter_linestyle

Show Freestyle’s Line Style data-blocks (default False)

**Type:**

bool

<a id="bpy.types.AssetShelf.filter_mask"></a>

#### bpy.types.AssetShelf.filter_mask

Show Mask data-blocks (default False)

**Type:**

bool

<a id="bpy.types.AssetShelf.filter_material"></a>

#### bpy.types.AssetShelf.filter_material

Show Material data-blocks (default False)

**Type:**

bool

<a id="bpy.types.AssetShelf.filter_mesh"></a>

#### bpy.types.AssetShelf.filter_mesh

Show Mesh data-blocks (default False)

**Type:**

bool

<a id="bpy.types.AssetShelf.filter_metaball"></a>

#### bpy.types.AssetShelf.filter_metaball

Show Metaball data-blocks (default False)

**Type:**

bool

<a id="bpy.types.AssetShelf.filter_movie_clip"></a>

#### bpy.types.AssetShelf.filter_movie_clip

Show Movie Clip data-blocks (default False)

**Type:**

bool

<a id="bpy.types.AssetShelf.filter_node_tree"></a>

#### bpy.types.AssetShelf.filter_node_tree

Show Node Tree data-blocks (default False)

**Type:**

bool

<a id="bpy.types.AssetShelf.filter_object"></a>

#### bpy.types.AssetShelf.filter_object

Show Object data-blocks (default False)

**Type:**

bool

<a id="bpy.types.AssetShelf.filter_paint_curve"></a>

#### bpy.types.AssetShelf.filter_paint_curve

Show Paint Curve data-blocks (default False)

**Type:**

bool

<a id="bpy.types.AssetShelf.filter_palette"></a>

#### bpy.types.AssetShelf.filter_palette

Show Palette data-blocks (default False)

**Type:**

bool

<a id="bpy.types.AssetShelf.filter_particle_settings"></a>

#### bpy.types.AssetShelf.filter_particle_settings

Show Particle Settings data-blocks (default False)

**Type:**

bool

<a id="bpy.types.AssetShelf.filter_pointcloud"></a>

#### bpy.types.AssetShelf.filter_pointcloud

Show/hide Point Cloud data-blocks (default False)

**Type:**

bool

<a id="bpy.types.AssetShelf.filter_scene"></a>

#### bpy.types.AssetShelf.filter_scene

Show Scene data-blocks (default False)

**Type:**

bool

<a id="bpy.types.AssetShelf.filter_sound"></a>

#### bpy.types.AssetShelf.filter_sound

Show Sound data-blocks (default False)

**Type:**

bool

<a id="bpy.types.AssetShelf.filter_speaker"></a>

#### bpy.types.AssetShelf.filter_speaker

Show Speaker data-blocks (default False)

**Type:**

bool

<a id="bpy.types.AssetShelf.filter_text"></a>

#### bpy.types.AssetShelf.filter_text

Show Text data-blocks (default False)

**Type:**

bool

<a id="bpy.types.AssetShelf.filter_texture"></a>

#### bpy.types.AssetShelf.filter_texture

Show Texture data-blocks (default False)

**Type:**

bool

<a id="bpy.types.AssetShelf.filter_volume"></a>

#### bpy.types.AssetShelf.filter_volume

Show/hide Volume data-blocks (default False)

**Type:**

bool

<a id="bpy.types.AssetShelf.filter_work_space"></a>

#### bpy.types.AssetShelf.filter_work_space

Show workspace data-blocks (default False)

**Type:**

bool

<a id="bpy.types.AssetShelf.filter_world"></a>

#### bpy.types.AssetShelf.filter_world

Show World data-blocks (default False)

**Type:**

bool

<a id="bpy.types.AssetShelf.preview_size"></a>

#### bpy.types.AssetShelf.preview_size

Size of the asset preview thumbnails in pixels (in [24, 256], default 0)

**Type:**

int

<a id="bpy.types.AssetShelf.search_filter"></a>

#### bpy.types.AssetShelf.search_filter

Filter assets by name (default “”, never None)

**Type:**

str

<a id="bpy.types.AssetShelf.show_names"></a>

#### bpy.types.AssetShelf.show_names

Show the asset name together with the preview. Otherwise only the preview will be visible. (default False)

**Type:**

bool

<a id="bpy.types.AssetShelf.poll"></a>

#### classmethod bpy.types.AssetShelf.poll(context)

If this method returns a non-null output, the asset shelf will be visible

**Parameters:**

**context** ([`Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context") | None) – The context

**Return type:**

bool

<a id="bpy.types.AssetShelf.asset_poll"></a>

#### classmethod bpy.types.AssetShelf.asset_poll(asset)

Determine if an asset should be visible in the asset shelf. If this method returns a non-null output, the asset will be visible.

**Parameters:**

**asset** ([`AssetRepresentation`](bpy.types.AssetRepresentation.md#bpy.types.AssetRepresentation "bpy.types.AssetRepresentation") | None) – The asset to test for visibility

**Return type:**

bool

<a id="bpy.types.AssetShelf.get_active_asset"></a>

#### classmethod bpy.types.AssetShelf.get_active_asset()

Return a reference to the asset that should be highlighted as active in the asset shelf

**Returns:**

The weak reference to the asset to be highlighted as active, or None

**Return type:**

[`AssetWeakReference`](bpy.types.AssetWeakReference.md#bpy.types.AssetWeakReference "bpy.types.AssetWeakReference")

<a id="bpy.types.AssetShelf.draw_context_menu"></a>

#### classmethod bpy.types.AssetShelf.draw_context_menu(context, asset, layout)

Draw UI elements into the context menu UI layout displayed on right click

**Parameters:**

- **context** ([`Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context") | None) – The context
- **asset** ([`AssetRepresentation`](bpy.types.AssetRepresentation.md#bpy.types.AssetRepresentation "bpy.types.AssetRepresentation") | None) – The active asset
- **layout** ([`UILayout`](bpy.types.UILayout.md#bpy.types.UILayout "bpy.types.UILayout") | None) – The layout to draw into

<a id="bpy.types.AssetShelf.bl_rna_get_subclass"></a>

#### classmethod bpy.types.AssetShelf.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.AssetShelf.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.AssetShelf.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="inherited-properties"></a>

## Inherited Properties

bpy_struct.id_data

<a id="inherited-functions"></a>

## Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values

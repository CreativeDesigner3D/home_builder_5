<!-- source: Blender Python API reference 5.2 / change_log.html -->

<a id="change-log"></a>

# Change Log

Changes in Blender’s Python API between releases.

<a id="to-5-2"></a>

## 5.1 to 5.2

<a id="bpy-types-annotationstroke"></a>

### bpy.types.AnnotationStroke

<a id="added"></a>

#### Added

- [`bpy.types.AnnotationStroke.display_mode`](bpy.types.AnnotationStroke.md#bpy.types.AnnotationStroke.display_mode "bpy.types.AnnotationStroke.display_mode")

<a id="bpy-types-assetmetadata"></a>

### bpy.types.AssetMetaData

<a id="id1"></a>

#### Added

- [`bpy.types.AssetMetaData.preferred_import_method`](bpy.types.AssetMetaData.md#bpy.types.AssetMetaData.preferred_import_method "bpy.types.AssetMetaData.preferred_import_method")
- [`bpy.types.AssetMetaData.use_preferred_import_method`](bpy.types.AssetMetaData.md#bpy.types.AssetMetaData.use_preferred_import_method "bpy.types.AssetMetaData.use_preferred_import_method")

<a id="bpy-types-assetrepresentation"></a>

### bpy.types.AssetRepresentation

<a id="id2"></a>

#### Added

- [`bpy.types.AssetRepresentation.is_online`](bpy.types.AssetRepresentation.md#bpy.types.AssetRepresentation.is_online "bpy.types.AssetRepresentation.is_online")
- [`bpy.types.AssetRepresentation.owner_asset_library`](bpy.types.AssetRepresentation.md#bpy.types.AssetRepresentation.owner_asset_library "bpy.types.AssetRepresentation.owner_asset_library")

<a id="bpy-types-blenddata"></a>

### bpy.types.BlendData

<a id="id3"></a>

#### Added

- [`bpy.types.BlendData.all_ids`](bpy.types.BlendData.md#bpy.types.BlendData.all_ids "bpy.types.BlendData.all_ids")

<a id="bpy-types-brush"></a>

### bpy.types.Brush

<a id="id4"></a>

#### Added

- [`bpy.types.Brush.minimum_distance`](bpy.types.Brush.md#bpy.types.Brush.minimum_distance "bpy.types.Brush.minimum_distance")
- [`bpy.types.Brush.project_ray_direction_type`](bpy.types.Brush.md#bpy.types.Brush.project_ray_direction_type "bpy.types.Brush.project_ray_direction_type")

<a id="removed"></a>

#### Removed

- **automasking_boundary_edges_propagation_steps**
- **automasking_cavity_blur_steps**
- **automasking_cavity_factor**
- **automasking_start_normal_falloff**
- **automasking_start_normal_limit**
- **automasking_view_normal_falloff**
- **automasking_view_normal_limit**
- **use_automasking_boundary_edges**
- **use_automasking_boundary_face_sets**
- **use_automasking_cavity_inverted**
- **use_automasking_custom_cavity_curve**
- **use_automasking_face_sets**
- **use_automasking_start_normal**
- **use_automasking_topology**
- **use_automasking_view_normal**
- **use_automasking_view_occlusion**

<a id="renamed"></a>

#### Renamed

- **automasking_cavity_curve** -> [`bpy.types.Brush.mesh_automasking_settings`](bpy.types.Brush.md#bpy.types.Brush.mesh_automasking_settings "bpy.types.Brush.mesh_automasking_settings")
- **use_automasking_cavity** -> [`bpy.types.Brush.use_bidirectional`](bpy.types.Brush.md#bpy.types.Brush.use_bidirectional "bpy.types.Brush.use_bidirectional")

<a id="bpy-types-brushgpencilsettings"></a>

### bpy.types.BrushGpencilSettings

<a id="id5"></a>

#### Added

- [`bpy.types.BrushGpencilSettings.conversion_threshold`](bpy.types.BrushGpencilSettings.md#bpy.types.BrushGpencilSettings.conversion_threshold "bpy.types.BrushGpencilSettings.conversion_threshold")
- [`bpy.types.BrushGpencilSettings.curve_type`](bpy.types.BrushGpencilSettings.md#bpy.types.BrushGpencilSettings.curve_type "bpy.types.BrushGpencilSettings.curve_type")
- [`bpy.types.BrushGpencilSettings.fill_gap_factor`](bpy.types.BrushGpencilSettings.md#bpy.types.BrushGpencilSettings.fill_gap_factor "bpy.types.BrushGpencilSettings.fill_gap_factor")
- [`bpy.types.BrushGpencilSettings.fill_internal_gaps`](bpy.types.BrushGpencilSettings.md#bpy.types.BrushGpencilSettings.fill_internal_gaps "bpy.types.BrushGpencilSettings.fill_internal_gaps")
- [`bpy.types.BrushGpencilSettings.fill_solver`](bpy.types.BrushGpencilSettings.md#bpy.types.BrushGpencilSettings.fill_solver "bpy.types.BrushGpencilSettings.fill_solver")

<a id="bpy-types-colorstrip"></a>

### bpy.types.ColorStrip

<a id="id6"></a>

#### Added

- [`bpy.types.ColorStrip.height`](bpy.types.ColorStrip.md#bpy.types.ColorStrip.height "bpy.types.ColorStrip.height")
- [`bpy.types.ColorStrip.width`](bpy.types.ColorStrip.md#bpy.types.ColorStrip.width "bpy.types.ColorStrip.width")

<a id="bpy-types-compositornodeoutputfile"></a>

### bpy.types.CompositorNodeOutputFile

<a id="id7"></a>

#### Added

- [`bpy.types.CompositorNodeOutputFile.use_file_extension`](bpy.types.CompositorNodeOutputFile.md#bpy.types.CompositorNodeOutputFile.use_file_extension "bpy.types.CompositorNodeOutputFile.use_file_extension")

<a id="bpy-types-compositornodetree"></a>

### bpy.types.CompositorNodeTree

<a id="id8"></a>

#### Added

- [`bpy.types.CompositorNodeTree.is_strip_modifier`](bpy.types.CompositorNodeTree.md#bpy.types.CompositorNodeTree.is_strip_modifier "bpy.types.CompositorNodeTree.is_strip_modifier")

<a id="bpy-types-cyclesrenderlayersettings"></a>

### bpy.types.CyclesRenderLayerSettings

<a id="id9"></a>

#### Added

- `bpy.types.CyclesRenderLayerSettings.denoising_pass_follow_reflections`
- `bpy.types.CyclesRenderLayerSettings.denoising_pass_use_albedo_roughness_weighting`

<a id="bpy-types-cyclesrendersettings"></a>

### bpy.types.CyclesRenderSettings

<a id="id10"></a>

#### Added

- `bpy.types.CyclesRenderSettings.debug_texture_cache_preserve_unused`
- `bpy.types.CyclesRenderSettings.debug_use_texture_cache_eviction`
- `bpy.types.CyclesRenderSettings.texture_resolution`
- `bpy.types.CyclesRenderSettings.texture_resolution_render`
- `bpy.types.CyclesRenderSettings.use_pixel_jitter`

<a id="bpy-types-cyclesworldsettings"></a>

### bpy.types.CyclesWorldSettings

<a id="id11"></a>

#### Added

- `bpy.types.CyclesWorldSettings.use_shadows`

<a id="bpy-types-fileassetselectparams"></a>

### bpy.types.FileAssetSelectParams

<a id="id12"></a>

#### Added

- [`bpy.types.FileAssetSelectParams.asset_access`](bpy.types.FileAssetSelectParams.md#bpy.types.FileAssetSelectParams.asset_access "bpy.types.FileAssetSelectParams.asset_access")
- [`bpy.types.FileAssetSelectParams.asset_catalog_visibility`](bpy.types.FileAssetSelectParams.md#bpy.types.FileAssetSelectParams.asset_catalog_visibility "bpy.types.FileAssetSelectParams.asset_catalog_visibility")

<a id="bpy-types-functionnodeinputstring"></a>

### bpy.types.FunctionNodeInputString

<a id="id13"></a>

#### Added

- [`bpy.types.FunctionNodeInputString.textbox_state`](bpy.types.FunctionNodeInputString.md#bpy.types.FunctionNodeInputString.textbox_state "bpy.types.FunctionNodeInputString.textbox_state")

<a id="bpy-types-functionnodeinputvector"></a>

### bpy.types.FunctionNodeInputVector

<a id="id14"></a>

#### Added

- [`bpy.types.FunctionNodeInputVector.vector_dimensions`](bpy.types.FunctionNodeInputVector.md#bpy.types.FunctionNodeInputVector.vector_dimensions "bpy.types.FunctionNodeInputVector.vector_dimensions")

<a id="bpy-types-greasepencil"></a>

### bpy.types.GreasePencil

<a id="id15"></a>

#### Added

- [`bpy.types.GreasePencil.unit_test_compare`](bpy.types.GreasePencil.md#bpy.types.GreasePencil.unit_test_compare "bpy.types.GreasePencil.unit_test_compare")

<a id="bpy-types-greasepencillayermasks"></a>

### bpy.types.GreasePencilLayerMasks

<a id="id16"></a>

#### Added

- [`bpy.types.GreasePencilLayerMasks.add`](bpy.types.GreasePencilLayerMasks.md#bpy.types.GreasePencilLayerMasks.add "bpy.types.GreasePencilLayerMasks.add")
- [`bpy.types.GreasePencilLayerMasks.remove`](bpy.types.GreasePencilLayerMasks.md#bpy.types.GreasePencilLayerMasks.remove "bpy.types.GreasePencilLayerMasks.remove")

<a id="bpy-types-greasepencillineartmodifier"></a>

### bpy.types.GreasePencilLineartModifier

<a id="id17"></a>

#### Added

- [`bpy.types.GreasePencilLineartModifier.fill_strokes`](bpy.types.GreasePencilLineartModifier.md#bpy.types.GreasePencilLineartModifier.fill_strokes "bpy.types.GreasePencilLineartModifier.fill_strokes")

<a id="bpy-types-idoverridelibrarypropertyoperation"></a>

### bpy.types.IDOverrideLibraryPropertyOperation

<a id="id18"></a>

#### Added

- [`bpy.types.IDOverrideLibraryPropertyOperation.label`](bpy.types.IDOverrideLibraryPropertyOperation.md#bpy.types.IDOverrideLibraryPropertyOperation.label "bpy.types.IDOverrideLibraryPropertyOperation.label")
- [`bpy.types.IDOverrideLibraryPropertyOperation.tooltip`](bpy.types.IDOverrideLibraryPropertyOperation.md#bpy.types.IDOverrideLibraryPropertyOperation.tooltip "bpy.types.IDOverrideLibraryPropertyOperation.tooltip")

<a id="bpy-types-lightprobeplane"></a>

### bpy.types.LightProbePlane

<a id="id19"></a>

#### Added

- [`bpy.types.LightProbePlane.parallax_distance`](bpy.types.LightProbePlane.md#bpy.types.LightProbePlane.parallax_distance "bpy.types.LightProbePlane.parallax_distance")

<a id="bpy-types-masklayer"></a>

### bpy.types.MaskLayer

<a id="id20"></a>

#### Added

- [`bpy.types.MaskLayer.fill_solver`](bpy.types.MaskLayer.md#bpy.types.MaskLayer.fill_solver "bpy.types.MaskLayer.fill_solver")

<a id="bpy-types-materialgpencilstyle"></a>

### bpy.types.MaterialGPencilStyle

<a id="id21"></a>

#### Added

- [`bpy.types.MaterialGPencilStyle.placement_count`](bpy.types.MaterialGPencilStyle.md#bpy.types.MaterialGPencilStyle.placement_count "bpy.types.MaterialGPencilStyle.placement_count")
- [`bpy.types.MaterialGPencilStyle.placement_density`](bpy.types.MaterialGPencilStyle.md#bpy.types.MaterialGPencilStyle.placement_density "bpy.types.MaterialGPencilStyle.placement_density")
- [`bpy.types.MaterialGPencilStyle.placement_mode`](bpy.types.MaterialGPencilStyle.md#bpy.types.MaterialGPencilStyle.placement_mode "bpy.types.MaterialGPencilStyle.placement_mode")
- [`bpy.types.MaterialGPencilStyle.placement_radius_spacing`](bpy.types.MaterialGPencilStyle.md#bpy.types.MaterialGPencilStyle.placement_radius_spacing "bpy.types.MaterialGPencilStyle.placement_radius_spacing")
- [`bpy.types.MaterialGPencilStyle.random_hue_factor`](bpy.types.MaterialGPencilStyle.md#bpy.types.MaterialGPencilStyle.random_hue_factor "bpy.types.MaterialGPencilStyle.random_hue_factor")
- [`bpy.types.MaterialGPencilStyle.random_noise_scale`](bpy.types.MaterialGPencilStyle.md#bpy.types.MaterialGPencilStyle.random_noise_scale "bpy.types.MaterialGPencilStyle.random_noise_scale")
- [`bpy.types.MaterialGPencilStyle.random_rotation_factor`](bpy.types.MaterialGPencilStyle.md#bpy.types.MaterialGPencilStyle.random_rotation_factor "bpy.types.MaterialGPencilStyle.random_rotation_factor")
- [`bpy.types.MaterialGPencilStyle.random_saturation_factor`](bpy.types.MaterialGPencilStyle.md#bpy.types.MaterialGPencilStyle.random_saturation_factor "bpy.types.MaterialGPencilStyle.random_saturation_factor")
- [`bpy.types.MaterialGPencilStyle.random_size_factor`](bpy.types.MaterialGPencilStyle.md#bpy.types.MaterialGPencilStyle.random_size_factor "bpy.types.MaterialGPencilStyle.random_size_factor")
- [`bpy.types.MaterialGPencilStyle.random_strength_factor`](bpy.types.MaterialGPencilStyle.md#bpy.types.MaterialGPencilStyle.random_strength_factor "bpy.types.MaterialGPencilStyle.random_strength_factor")
- [`bpy.types.MaterialGPencilStyle.random_value_factor`](bpy.types.MaterialGPencilStyle.md#bpy.types.MaterialGPencilStyle.random_value_factor "bpy.types.MaterialGPencilStyle.random_value_factor")
- [`bpy.types.MaterialGPencilStyle.use_randomization`](bpy.types.MaterialGPencilStyle.md#bpy.types.MaterialGPencilStyle.use_randomization "bpy.types.MaterialGPencilStyle.use_randomization")

<a id="bpy-types-menu"></a>

### bpy.types.Menu

<a id="function-arguments"></a>

#### Function Arguments

- [`bpy.types.Menu.draw_preset`](bpy.types.Menu.md#bpy.types.Menu.draw_preset "bpy.types.Menu.draw_preset") (self, context), *was (self, _context)*
- [`bpy.types.Menu.path_menu`](bpy.types.Menu.md#bpy.types.Menu.path_menu "bpy.types.Menu.path_menu") (self, searchpaths, operator, props_default, prop_filepath, filter_ext, filter_path, display_name, add_operator, add_operator_props, translate, recursive_paths), *was (self, searchpaths, operator, props_default, prop_filepath, filter_ext, filter_path, display_name, add_operator, add_operator_props, translate)*

<a id="bpy-types-movieclipproxy"></a>

### bpy.types.MovieClipProxy

<a id="id22"></a>

#### Removed

- **build_record_run**
- **timecode**

<a id="bpy-types-node"></a>

### bpy.types.Node

<a id="id23"></a>

#### Added

- [`bpy.types.Node.panel_states`](bpy.types.Node.md#bpy.types.Node.panel_states "bpy.types.Node.panel_states")

<a id="id24"></a>

#### Function Arguments

- [`bpy.types.Node.poll`](bpy.types.Node.md#bpy.types.Node.poll "bpy.types.Node.poll") (ntree), *was (_ntree)*

<a id="bpy-types-nodecustomgroup"></a>

### bpy.types.NodeCustomGroup

<a id="id25"></a>

#### Function Arguments

- `bpy.types.NodeCustomGroup.poll` (ntree), *was (_ntree)*

<a id="bpy-types-nodetreeinterfacepanel"></a>

### bpy.types.NodeTreeInterfacePanel

<a id="id26"></a>

#### Added

- [`bpy.types.NodeTreeInterfacePanel.identifier`](bpy.types.NodeTreeInterfacePanel.md#bpy.types.NodeTreeInterfacePanel.identifier "bpy.types.NodeTreeInterfacePanel.identifier")

<a id="bpy-types-nodesmodifier"></a>

### bpy.types.NodesModifier

<a id="id27"></a>

#### Added

- [`bpy.types.NodesModifier.is_input_used`](bpy.types.NodesModifier.md#bpy.types.NodesModifier.is_input_used "bpy.types.NodesModifier.is_input_used")
- [`bpy.types.NodesModifier.is_input_visible`](bpy.types.NodesModifier.md#bpy.types.NodesModifier.is_input_visible "bpy.types.NodesModifier.is_input_visible")
- [`bpy.types.NodesModifier.properties`](bpy.types.NodesModifier.md#bpy.types.NodesModifier.properties "bpy.types.NodesModifier.properties")

<a id="id28"></a>

#### Removed

- **bl_system_properties_get**

<a id="bpy-types-object"></a>

### bpy.types.Object

<a id="id29"></a>

#### Added

- [`bpy.types.Object.parent_bone_head_tail_factor`](bpy.types.Object.md#bpy.types.Object.parent_bone_head_tail_factor "bpy.types.Object.parent_bone_head_tail_factor")
- [`bpy.types.Object.visible_raycast`](bpy.types.Object.md#bpy.types.Object.visible_raycast "bpy.types.Object.visible_raycast")

<a id="bpy-types-paint"></a>

### bpy.types.Paint

<a id="id30"></a>

#### Removed

- **eraser_brush**

<a id="id31"></a>

#### Renamed

- **eraser_brush_asset_reference** -> [`bpy.types.Paint.mesh_automasking_settings`](bpy.types.Paint.md#bpy.types.Paint.mesh_automasking_settings "bpy.types.Paint.mesh_automasking_settings")

<a id="bpy-types-panel"></a>

### bpy.types.Panel

<a id="id32"></a>

#### Added

- [`bpy.types.Panel.bl_icon`](bpy.types.Panel.md#bpy.types.Panel.bl_icon "bpy.types.Panel.bl_icon")
- [`bpy.types.Panel.bl_icon_value`](bpy.types.Panel.md#bpy.types.Panel.bl_icon_value "bpy.types.Panel.bl_icon_value")

<a id="bpy-types-preferences"></a>

### bpy.types.Preferences

<a id="id33"></a>

#### Added

- [`bpy.types.Preferences.asset_libraries`](bpy.types.Preferences.md#bpy.types.Preferences.asset_libraries "bpy.types.Preferences.asset_libraries")

<a id="bpy-types-preferencesexperimental"></a>

### bpy.types.PreferencesExperimental

<a id="id34"></a>

#### Removed

- **use_geometry_bundle**

<a id="id35"></a>

#### Renamed

- **use_geometry_nodes_lists** -> [`bpy.types.PreferencesExperimental.use_collection_importer`](bpy.types.PreferencesExperimental.md#bpy.types.PreferencesExperimental.use_collection_importer "bpy.types.PreferencesExperimental.use_collection_importer")
- **use_geometry_nodes_lists** -> [`bpy.types.PreferencesExperimental.use_remote_asset_libraries`](bpy.types.PreferencesExperimental.md#bpy.types.PreferencesExperimental.use_remote_asset_libraries "bpy.types.PreferencesExperimental.use_remote_asset_libraries")

<a id="bpy-types-preferencesfilepaths"></a>

### bpy.types.PreferencesFilePaths

<a id="id36"></a>

#### Added

- [`bpy.types.PreferencesFilePaths.save_modified_images`](bpy.types.PreferencesFilePaths.md#bpy.types.PreferencesFilePaths.save_modified_images "bpy.types.PreferencesFilePaths.save_modified_images")
- [`bpy.types.PreferencesFilePaths.texture_cache_directory`](bpy.types.PreferencesFilePaths.md#bpy.types.PreferencesFilePaths.texture_cache_directory "bpy.types.PreferencesFilePaths.texture_cache_directory")

<a id="bpy-types-preferencessystem"></a>

### bpy.types.PreferencesSystem

<a id="id37"></a>

#### Added

- [`bpy.types.PreferencesSystem.geometry_nodes_stack_limit`](bpy.types.PreferencesSystem.md#bpy.types.PreferencesSystem.geometry_nodes_stack_limit "bpy.types.PreferencesSystem.geometry_nodes_stack_limit")
- [`bpy.types.PreferencesSystem.show_panel_tabs_compact`](bpy.types.PreferencesSystem.md#bpy.types.PreferencesSystem.show_panel_tabs_compact "bpy.types.PreferencesSystem.show_panel_tabs_compact")

<a id="id38"></a>

#### Removed

- **image_draw_method**

<a id="bpy-types-preferencesview"></a>

### bpy.types.PreferencesView

<a id="id39"></a>

#### Added

- [`bpy.types.PreferencesView.asset_access`](bpy.types.PreferencesView.md#bpy.types.PreferencesView.asset_access "bpy.types.PreferencesView.asset_access")
- [`bpy.types.PreferencesView.date_format`](bpy.types.PreferencesView.md#bpy.types.PreferencesView.date_format "bpy.types.PreferencesView.date_format")
- [`bpy.types.PreferencesView.time_format`](bpy.types.PreferencesView.md#bpy.types.PreferencesView.time_format "bpy.types.PreferencesView.time_format")

<a id="bpy-types-raytraceeevee"></a>

### bpy.types.RaytraceEEVEE

<a id="id40"></a>

#### Added

- [`bpy.types.RaytraceEEVEE.backface_radiance_scale`](bpy.types.RaytraceEEVEE.md#bpy.types.RaytraceEEVEE.backface_radiance_scale "bpy.types.RaytraceEEVEE.backface_radiance_scale")
- [`bpy.types.RaytraceEEVEE.use_backface_hit`](bpy.types.RaytraceEEVEE.md#bpy.types.RaytraceEEVEE.use_backface_hit "bpy.types.RaytraceEEVEE.use_backface_hit")

<a id="bpy-types-rendersettings"></a>

### bpy.types.RenderSettings

<a id="id41"></a>

#### Added

- [`bpy.types.RenderSettings.anisotropic_filter`](bpy.types.RenderSettings.md#bpy.types.RenderSettings.anisotropic_filter "bpy.types.RenderSettings.anisotropic_filter")
- [`bpy.types.RenderSettings.save_output`](bpy.types.RenderSettings.md#bpy.types.RenderSettings.save_output "bpy.types.RenderSettings.save_output")
- [`bpy.types.RenderSettings.use_auto_generate_texture_cache`](bpy.types.RenderSettings.md#bpy.types.RenderSettings.use_auto_generate_texture_cache "bpy.types.RenderSettings.use_auto_generate_texture_cache")
- [`bpy.types.RenderSettings.use_texture_cache`](bpy.types.RenderSettings.md#bpy.types.RenderSettings.use_texture_cache "bpy.types.RenderSettings.use_texture_cache")

<a id="bpy-types-scene-ul-gltf2-filter-action"></a>

### bpy.types.SCENE_UL_gltf2_filter_action

<a id="id42"></a>

#### Added

- `bpy.types.SCENE_UL_gltf2_filter_action.filter_items`

<a id="bpy-types-scene"></a>

### bpy.types.Scene

<a id="id43"></a>

#### Added

- [`bpy.types.Scene.allow_preroll`](bpy.types.Scene.md#bpy.types.Scene.allow_preroll "bpy.types.Scene.allow_preroll")
- [`bpy.types.Scene.playback_loop_mode`](bpy.types.Scene.md#bpy.types.Scene.playback_loop_mode "bpy.types.Scene.playback_loop_mode")

<a id="bpy-types-sceneeevee"></a>

### bpy.types.SceneEEVEE

<a id="id44"></a>

#### Removed

- **fast_gi_thickness_far**

<a id="bpy-types-scenestrip"></a>

### bpy.types.SceneStrip

<a id="id45"></a>

#### Added

- [`bpy.types.SceneStrip.view_layer`](bpy.types.SceneStrip.md#bpy.types.SceneStrip.view_layer "bpy.types.SceneStrip.view_layer")

<a id="bpy-types-sculpt"></a>

### bpy.types.Sculpt

<a id="id46"></a>

#### Removed

- **automasking_boundary_edges_propagation_steps**
- **automasking_cavity_blur_steps**
- **automasking_cavity_curve**
- **automasking_cavity_curve_op**
- **automasking_cavity_factor**
- **automasking_start_normal_falloff**
- **automasking_start_normal_limit**
- **automasking_view_normal_falloff**
- **automasking_view_normal_limit**
- **use_automasking_boundary_edges**
- **use_automasking_boundary_face_sets**
- **use_automasking_cavity**
- **use_automasking_cavity_inverted**
- **use_automasking_custom_cavity_curve**
- **use_automasking_face_sets**
- **use_automasking_start_normal**
- **use_automasking_topology**
- **use_automasking_view_normal**
- **use_automasking_view_occlusion**

<a id="bpy-types-sequencercompositormodifierdata"></a>

### bpy.types.SequencerCompositorModifierData

<a id="id47"></a>

#### Added

- [`bpy.types.SequencerCompositorModifierData.properties`](bpy.types.SequencerCompositorModifierData.md#bpy.types.SequencerCompositorModifierData.properties "bpy.types.SequencerCompositorModifierData.properties")
- [`bpy.types.SequencerCompositorModifierData.show_group_selector`](bpy.types.SequencerCompositorModifierData.md#bpy.types.SequencerCompositorModifierData.show_group_selector "bpy.types.SequencerCompositorModifierData.show_group_selector")

<a id="bpy-types-sequencerpreviewoverlay"></a>

### bpy.types.SequencerPreviewOverlay

<a id="id48"></a>

#### Added

- [`bpy.types.SequencerPreviewOverlay.composition_guide_color`](bpy.types.SequencerPreviewOverlay.md#bpy.types.SequencerPreviewOverlay.composition_guide_color "bpy.types.SequencerPreviewOverlay.composition_guide_color")
- [`bpy.types.SequencerPreviewOverlay.show_composition_center`](bpy.types.SequencerPreviewOverlay.md#bpy.types.SequencerPreviewOverlay.show_composition_center "bpy.types.SequencerPreviewOverlay.show_composition_center")
- [`bpy.types.SequencerPreviewOverlay.show_composition_center_diagonal`](bpy.types.SequencerPreviewOverlay.md#bpy.types.SequencerPreviewOverlay.show_composition_center_diagonal "bpy.types.SequencerPreviewOverlay.show_composition_center_diagonal")
- [`bpy.types.SequencerPreviewOverlay.show_composition_golden`](bpy.types.SequencerPreviewOverlay.md#bpy.types.SequencerPreviewOverlay.show_composition_golden "bpy.types.SequencerPreviewOverlay.show_composition_golden")
- [`bpy.types.SequencerPreviewOverlay.show_composition_golden_tria_a`](bpy.types.SequencerPreviewOverlay.md#bpy.types.SequencerPreviewOverlay.show_composition_golden_tria_a "bpy.types.SequencerPreviewOverlay.show_composition_golden_tria_a")
- [`bpy.types.SequencerPreviewOverlay.show_composition_golden_tria_b`](bpy.types.SequencerPreviewOverlay.md#bpy.types.SequencerPreviewOverlay.show_composition_golden_tria_b "bpy.types.SequencerPreviewOverlay.show_composition_golden_tria_b")
- [`bpy.types.SequencerPreviewOverlay.show_composition_guides`](bpy.types.SequencerPreviewOverlay.md#bpy.types.SequencerPreviewOverlay.show_composition_guides "bpy.types.SequencerPreviewOverlay.show_composition_guides")
- [`bpy.types.SequencerPreviewOverlay.show_composition_harmony_tri_a`](bpy.types.SequencerPreviewOverlay.md#bpy.types.SequencerPreviewOverlay.show_composition_harmony_tri_a "bpy.types.SequencerPreviewOverlay.show_composition_harmony_tri_a")
- [`bpy.types.SequencerPreviewOverlay.show_composition_harmony_tri_b`](bpy.types.SequencerPreviewOverlay.md#bpy.types.SequencerPreviewOverlay.show_composition_harmony_tri_b "bpy.types.SequencerPreviewOverlay.show_composition_harmony_tri_b")
- [`bpy.types.SequencerPreviewOverlay.show_composition_thirds`](bpy.types.SequencerPreviewOverlay.md#bpy.types.SequencerPreviewOverlay.show_composition_thirds "bpy.types.SequencerPreviewOverlay.show_composition_thirds")

<a id="bpy-types-sequencertimelineoverlay"></a>

### bpy.types.SequencerTimelineOverlay

<a id="id49"></a>

#### Added

- [`bpy.types.SequencerTimelineOverlay.thumbnail_display_style`](bpy.types.SequencerTimelineOverlay.md#bpy.types.SequencerTimelineOverlay.thumbnail_display_style "bpy.types.SequencerTimelineOverlay.thumbnail_display_style")

<a id="id50"></a>

#### Removed

- **show_thumbnails**

<a id="bpy-types-sequencertoolsettings"></a>

### bpy.types.SequencerToolSettings

<a id="id51"></a>

#### Added

- [`bpy.types.SequencerToolSettings.snap_to_all_channels`](bpy.types.SequencerToolSettings.md#bpy.types.SequencerToolSettings.snap_to_all_channels "bpy.types.SequencerToolSettings.snap_to_all_channels")

<a id="bpy-types-shadernoderaycast"></a>

### bpy.types.ShaderNodeRaycast

<a id="id52"></a>

#### Added

- [`bpy.types.ShaderNodeRaycast.active_index`](bpy.types.ShaderNodeRaycast.md#bpy.types.ShaderNodeRaycast.active_index "bpy.types.ShaderNodeRaycast.active_index")
- [`bpy.types.ShaderNodeRaycast.active_item`](bpy.types.ShaderNodeRaycast.md#bpy.types.ShaderNodeRaycast.active_item "bpy.types.ShaderNodeRaycast.active_item")
- [`bpy.types.ShaderNodeRaycast.sample_attribute_items`](bpy.types.ShaderNodeRaycast.md#bpy.types.ShaderNodeRaycast.sample_attribute_items "bpy.types.ShaderNodeRaycast.sample_attribute_items")

<a id="bpy-types-spaceimageeditor"></a>

### bpy.types.SpaceImageEditor

<a id="id53"></a>

#### Added

- [`bpy.types.SpaceImageEditor.show_gizmo_active_node`](bpy.types.SpaceImageEditor.md#bpy.types.SpaceImageEditor.show_gizmo_active_node "bpy.types.SpaceImageEditor.show_gizmo_active_node")

<a id="bpy-types-spacenodeoverlay"></a>

### bpy.types.SpaceNodeOverlay

<a id="id54"></a>

#### Added

- [`bpy.types.SpaceNodeOverlay.passepartout_alpha`](bpy.types.SpaceNodeOverlay.md#bpy.types.SpaceNodeOverlay.passepartout_alpha "bpy.types.SpaceNodeOverlay.passepartout_alpha")
- [`bpy.types.SpaceNodeOverlay.show_render_size`](bpy.types.SpaceNodeOverlay.md#bpy.types.SpaceNodeOverlay.show_render_size "bpy.types.SpaceNodeOverlay.show_render_size")

<a id="bpy-types-spaceoutliner"></a>

### bpy.types.SpaceOutliner

<a id="id55"></a>

#### Added

- [`bpy.types.SpaceOutliner.scroll_to_active`](bpy.types.SpaceOutliner.md#bpy.types.SpaceOutliner.scroll_to_active "bpy.types.SpaceOutliner.scroll_to_active")

<a id="bpy-types-spacesequenceeditor"></a>

### bpy.types.SpaceSequenceEditor

<a id="id56"></a>

#### Added

- [`bpy.types.SpaceSequenceEditor.show_scrubbing_region`](bpy.types.SpaceSequenceEditor.md#bpy.types.SpaceSequenceEditor.show_scrubbing_region "bpy.types.SpaceSequenceEditor.show_scrubbing_region")

<a id="bpy-types-spreadsheetrowfilter"></a>

### bpy.types.SpreadsheetRowFilter

<a id="id57"></a>

#### Added

- [`bpy.types.SpreadsheetRowFilter.value_float4`](bpy.types.SpreadsheetRowFilter.md#bpy.types.SpreadsheetRowFilter.value_float4 "bpy.types.SpreadsheetRowFilter.value_float4")

<a id="bpy-types-strip"></a>

### bpy.types.Strip

<a id="id58"></a>

#### Added

- [`bpy.types.Strip.connections`](bpy.types.Strip.md#bpy.types.Strip.connections "bpy.types.Strip.connections")

<a id="id59"></a>

#### Removed

- **use_linear_modifiers**

<a id="bpy-types-stripmodifier"></a>

### bpy.types.StripModifier

<a id="id60"></a>

#### Added

- [`bpy.types.StripModifier.show_preview`](bpy.types.StripModifier.md#bpy.types.StripModifier.show_preview "bpy.types.StripModifier.show_preview")

<a id="bpy-types-stripproxy"></a>

### bpy.types.StripProxy

<a id="id61"></a>

#### Removed

- **build_record_run**
- **timecode**

<a id="bpy-types-stripsmeta"></a>

### bpy.types.StripsMeta

<a id="id62"></a>

#### Function Arguments

- [`bpy.types.StripsMeta.new_movie`](bpy.types.StripsMeta.md#bpy.types.StripsMeta.new_movie "bpy.types.StripsMeta.new_movie") (name, filepath, channel, frame_start, fit_method, stream), *was (name, filepath, channel, frame_start, fit_method)*
- [`bpy.types.StripsMeta.new_sound`](bpy.types.StripsMeta.md#bpy.types.StripsMeta.new_sound "bpy.types.StripsMeta.new_sound") (name, filepath, channel, frame_start, stream), *was (name, filepath, channel, frame_start)*

<a id="bpy-types-stripstoplevel"></a>

### bpy.types.StripsTopLevel

<a id="id63"></a>

#### Function Arguments

- [`bpy.types.StripsTopLevel.new_movie`](bpy.types.StripsTopLevel.md#bpy.types.StripsTopLevel.new_movie "bpy.types.StripsTopLevel.new_movie") (name, filepath, channel, frame_start, fit_method, stream), *was (name, filepath, channel, frame_start, fit_method)*
- [`bpy.types.StripsTopLevel.new_sound`](bpy.types.StripsTopLevel.md#bpy.types.StripsTopLevel.new_sound "bpy.types.StripsTopLevel.new_sound") (name, filepath, channel, frame_start, stream), *was (name, filepath, channel, frame_start)*

<a id="bpy-types-textstrip"></a>

### bpy.types.TextStrip

<a id="id64"></a>

#### Added

- [`bpy.types.TextStrip.abs_space_line`](bpy.types.TextStrip.md#bpy.types.TextStrip.abs_space_line "bpy.types.TextStrip.abs_space_line")
- [`bpy.types.TextStrip.space_line`](bpy.types.TextStrip.md#bpy.types.TextStrip.space_line "bpy.types.TextStrip.space_line")
- [`bpy.types.TextStrip.textbox_state`](bpy.types.TextStrip.md#bpy.types.TextStrip.textbox_state "bpy.types.TextStrip.textbox_state")
- [`bpy.types.TextStrip.use_absolute_line_spacing`](bpy.types.TextStrip.md#bpy.types.TextStrip.use_absolute_line_spacing "bpy.types.TextStrip.use_absolute_line_spacing")

<a id="bpy-types-themeuserinterface"></a>

### bpy.types.ThemeUserInterface

<a id="id65"></a>

#### Added

- [`bpy.types.ThemeUserInterface.link`](bpy.types.ThemeUserInterface.md#bpy.types.ThemeUserInterface.link "bpy.types.ThemeUserInterface.link")

<a id="bpy-types-themeview3d"></a>

### bpy.types.ThemeView3D

<a id="id66"></a>

#### Added

- [`bpy.types.ThemeView3D.grid_axis_brightness`](bpy.types.ThemeView3D.md#bpy.types.ThemeView3D.grid_axis_brightness "bpy.types.ThemeView3D.grid_axis_brightness")

<a id="bpy-types-uilayout"></a>

### bpy.types.UILayout

<a id="id67"></a>

#### Added

- [`bpy.types.UILayout.link`](bpy.types.UILayout.md#bpy.types.UILayout.link "bpy.types.UILayout.link")
- [`bpy.types.UILayout.template_collection_importer`](bpy.types.UILayout.md#bpy.types.UILayout.template_collection_importer "bpy.types.UILayout.template_collection_importer")
- [`bpy.types.UILayout.textbox`](bpy.types.UILayout.md#bpy.types.UILayout.textbox "bpy.types.UILayout.textbox")
- [`bpy.types.UILayout.textbox_with_state`](bpy.types.UILayout.md#bpy.types.UILayout.textbox_with_state "bpy.types.UILayout.textbox_with_state")

<a id="id68"></a>

#### Function Arguments

- [`bpy.types.UILayout.prop`](bpy.types.UILayout.md#bpy.types.UILayout.prop "bpy.types.UILayout.prop") (data, property, text, text_ctxt, translate, icon, placeholder, expand, slider, toggle, icon_only, event, full_event, emboss, index, icon_value, invert_checkbox, text_align), *was (data, property, text, text_ctxt, translate, icon, placeholder, expand, slider, toggle, icon_only, event, full_event, emboss, index, icon_value, invert_checkbox)*
- [`bpy.types.UILayout.template_palette`](bpy.types.UILayout.md#bpy.types.UILayout.template_palette "bpy.types.UILayout.template_palette") (data, property), *was (data, property, color)*

<a id="bpy-types-uvlooplayers"></a>

### bpy.types.UVLoopLayers

<a id="id69"></a>

#### Added

- [`bpy.types.UVLoopLayers.active_render`](bpy.types.UVLoopLayers.md#bpy.types.UVLoopLayers.active_render "bpy.types.UVLoopLayers.active_render")
- [`bpy.types.UVLoopLayers.active_render_index`](bpy.types.UVLoopLayers.md#bpy.types.UVLoopLayers.active_render_index "bpy.types.UVLoopLayers.active_render_index")

<a id="bpy-types-userassetlibrary"></a>

### bpy.types.UserAssetLibrary

<a id="id70"></a>

#### Added

- [`bpy.types.UserAssetLibrary.remote_url`](bpy.types.UserAssetLibrary.md#bpy.types.UserAssetLibrary.remote_url "bpy.types.UserAssetLibrary.remote_url")
- [`bpy.types.UserAssetLibrary.use_remote_url`](bpy.types.UserAssetLibrary.md#bpy.types.UserAssetLibrary.use_remote_url "bpy.types.UserAssetLibrary.use_remote_url")

<a id="bpy-types-windowmanager"></a>

### bpy.types.WindowManager

<a id="id71"></a>

#### Added

- [`bpy.types.WindowManager.asset_library_status_begin_loading`](bpy.types.WindowManager.md#bpy.types.WindowManager.asset_library_status_begin_loading "bpy.types.WindowManager.asset_library_status_begin_loading")
- [`bpy.types.WindowManager.asset_library_status_failed_loading`](bpy.types.WindowManager.md#bpy.types.WindowManager.asset_library_status_failed_loading "bpy.types.WindowManager.asset_library_status_failed_loading")
- [`bpy.types.WindowManager.asset_library_status_finished_loading`](bpy.types.WindowManager.md#bpy.types.WindowManager.asset_library_status_finished_loading "bpy.types.WindowManager.asset_library_status_finished_loading")
- [`bpy.types.WindowManager.asset_library_status_ping_asset_file_failed`](bpy.types.WindowManager.md#bpy.types.WindowManager.asset_library_status_ping_asset_file_failed "bpy.types.WindowManager.asset_library_status_ping_asset_file_failed")
- [`bpy.types.WindowManager.asset_library_status_ping_asset_file_progress`](bpy.types.WindowManager.md#bpy.types.WindowManager.asset_library_status_ping_asset_file_progress "bpy.types.WindowManager.asset_library_status_ping_asset_file_progress")
- [`bpy.types.WindowManager.asset_library_status_ping_asset_file_succeeded`](bpy.types.WindowManager.md#bpy.types.WindowManager.asset_library_status_ping_asset_file_succeeded "bpy.types.WindowManager.asset_library_status_ping_asset_file_succeeded")
- [`bpy.types.WindowManager.asset_library_status_ping_finished_download_queue`](bpy.types.WindowManager.md#bpy.types.WindowManager.asset_library_status_ping_finished_download_queue "bpy.types.WindowManager.asset_library_status_ping_finished_download_queue")
- [`bpy.types.WindowManager.asset_library_status_ping_loaded_new_pages`](bpy.types.WindowManager.md#bpy.types.WindowManager.asset_library_status_ping_loaded_new_pages "bpy.types.WindowManager.asset_library_status_ping_loaded_new_pages")
- [`bpy.types.WindowManager.asset_library_status_ping_loaded_new_preview`](bpy.types.WindowManager.md#bpy.types.WindowManager.asset_library_status_ping_loaded_new_preview "bpy.types.WindowManager.asset_library_status_ping_loaded_new_preview")
- [`bpy.types.WindowManager.asset_library_status_ping_metafiles_in_place`](bpy.types.WindowManager.md#bpy.types.WindowManager.asset_library_status_ping_metafiles_in_place "bpy.types.WindowManager.asset_library_status_ping_metafiles_in_place")
- [`bpy.types.WindowManager.asset_library_status_ping_still_loading`](bpy.types.WindowManager.md#bpy.types.WindowManager.asset_library_status_ping_still_loading "bpy.types.WindowManager.asset_library_status_ping_still_loading")
- [`bpy.types.WindowManager.is_event_handling_break`](bpy.types.WindowManager.md#bpy.types.WindowManager.is_event_handling_break "bpy.types.WindowManager.is_event_handling_break")
- [`bpy.types.WindowManager.register_node_group_operators`](bpy.types.WindowManager.md#bpy.types.WindowManager.register_node_group_operators "bpy.types.WindowManager.register_node_group_operators")
- [`bpy.types.WindowManager.reports`](bpy.types.WindowManager.md#bpy.types.WindowManager.reports "bpy.types.WindowManager.reports")

<a id="id72"></a>

#### Function Arguments

- [`bpy.types.WindowManager.invoke_popup`](bpy.types.WindowManager.md#bpy.types.WindowManager.invoke_popup "bpy.types.WindowManager.invoke_popup") (operator, width, auto_keymap), *was (operator, width)*

<a id="bpy-types-xrsessionsettings"></a>

### bpy.types.XrSessionSettings

<a id="id73"></a>

#### Added

- [`bpy.types.XrSessionSettings.viewfinder_crosshair_enabled`](bpy.types.XrSessionSettings.md#bpy.types.XrSessionSettings.viewfinder_crosshair_enabled "bpy.types.XrSessionSettings.viewfinder_crosshair_enabled")
- [`bpy.types.XrSessionSettings.viewfinder_enabled`](bpy.types.XrSessionSettings.md#bpy.types.XrSessionSettings.viewfinder_enabled "bpy.types.XrSessionSettings.viewfinder_enabled")
- [`bpy.types.XrSessionSettings.viewfinder_hand`](bpy.types.XrSessionSettings.md#bpy.types.XrSessionSettings.viewfinder_hand "bpy.types.XrSessionSettings.viewfinder_hand")
- [`bpy.types.XrSessionSettings.viewfinder_passepartout_opacity`](bpy.types.XrSessionSettings.md#bpy.types.XrSessionSettings.viewfinder_passepartout_opacity "bpy.types.XrSessionSettings.viewfinder_passepartout_opacity")
- [`bpy.types.XrSessionSettings.viewfinder_passepartout_overscan`](bpy.types.XrSessionSettings.md#bpy.types.XrSessionSettings.viewfinder_passepartout_overscan "bpy.types.XrSessionSettings.viewfinder_passepartout_overscan")
- [`bpy.types.XrSessionSettings.viewfinder_scale`](bpy.types.XrSessionSettings.md#bpy.types.XrSessionSettings.viewfinder_scale "bpy.types.XrSessionSettings.viewfinder_scale")

<a id="bpy-types-xrsessionstate"></a>

### bpy.types.XrSessionState

<a id="id74"></a>

#### Added

- [`bpy.types.XrSessionState.viewfinder`](bpy.types.XrSessionState.md#bpy.types.XrSessionState.viewfinder "bpy.types.XrSessionState.viewfinder")

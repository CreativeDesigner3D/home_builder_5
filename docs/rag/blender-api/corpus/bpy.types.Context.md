<!-- source: Blender Python API reference 5.2 / bpy.types.Context.html -->

<a id="context-bpy-struct"></a>

# Context(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.Context"></a>

### class bpy.types.Context(bpy_struct)

Current windowmanager and data context

<a id="bpy.types.Context.area"></a>

#### bpy.types.Context.area

(readonly)

**Type:**

[`Area`](bpy.types.Area.md#bpy.types.Area "bpy.types.Area") | None

<a id="bpy.types.Context.asset"></a>

#### bpy.types.Context.asset

(readonly)

**Type:**

[`AssetRepresentation`](bpy.types.AssetRepresentation.md#bpy.types.AssetRepresentation "bpy.types.AssetRepresentation") | None

<a id="bpy.types.Context.blend_data"></a>

#### bpy.types.Context.blend_data

(readonly)

**Type:**

[`BlendData`](bpy.types.BlendData.md#bpy.types.BlendData "bpy.types.BlendData") | None

<a id="bpy.types.Context.collection"></a>

#### bpy.types.Context.collection

(readonly)

**Type:**

[`Collection`](bpy.types.Collection.md#bpy.types.Collection "bpy.types.Collection") | None

<a id="bpy.types.Context.engine"></a>

#### bpy.types.Context.engine

(default “”, readonly, never None)

**Type:**

str

<a id="bpy.types.Context.gizmo_group"></a>

#### bpy.types.Context.gizmo_group

(readonly)

**Type:**

[`GizmoGroup`](bpy.types.GizmoGroup.md#bpy.types.GizmoGroup "bpy.types.GizmoGroup") | None

<a id="bpy.types.Context.layer_collection"></a>

#### bpy.types.Context.layer_collection

(readonly)

**Type:**

[`LayerCollection`](bpy.types.LayerCollection.md#bpy.types.LayerCollection "bpy.types.LayerCollection") | None

<a id="bpy.types.Context.mode"></a>

#### bpy.types.Context.mode

(default `'EDIT_MESH'`, readonly)

**Type:**

Literal[[Context Mode Items](bpy_types_enum_items/context_mode_items.md#rna-enum-context-mode-items)]

<a id="bpy.types.Context.preferences"></a>

#### bpy.types.Context.preferences

(readonly)

**Type:**

[`Preferences`](bpy.types.Preferences.md#bpy.types.Preferences "bpy.types.Preferences") | None

<a id="bpy.types.Context.region"></a>

#### bpy.types.Context.region

(readonly)

**Type:**

[`Region`](bpy.types.Region.md#bpy.types.Region "bpy.types.Region") | None

<a id="bpy.types.Context.region_data"></a>

#### bpy.types.Context.region_data

(readonly)

**Type:**

[`RegionView3D`](bpy.types.RegionView3D.md#bpy.types.RegionView3D "bpy.types.RegionView3D") | None

<a id="bpy.types.Context.region_popup"></a>

#### bpy.types.Context.region_popup

The temporary region for pop-ups (including menus and pop-overs) (readonly)

**Type:**

[`Region`](bpy.types.Region.md#bpy.types.Region "bpy.types.Region") | None

<a id="bpy.types.Context.scene"></a>

#### bpy.types.Context.scene

(readonly)

**Type:**

[`Scene`](bpy.types.Scene.md#bpy.types.Scene "bpy.types.Scene") | None

<a id="bpy.types.Context.screen"></a>

#### bpy.types.Context.screen

(readonly)

**Type:**

[`Screen`](bpy.types.Screen.md#bpy.types.Screen "bpy.types.Screen") | None

<a id="bpy.types.Context.space_data"></a>

#### bpy.types.Context.space_data

The current space, may be None in background-mode, when the cursor is outside the window or when using menu-search (readonly)

**Type:**

[`Space`](bpy.types.Space.md#bpy.types.Space "bpy.types.Space") | None

<a id="bpy.types.Context.tool_settings"></a>

#### bpy.types.Context.tool_settings

(readonly)

**Type:**

[`ToolSettings`](bpy.types.ToolSettings.md#bpy.types.ToolSettings "bpy.types.ToolSettings") | None

<a id="bpy.types.Context.view_layer"></a>

#### bpy.types.Context.view_layer

(readonly)

**Type:**

[`ViewLayer`](bpy.types.ViewLayer.md#bpy.types.ViewLayer "bpy.types.ViewLayer") | None

<a id="bpy.types.Context.window"></a>

#### bpy.types.Context.window

(readonly)

**Type:**

[`Window`](bpy.types.Window.md#bpy.types.Window "bpy.types.Window") | None

<a id="bpy.types.Context.window_manager"></a>

#### bpy.types.Context.window_manager

(readonly)

**Type:**

[`WindowManager`](bpy.types.WindowManager.md#bpy.types.WindowManager "bpy.types.WindowManager") | None

<a id="bpy.types.Context.workspace"></a>

#### bpy.types.Context.workspace

(readonly)

**Type:**

[`WorkSpace`](bpy.types.WorkSpace.md#bpy.types.WorkSpace "bpy.types.WorkSpace") | None

Buttons Context

<a id="bpy.types.Context.texture_slot"></a>

#### bpy.types.Context.texture_slot

**Type:**

[`TextureSlot`](bpy.types.TextureSlot.md#bpy.types.TextureSlot "bpy.types.TextureSlot")

#### scene

**Type:**

[`Scene`](bpy.types.Scene.md#bpy.types.Scene "bpy.types.Scene")

<a id="bpy.types.Context.world"></a>

#### bpy.types.Context.world

**Type:**

[`World`](bpy.types.World.md#bpy.types.World "bpy.types.World")

<a id="bpy.types.Context.object"></a>

#### bpy.types.Context.object

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object")

<a id="bpy.types.Context.mesh"></a>

#### bpy.types.Context.mesh

**Type:**

[`Mesh`](bpy.types.Mesh.md#bpy.types.Mesh "bpy.types.Mesh")

<a id="bpy.types.Context.armature"></a>

#### bpy.types.Context.armature

**Type:**

[`Armature`](bpy.types.Armature.md#bpy.types.Armature "bpy.types.Armature")

<a id="bpy.types.Context.lattice"></a>

#### bpy.types.Context.lattice

**Type:**

[`Lattice`](bpy.types.Lattice.md#bpy.types.Lattice "bpy.types.Lattice")

<a id="bpy.types.Context.curve"></a>

#### bpy.types.Context.curve

**Type:**

[`Curve`](bpy.types.Curve.md#bpy.types.Curve "bpy.types.Curve")

<a id="bpy.types.Context.meta_ball"></a>

#### bpy.types.Context.meta_ball

**Type:**

[`MetaBall`](bpy.types.MetaBall.md#bpy.types.MetaBall "bpy.types.MetaBall")

<a id="bpy.types.Context.light"></a>

#### bpy.types.Context.light

**Type:**

[`Light`](bpy.types.Light.md#bpy.types.Light "bpy.types.Light")

<a id="bpy.types.Context.speaker"></a>

#### bpy.types.Context.speaker

**Type:**

[`Speaker`](bpy.types.Speaker.md#bpy.types.Speaker "bpy.types.Speaker")

<a id="bpy.types.Context.lightprobe"></a>

#### bpy.types.Context.lightprobe

**Type:**

[`LightProbe`](bpy.types.LightProbe.md#bpy.types.LightProbe "bpy.types.LightProbe")

<a id="bpy.types.Context.camera"></a>

#### bpy.types.Context.camera

**Type:**

[`Camera`](bpy.types.Camera.md#bpy.types.Camera "bpy.types.Camera")

<a id="bpy.types.Context.material"></a>

#### bpy.types.Context.material

**Type:**

[`Material`](bpy.types.Material.md#bpy.types.Material "bpy.types.Material")

<a id="bpy.types.Context.material_slot"></a>

#### bpy.types.Context.material_slot

**Type:**

[`MaterialSlot`](bpy.types.MaterialSlot.md#bpy.types.MaterialSlot "bpy.types.MaterialSlot")

<a id="bpy.types.Context.texture"></a>

#### bpy.types.Context.texture

**Type:**

[`Texture`](bpy.types.Texture.md#bpy.types.Texture "bpy.types.Texture")

<a id="bpy.types.Context.texture_user"></a>

#### bpy.types.Context.texture_user

**Type:**

[`ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID")

<a id="bpy.types.Context.texture_user_property"></a>

#### bpy.types.Context.texture_user_property

**Type:**

[`Property`](bpy.types.Property.md#bpy.types.Property "bpy.types.Property")

<a id="bpy.types.Context.texture_node"></a>

#### bpy.types.Context.texture_node

**Type:**

[`Node`](bpy.types.Node.md#bpy.types.Node "bpy.types.Node")

<a id="bpy.types.Context.bone"></a>

#### bpy.types.Context.bone

**Type:**

[`Bone`](bpy.types.Bone.md#bpy.types.Bone "bpy.types.Bone")

<a id="bpy.types.Context.edit_bone"></a>

#### bpy.types.Context.edit_bone

**Type:**

[`EditBone`](bpy.types.EditBone.md#bpy.types.EditBone "bpy.types.EditBone")

<a id="bpy.types.Context.pose_bone"></a>

#### bpy.types.Context.pose_bone

**Type:**

[`PoseBone`](bpy.types.PoseBone.md#bpy.types.PoseBone "bpy.types.PoseBone")

<a id="bpy.types.Context.particle_system"></a>

#### bpy.types.Context.particle_system

**Type:**

[`ParticleSystem`](bpy.types.ParticleSystem.md#bpy.types.ParticleSystem "bpy.types.ParticleSystem")

<a id="bpy.types.Context.particle_system_editable"></a>

#### bpy.types.Context.particle_system_editable

**Type:**

[`ParticleSystem`](bpy.types.ParticleSystem.md#bpy.types.ParticleSystem "bpy.types.ParticleSystem")

<a id="bpy.types.Context.particle_settings"></a>

#### bpy.types.Context.particle_settings

**Type:**

[`ParticleSettings`](bpy.types.ParticleSettings.md#bpy.types.ParticleSettings "bpy.types.ParticleSettings")

<a id="bpy.types.Context.cloth"></a>

#### bpy.types.Context.cloth

**Type:**

[`ClothModifier`](bpy.types.ClothModifier.md#bpy.types.ClothModifier "bpy.types.ClothModifier")

<a id="bpy.types.Context.soft_body"></a>

#### bpy.types.Context.soft_body

**Type:**

[`SoftBodyModifier`](bpy.types.SoftBodyModifier.md#bpy.types.SoftBodyModifier "bpy.types.SoftBodyModifier")

<a id="bpy.types.Context.fluid"></a>

#### bpy.types.Context.fluid

**Type:**

[`FluidModifier`](bpy.types.FluidModifier.md#bpy.types.FluidModifier "bpy.types.FluidModifier")

<a id="bpy.types.Context.collision"></a>

#### bpy.types.Context.collision

**Type:**

[`CollisionModifier`](bpy.types.CollisionModifier.md#bpy.types.CollisionModifier "bpy.types.CollisionModifier")

<a id="bpy.types.Context.brush"></a>

#### bpy.types.Context.brush

**Type:**

[`Brush`](bpy.types.Brush.md#bpy.types.Brush "bpy.types.Brush")

<a id="bpy.types.Context.dynamic_paint"></a>

#### bpy.types.Context.dynamic_paint

**Type:**

[`DynamicPaintModifier`](bpy.types.DynamicPaintModifier.md#bpy.types.DynamicPaintModifier "bpy.types.DynamicPaintModifier")

<a id="bpy.types.Context.line_style"></a>

#### bpy.types.Context.line_style

**Type:**

[`FreestyleLineStyle`](bpy.types.FreestyleLineStyle.md#bpy.types.FreestyleLineStyle "bpy.types.FreestyleLineStyle")

#### collection

**Type:**

[`LayerCollection`](bpy.types.LayerCollection.md#bpy.types.LayerCollection "bpy.types.LayerCollection")

<a id="bpy.types.Context.gpencil"></a>

#### bpy.types.Context.gpencil

**Type:**

[`GreasePencil`](bpy.types.GreasePencil.md#bpy.types.GreasePencil "bpy.types.GreasePencil")

<a id="bpy.types.Context.grease_pencil"></a>

#### bpy.types.Context.grease_pencil

**Type:**

[`GreasePencil`](bpy.types.GreasePencil.md#bpy.types.GreasePencil "bpy.types.GreasePencil")

<a id="bpy.types.Context.curves"></a>

#### bpy.types.Context.curves

**Type:**

[`Curves`](bpy.types.Curves.md#bpy.types.Curves "bpy.types.Curves")

<a id="bpy.types.Context.pointcloud"></a>

#### bpy.types.Context.pointcloud

**Type:**

[`PointCloud`](bpy.types.PointCloud.md#bpy.types.PointCloud "bpy.types.PointCloud")

<a id="bpy.types.Context.volume"></a>

#### bpy.types.Context.volume

**Type:**

[`Volume`](bpy.types.Volume.md#bpy.types.Volume "bpy.types.Volume")

<a id="bpy.types.Context.strip"></a>

#### bpy.types.Context.strip

**Type:**

[`Strip`](bpy.types.Strip.md#bpy.types.Strip "bpy.types.Strip")

<a id="bpy.types.Context.strip_modifier"></a>

#### bpy.types.Context.strip_modifier

**Type:**

[`StripModifier`](bpy.types.StripModifier.md#bpy.types.StripModifier "bpy.types.StripModifier")

Clip Context

<a id="bpy.types.Context.edit_movieclip"></a>

#### bpy.types.Context.edit_movieclip

**Type:**

[`MovieClip`](bpy.types.MovieClip.md#bpy.types.MovieClip "bpy.types.MovieClip")

<a id="bpy.types.Context.edit_mask"></a>

#### bpy.types.Context.edit_mask

**Type:**

[`Mask`](bpy.types.Mask.md#bpy.types.Mask "bpy.types.Mask")

File Context

<a id="bpy.types.Context.active_file"></a>

#### bpy.types.Context.active_file

**Type:**

[`FileSelectEntry`](bpy.types.FileSelectEntry.md#bpy.types.FileSelectEntry "bpy.types.FileSelectEntry")

<a id="bpy.types.Context.selected_files"></a>

#### bpy.types.Context.selected_files

**Type:**

Sequence[[`FileSelectEntry`](bpy.types.FileSelectEntry.md#bpy.types.FileSelectEntry "bpy.types.FileSelectEntry")]

<a id="bpy.types.Context.asset_library_reference"></a>

#### bpy.types.Context.asset_library_reference

**Type:**

[`AssetLibraryReference`](bpy.types.AssetLibraryReference.md#bpy.types.AssetLibraryReference "bpy.types.AssetLibraryReference")

#### asset

**Type:**

[`AssetRepresentation`](bpy.types.AssetRepresentation.md#bpy.types.AssetRepresentation "bpy.types.AssetRepresentation")

<a id="bpy.types.Context.selected_assets"></a>

#### bpy.types.Context.selected_assets

**Type:**

Sequence[[`AssetRepresentation`](bpy.types.AssetRepresentation.md#bpy.types.AssetRepresentation "bpy.types.AssetRepresentation")]

<a id="bpy.types.Context.id"></a>

#### bpy.types.Context.id

**Type:**

[`ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID")

<a id="bpy.types.Context.selected_ids"></a>

#### bpy.types.Context.selected_ids

**Type:**

Sequence[[`ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID")]

Image Context

<a id="bpy.types.Context.edit_image"></a>

#### bpy.types.Context.edit_image

**Type:**

[`Image`](bpy.types.Image.md#bpy.types.Image "bpy.types.Image")

#### edit_mask

**Type:**

[`Mask`](bpy.types.Mask.md#bpy.types.Mask "bpy.types.Mask")

Node Context

<a id="bpy.types.Context.selected_nodes"></a>

#### bpy.types.Context.selected_nodes

**Type:**

Sequence[[`Node`](bpy.types.Node.md#bpy.types.Node "bpy.types.Node")]

<a id="bpy.types.Context.active_node"></a>

#### bpy.types.Context.active_node

**Type:**

[`Node`](bpy.types.Node.md#bpy.types.Node "bpy.types.Node")

#### light

**Type:**

[`Light`](bpy.types.Light.md#bpy.types.Light "bpy.types.Light")

#### material

**Type:**

[`Material`](bpy.types.Material.md#bpy.types.Material "bpy.types.Material")

#### world

**Type:**

[`World`](bpy.types.World.md#bpy.types.World "bpy.types.World")

Screen Context

#### scene

**Type:**

[`Scene`](bpy.types.Scene.md#bpy.types.Scene "bpy.types.Scene")

#### view_layer

**Type:**

[`ViewLayer`](bpy.types.ViewLayer.md#bpy.types.ViewLayer "bpy.types.ViewLayer")

<a id="bpy.types.Context.visible_objects"></a>

#### bpy.types.Context.visible_objects

**Type:**

Sequence[[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object")]

<a id="bpy.types.Context.selectable_objects"></a>

#### bpy.types.Context.selectable_objects

**Type:**

Sequence[[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object")]

<a id="bpy.types.Context.selected_objects"></a>

#### bpy.types.Context.selected_objects

**Type:**

Sequence[[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object")]

<a id="bpy.types.Context.editable_objects"></a>

#### bpy.types.Context.editable_objects

**Type:**

Sequence[[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object")]

<a id="bpy.types.Context.selected_editable_objects"></a>

#### bpy.types.Context.selected_editable_objects

**Type:**

Sequence[[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object")]

<a id="bpy.types.Context.objects_in_mode"></a>

#### bpy.types.Context.objects_in_mode

**Type:**

Sequence[[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object")]

<a id="bpy.types.Context.objects_in_mode_unique_data"></a>

#### bpy.types.Context.objects_in_mode_unique_data

**Type:**

Sequence[[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object")]

<a id="bpy.types.Context.visible_bones"></a>

#### bpy.types.Context.visible_bones

**Type:**

Sequence[[`EditBone`](bpy.types.EditBone.md#bpy.types.EditBone "bpy.types.EditBone")]

<a id="bpy.types.Context.editable_bones"></a>

#### bpy.types.Context.editable_bones

**Type:**

Sequence[[`EditBone`](bpy.types.EditBone.md#bpy.types.EditBone "bpy.types.EditBone")]

<a id="bpy.types.Context.selected_bones"></a>

#### bpy.types.Context.selected_bones

**Type:**

Sequence[[`EditBone`](bpy.types.EditBone.md#bpy.types.EditBone "bpy.types.EditBone")]

<a id="bpy.types.Context.selected_editable_bones"></a>

#### bpy.types.Context.selected_editable_bones

**Type:**

Sequence[[`EditBone`](bpy.types.EditBone.md#bpy.types.EditBone "bpy.types.EditBone")]

<a id="bpy.types.Context.visible_pose_bones"></a>

#### bpy.types.Context.visible_pose_bones

**Type:**

Sequence[[`PoseBone`](bpy.types.PoseBone.md#bpy.types.PoseBone "bpy.types.PoseBone")]

<a id="bpy.types.Context.selected_pose_bones"></a>

#### bpy.types.Context.selected_pose_bones

**Type:**

Sequence[[`PoseBone`](bpy.types.PoseBone.md#bpy.types.PoseBone "bpy.types.PoseBone")]

<a id="bpy.types.Context.selected_pose_bones_from_active_object"></a>

#### bpy.types.Context.selected_pose_bones_from_active_object

**Type:**

Sequence[[`PoseBone`](bpy.types.PoseBone.md#bpy.types.PoseBone "bpy.types.PoseBone")]

<a id="bpy.types.Context.active_bone"></a>

#### bpy.types.Context.active_bone

**Type:**

[`EditBone`](bpy.types.EditBone.md#bpy.types.EditBone "bpy.types.EditBone") | [`Bone`](bpy.types.Bone.md#bpy.types.Bone "bpy.types.Bone")

<a id="bpy.types.Context.active_pose_bone"></a>

#### bpy.types.Context.active_pose_bone

**Type:**

[`PoseBone`](bpy.types.PoseBone.md#bpy.types.PoseBone "bpy.types.PoseBone")

<a id="bpy.types.Context.active_object"></a>

#### bpy.types.Context.active_object

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object")

#### object

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object")

<a id="bpy.types.Context.edit_object"></a>

#### bpy.types.Context.edit_object

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object")

<a id="bpy.types.Context.sculpt_object"></a>

#### bpy.types.Context.sculpt_object

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object")

<a id="bpy.types.Context.vertex_paint_object"></a>

#### bpy.types.Context.vertex_paint_object

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object")

<a id="bpy.types.Context.weight_paint_object"></a>

#### bpy.types.Context.weight_paint_object

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object")

<a id="bpy.types.Context.image_paint_object"></a>

#### bpy.types.Context.image_paint_object

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object")

<a id="bpy.types.Context.particle_edit_object"></a>

#### bpy.types.Context.particle_edit_object

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object")

<a id="bpy.types.Context.pose_object"></a>

#### bpy.types.Context.pose_object

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object")

<a id="bpy.types.Context.active_nla_track"></a>

#### bpy.types.Context.active_nla_track

**Type:**

[`NlaTrack`](bpy.types.NlaTrack.md#bpy.types.NlaTrack "bpy.types.NlaTrack")

<a id="bpy.types.Context.active_nla_strip"></a>

#### bpy.types.Context.active_nla_strip

**Type:**

[`NlaStrip`](bpy.types.NlaStrip.md#bpy.types.NlaStrip "bpy.types.NlaStrip")

<a id="bpy.types.Context.selected_nla_strips"></a>

#### bpy.types.Context.selected_nla_strips

**Type:**

Sequence[[`NlaStrip`](bpy.types.NlaStrip.md#bpy.types.NlaStrip "bpy.types.NlaStrip")]

<a id="bpy.types.Context.selected_movieclip_tracks"></a>

#### bpy.types.Context.selected_movieclip_tracks

**Type:**

Sequence[[`MovieTrackingTrack`](bpy.types.MovieTrackingTrack.md#bpy.types.MovieTrackingTrack "bpy.types.MovieTrackingTrack")]

<a id="bpy.types.Context.annotation_data"></a>

#### bpy.types.Context.annotation_data

**Type:**

[`GreasePencil`](bpy.types.GreasePencil.md#bpy.types.GreasePencil "bpy.types.GreasePencil")

<a id="bpy.types.Context.annotation_data_owner"></a>

#### bpy.types.Context.annotation_data_owner

**Type:**

[`ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID")

<a id="bpy.types.Context.active_annotation_layer"></a>

#### bpy.types.Context.active_annotation_layer

**Type:**

[`AnnotationLayer`](bpy.types.AnnotationLayer.md#bpy.types.AnnotationLayer "bpy.types.AnnotationLayer")

#### grease_pencil

**Type:**

[`GreasePencil`](bpy.types.GreasePencil.md#bpy.types.GreasePencil "bpy.types.GreasePencil")

<a id="bpy.types.Context.active_operator"></a>

#### bpy.types.Context.active_operator

**Type:**

[`Operator`](bpy.types.Operator.md#bpy.types.Operator "bpy.types.Operator")

<a id="bpy.types.Context.active_action"></a>

#### bpy.types.Context.active_action

**Type:**

[`Action`](bpy.types.Action.md#bpy.types.Action "bpy.types.Action")

<a id="bpy.types.Context.selected_visible_actions"></a>

#### bpy.types.Context.selected_visible_actions

**Type:**

Sequence[[`Action`](bpy.types.Action.md#bpy.types.Action "bpy.types.Action")]

<a id="bpy.types.Context.selected_editable_actions"></a>

#### bpy.types.Context.selected_editable_actions

**Type:**

Sequence[[`Action`](bpy.types.Action.md#bpy.types.Action "bpy.types.Action")]

<a id="bpy.types.Context.visible_fcurves"></a>

#### bpy.types.Context.visible_fcurves

**Type:**

Sequence[[`FCurve`](bpy.types.FCurve.md#bpy.types.FCurve "bpy.types.FCurve")]

<a id="bpy.types.Context.editable_fcurves"></a>

#### bpy.types.Context.editable_fcurves

**Type:**

Sequence[[`FCurve`](bpy.types.FCurve.md#bpy.types.FCurve "bpy.types.FCurve")]

<a id="bpy.types.Context.selected_visible_fcurves"></a>

#### bpy.types.Context.selected_visible_fcurves

**Type:**

Sequence[[`FCurve`](bpy.types.FCurve.md#bpy.types.FCurve "bpy.types.FCurve")]

<a id="bpy.types.Context.selected_editable_fcurves"></a>

#### bpy.types.Context.selected_editable_fcurves

**Type:**

Sequence[[`FCurve`](bpy.types.FCurve.md#bpy.types.FCurve "bpy.types.FCurve")]

<a id="bpy.types.Context.active_editable_fcurve"></a>

#### bpy.types.Context.active_editable_fcurve

**Type:**

[`FCurve`](bpy.types.FCurve.md#bpy.types.FCurve "bpy.types.FCurve")

<a id="bpy.types.Context.selected_editable_keyframes"></a>

#### bpy.types.Context.selected_editable_keyframes

**Type:**

Sequence[[`Keyframe`](bpy.types.Keyframe.md#bpy.types.Keyframe "bpy.types.Keyframe")]

<a id="bpy.types.Context.ui_list"></a>

#### bpy.types.Context.ui_list

**Type:**

[`UIList`](bpy.types.UIList.md#bpy.types.UIList "bpy.types.UIList")

<a id="bpy.types.Context.property"></a>

#### bpy.types.Context.property

**Type:**

[`AnyType`](bpy.types.AnyType.md#bpy.types.AnyType "bpy.types.AnyType") | `str` | `int`

Get the property associated with a hovered button.
Returns a tuple of the data-block, data path to the property, and array index.

> **Note:**
>
> When the property doesn’t have an associated [`bpy.types.ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID") non-ID data may be returned.
> This may occur when accessing windowing data, for example, operator properties.

```python
import bpy

# Example inserting keyframe for the hovered property.
active_property = bpy.context.property
if active_property:
    datablock, data_path, index = active_property
    datablock.keyframe_insert(data_path=data_path, index=index, frame=1)
```

#### asset_library_reference

**Type:**

[`AssetLibraryReference`](bpy.types.AssetLibraryReference.md#bpy.types.AssetLibraryReference "bpy.types.AssetLibraryReference")

<a id="bpy.types.Context.active_strip"></a>

#### bpy.types.Context.active_strip

**Type:**

[`Strip`](bpy.types.Strip.md#bpy.types.Strip "bpy.types.Strip")

<a id="bpy.types.Context.strips"></a>

#### bpy.types.Context.strips

**Type:**

Sequence[[`Strip`](bpy.types.Strip.md#bpy.types.Strip "bpy.types.Strip")]

<a id="bpy.types.Context.selected_strips"></a>

#### bpy.types.Context.selected_strips

**Type:**

Sequence[[`Strip`](bpy.types.Strip.md#bpy.types.Strip "bpy.types.Strip")]

<a id="bpy.types.Context.selected_editable_strips"></a>

#### bpy.types.Context.selected_editable_strips

**Type:**

Sequence[[`Strip`](bpy.types.Strip.md#bpy.types.Strip "bpy.types.Strip")]

<a id="bpy.types.Context.sequencer_scene"></a>

#### bpy.types.Context.sequencer_scene

**Type:**

[`Scene`](bpy.types.Scene.md#bpy.types.Scene "bpy.types.Scene")

Sequencer Context

#### edit_mask

**Type:**

[`Mask`](bpy.types.Mask.md#bpy.types.Mask "bpy.types.Mask")

#### tool_settings

**Type:**

[`ToolSettings`](bpy.types.ToolSettings.md#bpy.types.ToolSettings "bpy.types.ToolSettings")

Text Context

<a id="bpy.types.Context.edit_text"></a>

#### bpy.types.Context.edit_text

**Type:**

[`Text`](bpy.types.Text.md#bpy.types.Text "bpy.types.Text")

View3D Context

#### active_object

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object")

#### selected_ids

**Type:**

Sequence[[`ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID")]

Methods

<a id="bpy.types.Context.evaluated_depsgraph_get"></a>

#### bpy.types.Context.evaluated_depsgraph_get()

Get the dependency graph for the current scene and view layer, to access to data-blocks with animation and modifiers applied. If any data-blocks have been edited, the dependency graph will be updated. This invalidates all references to evaluated data-blocks from the dependency graph.

**Returns:**

Evaluated dependency graph

**Return type:**

[`Depsgraph`](bpy.types.Depsgraph.md#bpy.types.Depsgraph "bpy.types.Depsgraph")

<a id="bpy.types.Context.copy"></a>

#### bpy.types.Context.copy()

Get context members as a dictionary.

**Return type:**

dict[str, Any]

<a id="bpy.types.Context.path_resolve"></a>

#### bpy.types.Context.path_resolve(path, coerce=True)

Returns the property from the path, raise an exception when not found.

**Parameters:**

- **path** (str) – patch which this property resolves.
- **coerce** (bool) – optional argument, when True, the property will be converted into its Python representation.

**Returns:**

Property value or property object.

**Return type:**

Any | [`bpy_prop`](bpy.types.bpy_prop.md#bpy.types.bpy_prop "bpy.types.bpy_prop")

<a id="bpy.types.Context.bl_rna_get_subclass"></a>

#### classmethod bpy.types.Context.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.Context.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.Context.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="bpy.types.Context.temp_override"></a>

#### bpy.types.Context.temp_override(*, window=None, screen=None, area=None, region=None, **keywords)

Context manager to temporarily override members in the context.

**Parameters:**

- **window** ([`bpy.types.Window`](bpy.types.Window.md#bpy.types.Window "bpy.types.Window") | None) – Window override or None.
- **screen** ([`bpy.types.Screen`](bpy.types.Screen.md#bpy.types.Screen "bpy.types.Screen") | None) –

  Screen override or None.

  > **Note:**
  >
  > Switching to or away from full-screen areas & temporary screens isn’t supported. Passing in these screens will raise an exception, actions that leave the context such screens won’t restore the prior screen.

  > **Note:**
  >
  > Changing the screen has wider implications than other arguments as it will also change the works-space and potentially the scene (when pinned).
- **area** ([`bpy.types.Area`](bpy.types.Area.md#bpy.types.Area "bpy.types.Area") | None) – Area override or None.
- **region** ([`bpy.types.Region`](bpy.types.Region.md#bpy.types.Region "bpy.types.Region") | None) – Region override or None.
- **keywords** – Additional keywords override context members.

**Returns:**

The context manager.

**Return type:**

[`bpy.types.ContextTempOverride`](bpy.types.ContextTempOverride.md#bpy.types.ContextTempOverride "bpy.types.ContextTempOverride")

Overriding the context can be used to temporarily activate another `window` / `area` & `region`,
as well as other members such as the `active_object` or `bone`.

Notes:

- When overriding window, area and regions: the arguments must be consistent,
  so any region argument that’s passed in must be contained by the current area or the area passed in.
  The same goes for the area needing to be contained in the current window.
- Temporary context overrides may be nested, when this is done, members will be added to the existing overrides.
- Context members are restored outside the scope of the context-manager.
  The only exception to this is when the data is no longer available.

  In the event windowing data was removed (for example), the state of the context is left as-is.
  While this isn’t likely to happen, explicit window operation such as closing windows or loading a new file
  remove the windowing data that was set before the temporary context was created.

Overriding the context can be useful to set the context after loading files
(which would otherwise be None). For example:

```python
import bpy
from bpy import context

# Reload the current file and select all.
bpy.ops.wm.open_mainfile(filepath=bpy.data.filepath)
window = context.window_manager.windows[0]
with context.temp_override(window=window):
    bpy.ops.mesh.primitive_uv_sphere_add()
    # The context override is needed so it's possible to set edit-mode.
    bpy.ops.object.mode_set(mode='EDIT')
```

This example shows how it’s possible to add an object to the scene in another window.

```python
import bpy
from bpy import context

win_active = context.window
win_other = None
for win_iter in context.window_manager.windows:
    if win_iter != win_active:
        win_other = win_iter
        break

# Add cube in the other window.
with context.temp_override(window=win_other):
    bpy.ops.mesh.primitive_cube_add()
```

**Logging Context Member Access**

Context members can be logged by calling `logging_set(True)` on the “with” target of a temporary override.
This will log the members that are being accessed during the operation and may
assist in debugging when it is unclear which members need to be overridden.

In the event an operator fails to execute because of a missing context member, logging may help
identify which member is required.

This example shows how to log which context members are being accessed.
Log statements are printed to your system’s console.

> **Important:**
>
> Not all operators rely on Context Members and therefore will not be affected by
> [`bpy.types.Context.temp_override`](#bpy.types.Context.temp_override "bpy.types.Context.temp_override"), use logging to what members if any are accessed.

```python
import bpy
from bpy import context

my_objects = [context.scene.camera]

with context.temp_override(selected_objects=my_objects) as override:
    override.logging_set(
        True,  # Enable logging.
        hide_missing=True,  # Don't show failed attempts.
    )
    bpy.ops.object.delete()
```

<a id="inherited-properties"></a>

## Inherited Properties

bpy_struct.id_data

<a id="inherited-functions"></a>

## Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values

<a id="references"></a>

## References

|  |  |
| --- | --- |
| - [`AssetShelf.draw_context_menu`](bpy.types.AssetShelf.md#bpy.types.AssetShelf.draw_context_menu "bpy.types.AssetShelf.draw_context_menu") - [`AssetShelf.poll`](bpy.types.AssetShelf.md#bpy.types.AssetShelf.poll "bpy.types.AssetShelf.poll") - [`FileHandler.poll_drop`](bpy.types.FileHandler.md#bpy.types.FileHandler.poll_drop "bpy.types.FileHandler.poll_drop") - [`Gizmo.draw`](bpy.types.Gizmo.md#bpy.types.Gizmo.draw "bpy.types.Gizmo.draw") - [`Gizmo.draw_select`](bpy.types.Gizmo.md#bpy.types.Gizmo.draw_select "bpy.types.Gizmo.draw_select") - [`Gizmo.exit`](bpy.types.Gizmo.md#bpy.types.Gizmo.exit "bpy.types.Gizmo.exit") - [`Gizmo.invoke`](bpy.types.Gizmo.md#bpy.types.Gizmo.invoke "bpy.types.Gizmo.invoke") - [`Gizmo.modal`](bpy.types.Gizmo.md#bpy.types.Gizmo.modal "bpy.types.Gizmo.modal") - [`Gizmo.test_select`](bpy.types.Gizmo.md#bpy.types.Gizmo.test_select "bpy.types.Gizmo.test_select") - [`GizmoGroup.draw_prepare`](bpy.types.GizmoGroup.md#bpy.types.GizmoGroup.draw_prepare "bpy.types.GizmoGroup.draw_prepare") - [`GizmoGroup.invoke_prepare`](bpy.types.GizmoGroup.md#bpy.types.GizmoGroup.invoke_prepare "bpy.types.GizmoGroup.invoke_prepare") - [`GizmoGroup.poll`](bpy.types.GizmoGroup.md#bpy.types.GizmoGroup.poll "bpy.types.GizmoGroup.poll") - [`GizmoGroup.refresh`](bpy.types.GizmoGroup.md#bpy.types.GizmoGroup.refresh "bpy.types.GizmoGroup.refresh") - [`GizmoGroup.setup`](bpy.types.GizmoGroup.md#bpy.types.GizmoGroup.setup "bpy.types.GizmoGroup.setup") - [`Header.draw`](bpy.types.Header.md#bpy.types.Header.draw "bpy.types.Header.draw") - [`KeyingSetInfo.generate`](bpy.types.KeyingSetInfo.md#bpy.types.KeyingSetInfo.generate "bpy.types.KeyingSetInfo.generate") - [`KeyingSetInfo.iterator`](bpy.types.KeyingSetInfo.md#bpy.types.KeyingSetInfo.iterator "bpy.types.KeyingSetInfo.iterator") - [`KeyingSetInfo.poll`](bpy.types.KeyingSetInfo.md#bpy.types.KeyingSetInfo.poll "bpy.types.KeyingSetInfo.poll") - [`Macro.draw`](bpy.types.Macro.md#bpy.types.Macro.draw "bpy.types.Macro.draw") - [`Macro.poll`](bpy.types.Macro.md#bpy.types.Macro.poll "bpy.types.Macro.poll") - [`Menu.draw`](bpy.types.Menu.md#bpy.types.Menu.draw "bpy.types.Menu.draw") - [`Menu.poll`](bpy.types.Menu.md#bpy.types.Menu.poll "bpy.types.Menu.poll") - [`Node.draw_buttons`](bpy.types.Node.md#bpy.types.Node.draw_buttons "bpy.types.Node.draw_buttons") - [`Node.draw_buttons_ext`](bpy.types.Node.md#bpy.types.Node.draw_buttons_ext "bpy.types.Node.draw_buttons_ext") - [`Node.init`](bpy.types.Node.md#bpy.types.Node.init "bpy.types.Node.init") - [`Node.socket_value_update`](bpy.types.Node.md#bpy.types.Node.socket_value_update "bpy.types.Node.socket_value_update") - [`NodeInternal.draw_buttons`](bpy.types.NodeInternal.md#bpy.types.NodeInternal.draw_buttons "bpy.types.NodeInternal.draw_buttons") - [`NodeInternal.draw_buttons_ext`](bpy.types.NodeInternal.md#bpy.types.NodeInternal.draw_buttons_ext "bpy.types.NodeInternal.draw_buttons_ext") - [`NodeSocket.draw`](bpy.types.NodeSocket.md#bpy.types.NodeSocket.draw "bpy.types.NodeSocket.draw") - [`NodeSocket.draw_color`](bpy.types.NodeSocket.md#bpy.types.NodeSocket.draw_color "bpy.types.NodeSocket.draw_color") - [`NodeSocketStandard.draw`](bpy.types.NodeSocketStandard.md#bpy.types.NodeSocketStandard.draw "bpy.types.NodeSocketStandard.draw") - [`NodeSocketStandard.draw_color`](bpy.types.NodeSocketStandard.md#bpy.types.NodeSocketStandard.draw_color "bpy.types.NodeSocketStandard.draw_color") - [`NodeTree.get_from_context`](bpy.types.NodeTree.md#bpy.types.NodeTree.get_from_context "bpy.types.NodeTree.get_from_context") - [`NodeTree.interface_update`](bpy.types.NodeTree.md#bpy.types.NodeTree.interface_update "bpy.types.NodeTree.interface_update") - [`NodeTree.poll`](bpy.types.NodeTree.md#bpy.types.NodeTree.poll "bpy.types.NodeTree.poll") - [`NodeTreeInterfaceSocket.draw`](bpy.types.NodeTreeInterfaceSocket.md#bpy.types.NodeTreeInterfaceSocket.draw "bpy.types.NodeTreeInterfaceSocket.draw") - [`NodeTreeInterfaceSocketBool.draw`](bpy.types.NodeTreeInterfaceSocketBool.md#bpy.types.NodeTreeInterfaceSocketBool.draw "bpy.types.NodeTreeInterfaceSocketBool.draw") - [`NodeTreeInterfaceSocketBundle.draw`](bpy.types.NodeTreeInterfaceSocketBundle.md#bpy.types.NodeTreeInterfaceSocketBundle.draw "bpy.types.NodeTreeInterfaceSocketBundle.draw") - [`NodeTreeInterfaceSocketClosure.draw`](bpy.types.NodeTreeInterfaceSocketClosure.md#bpy.types.NodeTreeInterfaceSocketClosure.draw "bpy.types.NodeTreeInterfaceSocketClosure.draw") - [`NodeTreeInterfaceSocketCollection.draw`](bpy.types.NodeTreeInterfaceSocketCollection.md#bpy.types.NodeTreeInterfaceSocketCollection.draw "bpy.types.NodeTreeInterfaceSocketCollection.draw") - [`NodeTreeInterfaceSocketColor.draw`](bpy.types.NodeTreeInterfaceSocketColor.md#bpy.types.NodeTreeInterfaceSocketColor.draw "bpy.types.NodeTreeInterfaceSocketColor.draw") - [`NodeTreeInterfaceSocketFloat.draw`](bpy.types.NodeTreeInterfaceSocketFloat.md#bpy.types.NodeTreeInterfaceSocketFloat.draw "bpy.types.NodeTreeInterfaceSocketFloat.draw") - [`NodeTreeInterfaceSocketFloatAngle.draw`](bpy.types.NodeTreeInterfaceSocketFloatAngle.md#bpy.types.NodeTreeInterfaceSocketFloatAngle.draw "bpy.types.NodeTreeInterfaceSocketFloatAngle.draw") - [`NodeTreeInterfaceSocketFloatColorTemperature.draw`](bpy.types.NodeTreeInterfaceSocketFloatColorTemperature.md#bpy.types.NodeTreeInterfaceSocketFloatColorTemperature.draw "bpy.types.NodeTreeInterfaceSocketFloatColorTemperature.draw") - [`NodeTreeInterfaceSocketFloatDistance.draw`](bpy.types.NodeTreeInterfaceSocketFloatDistance.md#bpy.types.NodeTreeInterfaceSocketFloatDistance.draw "bpy.types.NodeTreeInterfaceSocketFloatDistance.draw") - [`NodeTreeInterfaceSocketFloatFactor.draw`](bpy.types.NodeTreeInterfaceSocketFloatFactor.md#bpy.types.NodeTreeInterfaceSocketFloatFactor.draw "bpy.types.NodeTreeInterfaceSocketFloatFactor.draw") - [`NodeTreeInterfaceSocketFloatFrequency.draw`](bpy.types.NodeTreeInterfaceSocketFloatFrequency.md#bpy.types.NodeTreeInterfaceSocketFloatFrequency.draw "bpy.types.NodeTreeInterfaceSocketFloatFrequency.draw") - [`NodeTreeInterfaceSocketFloatMass.draw`](bpy.types.NodeTreeInterfaceSocketFloatMass.md#bpy.types.NodeTreeInterfaceSocketFloatMass.draw "bpy.types.NodeTreeInterfaceSocketFloatMass.draw") - [`NodeTreeInterfaceSocketFloatPercentage.draw`](bpy.types.NodeTreeInterfaceSocketFloatPercentage.md#bpy.types.NodeTreeInterfaceSocketFloatPercentage.draw "bpy.types.NodeTreeInterfaceSocketFloatPercentage.draw") - [`NodeTreeInterfaceSocketFloatPixel.draw`](bpy.types.NodeTreeInterfaceSocketFloatPixel.md#bpy.types.NodeTreeInterfaceSocketFloatPixel.draw "bpy.types.NodeTreeInterfaceSocketFloatPixel.draw") - [`NodeTreeInterfaceSocketFloatTime.draw`](bpy.types.NodeTreeInterfaceSocketFloatTime.md#bpy.types.NodeTreeInterfaceSocketFloatTime.draw "bpy.types.NodeTreeInterfaceSocketFloatTime.draw") - [`NodeTreeInterfaceSocketFloatTimeAbsolute.draw`](bpy.types.NodeTreeInterfaceSocketFloatTimeAbsolute.md#bpy.types.NodeTreeInterfaceSocketFloatTimeAbsolute.draw "bpy.types.NodeTreeInterfaceSocketFloatTimeAbsolute.draw") - [`NodeTreeInterfaceSocketFloatUnsigned.draw`](bpy.types.NodeTreeInterfaceSocketFloatUnsigned.md#bpy.types.NodeTreeInterfaceSocketFloatUnsigned.draw "bpy.types.NodeTreeInterfaceSocketFloatUnsigned.draw") - [`NodeTreeInterfaceSocketFloatWavelength.draw`](bpy.types.NodeTreeInterfaceSocketFloatWavelength.md#bpy.types.NodeTreeInterfaceSocketFloatWavelength.draw "bpy.types.NodeTreeInterfaceSocketFloatWavelength.draw") - [`NodeTreeInterfaceSocketGeometry.draw`](bpy.types.NodeTreeInterfaceSocketGeometry.md#bpy.types.NodeTreeInterfaceSocketGeometry.draw "bpy.types.NodeTreeInterfaceSocketGeometry.draw") - [`NodeTreeInterfaceSocketImage.draw`](bpy.types.NodeTreeInterfaceSocketImage.md#bpy.types.NodeTreeInterfaceSocketImage.draw "bpy.types.NodeTreeInterfaceSocketImage.draw") - [`NodeTreeInterfaceSocketInt.draw`](bpy.types.NodeTreeInterfaceSocketInt.md#bpy.types.NodeTreeInterfaceSocketInt.draw "bpy.types.NodeTreeInterfaceSocketInt.draw") - [`NodeTreeInterfaceSocketIntFactor.draw`](bpy.types.NodeTreeInterfaceSocketIntFactor.md#bpy.types.NodeTreeInterfaceSocketIntFactor.draw "bpy.types.NodeTreeInterfaceSocketIntFactor.draw") - [`NodeTreeInterfaceSocketIntPercentage.draw`](bpy.types.NodeTreeInterfaceSocketIntPercentage.md#bpy.types.NodeTreeInterfaceSocketIntPercentage.draw "bpy.types.NodeTreeInterfaceSocketIntPercentage.draw") - [`NodeTreeInterfaceSocketIntPixel.draw`](bpy.types.NodeTreeInterfaceSocketIntPixel.md#bpy.types.NodeTreeInterfaceSocketIntPixel.draw "bpy.types.NodeTreeInterfaceSocketIntPixel.draw") - [`NodeTreeInterfaceSocketIntUnsigned.draw`](bpy.types.NodeTreeInterfaceSocketIntUnsigned.md#bpy.types.NodeTreeInterfaceSocketIntUnsigned.draw "bpy.types.NodeTreeInterfaceSocketIntUnsigned.draw") - [`NodeTreeInterfaceSocketIntVector2D.draw`](bpy.types.NodeTreeInterfaceSocketIntVector2D.md#bpy.types.NodeTreeInterfaceSocketIntVector2D.draw "bpy.types.NodeTreeInterfaceSocketIntVector2D.draw") - [`NodeTreeInterfaceSocketIntVector3D.draw`](bpy.types.NodeTreeInterfaceSocketIntVector3D.md#bpy.types.NodeTreeInterfaceSocketIntVector3D.draw "bpy.types.NodeTreeInterfaceSocketIntVector3D.draw") - [`NodeTreeInterfaceSocketIntVectorFactor2D.draw`](bpy.types.NodeTreeInterfaceSocketIntVectorFactor2D.md#bpy.types.NodeTreeInterfaceSocketIntVectorFactor2D.draw "bpy.types.NodeTreeInterfaceSocketIntVectorFactor2D.draw") - [`NodeTreeInterfaceSocketIntVectorFactor3D.draw`](bpy.types.NodeTreeInterfaceSocketIntVectorFactor3D.md#bpy.types.NodeTreeInterfaceSocketIntVectorFactor3D.draw "bpy.types.NodeTreeInterfaceSocketIntVectorFactor3D.draw") - [`NodeTreeInterfaceSocketIntVectorPercentage2D.draw`](bpy.types.NodeTreeInterfaceSocketIntVectorPercentage2D.md#bpy.types.NodeTreeInterfaceSocketIntVectorPercentage2D.draw "bpy.types.NodeTreeInterfaceSocketIntVectorPercentage2D.draw") - [`NodeTreeInterfaceSocketIntVectorPercentage3D.draw`](bpy.types.NodeTreeInterfaceSocketIntVectorPercentage3D.md#bpy.types.NodeTreeInterfaceSocketIntVectorPercentage3D.draw "bpy.types.NodeTreeInterfaceSocketIntVectorPercentage3D.draw") - [`NodeTreeInterfaceSocketIntVectorPixel2D.draw`](bpy.types.NodeTreeInterfaceSocketIntVectorPixel2D.md#bpy.types.NodeTreeInterfaceSocketIntVectorPixel2D.draw "bpy.types.NodeTreeInterfaceSocketIntVectorPixel2D.draw") - [`NodeTreeInterfaceSocketIntVectorPixel3D.draw`](bpy.types.NodeTreeInterfaceSocketIntVectorPixel3D.md#bpy.types.NodeTreeInterfaceSocketIntVectorPixel3D.draw "bpy.types.NodeTreeInterfaceSocketIntVectorPixel3D.draw") - [`NodeTreeInterfaceSocketIntVectorUnsigned2D.draw`](bpy.types.NodeTreeInterfaceSocketIntVectorUnsigned2D.md#bpy.types.NodeTreeInterfaceSocketIntVectorUnsigned2D.draw "bpy.types.NodeTreeInterfaceSocketIntVectorUnsigned2D.draw") - [`NodeTreeInterfaceSocketIntVectorUnsigned3D.draw`](bpy.types.NodeTreeInterfaceSocketIntVectorUnsigned3D.md#bpy.types.NodeTreeInterfaceSocketIntVectorUnsigned3D.draw "bpy.types.NodeTreeInterfaceSocketIntVectorUnsigned3D.draw") | - [`NodeTreeInterfaceSocketMaterial.draw`](bpy.types.NodeTreeInterfaceSocketMaterial.md#bpy.types.NodeTreeInterfaceSocketMaterial.draw "bpy.types.NodeTreeInterfaceSocketMaterial.draw") - [`NodeTreeInterfaceSocketMatrix.draw`](bpy.types.NodeTreeInterfaceSocketMatrix.md#bpy.types.NodeTreeInterfaceSocketMatrix.draw "bpy.types.NodeTreeInterfaceSocketMatrix.draw") - [`NodeTreeInterfaceSocketMenu.draw`](bpy.types.NodeTreeInterfaceSocketMenu.md#bpy.types.NodeTreeInterfaceSocketMenu.draw "bpy.types.NodeTreeInterfaceSocketMenu.draw") - [`NodeTreeInterfaceSocketObject.draw`](bpy.types.NodeTreeInterfaceSocketObject.md#bpy.types.NodeTreeInterfaceSocketObject.draw "bpy.types.NodeTreeInterfaceSocketObject.draw") - [`NodeTreeInterfaceSocketRotation.draw`](bpy.types.NodeTreeInterfaceSocketRotation.md#bpy.types.NodeTreeInterfaceSocketRotation.draw "bpy.types.NodeTreeInterfaceSocketRotation.draw") - [`NodeTreeInterfaceSocketShader.draw`](bpy.types.NodeTreeInterfaceSocketShader.md#bpy.types.NodeTreeInterfaceSocketShader.draw "bpy.types.NodeTreeInterfaceSocketShader.draw") - [`NodeTreeInterfaceSocketString.draw`](bpy.types.NodeTreeInterfaceSocketString.md#bpy.types.NodeTreeInterfaceSocketString.draw "bpy.types.NodeTreeInterfaceSocketString.draw") - [`NodeTreeInterfaceSocketStringFilePath.draw`](bpy.types.NodeTreeInterfaceSocketStringFilePath.md#bpy.types.NodeTreeInterfaceSocketStringFilePath.draw "bpy.types.NodeTreeInterfaceSocketStringFilePath.draw") - [`NodeTreeInterfaceSocketTexture.draw`](bpy.types.NodeTreeInterfaceSocketTexture.md#bpy.types.NodeTreeInterfaceSocketTexture.draw "bpy.types.NodeTreeInterfaceSocketTexture.draw") - [`NodeTreeInterfaceSocketVector.draw`](bpy.types.NodeTreeInterfaceSocketVector.md#bpy.types.NodeTreeInterfaceSocketVector.draw "bpy.types.NodeTreeInterfaceSocketVector.draw") - [`NodeTreeInterfaceSocketVector2D.draw`](bpy.types.NodeTreeInterfaceSocketVector2D.md#bpy.types.NodeTreeInterfaceSocketVector2D.draw "bpy.types.NodeTreeInterfaceSocketVector2D.draw") - [`NodeTreeInterfaceSocketVector4D.draw`](bpy.types.NodeTreeInterfaceSocketVector4D.md#bpy.types.NodeTreeInterfaceSocketVector4D.draw "bpy.types.NodeTreeInterfaceSocketVector4D.draw") - [`NodeTreeInterfaceSocketVectorAcceleration.draw`](bpy.types.NodeTreeInterfaceSocketVectorAcceleration.md#bpy.types.NodeTreeInterfaceSocketVectorAcceleration.draw "bpy.types.NodeTreeInterfaceSocketVectorAcceleration.draw") - [`NodeTreeInterfaceSocketVectorAcceleration2D.draw`](bpy.types.NodeTreeInterfaceSocketVectorAcceleration2D.md#bpy.types.NodeTreeInterfaceSocketVectorAcceleration2D.draw "bpy.types.NodeTreeInterfaceSocketVectorAcceleration2D.draw") - [`NodeTreeInterfaceSocketVectorAcceleration4D.draw`](bpy.types.NodeTreeInterfaceSocketVectorAcceleration4D.md#bpy.types.NodeTreeInterfaceSocketVectorAcceleration4D.draw "bpy.types.NodeTreeInterfaceSocketVectorAcceleration4D.draw") - [`NodeTreeInterfaceSocketVectorDirection.draw`](bpy.types.NodeTreeInterfaceSocketVectorDirection.md#bpy.types.NodeTreeInterfaceSocketVectorDirection.draw "bpy.types.NodeTreeInterfaceSocketVectorDirection.draw") - [`NodeTreeInterfaceSocketVectorDirection2D.draw`](bpy.types.NodeTreeInterfaceSocketVectorDirection2D.md#bpy.types.NodeTreeInterfaceSocketVectorDirection2D.draw "bpy.types.NodeTreeInterfaceSocketVectorDirection2D.draw") - [`NodeTreeInterfaceSocketVectorDirection4D.draw`](bpy.types.NodeTreeInterfaceSocketVectorDirection4D.md#bpy.types.NodeTreeInterfaceSocketVectorDirection4D.draw "bpy.types.NodeTreeInterfaceSocketVectorDirection4D.draw") - [`NodeTreeInterfaceSocketVectorEuler.draw`](bpy.types.NodeTreeInterfaceSocketVectorEuler.md#bpy.types.NodeTreeInterfaceSocketVectorEuler.draw "bpy.types.NodeTreeInterfaceSocketVectorEuler.draw") - [`NodeTreeInterfaceSocketVectorEuler2D.draw`](bpy.types.NodeTreeInterfaceSocketVectorEuler2D.md#bpy.types.NodeTreeInterfaceSocketVectorEuler2D.draw "bpy.types.NodeTreeInterfaceSocketVectorEuler2D.draw") - [`NodeTreeInterfaceSocketVectorEuler4D.draw`](bpy.types.NodeTreeInterfaceSocketVectorEuler4D.md#bpy.types.NodeTreeInterfaceSocketVectorEuler4D.draw "bpy.types.NodeTreeInterfaceSocketVectorEuler4D.draw") - [`NodeTreeInterfaceSocketVectorFactor.draw`](bpy.types.NodeTreeInterfaceSocketVectorFactor.md#bpy.types.NodeTreeInterfaceSocketVectorFactor.draw "bpy.types.NodeTreeInterfaceSocketVectorFactor.draw") - [`NodeTreeInterfaceSocketVectorFactor2D.draw`](bpy.types.NodeTreeInterfaceSocketVectorFactor2D.md#bpy.types.NodeTreeInterfaceSocketVectorFactor2D.draw "bpy.types.NodeTreeInterfaceSocketVectorFactor2D.draw") - [`NodeTreeInterfaceSocketVectorFactor4D.draw`](bpy.types.NodeTreeInterfaceSocketVectorFactor4D.md#bpy.types.NodeTreeInterfaceSocketVectorFactor4D.draw "bpy.types.NodeTreeInterfaceSocketVectorFactor4D.draw") - [`NodeTreeInterfaceSocketVectorPercentage.draw`](bpy.types.NodeTreeInterfaceSocketVectorPercentage.md#bpy.types.NodeTreeInterfaceSocketVectorPercentage.draw "bpy.types.NodeTreeInterfaceSocketVectorPercentage.draw") - [`NodeTreeInterfaceSocketVectorPercentage2D.draw`](bpy.types.NodeTreeInterfaceSocketVectorPercentage2D.md#bpy.types.NodeTreeInterfaceSocketVectorPercentage2D.draw "bpy.types.NodeTreeInterfaceSocketVectorPercentage2D.draw") - [`NodeTreeInterfaceSocketVectorPercentage4D.draw`](bpy.types.NodeTreeInterfaceSocketVectorPercentage4D.md#bpy.types.NodeTreeInterfaceSocketVectorPercentage4D.draw "bpy.types.NodeTreeInterfaceSocketVectorPercentage4D.draw") - [`NodeTreeInterfaceSocketVectorPixel.draw`](bpy.types.NodeTreeInterfaceSocketVectorPixel.md#bpy.types.NodeTreeInterfaceSocketVectorPixel.draw "bpy.types.NodeTreeInterfaceSocketVectorPixel.draw") - [`NodeTreeInterfaceSocketVectorPixel2D.draw`](bpy.types.NodeTreeInterfaceSocketVectorPixel2D.md#bpy.types.NodeTreeInterfaceSocketVectorPixel2D.draw "bpy.types.NodeTreeInterfaceSocketVectorPixel2D.draw") - [`NodeTreeInterfaceSocketVectorPixel4D.draw`](bpy.types.NodeTreeInterfaceSocketVectorPixel4D.md#bpy.types.NodeTreeInterfaceSocketVectorPixel4D.draw "bpy.types.NodeTreeInterfaceSocketVectorPixel4D.draw") - [`NodeTreeInterfaceSocketVectorTranslation.draw`](bpy.types.NodeTreeInterfaceSocketVectorTranslation.md#bpy.types.NodeTreeInterfaceSocketVectorTranslation.draw "bpy.types.NodeTreeInterfaceSocketVectorTranslation.draw") - [`NodeTreeInterfaceSocketVectorTranslation2D.draw`](bpy.types.NodeTreeInterfaceSocketVectorTranslation2D.md#bpy.types.NodeTreeInterfaceSocketVectorTranslation2D.draw "bpy.types.NodeTreeInterfaceSocketVectorTranslation2D.draw") - [`NodeTreeInterfaceSocketVectorTranslation4D.draw`](bpy.types.NodeTreeInterfaceSocketVectorTranslation4D.md#bpy.types.NodeTreeInterfaceSocketVectorTranslation4D.draw "bpy.types.NodeTreeInterfaceSocketVectorTranslation4D.draw") - [`NodeTreeInterfaceSocketVectorVelocity.draw`](bpy.types.NodeTreeInterfaceSocketVectorVelocity.md#bpy.types.NodeTreeInterfaceSocketVectorVelocity.draw "bpy.types.NodeTreeInterfaceSocketVectorVelocity.draw") - [`NodeTreeInterfaceSocketVectorVelocity2D.draw`](bpy.types.NodeTreeInterfaceSocketVectorVelocity2D.md#bpy.types.NodeTreeInterfaceSocketVectorVelocity2D.draw "bpy.types.NodeTreeInterfaceSocketVectorVelocity2D.draw") - [`NodeTreeInterfaceSocketVectorVelocity4D.draw`](bpy.types.NodeTreeInterfaceSocketVectorVelocity4D.md#bpy.types.NodeTreeInterfaceSocketVectorVelocity4D.draw "bpy.types.NodeTreeInterfaceSocketVectorVelocity4D.draw") - [`NodeTreeInterfaceSocketVectorXYZ.draw`](bpy.types.NodeTreeInterfaceSocketVectorXYZ.md#bpy.types.NodeTreeInterfaceSocketVectorXYZ.draw "bpy.types.NodeTreeInterfaceSocketVectorXYZ.draw") - [`NodeTreeInterfaceSocketVectorXYZ2D.draw`](bpy.types.NodeTreeInterfaceSocketVectorXYZ2D.md#bpy.types.NodeTreeInterfaceSocketVectorXYZ2D.draw "bpy.types.NodeTreeInterfaceSocketVectorXYZ2D.draw") - [`NodeTreeInterfaceSocketVectorXYZ4D.draw`](bpy.types.NodeTreeInterfaceSocketVectorXYZ4D.md#bpy.types.NodeTreeInterfaceSocketVectorXYZ4D.draw "bpy.types.NodeTreeInterfaceSocketVectorXYZ4D.draw") - [`Operator.cancel`](bpy.types.Operator.md#bpy.types.Operator.cancel "bpy.types.Operator.cancel") - [`Operator.check`](bpy.types.Operator.md#bpy.types.Operator.check "bpy.types.Operator.check") - [`Operator.description`](bpy.types.Operator.md#bpy.types.Operator.description "bpy.types.Operator.description") - [`Operator.draw`](bpy.types.Operator.md#bpy.types.Operator.draw "bpy.types.Operator.draw") - [`Operator.execute`](bpy.types.Operator.md#bpy.types.Operator.execute "bpy.types.Operator.execute") - [`Operator.invoke`](bpy.types.Operator.md#bpy.types.Operator.invoke "bpy.types.Operator.invoke") - [`Operator.modal`](bpy.types.Operator.md#bpy.types.Operator.modal "bpy.types.Operator.modal") - [`Operator.poll`](bpy.types.Operator.md#bpy.types.Operator.poll "bpy.types.Operator.poll") - [`Panel.draw`](bpy.types.Panel.md#bpy.types.Panel.draw "bpy.types.Panel.draw") - [`Panel.draw_header`](bpy.types.Panel.md#bpy.types.Panel.draw_header "bpy.types.Panel.draw_header") - [`Panel.draw_header_preset`](bpy.types.Panel.md#bpy.types.Panel.draw_header_preset "bpy.types.Panel.draw_header_preset") - [`Panel.poll`](bpy.types.Panel.md#bpy.types.Panel.poll "bpy.types.Panel.poll") - [`RenderEngine.draw`](bpy.types.RenderEngine.md#bpy.types.RenderEngine.draw "bpy.types.RenderEngine.draw") - [`RenderEngine.view_draw`](bpy.types.RenderEngine.md#bpy.types.RenderEngine.view_draw "bpy.types.RenderEngine.view_draw") - [`RenderEngine.view_update`](bpy.types.RenderEngine.md#bpy.types.RenderEngine.view_update "bpy.types.RenderEngine.view_update") - [`UIList.draw_filter`](bpy.types.UIList.md#bpy.types.UIList.draw_filter "bpy.types.UIList.draw_filter") - [`UIList.draw_item`](bpy.types.UIList.md#bpy.types.UIList.draw_item "bpy.types.UIList.draw_item") - [`UIList.filter_items`](bpy.types.UIList.md#bpy.types.UIList.filter_items "bpy.types.UIList.filter_items") - [`XrSessionState.action_binding_create`](bpy.types.XrSessionState.md#bpy.types.XrSessionState.action_binding_create "bpy.types.XrSessionState.action_binding_create") - [`XrSessionState.action_create`](bpy.types.XrSessionState.md#bpy.types.XrSessionState.action_create "bpy.types.XrSessionState.action_create") - [`XrSessionState.action_set_create`](bpy.types.XrSessionState.md#bpy.types.XrSessionState.action_set_create "bpy.types.XrSessionState.action_set_create") - [`XrSessionState.action_state_get`](bpy.types.XrSessionState.md#bpy.types.XrSessionState.action_state_get "bpy.types.XrSessionState.action_state_get") - [`XrSessionState.active_action_set_set`](bpy.types.XrSessionState.md#bpy.types.XrSessionState.active_action_set_set "bpy.types.XrSessionState.active_action_set_set") - [`XrSessionState.controller_aim_location_get`](bpy.types.XrSessionState.md#bpy.types.XrSessionState.controller_aim_location_get "bpy.types.XrSessionState.controller_aim_location_get") - [`XrSessionState.controller_aim_rotation_get`](bpy.types.XrSessionState.md#bpy.types.XrSessionState.controller_aim_rotation_get "bpy.types.XrSessionState.controller_aim_rotation_get") - [`XrSessionState.controller_grip_location_get`](bpy.types.XrSessionState.md#bpy.types.XrSessionState.controller_grip_location_get "bpy.types.XrSessionState.controller_grip_location_get") - [`XrSessionState.controller_grip_rotation_get`](bpy.types.XrSessionState.md#bpy.types.XrSessionState.controller_grip_rotation_get "bpy.types.XrSessionState.controller_grip_rotation_get") - [`XrSessionState.controller_pose_actions_set`](bpy.types.XrSessionState.md#bpy.types.XrSessionState.controller_pose_actions_set "bpy.types.XrSessionState.controller_pose_actions_set") - [`XrSessionState.haptic_action_apply`](bpy.types.XrSessionState.md#bpy.types.XrSessionState.haptic_action_apply "bpy.types.XrSessionState.haptic_action_apply") - [`XrSessionState.haptic_action_stop`](bpy.types.XrSessionState.md#bpy.types.XrSessionState.haptic_action_stop "bpy.types.XrSessionState.haptic_action_stop") - [`XrSessionState.is_running`](bpy.types.XrSessionState.md#bpy.types.XrSessionState.is_running "bpy.types.XrSessionState.is_running") - [`XrSessionState.reset_to_base_pose`](bpy.types.XrSessionState.md#bpy.types.XrSessionState.reset_to_base_pose "bpy.types.XrSessionState.reset_to_base_pose") |

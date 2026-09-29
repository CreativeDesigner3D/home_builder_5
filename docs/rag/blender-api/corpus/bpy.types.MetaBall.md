<!-- source: Blender Python API reference 5.2 / bpy.types.MetaBall.html -->

<a id="metaball-id"></a>

# MetaBall(ID)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID")

<a id="bpy.types.MetaBall"></a>

### class bpy.types.MetaBall(ID)

Metaball data-block to define blobby surfaces

<a id="bpy.types.MetaBall.animation_data"></a>

#### bpy.types.MetaBall.animation_data

Animation data for this data-block (readonly)

**Type:**

[`AnimData`](bpy.types.AnimData.md#bpy.types.AnimData "bpy.types.AnimData") | None

<a id="bpy.types.MetaBall.cycles"></a>

#### bpy.types.MetaBall.cycles

Cycles mesh settings (readonly)

**Type:**

`CyclesMeshSettings` | None

<a id="bpy.types.MetaBall.elements"></a>

#### bpy.types.MetaBall.elements

Metaball elements (default None, readonly)

**Type:**

[`MetaBallElements`](bpy.types.MetaBallElements.md#bpy.types.MetaBallElements "bpy.types.MetaBallElements")[[`MetaElement`](bpy.types.MetaElement.md#bpy.types.MetaElement "bpy.types.MetaElement")]

<a id="bpy.types.MetaBall.is_editmode"></a>

#### bpy.types.MetaBall.is_editmode

True when used in editmode (default False, readonly)

**Type:**

bool

<a id="bpy.types.MetaBall.materials"></a>

#### bpy.types.MetaBall.materials

(default None, readonly)

**Type:**

[`IDMaterials`](bpy.types.IDMaterials.md#bpy.types.IDMaterials "bpy.types.IDMaterials")[[`Material`](bpy.types.Material.md#bpy.types.Material "bpy.types.Material")]

<a id="bpy.types.MetaBall.render_resolution"></a>

#### bpy.types.MetaBall.render_resolution

Polygonization resolution in rendering (in [0.005, 10000], default 0.2)

**Type:**

float

<a id="bpy.types.MetaBall.resolution"></a>

#### bpy.types.MetaBall.resolution

Polygonization resolution in the 3D viewport (in [0.005, 10000], default 0.4)

**Type:**

float

<a id="bpy.types.MetaBall.texspace_location"></a>

#### bpy.types.MetaBall.texspace_location

Texture space location (array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.MetaBall.texspace_size"></a>

#### bpy.types.MetaBall.texspace_size

Texture space size (array of 3 items, in [-inf, inf], default (1.0, 1.0, 1.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.MetaBall.threshold"></a>

#### bpy.types.MetaBall.threshold

Influence of metaball elements (in [0, 5], default 0.6)

**Type:**

float

<a id="bpy.types.MetaBall.update_method"></a>

#### bpy.types.MetaBall.update_method

Metaball edit update behavior (default `'UPDATE_ALWAYS'`)

- `UPDATE_ALWAYS`
  Always – While editing, update metaball always.
- `HALFRES`
  Half – While editing, update metaball in half resolution.
- `FAST`
  Fast – While editing, update metaball without polygonization.
- `NEVER`
  Never – While editing, don’t update metaball at all.

**Type:**

Literal[‘UPDATE_ALWAYS’, ‘HALFRES’, ‘FAST’, ‘NEVER’]

<a id="bpy.types.MetaBall.use_auto_texspace"></a>

#### bpy.types.MetaBall.use_auto_texspace

Adjust active object’s texture space automatically when transforming object (default True)

**Type:**

bool

<a id="bpy.types.MetaBall.transform"></a>

#### bpy.types.MetaBall.transform(matrix)

Transform metaball elements by a matrix

**Parameters:**

**matrix** ([`mathutils.Matrix`](mathutils.md#mathutils.Matrix "mathutils.Matrix") | Sequence[Sequence[float]]) – Matrix (multi-dimensional array of 4 * 4 items, in [-inf, inf])

<a id="bpy.types.MetaBall.update_gpu_tag"></a>

#### bpy.types.MetaBall.update_gpu_tag()

update_gpu_tag

<a id="bpy.types.MetaBall.bl_rna_get_subclass"></a>

#### classmethod bpy.types.MetaBall.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.MetaBall.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.MetaBall.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="inherited-properties"></a>

## Inherited Properties

bpy_struct.id_data, ID.name, ID.name_full, ID.id_type, ID.session_uid, ID.is_evaluated, ID.original, ID.users, ID.use_fake_user, ID.use_extra_user, ID.is_embedded_data, ID.is_linked_packed, ID.is_missing, ID.is_runtime_data, ID.is_editable, ID.tag, ID.is_library_indirect, ID.library, ID.library_weak_reference, ID.asset_data, ID.override_library, ID.preview

<a id="inherited-functions"></a>

## Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values, ID.bl_system_properties_get, ID.rename, ID.evaluated_get, ID.copy, ID.asset_mark, ID.asset_clear, ID.asset_generate_preview, ID.override_create, ID.override_hierarchy_create, ID.user_clear, ID.user_remap, ID.make_local, ID.user_of_id, ID.animation_data_create, ID.animation_data_clear, ID.update_tag, ID.preview_ensure, ID.bl_rna_get_subclass, ID.bl_rna_get_subclass_py

<a id="references"></a>

## References

|  |  |
| --- | --- |
| - `bpy.context.meta_ball` - [`BlendData.metaballs`](bpy.types.BlendData.md#bpy.types.BlendData.metaballs "bpy.types.BlendData.metaballs") | - [`BlendDataMetaBalls.new`](bpy.types.BlendDataMetaBalls.md#bpy.types.BlendDataMetaBalls.new "bpy.types.BlendDataMetaBalls.new") - [`BlendDataMetaBalls.remove`](bpy.types.BlendDataMetaBalls.md#bpy.types.BlendDataMetaBalls.remove "bpy.types.BlendDataMetaBalls.remove") |

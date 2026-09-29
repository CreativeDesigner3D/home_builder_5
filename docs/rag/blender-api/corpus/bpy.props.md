<!-- source: Blender Python API reference 5.2 / bpy.props.html -->

<a id="module-bpy.props"></a>

# Property Definitions (bpy.props)

This module defines properties to extend Blender’s internal data. The result of these functions is used to assign properties to classes registered with Blender and can’t be used directly.

> **Note:**
>
> All parameters to these functions must be passed as keywords.

<a id="assigning-to-existing-classes"></a>

## Assigning to Existing Classes

Custom properties can be added to any subclass of an `ID`,
`Bone` and `PoseBone`.

These properties can be animated, accessed by the user interface and Python
like Blender’s existing properties.

> **Warning:**
>
> Access to these properties might happen in threaded context, on a per-data-block level.
> This has to be carefully considered when using accessors or update callbacks.
>
> Typically, these callbacks should not affect any other data that the one owned by their data-block.
> When accessing external non-Blender data, thread safety mechanisms should be considered.

```python
import bpy

# Assign a custom property to an existing type.
bpy.types.Material.custom_float = bpy.props.FloatProperty(name="Test Property")

# Test the property is there.
bpy.data.materials[0].custom_float = 5.0
```

<a id="operator-example"></a>

## Operator Example

A common use of custom properties is for Python based `Operator`
classes. Test this code by running it in the text editor, or by clicking the
button in the 3D Viewport’s Tools panel. The latter will show the properties
in the Redo panel and allow you to change them.

```python
import bpy

class OBJECT_OT_property_example(bpy.types.Operator):
    bl_idname = "object.property_example"
    bl_label = "Property Example"
    bl_options = {'REGISTER', 'UNDO'}

    my_float: bpy.props.FloatProperty(name="Some Floating Point")
    my_bool: bpy.props.BoolProperty(name="Toggle Option")
    my_string: bpy.props.StringProperty(name="String Value")

    def execute(self, context):
        self.report(
            {'INFO'}, "F: {:.2f}  B: {!s}  S: {!r}".format(
                self.my_float, self.my_bool, self.my_string,
            )
        )
        print('My float:', self.my_float)
        print('My bool:', self.my_bool)
        print('My string:', self.my_string)
        return {'FINISHED'}

class OBJECT_PT_property_example(bpy.types.Panel):
    bl_idname = "object_PT_property_example"
    bl_label = "Property Example"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Tool"

    def draw(self, context):
        # You can set the property values that should be used when the user
        # presses the button in the UI.
        props = self.layout.operator('object.property_example')
        props.my_bool = True
        props.my_string = "Shouldn't that be 47?"

        # You can set properties dynamically:
        if context.object:
            props.my_float = context.object.location.x
        else:
            props.my_float = 327

bpy.utils.register_class(OBJECT_OT_property_example)
bpy.utils.register_class(OBJECT_PT_property_example)

# Demo call. Be sure to also test in the 3D Viewport.
bpy.ops.object.property_example(
    my_float=47,
    my_bool=True,
    my_string="Shouldn't that be 327?",
)
```

<a id="propertygroup-example"></a>

## PropertyGroup Example

PropertyGroups can be used for collecting custom settings into one value
to avoid many individual settings mixed in together.

```python
import bpy

class MaterialSettings(bpy.types.PropertyGroup):
    my_int: bpy.props.IntProperty()
    my_float: bpy.props.FloatProperty()
    my_string: bpy.props.StringProperty()

bpy.utils.register_class(MaterialSettings)

bpy.types.Material.my_settings = bpy.props.PointerProperty(type=MaterialSettings)

# Test the new settings work.
material = bpy.data.materials[0]

material.my_settings.my_int = 5
material.my_settings.my_float = 3.0
material.my_settings.my_string = "Foo"
```

<a id="collection-example"></a>

## Collection Example

Custom properties can be added to any subclass of an `ID`,
`Bone` and `PoseBone`.

```python
import bpy

# Assign a collection.
class SceneSettingItem(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Test Property", default="Unknown")
    value: bpy.props.IntProperty(name="Test Property", default=22)

bpy.utils.register_class(SceneSettingItem)

bpy.types.Scene.my_settings = bpy.props.CollectionProperty(type=SceneSettingItem)

# Assume an armature object selected.
print("Adding 2 values!")

my_item = bpy.context.scene.my_settings.add()
my_item.name = "Spam"
my_item.value = 1000

my_item = bpy.context.scene.my_settings.add()
my_item.name = "Eggs"
my_item.value = 30

for my_item in bpy.context.scene.my_settings:
    print(my_item.name, my_item.value)
```

<a id="update-example"></a>

## Update Example

It can be useful to perform an action when a property is changed and can be
used to update other properties or synchronize with external data.

All properties define update functions except for CollectionProperty.

> **Warning:**
>
> Remember that these callbacks may be executed in threaded context.

> **Warning:**
>
> If the property belongs to an Operator, the update callback’s first
> parameter will be an OperatorProperties instance, rather than an instance
> of the operator itself. This means you can’t access other internal functions
> of the operator, only its other properties.

```python
import bpy

def update_func(self, context):
    print("my test function", self)

bpy.types.Scene.testprop = bpy.props.FloatProperty(update=update_func)

bpy.context.scene.testprop = 11.0

# >>> my test function <bpy_struct, Scene("Scene")>
```

<a id="getter-setter-example"></a>

## Getter/Setter Example

Accessor functions can be used for boolean, int, float, string and enum properties.

If `get` or `set` callbacks are defined, the property will not be stored in the ID properties
automatically. Instead, the `get` and `set` functions will be called when the property
is respectively read or written from the API, and are responsible to handle the data storage.

Note that:

- It is illegal to define a `set` callback without a matching `get` one.
- When a `get` callback is defined but no `set` one, the property is read-only.

`get_transform` and `set_transform` can be used when the returned value needs to be modified,
but the default internal storage is still used. They can only transform the value before it is
set or returned, but do not control how/where that data is stored.

> **Note:**
>
> It is possible to define both `get`/`set` and `get_transform`/`set_transform` callbacks
> for the same property. In practice however, this should rarely be needed, as most ‘transform’
> operation can also happen within a `get`/`set` callback.

> **Warning:**
>
> Remember that these callbacks may be executed in threaded context.

> **Warning:**
>
> Take care when accessing other properties in these callbacks, as it can easily trigger
> complex issues, such as infinite loops (if e.g. two properties try to also set the other
> property’s value in their own `set` callback), or unexpected side effects due to changes
> in data, caused e.g. by an `update` callback.

```python
import bpy

scene = bpy.context.scene

# Simple property reading/writing from 'custom' IDProperties.
# This is similar to what the RNA would do internally, albeit using it own separate,
# internal 'system' IDProperty storage, since Blender 5.0.
def get_float(self):
    return self.get("testprop", 0.0)

def set_float(self, value):
    self["testprop"] = value

bpy.types.Scene.test_float = bpy.props.FloatProperty(get=get_float, set=set_float)

# Testing the property:
print("test_float:", scene.test_float)
scene.test_float = 7.5
print("test_float:", scene.test_float)

# The above outputs:
# test_float: 0.0
# test_float: 7.5

# Read-only string property, returns the current date.
def get_date(self):
    import datetime
    return str(datetime.datetime.now())

bpy.types.Scene.test_date = bpy.props.StringProperty(get=get_date)

# Testing the property:
# scene.test_date = "blah"   # This would fail, property is read-only.
print("test_date:", scene.test_date)

# The above outputs something like:
# test_date: 2018-03-14 11:36:53.158653

# Boolean array.
# - Set function stores a single boolean value, returned as the second component.
# - Array getters must return a list or tuple.
# - Array size must match the property vector size exactly.
def get_array(self):
    return (True, self.get("somebool", True))

def set_array(self, values):
    self["somebool"] = values[0] and values[1]

bpy.types.Scene.test_array = bpy.props.BoolVectorProperty(size=2, get=get_array, set=set_array)

# Testing the property:
print("test_array:", tuple(scene.test_array))
scene.test_array = (True, False)
print("test_array:", tuple(scene.test_array))

# The above outputs:
# test_array: (True, True)
# test_array: (True, False)

# Boolean array, using 'transform' accessors.
# Note how the same result is achieved as with previous get/set example, but using default RNA storage.
# Transform accessors also have access to more information.
# Also note how the stored data _is_ a two-items array.
# - Set function stores a single boolean value, returned as the second component.
# - Array getters must return a list or tuple.
# - Array size must match the property vector size exactly.
def get_array_transform(self, curr_value, is_set):
    print("Stored data:", curr_value, "(is set:", is_set, ")")
    return (True, curr_value[1])

def set_array_transform(self, new_value, curr_value, is_set):
    print("New data:", new_value, "; Stored data:", curr_value, "(is set:", is_set, ")")
    return True, new_value[0] and new_value[1]

bpy.types.Scene.test_array_transform = bpy.props.BoolVectorProperty(
    size=2, get_transform=get_array_transform, set_transform=set_array_transform)

# Testing the property:
print("test_array_transform:", tuple(scene.test_array_transform))
scene.test_array_transform = (True, False)
print("test_array_transform:", tuple(scene.test_array_transform))

# The above outputs:
# Stored data: (False, False) (is set: False )
# test_array_transform: (True, False)
# New data: (True, False) ; Stored data: (False, False) (is set: False )
# Stored data: (True, False) (is set: True )
# test_array_transform: (True, False)

# Enum property.
# Note: the getter/setter callback must use integer identifiers!
test_items = [
    ("RED", "Red", "", 1),
    ("GREEN", "Green", "", 2),
    ("BLUE", "Blue", "", 3),
    ("YELLOW", "Yellow", "", 4),
]

def get_enum(self):
    import random
    return random.randint(1, 4)

def set_enum(self, value):
    print("setting value", value)

bpy.types.Scene.test_enum = bpy.props.EnumProperty(items=test_items, get=get_enum, set=set_enum)

# Testing the property:
print("test_enum:", scene.test_enum)
scene.test_enum = 'BLUE'
print("test_enum:", scene.test_enum)

# The above outputs something like:
# test_enum: YELLOW
# setting value 3
# test_enum: GREEN

# String, using 'transform' accessors to validate data before setting/returning it.
def get_string_transform(self, curr_value, is_set):
    import os
    is_valid_path = os.path.exists(curr_value)
    print("Stored data:", curr_value, "(is set:", is_set, ", is valid path:", is_valid_path, ")")
    return curr_value if is_valid_path else ""

def set_string_transform(self, new_value, curr_value, is_set):
    import os
    is_valid_path = os.path.exists(new_value)
    print("New data:", new_value, "(is_valid_path:", is_valid_path, ");",
          "Stored data:", curr_value, "(is set:", is_set, ")")
    return new_value if is_valid_path else curr_value

bpy.types.Scene.test_string_transform = bpy.props.StringProperty(
    subtype='DIR_PATH',
    default="an/invalid/path",
    get_transform=get_string_transform,
    set_transform=set_string_transform,
)

# Testing the property:
print("test_string_transform:", scene.test_string_transform)
scene.test_string_transform = "try\\to\\find\\me"
print("test_string_transform:", scene.test_string_transform)

# The above outputs something like:
# Stored data: an/invalid/path (is set: False , is valid path: False )
# test_string_transform:
# New data: try\to\find\me (is_valid_path: False ) ; Stored data: an/invalid/path (is set: False )
# Stored data: an/invalid/path (is set: True , is valid path: False )
# test_string_transform:
```

<a id="bpy.props.BoolProperty"></a>

### bpy.props.BoolProperty(*, name='', description='', translation_context='*', default=False, options={'ANIMATABLE'}, override=set(), tags=set(), subtype='NONE', update=None, get=None, set=None, get_transform=None, set_transform=None)

Returns a new boolean property definition.

**Parameters:**

- **name** (str) – Name used in the user interface.
- **description** (str) – Text used for the tooltip and api documentation.
- **translation_context** (str) – Text used as context to disambiguate translations.
- **default** (bool) – The default value for this property.
- **options** (set[str]) – Enumerator in [Property Flag Items](bpy_types_enum_items/property_flag_items.md#rna-enum-property-flag-items).
- **override** (set[str]) – Enumerator in [Property Override Flag Items](bpy_types_enum_items/property_override_flag_items.md#rna-enum-property-override-flag-items).
- **tags** (set[str]) – Enumerator of tags that are defined by parent class.
- **subtype** (str) – Enumerator in [Property Subtype Number Items](bpy_types_enum_items/property_subtype_number_items.md#rna-enum-property-subtype-number-items).
- **update** (Callable[[[`bpy.types.bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`bpy.types.Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context")], None] | None) – Function to be called when this value is modified,
  This function must take 2 values (self, context) and return None.
  Warning there are no safety checks to avoid infinite recursion.
- **get** (Callable[[[`bpy.types.bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")], bool] | None) –

  Function to be called when this value is ‘read’, and the default,
  system-defined storage is not used for this property.
  This function must take 1 value (self) and return the value of the property.

  > **Note:**
  >
  > Defining this callback without a matching `set` one will make the property read-only (even if `READ_ONLY` option is not set).
- **set** (Callable[[[`bpy.types.bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), bool], None] | None) –

  Function to be called when this value is ‘written’, and the default,
  system-defined storage is not used for this property.
  This function must take 2 values (self, value) and return None.

  > **Note:**
  >
  > Defining this callback without a matching `get` one is invalid.
- **get_transform** (Callable[[[`bpy.types.bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), bool, bool], bool] | None) –

  Function to be called when this value is ‘read’,
  if some additional processing must be performed on the stored value.
  This function must take three arguments (self, the stored value,
  and a boolean indicating if the property is currently set),
  and return the final, transformed value of the property.

  > **Note:**
  >
  > The callback is responsible to ensure that value limits of the property (min/max, length…) are respected. Otherwise a ValueError exception is raised.
- **set_transform** (Callable[[[`bpy.types.bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), bool, bool, bool], bool] | None) –

  Function to be called when this value is ‘written’,
  if some additional processing must be performed on the given value before storing it.
  This function must take four arguments (self, the given value to store,
  the currently stored value (‘raw’ value, without any `get_transform` applied to it),
  and a boolean indicating if the property is currently set),
  and return the final, transformed value of the property.

  > **Note:**
  >
  > The callback is responsible to ensure that value limits (min/max, length…) are respected. Otherwise a ValueError exception is raised.

**Returns:**

Opaque type used for registration.

**Return type:**

[`_PropertyDeferred`](#bpy.props._PropertyDeferred "bpy.props._PropertyDeferred")

<a id="bpy.props.BoolVectorProperty"></a>

### bpy.props.BoolVectorProperty(*, name='', description='', translation_context='*', default=(False, False, False), options={'ANIMATABLE'}, override=set(), tags=set(), subtype='NONE', size=3, update=None, get=None, set=None, get_transform=None, set_transform=None)

Returns a new vector boolean property definition.

**Parameters:**

- **name** (str) – Name used in the user interface.
- **description** (str) – Text used for the tooltip and api documentation.
- **translation_context** (str) – Text used as context to disambiguate translations.
- **default** (Sequence[bool]) – sequence of booleans the length of size.
- **options** (set[str]) – Enumerator in [Property Flag Items](bpy_types_enum_items/property_flag_items.md#rna-enum-property-flag-items).
- **override** (set[str]) – Enumerator in [Property Override Flag Items](bpy_types_enum_items/property_override_flag_items.md#rna-enum-property-override-flag-items).
- **tags** (set[str]) – Enumerator of tags that are defined by parent class.
- **subtype** (str) – Enumerator in [Property Subtype Number Array Items](bpy_types_enum_items/property_subtype_number_array_items.md#rna-enum-property-subtype-number-array-items).
- **size** (int | Sequence[int]) – Vector dimensions in [1, 32]. An int sequence can be used to define multi-dimension arrays.
- **update** (Callable[[[`bpy.types.bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`bpy.types.Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context")], None] | None) – Function to be called when this value is modified,
  This function must take 2 values (self, context) and return None.
  Warning there are no safety checks to avoid infinite recursion.
- **get** (Callable[[[`bpy.types.bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")], Sequence[bool]] | None) –

  Function to be called when this value is ‘read’, and the default,
  system-defined storage is not used for this property.
  This function must take 1 value (self) and return the value of the property.

  > **Note:**
  >
  > Defining this callback without a matching `set` one will make the property read-only (even if `READ_ONLY` option is not set).
- **set** (Callable[[[`bpy.types.bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), tuple[bool, …]], None] | None) –

  Function to be called when this value is ‘written’, and the default,
  system-defined storage is not used for this property.
  This function must take 2 values (self, value) and return None.

  > **Note:**
  >
  > Defining this callback without a matching `get` one is invalid.
- **get_transform** (Callable[[[`bpy.types.bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), Sequence[bool], bool], Sequence[bool]] | None) –

  Function to be called when this value is ‘read’,
  if some additional processing must be performed on the stored value.
  This function must take three arguments (self, the stored value,
  and a boolean indicating if the property is currently set),
  and return the final, transformed value of the property.

  > **Note:**
  >
  > The callback is responsible to ensure that value limits of the property (min/max, length…) are respected. Otherwise a ValueError exception is raised.
- **set_transform** (Callable[[[`bpy.types.bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), Sequence[bool], Sequence[bool], bool], Sequence[bool]] | None) –

  Function to be called when this value is ‘written’,
  if some additional processing must be performed on the given value before storing it.
  This function must take four arguments (self, the given value to store,
  the currently stored value (‘raw’ value, without any `get_transform` applied to it),
  and a boolean indicating if the property is currently set),
  and return the final, transformed value of the property.

  > **Note:**
  >
  > The callback is responsible to ensure that value limits (min/max, length…) are respected. Otherwise a ValueError exception is raised.

**Returns:**

Opaque type used for registration.

**Return type:**

[`_PropertyDeferred`](#bpy.props._PropertyDeferred "bpy.props._PropertyDeferred")

<a id="bpy.props.CollectionProperty"></a>

### bpy.props.CollectionProperty(type, *, name='', description='', translation_context='*', options={'ANIMATABLE'}, override=set(), tags=set())

Returns a new collection property definition.

**Parameters:**

- **type** (type[[`bpy.types.PropertyGroup`](bpy.types.PropertyGroup.md#bpy.types.PropertyGroup "bpy.types.PropertyGroup")]) – A subclass of a property group.
- **name** (str) – Name used in the user interface.
- **description** (str) – Text used for the tooltip and api documentation.
- **translation_context** (str) – Text used as context to disambiguate translations.
- **options** (set[str]) – Enumerator in [Property Flag Items](bpy_types_enum_items/property_flag_items.md#rna-enum-property-flag-items).
- **override** (set[str]) – Enumerator in [Property Override Flag Collection Items](bpy_types_enum_items/property_override_flag_collection_items.md#rna-enum-property-override-flag-collection-items).
- **tags** (set[str]) – Enumerator of tags that are defined by parent class.

**Returns:**

Opaque type used for registration.

**Return type:**

[`_PropertyDeferred`](#bpy.props._PropertyDeferred "bpy.props._PropertyDeferred")

<a id="bpy.props.EnumProperty"></a>

### bpy.props.EnumProperty(items, *, name='', description='', translation_context='*', default=None, options={'ANIMATABLE'}, override=set(), tags=set(), update=None, get=None, set=None, get_transform=None, set_transform=None)

Returns a new enumerator property definition.

**Parameters:**

- **items** (Iterable[tuple[str, str, str] | tuple[str, str, str, int] | tuple[str, str, str, str | int, int] | None] | Callable[[[`bpy.types.bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`bpy.types.Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context") | None], Iterable[tuple[str, str, str] | tuple[str, str, str, int] | tuple[str, str, str, str | int, int] | None]]) –

  sequence of enum items formatted:
  `[(identifier, name, description, icon, number), ...]`.

  The first three elements of the tuples are mandatory.

  **identifier:**

  The identifier is used for Python access.
  An empty identifier means that the item is a separator

  **name:**

  Name for the interface.

  **description:**

  Used for documentation and tooltips.

  **icon:**

  An icon string identifier or integer icon value
  (e.g. returned by [`bpy.types.UILayout.icon`](bpy.types.UILayout.md#bpy.types.UILayout.icon "bpy.types.UILayout.icon"))

  **number:**

  Unique value used as the identifier for this item (stored in file data).
  Use when the identifier may need to change. If the ENUM_FLAG option is used,
  the values are bit-masks and should be powers of two.

  When an item only contains 4 items they define `(identifier, name, description, number)`.

  Separators may be added using either None (nameless separator),
  or a regular item tuple with an empty identifier string, in which case the name,
  if non-empty, will be displayed in the UI above the separator line.
  For dynamic values a callback can be passed which returns a list in
  the same format as the static list.
  This function must take 2 arguments `(self, context)`, **context may be None**.

  > **Warning:**
  >
  > There is a known bug with using a callback,
  > Python must keep a reference to the strings returned by the callback or Blender
  > will misbehave or even crash.
- **name** (str) – Name used in the user interface.
- **description** (str) – Text used for the tooltip and api documentation.
- **translation_context** (str) – Text used as context to disambiguate translations.
- **default** (str | int | set[str] | None) – The default value for this enum, a string from the identifiers used in items, or integer matching an item number.
  If the ENUM_FLAG option is used this must be a set of such string identifiers instead.
  WARNING: Strings cannot be specified for dynamic enums
  (i.e. if a callback function is given as items parameter).
- **options** (set[str]) – Enumerator in [Property Flag Enum Items](bpy_types_enum_items/property_flag_enum_items.md#rna-enum-property-flag-enum-items).
- **override** (set[str]) – Enumerator in [Property Override Flag Items](bpy_types_enum_items/property_override_flag_items.md#rna-enum-property-override-flag-items).
- **tags** (set[str]) – Enumerator of tags that are defined by parent class.
- **update** (Callable[[[`bpy.types.bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`bpy.types.Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context")], None] | None) – Function to be called when this value is modified,
  This function must take 2 values (self, context) and return None.
  Warning there are no safety checks to avoid infinite recursion.
- **get** (Callable[[[`bpy.types.bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")], int] | None) –

  Function to be called when this value is ‘read’, and the default,
  system-defined storage is not used for this property.
  This function must take 1 value (self) and return the value of the property.

  > **Note:**
  >
  > Defining this callback without a matching `set` one will make the property read-only (even if `READ_ONLY` option is not set).
- **set** (Callable[[[`bpy.types.bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), int], None] | None) –

  Function to be called when this value is ‘written’, and the default,
  system-defined storage is not used for this property.
  This function must take 2 values (self, value) and return None.

  > **Note:**
  >
  > Defining this callback without a matching `get` one is invalid.
- **get_transform** (Callable[[[`bpy.types.bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), int, bool], int] | None) –

  Function to be called when this value is ‘read’,
  if some additional processing must be performed on the stored value.
  This function must take three arguments (self, the stored value,
  and a boolean indicating if the property is currently set),
  and return the final, transformed value of the property.

  > **Note:**
  >
  > The callback is responsible to ensure that value limits of the property (min/max, length…) are respected. Otherwise a ValueError exception is raised.
- **set_transform** (Callable[[[`bpy.types.bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), int, int, bool], int] | None) –

  Function to be called when this value is ‘written’,
  if some additional processing must be performed on the given value before storing it.
  This function must take four arguments (self, the given value to store,
  the currently stored value (‘raw’ value, without any `get_transform` applied to it),
  and a boolean indicating if the property is currently set),
  and return the final, transformed value of the property.

  > **Note:**
  >
  > The callback is responsible to ensure that value limits (min/max, length…) are respected. Otherwise a ValueError exception is raised.

**Returns:**

Opaque type used for registration.

**Return type:**

[`_PropertyDeferred`](#bpy.props._PropertyDeferred "bpy.props._PropertyDeferred")

<a id="bpy.props.FloatProperty"></a>

### bpy.props.FloatProperty(*, name='', description='', translation_context='*', default=0.0, min=-3.402823e+38, max=3.402823e+38, soft_min=-3.402823e+38, soft_max=3.402823e+38, step=3, precision=2, options={'ANIMATABLE'}, override=set(), tags=set(), subtype='NONE', unit='NONE', update=None, get=None, set=None, get_transform=None, set_transform=None)

Returns a new float (single precision) property definition.

**Parameters:**

- **name** (str) – Name used in the user interface.
- **description** (str) – Text used for the tooltip and api documentation.
- **translation_context** (str) – Text used as context to disambiguate translations.
- **default** (float) – The default value for this property.
- **min** (float) – Hard minimum, trying to assign a value below will silently assign this minimum instead.
- **max** (float) – Hard maximum, trying to assign a value above will silently assign this maximum instead.
- **soft_min** (float) – Soft minimum (>= min), user won’t be able to drag the widget below this value in the UI.
- **soft_max** (float) – Soft maximum (<= max), user won’t be able to drag the widget above this value in the UI.
- **step** (float) – Step of increment/decrement in UI, in [1, 100], defaults to 3 (WARNING: actual value is /100).
- **precision** (int) – Maximum number of decimal digits to display, in [0, 6]. Fraction is automatically hidden for exact integer values of fields with unit ‘NONE’ or ‘TIME’ (frame count) and step divisible by 100.
- **options** (set[str]) – Enumerator in [Property Flag Items](bpy_types_enum_items/property_flag_items.md#rna-enum-property-flag-items).
- **override** (set[str]) – Enumerator in [Property Override Flag Items](bpy_types_enum_items/property_override_flag_items.md#rna-enum-property-override-flag-items).
- **tags** (set[str]) – Enumerator of tags that are defined by parent class.
- **subtype** (str) – Enumerator in [Property Subtype Number Items](bpy_types_enum_items/property_subtype_number_items.md#rna-enum-property-subtype-number-items).
- **unit** (str) – Enumerator in [Property Unit Items](bpy_types_enum_items/property_unit_items.md#rna-enum-property-unit-items).
- **update** (Callable[[[`bpy.types.bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`bpy.types.Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context")], None] | None) – Function to be called when this value is modified,
  This function must take 2 values (self, context) and return None.
  Warning there are no safety checks to avoid infinite recursion.
- **get** (Callable[[[`bpy.types.bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")], float] | None) –

  Function to be called when this value is ‘read’, and the default,
  system-defined storage is not used for this property.
  This function must take 1 value (self) and return the value of the property.

  > **Note:**
  >
  > Defining this callback without a matching `set` one will make the property read-only (even if `READ_ONLY` option is not set).
- **set** (Callable[[[`bpy.types.bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), float], None] | None) –

  Function to be called when this value is ‘written’, and the default,
  system-defined storage is not used for this property.
  This function must take 2 values (self, value) and return None.

  > **Note:**
  >
  > Defining this callback without a matching `get` one is invalid.
- **get_transform** (Callable[[[`bpy.types.bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), float, bool], float] | None) –

  Function to be called when this value is ‘read’,
  if some additional processing must be performed on the stored value.
  This function must take three arguments (self, the stored value,
  and a boolean indicating if the property is currently set),
  and return the final, transformed value of the property.

  > **Note:**
  >
  > The callback is responsible to ensure that value limits of the property (min/max, length…) are respected. Otherwise a ValueError exception is raised.
- **set_transform** (Callable[[[`bpy.types.bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), float, float, bool], float] | None) –

  Function to be called when this value is ‘written’,
  if some additional processing must be performed on the given value before storing it.
  This function must take four arguments (self, the given value to store,
  the currently stored value (‘raw’ value, without any `get_transform` applied to it),
  and a boolean indicating if the property is currently set),
  and return the final, transformed value of the property.

  > **Note:**
  >
  > The callback is responsible to ensure that value limits (min/max, length…) are respected. Otherwise a ValueError exception is raised.

**Returns:**

Opaque type used for registration.

**Return type:**

[`_PropertyDeferred`](#bpy.props._PropertyDeferred "bpy.props._PropertyDeferred")

<a id="bpy.props.FloatVectorProperty"></a>

### bpy.props.FloatVectorProperty(*, name='', description='', translation_context='*', default=(0.0, 0.0, 0.0), min=-sys.float_info.max, max=sys.float_info.max, soft_min=-sys.float_info.max, soft_max=sys.float_info.max, step=3, precision=2, options={'ANIMATABLE'}, override=set(), tags=set(), subtype='NONE', unit='NONE', size=3, update=None, get=None, set=None, get_transform=None, set_transform=None)

Returns a new vector float property definition.

**Parameters:**

- **name** (str) – Name used in the user interface.
- **description** (str) – Text used for the tooltip and api documentation.
- **translation_context** (str) – Text used as context to disambiguate translations.
- **default** (Sequence[float]) – Sequence of floats the length of size.
- **min** (float) – Hard minimum, trying to assign a value below will silently assign this minimum instead.
- **max** (float) – Hard maximum, trying to assign a value above will silently assign this maximum instead.
- **soft_min** (float) – Soft minimum (>= min), user won’t be able to drag the widget below this value in the UI.
- **soft_max** (float) – Soft maximum (<= max), user won’t be able to drag the widget above this value in the UI.
- **step** (float) – Step of increment/decrement in UI, in [1, 100], defaults to 3 (WARNING: actual value is /100).
- **precision** (int) – Maximum number of decimal digits to display, in [0, 6]. Fraction is automatically hidden for exact integer values of fields with unit ‘NONE’ or ‘TIME’ (frame count) and step divisible by 100.
- **options** (set[str]) – Enumerator in [Property Flag Items](bpy_types_enum_items/property_flag_items.md#rna-enum-property-flag-items).
- **override** (set[str]) – Enumerator in [Property Override Flag Items](bpy_types_enum_items/property_override_flag_items.md#rna-enum-property-override-flag-items).
- **tags** (set[str]) – Enumerator of tags that are defined by parent class.
- **subtype** (str) – Enumerator in [Property Subtype Number Array Items](bpy_types_enum_items/property_subtype_number_array_items.md#rna-enum-property-subtype-number-array-items).
- **unit** (str) – Enumerator in [Property Unit Items](bpy_types_enum_items/property_unit_items.md#rna-enum-property-unit-items).
- **size** (int | Sequence[int]) – Vector dimensions in [1, 32]. An int sequence can be used to define multi-dimension arrays.
- **update** (Callable[[[`bpy.types.bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`bpy.types.Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context")], None] | None) – Function to be called when this value is modified,
  This function must take 2 values (self, context) and return None.
  Warning there are no safety checks to avoid infinite recursion.
- **get** (Callable[[[`bpy.types.bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")], Sequence[float]] | None) –

  Function to be called when this value is ‘read’, and the default,
  system-defined storage is not used for this property.
  This function must take 1 value (self) and return the value of the property.

  > **Note:**
  >
  > Defining this callback without a matching `set` one will make the property read-only (even if `READ_ONLY` option is not set).
- **set** (Callable[[[`bpy.types.bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), tuple[float, …]], None] | None) –

  Function to be called when this value is ‘written’, and the default,
  system-defined storage is not used for this property.
  This function must take 2 values (self, value) and return None.

  > **Note:**
  >
  > Defining this callback without a matching `get` one is invalid.
- **get_transform** (Callable[[[`bpy.types.bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), Sequence[float], bool], Sequence[float]] | None) –

  Function to be called when this value is ‘read’,
  if some additional processing must be performed on the stored value.
  This function must take three arguments (self, the stored value,
  and a boolean indicating if the property is currently set),
  and return the final, transformed value of the property.

  > **Note:**
  >
  > The callback is responsible to ensure that value limits of the property (min/max, length…) are respected. Otherwise a ValueError exception is raised.
- **set_transform** (Callable[[[`bpy.types.bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), Sequence[float], Sequence[float], bool], Sequence[float]] | None) –

  Function to be called when this value is ‘written’,
  if some additional processing must be performed on the given value before storing it.
  This function must take four arguments (self, the given value to store,
  the currently stored value (‘raw’ value, without any `get_transform` applied to it),
  and a boolean indicating if the property is currently set),
  and return the final, transformed value of the property.

  > **Note:**
  >
  > The callback is responsible to ensure that value limits (min/max, length…) are respected. Otherwise a ValueError exception is raised.

**Returns:**

Opaque type used for registration.

**Return type:**

[`_PropertyDeferred`](#bpy.props._PropertyDeferred "bpy.props._PropertyDeferred")

<a id="bpy.props.IntProperty"></a>

### bpy.props.IntProperty(*, name='', description='', translation_context='*', default=0, min=-2**31, max=2**31 - 1, soft_min=-2**31, soft_max=2**31 - 1, step=1, options={'ANIMATABLE'}, override=set(), tags=set(), subtype='NONE', update=None, get=None, set=None, get_transform=None, set_transform=None)

Returns a new int property definition.

**Parameters:**

- **name** (str) – Name used in the user interface.
- **description** (str) – Text used for the tooltip and api documentation.
- **translation_context** (str) – Text used as context to disambiguate translations.
- **default** (int) – The default value for this property.
- **min** (int) – Hard minimum, trying to assign a value below will silently assign this minimum instead.
- **max** (int) – Hard maximum, trying to assign a value above will silently assign this maximum instead.
- **soft_min** (int) – Soft minimum (>= min), user won’t be able to drag the widget below this value in the UI.
- **soft_max** (int) – Soft maximum (<= max), user won’t be able to drag the widget above this value in the UI.
- **step** (int) – Step of increment/decrement in UI, in [1, 100], defaults to 1 (WARNING: unused currently!).
- **options** (set[str]) – Enumerator in [Property Flag Items](bpy_types_enum_items/property_flag_items.md#rna-enum-property-flag-items).
- **override** (set[str]) – Enumerator in [Property Override Flag Items](bpy_types_enum_items/property_override_flag_items.md#rna-enum-property-override-flag-items).
- **tags** (set[str]) – Enumerator of tags that are defined by parent class.
- **subtype** (str) – Enumerator in [Property Subtype Number Items](bpy_types_enum_items/property_subtype_number_items.md#rna-enum-property-subtype-number-items).
- **update** (Callable[[[`bpy.types.bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`bpy.types.Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context")], None] | None) – Function to be called when this value is modified,
  This function must take 2 values (self, context) and return None.
  Warning there are no safety checks to avoid infinite recursion.
- **get** (Callable[[[`bpy.types.bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")], int] | None) –

  Function to be called when this value is ‘read’, and the default,
  system-defined storage is not used for this property.
  This function must take 1 value (self) and return the value of the property.

  > **Note:**
  >
  > Defining this callback without a matching `set` one will make the property read-only (even if `READ_ONLY` option is not set).
- **set** (Callable[[[`bpy.types.bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), int], None] | None) –

  Function to be called when this value is ‘written’, and the default,
  system-defined storage is not used for this property.
  This function must take 2 values (self, value) and return None.

  > **Note:**
  >
  > Defining this callback without a matching `get` one is invalid.
- **get_transform** (Callable[[[`bpy.types.bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), int, bool], int] | None) –

  Function to be called when this value is ‘read’,
  if some additional processing must be performed on the stored value.
  This function must take three arguments (self, the stored value,
  and a boolean indicating if the property is currently set),
  and return the final, transformed value of the property.

  > **Note:**
  >
  > The callback is responsible to ensure that value limits of the property (min/max, length…) are respected. Otherwise a ValueError exception is raised.
- **set_transform** (Callable[[[`bpy.types.bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), int, int, bool], int] | None) –

  Function to be called when this value is ‘written’,
  if some additional processing must be performed on the given value before storing it.
  This function must take four arguments (self, the given value to store,
  the currently stored value (‘raw’ value, without any `get_transform` applied to it),
  and a boolean indicating if the property is currently set),
  and return the final, transformed value of the property.

  > **Note:**
  >
  > The callback is responsible to ensure that value limits (min/max, length…) are respected. Otherwise a ValueError exception is raised.

**Returns:**

Opaque type used for registration.

**Return type:**

[`_PropertyDeferred`](#bpy.props._PropertyDeferred "bpy.props._PropertyDeferred")

<a id="bpy.props.IntVectorProperty"></a>

### bpy.props.IntVectorProperty(*, name='', description='', translation_context='*', default=(0, 0, 0), min=-2**31, max=2**31 - 1, soft_min=-2**31, soft_max=2**31 - 1, step=1, options={'ANIMATABLE'}, override=set(), tags=set(), subtype='NONE', size=3, update=None, get=None, set=None, get_transform=None, set_transform=None)

Returns a new vector int property definition.

**Parameters:**

- **name** (str) – Name used in the user interface.
- **description** (str) – Text used for the tooltip and api documentation.
- **translation_context** (str) – Text used as context to disambiguate translations.
- **default** (Sequence[int]) – sequence of ints the length of size.
- **min** (int) – Hard minimum, trying to assign a value below will silently assign this minimum instead.
- **max** (int) – Hard maximum, trying to assign a value above will silently assign this maximum instead.
- **soft_min** (int) – Soft minimum (>= min), user won’t be able to drag the widget below this value in the UI.
- **soft_max** (int) – Soft maximum (<= max), user won’t be able to drag the widget above this value in the UI.
- **step** (int) – Step of increment/decrement in UI, in [1, 100], defaults to 1 (WARNING: unused currently!).
- **options** (set[str]) – Enumerator in [Property Flag Items](bpy_types_enum_items/property_flag_items.md#rna-enum-property-flag-items).
- **override** (set[str]) – Enumerator in [Property Override Flag Items](bpy_types_enum_items/property_override_flag_items.md#rna-enum-property-override-flag-items).
- **tags** (set[str]) – Enumerator of tags that are defined by parent class.
- **subtype** (str) – Enumerator in [Property Subtype Number Array Items](bpy_types_enum_items/property_subtype_number_array_items.md#rna-enum-property-subtype-number-array-items).
- **size** (int | Sequence[int]) – Vector dimensions in [1, 32]. An int sequence can be used to define multi-dimension arrays.
- **update** (Callable[[[`bpy.types.bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`bpy.types.Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context")], None] | None) – Function to be called when this value is modified,
  This function must take 2 values (self, context) and return None.
  Warning there are no safety checks to avoid infinite recursion.
- **get** (Callable[[[`bpy.types.bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")], Sequence[int]] | None) –

  Function to be called when this value is ‘read’, and the default,
  system-defined storage is not used for this property.
  This function must take 1 value (self) and return the value of the property.

  > **Note:**
  >
  > Defining this callback without a matching `set` one will make the property read-only (even if `READ_ONLY` option is not set).
- **set** (Callable[[[`bpy.types.bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), tuple[int, …]], None] | None) –

  Function to be called when this value is ‘written’, and the default,
  system-defined storage is not used for this property.
  This function must take 2 values (self, value) and return None.

  > **Note:**
  >
  > Defining this callback without a matching `get` one is invalid.
- **get_transform** (Callable[[[`bpy.types.bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), Sequence[int], bool], Sequence[int]] | None) –

  Function to be called when this value is ‘read’,
  if some additional processing must be performed on the stored value.
  This function must take three arguments (self, the stored value,
  and a boolean indicating if the property is currently set),
  and return the final, transformed value of the property.

  > **Note:**
  >
  > The callback is responsible to ensure that value limits of the property (min/max, length…) are respected. Otherwise a ValueError exception is raised.
- **set_transform** (Callable[[[`bpy.types.bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), Sequence[int], Sequence[int], bool], Sequence[int]] | None) –

  Function to be called when this value is ‘written’,
  if some additional processing must be performed on the given value before storing it.
  This function must take four arguments (self, the given value to store,
  the currently stored value (‘raw’ value, without any `get_transform` applied to it),
  and a boolean indicating if the property is currently set),
  and return the final, transformed value of the property.

  > **Note:**
  >
  > The callback is responsible to ensure that value limits (min/max, length…) are respected. Otherwise a ValueError exception is raised.

**Returns:**

Opaque type used for registration.

**Return type:**

[`_PropertyDeferred`](#bpy.props._PropertyDeferred "bpy.props._PropertyDeferred")

<a id="bpy.props.PointerProperty"></a>

### bpy.props.PointerProperty(type, *, name='', description='', translation_context='*', options={'ANIMATABLE'}, override=set(), tags=set(), poll=None, update=None)

Returns a new pointer property definition.

**Parameters:**

- **type** (type[[`bpy.types.PropertyGroup`](bpy.types.PropertyGroup.md#bpy.types.PropertyGroup "bpy.types.PropertyGroup") | [`bpy.types.ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID")]) – A subclass of PropertyGroup or ID.
- **name** (str) – Name used in the user interface.
- **description** (str) – Text used for the tooltip and api documentation.
- **translation_context** (str) – Text used as context to disambiguate translations.
- **options** (set[str]) – Enumerator in [Property Flag Items](bpy_types_enum_items/property_flag_items.md#rna-enum-property-flag-items).
- **override** (set[str]) – Enumerator in [Property Override Flag Items](bpy_types_enum_items/property_override_flag_items.md#rna-enum-property-override-flag-items).
- **tags** (set[str]) – Enumerator of tags that are defined by parent class.
- **poll** (Callable[[[`bpy.types.bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`bpy.types.ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID")], bool] | None) –

  Function that determines whether an item is valid for this property.
  The function must take 2 values (self, object) and return a boolean.

  > **Note:**
  >
  > The return value will be checked only when assigning an item from the UI, but it is still possible to assign an “invalid” item to the property directly.
- **update** (Callable[[[`bpy.types.bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`bpy.types.Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context")], None] | None) – Function to be called when this value is modified,
  This function must take 2 values (self, context) and return None.
  Warning there are no safety checks to avoid infinite recursion.

**Returns:**

Opaque type used for registration.

**Return type:**

[`_PropertyDeferred`](#bpy.props._PropertyDeferred "bpy.props._PropertyDeferred")

> **Note:**
>
> Pointer properties do not support storing references to embedded IDs (e.g. [`bpy.types.Scene.collection`](bpy.types.Scene.md#bpy.types.Scene.collection "bpy.types.Scene.collection"), [`bpy.types.Material.node_tree`](bpy.types.Material.md#bpy.types.Material.node_tree "bpy.types.Material.node_tree")).
> These should exclusively be referenced and accessed through their owner ID (e.g. the scene or material).

<a id="bpy.props.RemoveProperty"></a>

### bpy.props.RemoveProperty(cls, attr)

Removes a dynamically defined property.

**Parameters:**

- **cls** (type[[`bpy.types.bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")]) – The class containing the property (must be a positional argument).
- **attr** (str) – Property name (must be passed as a keyword).

> **Note:**
>
> Typically this function doesn’t need to be accessed directly.
> Instead use `del cls.attr`

<a id="bpy.props.StringProperty"></a>

### bpy.props.StringProperty(*, name='', description='', translation_context='*', default='', maxlen=0, options={'ANIMATABLE'}, override=set(), tags=set(), subtype='NONE', update=None, get=None, set=None, get_transform=None, set_transform=None, search=None, search_options={'SUGGESTION'})

Returns a new string property definition.

**Parameters:**

- **name** (str) – Name used in the user interface.
- **description** (str) – Text used for the tooltip and api documentation.
- **translation_context** (str) – Text used as context to disambiguate translations.
- **default** (str) – initializer string.
- **maxlen** (int) – maximum length of the string.
- **options** (set[str]) – Enumerator in [Property Flag Items](bpy_types_enum_items/property_flag_items.md#rna-enum-property-flag-items).
- **override** (set[str]) – Enumerator in [Property Override Flag Items](bpy_types_enum_items/property_override_flag_items.md#rna-enum-property-override-flag-items).
- **tags** (set[str]) – Enumerator of tags that are defined by parent class.
- **subtype** (str) – Enumerator in [Property Subtype String Items](bpy_types_enum_items/property_subtype_string_items.md#rna-enum-property-subtype-string-items).
- **update** (Callable[[[`bpy.types.bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`bpy.types.Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context")], None] | None) – Function to be called when this value is modified,
  This function must take 2 values (self, context) and return None.
  Warning there are no safety checks to avoid infinite recursion.
- **get** (Callable[[[`bpy.types.bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")], str] | None) –

  Function to be called when this value is ‘read’, and the default,
  system-defined storage is not used for this property.
  This function must take 1 value (self) and return the value of the property.

  > **Note:**
  >
  > Defining this callback without a matching `set` one will make the property read-only (even if `READ_ONLY` option is not set).
- **set** (Callable[[[`bpy.types.bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), str], None] | None) –

  Function to be called when this value is ‘written’, and the default,
  system-defined storage is not used for this property.
  This function must take 2 values (self, value) and return None.

  > **Note:**
  >
  > Defining this callback without a matching `get` one is invalid.
- **get_transform** (Callable[[[`bpy.types.bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), str, bool], str] | None) –

  Function to be called when this value is ‘read’,
  if some additional processing must be performed on the stored value.
  This function must take three arguments (self, the stored value,
  and a boolean indicating if the property is currently set),
  and return the final, transformed value of the property.

  > **Note:**
  >
  > The callback is responsible to ensure that value limits of the property (min/max, length…) are respected. Otherwise a ValueError exception is raised.
- **set_transform** (Callable[[[`bpy.types.bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), str, str, bool], str] | None) –

  Function to be called when this value is ‘written’,
  if some additional processing must be performed on the given value before storing it.
  This function must take four arguments (self, the given value to store,
  the currently stored value (‘raw’ value, without any `get_transform` applied to it),
  and a boolean indicating if the property is currently set),
  and return the final, transformed value of the property.

  > **Note:**
  >
  > The callback is responsible to ensure that value limits (min/max, length…) are respected. Otherwise a ValueError exception is raised.
- **search** (Callable[[[`bpy.types.bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`bpy.types.Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context"), str], Iterable[str | tuple[str, str]]] | None) –

  Function to be called to show candidates for this string (shown in the UI).
  This function must take 3 values (self, context, edit_text)
  and return a sequence, iterator or generator where each item must be:

  - A single string (representing a candidate to display).
  - A tuple-pair of strings, where the first is a candidate and the second
    is additional information about the candidate.
- **search_options** (set[str]) –

  Set of strings in:

  - ’SORT’ sorts the resulting items.
  - ’SUGGESTION’ lets the user enter values not found in search candidates.
    **WARNING** disabling this flag causes the search callback to run on redraw,
    so only disable this flag if it’s not likely to cause performance issues.

**Returns:**

Opaque type used for registration.

**Return type:**

[`_PropertyDeferred`](#bpy.props._PropertyDeferred "bpy.props._PropertyDeferred")

<a id="bpy.props._PropertyDeferred"></a>

### class bpy.props._PropertyDeferred

Intermediate storage for properties before registration.

> **Note:**
>
> This is not part of the stable API and may change between releases.

<a id="bpy.props._PropertyDeferred.function"></a>

#### bpy.props._PropertyDeferred.function

The property registration function (e.g. [`bpy.props.IntProperty()`](#bpy.props.IntProperty "bpy.props.IntProperty")).

**Type:**

Callable

<a id="bpy.props._PropertyDeferred.keywords"></a>

#### bpy.props._PropertyDeferred.keywords

The keyword arguments passed to the property registration function.

**Type:**

dict[str, Any]

Special Methods

<a id="bpy.props._PropertyDeferred.__repr__"></a>

#### bpy.props._PropertyDeferred.__repr__()

**Return type:**

str

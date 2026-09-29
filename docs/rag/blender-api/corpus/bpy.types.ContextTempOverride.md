<!-- source: Blender Python API reference 5.2 / bpy.types.ContextTempOverride.html -->

<a id="contexttempoverride"></a>

# ContextTempOverride

<a id="bpy.types.ContextTempOverride"></a>

### class bpy.types.ContextTempOverride

<a id="bpy.types.ContextTempOverride.logging_set"></a>

#### bpy.types.ContextTempOverride.logging_set(enable, *, hide_missing=False)

Set context member logging options for this temporary override.

**Parameters:**

- **enable** (bool) – Enable logging of context member access.
- **hide_missing** (bool) – When true, suppress logging access to members that
  are not available in the current context.

Special Methods

<a id="bpy.types.ContextTempOverride.__enter__"></a>

#### bpy.types.ContextTempOverride.__enter__()

**Return type:**

[`ContextTempOverride`](#bpy.types.ContextTempOverride "bpy.types.ContextTempOverride")

<a id="bpy.types.ContextTempOverride.__exit__"></a>

#### bpy.types.ContextTempOverride.__exit__(exc_type, exc_value, traceback)

**Parameters:**

- **exc_type** (type | None) – Exception type, or `None`.
- **exc_value** (BaseException | None) – Exception instance, or `None`.
- **traceback** (BaseException | None) – Traceback object, or `None`.

**Return type:**

bool

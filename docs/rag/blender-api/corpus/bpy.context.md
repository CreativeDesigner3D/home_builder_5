<!-- source: Blender Python API reference 5.2 / bpy.context.html -->

<a id="module-bpy.context"></a>

# Context Access (bpy.context)

The context members available depend on the area of Blender which is currently being accessed.

Note that all context values are read-only,
but may be modified through the data API or by running operators.

<a id="bpy.context.context"></a>

### bpy.context.context

Access to the current window-manager and data context.

**Type:**

[`bpy.types.Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context")

<!-- source: Blender Python API reference 5.2 / bpy.types.PreferencesInput.html -->

<a id="preferencesinput-bpy-struct"></a>

# PreferencesInput(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.PreferencesInput"></a>

### class bpy.types.PreferencesInput(bpy_struct)

Settings for input devices

<a id="bpy.types.PreferencesInput.drag_threshold"></a>

#### bpy.types.PreferencesInput.drag_threshold

Number of pixels to drag before a drag event is triggered for keyboard and other non mouse/tablet input (otherwise click events are detected) (in [1, 255], default 30)

**Type:**

int

<a id="bpy.types.PreferencesInput.drag_threshold_mouse"></a>

#### bpy.types.PreferencesInput.drag_threshold_mouse

Number of pixels to drag before a drag event is triggered for mouse/trackpad input (otherwise click events are detected) (in [1, 255], default 3)

**Type:**

int

<a id="bpy.types.PreferencesInput.drag_threshold_tablet"></a>

#### bpy.types.PreferencesInput.drag_threshold_tablet

Number of pixels to drag before a drag event is triggered for tablet input (otherwise click events are detected) (in [1, 255], default 10)

**Type:**

int

<a id="bpy.types.PreferencesInput.invert_mouse_zoom"></a>

#### bpy.types.PreferencesInput.invert_mouse_zoom

Invert the axis of mouse movement for zooming (default False)

**Type:**

bool

<a id="bpy.types.PreferencesInput.invert_zoom_wheel"></a>

#### bpy.types.PreferencesInput.invert_zoom_wheel

Swap the Mouse Wheel zoom direction (default False)

**Type:**

bool

<a id="bpy.types.PreferencesInput.mouse_double_click_time"></a>

#### bpy.types.PreferencesInput.mouse_double_click_time

Time/delay (in ms) for a double click (in [1, 1000], default 350)

**Type:**

int

<a id="bpy.types.PreferencesInput.mouse_emulate_3_button_modifier"></a>

#### bpy.types.PreferencesInput.mouse_emulate_3_button_modifier

Hold this modifier to emulate the middle mouse button (default `'ALT'`)

**Type:**

Literal[‘ALT’, ‘OSKEY’]

<a id="bpy.types.PreferencesInput.move_threshold"></a>

#### bpy.types.PreferencesInput.move_threshold

Number of pixels to before the cursor is considered to have moved (used for cycling selected items on successive clicks) (in [0, 255], default 2)

**Type:**

int

<a id="bpy.types.PreferencesInput.navigation_mode"></a>

#### bpy.types.PreferencesInput.navigation_mode

Which method to use for viewport navigation (default `'WALK'`)

**Type:**

Literal[[Navigation Mode Items](bpy_types_enum_items/navigation_mode_items.md#rna-enum-navigation-mode-items)]

<a id="bpy.types.PreferencesInput.ndof_deadzone"></a>

#### bpy.types.PreferencesInput.ndof_deadzone

Threshold of initial movement needed from the device’s rest position (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.PreferencesInput.ndof_fly_helicopter"></a>

#### bpy.types.PreferencesInput.ndof_fly_helicopter

Device up/down directly controls the Z position of the 3D viewport (default False)

**Type:**

bool

<a id="bpy.types.PreferencesInput.ndof_fly_speed_auto"></a>

#### bpy.types.PreferencesInput.ndof_fly_speed_auto

Automatically adjusts fly navigation speed based on the distance of objects near the center of the viewport, making it easier to navigate complex scenes. Speed is recalculated each time movement starts. (default False)

**Type:**

bool

<a id="bpy.types.PreferencesInput.ndof_lock_camera_pan_zoom"></a>

#### bpy.types.PreferencesInput.ndof_lock_camera_pan_zoom

Pan/zoom the camera view instead of leaving the camera view when orbiting (default True)

**Type:**

bool

<a id="bpy.types.PreferencesInput.ndof_lock_horizon"></a>

#### bpy.types.PreferencesInput.ndof_lock_horizon

Lock Horizon forces the horizon to be kept leveled as it currently is (default True)

**Type:**

bool

<a id="bpy.types.PreferencesInput.ndof_navigation_mode"></a>

#### bpy.types.PreferencesInput.ndof_navigation_mode

3D Mouse Navigation Mode (default `'OBJECT'`)

- `OBJECT`
  Object – This mode is like reaching into the screen and holding the model in your hand. Push the 3D Mouse cap left, and the model moves left. Push right and the model moves right.
- `FLY`
  Fly – Enables using the 3D Mouse as if it is a camera. Push into the scene and the camera moves forward into the scene. You are entering the scene as if flying around in it. This also inverts pan & zoom for 2D views.
- `DRONE`
  Drone – Enables a Fly Mode navigation but pushing the cap forward while looking down will not change the altitude of the camera..

**Type:**

Literal[‘OBJECT’, ‘FLY’, ‘DRONE’]

<a id="bpy.types.PreferencesInput.ndof_orbit_center_auto"></a>

#### bpy.types.PreferencesInput.ndof_orbit_center_auto

Auto sets the orbit center dynamically. When the complete model is in view, the center of volume of the whole model is used as the rotation point. When you move closer, the orbit center will be set on an object close to your center of the view. (default True)

**Type:**

bool

<a id="bpy.types.PreferencesInput.ndof_orbit_center_selected"></a>

#### bpy.types.PreferencesInput.ndof_orbit_center_selected

Selected Item forces the orbit center to only take the currently selected objects into account. (default False)

**Type:**

bool

<a id="bpy.types.PreferencesInput.ndof_panx_invert_axis"></a>

#### bpy.types.PreferencesInput.ndof_panx_invert_axis

(default False)

**Type:**

bool

<a id="bpy.types.PreferencesInput.ndof_pany_invert_axis"></a>

#### bpy.types.PreferencesInput.ndof_pany_invert_axis

(default False)

**Type:**

bool

<a id="bpy.types.PreferencesInput.ndof_panz_invert_axis"></a>

#### bpy.types.PreferencesInput.ndof_panz_invert_axis

(default False)

**Type:**

bool

<a id="bpy.types.PreferencesInput.ndof_rotation_sensitivity"></a>

#### bpy.types.PreferencesInput.ndof_rotation_sensitivity

Overall sensitivity of the 3D Mouse for rotation (in [0.01, 40], default 4.0)

**Type:**

float

<a id="bpy.types.PreferencesInput.ndof_rotx_invert_axis"></a>

#### bpy.types.PreferencesInput.ndof_rotx_invert_axis

(default False)

**Type:**

bool

<a id="bpy.types.PreferencesInput.ndof_roty_invert_axis"></a>

#### bpy.types.PreferencesInput.ndof_roty_invert_axis

(default False)

**Type:**

bool

<a id="bpy.types.PreferencesInput.ndof_rotz_invert_axis"></a>

#### bpy.types.PreferencesInput.ndof_rotz_invert_axis

(default False)

**Type:**

bool

<a id="bpy.types.PreferencesInput.ndof_show_guide_orbit_axis"></a>

#### bpy.types.PreferencesInput.ndof_show_guide_orbit_axis

Display the center and axis during rotation (default False)

**Type:**

bool

<a id="bpy.types.PreferencesInput.ndof_show_guide_orbit_center"></a>

#### bpy.types.PreferencesInput.ndof_show_guide_orbit_center

Display the orbit center during rotation (default True)

**Type:**

bool

<a id="bpy.types.PreferencesInput.ndof_translation_sensitivity"></a>

#### bpy.types.PreferencesInput.ndof_translation_sensitivity

Overall sensitivity of the 3D Mouse for translation (in [0.01, 40], default 4.0)

**Type:**

float

<a id="bpy.types.PreferencesInput.ndof_zoom_direction"></a>

#### bpy.types.PreferencesInput.ndof_zoom_direction

Which axis of the 3D Mouse cap zooms the view (default `'NDOF_ZOOM_FORWARD'`)

- `NDOF_ZOOM_FORWARD`
  Forward/Backward – Zoom by pulling the 3D Mouse cap upwards or pushing the cap downwards.
- `NDOF_ZOOM_UP`
  Up/Down – Zoom by pulling the 3D Mouse cap upwards or pushing the cap downwards.

**Type:**

Literal[‘NDOF_ZOOM_FORWARD’, ‘NDOF_ZOOM_UP’]

<a id="bpy.types.PreferencesInput.pressure_softness"></a>

#### bpy.types.PreferencesInput.pressure_softness

Adjusts softness of the low pressure response onset using a gamma curve (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.PreferencesInput.pressure_threshold_max"></a>

#### bpy.types.PreferencesInput.pressure_threshold_max

Raw input pressure value that is interpreted as 100% by Blender (in [0, 1], default 1.0)

**Type:**

float

<a id="bpy.types.PreferencesInput.show_tablet_debug_values"></a>

#### bpy.types.PreferencesInput.show_tablet_debug_values

Show pressure values when using a paint operator (default False)

**Type:**

bool

<a id="bpy.types.PreferencesInput.tablet_api"></a>

#### bpy.types.PreferencesInput.tablet_api

Select the tablet API to use for pressure sensitivity (may require restarting Blender for changes to take effect) (default `'AUTOMATIC'`)

- `AUTOMATIC`
  Automatic – Automatically choose Wintab or Windows Ink depending on the device.
- `WINDOWS_INK`
  Windows Ink – Use native Windows Ink API, for modern tablet and pen devices. Requires Windows 8 or newer..
- `WINTAB`
  Wintab – Use Wintab driver for older tablets and Windows versions.

**Type:**

Literal[‘AUTOMATIC’, ‘WINDOWS_INK’, ‘WINTAB’]

<a id="bpy.types.PreferencesInput.touchpad_scroll_direction"></a>

#### bpy.types.PreferencesInput.touchpad_scroll_direction

Scroll direction (Wayland only) (default `'TRADITIONAL'`)

- `TRADITIONAL`
  Traditional – Traditional scroll direction.
- `NATURAL`
  Natural – Natural scroll direction.

**Type:**

Literal[‘TRADITIONAL’, ‘NATURAL’]

<a id="bpy.types.PreferencesInput.use_auto_perspective"></a>

#### bpy.types.PreferencesInput.use_auto_perspective

Automatically switch between orthographic and perspective when changing from top/front/side views (default True)

**Type:**

bool

<a id="bpy.types.PreferencesInput.use_drag_immediately"></a>

#### bpy.types.PreferencesInput.use_drag_immediately

Moving things with a mouse drag confirms when releasing the button (default True)

**Type:**

bool

<a id="bpy.types.PreferencesInput.use_emulate_numpad"></a>

#### bpy.types.PreferencesInput.use_emulate_numpad

Main 1 to 0 keys act as the numpad ones (useful for laptops) (default False)

**Type:**

bool

<a id="bpy.types.PreferencesInput.use_mouse_continuous"></a>

#### bpy.types.PreferencesInput.use_mouse_continuous

Let the mouse wrap around the view boundaries so mouse movements are not limited by the screen size (used by transform, dragging of UI controls, etc.) (default True)

**Type:**

bool

<a id="bpy.types.PreferencesInput.use_mouse_depth_navigate"></a>

#### bpy.types.PreferencesInput.use_mouse_depth_navigate

Use the depth under the mouse to improve view pan/rotate/zoom functionality (default False)

**Type:**

bool

<a id="bpy.types.PreferencesInput.use_mouse_emulate_3_button"></a>

#### bpy.types.PreferencesInput.use_mouse_emulate_3_button

Emulate Middle Mouse with Alt+Left Mouse (default False)

**Type:**

bool

<a id="bpy.types.PreferencesInput.use_multitouch_gestures"></a>

#### bpy.types.PreferencesInput.use_multitouch_gestures

Use multi-touch gestures for navigation with touchpad, instead of scroll wheel emulation (default True)

**Type:**

bool

<a id="bpy.types.PreferencesInput.use_numeric_input_advanced"></a>

#### bpy.types.PreferencesInput.use_numeric_input_advanced

When entering numbers while transforming, default to advanced mode for full math expression evaluation (default False)

**Type:**

bool

<a id="bpy.types.PreferencesInput.use_rotate_around_active"></a>

#### bpy.types.PreferencesInput.use_rotate_around_active

Use the selection (or the last stroke center in Paint modes) as the pivot point for orbiting (default False)

**Type:**

bool

<a id="bpy.types.PreferencesInput.use_zoom_to_mouse"></a>

#### bpy.types.PreferencesInput.use_zoom_to_mouse

Zoom in towards the mouse pointer’s position in the 3D view, rather than the 2D window center (default False)

**Type:**

bool

<a id="bpy.types.PreferencesInput.view_rotate_method"></a>

#### bpy.types.PreferencesInput.view_rotate_method

Orbit method in the viewport (default `'TURNTABLE'`)

- `TURNTABLE`
  Turntable – Turntable keeps the Z-axis upright while orbiting.
- `TRACKBALL`
  Trackball – Trackball allows you to tumble your view at any angle.

**Type:**

Literal[‘TURNTABLE’, ‘TRACKBALL’]

<a id="bpy.types.PreferencesInput.view_rotate_sensitivity_trackball"></a>

#### bpy.types.PreferencesInput.view_rotate_sensitivity_trackball

Scale trackball orbit sensitivity (in [0.1, 10], default 1.0)

**Type:**

float

<a id="bpy.types.PreferencesInput.view_rotate_sensitivity_turntable"></a>

#### bpy.types.PreferencesInput.view_rotate_sensitivity_turntable

Rotation amount per pixel to control how fast the viewport orbits (in [1.74533e-05, 0.261799], default 0.00698132)

**Type:**

float

<a id="bpy.types.PreferencesInput.view_zoom_axis"></a>

#### bpy.types.PreferencesInput.view_zoom_axis

Axis of mouse movement to zoom in or out on (default `'VERTICAL'`)

- `VERTICAL`
  Vertical – Zoom in and out based on vertical mouse movement.
- `HORIZONTAL`
  Horizontal – Zoom in and out based on horizontal mouse movement.

**Type:**

Literal[‘VERTICAL’, ‘HORIZONTAL’]

<a id="bpy.types.PreferencesInput.view_zoom_method"></a>

#### bpy.types.PreferencesInput.view_zoom_method

Which style to use for viewport scaling (default `'DOLLY'`)

- `CONTINUE`
  Continue – Continuous zooming. The zoom direction and speed depends on how far along the set Zoom Axis the mouse has moved..
- `DOLLY`
  Dolly – Zoom in and out based on mouse movement along the set Zoom Axis.
- `SCALE`
  Scale – Zoom in and out as if you are scaling the view, mouse movements relative to center.

**Type:**

Literal[‘CONTINUE’, ‘DOLLY’, ‘SCALE’]

<a id="bpy.types.PreferencesInput.walk_navigation"></a>

#### bpy.types.PreferencesInput.walk_navigation

Settings for walk navigation mode (readonly, never None)

**Type:**

[`WalkNavigation`](bpy.types.WalkNavigation.md#bpy.types.WalkNavigation "bpy.types.WalkNavigation")

<a id="bpy.types.PreferencesInput.xr_navigation"></a>

#### bpy.types.PreferencesInput.xr_navigation

Settings for navigation in XR (readonly, never None)

**Type:**

[`XrNavigation`](bpy.types.XrNavigation.md#bpy.types.XrNavigation "bpy.types.XrNavigation")

<a id="bpy.types.PreferencesInput.bl_rna_get_subclass"></a>

#### classmethod bpy.types.PreferencesInput.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.PreferencesInput.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.PreferencesInput.bl_rna_get_subclass_py(id, default=None, /)

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

<a id="references"></a>

## References

|  |  |
| --- | --- |
| - [`Preferences.inputs`](bpy.types.Preferences.md#bpy.types.Preferences.inputs "bpy.types.Preferences.inputs") |  |

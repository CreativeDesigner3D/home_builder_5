<!-- source: Blender Python API reference 5.2 / bpy.types.PreferencesView.html -->

<a id="preferencesview-bpy-struct"></a>

# PreferencesView(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.PreferencesView"></a>

### class bpy.types.PreferencesView(bpy_struct)

Preferences related to viewing data

<a id="bpy.types.PreferencesView.asset_access"></a>

#### bpy.types.PreferencesView.asset_access

Choose the visibility of online and offline assets (default `'ALL'`)

**Type:**

Literal[[Asset Access Items](bpy_types_enum_items/asset_access_items.md#rna-enum-asset-access-items)]

<a id="bpy.types.PreferencesView.border_width"></a>

#### bpy.types.PreferencesView.border_width

Size of the padding around each editor. (in [1, 10], default 2)

**Type:**

int

<a id="bpy.types.PreferencesView.color_picker_type"></a>

#### bpy.types.PreferencesView.color_picker_type

Different styles of displaying the color picker widget (default `'CIRCLE_HSV'`)

- `CIRCLE_HSV`
  Circle (HSV) – A circular Hue/Saturation color wheel, with Value slider.
- `CIRCLE_HSL`
  Circle (HSL) – A circular Hue/Saturation color wheel, with Lightness slider.
- `SQUARE_SV`
  Square (SV + H) – A square showing Saturation/Value, with Hue slider.
- `SQUARE_HS`
  Square (HS + V) – A square showing Hue/Saturation, with Value slider.
- `SQUARE_HV`
  Square (HV + S) – A square showing Hue/Value, with Saturation slider.

**Type:**

Literal[‘CIRCLE_HSV’, ‘CIRCLE_HSL’, ‘SQUARE_SV’, ‘SQUARE_HS’, ‘SQUARE_HV’]

<a id="bpy.types.PreferencesView.date_format"></a>

#### bpy.types.PreferencesView.date_format

Format for displaying date strings (default `'DEFAULT'`)

- `DEFAULT`
  Default – Default date formatting based on output language.
- `LE_SLASH`
  dd/mm/yyyy – Date format: dd/mm/yyyy, eg: 27/02/2019.
- `LE_DOT`
  dd.mm.yyyy – Date format: dd.mm.yyyy, eg: 27.02.2019.
- `LE_DASH`
  dd-mm-yyyy – Date format: dd-mm-yyyy, eg: 27-02-2019.
- `ME_SLASH`
  mm/dd/yyyy – Date format: mm/dd/yyyy, eg: 02/27/2019.
- `BE_SLASH`
  yyyy/mm/dd – Date format: yyyy/mm/dd, eg: 2019/02/27.
- `BE_DOT`
  yyyy.mm.dd – Date format: yyyy.mm.dd, eg: 2019.02.27.
- `BE_DASH`
  yyyy-mm-dd – Date format: yyyy-mm-dd, eg: 2019-02-27.

**Type:**

Literal[‘DEFAULT’, ‘LE_SLASH’, ‘LE_DOT’, ‘LE_DASH’, ‘ME_SLASH’, ‘BE_SLASH’, ‘BE_DOT’, ‘BE_DASH’]

<a id="bpy.types.PreferencesView.factor_display_type"></a>

#### bpy.types.PreferencesView.factor_display_type

How factor values are displayed (default `'FACTOR'`)

- `FACTOR`
  Factor – Display factors as values between 0 and 1.
- `PERCENTAGE`
  Percentage – Display factors as percentages.

**Type:**

Literal[‘FACTOR’, ‘PERCENTAGE’]

<a id="bpy.types.PreferencesView.filebrowser_display_type"></a>

#### bpy.types.PreferencesView.filebrowser_display_type

Default location where the File Editor will be displayed in (default `'WINDOW'`)

- `SCREEN`
  Maximized Area – Open the temporary editor in a maximized screen.
- `WINDOW`
  New Window – Open the temporary editor in a new window.

**Type:**

Literal[‘SCREEN’, ‘WINDOW’]

<a id="bpy.types.PreferencesView.font_path_ui"></a>

#### bpy.types.PreferencesView.font_path_ui

Path to interface font (default “”, never None)

**Type:**

str

<a id="bpy.types.PreferencesView.font_path_ui_mono"></a>

#### bpy.types.PreferencesView.font_path_ui_mono

Path to interface monospaced Font (default “”, never None)

**Type:**

str

<a id="bpy.types.PreferencesView.gizmo_size"></a>

#### bpy.types.PreferencesView.gizmo_size

Diameter of the gizmo (in [10, 200], default 75)

**Type:**

int

<a id="bpy.types.PreferencesView.gizmo_size_navigate_v3d"></a>

#### bpy.types.PreferencesView.gizmo_size_navigate_v3d

The Navigate Gizmo size (in [30, 200], default 80)

**Type:**

int

<a id="bpy.types.PreferencesView.header_align"></a>

#### bpy.types.PreferencesView.header_align

Default header position for new space-types (default `'BOTTOM'`)

- `NONE`
  Keep Existing – Keep existing header alignment.
- `TOP`
  Top – Top aligned on load.
- `BOTTOM`
  Bottom – Bottom align on load (except for property editors).

**Type:**

Literal[‘NONE’, ‘TOP’, ‘BOTTOM’]

<a id="bpy.types.PreferencesView.language"></a>

#### bpy.types.PreferencesView.language

Language used for translation (default `'DEFAULT'`)

- `DEFAULT`
  Automatic – Automatically choose the system-defined language if available, or fall-back to English (US).
- `ab`
  Abkhaz - Аԥсуа бызшәа – Locale code: ab. Translation progress: 0%.
- `ar_EG`
  Arabic - ﺔﻴﺑﺮﻌﻟﺍ – Locale code: ar_EG. Translation progress: 23%.
- `eu_EU`
  Basque - Euskara – Locale code: eu_EU. Translation progress: 1%.
- `be`
  Belarusian - Беларуская – Locale code: be. Translation progress: 0%.
- `bg_BG`
  Bulgarian - Български – Locale code: bg_BG. Translation progress: 1%.
- `ca_AD`
  Catalan - Català – Locale code: ca_AD. Translation progress: 100%.
- `zh_HANS`
  Chinese (Simplified) - 简体中文 – Locale code: zh_HANS. Translation progress: 100%.
- `zh_HANT`
  Chinese (Traditional) - 繁體中文 – Locale code: zh_HANT. Translation progress: 60%.
- `hr`
  Croatian - Hrvatski – Locale code: hr. Translation progress: 1%.
- `cs_CZ`
  Czech - Čeština – Locale code: cs_CZ. Translation progress: 26%.
- `da`
  Danish - Dansk – Locale code: da. Translation progress: 3%.
- `nl_NL`
  Dutch - Nederlands – Locale code: nl_NL. Translation progress: 7%.
- `en_GB`
  English (UK) – Locale code: en_GB. Translation progress: 95%.
- `en_US`
  English (US) – Locale code: en_US. Translation progress: 100%.
- `eo`
  Esperanto - Esperanto – Locale code: eo. Translation progress: 0%.
- `fi_FI`
  Finnish - Suomi – Locale code: fi_FI. Translation progress: 11%.
- `fr_FR`
  French - Français – Locale code: fr_FR. Translation progress: 100%.
- `ka`
  Georgian - ქართული – Locale code: ka. Translation progress: 100%.
- `de_DE`
  German - Deutsch – Locale code: de_DE. Translation progress: 35%.
- `el_GR`
  Greek - Ελληνικά – Locale code: el_GR. Translation progress: 1%.
- `he_IL`
  Hebrew - תירִבְעִ – Locale code: he_IL. Translation progress: 2%.
- `hi_IN`
  Hindi - हिन्दी – Locale code: hi_IN. Translation progress: 4%.
- `hu_HU`
  Hungarian - Magyar – Locale code: hu_HU. Translation progress: 10%.
- `id_ID`
  Indonesian - Bahasa indonesia – Locale code: id_ID. Translation progress: 21%.
- `it_IT`
  Italian - Italiano – Locale code: it_IT. Translation progress: 43%.
- `ja_JP`
  Japanese - 日本語 – Locale code: ja_JP. Translation progress: 100%.
- `ko_KR`
  Korean - 한국어 – Locale code: ko_KR. Translation progress: 93%.
- `ky_KG`
  Kyrgyz - Кыргыз тили – Locale code: ky_KG. Translation progress: 2%.
- `lt`
  Lithuanian - Lietuviškai – Locale code: lt. Translation progress: 3%.
- `ml`
  Malayalam - മലയാളം – Locale code: ml. Translation progress: 0%.
- `nb`
  Norwegian (Bokmål) - Norsk bokmål – Locale code: nb. Translation progress: 4%.
- `fa_IR`
  Persian - ﯽﺳﺭﺎﻓ – Locale code: fa_IR. Translation progress: 3%.
- `pl_PL`
  Polish - Polski – Locale code: pl_PL. Translation progress: 100%.
- `pt_BR`
  Portuguese (Brazil) - Português brasileiro – Locale code: pt_BR. Translation progress: 41%.
- `pt_PT`
  Portuguese (Portugal) - Português europeu – Locale code: pt_PT. Translation progress: 79%.
- `ro_RO`
  Romanian - Român – Locale code: ro_RO. Translation progress: 2%.
- `ru_RU`
  Russian - Русский – Locale code: ru_RU. Translation progress: 100%.
- `sr_RS`
  Serbian (Cyrillic) - Српски – Locale code: sr_RS. Translation progress: 15%.
- `sr_RS@latin`
  Serbian (Latin) - Srpski latinica – Locale code: [sr_RS@latin](mailto:sr_RS%40latin). Translation progress: 15%.
- `sk_SK`
  Slovak - Slovenčina – Locale code: sk_SK. Translation progress: 100%.
- `sl`
  Slovenian - Slovenščina – Locale code: sl. Translation progress: 50%.
- `es`
  Spanish - Español – Locale code: es. Translation progress: 100%.
- `sw`
  Swahili - Kiswahili – Locale code: sw. Translation progress: 69%.
- `sv_SE`
  Swedish - Svenska – Locale code: sv_SE. Translation progress: 96%.
- `ta`
  Tamil - தமிழ் – Locale code: ta. Translation progress: 96%.
- `th_TH`
  Thai - ภาษาไทย – Locale code: th_TH. Translation progress: 5%.
- `tr_TR`
  Turkish - Türkçe – Locale code: tr_TR. Translation progress: 75%.
- `uk_UA`
  Ukrainian - Українська – Locale code: uk_UA. Translation progress: 55%.
- `ur`
  Urdu - وُدرُا – Locale code: ur. Translation progress: 82%.
- `vi_VN`
  Vietnamese - Tiếng Việt – Locale code: vi_VN. Translation progress: 96%.

**Type:**

Literal[‘DEFAULT’, ‘ab’, ‘ar_EG’, ‘eu_EU’, ‘be’, ‘bg_BG’, ‘ca_AD’, ‘zh_HANS’, ‘zh_HANT’, ‘hr’, ‘cs_CZ’, ‘da’, ‘nl_NL’, ‘en_GB’, ‘en_US’, ‘eo’, ‘fi_FI’, ‘fr_FR’, ‘ka’, ‘de_DE’, ‘el_GR’, ‘he_IL’, ‘hi_IN’, ‘hu_HU’, ‘id_ID’, ‘it_IT’, ‘ja_JP’, ‘ko_KR’, ‘ky_KG’, ‘lt’, ‘ml’, ‘nb’, ‘fa_IR’, ‘pl_PL’, ‘pt_BR’, ‘pt_PT’, ‘ro_RO’, ‘ru_RU’, ‘sr_RS’, [‘sr_RS@latin](mailto:'sr_RS%40latin)’, ‘sk_SK’, ‘sl’, ‘es’, ‘sw’, ‘sv_SE’, ‘ta’, ‘th_TH’, ‘tr_TR’, ‘uk_UA’, ‘ur’, ‘vi_VN’]

<a id="bpy.types.PreferencesView.lookdev_sphere_size"></a>

#### bpy.types.PreferencesView.lookdev_sphere_size

Diameter of the HDRI reference spheres (in [50, 400], default 150)

**Type:**

int

<a id="bpy.types.PreferencesView.menu_close_leave"></a>

#### bpy.types.PreferencesView.menu_close_leave

Close menus when the mouse is moved out of the region. (default False)

**Type:**

bool

<a id="bpy.types.PreferencesView.mini_axis_brightness"></a>

#### bpy.types.PreferencesView.mini_axis_brightness

Brightness of the icon (in [0, 10], default 8)

**Type:**

int

<a id="bpy.types.PreferencesView.mini_axis_size"></a>

#### bpy.types.PreferencesView.mini_axis_size

The axes icon’s size (in [10, 64], default 25)

**Type:**

int

<a id="bpy.types.PreferencesView.mini_axis_type"></a>

#### bpy.types.PreferencesView.mini_axis_type

Show small rotating 3D axes in the top right corner of the 3D viewport (default `'GIZMO'`)

**Type:**

Literal[‘NONE’, ‘MINIMAL’, ‘GIZMO’]

<a id="bpy.types.PreferencesView.open_sublevel_delay"></a>

#### bpy.types.PreferencesView.open_sublevel_delay

Time delay in 1/10 seconds before automatically opening sub level menus (in [1, 40], default 2)

**Type:**

int

<a id="bpy.types.PreferencesView.open_toplevel_delay"></a>

#### bpy.types.PreferencesView.open_toplevel_delay

Time delay in 1/10 seconds before automatically opening top level menus (in [1, 40], default 5)

**Type:**

int

<a id="bpy.types.PreferencesView.pie_animation_timeout"></a>

#### bpy.types.PreferencesView.pie_animation_timeout

Time needed to fully animate the pie to unfolded state (in 1/100ths of sec) (in [0, 1000], default 6)

**Type:**

int

<a id="bpy.types.PreferencesView.pie_initial_timeout"></a>

#### bpy.types.PreferencesView.pie_initial_timeout

Pie menus will use the initial mouse position as center for this amount of time (in 1/100ths of sec) (in [0, 1000], default 0)

**Type:**

int

<a id="bpy.types.PreferencesView.pie_menu_confirm"></a>

#### bpy.types.PreferencesView.pie_menu_confirm

Distance threshold after which selection is made (zero to disable) (in [0, 1000], default 0)

**Type:**

int

<a id="bpy.types.PreferencesView.pie_menu_radius"></a>

#### bpy.types.PreferencesView.pie_menu_radius

Pie menu size in pixels (in [0, 1000], default 100)

**Type:**

int

<a id="bpy.types.PreferencesView.pie_menu_threshold"></a>

#### bpy.types.PreferencesView.pie_menu_threshold

Distance from center needed before a selection can be made (in [0, 1000], default 12)

**Type:**

int

<a id="bpy.types.PreferencesView.pie_tap_timeout"></a>

#### bpy.types.PreferencesView.pie_tap_timeout

Pie menu button held longer than this will dismiss menu on release (in 1/100ths of sec) (in [0, 1000], default 20)

**Type:**

int

<a id="bpy.types.PreferencesView.playback_fps_samples"></a>

#### bpy.types.PreferencesView.playback_fps_samples

The number of frames to use for calculating FPS average. Zero to calculate this automatically, where the number of samples matches the target FPS. (in [0, 5000], default 8)

**Type:**

int

<a id="bpy.types.PreferencesView.preferences_display_type"></a>

#### bpy.types.PreferencesView.preferences_display_type

Default location where the Preferences will be displayed in (default `'WINDOW'`)

- `SCREEN`
  Maximized Area – Open the temporary editor in a maximized screen.
- `WINDOW`
  New Window – Open the temporary editor in a new window.

**Type:**

Literal[‘SCREEN’, ‘WINDOW’]

<a id="bpy.types.PreferencesView.render_display_type"></a>

#### bpy.types.PreferencesView.render_display_type

Default location where rendered images will be displayed in (default `'WINDOW'`)

- `NONE`
  Keep User Interface – Images are rendered without changing the user interface.
- `SCREEN`
  Maximized Area – Images are rendered in a maximized Image Editor.
- `AREA`
  Image Editor – Images are rendered in an Image Editor.
- `WINDOW`
  New Window – Images are rendered in a new window.

**Type:**

Literal[‘NONE’, ‘SCREEN’, ‘AREA’, ‘WINDOW’]

<a id="bpy.types.PreferencesView.rotation_angle"></a>

#### bpy.types.PreferencesView.rotation_angle

Rotation step for numerical pad keys (2 4 6 8) (in [0, 90], default 15.0)

**Type:**

float

<a id="bpy.types.PreferencesView.show_addons_enabled_only"></a>

#### bpy.types.PreferencesView.show_addons_enabled_only

Only show enabled add-ons. Un-check to see all installed add-ons. (default False)

**Type:**

bool

<a id="bpy.types.PreferencesView.show_area_handle"></a>

#### bpy.types.PreferencesView.show_area_handle

Show visible area maintenance corner handles (default False)

**Type:**

bool

<a id="bpy.types.PreferencesView.show_column_layout"></a>

#### bpy.types.PreferencesView.show_column_layout

Use a column layout for toolbox (default True)

**Type:**

bool

<a id="bpy.types.PreferencesView.show_developer_ui"></a>

#### bpy.types.PreferencesView.show_developer_ui

Display advanced settings and tools for developers (default False)

**Type:**

bool

<a id="bpy.types.PreferencesView.show_extensions_updates"></a>

#### bpy.types.PreferencesView.show_extensions_updates

Show Extensions Update Count (default True)

**Type:**

bool

<a id="bpy.types.PreferencesView.show_gizmo"></a>

#### bpy.types.PreferencesView.show_gizmo

Use transform gizmos by default (default True)

**Type:**

bool

<a id="bpy.types.PreferencesView.show_navigate_ui"></a>

#### bpy.types.PreferencesView.show_navigate_ui

Show navigation controls in 2D and 3D views which do not have scroll bars (default True)

**Type:**

bool

<a id="bpy.types.PreferencesView.show_number_arrows"></a>

#### bpy.types.PreferencesView.show_number_arrows

Display arrows in numeric input fields for increasing or decreasing values (default False)

**Type:**

bool

<a id="bpy.types.PreferencesView.show_object_info"></a>

#### bpy.types.PreferencesView.show_object_info

Include the name of the active object and the current frame number in the text info overlay (default True)

**Type:**

bool

<a id="bpy.types.PreferencesView.show_playback_fps"></a>

#### bpy.types.PreferencesView.show_playback_fps

Include the number of frames displayed per second in the text info overlay while animation is played back (default True)

**Type:**

bool

<a id="bpy.types.PreferencesView.show_splash"></a>

#### bpy.types.PreferencesView.show_splash

Display splash screen on startup (default True)

**Type:**

bool

<a id="bpy.types.PreferencesView.show_statusbar_memory"></a>

#### bpy.types.PreferencesView.show_statusbar_memory

Show Blender memory usage (default False)

**Type:**

bool

<a id="bpy.types.PreferencesView.show_statusbar_scene_duration"></a>

#### bpy.types.PreferencesView.show_statusbar_scene_duration

Show scene duration (default False)

**Type:**

bool

<a id="bpy.types.PreferencesView.show_statusbar_stats"></a>

#### bpy.types.PreferencesView.show_statusbar_stats

Show scene statistics (default False)

**Type:**

bool

<a id="bpy.types.PreferencesView.show_statusbar_version"></a>

#### bpy.types.PreferencesView.show_statusbar_version

Show Blender version string (default True)

**Type:**

bool

<a id="bpy.types.PreferencesView.show_statusbar_vram"></a>

#### bpy.types.PreferencesView.show_statusbar_vram

Show GPU video memory usage (default False)

**Type:**

bool

<a id="bpy.types.PreferencesView.show_tooltips"></a>

#### bpy.types.PreferencesView.show_tooltips

Display tooltips (when disabled, hold Alt then hover to force display) (default True)

**Type:**

bool

<a id="bpy.types.PreferencesView.show_tooltips_python"></a>

#### bpy.types.PreferencesView.show_tooltips_python

Show Python references in tooltips (default False)

**Type:**

bool

<a id="bpy.types.PreferencesView.show_view_name"></a>

#### bpy.types.PreferencesView.show_view_name

Include the name of the view orientation in the text info overlay (default True)

**Type:**

bool

<a id="bpy.types.PreferencesView.smooth_view"></a>

#### bpy.types.PreferencesView.smooth_view

Time to animate the view in milliseconds, zero to disable (in [0, 1000], default 200)

**Type:**

int

<a id="bpy.types.PreferencesView.text_hinting"></a>

#### bpy.types.PreferencesView.text_hinting

Method for making user interface text render sharp (default `'AUTO'`)

**Type:**

Literal[‘AUTO’, ‘NONE’, ‘SLIGHT’, ‘FULL’]

<a id="bpy.types.PreferencesView.time_format"></a>

#### bpy.types.PreferencesView.time_format

Format for displaying time strings (default `'H24'`)

- `H24`
  24-Hour (23:59) – Time format: 24-hour clock with colon, eg: 23:59.
- `H12`
  12-Hour (11:59 PM) – Time format: 12-hour clock, eg: 11:59 PM.

**Type:**

Literal[‘H24’, ‘H12’]

<a id="bpy.types.PreferencesView.timecode_style"></a>

#### bpy.types.PreferencesView.timecode_style

Format of timecode displayed when not displaying timing in terms of frames (default `'MINIMAL'`)

- `MINIMAL`
  Minimal Info – Most compact representation, uses ‘+’ as separator for sub-second frame numbers, with left and right truncation of the timecode as necessary.
- `SMPTE`
  SMPTE (Full) – Full SMPTE timecode (format is HH:MM:SS:FF).
- `SMPTE_COMPACT`
  SMPTE (Compact) – SMPTE timecode showing minutes, seconds, and frames only - hours are also shown if necessary, but not by default.
- `MILLISECONDS`
  Compact with Decimals – Similar to SMPTE (Compact), except that the decimal part of the second is shown instead of frames.
- `SECONDS_ONLY`
  Only Seconds – Direct conversion of frame numbers to seconds.

**Type:**

Literal[‘MINIMAL’, ‘SMPTE’, ‘SMPTE_COMPACT’, ‘MILLISECONDS’, ‘SECONDS_ONLY’]

<a id="bpy.types.PreferencesView.ui_line_width"></a>

#### bpy.types.PreferencesView.ui_line_width

Changes the thickness of widget outlines, lines and dots in the interface (default `'AUTO'`)

- `THIN`
  Thin – Thinner lines than the default.
- `AUTO`
  Default – Automatic line width based on UI scale.
- `THICK`
  Thick – Thicker lines than the default.

**Type:**

Literal[‘THIN’, ‘AUTO’, ‘THICK’]

<a id="bpy.types.PreferencesView.ui_scale"></a>

#### bpy.types.PreferencesView.ui_scale

Changes the size of the fonts and widgets in the interface (in [0.5, 6], default 1.0)

**Type:**

float

<a id="bpy.types.PreferencesView.use_filter_brushes_by_tool"></a>

#### bpy.types.PreferencesView.use_filter_brushes_by_tool

Only show brushes applicable for the currently active tool in the asset shelf. Stored in the Preferences, which may have to be saved manually if Auto-Save Preferences is disabled (default False)

**Type:**

bool

<a id="bpy.types.PreferencesView.use_fresnel_edit"></a>

#### bpy.types.PreferencesView.use_fresnel_edit

Enable a fresnel effect on edit mesh overlays.
It improves shape readability of very dense meshes, but increases eye fatigue when modeling lower poly

(default False)

**Type:**

bool

<a id="bpy.types.PreferencesView.use_mouse_over_open"></a>

#### bpy.types.PreferencesView.use_mouse_over_open

Open menu buttons and pull-downs automatically when the mouse is hovering (default False)

**Type:**

bool

<a id="bpy.types.PreferencesView.use_reduce_motion"></a>

#### bpy.types.PreferencesView.use_reduce_motion

Avoid animations and other motion effects in the interface (default False)

**Type:**

bool

<a id="bpy.types.PreferencesView.use_save_prompt"></a>

#### bpy.types.PreferencesView.use_save_prompt

Ask for confirmation when quitting with unsaved changes (default True)

**Type:**

bool

<a id="bpy.types.PreferencesView.use_text_antialiasing"></a>

#### bpy.types.PreferencesView.use_text_antialiasing

Smooth jagged edges of user interface text (default True)

**Type:**

bool

<a id="bpy.types.PreferencesView.use_text_render_subpixelaa"></a>

#### bpy.types.PreferencesView.use_text_render_subpixelaa

Render text for optimal horizontal placement (default False)

**Type:**

bool

<a id="bpy.types.PreferencesView.use_translate_interface"></a>

#### bpy.types.PreferencesView.use_translate_interface

Translate all labels in menus, buttons and panels (note that this might make it hard to follow tutorials or the manual) (default True)

**Type:**

bool

<a id="bpy.types.PreferencesView.use_translate_new_dataname"></a>

#### bpy.types.PreferencesView.use_translate_new_dataname

Translate the names of new data-blocks (objects, materials…) (default True)

**Type:**

bool

<a id="bpy.types.PreferencesView.use_translate_reports"></a>

#### bpy.types.PreferencesView.use_translate_reports

Translate additional information, such as error messages (default True)

**Type:**

bool

<a id="bpy.types.PreferencesView.use_translate_tooltips"></a>

#### bpy.types.PreferencesView.use_translate_tooltips

Translate the descriptions when hovering UI elements (recommended) (default True)

**Type:**

bool

<a id="bpy.types.PreferencesView.use_weight_color_range"></a>

#### bpy.types.PreferencesView.use_weight_color_range

Enable color range used for weight visualization in weight painting mode (default False)

**Type:**

bool

<a id="bpy.types.PreferencesView.view2d_grid_spacing_min"></a>

#### bpy.types.PreferencesView.view2d_grid_spacing_min

Minimum number of pixels between each gridline in 2D Viewports (in [1, 500], default 45)

**Type:**

int

<a id="bpy.types.PreferencesView.view_frame_keyframes"></a>

#### bpy.types.PreferencesView.view_frame_keyframes

Keyframes around cursor that we zoom around (in [1, 500], default 0)

**Type:**

int

<a id="bpy.types.PreferencesView.view_frame_seconds"></a>

#### bpy.types.PreferencesView.view_frame_seconds

Seconds around cursor that we zoom around (in [0, 10000], default 0.0)

**Type:**

float

<a id="bpy.types.PreferencesView.view_frame_type"></a>

#### bpy.types.PreferencesView.view_frame_type

How zooming to frame focuses around current frame (default `'KEEP_RANGE'`)

**Type:**

Literal[‘KEEP_RANGE’, ‘SECONDS’, ‘KEYFRAMES’]

<a id="bpy.types.PreferencesView.weight_color_range"></a>

#### bpy.types.PreferencesView.weight_color_range

Color range used for weight visualization in weight painting mode (readonly, never None)

**Type:**

[`ColorRamp`](bpy.types.ColorRamp.md#bpy.types.ColorRamp "bpy.types.ColorRamp")

<a id="bpy.types.PreferencesView.bl_rna_get_subclass"></a>

#### classmethod bpy.types.PreferencesView.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.PreferencesView.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.PreferencesView.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`Preferences.view`](bpy.types.Preferences.md#bpy.types.Preferences.view "bpy.types.Preferences.view") |  |

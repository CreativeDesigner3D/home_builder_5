<!-- source: Blender Python API reference 5.2 / bpy.types.WindowManager.html -->

<a id="windowmanager-id"></a>

# WindowManager(ID)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID")

<a id="bpy.types.WindowManager"></a>

### class bpy.types.WindowManager(ID)

Window manager data-block defining open windows and other user interface data

<a id="bpy.types.WindowManager.addon_filter"></a>

#### bpy.types.WindowManager.addon_filter

Filter add-ons by category

**Type:**

str

<a id="bpy.types.WindowManager.addon_search"></a>

#### bpy.types.WindowManager.addon_search

Filter by add-on name, author & category (default “”, never None)

**Type:**

str

<a id="bpy.types.WindowManager.addon_support"></a>

#### bpy.types.WindowManager.addon_support

Display support level (default {`'COMMUNITY'`, `'OFFICIAL'`})

- `OFFICIAL`
  Official – Officially supported.
- `COMMUNITY`
  Community – Maintained by community developers.

**Type:**

set[Literal[‘OFFICIAL’, ‘COMMUNITY’]]

<a id="bpy.types.WindowManager.addon_tags"></a>

#### bpy.types.WindowManager.addon_tags

(default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[`BlExtDummyGroup`]

<a id="bpy.types.WindowManager.asset_path_dummy"></a>

#### bpy.types.WindowManager.asset_path_dummy

Full path to the Blender file containing the active asset (default “”, readonly, never None)

**Type:**

str

<a id="bpy.types.WindowManager.extension_repo_filter"></a>

#### bpy.types.WindowManager.extension_repo_filter

Filter extensions by repository

**Type:**

str

<a id="bpy.types.WindowManager.extension_search"></a>

#### bpy.types.WindowManager.extension_search

Filter by extension name, author & category (default “”, never None)

**Type:**

str

<a id="bpy.types.WindowManager.extension_show_panel_available"></a>

#### bpy.types.WindowManager.extension_show_panel_available

Show the available extensions panel (default True)

**Type:**

bool

<a id="bpy.types.WindowManager.extension_show_panel_installed"></a>

#### bpy.types.WindowManager.extension_show_panel_installed

Show the installed extensions panel (default True)

**Type:**

bool

<a id="bpy.types.WindowManager.extension_tags"></a>

#### bpy.types.WindowManager.extension_tags

(default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[`BlExtDummyGroup`]

<a id="bpy.types.WindowManager.extension_type"></a>

#### bpy.types.WindowManager.extension_type

Show extensions by type (default `'ADDON'`)

- `ALL`
  All – Show all extension types.
- `ADDON`
  Add-ons – Only show add-ons.
- `THEME`
  Themes – Only show themes.

**Type:**

Literal[‘ALL’, ‘ADDON’, ‘THEME’]

<a id="bpy.types.WindowManager.extension_use_filter"></a>

#### bpy.types.WindowManager.extension_use_filter

Filter Extensions by Tags & Repository (default False)

**Type:**

bool

<a id="bpy.types.WindowManager.extensions_blocked"></a>

#### bpy.types.WindowManager.extensions_blocked

Number of installed extensions which are blocked (in [-inf, inf], default 0)

**Type:**

int

<a id="bpy.types.WindowManager.extensions_updates"></a>

#### bpy.types.WindowManager.extensions_updates

Number of extensions with available update (in [-inf, inf], default 0)

**Type:**

int

<a id="bpy.types.WindowManager.is_event_handling_break"></a>

#### bpy.types.WindowManager.is_event_handling_break

Remaining events in the queue are delayed until the next main loop iteration (default False, readonly)

**Type:**

bool

<a id="bpy.types.WindowManager.is_interface_locked"></a>

#### bpy.types.WindowManager.is_interface_locked

If true, the interface is currently locked by a running job and data should not be modified from application timers. Otherwise, the running job might conflict with the handler causing unexpected results or even crashes. (default False, readonly)

**Type:**

bool

<a id="bpy.types.WindowManager.keyconfigs"></a>

#### bpy.types.WindowManager.keyconfigs

Registered key configurations (default None, readonly)

**Type:**

[`KeyConfigurations`](bpy.types.KeyConfigurations.md#bpy.types.KeyConfigurations "bpy.types.KeyConfigurations")[[`KeyConfig`](bpy.types.KeyConfig.md#bpy.types.KeyConfig "bpy.types.KeyConfig")]

<a id="bpy.types.WindowManager.operators"></a>

#### bpy.types.WindowManager.operators

Operator registry (default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`Operator`](bpy.types.Operator.md#bpy.types.Operator "bpy.types.Operator")]

<a id="bpy.types.WindowManager.poselib_previous_action"></a>

#### bpy.types.WindowManager.poselib_previous_action

**Type:**

[`Action`](bpy.types.Action.md#bpy.types.Action "bpy.types.Action") | None

<a id="bpy.types.WindowManager.preset_name"></a>

#### bpy.types.WindowManager.preset_name

Name for new preset (default “New Preset”, never None)

**Type:**

str

<a id="bpy.types.WindowManager.reports"></a>

#### bpy.types.WindowManager.reports

Collection of reports (default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`Report`](bpy.types.Report.md#bpy.types.Report "bpy.types.Report")]

<a id="bpy.types.WindowManager.windows"></a>

#### bpy.types.WindowManager.windows

Open windows (default None, readonly)

**Type:**

[`Windows`](bpy.types.Windows.md#bpy.types.Windows "bpy.types.Windows")[[`Window`](bpy.types.Window.md#bpy.types.Window "bpy.types.Window")]

<a id="bpy.types.WindowManager.xr_session_settings"></a>

#### bpy.types.WindowManager.xr_session_settings

(readonly, never None)

**Type:**

[`XrSessionSettings`](bpy.types.XrSessionSettings.md#bpy.types.XrSessionSettings "bpy.types.XrSessionSettings")

<a id="bpy.types.WindowManager.xr_session_state"></a>

#### bpy.types.WindowManager.xr_session_state

Runtime state information about the VR session (readonly)

**Type:**

[`XrSessionState`](bpy.types.XrSessionState.md#bpy.types.XrSessionState "bpy.types.XrSessionState") | None

<a id="bpy.types.WindowManager.clipboard"></a>

#### bpy.types.WindowManager.clipboard

Clipboard text storage.

**Type:**

str

<a id="bpy.types.WindowManager.fileselect_add"></a>

#### classmethod bpy.types.WindowManager.fileselect_add(operator)

Opens a file selector with an operator.

**Parameters:**

**operator** ([`Operator`](bpy.types.Operator.md#bpy.types.Operator "bpy.types.Operator") | None) – Operator to call

This method is used from the operators `invoke` callback
which must then return `{'RUNNING_MODAL'}`.

Accepting the file selector will run the operators `execute` callback.

The following properties are supported:

`filepath`: `bpy.props.StringProperty(subtype='FILE_PATH')`
:   Represents the absolute path to the file.

`dirpath`: `bpy.props.StringProperty(subtype='DIR_PATH')`
:   Represents the absolute path to the directory.

`filename`: `bpy.props.StringProperty(subtype='FILE_NAME')`
:   Represents the filename without the leading directory.

`files`: `bpy.props.CollectionProperty(type=bpy.types.OperatorFileListElement)`
:   When present in the operator this collection includes all selected files.

`filter_glob`: `bpy.props.StringProperty(default="*.ext")`
:   When present in the operator and it’s not empty,
    it will be used as a file filter (example value: `*.zip;*.py;*.exe`).

`check_existing`: `bpy.props.BoolProperty()`
:   If this property is present and set to `True`,
    the operator will warn if the provided file-path already exists
    by highlighting the filename input field in red.

> **Warning:**
>
> After opening the file-browser the user may continue to use Blender,
> this means it is possible for the user to change the context in ways
> that would cause the operators `poll` function to fail.
>
> Unless the operator reads all necessary data from the context before the file-selector is opened,
> it is recommended for operators to check the `poll` function from `execute`
> to ensure the context is still valid.
>
> Example from the body of an operators `execute` function:
>
> ```python
> if self.options.is_invoke:
>     # The context may have changed since invoking the file selector.
>     if not self.poll(context):
>         self.report({'ERROR'}, "Invalid context")
>         return {'CANCELLED'}
> ```

<a id="bpy.types.WindowManager.modal_handler_add"></a>

#### classmethod bpy.types.WindowManager.modal_handler_add(operator)

Add a modal handler to the window manager, for the given modal operator (called by invoke() with self, just before returning {‘RUNNING_MODAL’})

**Parameters:**

**operator** ([`Operator`](bpy.types.Operator.md#bpy.types.Operator "bpy.types.Operator") | None) – Operator to call

**Returns:**

Whether adding the handler was successful

**Return type:**

bool

<a id="bpy.types.WindowManager.event_timer_add"></a>

#### bpy.types.WindowManager.event_timer_add(time_step, *, window=None)

Add a timer to the given window, to generate periodic ‘TIMER’ events

**Parameters:**

- **time_step** (float) – Time Step, Interval in seconds between timer events (in [0, inf])
- **window** ([`Window`](bpy.types.Window.md#bpy.types.Window "bpy.types.Window") | None) – Window to attach the timer to, or None (optional)

**Return type:**

[`Timer`](bpy.types.Timer.md#bpy.types.Timer "bpy.types.Timer")

<a id="bpy.types.WindowManager.event_timer_remove"></a>

#### bpy.types.WindowManager.event_timer_remove(timer)

event_timer_remove

**Parameters:**

**timer** ([`Timer`](bpy.types.Timer.md#bpy.types.Timer "bpy.types.Timer") | None) – (never None)

<a id="bpy.types.WindowManager.gizmo_group_type_ensure"></a>

#### classmethod bpy.types.WindowManager.gizmo_group_type_ensure(identifier)

Activate an existing widget group (when the persistent option isn’t set)

**Parameters:**

**identifier** (str) – Gizmo group type name (never None)

<a id="bpy.types.WindowManager.gizmo_group_type_unlink_delayed"></a>

#### classmethod bpy.types.WindowManager.gizmo_group_type_unlink_delayed(identifier)

Unlink a widget group (when the persistent option is set)

**Parameters:**

**identifier** (str) – Gizmo group type name (never None)

<a id="bpy.types.WindowManager.progress_begin"></a>

#### bpy.types.WindowManager.progress_begin(min, max)

Start progress report

**Parameters:**

- **min** (float) – min, any value in range [0,9999] (in [-inf, inf])
- **max** (float) – max, any value in range [min+1,9998] (in [-inf, inf])

<a id="bpy.types.WindowManager.progress_update"></a>

#### bpy.types.WindowManager.progress_update(value)

Update the progress feedback

**Parameters:**

**value** (float) – value, Any value between min and max as set in progress_begin() (in [-inf, inf])

<a id="bpy.types.WindowManager.progress_end"></a>

#### bpy.types.WindowManager.progress_end()

Terminate progress report

<a id="bpy.types.WindowManager.invoke_props_popup"></a>

#### classmethod bpy.types.WindowManager.invoke_props_popup(operator, event)

Operator popup invoke (show operator properties and execute it automatically on changes)

**Parameters:**

- **operator** ([`Operator`](bpy.types.Operator.md#bpy.types.Operator "bpy.types.Operator") | None) – Operator to call
- **event** ([`Event`](bpy.types.Event.md#bpy.types.Event "bpy.types.Event") | None) – Event

**Returns:**

result

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.types.WindowManager.invoke_props_dialog"></a>

#### classmethod bpy.types.WindowManager.invoke_props_dialog(operator, *, width=300, title='', confirm_text='', cancel_default=False, text_ctxt='', translate=True)

Operator dialog (non-autoexec popup) invoke (show operator properties and only execute it on click on OK button)

**Parameters:**

- **operator** ([`Operator`](bpy.types.Operator.md#bpy.types.Operator "bpy.types.Operator") | None) – Operator to call
- **width** (int) – Width of the popup (in [0, inf], optional)
- **title** (str) – Title, Optional text to show as title of the popup (optional, never None)
- **confirm_text** (str) – Confirm Text, Optional text to show instead to the default “OK” confirmation button text (optional, never None)
- **cancel_default** (bool) – cancel_default, (optional)
- **text_ctxt** (str) – Override automatic translation context of the given text (optional)
- **translate** (bool) – Translate the given text, when UI translation is enabled (optional)

**Returns:**

result

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.types.WindowManager.invoke_search_popup"></a>

#### classmethod bpy.types.WindowManager.invoke_search_popup(operator)

Operator search popup invoke which searches values of the operator’s [`bpy.types.Operator.bl_property`](bpy.types.Operator.md#bpy.types.Operator.bl_property "bpy.types.Operator.bl_property") (which must be an EnumProperty), executing it on confirmation

**Parameters:**

**operator** ([`Operator`](bpy.types.Operator.md#bpy.types.Operator "bpy.types.Operator") | None) – Operator to call

<a id="bpy.types.WindowManager.invoke_popup"></a>

#### classmethod bpy.types.WindowManager.invoke_popup(operator, *, width=300, auto_keymap=False)

Operator popup invoke (only shows operator’s properties, without executing it)

**Parameters:**

- **operator** ([`Operator`](bpy.types.Operator.md#bpy.types.Operator "bpy.types.Operator") | None) – Operator to call
- **width** (int) – Width of the popup (in [0, inf], optional)
- **auto_keymap** (bool) – Auto Keymap, Assign accelerator keys to buttons, shown as underlined characters (optional)

**Returns:**

result

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.types.WindowManager.invoke_confirm"></a>

#### classmethod bpy.types.WindowManager.invoke_confirm(operator, event, *, title='', message='', confirm_text='', icon='NONE', text_ctxt='', translate=True)

Operator confirmation popup (only to let user confirm the execution, no operator properties shown)

**Parameters:**

- **operator** ([`Operator`](bpy.types.Operator.md#bpy.types.Operator "bpy.types.Operator") | None) – Operator to call
- **event** ([`Event`](bpy.types.Event.md#bpy.types.Event "bpy.types.Event") | None) – Event
- **title** (str) – Title, Optional text to show as title of the popup (optional, never None)
- **message** (str) – Message, Optional first line of content text (optional, never None)
- **confirm_text** (str) – Confirm Text, Optional text to show instead to the default “OK” confirmation button text (optional, never None)
- **icon** (Literal['NONE', 'WARNING', 'QUESTION', 'ERROR', 'INFO']) – Icon, Optional icon displayed in the dialog (optional)
- **text_ctxt** (str) – Override automatic translation context of the given text (optional)
- **translate** (bool) – Translate the given text, when UI translation is enabled (optional)

**Returns:**

result

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.types.WindowManager.popmenu_begin__internal"></a>

#### classmethod bpy.types.WindowManager.popmenu_begin__internal(title, *, icon='NONE')

popmenu_begin__internal

**Parameters:**

- **title** (str) – (never None)
- **icon** (Literal[[Icon Items](bpy_types_enum_items/icon_items.md#rna-enum-icon-items)]) – icon, (optional)

**Returns:**

(never None)

**Return type:**

[`UIPopupMenu`](bpy.types.UIPopupMenu.md#bpy.types.UIPopupMenu "bpy.types.UIPopupMenu")

<a id="bpy.types.WindowManager.popmenu_end__internal"></a>

#### classmethod bpy.types.WindowManager.popmenu_end__internal(menu)

popmenu_end__internal

**Parameters:**

**menu** ([`UIPopupMenu`](bpy.types.UIPopupMenu.md#bpy.types.UIPopupMenu "bpy.types.UIPopupMenu") | None) – (never None)

<a id="bpy.types.WindowManager.popover_begin__internal"></a>

#### classmethod bpy.types.WindowManager.popover_begin__internal(*, ui_units_x=0, from_active_button=False)

popover_begin__internal

**Parameters:**

- **ui_units_x** (int) – ui_units_x, (in [0, inf], optional)
- **from_active_button** (bool) – Use Button, Use the active button for positioning (optional)

**Returns:**

(never None)

**Return type:**

[`UIPopover`](bpy.types.UIPopover.md#bpy.types.UIPopover "bpy.types.UIPopover")

<a id="bpy.types.WindowManager.popover_end__internal"></a>

#### classmethod bpy.types.WindowManager.popover_end__internal(menu, *, keymap=None)

popover_end__internal

**Parameters:**

- **menu** ([`UIPopover`](bpy.types.UIPopover.md#bpy.types.UIPopover "bpy.types.UIPopover") | None) – (never None)
- **keymap** ([`KeyMap`](bpy.types.KeyMap.md#bpy.types.KeyMap "bpy.types.KeyMap") | None) – Key Map, Active key map (optional)

<a id="bpy.types.WindowManager.piemenu_begin__internal"></a>

#### classmethod bpy.types.WindowManager.piemenu_begin__internal(title, *, icon='NONE', event=None)

piemenu_begin__internal

**Parameters:**

- **title** (str) – (never None)
- **icon** (Literal[[Icon Items](bpy_types_enum_items/icon_items.md#rna-enum-icon-items)]) – icon, (optional)
- **event** ([`Event`](bpy.types.Event.md#bpy.types.Event "bpy.types.Event") | None) – (optional, never None)

**Returns:**

(never None)

**Return type:**

[`UIPieMenu`](bpy.types.UIPieMenu.md#bpy.types.UIPieMenu "bpy.types.UIPieMenu")

<a id="bpy.types.WindowManager.piemenu_end__internal"></a>

#### classmethod bpy.types.WindowManager.piemenu_end__internal(menu)

piemenu_end__internal

**Parameters:**

**menu** ([`UIPieMenu`](bpy.types.UIPieMenu.md#bpy.types.UIPieMenu "bpy.types.UIPieMenu") | None) – (never None)

<a id="bpy.types.WindowManager.operator_properties_last"></a>

#### classmethod bpy.types.WindowManager.operator_properties_last(operator)

operator_properties_last

**Parameters:**

**operator** (str) – (never None)

**Returns:**

(never None)

**Return type:**

[`OperatorProperties`](bpy.types.OperatorProperties.md#bpy.types.OperatorProperties "bpy.types.OperatorProperties")

<a id="bpy.types.WindowManager.print_undo_steps"></a>

#### bpy.types.WindowManager.print_undo_steps()

print_undo_steps

<a id="bpy.types.WindowManager.tag_script_reload"></a>

#### classmethod bpy.types.WindowManager.tag_script_reload()

Tag for refreshing the interface after scripts have been reloaded

<a id="bpy.types.WindowManager.asset_library_status_begin_loading"></a>

#### classmethod bpy.types.WindowManager.asset_library_status_begin_loading(library_url, *, timeout=0.3)

Inform the asset system that the asset library at the given URL is being loaded.

**Parameters:**

- **library_url** (str) – URL, The URL identifying the asset library being loaded (never None)
- **timeout** (float) – Timeout, Maximum time in seconds after which the asset library loading will be considered cancelled, if no further status reporting is done (e.g. by repeated calls to asset_library_status_ping_still_loading()). (in [0, inf], optional)

<a id="bpy.types.WindowManager.asset_library_status_ping_still_loading"></a>

#### classmethod bpy.types.WindowManager.asset_library_status_ping_still_loading(library_url)

Inform the asset system that the loading is still ongoing. Call this regularly to prevent the loading status to timeout.

**Parameters:**

**library_url** (str) – URL, The URL identifying the asset library being loaded (never None)

<a id="bpy.types.WindowManager.asset_library_status_ping_metafiles_in_place"></a>

#### classmethod bpy.types.WindowManager.asset_library_status_ping_metafiles_in_place(library_url)

Inform the asset system that the asset meta files (_asset-library-meta.json, asset-listing.json, blender_assets.cats.txt) are in place and ready to be loaded

**Parameters:**

**library_url** (str) – URL, The URL identifying the asset library being loaded (never None)

<a id="bpy.types.WindowManager.asset_library_status_ping_loaded_new_pages"></a>

#### classmethod bpy.types.WindowManager.asset_library_status_ping_loaded_new_pages(library_url)

Inform the asset system that new content

**Parameters:**

**library_url** (str) – URL, The URL identifying the asset library being loaded (never None)

<a id="bpy.types.WindowManager.asset_library_status_ping_loaded_new_preview"></a>

#### classmethod bpy.types.WindowManager.asset_library_status_ping_loaded_new_preview(preview_full_path)

Inform the asset system that a new preview is available and ready for display

**Parameters:**

**preview_full_path** (str) – URL, The full path (not URL!) pointing to the the asset preview that should be available now (never None)

<a id="bpy.types.WindowManager.asset_library_status_ping_asset_file_progress"></a>

#### classmethod bpy.types.WindowManager.asset_library_status_ping_asset_file_progress(absolute_file_url, size_written)

Inform the asset system about the current progress of an asset file.

**Parameters:**

- **absolute_file_url** (str) – URL, The absolute URL this file was downloaded from (never None)
- **size_written** (int) – Size Written to Disk, The number of bytes written to disk after uncompressing the download data, if needed (in [0, inf])

<a id="bpy.types.WindowManager.asset_library_status_ping_asset_file_succeeded"></a>

#### classmethod bpy.types.WindowManager.asset_library_status_ping_asset_file_succeeded(library_url, absolute_file_url, local_file_abspath)

Inform the asset system that a single asset file download has finished successfully.

**Parameters:**

- **library_url** (str) – URL, The URL identifying the asset library being loaded (never None)
- **absolute_file_url** (str) – URL, The absolute URL this file was downloaded from (never None)
- **local_file_abspath** (str) – Local Path, The absolute path this file was downloaded to (never None)

<a id="bpy.types.WindowManager.asset_library_status_ping_asset_file_failed"></a>

#### classmethod bpy.types.WindowManager.asset_library_status_ping_asset_file_failed(library_url, absolute_file_url, local_file_abspath)

Inform the asset system that a single asset file download has stopped because of some failure.

**Parameters:**

- **library_url** (str) – URL, The URL identifying the asset library being loaded (never None)
- **absolute_file_url** (str) – URL, The absolute URL this file was downloaded from (never None)
- **local_file_abspath** (str) – Local Path, The absolute path this file was supposed to be downloaded to (never None)

<a id="bpy.types.WindowManager.asset_library_status_ping_finished_download_queue"></a>

#### classmethod bpy.types.WindowManager.asset_library_status_ping_finished_download_queue()

Inform the asset system that there are no more pending asset file downloads for any asset library.

<a id="bpy.types.WindowManager.asset_library_status_finished_loading"></a>

#### classmethod bpy.types.WindowManager.asset_library_status_finished_loading(library_url)

Inform the asset system that the asset library at the given URL has successfully finished loading.

**Parameters:**

**library_url** (str) – URL, The URL identifying the asset library being loaded (never None)

<a id="bpy.types.WindowManager.asset_library_status_failed_loading"></a>

#### classmethod bpy.types.WindowManager.asset_library_status_failed_loading(library_url, *, message='')

Inform the asset system that the asset library at the given URL failed loading, and should be aborted.

**Parameters:**

- **library_url** (str) – URL, The URL identifying the asset library being loaded (never None)
- **message** (str) – Message, An error message to show to users (optional, never None)

<a id="bpy.types.WindowManager.register_node_group_operators"></a>

#### classmethod bpy.types.WindowManager.register_node_group_operators()

Trigger manual re-registration of node group operators. Useful in background mode where this doesn’t happen automatically.

<a id="bpy.types.WindowManager.popover"></a>

#### bpy.types.WindowManager.popover(draw_func, *, ui_units_x=0, keymap=None, from_active_button=False)

Display a popover populated by *draw_func*.

**Parameters:**

- **draw_func** (Callable[[[`UIPopover`](bpy.types.UIPopover.md#bpy.types.UIPopover "bpy.types.UIPopover"), [`Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context")], None]) – Function to populate the popover layout.
- **ui_units_x** (int) – Width of the popover in UI units (0 for the default).
- **keymap** ([`KeyMap`](bpy.types.KeyMap.md#bpy.types.KeyMap "bpy.types.KeyMap") | None) – Optional keymap to attach to the popover.
- **from_active_button** (bool) – Anchor the popover to the active button.

<a id="bpy.types.WindowManager.popup_menu"></a>

#### bpy.types.WindowManager.popup_menu(draw_func, *, title='', icon='NONE')

Display a popup menu populated by *draw_func*.

**Parameters:**

- **draw_func** (Callable[[[`UIPopupMenu`](bpy.types.UIPopupMenu.md#bpy.types.UIPopupMenu "bpy.types.UIPopupMenu"), [`Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context")], None]) – Function to populate the menu layout.
- **title** (str) – Title shown above the menu.
- **icon** (str) – Icon shown next to the title.

Popup menus can be useful for creating menus without having to register menu classes.

Note that they will not block the scripts execution, so the caller can’t wait for user input.

```python
import bpy

def draw(self, context):
    self.layout.label(text="Hello World")

bpy.context.window_manager.popup_menu(draw, title="Greeting", icon='INFO')
```

<a id="bpy.types.WindowManager.popup_menu_pie"></a>

#### bpy.types.WindowManager.popup_menu_pie(event, draw_func, *, title='', icon='NONE')

Display a pie menu populated by *draw_func* at the location of *event*.

**Parameters:**

- **event** ([`Event`](bpy.types.Event.md#bpy.types.Event "bpy.types.Event")) – Event used to position the pie menu.
- **draw_func** (Callable[[[`UIPieMenu`](bpy.types.UIPieMenu.md#bpy.types.UIPieMenu "bpy.types.UIPieMenu"), [`Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context")], None]) – Function to populate the pie menu layout.
- **title** (str) – Title shown at the center of the pie.
- **icon** (str) – Icon shown next to the title.

<a id="bpy.types.WindowManager.bl_rna_get_subclass"></a>

#### classmethod bpy.types.WindowManager.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.WindowManager.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.WindowManager.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="bpy.types.WindowManager.draw_cursor_add"></a>

#### classmethod bpy.types.WindowManager.draw_cursor_add(callback, args, space_type, region_type)

Add a new draw cursor handler to this space type.
It will be called every time the cursor for the specified region in the space type will be drawn.
Note: All arguments are positional only for now.

**Parameters:**

- **callback** (Callable[..., Any]) – A function that will be called when the cursor is drawn.
  It gets the specified arguments as input with the mouse position (`tuple[int, int]`) as last argument.
- **args** (tuple[Any, ...]) – Arguments that will be passed to the callback.
- **space_type** (str) – The space type the callback draws in; for example `VIEW_3D`. ([`bpy.types.Space.type`](bpy.types.Space.md#bpy.types.Space.type "bpy.types.Space.type"))
- **region_type** (str) – The region type the callback draws in; usually `WINDOW`. ([`bpy.types.Region.type`](bpy.types.Region.md#bpy.types.Region.type "bpy.types.Region.type"))

**Returns:**

Handler that can be removed later on.

**Return type:**

object

<a id="bpy.types.WindowManager.draw_cursor_remove"></a>

#### classmethod bpy.types.WindowManager.draw_cursor_remove(handler)

Remove a draw cursor handler that was added previously.

**Parameters:**

**handler** (object) – The draw cursor handler that should be removed.

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
| - [`BlendData.window_managers`](bpy.types.BlendData.md#bpy.types.BlendData.window_managers "bpy.types.BlendData.window_managers") | - [`Context.window_manager`](bpy.types.Context.md#bpy.types.Context.window_manager "bpy.types.Context.window_manager") |

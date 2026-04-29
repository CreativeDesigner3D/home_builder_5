"""Catalog browser UIList + sidebar panel.

Single UIList class HB_UL_catalog handles both layouts:
    - DEFAULT: full row with kind icon + code + name
    - GRID: compact icon + name (Blender renders these as a tile grid)

filter_items() does three jobs in one place:
    1. fuzzy substring + subsequence search across code/name/description
    2. category match (an item with category 'cabinets/base/sink' matches
       any selected ancestor: 'cabinets', 'cabinets/base', 'cabinets/base/sink')
    3. context-aware reordering - when a face frame cabinet is selected,
       option-kind items bubble to the top; when a bay is selected,
       insert-kind items bubble.
"""
import bpy

from . import catalog_data
from . import previews_catalog


def _filter_visible(state):
    """Return [(index, item), ...] for items that pass current search + category.

    Shared by HB_UL_catalog.filter_items (list view) and
    HB_CATALOG_PT_browser._draw_grid (grid view) so the two surfaces
    stay in sync. Pure read - safe from any context.
    """
    query = state.search.lower().strip()
    category = state.category
    visible = []
    for idx, item in enumerate(state.items):
        if category != 'all':
            if item.category != category and not item.category.startswith(category + '/'):
                continue
        if query:
            hay = (item.code + ' ' + item.name + ' ' + item.description).lower()
            if query not in hay and not _fuzzy_subseq(query, hay):
                continue
        visible.append((idx, item))
    return visible


def _fuzzy_subseq(needle, hay):
    """True if every char of needle appears in hay in order."""
    i = 0
    for ch in needle:
        j = hay.find(ch, i)
        if j < 0:
            return False
        i = j + 1
    return True


class HB_UL_catalog(bpy.types.UIList):
    """Single list class, two layout types (DEFAULT and GRID). The user
    toggles between them via state.view_mode which we pass as the
    template_list 'type' parameter.
    """

    def draw_item(self, context, layout, data, item, icon,
                  active_data, active_propname, index):
        """Render one row.

        Designers focus on product names, not catalog codes - so the
        name leads, and the code (if any) sits as a small muted label
        on the right edge of the row.
        """
        kind_icon = catalog_data.KIND_ICONS.get(item.kind, 'QUESTION')

        # Look up the item's thumbnail icon_id (falls back to no_thumbnail.png)
        # Items in CATALOG carry a 'thumbnail' filename; for now they're all
        # empty strings so every item resolves to the placeholder.
        entry = catalog_data.find_entry(item.item_id)
        thumb_file = entry.get('thumbnail', '') if entry else ''
        thumb_icon = previews_catalog.get_icon_id(thumb_file, item.item_id)

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row(align=True)
            # Kind icon (small leading icon - product cube vs insert)
            row.label(text="", icon=kind_icon)
            # Name takes the full available width
            row.label(text=item.name)
            # Code aligned to the right, narrow column
            if item.code:
                code_col = row.row()
                code_col.alignment = 'RIGHT'
                code_col.scale_x = 0.4
                code_col.label(text=item.code)
        elif self.layout_type == 'GRID':
            # Grid view shows the thumbnail (or placeholder) + name.
            # icon_value renders a real raster image, unlike icon=.
            layout.alignment = 'CENTER'
            layout.label(text=item.name, icon_value=thumb_icon)

    def filter_items(self, context, data, propname):
        """Filter + reorder. Returns (filter_flags, neworder)."""
        items = getattr(data, propname)
        flt = self.bitflag_filter_item

        state = context.scene.hb_catalog
        visible_indices = {idx for idx, _ in _filter_visible(state)}

        flags = [flt if i in visible_indices else 0 for i in range(len(items))]

        cabinet_selected = self._has_face_frame_cabinet_selected(context)
        bay_selected = self._has_face_frame_bay_selected(context)
        if cabinet_selected or bay_selected:
            new_order = sorted(
                range(len(items)),
                key=lambda j: self._priority(items[j], cabinet_selected, bay_selected)
            )
        else:
            new_order = []

        return flags, new_order

    @staticmethod
    def _priority(item, cabinet_selected, bay_selected):
        """Lower priority = appears first in the reordered list."""
        if bay_selected and item.kind == 'insert':
            return 0
        if cabinet_selected and item.kind == 'option':
            return 0
        return 1

    @staticmethod
    def _has_face_frame_cabinet_selected(context):
        """True if active object is a face frame cabinet root, a bay
        cage, or any descendant part. Reuses find_cabinet_root which
        walks up parents and checks IS_FACE_FRAME_CABINET_CAGE.
        """
        # Lazy import to avoid loading face_frame at catalog register time
        try:
            from ..product_libraries.face_frame.types_face_frame import find_cabinet_root
        except ImportError:
            return False
        return find_cabinet_root(context.active_object) is not None

    @staticmethod
    def _has_face_frame_bay_selected(context):
        """True if active object is itself a face frame bay cage."""
        obj = context.active_object
        if obj is None:
            return False
        return bool(obj.get('IS_FACE_FRAME_BAY_CAGE'))


class HB_CATALOG_PT_browser(bpy.types.Panel):
    """Catalog browser - top of the Home Builder sidebar."""
    bl_label = "Catalog"
    bl_idname = "HB_CATALOG_PT_browser"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Home Builder"
    bl_order = 1

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        state = scene.hb_catalog

        # Items are populated by props_catalog.register() (deferred timer)
        # and by the load_post handler. If the panel sees a mismatch
        # (e.g., a brand-new scene mid-session), schedule a deferred
        # sync - we can't write to the scene from draw().
        from . import props_catalog
        if props_catalog.needs_sync(scene):
            props_catalog.schedule_sync()

        # Search bar (icon-prefixed, full width)
        layout.prop(state, 'search', text="", icon='VIEWZOOM')

        # Category dropdown
        layout.prop(state, 'category', text="")

        # View toggle - List uses template_list (Blender's native list);
        # Grid uses a manual grid_flow because Blender 5.x's template_list
        # only supports 'DEFAULT' / 'COMPACT' types - no 'GRID'.
        row = layout.row(align=True)
        row.prop(state, 'view_mode', expand=True)

        if state.view_mode == 'GRID':
            self._draw_grid(layout, state)
        else:
            layout.template_list(
                "HB_UL_catalog", "",
                state, "items",
                state, "active_index",
                type='DEFAULT',
                rows=8,
            )

        # Detail card only in LIST mode. In GRID mode, clicking a tile
        # activates the place operator immediately - there is no "select"
        # state to describe.
        if state.view_mode != 'GRID' and 0 <= state.active_index < len(state.items):
            item = state.items[state.active_index]
            entry = catalog_data.find_entry(item.item_id)
            if entry is not None:
                self._draw_detail(layout, entry)

    @staticmethod
    def _draw_grid(layout, state):
        """Render the catalog as a 2-column thumbnail grid.

        Each tile is two stacked elements:
          1) layout.template_icon - displays the thumbnail at scale=4
             (~80px). Display-only; not clickable.
          2) layout.operator(activate_item) - a button below the icon
             with the item's name. Clicking it fires the place
             operator immediately - no select-then-button.

        A more polished look would use layout.template_asset_view, which
        is Blender's Asset Library widget. That would require migrating
        every catalog item to a marked asset in a .blend file with a
        rendered preview - a separate project. This custom grid is the
        best Blender's lower-level primitives allow without that
        migration.
        """
        visible = _filter_visible(state)
        if not visible:
            layout.label(text="No matches", icon='INFO')
            return

        grid = layout.grid_flow(
            row_major=True, columns=2,
            even_columns=True, even_rows=True,
            align=False,
        )
        for idx, item in visible:
            entry = catalog_data.find_entry(item.item_id)
            thumb_file = entry.get('thumbnail', '') if entry else ''
            thumb_icon = previews_catalog.get_icon_id(thumb_file, item.item_id)

            cell = grid.column(align=True)
            cell.template_icon(icon_value=thumb_icon, scale=4.0)
            op = cell.operator(
                'hb_catalog.activate_item',
                text=item.name,
            )
            op.item_id = item.item_id

    @staticmethod
    def _draw_detail(layout, entry):
        box = layout.box()
        col = box.column(align=True)

        kind_icon = catalog_data.KIND_ICONS.get(entry['kind'], 'QUESTION')
        col.label(text=entry['name'], icon=kind_icon)

        if entry.get('code') or entry.get('catalog_page'):
            sub = col.row()
            if entry.get('code'):
                sub.label(text=f"Code: {entry['code']}")
            if entry.get('catalog_page'):
                sub.label(text=f"p. {entry['catalog_page']}")

        if entry.get('description'):
            col.separator()
            # Word-wrap: split into ~40-char chunks
            desc = entry['description']
            for chunk in _wrap(desc, 40):
                col.label(text=chunk)

        col.separator()
        verb = catalog_data.KIND_VERBS.get(entry['kind'], 'Activate')
        op = col.operator('hb_catalog.activate_item', text=verb, icon='PLAY')
        op.item_id = entry['id']

        # Per-item thumbnail render button. Only enabled for entries that
        # have a real action_operator wired - rendering a stub would
        # produce nothing useful. The button appears greyed-out (disabled)
        # for stubs rather than vanishing, so it's discoverable.
        is_renderable = entry.get('action_operator', '') != 'hb_catalog.not_yet_implemented'
        render_row = col.row(align=True)
        render_row.enabled = is_renderable
        rop = render_row.operator(
            'hb_catalog.render_thumbnail',
            text="Render Thumbnail",
            icon='RENDER_STILL',
        )
        rop.item_id = entry['id']


def _wrap(text, width):
    """Naive word-wrap so long descriptions don't run off the panel."""
    out = []
    line = ""
    for word in text.split():
        if len(line) + len(word) + 1 > width:
            if line:
                out.append(line)
            line = word
        else:
            line = (line + " " + word) if line else word
    if line:
        out.append(line)
    return out


classes = (
    HB_UL_catalog,
    HB_CATALOG_PT_browser,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

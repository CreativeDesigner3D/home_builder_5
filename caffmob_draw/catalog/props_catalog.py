"""Catalog browser state (Scene PropertyGroup) + the mirror collection.

The CATALOG list in catalog_data.py is the source of truth. To let
Blender's UIList iterate it, we mirror each entry into a
CollectionProperty of HBCatalogItem.

Sync timing is the tricky part:
  - register() queues a deferred timer to do the initial sync (Panel
    draw() can't write to ID blocks, so we never sync from there).
  - A load_post handler re-syncs after file open.
  - schedule_sync() lets other code (the panel) request a sync from a
    read-only context; it queues a one-shot timer that does the work
    on the next idle.
"""
import bpy
from bpy.app.handlers import persistent
from bpy.props import (
    StringProperty, EnumProperty, IntProperty, CollectionProperty,
)

from . import catalog_data


def _category_items_cb(self, context):
    items = [('all', 'Everything', 'Show all items')]
    for path in catalog_data.list_categories():
        items.append((path, catalog_data.category_indented_label(path), ''))
    return items


class HBCatalogItem(bpy.types.PropertyGroup):
    """One catalog entry mirrored from CATALOG so UIList can iterate it.

    Only carries fields needed for filtering and display. The full entry
    dict is fetched by id via catalog_data.find_entry(item.item_id).
    """
    item_id: StringProperty()  # type: ignore
    code: StringProperty()  # type: ignore
    name: StringProperty()  # type: ignore
    description: StringProperty()  # type: ignore
    kind: StringProperty()  # type: ignore
    category: StringProperty()  # type: ignore


class HBCatalogState(bpy.types.PropertyGroup):
    """Browser state - attached to Scene as scene.hb_catalog."""
    search: StringProperty(
        name="Search",
        description="Filter by code, name, or description",
        default="",
    )  # type: ignore

    category: EnumProperty(
        name="Category",
        description="Filter by category",
        items=_category_items_cb,
    )  # type: ignore

    view_mode: EnumProperty(
        name="View",
        items=[
            ('DEFAULT', 'List', 'Detailed list view'),
            ('GRID',    'Grid', 'Compact grid view'),
        ],
        default='DEFAULT',
    )  # type: ignore

    items: CollectionProperty(type=HBCatalogItem)  # type: ignore
    active_index: IntProperty(default=-1)  # type: ignore


# ---------------------------------------------------------------------------
# Sync mechanism - all writes happen here, never from draw()
# ---------------------------------------------------------------------------
def sync_catalog(scene):
    """Mirror CATALOG into scene.hb_catalog.items. WRITES to the scene.

    Must only be called from a context where ID writes are allowed:
    operators, timers, handlers - NOT Panel.draw().
    """
    state = scene.hb_catalog
    state.items.clear()
    for entry in catalog_data.CATALOG:
        item = state.items.add()
        item.item_id = entry['id']
        item.code = entry.get('code', '')
        item.name = entry['name']
        item.description = entry.get('description', '')
        item.kind = entry['kind']
        item.category = entry.get('category', '')


def needs_sync(scene):
    """True if scene's items collection doesn't match the catalog size.

    Cheap, read-only - safe to call from draw().
    """
    return len(scene.hb_catalog.items) != len(catalog_data.CATALOG)


_sync_pending = False


def _deferred_sync():
    """Timer callback. Syncs every scene that needs it, then exits."""
    global _sync_pending
    _sync_pending = False
    for scene in bpy.data.scenes:
        if needs_sync(scene):
            sync_catalog(scene)
    return None  # one-shot - don't repeat


def schedule_sync():
    """Queue a deferred sync on the next idle. Read-only - safe from draw().

    The actual write happens in _deferred_sync() which runs outside the
    read-only context. Coalesces - multiple calls in one frame schedule
    only one timer.
    """
    global _sync_pending
    if _sync_pending:
        return
    _sync_pending = True
    bpy.app.timers.register(_deferred_sync, first_interval=0.0)


@persistent
def _catalog_load_post(_dummy):
    """Re-sync all scenes after file open."""
    for scene in bpy.data.scenes:
        sync_catalog(scene)


classes = (HBCatalogItem, HBCatalogState)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.hb_catalog = bpy.props.PointerProperty(type=HBCatalogState)
    if _catalog_load_post not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(_catalog_load_post)
    # Initial sync, deferred to first idle (register() can't safely write)
    schedule_sync()


def unregister():
    if _catalog_load_post in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(_catalog_load_post)
    if hasattr(bpy.types.Scene, 'hb_catalog'):
        del bpy.types.Scene.hb_catalog
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

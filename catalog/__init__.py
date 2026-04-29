"""Catalog browser package.

Top-level sidebar panel that browses all HB5 library items - placeable
products and in-cabinet inserts - in one unified surface with search,
categories, grid/list views, and context-aware reordering.

The data lives in catalog_data.CATALOG (a plain Python list); the UI is
a thin renderer over it. Per-item thumbnails (or the no_thumbnail.png
placeholder) are managed by previews_catalog.
"""
from . import catalog_data
from . import previews_catalog
from . import props_catalog
from . import ops_catalog
from . import ui_catalog


def register():
    # Previews must register before UI so icon_id lookups succeed during
    # the first draw cycle.
    previews_catalog.register()
    props_catalog.register()
    ops_catalog.register()
    ui_catalog.register()


def unregister():
    ui_catalog.unregister()
    ops_catalog.unregister()
    props_catalog.unregister()
    previews_catalog.unregister()

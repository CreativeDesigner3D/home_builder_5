"""Opt-in experimental Semantic Lines module for Home Builder.

This package is deliberately self-contained so it can be reviewed, adopted,
or removed independently of the established wireframe and Line Art workflows.
"""

from . import semantic_edge_overlay
from . import semantic_line_render


def register():
    """Register the interactive and render consumers together."""
    semantic_edge_overlay.register()
    semantic_line_render.register()


def unregister():
    """Unregister in reverse dependency order."""
    semantic_line_render.unregister()
    semantic_edge_overlay.unregister()

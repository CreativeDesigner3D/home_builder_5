"""Drawings made straight from the model.

A drawing set is data (sheets.py): sheets of placed views. Each view
kind (views.py) reads the model into a Drawing (drawing.py), a record
of drawing calls. One record serves the PDF (hb_pdf) and the viewport
(gpu_painter.py, preview.py), so no scene, instance, dimension or text
object is made for a sheet, and what is previewed is what prints.

Another add-on can add view kinds (views.register_view_kind) and draw
the sheets' border and title block (sheets.register_sheet_furniture).
"""

from . import preview, views


def register():
    views.register()
    preview.register()


def unregister():
    preview.unregister()
    views.unregister()

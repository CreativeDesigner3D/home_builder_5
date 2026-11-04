"""Furniture as cages (see furniture_geo for their models).

Not appliances: appliances are for counters, panels and cabinet gaps,
none of which should touch a sofa.
"""

from ...hb_types import GeoNodeCage
from ...units import inch
from . import furniture_geo

MENU_ID = "HOME_BUILDER_MT_furnishing_commands"


class Furnishing(GeoNodeCage):
    """A piece of furniture: its kind and size, its back at y = 0."""

    KIND = 'SOFA'
    LABEL = "Furniture"
    width = inch(84)
    depth = inch(36)
    height = inch(34)
    extra = {}

    def create(self, name=None):
        super().create(name or self.LABEL)
        obj = self.obj
        obj[furniture_geo.FURNISHING_KEY] = True
        obj[furniture_geo.KIND_KEY] = self.KIND
        for key, value in self.extra.items():
            obj[key] = value
        obj['MENU_ID'] = MENU_ID
        obj.display_type = 'WIRE'
        self.set_input('Dim X', self.width)
        self.set_input('Dim Y', self.depth)
        self.set_input('Dim Z', self.height)
        self.set_input('Mirror Y', True)


def _kind(kind, label, w, d, h, **extra):
    return type(label.replace(' ', ''), (Furnishing,),
                {'KIND': kind, 'LABEL': label, 'width': w, 'depth': d, 'height': h, 'extra': extra})


Bed = _kind('BED', "Queen Bed", inch(60), inch(84), inch(48), FURNISHING_SIZE='QUEEN')
Nightstand = _kind('NIGHTSTAND', "Nightstand", inch(24), inch(18), inch(26))
Dresser = _kind('DRESSER', "Dresser", inch(60), inch(20), inch(32))
Sofa = _kind('SOFA', "Sofa", inch(84), inch(36), inch(34))
Loveseat = _kind('LOVESEAT', "Loveseat", inch(60), inch(36), inch(34))
Sectional = _kind('SECTIONAL', "Sectional", inch(108), inch(84), inch(34), FURNISHING_SIDE='LEFT')
Armchair = _kind('ARMCHAIR', "Armchair", inch(34), inch(34), inch(33))
CoffeeTable = _kind('COFFEE_TABLE', "Coffee Table", inch(48), inch(24), inch(18))
EndTable = _kind('END_TABLE', "End Table", inch(22), inch(22), inch(24))
TVConsole = _kind('TV_CONSOLE', "TV Console", inch(66), inch(18), inch(24))
Rug = _kind('RUG', "Rug", inch(96), inch(72), inch(0.5))
DiningTable = _kind('DINING_TABLE', "Dining Table", inch(72), inch(40), inch(30),
                    FURNISHING_SHAPE='RECT', FURNISHING_CHAIRS=0)
Desk = _kind('DESK', "Desk", inch(60), inch(30), inch(30))
Bookcase = _kind('BOOKCASE', "Bookcase", inch(36), inch(12), inch(84))

CLASSES = (Bed, Nightstand, Dresser, Sofa, Loveseat, Sectional, Armchair, CoffeeTable,
           EndTable, TVConsole, Rug, DiningTable, Desk, Bookcase)


def class_for(kind):
    return next((c for c in CLASSES if c.KIND == kind), None)

"""Light fixtures as cages (see lighting_geo for their models and lights)."""

import bpy

from ...hb_types import GeoNodeCage
from ...units import inch
from . import lighting_geo

MENU_ID = "HOME_BUILDER_MT_light_fixture_commands"


class LightFixture(GeoNodeCage):
    """A light fixture: its kind, size, lumens and colour temperature."""

    KIND = 'PENDANT'
    LABEL = "Light"
    width = inch(12)
    depth = inch(12)
    height = inch(30)
    lumens = 800.0
    kelvin = 2700.0
    on_wall = False

    def create(self, name=None):
        super().create(name or self.LABEL)
        obj = self.obj
        obj[lighting_geo.FIXTURE_KEY] = True
        obj[lighting_geo.KIND_KEY] = self.KIND
        obj[lighting_geo.LUMENS_KEY] = self.lumens
        obj[lighting_geo.KELVIN_KEY] = self.kelvin
        obj['MENU_ID'] = MENU_ID
        obj.display_type = 'WIRE'
        self.set_input('Dim X', self.width)
        self.set_input('Dim Y', self.depth)
        self.set_input('Dim Z', self.height)
        if self.on_wall:
            # Its back to the wall, like an appliance: the room at -y
            self.set_input('Mirror Y', True)


class Pendant(LightFixture):
    KIND, LABEL = 'PENDANT', "Pendant"
    width = depth = inch(12)
    height = inch(30)


class FlushMount(LightFixture):
    KIND, LABEL = 'FLUSH', "Flush Mount"
    width = depth = inch(14)
    height = inch(5)
    lumens = 1600.0


class RecessedCan(LightFixture):
    KIND, LABEL = 'RECESSED', "Recessed Can"
    width = depth = inch(6)
    height = inch(1)
    lumens = 650.0


class Chandelier(LightFixture):
    KIND, LABEL = 'CHANDELIER', "Chandelier"
    width = depth = inch(26)
    height = inch(28)
    lumens = 2400.0


class CeilingFan(LightFixture):
    KIND, LABEL = 'FAN', "Ceiling Fan"
    width = depth = inch(52)
    height = inch(14)
    lumens = 1200.0


class Sconce(LightFixture):
    KIND, LABEL = 'SCONCE', "Wall Sconce"
    width = inch(6)
    depth = inch(8)
    height = inch(11)
    lumens = 450.0
    on_wall = True
    mount_height = inch(66)


class VanityBar(LightFixture):
    KIND, LABEL = 'VANITY', "Vanity Light"
    width = inch(24)
    depth = inch(7)
    height = inch(7)
    lumens = 1600.0
    on_wall = True
    mount_height = inch(78)


CLASSES = (Pendant, FlushMount, RecessedCan, Chandelier, CeilingFan, Sconce, VanityBar)


def class_for(kind):
    return next((c for c in CLASSES if c.KIND == kind), None)

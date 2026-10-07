"""Appliance-panel spec provider registry.

A spec provider is an object exposing:

    manufacturers() -> [str]
    models(manufacturer) -> [ {"model", "series", "appliance_type"} ]
    resolve(manufacturer, model) -> spec dict, carrying at least
        "operator_config", "operator_panel_type", "appliance_dim_x_m",
        "weight_max_lb", "panels", "flags".

HB5 ships no provider, so the appliance-panel dropdowns fall back to manual
entry; the host application registers a provider with the catalog data. Plain
data registry - no Blender classes, nothing to register()/unregister() at the
add-on level.
"""

_provider = None


def register_provider(provider):
    """Register the appliance-panel spec provider (overwrites any prior one)."""
    global _provider
    _provider = provider


def unregister_provider():
    global _provider
    _provider = None


def get_provider():
    return _provider

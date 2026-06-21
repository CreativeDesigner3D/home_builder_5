"""Accessory provider registry.

A provider is a zero-arg callable returning a list of plain dicts. Each
dict is expected to carry at least ``code`` and ``name``; consumers may
also read ``category`` and ``min_opening_w``. Plain data registry - no
Blender classes, so there is nothing to register()/unregister() at the
add-on level.
"""

# host key -> provider callable
_providers = {}


def register_provider(host, fn):
    """Register ``fn`` as the item provider for ``host`` (overwrites)."""
    _providers[host] = fn


def unregister_provider(host):
    """Remove the provider for ``host`` if present."""
    _providers.pop(host, None)


def has_provider(host):
    return host in _providers


def get_items(host):
    """Items for ``host`` from its provider, or [] if none / on error."""
    fn = _providers.get(host)
    if fn is None:
        return []
    try:
        return list(fn())
    except Exception as e:  # pragma: no cover - defensive
        print("HB5 accessory_registry: provider for %s failed: %s" % (host, e))
        return []


def lookup(host, code):
    for it in get_items(host):
        if it.get("code") == code:
            return it
    return None


def categories(host):
    seen = []
    for it in get_items(host):
        c = it.get("category")
        if c and c not in seen:
            seen.append(c)
    return seen

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


def all_items():
    """Every item from every registered provider, each dict carrying an
    injected ``host`` key (provider-registration order). Lets a caller list
    the whole catalog without knowing the host keys; per-host providers stay
    the single source of data."""
    out = []
    for host, fn in _providers.items():
        try:
            for it in fn():
                d = dict(it)
                d.setdefault("host", host)
                out.append(d)
        except Exception as e:  # pragma: no cover - defensive
            print("HB5 accessory_registry: provider for %s failed: %s" % (host, e))
    return out


def all_categories():
    """Ordered, de-duplicated category names across every provider."""
    seen = []
    for it in all_items():
        c = it.get("category")
        if c and c not in seen:
            seen.append(c)
    return seen


def find(code):
    """First item (with its ``host``) matching ``code`` across every
    provider, or None. Catalog codes are unique across hosts."""
    for it in all_items():
        if it.get("code") == code:
            return it
    return None


def sections():
    """Ordered, de-duplicated ``section`` names across every provider."""
    seen = []
    for it in all_items():
        s = it.get("section")
        if s and s not in seen:
            seen.append(s)
    return seen


def groups(section):
    """Ordered, de-duplicated ``group`` names within ``section``."""
    seen = []
    for it in all_items():
        if it.get("section") != section:
            continue
        g = it.get("group")
        if g and g not in seen:
            seen.append(g)
    return seen


def group_items(section, group):
    """Items carrying the given ``section`` + ``group`` (provider order)."""
    return [it for it in all_items()
            if it.get("section") == section and it.get("group") == group]


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
